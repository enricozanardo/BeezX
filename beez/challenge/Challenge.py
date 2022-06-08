from __future__ import annotations
from typing import TYPE_CHECKING, Any, Callable, Dict, Optional
import uuid

if TYPE_CHECKING:
    from beez.Types import SharedFunction, Prize, PublicKeyString
    from beez.challenge.ChallengeType import ChallengeType

    
from beez.challenge.ChallengeState import ChallengeState


class Challenge():
    """
    Manage the challenge that must be broacasted to a cluster of peers.
    """

    def __init__(self, ownerPublicKey: PublicKeyString, sharedFunction: Callable[[], Any], reward: Prize, iteration: int, challengeType: ChallengeType):
        self.id = uuid.uuid1().hex
        self.ownerPublicKey = ownerPublicKey
        self.sharedFunction = sharedFunction
        self.challengeType = challengeType
        self.state = ChallengeState.CREATED.name
        self.reward = reward
        self.iteration = iteration
        self.result = 0
        self.counter = 1
        self.workers : Dict[PublicKeyString: int] = {}

        



