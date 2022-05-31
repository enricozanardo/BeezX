from __future__ import annotations
from typing import TYPE_CHECKING, Optional
import uuid
import time
import copy

from loguru import logger

if TYPE_CHECKING:
    from .TransactionType import TransactionType
    from beez.Types import WalletAddress, PublicKeyString

from beez.transaction.Transaction import Transaction
from beez.block.Block import Block

class BlockTX(Transaction):

    def __init__(self, senderPublicKey: PublicKeyString, receiverPublicKey: PublicKeyString, amount: int, type: TransactionType.name, block: Block):
        super().__init__(senderPublicKey, receiverPublicKey, amount, type)
        self.block = block

    def toJson(self):
        jsonBlock = {}
        jsonBlock['id'] = self.id
        jsonBlock['senderPublicKey'] = self.senderPublicKey
        jsonBlock['receiverPublicKey'] = self.receiverPublicKey
        jsonBlock['amount'] = self.amount
        jsonBlock['type'] = self.type
        jsonBlock['timestamp'] = self.timestamp
        jsonBlock['signature'] = self.signature
        jsonBlock['block'] = {}
        
        return jsonBlock