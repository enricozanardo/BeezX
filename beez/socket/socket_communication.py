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

if TYPE_CHECKING:
    from beez.types import Address
    from beez.node.beez_node import BeezNode
    from beez.socket.message import Message


load_dotenv()  # load .env
LOCAL_TEST_IP = "192.168.1.209"
LOCAL_P2P_PORT = 8181  # 8122

FIRST_SERVER_IP = os.getenv("FIRST_SERVER_IP", LOCAL_TEST_IP)   # pylint: disable=invalid-envvar-default
P_2_P_PORT = int(os.getenv("P_2_P_PORT", LOCAL_P2P_PORT))   # pylint: disable=invalid-envvar-default


class SocketCommunication(Node):
    """
    This class manage the P2P communication.
    """

    def __init__(self, ip: Address, port: int):
        super(SocketCommunication, self).__init__(ip, port, None)   # pylint: disable=super-with-arguments
        self.own_connections: List[SocketConnector] = []
        self.peer_discovery_handler = PeerDiscoveryHandler(self)
        self.socket_connector = SocketConnector(ip, port)
        self.beez_node: Optional[BeezNode] = None

        logger.info(f"Socket Communication created.. {FIRST_SERVER_IP}: {P_2_P_PORT}")

    def connect_to_first_node(self):
        """Connects to first, hardcoded beez blockchain node."""
        logger.info(f"Check to connect to first node {FIRST_SERVER_IP} at port {P_2_P_PORT}")

        if (
            self.socket_connector.ip_address != FIRST_SERVER_IP
            or self.socket_connector.port != P_2_P_PORT
        ):
            # connect to the first node
            self.connect_with_node(FIRST_SERVER_IP, P_2_P_PORT)

    def start_socket_communication(self, beez_node: BeezNode):
        """Starts socket communication."""
        self.beez_node = beez_node
        self.start()
        self.peer_discovery_handler.start()
        self.connect_to_first_node()

    def broadcast(self, message: str):
        """Broadcast the message to all connected nodes."""
        self.send_to_nodes(message)

    def send(self, receiver: Node, message: str):
        """Send the message to a specific node."""
        self.send_to_node(receiver, message)

    def inbound_node_connected(self, node: Node):
        """Callback method of receiving requests from nodes."""
        logger.info("inbound connection (some node wants to connect to this node)")
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
            block: Block = Block.deserialize(message.block)
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
                f"A BLOCKCHAIN Message will be sent to the requester peer!! {message.message_type}"
            )
            blockchain: Blockchain = Blockchain.deserialize(message.serialized_blockchain)
            if self.beez_node:
                self.beez_node.handle_blockchain(blockchain)
            else:
                logger.info("Socket communication module has to node reference.")
