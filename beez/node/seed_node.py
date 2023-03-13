"""Beez blockchain - beez seed node."""

from __future__ import annotations
import os
from dotenv import load_dotenv

from beez.socket.socket_communication.seed_socket_communication import (
    SeedSocketCommunication,
)
from beez.api.node_api import SeedNodeAPI
from beez.node.beez_node import BasicNode

load_dotenv()  # load .env
P_2_P_PORT = int(os.getenv("P_2_P_PORT", 8122))  # pylint: disable=invalid-envvar-default


class SeedNode(BasicNode):
    """Beez Seed Node class."""

    def __init__(self, key=None, ip=None, port=None) -> None:
        BasicNode.__init__(
            self, key=key, ip=ip, port=port, communication_protocol=SeedSocketCommunication
        )
        self.start_network_health_scans()

    def start_api(self, port=None):
        """Starts the nodes API."""
        self.api = SeedNodeAPI()
        # Inject Node to NodeAPI
        self.api.inject_node(self)
        self.api.start(self.ip_address, port)

    def start_network_health_scans(self):
        """Starts the network scans for Beez Node health discovery."""
        self.p2p.network_health_scan()

    def stop(self):
        self.p2p.health_checks_active = False
        self.p2p.stop()
