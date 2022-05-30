from __future__ import annotations
from typing import TYPE_CHECKING, List
import time
import copy

if TYPE_CHECKING:
    from beez.transaction.Transaction import Transaction
    from beez.transaction.ChallengeTX import ChallengeTX
    from beez.wallet.Wallet import Wallet
    from beez.Types import WalletAddress, PublicKeyString

class Block():
    """
    A Block contain a list of Transaction that are validated from a Forger into the Network.
    """
    def __init__(self, transactions: List[Transaction], lastHash: str, forger: PublicKeyString, blockCount: int):
        self.transactions = transactions
        self.lastHash = lastHash
        self.forger = forger
        self.blockCount = blockCount
        self.timestamp = time.time()
        self.signature = ''


    @staticmethod
    def genesis() -> Block:
        genesisBlock = Block([], 'Hello Beez! 🐝 ', 'Author: Enrico Zanardo 🤙🏽', 0)
        genesisBlock.timestamp = 0 # every node will start with the same genesis Block
        return genesisBlock

    
    def toJson(self):
        jsonBlock = {}
        jsonBlock['lastHash'] = self.lastHash
        jsonBlock['forger'] = self.forger
        jsonBlock['blockCount'] = self.blockCount
        jsonBlock['timestamp'] = self.timestamp
        jsonBlock['signature'] = self.signature
        transactions = []

        for tx in self.transactions:
            transactions.append(tx.toJson())

        jsonBlock['transactions'] = transactions

        return jsonBlock
    
    def payload(self):
        jsonRepresentation = copy.deepcopy(self.toJson())
        jsonRepresentation['signature'] = ''

        return jsonRepresentation

    def sign(self, signature):
        self.signature = signature
