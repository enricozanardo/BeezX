"""Beez blockchain - account state model."""

from __future__ import annotations
from typing import TYPE_CHECKING, Any
import threading
from loguru import logger

if TYPE_CHECKING:
    from beez.types import PublicKeyString


class AccountStateModel:
    """
    The account state model keeps the states of the balances of the wallets in the Blockchain.
    Every time that a block is added to the Blockchain, the ASM will update the wallet balances
    based on the transactions accured.
    """

    def __init__(self):
        self.accounts_index = []
        self.balance_index = {}

    def start(self):
        """Start status thread."""
        status_thread = threading.Thread(target=self.status, args={})
        status_thread.start()

    def serialize(self) -> dict[str,Any]:
        """Serializes account state model to json."""
        logger.info(f"accounts: {self.accounts()}")
        return {"accounts": self.accounts(), "balances": self.balances()}

    @staticmethod
    def deserialize(serialized_balances, index=True):
        """Creates new account state model object from serialized form."""
        return AccountStateModel()._deserialize(    # pylint: disable=protected-access
            serialized_balances, index
        )

    def _deserialize(self, serialized_balances, index=True):  # pylint: disable=unused-argument
        """Private deserialize helper."""
        self.accounts_index = []
        self.balance_index = {}
        for acc_id, bal in serialized_balances.items():
            self.update_balance(acc_id, bal)
        return self

    def balances(self) -> dict[str, int]:
        """Returns a dict containing a mapping from account to balance."""
        return self.balance_index

    def accounts(self) -> list[str]:
        """Returns a list of all account ids."""
        return self.accounts_index

    def status(self):
        """Logs the current status of the account state model."""
        logger.info("Not yet implemented")

    def add_account(self, public_key_string: PublicKeyString):
        """Adds a new account to the account state model and initializes the balance to 0."""
        logger.info("Adding account: %s", public_key_string)
        if public_key_string not in self.accounts_index:
            self.accounts_index.append(public_key_string)
            self.balance_index[public_key_string] = 0

    def get_balance(self, public_key_string: PublicKeyString):
        """Returns the balance of the given account."""
        if public_key_string not in self.accounts_index:
            self.add_account(public_key_string)
        return self.balance_index[public_key_string]

    def update_balance(self, public_key_string: PublicKeyString, amount: int):
        """Updates the balance of account by amount."""
        logger.info("Update balance: %s, amount: %s", public_key_string, str(amount))
        if public_key_string not in self.accounts_index:
            self.add_account(public_key_string)

        old_balance = self.get_balance(public_key_string)
        self.balance_index[public_key_string] = old_balance + amount
