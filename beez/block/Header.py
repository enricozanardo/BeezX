from __future__ import annotations
from typing import TYPE_CHECKING, Dict, Optional
from loguru import logger

from beez.challenge.BeezKeeper import BeezKeeper
from beez.state.AccountStateModel import AccountStateModel

class Header():
    """
    The Header of the block contains the updated data of the in memory objects:

    AccountStateModel : Wallet balances
    BeezKeeper: Challenges

    that must be shared between peers
    """
    def __init__(self, beezKeeper: BeezKeeper, accountStateModel: AccountStateModel) -> None:
        self.beezKeeper = beezKeeper
        self.accountStateModel = accountStateModel

    def serialize(self):
        return {"beezKeeper": self.beezKeeper.serialize() if self.beezKeeper else {}, "accountStateModel": self.accountStateModel.serialize() if self.accountStateModel else {}}

    @staticmethod
    def deserialize(serialized_beezKeeper, serialized_accountStateModel, index=True) -> Header:
        return Header(BeezKeeper.deserialize(serialized_beezKeeper, index), AccountStateModel.deserialize(serialized_accountStateModel["balances"], index))

    def _deserialize(self, serialized_beezKeeper, serialized_accountStateModel):
        self.beezKeeper.deserialize(serialized_beezKeeper) # need Real Challenge objects here
        self.accountStateModel.deserialize(serialized_accountStateModel) 

    def getBeezKeeper(self) -> BeezKeeper:
        return self.beezKeeper

    def getAccountStateModel(self) -> AccountStateModel:
        return self.accountStateModel