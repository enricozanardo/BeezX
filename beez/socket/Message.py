"""Beez blockchain - message"""
from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from beez.socket.message_type import MessageType
    from beez.socket.socket_connector import SocketConnector


class Message:  # pylint: disable=too-few-public-methods
    """
    Represent the message that can be trasmitted in the network
    """

    def __init__(self, sender_connector: SocketConnector, message_type: MessageType):
        self.sender_connector = sender_connector
        self.message_type = message_type
