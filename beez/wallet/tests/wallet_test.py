# pylint: skip-file
import shutil
import pathlib
import pytest
from beez.wallet.wallet import Wallet
from beez.block.block import Block
from beez.block.blockchain import Blockchain
from beez.beez_utils import BeezUtils
from beez.transaction.transaction_type import TransactionType
from beez.challenge.challenge import Challenge

def remove_blockchain():
    shutil.rmtree("blocks_indices")

@pytest.fixture
def wallet():
    return Wallet()

@pytest.fixture()
def blockchain():
    yield Blockchain()
    remove_blockchain()

def test_wallet_creation(wallet):
    assert wallet is not None

def test_generate_address(wallet):
    assert wallet.address != ""

def test_from_key():
    currentPath = pathlib.Path().resolve()
    bob_private_key_path = f"{currentPath}/beez/keys/bobPrivateKey.pem"

    bob_wallet = Wallet()
    bob_wallet.from_key(bob_private_key_path)

    assert bob_wallet.public_key_string() == """-----BEGIN PUBLIC KEY-----
MCowBQYDK2VwAyEA64XvCF47cEFjKYKrYoPfG9YkoRYvrhJWHIgl5hdsi08=
-----END PUBLIC KEY-----"""

def test_sign(wallet):
    test_data = "Testdata to sign"
    signature = wallet.sign(test_data)

    assert Wallet.signature_valid(test_data, signature, wallet.public_key_string()) == True
    assert Wallet.signature_valid("wrong data", signature, wallet.public_key_string()) == False

def test_signature_valid(wallet):
    second_wallet = Wallet()
    test_data = "Testdata to sign"
    signature = wallet.sign(test_data)
    assert Wallet.signature_valid(test_data, signature, wallet.public_key_string()) == True
    assert Wallet.signature_valid(test_data, signature, second_wallet.public_key_string()) == False

def test_public_key_string():
    currentPath = pathlib.Path().resolve()
    bob_private_key_path = f"{currentPath}/beez/keys/bobPrivateKey.pem"

    bob_wallet = Wallet()
    bob_wallet.from_key(bob_private_key_path)
    assert bob_wallet.public_key_string() == """-----BEGIN PUBLIC KEY-----
MCowBQYDK2VwAyEA64XvCF47cEFjKYKrYoPfG9YkoRYvrhJWHIgl5hdsi08=
-----END PUBLIC KEY-----"""

def test_challenge_transaction(wallet):
    challenge = Challenge(sum, 20)
    tx = wallet.create_challenge_transaction(
        10,
        TransactionType.CHALLENGE.name,
        challenge
    )
    assert Wallet.signature_valid(tx.payload(), tx.signature, wallet.public_key_string()) == True

def test_create_block(wallet, blockchain):
    block = wallet.create_block(
        None,
        [],
        BeezUtils.hash(blockchain.blocks()[-1].payload()).hexdigest(),
        1,
    )
    assert Wallet.signature_valid(block.payload(), block.signature, wallet.public_key_string()) == True
    