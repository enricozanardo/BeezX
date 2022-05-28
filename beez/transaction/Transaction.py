from __future__ import annotations
from typing import TYPE_CHECKING, Optional
import uuid
import time
import copy

from loguru import logger

if TYPE_CHECKING:
    from .TransactionType import TransactionType
    from beez.Types import PublicKeyString, WalletAddress


class Transaction():
    """
    A Transaction represent the data that will spread betweeen network's peers
    """

    def __init__(self, senderWalletAddress: WalletAddress, receiverWalletAddress: WalletAddress, amount: int, type: TransactionType):
        self.senderWalletAddress = senderWalletAddress
        self.receiverWalletAddress = receiverWalletAddress
        self.amount = amount
        self.type = type
        self.id = uuid.uuid1().hex
        self.timestamp = time.time()
        self.signature = '' # guarantee that only the owner can perform this tx
        
        logger.info(f"Transaction of type: {self.type.name} generated..")

    def sign(self, signature):
        self.signature = signature


    def equals(self, transaction: Transaction):
        if self.id == transaction.id:
            return True
        else:
            return False

    # TODO: get a consistent representation of the signed transaction
    
