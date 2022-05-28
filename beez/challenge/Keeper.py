from __future__ import annotations
from optparse import Option
from typing import TYPE_CHECKING, Dict, List
from loguru import logger
import pathlib

if TYPE_CHECKING:
    from beez.Types import Prize, ChallengeID, PublicKeyString

from beez.BeezUtils import BeezUtils

class Keeper():
    """
    keeps track of the prizes of each Challenge 
    """
    def __init__(self):
        self.prizes : Dict[ChallengeID : Prize] = {}
        
    def set(self, challengeID: ChallengeID, prize: Prize):
        if challengeID in self.prizes.keys():
            # Challenge already created!
            logger.warning(f"Challenge already created")
        else:
            logger.info(f"Challenge id: {challengeID} of {prize} tokens kept.")
            self.prizes[challengeID] = prize
    
    def get(self, challengeID: ChallengeID) -> Option[Prize]:
        if challengeID in self.prizes.keys():
            return self.prizes[challengeID]
        else:
            return None

    # TODO: Generate the rewarding function!!!