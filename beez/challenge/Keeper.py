from __future__ import annotations
from typing import TYPE_CHECKING, Dict, Optional
from loguru import logger
import copy

if TYPE_CHECKING:
    from beez.Types import Prize, ChallengeID, PublicKeyString
    from beez.transaction.ChallengeTX import ChallengeTX
    from beez.challenge.Challenge import Challenge

from beez.BeezUtils import BeezUtils
from beez.challenge.ChallengeState import ChallengeState

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
        
    def set(self, challenge: Challenge) -> Optional[ChallengeState]:
        challengeID : ChallengeID = challenge.id
        reward = challenge.reward

        if challengeID in self.challenges.keys():
            logger.info(f"Challenge already created, check for updates!!!")
            if challenge.state == ChallengeState.UPDATED.name:
                logger.info(f"Challenge state: {challenge.state}")
                # self.keeper.update(challenge) 
                return ChallengeState.UPDATED.name
            elif challenge.state == ChallengeState.CLOSED.name:
                logger.info(f"Challenge state: {challenge.state}")
                # self.keeper.close(challenge) 
                return ChallengeState.CLOSED.name
        else:
            # new challenge
            logger.info(f"Challenge id: {challengeID} of reward {reward} tokens kept.")
            self.challenges[challengeID] = challenge

            if challenge.state == ChallengeState.CREATED.name:
                logger.info(f"Challenge state: {challenge.state}")
                # TODO: decide to join the challenge
                # update the keeper
                challenge.state = ChallengeState.ACCEPTED.name
                self.challenges[challengeID] = challenge
                return ChallengeState.ACCEPTED.name

            return challenge.state

    
        
    
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

    def update(self, receivedChallenge: Challenge) -> bool:
        # do a copy of the local challenge!
        challengeExists = self.challegeExists(receivedChallenge.id)
        if challengeExists:
            logger.info(f"Update the local version of the Challenge")
            self.challenges[receivedChallenge.id] = receivedChallenge


    # TODO: Generate the rewarding function!!!