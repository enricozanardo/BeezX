"""Beez blockchain - beez keeper."""
from __future__ import annotations
import json

# for function
import random
import threading
import time
import os
from typing import TYPE_CHECKING, Optional
from loguru import logger
from dotenv import load_dotenv

from beez.challenge.challenge import Challenge

if TYPE_CHECKING:
    from beez.types import ChallengeID

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
        self.challenges: dict[str, Challenge] = {}

    def start(self):
        """Starting the beez keeper thread."""
        # start node threads...
        status_thread = threading.Thread(target=self.status, args={})
        status_thread.start()

    def serialize(self) -> dict[str, dict]:
        """Returns all challenges"""
        # Load all challenges from index
        serialized_challenges = {}
        challenges = self.challanges()
        for id, challenge in challenges.items():
            serialized_challenges[id] = json.loads(str(Challenge.to_pickle(challenge)))
        return serialized_challenges


    @staticmethod
    def deserialize(serialized_challenges: dict[str, dict], index=True):  # pylint: disable=unused-argument
        """Returning a beez keeper from serialized challenges."""
        beez_keeper = BeezKeeper()
        beez_keeper._deserialize(   # pylint: disable=protected-access
            serialized_challenges
        )
        return beez_keeper

    def _deserialize(self, serialized_challenges):
        """Deserialize beez keeper."""
        for challenge_id, challenge in serialized_challenges.items():
            self.append(challenge_id, Challenge.from_pickle(str(challenge).replace("'", '"')))

    def challanges(self) -> dict[str, Challenge]:
        """Returns all challenges."""
        return self.challenges

    def append(self, identifier: str, challenge: Challenge):
        """Adds a new challenge."""
        self.challenges[identifier] = challenge

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
            self.append(received_challenge.identifier, received_challenge)

    # TODO: Generate the rewarding function!!!
