"""Beez blockchain - peer discovery handler."""

from __future__ import annotations
from typing import TYPE_CHECKING, List
import threading
import time
import os
from loguru import logger
from dotenv import load_dotenv

from beez.socket.socket_connector import SocketConnector
from beez.socket.message_type import MessageType
from beez.socket.message_own_connections import MessageOwnConnections
from beez.beez_utils import BeezUtils

if TYPE_CHECKING:
    from beez.socket.socket_communication import SocketCommunication
    from p2pnetwork.node import Node    # type: ignore

load_dotenv()  # load .env
LOCAL_INTERVALS = 10
INTERVALS = int(os.getenv("INTERVALS", LOCAL_INTERVALS))    # pylint: disable=invalid-envvar-default


class PeerDiscoveryHandler:
    """
    A Socket Communication submodule that frequently checks if there are new peers in the network.
    """

    def __init__(self, socket_communication: SocketCommunication) -> None:
        self.socket_communication = socket_communication

    def start(self):
        """Starts the status thread and the discovery thread."""
        # start node threads...
        status_thread = threading.Thread(target=self.status, args={})
        status_thread.start()

        # discovery_thread = threading.Thread(target=self.discovery, args={})
        # discovery_thread.start()

    def status(self):
        """Display the nodes that are connected to a node"""
        while True:
            logger.info("Current connections:")
            for connection in self.socket_communication.own_connections:
                logger.info(f"Peer: {str(connection.ip_address)}:{str(connection.port)}")

            time.sleep(INTERVALS)

    def discovery(self):
        """Broadcasts discovery messages into the blockchain."""
        while True:
            logger.info("discovery")
            handshake_message = self.handshake_message()
            # Broadcast the message
            self.socket_communication.broadcast(handshake_message)

            time.sleep(INTERVALS)

    # send a message to a specific node
    def handshake(self, connected_node:Node):
        """
        exchange of information between nodes.
        """
        handshake_message = self.handshake_message()  # create the message of type DISCOVERY
        self.socket_communication.send(connected_node, handshake_message)

    def handshake_message(self):
        """
        Define the specific content of the Discovery message that will be shared between peers.
        Here, what is important is to share the knowed peers
        """
        own_connector = self.socket_communication.socket_connector
        own_connections = self.socket_communication.own_connections
        message_type = MessageType.DISCOVERY

        own_addresses = self.socket_communication.beez_node.get_registered_addresses()

        message = MessageOwnConnections(own_connector, message_type, own_connections, own_addresses)

        # Encode the message since peers communicate with bytes!
        encoded_message: str = BeezUtils.encode(message)

        return encoded_message

    def handle_message(self, message: MessageOwnConnections):
        """Handles message."""
        peer_socket_connector = message.sender_connector
        peer_connection_list: List[SocketConnector] = message.own_connections
        peer_addresses = message.own_addresses
        new_peer = True

        for connection in self.socket_communication.own_connections:
            if connection.equals(peer_socket_connector):
                # the node is itself
                new_peer = False

        if new_peer is True:
            # if is not itself add to the list of peers
            self.socket_communication.own_connections.append(peer_socket_connector)

        # Check if in the peersPeerList there are new peers and connect to them
        # for connection_peer in peer_connection_list:
        #     peer_known = False
        #     for connection in self.socket_communication.own_connections:
        #         if connection.equals(connection_peer):
        #             peer_known = True
        #     if not peer_known and not connection_peer.equals(
        #         self.socket_communication.socket_connector
        #     ):
        #         self.socket_communication.connect_with_node(
        #             connection_peer.ip_address, connection_peer.port
        #         )

        # Update addresses
        for address in peer_addresses:
            self.socket_communication.beez_node.handle_address_registration(
                address["public_key_pem"], False
            )
