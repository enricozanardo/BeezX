from __future__ import annotations
from typing import TYPE_CHECKING, List

if TYPE_CHECKING:
    from beez.socket.SocketConnector import SocketConnector
    from beez.Types import ChallengeID 
    
from beez.socket.Message import Message
from beez.socket.MessageType import MessageType

class MessageChallengeID(Message):

    def __init__(self, senderConnector: SocketConnector, messageType: MessageType, challengeID: ChallengeID):
        super().__init__(senderConnector, messageType)
        self.challengeID = challengeID