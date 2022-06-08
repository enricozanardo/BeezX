from enum import Enum


class ChallengeType(Enum):
    """
    Define the types of challenge that will worked by the peers.

    CALCULUS: Perform a shared function
    IRIS: Train a model of the IRIS dataset
    """
    CALCULUS = "calculus"
    IRIS = "iris"
   