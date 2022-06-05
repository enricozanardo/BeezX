from __future__ import annotations
from typing import TYPE_CHECKING, Dict, Optional
from loguru import logger
import copy
import threading
import os
from dotenv import load_dotenv
import time

# for function
import random

load_dotenv()  # load .env

if TYPE_CHECKING:
    from beez.Types import Prize, ChallengeID, PublicKeyString
    from beez.transaction.ChallengeTX import ChallengeTX
    from beez.challenge.Challenge import Challenge

from beez.BeezUtils import BeezUtils
from beez.challenge.ChallengeState import ChallengeState



class BeezKeeper():
    """
    keeps track of each Challenge.
    Every time that a block is added to the Blockchain, the beezKeeper will update the challenge based
    on the transactions accured.
    """
    def __init__(self):
        self.challenges : Dict[ChallengeID : Challenge] = {}
    
    def set(self, challenge: Challenge):
        challengeID : ChallengeID = challenge.id
        reward = challenge.reward

        if challengeID in self.challenges.keys():
            logger.info(f"Challenge already created, update the challenge {challengeID}")
            self.challenges[challengeID] = challenge
        else:
            # new challenge! Thinkto broadcast the challenge and no more!
            logger.info(f"Challenge id: {challengeID} of reward {reward} tokens kept. Challenge STATE: {challenge.state}")
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


    def acceptChallenge(self, challenge: Challenge):
        logger.info(f"accept challengeid: {challenge.id}")
        logger.info(f"Current ChallengeState: {challenge.state}")
        isAccepted = False

        if challenge.state == ChallengeState.CREATED.name:

            localChallenge : Challenge = self.challenges[challenge.id]
            localChallenge.state = ChallengeState.ACCEPTED.name
            self.challenges[challenge.id] = localChallenge

            logger.info(f"Updated localKeeper ChallengeState: {localChallenge.state}")
            isAccepted = True
        
        return isAccepted


    def workOnChallenge(self, challenge: Challenge):
        logger.info(f"work on challenge...! {challenge.id}")

        logger.info(f"Current ChallengeState: {challenge.state}")
        if challenge.state == ChallengeState.CREATED.name:

            localChallenge : Challenge = self.challenges[challenge.id]
            localChallenge.state = ChallengeState.ACCEPTED.name
            self.challenges[challenge.id] = localChallenge

            logger.info(f"Updated localKeeper ChallengeState: {localChallenge.state}")

    
        # #work on challenge!
        # if challenge.state == ChallengeState.ACCEPTED.name:
        #     # Somebody else is working on the challenge...
        #     logger.info(f"Somebody else is working on the challenge.. {challenge.state}")

        localChallenge : Challenge = self.challenges[challenge.id]

        if localChallenge.state == ChallengeState.ACCEPTED.name:
            logger.info(f"challenge function: {localChallenge.sharedFunction.__doc__}")
            sharedfunction = localChallenge.sharedFunction
            # logger.info(f"challenge function: {type(sharedfunction)}")
            inputA = random.randint(0, 100)
            inputB = random.randint(0, 100)

            result = sharedfunction(inputA, inputB)

            localChallenge.result = localChallenge.result + result

            logger.info(f"result: {result}")
            logger.info(f"localChallenge result: {localChallenge.result}")

            # localChallenge.state = ChallengeState.CLOSED.name
            # self.challenges[challenge.id] = localChallenge
            # logger.info(f"Updated localKeeper ChallengeState: {localChallenge.state}")

       
        
    def update(self, receivedChallenge: Challenge) -> bool:
        # do a copy of the local challenge!
        challengeExists = self.challegeExists(receivedChallenge.id)
        if challengeExists:
            logger.info(f"Update the local version of the Challenge")
            self.challenges[receivedChallenge.id] = receivedChallenge


    # TODO: Generate the rewarding function!!!