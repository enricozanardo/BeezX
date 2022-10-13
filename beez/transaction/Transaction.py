"""Beez blockchain - transaction."""

from __future__ import annotations
from typing import TYPE_CHECKING
import uuid
import time
import copy


if TYPE_CHECKING:
    from .transaction_type import TransactionType
    from beez.types import PublicKeyString, WalletAddress


class Transaction:
    """
    A Transaction represent the data that will spread betweeen network's peers
    """

    def __init__(
        self,
        sender_public_key: PublicKeyString,
        receiver_public_key: PublicKeyString,
        amount: int,
        transaction_type: TransactionType.name,
    ):
        self.sender_public_key = sender_public_key
        self.receiver_public_key = receiver_public_key
        self.amount = amount
        self.transaction_type = transaction_type
        self.identifier = uuid.uuid1().hex
        self.timestamp = time.time()
        self.signature = ""  # guarantee that only the owner can perform this tx

    def sign(self, signature):
        """Signs the transaction."""
        self.signature = signature

    def to_json(self):
        """Converts the transaction to json."""
        json_block = {}
        json_block["id"] = self.identifier
        json_block["senderPublicKey"] = self.sender_public_key
        json_block["receiverPublicKey"] = self.receiver_public_key
        json_block["amount"] = self.amount
        json_block["type"] = self.transaction_type
        json_block["timestamp"] = self.timestamp
        json_block["signature"] = self.signature

        return json_block

    @staticmethod
    def from_json(json_block):
        """Creates a new transaction from a json serialization."""
        transaction = Transaction(
            sender_public_key=json_block["senderPublicKey"],
            receiver_public_key=json_block["receiverPublicKey"],
            amount=json_block["amount"],
            transaction_type=json_block["type"],
        )
        transaction.identifier = json_block["id"]
        transaction.timestamp = json_block["timestamp"]
        transaction.signature = json_block["signature"]
        return transaction

    def equals(self, transaction: Transaction):
        """Comparator."""
        if self.identifier == transaction.identifier:
            return True
        return False

    # get a consistent representation of the signed transaction
    def payload(self):
        """Returns the transactions payload without signature."""
        json_representation = copy.deepcopy(self.to_json())
        json_representation["signature"] = ""

        return json_representation
