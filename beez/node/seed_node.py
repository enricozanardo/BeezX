"""Beez blockchain - beez seed node."""

from __future__ import annotations
import os
from dotenv import load_dotenv
import time
from loguru import logger

from whoosh.fields import Schema, TEXT, KEYWORD, ID  # type: ignore

from beez.socket.socket_communication.seed_socket_communication import (
    SeedSocketCommunication,
)
from beez.beez_utils import BeezUtils
from beez.api.node_api import SeedNodeAPI
from beez.node.beez_node import BasicNode
from beez.index.index_engine import DigitalAssetMetadataIndexEngine
from beez.socket.messages.message_push_junk import MessagePushJunk
from beez.socket.messages.message_pull_junk import MessagePullJunk

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

    def start_p2p(self):
        self.p2p.start_socket_communication(self)

    def start_api(self, port=None):
        """Starts the nodes API."""
        self.api = SeedNodeAPI()
        # Inject Node to NodeAPI
        self.api.inject_node(self)
        self.api.start(self.ip_address, port)

    def start_available_peers_broadcast(self):
        self.p2p.available_peers_broadcast_thread()

    def start_network_health_scans(self):
        """Starts the network scans for Beez Node health discovery."""
        self.p2p.network_health_scan()

    def process_uploaded_asset(self, filename, digital_asset):
        asset_hash = BeezUtils.hash(digital_asset).hexdigest()
        parts = self.split_digital_asset_in_junks(digital_asset)
        # get nodes to store asset junks
        nodes = []
        for index,node in enumerate(self.p2p.all_nodes):
            if index < len(parts):
                nodes.append(node)
        chunk_locations = {}
        for index, node in enumerate(nodes):
            self.push_junk_to_node(node, f"{asset_hash}-{index}.dap", parts[index])
            chunk_locations[node.id] = [index]
        # store metadata for digital asset
        self.digital_asset_metadata[filename] = {
            "fileName": filename,
            "fileHash": asset_hash,
            "numOfChunks": 3,
            "chunkLocations": chunk_locations,
        }
        logger.info('GOT DIGITAL ASSET')
        logger.info(self.digital_asset_metadata)


    def split_digital_asset_in_junks(self, digital_asset):
        length = len(digital_asset)
        part_1 = digital_asset[:int(length/3)]
        part_2 = digital_asset[int(length/3):2*int(length/3)]
        part_3 = digital_asset[2*int(length/3):]
        parts = [part_1, part_2, part_3]
        return parts

    def push_junk_to_node(self, node, junk_id, digital_asset_junk):
        junk_message = MessagePushJunk(self.p2p.socket_connector, "push_junk", junk_id=junk_id ,junk=digital_asset_junk)
        encoded_junk_message: str = BeezUtils.encode(junk_message)
        self.p2p.send(node, encoded_junk_message)

    def get_distributed_asset(self, asset_name):
        # get metadata for file
        asset_metadata = self.digital_asset_metadata[asset_name]
        asset_node_ids = asset_metadata["chunkLocations"].keys()
        asset_hash = asset_metadata["fileHash"]
        asset_name = asset_metadata["fileName"]
        
        for node in self.p2p.all_nodes:
            if node.id in asset_node_ids:
                pull_junk_message = MessagePullJunk(self.p2p.socket_connector, "pull_junk", f"{asset_hash}-{asset_metadata['chunkLocations'][node.id][0]}.dap", asset_name)
                encoded_pull_junk_message: str = BeezUtils.encode(pull_junk_message)
                self.p2p.send(node, encoded_pull_junk_message)
        while asset_hash not in self.concatenated_files:
            time.sleep(3)
        return self.concatenated_files[asset_hash]

    def add_asset_junks(self, file_name, chunk_name, junk):
        digital_asset_hash = chunk_name.rsplit("-", 1)[0]
        if not digital_asset_hash in self.asset_parts:
            self.asset_parts[digital_asset_hash] = {chunk_name: junk}
        else:
            self.asset_parts[digital_asset_hash][chunk_name] = junk

        if len(self.asset_parts[digital_asset_hash]) == self.digital_asset_metadata[file_name]["numOfChunks"]:
            concatenated_file = self.concatenate_junks(self.asset_parts[digital_asset_hash])
            self.concatenated_files[digital_asset_hash] = concatenated_file
        

    def concatenate_junks(self, junks):
        after_string = b""
        chunk_names = sorted(junks.keys())
        for chunk_name in chunk_names:
            after_string = after_string + junks[chunk_name]
            # after_string = after_string + junks[chunk_name].encode()
        return after_string

    def get_junk_from_node(self, junk_id):
        pass
    def stop(self):
        """Stops the p2p communication."""
        self.p2p.health_checks_active = False
        self.p2p.stop()
