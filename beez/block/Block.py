from __future__ import annotations
from typing import TYPE_CHECKING, List, Optional
import time
import copy
import json

from loguru import logger
from beez.challenge.BeezKeeper import BeezKeeper
from beez.transaction.Transaction import Transaction
from beez.block.Header import Header

if TYPE_CHECKING:
    from beez.transaction.ChallengeTX import ChallengeTX
    from beez.wallet.Wallet import Wallet
    from beez.Types import WalletAddress, PublicKeyString

from beez.transaction.TransactionType import TransactionType
import jsonpickle

class Block():
    """
    A Block contain a list of Transaction that are validated from a Forger into the Network.
    """
    def __init__(self, header: Optional[Header], transactions: List[Transaction], lastHash: str, forger: PublicKeyString, blockCount: int):
        self.header = header
        self.transactions = transactions
        self.lastHash = lastHash
        self.forger = forger
        self.blockCount = blockCount
        self.timestamp = time.time()
        self.signature = ''

    @staticmethod
    def genesis() -> Block:
        genesisBlock = Block(None, [], 'Hello Beezkeepers! 🐝', 'BeezAuthors: Enrico Zanardo 🤙🏽 & ⭐', 0)
        genesisBlock.timestamp = 0 # every node will start with the same genesis Block
        return genesisBlock

    def serialize(self):
        return {
            "header": self.header.serialize() if self.header else "",
            "transactions": [tx.toJson() for tx in self.transactions],
            "lastHash": self.lastHash,
            "forger": self.forger,
            "blockCount": self.blockCount,
            "timestamp": self.timestamp,
            "signature": self.signature
        }

    @staticmethod
    def deserialize(serialized_block, index=True):
        print("DESERIALIZE BLOCK")
        serialized_block = json.loads(serialized_block.replace("'", "\""))
        block = Block(
            header=Header.deserialize(serialized_block["header"]["beezKeeper"], serialized_block["header"]["accountStateModel"], index) if serialized_block["header"] != "" else None,
            transactions=[Transaction.fromJson(tx_json) for tx_json in serialized_block["transactions"]],
            lastHash=serialized_block["lastHash"],
            forger=serialized_block["forger"],
            blockCount=serialized_block["blockCount"],
        )
        block.timestamp=serialized_block["timestamp"]
        block.signature = serialized_block["signature"]
        return block

    
    def toJson(self):
        jsonBlock = {}
        jsonBlock['lastHash'] = self.lastHash
        jsonBlock['forger'] = self.forger
        jsonBlock['blockCount'] = self.blockCount
        jsonBlock['timestamp'] = self.timestamp
        jsonBlock['signature'] = self.signature
        transactions = []

        for tx in self.transactions:
            if tx.type == TransactionType.CHALLENGE:
                challengeTx: ChallengeTX = tx
                transactions.append(challengeTx.toJson())
            else:
                transactions.append(tx.toJson())

        jsonBlock['transactions'] = transactions

        return jsonBlock

    # @staticmethod
    # def fromPickle(pickle) -> Block:
    #     block = jsonpickle.decode(pickle["object"])
    #     beezKeeper = BeezKeeper()
    #     header = Header()
        
    #     return jsonpickle.decode(pickle)

    # @staticmethod
    # def toPickle(block):
    #     return {"object": jsonpickle.encode(block), "header": block.header.deserialized()}
    
    def payload(self):
        jsonRepresentation = copy.deepcopy(self.toJson())
        jsonRepresentation['signature'] = ''

        return jsonRepresentation

    def sign(self, signature):
        self.signature = signature
