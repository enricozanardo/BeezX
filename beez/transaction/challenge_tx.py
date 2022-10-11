"""Beez blockchain - challenge transaction."""

from __future__ import annotations
from typing import TYPE_CHECKING

from beez.transaction.transaction import Transaction
from beez.challenge.challenge import Challenge

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
        transaction_type: TransactionType.name,
        challenge: Challenge,
    ):
        super().__init__(sender_public_key, receiver_public_key, amount, transaction_type)
        self.challenge = challenge

    def to_json(self):
        """Converts the challenge transaction to json."""
        # json_block = {}
        # json_block["id"] = self.identifier
        # json_block["senderPublicKey"] = self.sender_public_key
        # json_block["receiverPublicKey"] = self.receiver_public_key
        # json_block["amount"] = self.amount
        # json_block["type"] = self.transaction_type
        # json_block["timestamp"] = self.timestamp
        # json_block["signature"] = self.signature
        json_block = super().to_json()
        json_block["challenge"] = {
            "state": self.challenge.state,
            "id": self.challenge.identifier,
            "reward": self.challenge.reward,
            "workers": ["w1", "w2"],
            "enrolment": "Mon 30.06.2022@23:59",
        }

        return json_block
