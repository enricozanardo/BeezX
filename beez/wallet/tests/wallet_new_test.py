import shutil
import pathlib
import pytest
from beez.wallet.wallet_new import Wallet
from beez.block.block import Block
from beez.block.blockchain import Blockchain
from beez.beez_utils import BeezUtils
from beez.transaction.transaction_type import TransactionType
from beez.challenge.challenge import Challenge
import binascii


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


def test_from_key():
    key = "2243f5a4b0a66b9c40e42bb0855021daf222ec6b8f249aa8eb026366f324100d"
    bob_wallet = Wallet()
    bob_wallet.from_key(key)
    assert bob_wallet.public_key_string() == key


def test_sign(wallet):
    # recupero la public key
    public_key = wallet.public_key_string()
    # definisco una variabile dati
    test_data = "Test data to sign"
    # converto i dati in hash
    test_data_hash = BeezUtils.hash(test_data)
    # converto i dati in bytes
    encoded_hash_hex = test_data_hash.hexdigest().encode('utf-8')
    data_hex = binascii.hexlify(encoded_hash_hex).decode('utf-8')
    data_bytes = bytes.fromhex(data_hex)
    # genero la signature
    signature = wallet.sign(data_bytes)
    # test sulla signature
    assert Wallet.signature_valid(test_data, signature, public_key) == True
    assert Wallet.signature_valid("Test data to error", signature, public_key) == False


def test_challenge_transaction(wallet):
    challenge = Challenge(sum, 20)
    tx = wallet.create_challenge_transaction(
        10,
        TransactionType.CHALLENGE.name,
        challenge
    )
    print('tx.payload(): ', tx.payload())
    assert Wallet.signature_valid(tx.payload(), tx.signature, wallet.public_key_string()) == True


def test_create_block(wallet, blockchain):
    block = wallet.create_block(
        None,
        [],
        BeezUtils.hash(blockchain.blocks()[-1].payload()).hexdigest(),
        1,
    )
    assert Wallet.signature_valid(block.payload(), block.signature, wallet.public_key_string()) == True
