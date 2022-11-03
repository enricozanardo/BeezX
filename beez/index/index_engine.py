"Beez blockchain - index engines."

import os
import json
from loguru import logger
from typing import Sequence, Optional
from whoosh import index  # type: ignore
from whoosh.fields import TEXT  # type: ignore
from whoosh.qparser import MultifieldParser     # type: ignore
from whoosh.filedb.filestore import FileStorage     # type: ignore



class Engine:
    """Engine base class."""

    def __init__(self):
        self.index = None
        self.schema = None

    def index_documents(self, docs: Sequence) -> None:
        """Adds docs to index."""
        writer = self.index.writer()
        for doc in docs:
            data = {key: value for key, value in doc.items() if key in self.schema.stored_names()}
            data["raw"] = json.dumps(doc)  # raw version of all of doc
            writer.add_document(**data)
        writer.commit(optimize=True)

    def get_index_size(self) -> int:
        """Returns number of docs in index."""
        return self.index.doc_count_all()

    def delete_document(self, field: str, term: str) -> None:
        """Deletes a document from index."""
        writer = self.index.writer()
        writer.delete_by_term(field, term)
        writer.commit()

    def query(self, query: str, fields: Sequence, highlight: bool = True) -> list[dict]:
        """Query index and returns docs matching query."""
        search_results = []
        with self.index.searcher() as searcher:
            results = searcher.search(MultifieldParser(fields, schema=self.schema).parse(query))
            for result in results:
                raw_data = json.loads(result["raw"])
                if highlight:
                    for field in fields:
                        if result[field] and isinstance(result[field], str):
                            raw_data[field] = result.highlights(field) or result[field]

                search_results.append(raw_data)

        return search_results

    def query_at(
        self, query: str, fields: Sequence, highlight: bool = True, index: int = 0
    ) -> dict:
        """Returns the document at index from all docs matching the query."""
        return self.query(query, fields, highlight)[index]


class TxIndexEngine(Engine):
    """Transaction index engine."""

    engine = None

    def __init__(self, schema):
        super().__init__()
        self.schema = schema
        schema.add("raw", TEXT(stored=True))
        if not os.path.isdir("indices"):
            os.makedirs("indices", exist_ok=True)
            self.index = FileStorage("indices").create_index(
                self.schema, indexname="transactions_index"
            )
        else:
            self.index = FileStorage("indices").open_index("transactions_index")
        TxIndexEngine.engine = self

    # Singleton
    @staticmethod
    def get_engine(schema, force_new: bool = False):
        """Returns an engine for the given schema."""
        if not TxIndexEngine.engine or force_new or not index.exists_in("indices"):
            new_engine = TxIndexEngine(schema)
            TxIndexEngine.engine = new_engine
        return TxIndexEngine.engine


class BlockIndexEngine(Engine):
    """Index engine for block index."""
    engine = None

    def __init__(self, schema):
        super().__init__()
        self.schema = schema
        schema.add("raw", TEXT(stored=True))
        if not os.path.isdir("blocks_indices"):
            os.makedirs("blocks_indices", exist_ok=True)
            self.index = FileStorage("blocks_indices").create_index(
                self.schema, indexname="blocks_index"
            )
        else:
            self.index = FileStorage("blocks_indices").open_index("blocks_index")
        BlockIndexEngine.engine = self

    # Singleton
    @staticmethod
    def get_engine(schema, force_new: bool = False):
        """Returns an engine for the given schema."""
        if not BlockIndexEngine.engine or force_new or not index.exists_in("blocks_indices"):
            new_engine = BlockIndexEngine(schema)
            BlockIndexEngine.engine = new_engine
        return BlockIndexEngine.engine


class TxpIndexEngine(Engine):
    """Index engine for transaction pool model."""
    engine = None

    def __init__(self, schema):
        super().__init__()
        self.schema = schema
        schema.add("raw", TEXT(stored=True))
        if not os.path.isdir("txp_indices"):
            os.makedirs("txp_indices", exist_ok=True)
            self.index = FileStorage("txp_indices").create_index(self.schema, indexname="txp_index")
        else:
            self.index = FileStorage("txp_indices").open_index("txp_index")
        TxpIndexEngine.engine = self

    # Singleton
    @staticmethod
    def get_engine(schema, force_new: bool = False):
        """Returns an engine for the given schema."""
        if not TxpIndexEngine.engine or force_new or not index.exists_in("txp_indices"):
            new_engine = TxpIndexEngine(schema)
            TxpIndexEngine.engine = new_engine
        return TxpIndexEngine.engine


class AccountModelEngine(Engine):
    """Index engine for account model."""
    engine = None

    def __init__(self, schema):
        super().__init__()
        self.schema = schema
        schema.add("raw", TEXT(stored=True))
        if not os.path.isdir("account_indices"):
            os.makedirs("account_indices", exist_ok=True)
            self.index = FileStorage("account_indices").create_index(
                self.schema, indexname="account_index"
            )
        else:
            self.index = FileStorage("account_indices").open_index("account_index")
        AccountModelEngine.engine = self

    # Singleton
    @staticmethod
    def get_engine(schema, force_new: bool = False):
        """Returns an engine for the given schema."""
        if not AccountModelEngine.engine or force_new or not index.exists_in("account_indices"):
            new_engine = AccountModelEngine(schema)
            AccountModelEngine.engine = new_engine
        return AccountModelEngine.engine


class BalancesModelEngine(Engine):
    """Index engine for balance model."""
    engine = None

    def __init__(self, schema):
        super().__init__()
        self.schema = schema
        schema.add("raw", TEXT(stored=True))
        if not os.path.isdir("balance_indices"):
            os.makedirs("balance_indices", exist_ok=True)
            self.index = FileStorage("balance_indices").create_index(
                self.schema, indexname="balance_index"
            )
        else:
            self.index = FileStorage("balance_indices").open_index("balance_index")
        BalancesModelEngine.engine = self

    # Singleton
    @staticmethod
    def get_engine(schema, force_new: bool = False):
        """Returns an engine for the given schema."""
        if not BalancesModelEngine.engine or force_new or not index.exists_in("balance_indices"):
            new_engine = BalancesModelEngine(schema)
            BalancesModelEngine.engine = new_engine
        return BalancesModelEngine.engine


class PosModelEngine(Engine):
    """Index engine for PoS model."""
    engine: Optional[Engine] = None

    def __init__(self, schema):
        super().__init__()
        self.schema = schema
        schema.add("raw", TEXT(stored=True))
        logger.info('hier drinnen')
        if not os.path.isdir("pos_indices"):
            os.makedirs("pos_indices", exist_ok=True)
            self.index = FileStorage("pos_indices").create_index(self.schema, indexname="pos_index")
        else:
            self.index = FileStorage("pos_indices").open_index("pos_index")
        PosModelEngine.engine = self

    # Singleton
    @staticmethod
    def get_engine(schema, force_new=False):
        """Returns an engine for the given schema."""
        logger.info('aber hier')
        if not PosModelEngine.engine or force_new or not index.exists_in("pos_indices"):
            new_engine = PosModelEngine(schema)
            PosModelEngine.engine = new_engine
        return PosModelEngine.engine


class ChallengeModelEngine(Engine):
    """Index engine for challenge model."""
    engine = None

    def __init__(self, schema):
        super().__init__()
        self.schema = schema
        schema.add("raw", TEXT(stored=True))
        if not os.path.isdir("challenge_indices"):
            os.makedirs("challenge_indices", exist_ok=True)
            self.index = FileStorage("challenge_indices").create_index(
                self.schema, indexname="challenge_index"
            )
        else:
            self.index = FileStorage("challenge_indices").open_index("challenge_index")
        ChallengeModelEngine.engine = self

    # Singleton
    @staticmethod
    def get_engine(schema, force_new: bool = False):
        """Returns an engine for the given schema."""
        if not ChallengeModelEngine.engine or force_new or not index.exists_in("challenge_indices"):
            new_engine = ChallengeModelEngine(schema)
            ChallengeModelEngine.engine = new_engine
        return ChallengeModelEngine.engine
