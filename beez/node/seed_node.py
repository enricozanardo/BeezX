"""Beez blockchain - beez seed node."""

from __future__ import annotations
import os
import random
from dotenv import load_dotenv
import time
import math
import copy
import threading
from datetime import datetime
from loguru import logger

from whoosh.fields import Schema, TEXT, KEYWORD, ID  # type: ignore

from beez.socket.socket_communication.seed_socket_communication import (
    SeedSocketCommunication,
)
from beez.beez_utils import BeezUtils
from beez.api.node_api import SeedNodeAPI
from beez.node.beez_node import BasicNode
from beez.index.index_engine import DigitalAssetMetadataIndexEngine
from beez.socket.messages.message_transaction import MessageTransation
from beez.socket.messages.message_type import MessageType
from beez.socket.messages.message_push_chunk import MessagePushChunk
from beez.socket.messages.message_pull_chunk import MessagePullChunk

load_dotenv()  # load .env
P_2_P_PORT = int(os.getenv("P_2_P_PORT", 8122))  # pylint: disable=invalid-envvar-default


class SeedNode(BasicNode):
    """Beez Seed Node class."""

    def __init__(self, key=None, ip_address=None, port=None) -> None:
        BasicNode.__init__(     # pylint: disable=duplicate-code
            self,
            key=key,
            ip_address=ip_address,
            port=port,
            communication_protocol=SeedSocketCommunication
        )
        self.dam_metadata_index = DigitalAssetMetadataIndexEngine.get_engine(
            Schema(
                id=ID(stored=True),
                type=KEYWORD(stored=True),
                dam_id=TEXT(stored=True),
                metadata=TEXT(stored=True),
            )
        )
        self.start_network_health_scans()
        self.digital_asset_metadata = {}
        self.asset_parts = {}
        self.concatenated_files = {}
        self.pending_chunks = {}    # chunks without ack from storage node
        self.pending_pull_chunks = {}

    def start_p2p(self):
        self.p2p.start_socket_communication(self)
        self.resend_pending_chunks()
        self.repull_pending_chunks()

    def start_api(self, port=None):
        """Starts the nodes API."""
        self.api = SeedNodeAPI()
        # Inject Node to NodeAPI
        self.api.inject_node(self)
        self.api.start(self.ip_address, port)

    def repull_pending_chunks(self):
        repull_chunks_thread = threading.Thread(target=self.repull_chunks, args={})
        repull_chunks_thread.daemon = True
        repull_chunks_thread.start()

    def repull_chunks(self):
        while True:
            current_pending_pull_chunks = copy.deepcopy(self.pending_pull_chunks)
            for asset_hash in current_pending_pull_chunks.keys():
                for chunk_id in current_pending_pull_chunks[asset_hash].keys():
                    status_dict = current_pending_pull_chunks[asset_hash][chunk_id]
                    if status_dict["status"] == True:
                        now = datetime.now()
                        if (now-status_dict["last_update"]).total_seconds() > 15 and (now-status_dict["last_update"]).total_seconds() < 600:
                            for node in self.p2p.all_nodes:
                                if f"{node.host}:{node.port}" == status_dict["node_identifier"]:
                                    logger.info(f'REPULLING CHUNK {chunk_id}')
                                    self.pull_chunk_from_node(node, chunk_id, status_dict["asset_name"])
                                    status_dict["last_update"] = now
            time.sleep(3)

    # TODO: resend chunks which i got no response from
    def resend_pending_chunks(self):
        """Execution thread to iteratively request the peers health status."""
        resend_chunks_thread = threading.Thread(target=self.resend_chunks, args={})
        resend_chunks_thread.daemon = True
        resend_chunks_thread.start()

    def resend_chunks(self):
        while True:
            current_pending_chunks = copy.deepcopy(self.pending_chunks)
            for asset_hash in current_pending_chunks.keys():
                for chunk_id in current_pending_chunks[asset_hash].keys():
                    status_dict = current_pending_chunks[asset_hash][chunk_id]
                    if status_dict["status"] == True:
                        now = datetime.now()
                        if (now-status_dict["last_update"]).total_seconds() > 15 and (now-status_dict["last_update"]).total_seconds() < 300:
                            for node in self.p2p.all_nodes:
                                if f"{node.host}:{node.port}" == status_dict["node_identifier"]:
                                    logger.info(f'RESENDING CHUNK {chunk_id}')
                                    self.push_chunk_to_node(node, chunk_id, status_dict["chunk"])
            time.sleep(3)

    def start_available_peers_broadcast(self):
        self.p2p.available_peers_broadcast_thread()

    def start_network_health_scans(self):
        """Starts the network scans for Beez Node health discovery."""
        self.p2p.network_health_scan()

    def assign_chunks_to_nodes(self, chunks, nodes) -> dict[int, list(int)]:
        """Gets the list of nodes and chunks and assigns the chunks to the nodes"""
        number_of_chunks = len(chunks)
        number_of_nodes = len(nodes)
        chunk_assignment = {}
        for i in range(number_of_chunks):
            if not nodes[i%number_of_nodes] in chunk_assignment:
                chunk_assignment[nodes[i%number_of_nodes]] = {}
            chunk_assignment[nodes[i%number_of_nodes]][i]=chunks[i]
        return chunk_assignment

    def process_uploaded_asset(self, filename, digital_asset):
        asset_hash = BeezUtils.hash(digital_asset).hexdigest()
        parts = self.split_digital_asset_in_chunks(digital_asset)
        chunks_assigned = self.assign_chunks_to_nodes(parts, self.p2p.all_nodes)
        # get nodes to store asset chunks
        chunk_locations = {}
        # do not send all chunks of a node directly but mix it up for better performance and smaller message buffers on nodes
        mixed_chunk_tuples = []
        for node, dict_of_chunks in chunks_assigned.items():
            for chunk_ctr, chunk in dict_of_chunks.items():
                chunk_id = f"{asset_hash}-{chunk_ctr}.dap"
                mixed_chunk_tuples.append((node, chunk_id, chunk))
        random.shuffle(mixed_chunk_tuples)

        # send chunks to nodes and add it to pending chunks
        for chunk_tuple in mixed_chunk_tuples:
            node = chunk_tuple[0]
            chunk_id = chunk_tuple[1]
            chunk = chunk_tuple[2]
            chunk_ctr = chunk_id.split("-")[1].split(".")[0]
            self.push_chunk_to_node(node, chunk_id, chunk)
            node_identifier = f"{node.host}:{node.port}"
            if asset_hash not in self.pending_chunks:
                self.pending_chunks[asset_hash] = {}
            self.pending_chunks[asset_hash][chunk_id] = {"status": True, "chunk": chunk, "last_update": datetime.now(), "node_identifier": node_identifier}
            if node_identifier not in chunk_locations:
                chunk_locations[node_identifier] = sorted([chunk_ctr])
            else:
                chunk_locations[node_identifier] += [chunk_ctr]
                chunk_locations[node_identifier] = sorted(chunk_locations[node_identifier])
            time.sleep(0.1)   # worked with 5s
                
        # store metadata for digital asset
        self.digital_asset_metadata[filename] = {
            "fileName": filename,
            "fileHash": asset_hash,
            "numOfChunks": len(parts),
            "chunkLocations": chunk_locations,
        }
        
    def update_digital_asset_metadata(self, available_peers_status):
        """Gets information about the node and whether it joined or left and updates the metdata accordingly."""        
        # Iterate digital asset metadata
        for _, metadata in self.digital_asset_metadata.items():
            new_chunk_locations = copy.deepcopy(metadata["chunkLocations"])
            current_locations = list(metadata["chunkLocations"].keys())
            # Compare chunkLocations with available_peers_status.
            # If there are etnryies not in available_peers_status but in chunkLocations, 
            # move chunks from missing node to following node and delete obsolete chunkLocations entry
            for node_socket_connector_string, chunk_list in metadata["chunkLocations"].items():
                if node_socket_connector_string not in list(available_peers_status.keys()):
                    # get next socket_connector in list of all
                    new_socket_connector_index = current_locations.index(node_socket_connector_string) + 1
                    if new_socket_connector_index >= len(current_locations):
                        new_socket_connector_index = 0
                    new_socket_connector = current_locations[new_socket_connector_index]
                    # move chunks to new location
                    new_chunk_locations[new_socket_connector] += chunk_list
                    new_chunk_locations[new_socket_connector] = sorted(new_chunk_locations[new_socket_connector])
                    # delete obsolete socket_connector entry in chunkList
                    new_chunk_locations.pop(node_socket_connector_string, None)
            # Update metadata for file
            metadata["chunkLocations"] = new_chunk_locations

    def get_number_of_chunks_for_size(self, size: int) -> int:
        """Returns the required number of chunks based on the given file size in digits."""
        if size > 10000000000:
            return 800
        if size > 1000000000:
            return 400
        if size > 100000000:
            return 200
        if size > 10000000:
            return 50
        if size > 1000000:
            return 25
        if size > 100000:
            return 10
        if size > 10000:
            return 5
        if size > 5000:
            return 2
        return 1


    def split_digital_asset_in_chunks(self, digital_asset):
        length = len(digital_asset)
        number_of_chunks = self.get_number_of_chunks_for_size(length)
        chunk_size = math.ceil(length/number_of_chunks)
        chunks = [digital_asset[i:i+chunk_size] for i in range(0, len(digital_asset), chunk_size)]
        return chunks

    def push_chunk_to_node(self, node, chunk_id, digital_asset_chunk):
        chunk_message = MessagePushChunk(self.p2p.socket_connector, "push_chunk", chunk_id=chunk_id ,chunk=digital_asset_chunk, chunk_type='primary')
        encoded_chunk_message: str = BeezUtils.encode(chunk_message)
        if not "message_type" in encoded_chunk_message or not "chunk_id" in encoded_chunk_message or not "chunk_type" in encoded_chunk_message or not "chunk" in encoded_chunk_message:
            logger.info('COULD NOT ENCODE!!!!!!!!')
            encoded_chunk_message: str = BeezUtils.encode(chunk_message)
        self.p2p.send(node, encoded_chunk_message)

    def pull_chunk_from_node(self, node, chunk_id, asset_name):
        pull_chunk_message = MessagePullChunk(self.p2p.socket_connector, "pull_chunk", chunk_id, asset_name)
        encoded_pull_chunk_message: str = BeezUtils.encode(pull_chunk_message)
        self.p2p.send(node, encoded_pull_chunk_message)


    def get_distributed_asset(self, asset_name):
        # get metadata for file
        asset_metadata = self.digital_asset_metadata[asset_name]
        asset_node_socket_connector_strings = asset_metadata["chunkLocations"].keys()
        asset_hash = asset_metadata["fileHash"]
        asset_name = asset_metadata["fileName"]
        
        for node in self.p2p.all_nodes:
            node_socket_connector_string = f"{node.host}:{node.port}"
            if node_socket_connector_string in asset_node_socket_connector_strings:
                chunks_on_node = asset_metadata['chunkLocations'][node_socket_connector_string]
                for chunk_index in chunks_on_node:
                    chunk_id = f"{asset_hash}-{chunk_index}.dap"
                    node_identifier = f"{node.host}:{node.port}"
                    self.pull_chunk_from_node(node, chunk_id, asset_name)
                    if asset_hash not in self.pending_pull_chunks:
                        self.pending_pull_chunks[asset_hash] = {}
                    self.pending_pull_chunks[asset_hash][chunk_id] = {"status": True, "chunk_id": chunk_id, "last_update": datetime.now(), "node_identifier": node_identifier, "asset_name": asset_name}
                    # pull_chunk_message = MessagePullChunk(self.p2p.socket_connector, "pull_chunk", f"{asset_hash}-{chunk_index}.dap", asset_name)
                    # encoded_pull_chunk_message: str = BeezUtils.encode(pull_chunk_message)
                    # self.p2p.send(node, encoded_pull_chunk_message)
                    time.sleep(0.1)
        while asset_hash not in self.concatenated_files:
            time.sleep(1)
        return self.concatenated_files[asset_hash]

    def add_asset_chunks(self, file_name, chunk_name, chunk):
        logger.info('add asset chunk')
        digital_asset_hash = chunk_name.rsplit("-", 1)[0]
        if not digital_asset_hash in self.asset_parts:
            self.asset_parts[digital_asset_hash] = {chunk_name: chunk}
        else:
            self.asset_parts[digital_asset_hash][chunk_name] = chunk

        self.pending_pull_chunks[digital_asset_hash][chunk_name]["status"] = False

        if len(self.asset_parts[digital_asset_hash]) == self.digital_asset_metadata[file_name]["numOfChunks"]:
            concatenated_file = self.concatenate_chunks(self.asset_parts[digital_asset_hash])
            self.concatenated_files[digital_asset_hash] = concatenated_file

        logger.info(chunk_name)

        logger.info(f"GOT {len(self.asset_parts[digital_asset_hash])} chunks of {self.digital_asset_metadata[file_name]['numOfChunks']}")
        

    def concatenate_chunks(self, chunks):
        after_string = b""
        chunk_names = sorted(chunks.keys())
        for chunk_name in chunk_names:
            after_string = after_string + chunks[chunk_name]
        return after_string

    def get_chunk_from_node(self, chunk_id):
        pass

    def broadcast_transaction(self, transaction):
        # Propagate the transaction to other peers
        message = MessageTransation(
            self.p2p.socket_connector, MessageType.TRANSACTION, transaction
        )
        encoded_message = BeezUtils.encode(message)
        self.p2p.broadcast(encoded_message)

    def stop(self):
        """Stops the p2p communication."""
        self.p2p.health_checks_active = False
        self.p2p.stop()
