from __future__ import annotations
from optparse import Option
from typing import TYPE_CHECKING, Dict, List
from loguru import logger
import pathlib

if TYPE_CHECKING:
    from beez.Types import Stake, PublicKeyString

from beez.consensus.Lot import Lot
from beez.BeezUtils import BeezUtils

class ProofOfStake():
    """
    keeps track of the stakes of each account
    """

    def __init__(self):
        self.stakers : Dict[PublicKeyString : Stake] = {}
        self.setGenesisNodeStake()

    def setGenesisNodeStake(self):
        currentPath = pathlib.Path().resolve()
        logger.info(f"currentPath: {currentPath}")

        genisisPublicKey = open(f"{currentPath}/beez/keys/genesisPublicKey.pem", 'r').read()
        # TODO: check if exist!!!
        # logger.info(f"GenesisublicKey: {genisisPublicKey}")
        # give to the genesis staker 1 stake to allow him to forge the initial Block
        self.stakers[genisisPublicKey] = 1

    def update(self, publicKeyString: PublicKeyString, stake: Stake):
        if publicKeyString in self.stakers.keys():
            self.stakers[publicKeyString] += stake
        else:
            self.stakers[publicKeyString] = stake

    def get(self, publicKeyString: PublicKeyString) -> Option[Stake]:
        if publicKeyString in self.stakers.keys():
            return self.stakers[publicKeyString]
        else:
            return None
    
    def validatorLots(self, seed: str) -> List[Lot]:
        lots : List[Lot] = []
        for validator in self.stakers.keys():
            for stake in range(self.get(validator)):
                lots.append(Lot(validator, stake + 1, seed))
        return lots

    def winnerLot(self, lots: List[Lot], seed: str) -> Lot:
        winnerLot: Lot = None
        leastOffSet = None
        # get the integer representation of a give hash
        referenceHashIntValue = int(BeezUtils.hash(seed).hexdigest(), 16)
        # fin the nearest lot
        for lot in lots:
            lotIntValue = int(lot.lotteryHash(), 16)
            offset = abs(lotIntValue-referenceHashIntValue)
            if leastOffSet is None or offset < leastOffSet:
                leastOffSet = offset
                winnerLot = lot

        return winnerLot 


    def forger(self, lastBlockHash: str):
        lots = self.validatorLots(lastBlockHash)
        winnerLot: Lot = self.winnerLot(lots, lastBlockHash)

        return winnerLot.publicKeyString