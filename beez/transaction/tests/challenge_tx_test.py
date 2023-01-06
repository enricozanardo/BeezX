# pylint: skip-file
import pytest
import pathlib
import shutil
import json
import jsonpickle

from beez.beez_utils import BeezUtils
from beez.wallet.wallet import Wallet
from beez.transaction.challenge_tx import ChallengeTX
from beez.challenge.challenge import Challenge
from beez.transaction.transaction_type import TransactionType

def clear_indices():
    shutil.rmtree("account_indices", ignore_errors=True)
    shutil.rmtree("balance_indices", ignore_errors=True)
    shutil.rmtree("blocks_indices", ignore_errors=True)
    shutil.rmtree("challenge_indices", ignore_errors=True)
    shutil.rmtree("pos_indices", ignore_errors=True)
    shutil.rmtree("txp_indices", ignore_errors=True)

def shared_function(a: int, b: int):
    return a+b

@pytest.fixture
def challenge_tx():
    currentPath = pathlib.Path().resolve()

    genesis_private_key_path = f"{currentPath}/beez/keys/genesisPrivateKey.pem"
    alice_private_key_path = f"{currentPath}/beez/keys/alicePrivateKey.pem"

    genesis_wallet = Wallet()
    genesis_wallet.from_key(genesis_private_key_path)
    alice_wallet = Wallet()
    alice_wallet.from_key(alice_private_key_path)
    challenge = Challenge(shared_function, 5)
    challenge_tx = alice_wallet.create_challenge_transaction(10, TransactionType.CHALLENGE.name, challenge)

    yield challenge_tx
    clear_indices()

def test_challenge_tx_creation(challenge_tx):
    currentPath = pathlib.Path().resolve()

    genesis_private_key_path = f"{currentPath}/beez/keys/genesisPrivateKey.pem"
    alice_private_key_path = f"{currentPath}/beez/keys/alicePrivateKey.pem"

    genesis_wallet = Wallet()
    genesis_wallet.from_key(genesis_private_key_path)
    alice_wallet = Wallet()
    alice_wallet.from_key(alice_private_key_path)

    assert challenge_tx is not None
    assert challenge_tx.sender_address == BeezUtils.address_from_public_key(alice_wallet.public_key_string())
    assert challenge_tx.receiver_address == BeezUtils.address_from_public_key(alice_wallet.public_key_string())
    assert challenge_tx.amount == 10
    assert challenge_tx.transaction_type == TransactionType.CHALLENGE.name
    assert challenge_tx.challenge.shared_function == shared_function

def test_to_json(challenge_tx):
    currentPath = pathlib.Path().resolve()

    genesis_private_key_path = f"{currentPath}/beez/keys/genesisPrivateKey.pem"
    alice_private_key_path = f"{currentPath}/beez/keys/alicePrivateKey.pem"

    genesis_wallet = Wallet()
    genesis_wallet.from_key(genesis_private_key_path)
    alice_wallet = Wallet()
    alice_wallet.from_key(alice_private_key_path)

    assert challenge_tx.to_json() == {
        "id": challenge_tx.identifier,
        "senderAddress": BeezUtils.address_from_public_key(alice_wallet.public_key_string()),
        "receiverAddress": BeezUtils.address_from_public_key(alice_wallet.public_key_string()),
        "amount": 10,
        "type": TransactionType.CHALLENGE.name,
        "timestamp": challenge_tx.timestamp,
        "signature": challenge_tx.signature,
        "challenge": json.loads(jsonpickle.encode(challenge_tx.challenge))
    }

def test_from_json():
    currentPath = pathlib.Path().resolve()

    genesis_private_key_path = f"{currentPath}/beez/keys/genesisPrivateKey.pem"
    alice_private_key_path = f"{currentPath}/beez/keys/alicePrivateKey.pem"

    genesis_wallet = Wallet()
    genesis_wallet.from_key(genesis_private_key_path)
    alice_wallet = Wallet()
    alice_wallet.from_key(alice_private_key_path)

    challenge = Challenge(shared_function, 10)
    local_challenge_tx = ChallengeTX.from_json({
        "id": "abc",
        "senderPublicKey": BeezUtils.address_from_public_key(alice_wallet.public_key_string()),
        "receiverPublicKey": BeezUtils.address_from_public_key(alice_wallet.public_key_string()),
        "amount": 10,
        "type": TransactionType.CHALLENGE.name,
        "timestamp": "now",
        "signature": "alice_signature",
        "challenge": json.loads(jsonpickle.encode(challenge))
    })

    assert local_challenge_tx.sender_address == BeezUtils.address_from_public_key(alice_wallet.public_key_string())
    assert local_challenge_tx.receiver_address == BeezUtils.address_from_public_key(alice_wallet.public_key_string())
    assert local_challenge_tx.amount == 10
    assert local_challenge_tx.transaction_type == TransactionType.CHALLENGE.name
    assert local_challenge_tx.timestamp == "now"
    assert local_challenge_tx.signature == "alice_signature"
    assert local_challenge_tx.challenge.reward == 10
    assert local_challenge_tx.challenge.shared_function == shared_function
    clear_indices()
