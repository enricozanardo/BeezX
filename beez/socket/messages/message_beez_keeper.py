"""Beez blockchain - beez keeper message"""

from __future__ import annotations
from typing import TYPE_CHECKING

from beez.socket.messages.message import Message
from beez.socket.messages.message_type import MessageType

if TYPE_CHECKING:
    from beez.socket.socket_connector import SocketConnector
    from beez.challenge.beez_keeper import BeezKeeper


class MessageBeezKeeper(Message):    # pylint: disable=too-few-public-methods
    """Beez Keeper message."""

    def __init__(
        self, sender_connector: SocketConnector, message_type: MessageType, beez_keeper: BeezKeeper
    ):
        super().__init__(sender_connector, message_type)
        self.beez_keeper = beez_keeper
