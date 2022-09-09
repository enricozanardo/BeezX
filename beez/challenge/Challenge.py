from __future__ import annotations
from typing import TYPE_CHECKING, Any, Callable
import uuid
import jsonpickle

if TYPE_CHECKING:
    from beez.Types import SharedFunction, Prize
    
from beez.challenge.ChallengeState import ChallengeState

class Challenge():
    """
    Manage the challenge that must be broacasted to a cluster of peers.
    """

    def __init__(self, sharedFunction: Callable[[], Any], reward: Prize):
        self.id = uuid.uuid1().hex
        self.sharedFunction = sharedFunction
        self.state = ChallengeState.CREATED.name
        self.reward = reward

    @staticmethod
    def fromPickle(pickle):
        return jsonpickle.decode(pickle)

    @staticmethod
    def toPickle(challenge: Challenge):
        return jsonpickle.encode(challenge)


