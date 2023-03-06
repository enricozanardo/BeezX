"""Beez blockchain - available peers message"""

from __future__ import annotations
from typing import TYPE_CHECKING

from beez.socket.messages.message import Message
from beez.socket.messages.message_type import MessageType

if TYPE_CHECKING:
    from beez.socket.socket_connector import SocketConnector


class MessageAvailablePeers(Message):  # pylint: disable=too-few-public-methods
    """Available peers message"""

    def __init__(   # pylint: disable=dangerous-default-value
        self,
        sender_connector: SocketConnector,
        message_type: MessageType,
        available_peers: dict[str,int],
        dead_peers: list[str] = []
    ):
        super().__init__(sender_connector, message_type)
        self.available_peers = available_peers
        self.dead_peers = dead_peers
