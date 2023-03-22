"""Beez blockchain - socket communication."""

from __future__ import annotations
import json
from typing import TYPE_CHECKING, Optional
import os
from dotenv import load_dotenv
from loguru import logger
from p2pnetwork.node import Node    # type: ignore

from beez.socket.socket_communication.base_socket_communication import BaseSocketCommunication
from beez.socket.socket_connector import SocketConnector
from beez.socket.peer_discovery_handler import PeerDiscoveryHandler
from beez.beez_utils import BeezUtils
from beez.socket.messages.message_type import MessageType
from beez.transaction.transaction import Transaction
from beez.transaction.challenge_tx import ChallengeTX
from beez.block.blockchain import Blockchain
from beez.block.block import Block
from beez.socket.messages.message_health import MessageHealth
from beez.socket.messages.message_junk_reply import MessageJunkReply
from beez.socket.messages.message_push_junk_reply import MessagePushJunkReply
from beez.socket.messages.message_push_junk import MessagePushJunk

if TYPE_CHECKING:
    from beez.types import Address
    from beez.node.beez_node import BeezNode
    from beez.socket.messages.message import Message


load_dotenv()  # load .env
LOCAL_TEST_IP = "192.168.1.209"
LOCAL_P2P_PORT = 5444

FIRST_SERVER_IP = os.getenv("FIRST_SERVER_IP", LOCAL_TEST_IP)   # pylint: disable=invalid-envvar-default
P_2_P_PORT = int(os.getenv("P_2_P_PORT", LOCAL_P2P_PORT))   # pylint: disable=invalid-envvar-default
LOCAL_INTERVALS = 10
INTERVALS = int(os.getenv("INTERVALS", LOCAL_INTERVALS))    # pylint: disable=invalid-envvar-default
# NODE_DAM_FOLDER = os.environ.get("NODE_DAM_FOLDER", default="/assets/")



class SocketCommunication(BaseSocketCommunication):
    """
    This class manage the P2P communication.
    """

    def __init__(self, ip: Address, port: int):
        BaseSocketCommunication.__init__(self, ip, port)   # pylint: disable=super-with-arguments
        self.peer_discovery_handler = PeerDiscoveryHandler(self)
        self.beez_node: Optional[BeezNode] = None
        self.neighbor: Optional[SocketConnector] = None
        self.primary_node: Optional[SocketConnector] = None

    def connect_to_first_node(self):
        """Connects to first, hardcoded beez blockchain node."""
        first_server_ip = FIRST_SERVER_IP
        first_server_port = P_2_P_PORT
        if self.beez_node and self.beez_node.first_server_ip:
            first_server_ip = self.beez_node.first_server_ip
        if self.beez_node and self.beez_node.first_server_port:
            first_server_port = self.beez_node.first_server_port
        logger.info(f"Check to connect to first node {first_server_ip} at port {first_server_port}")

        if (
            self.socket_connector.ip_address != first_server_ip
            or self.socket_connector.port != first_server_port
        ):
            # connect to the first node
            self.connect_with_node(first_server_ip, first_server_port)
            
    def connect_with_adjacent_node(self, ip, port):
        """Connects to adjacent neighbor based on peers list from seed node."""
        logger.info(f"Check to connect to neighbor node {ip} at port {port}")

        if (
            self.socket_connector.ip_address != ip
            or self.socket_connector.port != port
        ):
            # connect to adjacent neighbor node
            connection_to_neighbor = False
            import time
            while not connection_to_neighbor:
                logger.info(f"connecting with node {ip}:{port}")
                connection_to_neighbor = self.connect_with_node(str(ip), int(port))
                logger.info(connection_to_neighbor)
                time.sleep(10)

    def neighbor_node(self):
        neighbor_node = None
        for node in self.all_nodes:
            if f"{node.host}:{node.port}" == f"{self.neighbor.ip_address}:{self.neighbor.port}":
                neighbor_node = node
        return neighbor_node

    def start_socket_communication(self, beez_node: BeezNode):
        """Starts socket communication."""
        self.beez_node = beez_node
        self.start()
        self.connect_to_first_node()

    def inbound_node_connected(self, node: Node):
        """Callback method of receiving requests from nodes."""
        logger.info("inbound connection (some node wants to connect to this node)")
        # TODO: save connection
        self.peer_discovery_handler.handshake(node)

    def outbound_node_connected(self, node: Node):
        """Callback method of sending requests to nodes."""
        logger.info("outbound connection (this node wants to connect to other node)")
        self.peer_discovery_handler.handshake(node)

    # Once connected send a message
    # this is automatically provided by the library
    def node_message(self, node: Node, data: Message):  # pylint: disable=too-many-branches
        """Handles incomming messages."""
        message = BeezUtils.decode(json.dumps(data))

        logger.info(f"messagetype? {message.message_type}")

        if message.message_type == MessageType.DISCOVERY:
            # handle the DISCOVERY
            logger.info(f"manage the message {message.message_type}")
            self.peer_discovery_handler.handle_message(message)

        elif message.message_type == MessageType.HEALTH:
            pass

        elif message.message_type == MessageType.TRANSACTION:
            # handle the TRANSACTION
            logger.info(f"A Transaction Message will be broadcasted!! {message.message_type}")
            transaction: Transaction = message.transaction
            if self.beez_node:
                self.beez_node.handle_transaction(transaction)
            else:
                logger.info("Socket communication module has to node reference.")

        elif message.message_type == MessageType.CHALLENGE:
            # handle the CHALLENGE
            logger.info(f"A CHALLENGE Message will be broadcasted!! {message.message_type}")
            challenge_transaction: ChallengeTX = message.challengeTx
            if self.beez_node:
                self.beez_node.handle_challenge_tx(challenge_transaction)
            else:
                logger.info("Socket communication module has to node reference.")

        elif message.message_type == MessageType.BLOCK:
            # handle the BLOCK
            logger.info(f"A BLOCK Message will be broadcasted!! {message.message_type}")
            block: Block = Block.deserialize(message.block, index=False)
            if self.beez_node:
                self.beez_node.handle_block(block)
            else:
                logger.info("Socket communication module has to node reference.")

        elif message.message_type == MessageType.BLOCKCHAINREQUEST:
            # handle the BLOCKCHAINREQUEST
            logger.info(f"A BLOCKCHAINREQUEST Message will be broadcasted!! {message.message_type}")
            # this message do not contain any object
            if self.beez_node:
                self.beez_node.handle_blockchain_request(node)
            else:
                logger.info("Socket communication module has to node reference.")

        elif message.message_type == MessageType.BLOCKCHAIN:
            # handle the BLOCKCHAIN
            logger.info(
                f"A BLOCKCHAIN Message came in!! {message.message_type}"
            )
            blockchain: Blockchain = Blockchain.deserialize(
                message.serialized_blockchain,
                index=False
            )
            if self.beez_node:
                self.beez_node.handle_blockchain(blockchain)
            else:
                logger.info("Socket communication module has to node reference.")
        elif message.message_type == MessageType.ADDRESSREGISTRATION:
            # handle address registration
            if self.beez_node:
                self.beez_node.handle_address_registration(message.public_key_hex)
        elif message.message_type == "push_junk":
            junk_reply = MessagePushJunkReply(self.socket_connector, "push_junk_reply", junk_id=message.junk_id, ack=True)
            try:
                with open(f"{self.beez_node.dam_asset_path}{message.junk_id}", "w+b") as outfile:
                    outfile.write(message.junk)
                if message.chunk_type == "primary":
                    logger.info(50*'#')
                    logger.info('GOT PRIMARY CHUNK')
                    if message.junk_id not in self.beez_node.primary_chunks:
                        self.beez_node.primary_chunks.append(message.junk_id)
                        # also push to backup node
                        self.push_chunk_to_neighbor(message.junk_id, message.junk)
                elif message.chunk_type == "backup":
                    logger.info(50*'#')
                    logger.info('GOT BACKUP CHUNK')
                    if message.junk_id not in self.beez_node.backup_chunks:
                        self.beez_node.backup_chunks.append(message.junk_id)
            except Exception as ex:
                junk_reply = MessagePushJunkReply(self.socket_connector, "push_junk_reply", junk_id=message.junk_id, ack=False)
            encoded_junk_reply: str = BeezUtils.encode(junk_reply)
            self.send(node, encoded_junk_reply)
        elif message.message_type == "pull_junk":
            content = b''
            with open(f"{self.beez_node.dam_asset_path}{message.junk_name}", "rb") as infile:
                content = infile.read()
            junk_reply = MessageJunkReply(self.socket_connector, "junk_reply", message.file_name, message.junk_name, content)
            # junk_reply = MessageJunkReply(self.socket_connector, "junk_reply", message.file_name, message.junk_name, str(content))
            encoded_junk_reply: str = BeezUtils.encode(junk_reply)
            self.send(node, encoded_junk_reply)
        elif message.message_type == MessageType.PEERSREQUEST:

            # add sender of message to own connections if not exists
            sender_connector_exists: bool = False
            for connector in self.own_connections:
                if f"{connector.ip_address}:{connector.port}" == f"{message.sender_connector.ip_address}:{message.sender_connector.port}":
                    sender_connector_exists = True
            if not sender_connector_exists:
                self.own_connections.append(message.sender_connector)
                self.own_connections.sort(key=lambda x: f"{x.ip_address}:{x.port}", reverse=True)

            # check if there are any dead nodes and if this node has connection to dead node
            if message.dead_peers:
                for dead_peer in message.dead_peers:
                    self.disconnect_peer(SocketConnector(dead_peer.split(':')[0], int(dead_peer.split(':')[1])))
                    # check if the node to which this node is the neigbor is dead and if so, send the backup chunks
                    # to this nodes neighbor

            # check if there are any available peers (this node should also be part of the list)
            if not list(message.available_peers.keys()) or (len(list(message.available_peers.keys())) == 1 and list(message.available_peers.keys())[0] == f"{self.socket_connector.ip_address}:{self.socket_connector.port}"):
                logger.info('No peers available')
                return

            # get adjacent neighbor
            adjacent_index: int = -1    # index of this nodes neighbor
            primary_node_index: int = -1    # index of node this node is neigbor to
            for index, available_peer in enumerate(list(message.available_peers.keys())):
                if available_peer == f"{self.socket_connector.ip_address}:{self.socket_connector.port}":
                    adjacent_index = index + 1
                    primary_node_index = index - 1
            if adjacent_index >= len(list(message.available_peers.keys())):
                adjacent_index = 0
            if primary_node_index < 0 and len(list(message.available_peers.keys())) > 1:
                primary_node_index = len(list(message.available_peers.keys())) -1
            if adjacent_index < 0:
                logger.info('Could not calculate valid adjacent_index')
                return
            if primary_node_index < 0:
                logger.info('Could not find node this node is neigbor to')
                return
            adjacent_key = list(message.available_peers.keys())[adjacent_index]
            primary_node_key = list(message.available_peers.keys())[primary_node_index]

            # check if node this node is neighbor to changed
            if not self.primary_node or primary_node_key != f"{self.primary_node.ip_address}:{self.primary_node.port}":
                # check if node this node was neighbor previously is dead
                if not self.primary_node or (self.primary_node and f"{self.primary_node.ip_address}:{self.primary_node.port}" not in list(message.available_peers.keys())):
                    # primary node is dead
                    self.primary_node = SocketConnector(primary_node_key.split(':')[0], int(primary_node_key.split(':')[1]))    # define new primary node
                    # push all backup chunks to primary_nodes primary chunks
                    for chunk_id in self.beez_node.backup_chunks:
                        with open(f"{self.beez_node.dam_asset_path}{chunk_id}", "rb") as infile:
                            chunk = infile.read()
                            logger.info('PUSHHHHHING')
                            self.push_chunk_to_node(chunk_id, chunk, self.primary_node)
                # check if there is a new node and thus this node is the neighbor of a new node now
                elif self.primary_node and f"{self.primary_node.ip_address}:{self.primary_node.port}" in list(message.available_peers.keys()):
                    self.primary_node = SocketConnector(primary_node_key.split(':')[0], int(primary_node_key.split(':')[1]))    # define new primary node
                    # delete all backup chunks as this node is not neighbor to the node we got backups from anymore
                    self.beez_node.backup_chunks = []

            # check if adjacent neighbor is already the neighbor
            if self.neighbor and adjacent_key == f"{self.neighbor.ip_address}:{self.neighbor.port}":
                logger.info('Already connected to correct neighbor')
                return
            
            # disconnect form current neighbor if exists
            if self.neighbor:
                self.disconnect_peer(self.neighbor)

            # connect to neighbor
            logger.info('connecting with neighbor')
            self.connect_with_adjacent_node(ip=adjacent_key.split(':')[0], port=adjacent_key.split(':')[1])
            self.neighbor = SocketConnector(adjacent_key.split(':')[0], int(adjacent_key.split(':')[1]))
            # push all asset chunks which this node is primary node to neighbor
            for chunk_id in self.beez_node.primary_chunks:
                with open(f"{self.beez_node.dam_asset_path}{chunk_id}", "rb") as infile:
                    chunk = infile.read()
                    self.push_chunk_to_neighbor(chunk_id, chunk)
        elif message.message_type == MessageType.HEALTHREQUEST:
            current_health = self.beez_node.node_health
            health_reply = MessageHealth(self.socket_connector, MessageType.HEALTH, current_health)
            encoded_health_reply_message: str = BeezUtils.encode(health_reply)
            self.send(node, encoded_health_reply_message)

    def push_chunk_to_node(self, chunk_id, chunk, node_socket_connector):
        logger.info('GOING TO PUSH CHUNKS TO NODE')
        primary_node = None
        for node in self.all_nodes:
            logger.info(f"Target: {node_socket_connector.ip_address}:{node_socket_connector.port}")
            logger.info(f"Node: {node.host}:{node.port}")
            if f"{node.host}:{node.port}" == f"{node_socket_connector.ip_address}:{node_socket_connector.port}":
                primary_node = node
        if primary_node:
            logger.info('SENDING CHUNK TO NODE')
            logger.info(chunk_id)
            chunk_message = MessagePushJunk(self.socket_connector, "push_junk", junk_id=chunk_id ,junk=chunk, chunk_type='primary')
            encoded_junk_message: str = BeezUtils.encode(chunk_message)
            self.send(primary_node, encoded_junk_message)

    def push_chunk_to_neighbor(self, chunk_id, chunk):
        neighbor_node = self.neighbor_node()
        if neighbor_node:
            chunk_message = MessagePushJunk(self.socket_connector, "push_junk", junk_id=chunk_id ,junk=chunk, chunk_type='backup')
            encoded_junk_message: str = BeezUtils.encode(chunk_message)
            self.send(neighbor_node, encoded_junk_message)
    
    def disconnect_peer(self, socket_connector: SocketConnector):
        """Disconnect form peer with socket connector."""
        nodes_to_disconnect: list[Node] = []
        for node in self.all_nodes:
            if f"{node.host}:{node.port}" == f"{socket_connector.ip_address}:{socket_connector.port}":
                nodes_to_disconnect.append(node)
        for node in nodes_to_disconnect:
            index_to_delete = -1
            for index,connection in enumerate(self.own_connections):
                if f"{node.host}:{node.port}" == f"{connection.ip_address}:{connection.port}":
                    index_to_delete = index
            if index_to_delete > -1:
                del self.own_connections[index_to_delete]
            if self.neighbor and f"{self.neighbor.ip_address}:{self.neighbor.port}" == f"{node.host}:{node.port}":
                self.neighbor = None
            self.own_connections.sort(key=lambda x: f"{x.ip_address}:{x.port}", reverse=True)
            self.node_disconnect_with_outbound_node(node)
