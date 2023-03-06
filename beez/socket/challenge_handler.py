"""Beez blockchain - challenge handler"""

from __future__ import annotations
from typing import TYPE_CHECKING, Any
import threading
import time
import os
from loguru import logger
from dotenv import load_dotenv


from beez.socket.messages.message_type import MessageType
from beez.socket.messages.message_challenge import MessageChallenge
from beez.beez_utils import BeezUtils


if TYPE_CHECKING:
    from beez.socket.socket_communication.socket_communication import SocketCommunication
    from p2pnetwork.node import Node    # type: ignore
    from beez.types import ChallengeID

load_dotenv()  # load .env
LOCAL_INTERVALS = 10
INTERVALS = int(os.getenv("INTERVALS", LOCAL_INTERVALS))    # pylint: disable=invalid-envvar-default


class ChallengeHandler:
    """
    A Socket Communication submodule that frequently checks
    if there are new challenges in the network.
    """

    def __init__(self, socket_communication: SocketCommunication) -> None:
        self.socket_communication = socket_communication
        self.challenges: dict[str, Any] = {}

    def start(self):
        """Starts the status thread and the discovery thread."""
        # start node threads...
        status_tread = threading.Thread(target=self.status, args={})
        status_tread.start()

        discovery_thread = threading.Thread(target=self.discovery, args={})
        discovery_thread.start()

    def challenge_exists(self, challenge_id: ChallengeID) -> bool:
        """Returns whether a challenge with the given id exists."""
        if challenge_id in self.challenges.keys():  # pylint: disable=consider-iterating-dictionary
            return True
        return False

    def status(self):
        """Display the current challenges."""
        while True:
            logger.info("#### Current Challenges #####:")
            for idx, _ in self.socket_communication.challenges.items():
                logger.info(f"From ChallengeHandler -> ChallengeID : {idx}")
            time.sleep(INTERVALS)

    def discovery(self):
        """Looks for new challenges."""
        while True:
            logger.info("#### Manage Challenges #####")
            challenge_message = self.challenges_message()
            # Broadcast the message
            self.socket_communication.broadcast(challenge_message)

            time.sleep(INTERVALS)

    # send a message to a specific node
    def handshake(self, connected_node: Node):
        """
        exchange of information between nodes.
        """
        encoded_message = self.challenges_message()  # create the message of type DISCOVERY
        self.socket_communication.send(connected_node, encoded_message)

    def challenges_message(self):
        """
        Define the specific content of the Discovery message that will be shared between peers.
        Here, what is important is to share the knowed peers
        """
        own_connector = self.socket_communication.socket_connector
        owned_challenges = self.socket_communication.challenges
        # TODO: get the challenges from the blockchian
        logger.info(f"#### get the challenges from the blockchian {owned_challenges} #####")

        message_type = MessageType.CHALLENGE

        message = MessageChallenge(own_connector, message_type, owned_challenges)

        # Encode the message since peers communicate with bytes!
        encoded_message: str = BeezUtils.encode(message)

        return encoded_message

    # def handle_challenges_message(self, message: MessageChallenge):
    #     """Handles an incomming challenge message."""
    #     challenges: Challenge = message.challenge
    #     new_challenge = True

        # TODO: implement this
        # for idx, challenge in challenges.items():
        #     challege_exist = self.challenge_exists(idx)
        #     if challege_exist:
        #         # challenge already exist!
        #         # TODO: check if must be updated!!!
        #         new_challenge = False

        #     if new_challenge is True:
        #         # Add the challenge to the Dictionary
        #         self.socket_communication.challenges[idx] = challenge
