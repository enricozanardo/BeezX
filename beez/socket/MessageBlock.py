from __future__ import annotations
from typing import TYPE_CHECKING, List

if TYPE_CHECKING:
    from beez.socket.SocketConnector import SocketConnector
    from beez.block.Block import Block

from beez.socket.Message import Message
from beez.socket.MessageType import MessageType

class MessageBlock(Message):

    def __init__(self, senderConnector: SocketConnector, messageType: MessageType, block: Block):
        super().__init__(senderConnector, messageType)
        self.block = block