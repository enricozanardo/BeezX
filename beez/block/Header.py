"""Beez blockchain - block header."""

from __future__ import annotations

from beez.challenge.beez_keeper import BeezKeeper
from beez.state.AccountStateModel import AccountStateModel


class Header:
    """
    The Header of the block contains the updated data of the in memory objects:

    AccountStateModel : Wallet balances
    BeezKeeper: Challenges

    that must be shared between peers
    """

    def __init__(self, beez_keeper: BeezKeeper, account_state_model: AccountStateModel) -> None:
        self.beez_keeper = beez_keeper
        self.account_state_model = account_state_model

    def serialize(self):
        """Returns the header in serialized form."""
        return {
            "beezKeeper": self.beez_keeper.serialize() if self.beez_keeper else {},
            "accountStateModel": self.account_state_model.serialize()
            if self.account_state_model
            else {},
        }

    @staticmethod
    def deserialize(serialized_beez_keeper, serialized_account_state_model, index=True) -> Header:
        """Returns a header object based on serialized header."""
        return Header(
            BeezKeeper.deserialize(serialized_beez_keeper, index),
            AccountStateModel.deserialize(serialized_account_state_model["balances"], index),
        )

    def _deserialize(self, serialized_beez_keeper, serialized_account_state_model):
        """Deserializes the header."""
        self.beez_keeper.deserialize(serialized_beez_keeper)  # need Real Challenge objects here
        self.account_state_model.deserialize(serialized_account_state_model)

    def get_beez_keeper(self) -> BeezKeeper:
        """Returns the beez keeper."""
        return self.beez_keeper

    def get_account_state_model(self) -> AccountStateModel:
        """Returns the account state model."""
        return self.account_state_model
