# pylint: skip-file
import pytest
import shutil
from beez.challenge.beez_keeper import BeezKeeper
from beez.challenge.challenge import Challenge

def clear_indices():
    shutil.rmtree("account_indices", ignore_errors=True)
    shutil.rmtree("balance_indices", ignore_errors=True)
    shutil.rmtree("blocks_indices", ignore_errors=True)
    shutil.rmtree("challenge_indices", ignore_errors=True)
    shutil.rmtree("pos_indices", ignore_errors=True)

@pytest.fixture
def beez_keeper():
    yield BeezKeeper()
    clear_indices()

def test_beez_keeper_creation(beez_keeper):
    assert beez_keeper is not None

def test_serialize(beez_keeper):
    assert beez_keeper.serialize() == {}

def test_deserialize():
    challenge = Challenge(sum, 10)
    local_beez_keeper = BeezKeeper.deserialize({"test_public_key": challenge})
    assert len(local_beez_keeper.challanges()) == 1
    assert local_beez_keeper.challanges()["test_public_key"].reward == 10
    assert local_beez_keeper.challanges()["test_public_key"].shared_function == sum
    clear_indices()

def test_challenges(beez_keeper):
    beez_keeper.append("test", Challenge(sum, 100))
    assert len(beez_keeper.challanges()) == 1
    assert beez_keeper.challanges()["test"].reward == 100
    assert beez_keeper.challanges()["test"].shared_function == sum

def test_append(beez_keeper):
    beez_keeper.append("test", Challenge(sum, 100))
    assert len(beez_keeper.challanges()) == 1
    assert beez_keeper.challanges()["test"].reward == 100
    assert beez_keeper.challanges()["test"].shared_function == sum

def test_set(beez_keeper):
    def add(a:int, b:int) -> int:
        return a+b
    challenge = Challenge(add, 15)
    challenge_2 = Challenge(add, 30)
    beez_keeper.set(challenge)
    beez_keeper.set(challenge_2)
    assert len(beez_keeper.challanges()) == 2

def test_get(beez_keeper):
    beez_keeper.append("test", Challenge(sum, 99))
    assert beez_keeper.get("test").reward == 99

def test_challenge_exists(beez_keeper):
    beez_keeper.append("test", Challenge(sum, 99))
    assert beez_keeper.challege_exists("test") == True
    assert beez_keeper.challege_exists("test2") == False

def test_update(beez_keeper):
    challenge = Challenge(sum, 99)
    challenge.identifier = "id"
    beez_keeper.append("id", challenge)
    challenge.reward = 100
    beez_keeper.update(challenge)
    assert beez_keeper.get("id").reward == 100