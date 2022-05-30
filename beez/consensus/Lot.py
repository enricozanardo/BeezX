from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from beez.Types import PublicKeyString, Stake

from beez.BeezUtils import BeezUtils

class Lot():
    """
    Randomly select a Peer that will become the Forger of a pool of Transactions

    publicKeyString: The publicKeyString of the node that wants to become a forger
    iteration: correspond on the numner of tokens that are staked by the node
    lastBlockHash: needed to be sure for witch block the forger can add the next Block
    """
    def __init__(self, publicKeyString: PublicKeyString, iteration: Stake, lastBlockHash: str):
        self.publicKeyString = publicKeyString
        self.iteration = iteration
        self.lastBlockHash = lastBlockHash

    
    def lotteryHash(self):
        hashData = self.publicKeyString + self.lastBlockHash
        for _ in range(self.iteration):
            hashData = BeezUtils.hash(hashData).hexdigest()
        
        return hashData
