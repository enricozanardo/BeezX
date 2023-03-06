"""Beez blockchain - asking for health status of nodes"""

from __future__ import annotations
from typing import TYPE_CHECKING

from beez.socket.messages.message import Message
from beez.socket.messages.message_type import MessageType

if TYPE_CHECKING:
    from beez.socket.socket_connector import SocketConnector


class MessageHealthRequest(Message):  # pylint: disable=too-few-public-methods
    """Request current health status of node"""

    def __init__(    # pylint: disable=useless-parent-delegation
        self,
        sender_connector: SocketConnector,
        message_type: MessageType,
    ):
        super().__init__(sender_connector, message_type)
