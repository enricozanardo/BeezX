"""Beez blockchain - beez keeper."""
from __future__ import annotations

# for function
import random
import threading
import time
import os
from typing import TYPE_CHECKING, Optional
from loguru import logger
from dotenv import load_dotenv

from whoosh.fields import Schema, TEXT, KEYWORD, ID     # type: ignore
from beez.index.index_engine import ChallengeModelEngine

if TYPE_CHECKING:
    from beez.types import Prize, ChallengeID, PublicKeyString
    from beez.challenge.challenge import Challenge

load_dotenv()  # load .env
LOCAL_INTERVALS = 10
INTERVALS = int(
    os.getenv("INTERVALS", LOCAL_INTERVALS) # pylint: disable=invalid-envvar-default
)


class BeezKeeper:
    """
    keeps track of each Challenge.
    Every time that a block is added to the Blockchain, the beezKeeper will update
    the challenge basedon the transactions accured.
    """

    def __init__(self):
        self.challenges_index = ChallengeModelEngine.get_engine(
            Schema(
                id=ID(stored=True),
                type=KEYWORD(stored=True),
                challenge_pickled=TEXT(stored=True),
            )
        )

    def start(self):
        """Starting the beez keeper thread."""
        # start node threads...
        status_thread = threading.Thread(target=self.status, args={})
        status_thread.start()

    def serialize(self) -> dict[str, Challenge]:
        """Returns all challenges"""
        # Load all challenges from index
        return self.challanges()

    @staticmethod
    def deserialize(serialized_challenges, index=True):  # pylint: disable=unused-argument
        """Returning a beez keeper from serialized challenges."""
        return BeezKeeper()._deserialize(   # pylint: disable=protected-access
            serialized_challenges
        )

    def _deserialize(self, serialized_challenges):
        """Deserialize beez keeper."""
        # Reset challenges from serialized challenges
        self.challenges_index.delete_document("type", "CHALLENGE")
        for challenge_id, challenge in serialized_challenges.items():
            self.append(challenge_id, challenge)

    def challanges(self) -> dict[str, Challenge]:
        """Returns all challenges."""
        challenges: dict[str, Challenge] = {}
        challenge_docs = self.challenges_index.query(
            query="CHALLENGE", fields=["type"], highlight=True
        )
        for doc in challenge_docs:
            challenge = Challenge.from_pickle(doc["challenge_pickled"])
            challenges[doc["id"]] = challenge
        return challenges

    def append(self, identifier: str, challenge: Challenge):
        """Adds a new challenge."""
        self.challenges_index.index_documents(
            [
                {
                    "id": identifier,
                    "type": "CHALLENGE",
                    "challenge_pickled": Challenge.to_pickle(challenge),
                }
            ]
        )

    def status(self):
        """Logs status of beezkepper."""
        while True:
            logger.info(f"challenge status.... {len(self.challanges().items())}")

            for key, value in self.challanges().items():
                challenge: Challenge = value
                challenge_id: ChallengeID = key

                logger.info(
                    f"Do something with challenge ID: {challenge_id} on status: {challenge.state}"
                )

            # challengeStatusMessage = self.challengeStatusMessage()
            # # Broadcast the message
            # self.socketCommunication.broadcast(challengeStatusMessage)

            time.sleep(INTERVALS)

    def set(self, challenge: Challenge):
        """Set a challenge."""
        challenge_id: ChallengeID = challenge.identifier
        reward = challenge.reward

        if (
            challenge_id
            in self.challanges().keys()  # pylint: disable=consider-iterating-dictionary
        ):
            logger.info("Challenge already created")
        else:
            # new challenge! Thinkto broadcast the challenge and no more!
            logger.info(
                f"""Challenge id: {challenge_id} of reward {reward} tokens kept.
                Challenge STATE: {challenge.state}"""
            )

            self.append(challenge_id, challenge)

            self.work_on_challenge(challenge)

    def get(self, challenge_id: ChallengeID) -> Optional[Challenge]:
        """Get a challenge by id."""
        if (
            challenge_id
            in self.challanges().keys()  # pylint: disable=consider-iterating-dictionary
        ):
            return self.challanges()[challenge_id]
        return None

    def challege_exists(self, challenge_id: ChallengeID) -> bool:
        """Check if challenge exists."""
        if (
            challenge_id
            in self.challanges().keys()  # pylint: disable=consider-iterating-dictionary
        ):
            return True
        return False

    def work_on_challenge(self, challenge: Challenge):
        """Work on given challenge."""
        logger.info(
            f"work on challenge... move to the ChallengesHandler this job! {challenge.identifier}"
        )

        # Accept the challenge!
        # update the challenge state!
        # create a new Challenge TX!

        logger.info(f"challenge function: {challenge.shared_function.__doc__}")

        shared_function = challenge.shared_function
        # logger.info(f"challenge function: {type(sharedfunction)}")
        input_a = random.randint(0, 100)
        input_b = random.randint(0, 100)

        result = shared_function(input_a, input_b)  # type: ignore

        logger.info(f"result: {result}")

    def update(self, received_challenge: Challenge) -> None:
        """Updating the local version of a challenge."""
        # do a copy of the local challenge!
        challenge_exists = self.challege_exists(received_challenge.identifier)
        if challenge_exists:
            logger.info("Update the local version of the Challenge")
            self.challenges_index.delete_document("id", received_challenge.identifier)
            self.append(received_challenge.identifier, received_challenge)

    # TODO: Generate the rewarding function!!!
