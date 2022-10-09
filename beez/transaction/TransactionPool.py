from __future__ import annotations
from typing import TYPE_CHECKING, List
from whoosh.fields import Schema, TEXT, ID, KEYWORD
from beez.index.index_engine import TxpIndexEngine
from beez.transaction.Transaction import Transaction

from loguru import logger
import json

if TYPE_CHECKING:
    from beez.transaction.ChallengeTX import ChallengeTX

class TransactionPool():
    """
    collect all the transactions that are not currently stored into a block
    """

    def __init__(self):
        self.tx_schema = Schema(id=ID(stored=True), type=KEYWORD(stored=True), txp_encoded=TEXT(stored=True))
        self.transactions_index = TxpIndexEngine.get_engine(self.tx_schema)

    def transactions(self):
        transactions = self.transactions_index.query('TXP', ['type'])
        txs:List[Transaction] = []
        for tx in transactions:
            tx_encoded = tx["txp_encoded"].replace("'", "\"")
            txs.append(Transaction.fromJson(json.loads(tx_encoded)))
        return txs

    def addTransaction(self, transaction: Transaction):
        self.transactions_index.index_documents([{"id":str(transaction.id), "type": "TXP", "txp_encoded": str(transaction.toJson())}])


    def challengeExists(self, challengeTx: ChallengeTX):
        for tx in self.transactions():
            if tx.id == challengeTx.id:
                return True
        return False

    def transactionExists(self, transaction: Transaction):
        for tx in self.transactions():
            if tx.equals(transaction):
                return True
        return False

    def removeFromPool(self, transactions: List[Transaction]):
        newPoolTransactions: List[Transaction] = []
        for pooltransaction in self.transactions():
            insert = True
            for transaction in transactions:
                if pooltransaction.equals(transaction):
                    insert = False
            if insert == True:
                newPoolTransactions.append(pooltransaction)
        self.transactions_index.delete_document("type", "TXP")
        for tx in newPoolTransactions:
            self.addTransaction(tx)


    def forgerRequired(self) -> bool:
        """
        check when is time to forge a new Block of transactions
        """
        numberOfTransactionsForEachBlock = 3 # 1 = Mine a Block every time that a transaction is present into the transaction pool.
        if len(self.transactions()) >= numberOfTransactionsForEachBlock:
            return True
        else:
            return False