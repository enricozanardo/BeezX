from __future__ import annotations
from typing import TYPE_CHECKING, Dict, Optional
from loguru import logger

if TYPE_CHECKING:
    from beez.Types import Prize, ChallengeID, PublicKeyString
    from beez.transaction.ChallengeTX import ChallengeTX
    from beez.challenge.Challenge import Challenge

from beez.BeezUtils import BeezUtils

class Keeper():
    """
    keeps track of each Challenge.
    Every time that a block is added to the Blockchain, the Keeper will update the challenge based
    on the transactions accured.
    """
    def __init__(self):
        self.challenges : Dict[ChallengeID : Challenge] = {}


    def start(self):
        # TODO: init a thread that periodically check the states of the challenges
        pass
        
    def set(self, challenge: Challenge):
        challengeID : ChallengeID = challenge.id
        prize = challenge.prize

        if challengeID in self.challenges.keys():
            # Challenge already created!
            logger.warning(f"Challenge already created")
        else:
            logger.info(f"Challenge id: {challengeID} of {prize} tokens kept.")
            self.challenges[challengeID] = challenge
    
    def get(self, challengeID: ChallengeID) -> Optional[Challenge]:
        if challengeID in self.challenges.keys():
            return self.challenges[challengeID]
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
            challege = self.get(challengeID)
            if challege:
                logger.info(f"{challege.state}")
            return True
        else:
            logger.info(f"Challenge not found!!!")
            return False

    # TODO: Generate the rewarding function!!!