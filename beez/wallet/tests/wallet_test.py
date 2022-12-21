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

    assert bob_wallet.public_key_string() == "2d2d2d2d2d424547494e205055424c4943204b45592d2d2d2d2d0a4d4947654d413047435371475349623344514542415155414134474d4144434269414b4267487754686d71626f6b554661706335396758766b767850707243770a33572f5775716533556b39796452454b4e3674784e666e4c69706166785449776537666a74614b46424f4e59447a396b4d30657764744c6177445175594d774c0a56417a3530474662584b7079645842374a2f59722b37574b594671335777356877637465414d476b663851524a576c655a462b4565626b425a582f51484a2b630a5764774877387a2b556b74705761665841674d424141453d0a2d2d2d2d2d454e44205055424c4943204b45592d2d2d2d2d"

def test_sign(wallet):
    test_data = "Testdata to sign"
    signature = wallet.sign(test_data)

    print(wallet.public_key_string())

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
    assert bob_wallet.public_key_string() == "2d2d2d2d2d424547494e205055424c4943204b45592d2d2d2d2d0a4d4947654d413047435371475349623344514542415155414134474d4144434269414b4267487754686d71626f6b554661706335396758766b767850707243770a33572f5775716533556b39796452454b4e3674784e666e4c69706166785449776537666a74614b46424f4e59447a396b4d30657764744c6177445175594d774c0a56417a3530474662584b7079645842374a2f59722b37574b594671335777356877637465414d476b663851524a576c655a462b4565626b425a582f51484a2b630a5764774877387a2b556b74705761665841674d424141453d0a2d2d2d2d2d454e44205055424c4943204b45592d2d2d2d2d"

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
    