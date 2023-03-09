"""Beez blockchain - message junk reply."""

from __future__ import annotations
from typing import TYPE_CHECKING

from beez.socket.messages.message import Message
from beez.socket.messages.message_type import MessageType

if TYPE_CHECKING:
    from beez.socket.socket_connector import SocketConnector
    from beez.block.block import Block


class MessageJunkReply(Message):  # pylint: disable=too-few-public-methods
    """Message junk reply."""

    def __init__(
        self,
        sender_connector: SocketConnector,
        message_type: MessageType,
        file_name: str,
        junk_name: str,
        junk: str
    ):
        super().__init__(sender_connector, message_type)
        self.file_name = file_name
        self.junk_name = junk_name
        self.junk = junk
        
