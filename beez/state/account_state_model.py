"""Beez blockchain - account state model."""

from __future__ import annotations
from typing import TYPE_CHECKING, Any
import threading
import time
from loguru import logger
from whoosh.fields import Schema, TEXT, NUMERIC, ID, KEYWORD
from beez.beez_utils import BeezUtils

from beez.index.index_engine import AccountModelEngine, BalancesModelEngine

if TYPE_CHECKING:
    from beez.Types import PublicKeyString


class AccountStateModel:
    """
    The account state model keeps the states of the balances of the wallets in the Blockchain.
    Every time that a block is added to the Blockchain, the ASM will update the wallet balances
    based on the transactions accured.
    """

    def __init__(self):
        self.accounts_index_engine = AccountModelEngine.get_engine(
            Schema(id=ID(stored=True), type=KEYWORD(stored=True))
        )
        self.balance_index_engine = BalancesModelEngine.get_engine(
            Schema(
                id=ID(stored=True),
                type=KEYWORD(stored=True),
                account_id=TEXT(stored=True),
                balance=NUMERIC(stored=True),
            )
        )

    def start(self):
        """Start status thread."""
        status_thread = threading.Thread(target=self.status, args={})
        status_thread.start()

    def serialize(self) -> dict[str:Any]:
        """Serializes account state model to json."""
        return {"accounts": self.accounts(), "balances": self.balances()}

    @staticmethod
    def deserialize(serialized_balances, index=True):
        """Creates new account state model object from serialized form."""
        return AccountStateModel()._deserialize(    # pylint: disable=protected-access
            serialized_balances, index
        )

    def _deserialize(self, serialized_balances, index=True):
        """Private deserialize helper."""
        if index:
            # Remove all balances and accounts and load from serialized ones
            self.accounts_index_engine.delete_document("type", "ACCOUNT")
            self.balance_index_engine.delete_document("type", "BALANCE")
            for acc_id, bal in serialized_balances.items():
                self.update_balance(acc_id, bal)
        return self

    def balances(self) -> dict[str, int]:
        """Returns a dict containing a mapping from account to balance."""
        balances: dict[str, int] = {}
        for balance_doc in self.balance_index_engine.query(
            query="BALANCE", fields=["type"], highlight=True
        ):
            balances[balance_doc["account_id"]] = balance_doc["balance"]
        return balances

    def accounts(self) -> list[str]:
        """Returns a list of all account ids."""
        accounts: list[str] = []
        for account_doc in self.accounts_index_engine.query(
            query="ACCOUNT", fields=["type"], highlight=True
        ):
            accounts.append(account_doc["id"])
        return accounts

    def status(self):
        """Logs the current status of the account state model."""
        while True:
            logger.info(
                f"""Account State Model Status
                {len(self.balance_index_engine.query(query="BALANCE", fields=["type"], highlight=True))}"""     # pylint: disable=line-too-long
            )

            for doc in self.balance_index_engine.query(
                query="BALANCE", fields=["type"], highlight=True
            ):
                wallet_public_key: PublicKeyString = doc["account_id"]
                balance: int = doc["balance"]

                logger.info(f"Wallet: {wallet_public_key} balance: {str(balance)}")

            time.sleep(5)

    def add_account(self, public_key_string: PublicKeyString):
        """Adds a new account to the account state model and initializes the balance to 0."""
        identifier = BeezUtils.hash(
            public_key_string.replace("'", "").replace("\n", "")
        ).hexdigest()
        if (
            len(
                self.accounts_index_engine.query(
                    query=identifier, fields=["id"], highlight=True
                )
            )
            == 0
        ):
            self.accounts_index_engine.index_documents(
                [{"id": identifier, "type": "ACCOUNT"}]
            )
            self.balance_index_engine.index_documents(
                [
                    {
                        "id": identifier,
                        "type": "BALANCE",
                        "account_id": public_key_string,
                        "balance": 0,
                    }
                ]
            )

    def get_balance(self, public_key_string: PublicKeyString):
        """Returns the balance of the given account."""
        identifier = BeezUtils.hash(
            public_key_string.replace("'", "").replace("\n", "")
        ).hexdigest()
        if (
            len(
                self.accounts_index_engine.query(
                    query=identifier, fields=["id"], highlight=True
                )
            )
            == 0
        ):
            self.add_account(public_key_string)
        return self.balance_index_engine.query(
            query=identifier, fields=["id"], highlight=True
        )[0]["balance"]

    def update_balance(self, public_key_string: PublicKeyString, amount: int):
        """Updates the balance of account by amount."""
        identifier = BeezUtils.hash(
            public_key_string.replace("'", "").replace("\n", "")
        ).hexdigest()
        if (
            len(
                self.accounts_index_engine.query(
                    query=identifier, fields=["id"], highlight=True
                )
            )
            == 0
        ):
            self.add_account(public_key_string)

        old_balance = self.get_balance(public_key_string)
        self.balance_index_engine.delete_document("id", identifier)
        self.balance_index_engine.index_documents(
            [
                {
                    "id": identifier,
                    "type": "BALANCE",
                    "account_id": public_key_string,
                    "balance": old_balance + amount,
                }
            ]
        )
