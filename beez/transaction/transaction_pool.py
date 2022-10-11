"""Beez blockchain - transaction pool."""

from __future__ import annotations
import json
from typing import TYPE_CHECKING, List
from whoosh.fields import Schema, TEXT, ID, KEYWORD
from beez.index.index_engine import TxpIndexEngine
from beez.transaction.transaction import Transaction


if TYPE_CHECKING:
    from beez.transaction.challenge_tx import ChallengeTX


class TransactionPool:
    """
    collect all the transactions that are not currently stored into a block
    """

    def __init__(self):
        self.tx_schema = Schema(
            id=ID(stored=True), type=KEYWORD(stored=True), txp_encoded=TEXT(stored=True)
        )
        self.transactions_index = TxpIndexEngine.get_engine(self.tx_schema)

    def transactions(self):
        """Returns the transactions in the transaction pool."""
        transactions = self.transactions_index.query("TXP", ["type"])
        txs: List[Transaction] = []
        for transaction in transactions:
            tx_encoded = transaction["txp_encoded"].replace("'", '"')
            txs.append(Transaction.from_json(json.loads(tx_encoded)))
        return txs

    def add_transaction(self, transaction: Transaction):
        """Adds a new transaction to the transaction pool."""
        self.transactions_index.index_documents(
            [
                {
                    "id": str(transaction.identifier),
                    "type": "TXP",
                    "txp_encoded": str(transaction.to_json()),
                }
            ]
        )

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
        self.transactions_index.delete_document("type", "TXP")
        for new_pool_transaction in new_pool_transactions:
            self.add_transaction(new_pool_transaction)

    def forger_required(self) -> bool:
        """
        check when is time to forge a new Block of transactions
        """
        # 1 = Mine a Block every time that a transaction is present into the transaction pool.
        number_of_transactions_for_each_block = 3
        if len(self.transactions()) >= number_of_transactions_for_each_block:
            return True
        return False
