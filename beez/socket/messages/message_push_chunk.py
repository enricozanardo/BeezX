"""Beez blockchain - message digital asset chunk."""

from __future__ import annotations
from typing import TYPE_CHECKING

from beez.socket.messages.message import Message
from beez.socket.messages.message_type import MessageType

if TYPE_CHECKING:
    from beez.socket.socket_connector import SocketConnector
    from beez.block.block import Block


class MessagePushChunk(Message):  # pylint: disable=too-few-public-methods
    """Message push digital asset chunk."""

    def __init__(
        self,
        sender_connector: SocketConnector,
        message_type: MessageType,
        chunk_id: str,
        chunk: str,
        chunk_type: str
    ):
        super().__init__(sender_connector, message_type)
        self.chunk_id = chunk_id
        self.chunk = chunk
        self.chunk_type = chunk_type
        
