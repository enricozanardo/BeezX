"""Beez blockchain - challenge message."""

from __future__ import annotations
from typing import TYPE_CHECKING

from beez.socket.messages.message import Message
from beez.socket.messages.message_type import MessageType

if TYPE_CHECKING:
    from beez.socket.socket_connector import SocketConnector
    from beez.challenge.challenge import Challenge


class MessageChallenge(Message):  # pylint: disable=too-few-public-methods
    """Challenge message."""

    def __init__(
        self, sender_connector: SocketConnector, message_type: MessageType, challenge: Challenge
    ):
        super().__init__(sender_connector, message_type)
        self.challenge = challenge
