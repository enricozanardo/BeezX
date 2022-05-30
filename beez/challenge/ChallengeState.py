from enum import Enum


class ChallengeState(Enum):
    """
    Define the state of a challenge that will accur into the Blockchain

    CREATED: The challenge tx is stored into the blockchain and 
    OPENED: Peers started to work on the joined challenge
    UPDATED: The challenge has got some results and is updated 
    CLOSED: Challege closed and peers that joined the challege are rewarded
    """
    CREATED = "created"
    OPENED = "opened"
    UPDATED = "updated"
    CLOSED = "closed"