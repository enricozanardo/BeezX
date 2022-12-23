"""Beez blockchain - message address registration"""

from __future__ import annotations
from typing import TYPE_CHECKING

from beez.socket.message import Message
from beez.socket.message_type import MessageType

if TYPE_CHECKING:
    from beez.socket.socket_connector import SocketConnector
    from beez.block.block import Block


class MessageAddressRegistration(Message):  # pylint: disable=too-few-public-methods
    """Message address registration."""

    def __init__(self, sender_connector: SocketConnector, message_type: MessageType, public_key_hex: str, address: str):
        super().__init__(sender_connector, message_type)
        self.public_key_hex = public_key_hex
        self.address = address
