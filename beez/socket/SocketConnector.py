from __future__ import annotations
from typing import TYPE_CHECKING, TypeVar
from loguru import logger

SelfSocketConnector = TypeVar("SelfSocketConnector", bound="SocketConnector")

if TYPE_CHECKING:
    from beez.Types import Address

class SocketConnector():
    """
    keep information about the ip and port of a node
    """

    def __init__(self, ip: Address, port: int):
        self.ip = ip
        self.port = port

    def equals(self, connector: SelfSocketConnector):
        if connector.ip == self.ip and connector.port == self.port:
            # logger.info(f"The node is itsef!")
            return True
        else:
            return False