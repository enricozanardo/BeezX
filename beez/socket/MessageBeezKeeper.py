from __future__ import annotations
from typing import TYPE_CHECKING, List

if TYPE_CHECKING:
    from beez.socket.SocketConnector import SocketConnector
    from beez.challenge.BeezKeeper import BeezKeeper

from beez.socket.Message import Message
from beez.socket.MessageType import MessageType

class MessageBeezKeeper(Message):

    def __init__(self, senderConnector: SocketConnector, messageType: MessageType, beezKeeper: BeezKeeper):
        super().__init__(senderConnector, messageType)
        self.beezKeeper = beezKeeper