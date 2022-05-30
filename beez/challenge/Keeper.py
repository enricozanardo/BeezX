from __future__ import annotations
from optparse import Option
from typing import TYPE_CHECKING, Dict, List
from loguru import logger
import pathlib

if TYPE_CHECKING:
    from beez.Types import Prize, ChallengeID, PublicKeyString
    from beez.transaction.ChallengeTX import ChallengeTX

from beez.BeezUtils import BeezUtils

class Keeper():
    """
    keeps track of each Challenge.
    Every time that a block is added to the Blockchain, the Keeper will update the challenge based
    on the transactions accured.
    """
    def __init__(self):
        self.challenges : Dict[ChallengeID : ChallengeTX] = {}
        
    def set(self, challengeTX: ChallengeTX):
        challengeID = challengeTX.id
        prize = challengeTX.amount

        if challengeID in self.challenges.keys():
            # Challenge already created!
            logger.warning(f"Challenge already created")
        else:
            logger.info(f"Challenge id: {challengeID} of {prize} tokens kept.")
            self.challenges[challengeID] = challengeTX
    
    def get(self, challengeID: ChallengeID) -> Option[ChallengeTX]:
        if challengeID in self.challenges.keys():
            return self.challenges[ChallengeTX]
        else:
            return None

    def challegeExists(self, challengeID: ChallengeID) -> bool:
        if challengeID in self.challenges.keys():
            return True
        else:
            return False

    def update(self, challengeID: ChallengeID) -> bool:
        if challengeID in self.challenges.keys():
            # Update the challenge!!!
            return True
        else:
            return False

    # TODO: Generate the rewarding function!!!