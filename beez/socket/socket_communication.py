"""Beez blockchain - socket communication."""

from __future__ import annotations
import json
from typing import TYPE_CHECKING, List, Optional
import os
from dotenv import load_dotenv
from loguru import logger
from p2pnetwork.node import Node    # type: ignore

from beez.socket.socket_connector import SocketConnector
from beez.socket.peer_discovery_handler import PeerDiscoveryHandler
from beez.beez_utils import BeezUtils
from beez.socket.message_type import MessageType
from beez.transaction.transaction import Transaction
from beez.transaction.challenge_tx import ChallengeTX
from beez.block.blockchain import Blockchain
from beez.block.block import Block
from beez.socket.message_available_peers import MessageAvailablePeers

if TYPE_CHECKING:
    from beez.types import Address
    from beez.node.beez_node import BeezNode
    from beez.socket.message import Message


load_dotenv()  # load .env
LOCAL_TEST_IP = "192.168.1.209"
LOCAL_P2P_PORT = 5444

FIRST_SERVER_IP = os.getenv("FIRST_SERVER_IP", LOCAL_TEST_IP)   # pylint: disable=invalid-envvar-default
P_2_P_PORT = int(os.getenv("P_2_P_PORT", LOCAL_P2P_PORT))   # pylint: disable=invalid-envvar-default


class BaseSocketCommunication(Node):
    def __init__(self, ip: Address, port: int):
        super(BaseSocketCommunication, self).__init__(ip, port, None)   # pylint: disable=super-with-arguments
        self.own_connections: List[SocketConnector] = []
        self.socket_connector = SocketConnector(ip, port)

        logger.info(f"Socket Communication created.. {FIRST_SERVER_IP}: {P_2_P_PORT}")

    def start_socket_communication(self):
        """Starts socket communication."""
        self.start()

    def broadcast(self, message: str):
        """Broadcast the message to all connected nodes."""
        self.send_to_nodes(message)

    def send(self, receiver: Node, message: str):
        """Send the message to a specific node."""
        self.send_to_node(receiver, message)

class SeedSocketCommunication(BaseSocketCommunication):


    def check_health(self):
        # TODO: get current health status of each connected storage node
        pass

    def inbound_node_connected(self, node: Node):
        """Callback method of receiving requests from nodes."""
        logger.info("Storage node wants to connect - send list of peers")

        own_connector = self.socket_connector
        message_type = MessageType.DISCOVERY
        message_type = "request_peers"

        # calculate list of peers
        peers_list = {}
        for socket_connector in self.own_connections:
            peers_list[f"{socket_connector.ip_address}:{socket_connector.port}"] = 100   # TODO: calculate real health

        message = MessageAvailablePeers(own_connector, message_type, peers_list)

        # Encode the message since peers communicate with bytes!
        encoded_peers_message: str = BeezUtils.encode(message)

        new_peer = True
        node_socket_connector = SocketConnector(node.host, node.port)
        # node_socket_connector = SocketConnector(node.host, 5444)
        logger.info('GOT SOCKET CONNECTOR')
        logger.info(node_socket_connector.ip_address)
        logger.info(node_socket_connector.port)
        for connection in self.own_connections:
            if connection.equals(node_socket_connector):
                # the node is itself
                new_peer = False

        if new_peer is True:
            # if is not itself add to the list of peers
            self.own_connections.append(node_socket_connector)
    
        self.send(node, encoded_peers_message)


class SocketCommunication(BaseSocketCommunication):
    """
    This class manage the P2P communication.
    """

    def __init__(self, ip: Address, port: int):
        BaseSocketCommunication.__init__(self, ip, port)   # pylint: disable=super-with-arguments
        self.peer_discovery_handler = PeerDiscoveryHandler(self)
        self.beez_node: Optional[BeezNode] = None

    def connect_to_first_node(self):
        """Connects to first, hardcoded beez blockchain node."""
        logger.info(f"Check to connect to first node {FIRST_SERVER_IP} at port {P_2_P_PORT}")

        if (
            self.socket_connector.ip_address != FIRST_SERVER_IP
            or self.socket_connector.port != P_2_P_PORT
        ):
            # connect to the first node
            self.connect_with_node(FIRST_SERVER_IP, P_2_P_PORT)

    def connect_with_adjacent_node(self, ip, port):
        logger.info(f"Check to connect to neighbor node {ip} at port {port}")

        if (
            self.socket_connector.ip_address != ip
            or self.socket_connector.port != port
        ):
            # connect to adjacent neighbor node
            connection_to_neighbor = False
            while not connection_to_neighbor:
                logger.info("connecting with node")
                connection_to_neighbor = self.connect_with_node(ip, port)
                logger.info(connection_to_neighbor)
            

    def start_socket_communication(self, beez_node: BeezNode):
        """Starts socket communication."""
        self.beez_node = beez_node
        self.start()
        self.peer_discovery_handler.start()
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
        elif message.message_type == 'request_peers':
            logger.info(100*'##')
            logger.info('got list of available peers from seed node')
            logger.info(message.available_peers)
            logger.info('calculate adjacent node')
            logger.info('adjacent node is ')
            self.own_connections.append(message.sender_connector)
            if list(message.available_peers.keys()):
                adjacent_key = list(message.available_peers.keys())[-1]
                logger.info(message.available_peers[adjacent_key])
                logger.info('connecting with neighbor')
                self.connect_with_adjacent_node(ip=adjacent_key.split(':')[0], port=adjacent_key.split(':')[1])
            else:
                logger.info('there is no node yet')
        elif message.message_type == 'request_health':
            logger.info(100*'-')
            logger.info('seed node is requesting health')
            logger.info(message)

