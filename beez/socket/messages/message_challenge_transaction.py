"""Beez blockchain - challenge transaction mesage."""

from __future__ import annotations
from typing import TYPE_CHECKING

from beez.socket.messages.message import Message
from beez.socket.messages.message_type import MessageType

if TYPE_CHECKING:
    from beez.socket.socket_connector import SocketConnector
    from beez.transaction.challenge_tx import ChallengeTX


class MessageChallengeTransation(Message):      # pylint: disable=too-few-public-methods
    """Challenge transaction message."""

    def __init__(
        self,
        sender_connector: SocketConnector,
        message_type: MessageType,
        challenge_tx: ChallengeTX,
    ):
        super().__init__(sender_connector, message_type)
        self.challenge_tx = challenge_tx
