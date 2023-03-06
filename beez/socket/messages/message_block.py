"""Beez blockchain - message block"""

from __future__ import annotations
from typing import TYPE_CHECKING

from beez.socket.messages.message import Message
from beez.socket.messages.message_type import MessageType

if TYPE_CHECKING:
    from beez.socket.socket_connector import SocketConnector
    from beez.block.block import Block


class MessageBlock(Message):  # pylint: disable=too-few-public-methods
    """Message block."""

    def __init__(self, sender_connector: SocketConnector, message_type: MessageType, block: Block):
        super().__init__(sender_connector, message_type)
        self.block = block
