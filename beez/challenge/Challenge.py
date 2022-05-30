from __future__ import annotations
from typing import TYPE_CHECKING, Any, Callable

if TYPE_CHECKING:
    from beez.Types import SharedFunction
    
from beez.challenge.ChallengeState import ChallengeState

class Challenge():
    """
    Manage the challenge that must be broacasted to a cluster of peers.
    """

    def __init__(self, sharedFunction: Callable[[], Any]):
        self.sharedFunction = sharedFunction
        self.state = ChallengeState.OPENED.name


