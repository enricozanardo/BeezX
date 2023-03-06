"""Beez blockchain - inform about current health status"""

from __future__ import annotations
from typing import TYPE_CHECKING

from beez.socket.messages.message import Message
from beez.socket.messages.message_type import MessageType

if TYPE_CHECKING:
    from beez.socket.socket_connector import SocketConnector


class MessageHealth(Message):  # pylint: disable=too-few-public-methods
    """Inform about current health status."""

    def __init__(
        self,
        sender_connector: SocketConnector,
        message_type: MessageType,
        health_status: int
    ):
        super().__init__(sender_connector, message_type)
        self.health_status = health_status
