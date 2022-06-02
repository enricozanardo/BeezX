from __future__ import annotations
from typing import TYPE_CHECKING, Dict
import threading
import time
from loguru import logger
import os
from dotenv import load_dotenv


from beez.socket.MessageType import MessageType
from beez.socket.MessageChallenge import MessageChallenges
from beez.BeezUtils import BeezUtils


if TYPE_CHECKING:
    from beez.socket.SocketCommunication import SocketCommunication
    from p2pnetwork.node import Node
    from beez.challenge.Challenge import Challenge
    from beez.Types import ChallengeID
    from beez.node.BeezNode import BeezNode

load_dotenv()  # load .env
LOCAL_INTERVALS = 10
INTERVALS = int(os.getenv('INTERVALS', LOCAL_INTERVALS))


class ChallengeHandler():
    """
    A Socket Communication submodule that frequently checks if there are new challenges in the network.
    """
    def __init__(self, socketCommunication: SocketCommunication) -> None:
        self.socketCommunication = socketCommunication
        
    def start(self):
        # start node threads... 
        statusThread = threading.Thread(target=self.status, args={})
        statusThread.start()

        discoveryThread = threading.Thread(target=self.discovery, args={})
        discoveryThread.start()

    def challegeExists(self, challengeID: ChallengeID) -> bool:
        if challengeID in self.challenges.keys():
            return True
        else:
            return False

    """
    Display the current challenges
    """
    def status(self):
        while True:
            logger.info(f"#### Current Challenges #####:")
            for idx, challenge in self.socketCommunication.challenges.items():
                logger.info(f"From ChallengeHandler -> ChallengeID : {idx}")
            time.sleep(INTERVALS)


    def discovery(self):
         while True:
            logger.info(f"#### Manage Challenges #####")
            challengeMessage = self.challengesMessage()
            # Broadcast the message
            self.socketCommunication.broadcast(challengeMessage)

            time.sleep(INTERVALS)

    # send a message to a specific node
    def handshake(self, connectedNode: Node):
        """
        exchange of information between nodes.
        """
        encodedMessage = self.challengesMessage() # create the message of type DISCOVERY
        self.socketCommunication.send(connectedNode, encodedMessage)

        
    def challengesMessage(self):
        """
        Define the specific content of the Discovery message that will be shared between peers.
        Here, what is important is to share the knowed peers
        """
        ownConnector = self.socketCommunication.socketConnector
        ownedChallenges = self.socketCommunication.challenges
        # TODO: get the challenges from the blockchian
        logger.info(f"#### get the challenges from the blockchian {ownedChallenges} #####")
        
        messageType = MessageType.CHALLENGES.name

        message = MessageChallenges(ownConnector, messageType, ownedChallenges)

        # Encode the message since peers communicate with bytes!
        encodedMessage: str = BeezUtils.encode(message)

        return encodedMessage

    def handleChallengesMessage(self, message: MessageChallenges):

        challenges: Dict[ChallengeID : Challenge] = message.challenges
        newChallenge = True

        for idx, challenge in challenges.items():
            challegeExist = self.challegeExists(idx)
            if challegeExist:
                # challenge already exist!
                # TODO: check if must be updated!!!
                newChallenge = False
            
            if newChallenge == True:
                # Add the challenge to the Dictionary
                self.socketCommunication.challenges[idx] = challenge