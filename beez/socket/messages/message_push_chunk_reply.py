"""Beez blockchain - message digital asset chunk."""

from __future__ import annotations
from typing import TYPE_CHECKING

from beez.socket.messages.message import Message
from beez.socket.messages.message_type import MessageType

if TYPE_CHECKING:
    from beez.socket.socket_connector import SocketConnector
    from beez.block.block import Block


class MessagePushChunkReply(Message):  # pylint: disable=too-few-public-methods
    """Message reply on push digital asset chunk."""

    def __init__(
        self,
        sender_connector: SocketConnector,
        message_type: MessageType,
        chunk_id: str,
        ack: bool
    ):
        super().__init__(sender_connector, message_type)
        self.chunk_id = chunk_id
        self.ack = ack
        
