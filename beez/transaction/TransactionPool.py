from __future__ import annotations
from typing import TYPE_CHECKING, List

from loguru import logger

if TYPE_CHECKING:
    from beez.transaction.Transaction import Transaction
    from beez.transaction.ChallengeTX import ChallengeTX

class TransactionPool():
    """
    collect all the transactions that are not currently stored into a block
    """

    def __init__(self):
        self.transactions: List[Transaction] = []

    def addTransaction(self, transaction: Transaction):
        # logger.info(f"transaction to add: {transaction.id}")
        self.transactions.append(transaction)


    def challengeExists(self, challengeTx: ChallengeTX):
        for tx in self.transactions:
            if tx.id == challengeTx.id:
                return True
        return False

    def transactionExists(self, transaction: Transaction):
        for tx in self.transactions:
            if tx.equals(transaction):
                return True
        return False

    def removeFromPool(self, transactions: List[Transaction]):
        # Remove closed challenge tx....
        logger.warning("# Remove closed challenge tx....")

        newPoolTransactions: List[Transaction] = []
        for pooltransaction in self.transactions:
            insert = True
            for transaction in transactions:
                if pooltransaction.equals(transaction):
                    insert = False
            if insert == True:
                newPoolTransactions.append(pooltransaction)
            
        self.transactions = newPoolTransactions

    def forgerRequired(self) -> bool:
        """
        check when is time to forge a new Block of transactions
        """
        numberOfTransactionsForEachBlock = 1 # 1 = Mine a Block every time that a transaction is present into the transaction pool.
        if len(self.transactions) >= numberOfTransactionsForEachBlock:
            return True
        else:
            return False