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
LOCAL_INTERVALS = 10
INTERVALS = int(os.getenv('INTERVALS', LOCAL_INTERVALS))

if TYPE_CHECKING:
    from beez.Types import Prize, ChallengeID, PublicKeyString
    from beez.transaction.ChallengeTX import ChallengeTX
    from beez.challenge.Challenge import Challenge

from beez.BeezUtils import BeezUtils
from beez.challenge.ChallengeState import ChallengeState
from beez.index.IndexEngine import ChallengeModelEngine
from whoosh.fields import Schema, TEXT, KEYWORD,ID
from typing import Any



class BeezKeeper():
    """
    keeps track of each Challenge.
    Every time that a block is added to the Blockchain, the beezKeeper will update the challenge based
    on the transactions accured.
    """
    def __init__(self):
        self.challenges_index = ChallengeModelEngine.get_engine(Schema(id=ID(stored=True), type=KEYWORD(stored=True), challenge_pickled=TEXT(stored=True)))

    def start(self):
        # start node threads... 
        statusThread = threading.Thread(target=self.status, args={})
        statusThread.start()

    def serialize(self) -> dict[str, Challenge]:
        # Load all challenges from index
        return self.challanges()

    @staticmethod
    def deserialize(serialized_challenges, index=True):
        return BeezKeeper()._deserialize(serialized_challenges)

    def _deserialize(self, serialized_challenges):
        # Reset challenges from serialized challenges
        self.challenges_index.delete_document("type", "CHALLENGE")
        for challenge_id, challenge in serialized_challenges.items():
            self.append(challenge_id, challenge)
            
    def challanges(self) -> dict[str, Challenge]:
        challenges: dict[str, Challenge] = {}
        challenge_docs = self.challenges_index.query(q="CHALLENGE", fields=["type"], highlight=True)
        for doc in challenge_docs:
            ch = Challenge.fromPickle(doc["challenge_pickled"])
            challenges[doc["id"]] = ch
        return challenges

    def append(self, id: str, challenge: Challenge):
        self.challenges_index.index_documents([{"id": id, "type": "CHALLENGE", "challenge_pickled": Challenge.toPickle(challenge)}])

    def status(self):
         while True:
            logger.info(f"challenge status.... {len(self.challenges().items())}")
            
            for key, value in self.challanges().items():
                challenge: Challenge = value
                challengeID : ChallengeID = key
                
                logger.info(f"Do something with challenge ID: {challengeID} on status: {challenge.state}")

            # challengeStatusMessage = self.challengeStatusMessage()
            # # Broadcast the message
            # self.socketCommunication.broadcast(challengeStatusMessage)

            time.sleep(INTERVALS)
        
    def set(self, challenge: Challenge):
        challengeID : ChallengeID = challenge.id
        reward = challenge.reward

        if challengeID in self.challenges().keys():
            logger.info(f"Challenge already created")
        else:
            # new challenge! Thinkto broadcast the challenge and no more!
            logger.info(f"Challenge id: {challengeID} of reward {reward} tokens kept. Challenge STATE: {challenge.state}")

            self.append(challengeID, challenge)

            self.workOnChallenge(challenge)

    def get(self, challengeID: ChallengeID) -> Optional[Challenge]:
        if challengeID in self.challenges().keys():
            return self.challenges()[challengeID]
        else:
            return None

    def challegeExists(self, challengeID: ChallengeID) -> bool:
        if challengeID in self.challenges().keys():
            return True
        else:
            return False


    def workOnChallenge(self, challenge: Challenge):
        logger.info(f"work on challenge... move to the ChallengesHandler this job! {challenge.id}")

        # Accept the challenge!
        # update the challenge state!
        # create a new Challenge TX!

        logger.info(f"challenge function: {challenge.sharedFunction.__doc__}")

        sharedfunction = challenge.sharedFunction
        # logger.info(f"challenge function: {type(sharedfunction)}")
        inputA = random.randint(0, 100)
        inputB = random.randint(0, 100)

        result = sharedfunction(inputA, inputB)

        logger.info(f"result: {result}")
        



    def update(self, receivedChallenge: Challenge) -> bool:
        # do a copy of the local challenge!
        challengeExists = self.challegeExists(receivedChallenge.id)
        if challengeExists:
            logger.info(f"Update the local version of the Challenge")
            self.challenges_index.delete_document("id", receivedChallenge.id)
            self.append(receivedChallenge.id, receivedChallenge)



    # TODO: Generate the rewarding function!!!