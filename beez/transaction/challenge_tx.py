"""Beez blockchain - challenge transaction."""

from __future__ import annotations
from typing import TYPE_CHECKING
import json
import jsonpickle

from beez.transaction.transaction import Transaction
from beez.challenge.challenge import Challenge

if TYPE_CHECKING:
    from .transaction_type import TransactionType
    from beez.types import PublicKeyString


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
        # json_block["challenge"] = {
        #     "state": self.challenge.state,
        #     "id": self.challenge.identifier,
        #     "reward": self.challenge.reward,
        #     "workers": ["w1", "w2"],
        #     "enrollment": "Mon 30.06.2022@23:59",
        # }
        json_challenge = jsonpickle.encode(self.challenge, unpicklable=True)
        json_block["challenge"] = json.loads(json_challenge)
        return json_block

    @staticmethod
    def from_json(json_block):
        """Creates a new challenge tx from json serialization."""
        challenge = jsonpickle.decode(json.dumps(json_block["challenge"]))
        challenge_tx = ChallengeTX(
            sender_public_key=json_block["senderPublicKey"],
            receiver_public_key=json_block["receiverPublicKey"],
            amount=json_block["amount"],
            transaction_type=json_block["type"],
            challenge=challenge
        )
        challenge_tx.identifier = json_block["id"]
        challenge_tx.timestamp = json_block["timestamp"]
        challenge_tx.signature = json_block["signature"]
        return challenge_tx
    