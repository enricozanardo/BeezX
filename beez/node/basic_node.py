"""Beez blockchain - basic node."""

from __future__ import annotations
from typing import TYPE_CHECKING
import os
import socket
from dotenv import load_dotenv
from loguru import logger

from beez.wallet.wallet import Wallet
from beez.socket.socket_communication.base_socket_communication import (
    BaseSocketCommunication,
)

if TYPE_CHECKING:
    from beez.types import Address

load_dotenv()  # load .env
P_2_P_PORT = int(os.getenv("P_2_P_PORT", 8122))  # pylint: disable=invalid-envvar-default


class BasicNode:
    """Base class for Beez Nodes."""
    def __init__(
        self,
        key=None,
        port=None,
        communication_protocol: BaseSocketCommunication = BaseSocketCommunication,
    ) -> None:
        self.api = None
        self.ip_address = self.get_ip()
        self.port = int(P_2_P_PORT)
        self.wallet = Wallet()
        self.p2p = communication_protocol(self.ip_address, port if port else self.port)

        if key is not None:
            self.wallet.from_key(key)

    def get_ip(self) -> Address:
        """Return IP of node."""
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            sock.connect(("8.8.8.8", 53))
            node_address: Address = sock.getsockname()[0]
            logger.info(f"Node IP: {node_address}")

            return node_address

    def start_p2p(self):
        """Starts the peer to peer communication."""
        self.p2p.start_socket_communication()
