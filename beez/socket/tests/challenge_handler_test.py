# pylint: skip-file
import pytest
import shutil
from beez.socket.challenge_handler import ChallengeHandler
from beez.socket.socket_communication.socket_communication import SocketCommunication

def clear_indices():
    shutil.rmtree("account_indices", ignore_errors=True)
    shutil.rmtree("balance_indices", ignore_errors=True)
    shutil.rmtree("blocks_indices", ignore_errors=True)
    shutil.rmtree("challenge_indices", ignore_errors=True)
    shutil.rmtree("pos_indices", ignore_errors=True)

# Cannot use fixture because cannot connect host to port bc.
# Address already in use error --> 
# https://stackoverflow.com/questions/6380057/python-binding-
# socket-address-already-in-use
@pytest.fixture
def challenge_handler():
    socket_communication = SocketCommunication("127.0.0.1", 4445)
    yield ChallengeHandler(socket_communication)
    socket_communication.stop()
    clear_indices()

def test_challenge_handler_creation():
    socket_communication = SocketCommunication("127.0.0.1", 4445)
    challenge_handler = ChallengeHandler(socket_communication)
    assert challenge_handler is not None
    assert challenge_handler.challenges == {}
    clear_indices()

def test_challenge_exists():
    socket_communication = SocketCommunication("127.0.0.1", 4446)
    challenge_handler = ChallengeHandler(socket_communication)
    assert challenge_handler.challenge_exists("testid") == False
    clear_indices()
