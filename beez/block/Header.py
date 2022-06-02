from __future__ import annotations
from typing import TYPE_CHECKING, Dict, Optional
from loguru import logger

if TYPE_CHECKING:
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


    def getBeezKeeper(self) -> BeezKeeper:
        logger.info(f"get BeezKeeper")
        return self.beezKeeper

    def getAccountStateModel(self) -> AccountStateModel:
        logger.info(f"get AccountStateModel")
        return self.accountStateModel