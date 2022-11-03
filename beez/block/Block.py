"""Beez Blockchain - Block."""

from __future__ import annotations
from typing import TYPE_CHECKING, List, Optional, cast
import time
import copy
import json

from beez.transaction.transaction_type import TransactionType
from beez.transaction.Transaction import Transaction
from beez.block.Header import Header
from beez.Types import PublicKeyString

if TYPE_CHECKING:
    from beez.transaction.challenge_tx import ChallengeTX



class Block:
    """
    A Block contain a list of Transaction that are validated from a Forger into the Network.
    """

    def __init__(   # pylint: disable=too-many-arguments
        self,
        header: Optional[Header],
        transactions: List[Transaction],
        last_hash: str,
        forger: PublicKeyString,
        block_count: int,
    ):
        self.header = header
        self.transactions = transactions
        self.last_hash = last_hash
        self.forger = forger
        self.block_count = block_count
        self.timestamp = time.time()
        self.signature = ""

    @staticmethod
    def genesis() -> Block:
        """Returning a predefined genesis block."""
        genesis_block = Block(
            None,
            [],
            "Hello Beezkeepers! 🐝",
            cast(PublicKeyString, "BeezAuthors: Enrico Zanardo 🤙🏽 & ⭐"),
            0,
        )
        genesis_block.timestamp = (
            0  # every node will start with the same genesis Block
        )
        return genesis_block

    def serialize(self):
        """Serializing the block to json."""
        block_serialized = {
            "header": self.header.serialize() if self.header else "",
            "transactions": [tx.to_json() for tx in self.transactions],
            "lastHash": self.last_hash,
            "forger": self.forger,
            "blockCount": self.block_count,
            "timestamp": self.timestamp,
            "signature": self.signature,
        }
        return block_serialized

    @staticmethod
    def deserialize(serialized_block, index=True):
        """Recreating a block object from a serialized blockchain json."""
        serialized_block = json.loads(str(serialized_block).replace("'", '"'))
        block = Block(
            header=Header.deserialize(
                serialized_block["header"]["beezKeeper"],
                serialized_block["header"]["accountStateModel"],
                index,
            )
            if serialized_block["header"] != ""
            else None,
            transactions=[
                Transaction.from_json(tx_json)
                for tx_json in serialized_block["transactions"]
            ],
            last_hash=serialized_block["lastHash"],
            forger=serialized_block["forger"],
            block_count=serialized_block["blockCount"],
        )
        block.timestamp = serialized_block["timestamp"]
        block.signature = serialized_block["signature"]
        return block

    def to_json(self):
        """Converting the block to json."""
        json_block = {}
        json_block["lastHash"] = self.last_hash
        json_block["forger"] = self.forger
        json_block["blockCount"] = self.block_count
        json_block["timestamp"] = self.timestamp
        json_block["signature"] = self.signature
        transactions = []

        for transaction in self.transactions:
            if transaction.transaction_type == TransactionType.CHALLENGE:
                challenge_tx: ChallengeTX = transaction
                transactions.append(challenge_tx.to_json())
            else:
                transactions.append(transaction.to_json())

        json_block["transactions"] = transactions

        return json_block

    def payload(self):
        """Returning the payload of the block only without the signature."""
        json_representation = copy.deepcopy(self.to_json())
        json_representation["signature"] = ""

        return json_representation

    def sign(self, signature):
        """Signing the block by setting the block's signature."""
        self.signature = signature
