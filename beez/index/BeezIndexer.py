from __future__ import annotations
from typing import TYPE_CHECKING, Dict, List, Sequence
import pathlib
from loguru import logger

from whoosh.index import create_in
from whoosh.fields import *
from whoosh.qparser import MultifieldParser
from whoosh.filedb.filestore import RamStorage
from whoosh.index import create_in
from whoosh.analysis import StemmingAnalyzer
from whoosh import index

import json
from datetime import datetime

if TYPE_CHECKING:
    from beez.block.Block import Block
    from beez.transaction.Transaction import Transaction
    

from beez.BeezUtils import BeezUtils
from beez.transaction.IndexedTransaction import IndexedTransaction

class BeezIndexer:

    def __init__(self) -> None:
        self.setSchemas()
        self.txSchema.add('raw', TEXT(stored=True))

        currentPath = pathlib.Path().resolve()
        indexerPath = f"{currentPath}/beez/indexdir/"
        
        try:
            self.index = index.open_dir(indexerPath, "BeexIndex", False, self.txSchema)
        except index.EmptyIndexError:
            self.index = create_in(indexerPath, self.txSchema, "BeexIndex")

    def setSchemas(self):

        # For Transactions
        self.txSchema: Schema = Schema(
            id = ID(stored=True),
            amount = NUMERIC(stored=True),
            receiverPublicKey = TEXT(stored=True),
            senderPublicKey = TEXT(stored=True),
            signature = TEXT(stored=True),
            type = TEXT(stored=True),
            timestamp = TEXT(stored=True),
            blockCount = NUMERIC(stored=True),
            forger = TEXT(stored=True),
            lastHash = TEXT(stored=True)
        )
 
    def indexBlock(self, block: Block):
        writer = self.index.writer()

        transactions: List[Transaction] = block.transactions


        for tx in transactions:
            indexedTransaction : IndexedTransaction = IndexedTransaction(tx.senderPublicKey, tx.receiverPublicKey, tx.amount, tx.type, block.blockCount, block.forger, block.lastHash, tx.id, tx.signature) 
            encodedTransaction = BeezUtils.encode(indexedTransaction)
            doc = {}
            # Block data
            doc['blockCount'] = block.blockCount
            doc['forger'] = block.forger
            doc['lastHash'] = block.lastHash
            # Transaction data
            doc['id'] = tx.id
            doc['amount'] = tx.amount
            doc['receiverPublicKey'] = tx.receiverPublicKey 
            doc['senderPublicKey'] = tx.senderPublicKey
            doc['signature'] = tx.signature
            doc['type'] = tx.type
            doc['timestamp'] = str(tx.timestamp)
            doc['raw'] = encodedTransaction
            
            writer.add_document(**doc)
        
        writer.commit(optimize=True)


    def getIndexSize(self) -> int:
        return self.index.doc_count_all()

    
    def query(self, query: str, fields: Sequence, highlight: bool = True) -> List[IndexedTransaction]:
        searchResults = []

        with self.index.searcher() as searcher:
            results = searcher.search(MultifieldParser(fields, schema=self.txSchema).parse(query))

            for result in results:
                indexedTransaction : IndexedTransaction = BeezUtils.decode(result['raw'])

                if highlight:
                    searchResults.append(indexedTransaction)

        return searchResults