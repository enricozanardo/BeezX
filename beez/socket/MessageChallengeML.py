from __future__ import annotations
from typing import TYPE_CHECKING, List

if TYPE_CHECKING:
    from beez.socket.SocketConnector import SocketConnector
    from beez.challenge.MLChallenge import MLChallenge
    
from beez.socket.Message import Message
from beez.socket.MessageType import MessageType

class MessageChallengeML(Message):

    def __init__(self, senderConnector: SocketConnector, messageType: MessageType, challenge: MLChallenge):
        super().__init__(senderConnector, messageType)
        self.challenge = challenge