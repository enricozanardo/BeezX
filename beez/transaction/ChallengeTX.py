from __future__ import annotations
from typing import TYPE_CHECKING, Optional
import uuid
import time
import copy

from loguru import logger

if TYPE_CHECKING:
    from .TransactionType import TransactionType
    from beez.Types import WalletAddress

from beez.transaction.Transaction import Transaction
from beez.challenge.Challenge import Challenge

class ChallengeTX(Transaction):

    def __init__(self, senderWalletAddress: WalletAddress, receiverWalletAddress: WalletAddress, amount: int, type: TransactionType, challenge: Challenge):
        super().__init__(senderWalletAddress, receiverWalletAddress, amount, type)
        self.challenge = challenge

    
    def toJson(self):
        jsonBlock = {}
        jsonBlock['id'] = self.id
        jsonBlock['senderWalletAddress'] = self.senderWalletAddress
        jsonBlock['receiverWalletAddress'] = self.receiverWalletAddress
        jsonBlock['amount'] = self.amount
        jsonBlock['type'] = self.type.name
        jsonBlock['timestamp'] = self.timestamp
        jsonBlock['signature'] = self.signature
        jsonBlock['challenge'] = {
            "workers": ["w1", "w2"],
            "enrolment": "Mon 30.06.2022@23:59"
        }
        
        
        return jsonBlock
