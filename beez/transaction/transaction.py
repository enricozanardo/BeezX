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
        sender_address: WalletAddress,
        receiver_address: WalletAddress,
        amount: int,
        transaction_type: TransactionType,
        public_key: PublicKeyString
    ):
        self.sender_address = sender_address
        self.receiver_address = receiver_address
        self.amount = amount
        self.transaction_type = transaction_type
        self.identifier = uuid.uuid1().hex
        self.timestamp = time.time()
        self.public_key = public_key
        self.signature = ""  # guarantee that only the owner can perform this tx

    def sign(self, signature):
        """Signs the transaction."""
        self.signature = signature

    def to_json(self):
        """Converts the transaction to json."""
        json_block = {}
        json_block["id"] = self.identifier
        json_block["senderAddress"] = self.sender_address
        json_block["receiverAddress"] = self.receiver_address
        json_block["amount"] = self.amount
        json_block["type"] = self.transaction_type
        json_block["timestamp"] = self.timestamp
        json_block["signature"] = self.signature
        json_block["public_key"] = self.public_key

        return json_block

    @staticmethod
    def from_json(json_block):
        """Creates a new transaction from a json serialization."""
        transaction = Transaction(
            sender_address=json_block["senderAddress"],
            receiver_address=json_block["receiverAddress"],
            amount=json_block["amount"],
            transaction_type=json_block["type"],
            public_key=json_block["public_key"],
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
