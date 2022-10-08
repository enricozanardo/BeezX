from __future__ import annotations
from tarfile import BLOCKSIZE
from typing import TYPE_CHECKING, List

if TYPE_CHECKING:
    from beez.socket.SocketConnector import SocketConnector
    from beez.block.blockchain import Blockchain

from beez.socket.Message import Message
from beez.socket.MessageType import MessageType

class MessageBlockchain(Message):

    def __init__(self, senderConnector: SocketConnector, messageType: MessageType, serialized_blockchain):
        super().__init__(senderConnector, messageType)
        self.serialized_blockchain = serialized_blockchain