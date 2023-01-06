"""Beez blockchain - own connections message"""

from __future__ import annotations
from typing import TYPE_CHECKING, List, Any

from beez.socket.message import Message
from beez.socket.message_type import MessageType

if TYPE_CHECKING:
    from beez.socket.socket_connector import SocketConnector


class MessageOwnConnections(Message):  # pylint: disable=too-few-public-methods
    """Own connections message"""

    def __init__(
        self,
        sender_connector: SocketConnector,
        message_type: MessageType,
        own_connections: List[SocketConnector],
        own_addresses: list[dict[str, str]],
    ):
        super().__init__(sender_connector, message_type)
        self.own_connections = own_connections
        self.own_addresses = own_addresses
