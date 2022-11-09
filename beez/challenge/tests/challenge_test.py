# pylint: skip-file
import pytest
import shutil
import copy
from beez.challenge.challenge import Challenge
from beez.challenge.challenge_state import ChallengeState

def clear_indices():
    shutil.rmtree("account_indices", ignore_errors=True)
    shutil.rmtree("balance_indices", ignore_errors=True)
    shutil.rmtree("blocks_indices", ignore_errors=True)
    shutil.rmtree("challenge_indices", ignore_errors=True)
    shutil.rmtree("pos_indices", ignore_errors=True)

def shared_function(a: int, b: int) -> int:
        return a+b

@pytest.fixture
def challenge():
    yield Challenge(shared_function, 20)
    clear_indices()

def test_challenge_creation(challenge):
    assert challenge is not None
    assert challenge.shared_function == shared_function
    assert challenge.reward == 20
    assert challenge.state == ChallengeState.CREATED.name

def test_pickling():
    local_challenge = Challenge(shared_function, 30)
    challenge_copy = copy.deepcopy(local_challenge)
    pickle = Challenge.to_pickle(local_challenge)
    local_challenge = Challenge.from_pickle(pickle)
    assert local_challenge.identifier == challenge_copy.identifier
    assert local_challenge.shared_function == challenge_copy.shared_function
    assert local_challenge.state == challenge_copy.state
    assert local_challenge.reward == challenge_copy.reward
    clear_indices()