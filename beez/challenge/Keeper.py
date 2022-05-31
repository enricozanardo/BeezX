from __future__ import annotations
from typing import TYPE_CHECKING, Dict, Optional
from loguru import logger

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


    def start(self):
        # TODO: init a thread that periodically check the states of the challenges
        pass
        
    def set(self, challengeTX: ChallengeTX):
        challengeID = challengeTX.id
        prize = challengeTX.amount

        if challengeID in self.challenges.keys():
            # Challenge already created!
            logger.warning(f"Challenge already created")
        else:
            logger.info(f"Challenge id: {challengeID} of {prize} tokens kept.")
            self.challenges[challengeID] = challengeTX
    
    def get(self, challengeID: ChallengeID) -> Optional[ChallengeTX]:
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
            logger.info(f"Update the challenge!!!")
            challegeTX = self.get(challengeID)
            if challegeTX:
                logger.info(f"{challegeTX.state}")
            return True
        else:
            return False

    # TODO: Generate the rewarding function!!!