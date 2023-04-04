"""Beez blockchain - message chunk reply."""

from __future__ import annotations
from typing import TYPE_CHECKING

from beez.socket.messages.message import Message
from beez.socket.messages.message_type import MessageType

if TYPE_CHECKING:
    from beez.socket.socket_connector import SocketConnector
    from beez.block.block import Block


class MessageChunkReply(Message):  # pylint: disable=too-few-public-methods
    """Message chunk reply."""

    def __init__(
        self,
        sender_connector: SocketConnector,
        message_type: MessageType,
        file_name: str,
        chunk_name: str,
        chunk: str
    ):
        super().__init__(sender_connector, message_type)
        self.file_name = file_name
        self.chunk_name = chunk_name
        self.chunk = chunk
        
