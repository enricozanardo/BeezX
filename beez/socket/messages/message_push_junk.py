"""Beez blockchain - message digital asset junk."""

from __future__ import annotations
from typing import TYPE_CHECKING

from beez.socket.messages.message import Message
from beez.socket.messages.message_type import MessageType

if TYPE_CHECKING:
    from beez.socket.socket_connector import SocketConnector
    from beez.block.block import Block


class MessagePushJunk(Message):  # pylint: disable=too-few-public-methods
    """Message push digital asset junk."""

    def __init__(
        self,
        sender_connector: SocketConnector,
        message_type: MessageType,
        junk_id: str,
        junk: str
    ):
        super().__init__(sender_connector, message_type)
        self.junk_id = junk_id
        self.junk = junk
        
