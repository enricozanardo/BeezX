from ast import Index
from asyncio.log import logger
from tokenize import Number
from typing import Dict, List, Sequence
import os
from whoosh.index import create_in
from whoosh.fields import *
from whoosh.qparser import MultifieldParser, SimpleParser
from whoosh.filedb.filestore import RamStorage, FileStorage
from whoosh.analysis import StemmingAnalyzer
from whoosh import index

import json


class Engine:

    def __init__(self):
        self.ix = None 

    def index_documents(self, docs: Sequence):
        writer = self.ix.writer()
        for doc in docs:
            d = {k: v for k,v in doc.items() if k in self.schema.stored_names()}
            d['raw'] = json.dumps(doc) # raw version of all of doc
            writer.add_document(**d)
        writer.commit(optimize=True)

    def get_index_size(self) -> int:
        return self.ix.doc_count_all()


    def delete_document(self, field: str, term: str):
        writer = self.ix.writer()
        writer.delete_by_term(field, term)
        writer.commit()
    
    def query(self, q: str, fields: Sequence, highlight: bool=True) -> List[Dict]:
        search_results = []
        with self.ix.searcher() as searcher:
            results = searcher.search(MultifieldParser(fields, schema=self.schema).parse(q))
            for r in results:
                d = json.loads(r['raw'])
                if highlight:
                    for f in fields:
                        if r[f] and isinstance(r[f], str):
                            d[f] = r.highlights(f) or r[f]

                search_results.append(d)

        return search_results

    def query_at(self, q: str, fields: Sequence, highlight: bool=True, index: int=0) -> List[Dict]:
        return self.query(q, fields, highlight)[index]


class TxIndexEngine(Engine):

    engine = None

    def __init__(self, schema):
        super().__init__()
        self.schema = schema
        schema.add('raw', TEXT(stored=True))
        if not os.path.isdir("indices"):
            os.makedirs("indices", exist_ok=True)
            self.ix = FileStorage("indices").create_index(self.schema, indexname="transactions_index")
        else:
            self.ix = FileStorage("indices").open_index("transactions_index")
        TxIndexEngine.engine = self

    # Singleton
    @staticmethod
    def get_engine(schema):
        if not TxIndexEngine.engine:
            en = TxIndexEngine(schema)
            TxIndexEngine.engine = en
        return TxIndexEngine.engine




class BlockIndexEngine(Engine):

    engine = None

    def __init__(self, schema):
        super().__init__()
        self.schema = schema
        schema.add('raw', TEXT(stored=True))
        if not os.path.isdir("blocks_indices"):
            os.makedirs("blocks_indices", exist_ok=True)
            self.ix = FileStorage("blocks_indices").create_index(self.schema, indexname="blocks_index")
        else:
            self.ix = FileStorage("blocks_indices").open_index("blocks_index")
        BlockIndexEngine.engine = self

    # Singleton
    @staticmethod
    def get_engine(schema):
        if not BlockIndexEngine.engine:
            en = BlockIndexEngine(schema)
            BlockIndexEngine.engine = en
        return BlockIndexEngine.engine

class TxpIndexEngine(Engine):

    engine = None

    def __init__(self, schema):
        super().__init__()
        self.schema = schema
        schema.add('raw', TEXT(stored=True))
        if not os.path.isdir("txp_indices"):
            os.makedirs("txp_indices", exist_ok=True)
            self.ix = FileStorage("txp_indices").create_index(self.schema, indexname="txp_index")
        else:
            self.ix = FileStorage("txp_indices").open_index("txp_index")
        TxpIndexEngine.engine = self

    # Singleton
    @staticmethod
    def get_engine(schema):
        if not TxpIndexEngine.engine:
            en = TxpIndexEngine(schema)
            TxpIndexEngine.engine = en
        return TxpIndexEngine.engine


class AccountModelEngine(Engine):

    engine = None

    def __init__(self, schema):
        super().__init__()
        self.schema = schema
        schema.add('raw', TEXT(stored=True))
        if not os.path.isdir("account_indices"):
            os.makedirs("account_indices", exist_ok=True)
            self.ix = FileStorage("account_indices").create_index(self.schema, indexname="account_index")
        else:
            self.ix = FileStorage("account_indices").open_index("account_index")
        AccountModelEngine.engine = self

    # Singleton
    @staticmethod
    def get_engine(schema):
        if not AccountModelEngine.engine:
            en = AccountModelEngine(schema)
            AccountModelEngine.engine = en
        return AccountModelEngine.engine

class BalancesModelEngine(Engine):

    engine = None

    def __init__(self, schema):
        super().__init__()
        self.schema = schema
        schema.add('raw', TEXT(stored=True))
        if not os.path.isdir("balance_indices"):
            os.makedirs("balance_indices", exist_ok=True)
            self.ix = FileStorage("balance_indices").create_index(self.schema, indexname="balance_index")
        else:
            self.ix = FileStorage("balance_indices").open_index("balance_index")
        BalancesModelEngine.engine = self

    # Singleton
    @staticmethod
    def get_engine(schema):
        if not BalancesModelEngine.engine:
            en = BalancesModelEngine(schema)
            BalancesModelEngine.engine = en
        return BalancesModelEngine.engine

class PosModelEngine(Engine):

    engine = None

    def __init__(self, schema):
        super().__init__()
        self.schema = schema
        schema.add('raw', TEXT(stored=True))
        if not os.path.isdir("pos_indices"):
            os.makedirs("pos_indices", exist_ok=True)
            self.ix = FileStorage("pos_indices").create_index(self.schema, indexname="pos_index")
        else:
            self.ix = FileStorage("pos_indices").open_index("pos_index")
        PosModelEngine.engine = self

    # Singleton
    @staticmethod
    def get_engine(schema):
        if not PosModelEngine.engine:
            en = PosModelEngine(schema)
            PosModelEngine.engine = en
        return PosModelEngine.engine

    
class ChallengeModelEngine(Engine):

    engine = None

    def __init__(self, schema):
        super().__init__()
        self.schema = schema
        schema.add('raw', TEXT(stored=True))
        if not os.path.isdir("challenge_indices"):
            os.makedirs("challenge_indices", exist_ok=True)
            self.ix = FileStorage("challenge_indices").create_index(self.schema, indexname="challenge_index")
        else:
            self.ix = FileStorage("challenge_indices").open_index("challenge_index")
        ChallengeModelEngine.engine = self

    # Singleton
    @staticmethod
    def get_engine(schema):
        if not ChallengeModelEngine.engine:
            en = ChallengeModelEngine(schema)
            ChallengeModelEngine.engine = en
        return ChallengeModelEngine.engine





