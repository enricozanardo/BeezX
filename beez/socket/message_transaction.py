"""Beez blockchain - transaction message."""

from __future__ import annotations
from typing import TYPE_CHECKING

from beez.socket.message import Message
from beez.socket.message_type import MessageType

if TYPE_CHECKING:
    from beez.socket.socket_connector import SocketConnector
    from beez.transaction.Transaction import Transaction


class MessageTransation(Message):   # pylint: disable=too-few-public-methods
    """Transaction message"""

    def __init__(
        self, sender_connector: SocketConnector, message_type: MessageType, transaction: Transaction
    ):
        super().__init__(sender_connector, message_type)
        self.transaction = transaction
