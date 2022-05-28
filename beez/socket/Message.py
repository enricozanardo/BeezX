from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from beez.socket.MessageType import MessageType  
    from beez.socket.SocketConnector import SocketConnector

class Message():
    """
    Represent the message that can be trasmitted in the network
    """
    def __init__(self, senderConnector: SocketConnector, messageType: MessageType):
        self.senderConnector = senderConnector
        self.messageType = messageType