"""Beez blockchain - socket connector."""

from __future__ import annotations
from typing import TYPE_CHECKING, TypeVar

SelfSocketConnector = TypeVar("SelfSocketConnector", bound="SocketConnector")

if TYPE_CHECKING:
    from beez.Types import Address


class SocketConnector:      # pylint: disable=too-few-public-methods
    """
    keep information about the ip and port of a node
    """

    def __init__(self, ip_address: Address, port: int):
        self.ip_address = ip_address
        self.port = port

    def equals(self, connector: SelfSocketConnector):
        """Returns whether a connector equals this."""
        if connector.ip_address == self.ip_address and connector.port == self.port:
            # logger.info(f"The node is itsef!")
            return True
        return False
