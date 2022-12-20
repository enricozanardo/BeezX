"""Beez blockchain - transaction pool."""

from __future__ import annotations
from typing import List
from beez.transaction.transaction import Transaction
from beez.transaction.challenge_tx import ChallengeTX

class TransactionPool:
    """
    collect all the transactions that are not currently stored into a block
    """

    def __init__(self):
        self.transactions_in_pool = []

    def transactions(self):
        """Returns the transactions in the transaction pool."""
        return self.transactions_in_pool

    def add_transaction(self, transaction: Transaction):
        """Adds a new transaction to the transaction pool."""
        self.transactions_in_pool.append(transaction)

    def challenge_exists(self, challenge_tx: ChallengeTX):
        """Checks if a challenge exists."""
        for transaction in self.transactions():
            if transaction.identifier == challenge_tx.identifier:
                return True
        return False

    def transaction_exists(self, transaction: Transaction):
        """Checks if a transaction exists."""
        for pool_transaction in self.transactions():
            if transaction.equals(pool_transaction):
                return True
        return False

    def remove_from_pool(self, transactions: List[Transaction]):
        """Removes the given list of transactions from the pool."""
        new_pool_transactions: List[Transaction] = []
        for pooltransaction in self.transactions():
            insert = True
            for transaction in transactions:
                if pooltransaction.equals(transaction):
                    insert = False
            if insert is True:
                new_pool_transactions.append(pooltransaction)
        self.transactions_in_pool = new_pool_transactions

    def forger_required(self) -> bool:
        """
        check when is time to forge a new Block of transactions
        """
        # 1 = Mine a Block every time that a transaction is present into the transaction pool.
        number_of_transactions_for_each_block = 1
        if len(self.transactions()) >= number_of_transactions_for_each_block:
            return True
        return False
