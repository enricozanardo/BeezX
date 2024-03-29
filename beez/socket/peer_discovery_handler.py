"""Beez blockchain - peer discovery handler."""

from __future__ import annotations
from typing import TYPE_CHECKING
import time
import os
from loguru import logger
from dotenv import load_dotenv

from beez.socket.messages.message_type import MessageType
from beez.socket.messages.message_own_connections import MessageOwnConnections
from beez.beez_utils import BeezUtils

if TYPE_CHECKING:
    from beez.socket.socket_communication.socket_communication import SocketCommunication
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
        peer_addresses = message.own_addresses
        new_peer = True

        for connection in self.socket_communication.own_connections:
            if connection.equals(peer_socket_connector):
                # the node is itself
                new_peer = False

        if new_peer is True:
            # if is not itself add to the list of peers
            self.socket_communication.own_connections.append(peer_socket_connector)

        # Update addresses
        for address in peer_addresses:
            self.socket_communication.beez_node.handle_address_registration(
                address["public_key_pem"], False
            )
