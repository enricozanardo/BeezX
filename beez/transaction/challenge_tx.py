"""Beez blockchain - challenge transaction."""

from __future__ import annotations
from typing import TYPE_CHECKING

from beez.transaction.Transaction import Transaction
from beez.challenge.Challenge import Challenge

if TYPE_CHECKING:
    from .transaction_type import TransactionType
    from beez.Types import PublicKeyString


class ChallengeTX(Transaction):
    """Challenge transaction"""

    def __init__(   # pylint: disable=too-many-arguments
        self,
        sender_public_key: PublicKeyString,
        receiver_public_key: PublicKeyString,
        amount: int,
        transaction_type: TransactionType,
        challenge: Challenge,
    ):
        super().__init__(sender_public_key, receiver_public_key, amount, transaction_type)
        self.challenge = challenge

    def to_json(self):
        """Converts the challenge transaction to json."""
        json_block = super().to_json()
        json_block["challenge"] = {
            "state": self.challenge.state,
            "id": self.challenge.identifier,
            "reward": self.challenge.reward,
            "workers": ["w1", "w2"],
            "enrolment": "Mon 30.06.2022@23:59",
        }

        return json_block
