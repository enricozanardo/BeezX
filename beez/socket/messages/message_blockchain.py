"""Beez blockchain - message blockchain"""

from __future__ import annotations
from typing import TYPE_CHECKING, Any

from beez.socket.messages.message import Message
from beez.socket.messages.message_type import MessageType

if TYPE_CHECKING:
    from beez.socket.socket_connector import SocketConnector


class MessageBlockchain(Message):  # pylint: disable=too-few-public-methods
    """Message blockchain."""

    def __init__(
        self,
        sender_connector: SocketConnector,
        message_type: MessageType,
        serialized_blockchain: dict[str, Any],
    ):
        super().__init__(sender_connector, message_type)
        self.serialized_blockchain = serialized_blockchain
