"""Beez blockchain - base class for socket communication."""

from __future__ import annotations
from typing import TYPE_CHECKING, List
import os
from dotenv import load_dotenv
from loguru import logger
from p2pnetwork.node import Node    # type: ignore

from beez.socket.socket_connector import SocketConnector

if TYPE_CHECKING:
    from beez.types import Address


load_dotenv()  # load .env
LOCAL_TEST_IP = "192.168.1.209"
LOCAL_P2P_PORT = 5444

FIRST_SERVER_IP = os.getenv("FIRST_SERVER_IP", LOCAL_TEST_IP)   # pylint: disable=invalid-envvar-default
P_2_P_PORT = int(os.getenv("P_2_P_PORT", LOCAL_P2P_PORT))   # pylint: disable=invalid-envvar-default
LOCAL_INTERVALS = 10
INTERVALS = int(os.getenv("INTERVALS", LOCAL_INTERVALS))    # pylint: disable=invalid-envvar-default


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