from ast import Index
from typing import Dict, List, Sequence
import os
from whoosh.index import create_in
from whoosh.fields import *
from whoosh.qparser import MultifieldParser
from whoosh.filedb.filestore import RamStorage, FileStorage
from whoosh.analysis import StemmingAnalyzer

import json

class IndexEngine:

    engine = None

    def __init__(self, schema):
        self.schema = schema
        schema.add('raw', TEXT(stored=True))
        if not os.path.isdir("transactions_index"):
            os.makedirs("transactions_index", exist_ok=True)
        self.ix = FileStorage("transactions_index").create_index(self.schema)
        IndexEngine.engine = self

    # Singleton
    @staticmethod
    def get_engine(schema):
        if not IndexEngine.engine:
            en = IndexEngine(schema)
            IndexEngine.engine = en
        return IndexEngine.engine

    def index_documents(self, docs: Sequence):
        writer = self.ix.writer()
        for doc in docs:
            d = {k: v for k,v in doc.items() if k in self.schema.stored_names()}
            d['raw'] = json.dumps(doc) # raw version of all of doc
            writer.add_document(**d)
        writer.commit(optimize=True)

    def get_index_size(self) -> int:
        return self.ix.doc_count_all()

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