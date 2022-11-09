from __future__ import annotations
import re
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

    def __init__(self, senderPublicKey: PublicKeyString, receiverPublicKey: PublicKeyString, amount: int, type: TransactionType.name):
        self.senderPublicKey = senderPublicKey
        self.receiverPublicKey = receiverPublicKey
        self.amount = amount
        self.type = type
        self.id = uuid.uuid1().hex
        self.timestamp = time.time()
        self.signature = '' # guarantee that only the owner can perform this tx
        

    def sign(self, signature):
        self.signature = signature

    def toJson(self):
        jsonBlock = {}
        jsonBlock['id'] = self.id
        jsonBlock['senderPublicKey'] = self.senderPublicKey
        jsonBlock['receiverPublicKey'] = self.receiverPublicKey
        jsonBlock['amount'] = self.amount
        jsonBlock['type'] = self.type
        jsonBlock['timestamp'] = self.timestamp
        jsonBlock['signature'] = self.signature

        return jsonBlock

    @staticmethod
    def fromJson(jsonBlock):
        tx = Transaction(senderPublicKey=jsonBlock["senderPublicKey"], receiverPublicKey=jsonBlock["receiverPublicKey"], amount=jsonBlock['amount'], type=jsonBlock["type"])
        tx.id = jsonBlock['id']
        tx.timestamp = jsonBlock['timestamp']
        tx.signature = jsonBlock['signature']
        return tx

    def equals(self, transaction: Transaction):
        if self.id == transaction.id:
            return True
        else:
            return False

    # get a consistent representation of the signed transaction
    def payload(self):
        jsonRepresentation = copy.deepcopy(self.toJson())
        jsonRepresentation['signature'] = ''

        return jsonRepresentation
