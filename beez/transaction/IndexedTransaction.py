from __future__ import annotations
from typing import TYPE_CHECKING, Optional
import uuid
import time
import copy

from loguru import logger

if TYPE_CHECKING:
    from .TransactionType import TransactionType
    from beez.Types import PublicKeyString, WalletAddress
    
from beez.transaction.Transaction import Transaction

class IndexedTransaction():
    """
    A Transaction represent the data that will spread betweeen network's peers
    """
    def __init__(self, senderPublicKey: PublicKeyString, receiverPublicKey: PublicKeyString, amount: int, type: TransactionType.name, blockCount: int, forger: PublicKeyString, lastHash:str, id: str, signature: PublicKeyString):
        
        self.senderPublicKey = senderPublicKey
        self.receiverPublicKey = receiverPublicKey
        self.amount = amount
        self.type = type
        self.id = id
        self.timestamp = time.time()
        self.signature = signature 
        self.blockCount = blockCount
        self.forger = forger
        self.lastHash = lastHash

    def toJson(self):
        jsonBlock = {}
        jsonBlock['id'] = self.id
        jsonBlock['senderPublicKey'] = self.senderPublicKey
        jsonBlock['receiverPublicKey'] = self.receiverPublicKey
        jsonBlock['amount'] = self.amount
        jsonBlock['type'] = self.type
        jsonBlock['timestamp'] = self.timestamp
        jsonBlock['signature'] = self.signature
        jsonBlock['blockCount'] = self.blockCount
        jsonBlock['forger'] = self.forger
        jsonBlock['lastHash'] = self.lastHash

        return jsonBlock

 
