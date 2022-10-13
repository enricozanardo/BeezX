"""Beez blockchain - challenge."""
from __future__ import annotations
from typing import TYPE_CHECKING, Any, Callable
import uuid
import jsonpickle
from beez.challenge.challenge_state import ChallengeState

if TYPE_CHECKING:
    from beez.types import Prize



class Challenge:
    """
    Manage the challenge that must be broacasted to a cluster of peers.
    """

    def __init__(self, shared_function: Callable[[], Any], reward: Prize):
        self.identifier = uuid.uuid1().hex
        self.shared_function = shared_function
        self.state = ChallengeState.CREATED.name
        self.reward = reward

    @staticmethod
    def from_pickle(pickle):
        """Loading a challenge from pickle format."""
        return jsonpickle.decode(pickle)

    @staticmethod
    def to_pickle(challenge: Challenge):
        """Pickle challenge object."""
        return jsonpickle.encode(challenge)
