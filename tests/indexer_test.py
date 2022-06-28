
from typing import List
from loguru import logger
from beez.BeezUtils import BeezUtils
from datetime import datetime

from beez.index.BeezIndexer import BeezIndexer
from beez.transaction.Transaction import Transaction
from beez.wallet.Wallet import Wallet
from beez.transaction.TransactionType import TransactionType
from beez.transaction.IndexedTransaction import IndexedTransaction



def test_indexer():
    logger.info(f"start testing indexer")
    beezIndexer = BeezIndexer()

    wallet = Wallet()

    transactions: List[Transaction] = []

    # for i in range(5):
    #     transaction = wallet.createTransaction(f"pino{i}", 100 - i, TransactionType.TRANSFER.name)
    #     transactions.append(transaction)

    # lastHash = "123456cde"
    # block = wallet.createBlock(transactions, lastHash, 1)

    # beezIndexer.indexBlock(block)
    # transactions: List[Transaction] = []

    # for i in range(5):
    #     transaction = wallet.createTransaction(f"gino{i}", 500 + i, TransactionType.EXCHANGE.name)
    #     transactions.append(transaction)
    
    # lastHash = "78901abc"
    # block = wallet.createBlock(transactions, lastHash, 2)

    # beezIndexer.indexBlock(block)
    # transactions: List[Transaction] = []


    logger.info(f"indexed {beezIndexer.getIndexSize()} transactions")

    fields_to_search = ["id", "amount", "type", "lastHash", "timestamp", "blockCount", "receiverPublicKey"]

    for q in ["4e9159d4f70c11ecb214e6dd7b0e5c18", "99", "1501", "502", "pino3", "1", "78901abc", "825757e8f71911ec82d2e6dd7b0e5c18"]:
        logger.info(f"Query: {q}")

        results: List[IndexedTransaction] = beezIndexer.query(q, fields_to_search, highlight=True)

        for result in results:
            logger.info(f"\t Block:{result.blockCount} - lashHash:{result.lastHash} TX_id: {result.id} - Amount: {result.amount}, Tx_type: {result.type}, Receiver: {result.receiverPublicKey}")

        logger.info("-"*70)

   

    assert isinstance(beezIndexer, BeezIndexer)