from __future__ import annotations
from p2pnetwork.node import Node
import os
from dotenv import load_dotenv
from loguru import logger
from typing import TYPE_CHECKING, List


if TYPE_CHECKING:
    from beez.Types import Address
    from beez.node.BeezNode import BeezNode
    
from beez.socket.SocketConnector import SocketConnector
from beez.socket.PeerDiscoveryHandler import PeerDiscoveryHandler

load_dotenv()  # load .env
LOCAL_TEST_IP = '192.168.1.209'
LOCAL_P2P_PORT = 8181 # 8122

FIRST_SERVER_IP = os.getenv('FIRST_SERVER_IP', LOCAL_TEST_IP)
P_2_P_PORT = int(os.getenv('P_2_P_PORT', LOCAL_P2P_PORT))


class SocketCommunication(Node):
    """
    This class manage the P2P communication.
    """

    def __init__(self, ip: Address, port: int):
        super(SocketCommunication, self).__init__(ip, port, None)
        # TODO: move the peers to a storage!
        self.ownConnections: List[SocketConnector] = []
        self.peerDiscoveryHandler = PeerDiscoveryHandler(self)
        self.socketConnector = SocketConnector(ip, port)

        logger.info(f"Socket Communication created.. {FIRST_SERVER_IP}: {P_2_P_PORT}")

    def connectToFirstNode(self):
        logger.info(f"Check to connect to first node {FIRST_SERVER_IP} at port {P_2_P_PORT}")

        if self.socketConnector.ip != FIRST_SERVER_IP or self.socketConnector.port != P_2_P_PORT:
         # connect to the first node
            self.connect_with_node(FIRST_SERVER_IP, P_2_P_PORT)
    
    def startSocketCommunication(self, beezNode: BeezNode):
        self.beezNode = beezNode
        self.start()
        self.peerDiscoveryHandler.start()
        self.connectToFirstNode()

    # Broadcast the message to alle the nodes
    def broadcast(self, message: str):
        self.send_to_nodes(message)

    # Send the message to a specific node
    def send(self, receiver: Node, message: str):
        self.send_to_node(receiver, message)

    # Callback method of receiving requests from nodes
    def inbound_node_connected(self, connectedNode: Node):
        logger.info(
            f"inbound connection (some node wants to connect to this node)")
        self.peerDiscoveryHandler.handshake(connectedNode)

    # Callback method of sending requests to nodes
    def outbound_node_connected(self, connectedNode: Node):
        logger.info(
            f"outbound connection (this node wants to connect to other node)")
        self.peerDiscoveryHandler.handshake(connectedNode)