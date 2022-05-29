from __future__ import annotations
from typing import TYPE_CHECKING, List

if TYPE_CHECKING:
    from beez.socket.SocketConnector import SocketConnector
    from beez.transaction.Transaction import Transaction


from beez.socket.Message import Message
from beez.socket.MessageType import MessageType

class MessageTransation(Message):

    def __init__(self, senderConnector: SocketConnector, messageType: MessageType, transaction: Transaction):
        super().__init__(senderConnector, messageType)
        self.transaction = transaction