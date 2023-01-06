# pylint: skip-file
import pytest
import pathlib
import shutil

from beez.beez_utils import BeezUtils
from beez.wallet.wallet import Wallet
from beez.transaction.transaction import Transaction
from beez.transaction.transaction_type import TransactionType

def clear_indices():
    shutil.rmtree("account_indices", ignore_errors=True)
    shutil.rmtree("balance_indices", ignore_errors=True)
    shutil.rmtree("blocks_indices", ignore_errors=True)
    shutil.rmtree("challenge_indices", ignore_errors=True)
    shutil.rmtree("pos_indices", ignore_errors=True)
    shutil.rmtree("txp_indices", ignore_errors=True)

@pytest.fixture
def transaction():
    currentPath = pathlib.Path().resolve()

    alice_private_key_path = f"{currentPath}/beez/keys/alicePrivateKey.pem"
    bob_private_key_path = f"{currentPath}/beez/keys/bobPrivateKey.pem"

    alice_wallet = Wallet()
    alice_wallet.from_key(alice_private_key_path)
    bob_wallet = Wallet()
    bob_wallet.from_key(bob_private_key_path)

    transaction = Transaction(
        BeezUtils.address_from_public_key(alice_wallet.public_key_string()),
        BeezUtils.address_from_public_key(bob_wallet.public_key_string()),
        10,
        TransactionType.TRANSFER.name
    )
    yield transaction
    clear_indices()

def test_transaction_creation(transaction):
    currentPath = pathlib.Path().resolve()

    alice_private_key_path = f"{currentPath}/beez/keys/alicePrivateKey.pem"
    bob_private_key_path = f"{currentPath}/beez/keys/bobPrivateKey.pem"

    alice_wallet = Wallet()
    alice_wallet.from_key(alice_private_key_path)
    bob_wallet = Wallet()
    bob_wallet.from_key(bob_private_key_path)

    assert transaction is not None
    assert transaction.signature == ""
    assert transaction.amount == 10
    assert transaction.sender_address == BeezUtils.address_from_public_key(alice_wallet.public_key_string())
    assert transaction.receiver_address == BeezUtils.address_from_public_key(bob_wallet.public_key_string())

def test_sign(transaction):
    transaction.sign("test_signature")
    assert transaction.signature == "test_signature"

def test_to_json(transaction):
    currentPath = pathlib.Path().resolve()

    alice_private_key_path = f"{currentPath}/beez/keys/alicePrivateKey.pem"
    bob_private_key_path = f"{currentPath}/beez/keys/bobPrivateKey.pem"

    alice_wallet = Wallet()
    alice_wallet.from_key(alice_private_key_path)
    bob_wallet = Wallet()
    bob_wallet.from_key(bob_private_key_path)

    assert transaction.to_json() == {
        "id": transaction.identifier,
        "senderAddress": BeezUtils.address_from_public_key(alice_wallet.public_key_string()),
        "receiverAddress": BeezUtils.address_from_public_key(bob_wallet.public_key_string()),
        "amount": 10,
        "type": TransactionType.TRANSFER.name,
        "timestamp": transaction.timestamp,
        "signature": ""
    }

def test_from_json():
    local_transaction = Transaction.from_json(
        {
            "id": "abc",
            "senderAddress": "bob",
            "receiverAddress": "alice",
            "amount": 10,
            "type": TransactionType.TRANSFER.name,
            "timestamp": "now",
            "signature": "bob_signature"
        }
    )
    assert local_transaction.identifier == "abc"
    assert local_transaction.sender_address == "bob"
    assert local_transaction.receiver_address == "alice"
    assert local_transaction.amount == 10
    assert local_transaction.transaction_type == TransactionType.TRANSFER.name
    assert local_transaction.timestamp == "now"
    assert local_transaction.signature == "bob_signature"
    clear_indices()

def test_equals(transaction):
    currentPath = pathlib.Path().resolve()

    alice_private_key_path = f"{currentPath}/beez/keys/alicePrivateKey.pem"
    bob_private_key_path = f"{currentPath}/beez/keys/bobPrivateKey.pem"

    alice_wallet = Wallet()
    alice_wallet.from_key(alice_private_key_path)
    bob_wallet = Wallet()
    bob_wallet.from_key(bob_private_key_path)

    local_transaction = Transaction(
        alice_wallet.public_key_string(),
        bob_wallet.public_key_string(),
        10,
        TransactionType.TRANSFER.name
    )
    
    assert local_transaction.equals(transaction) == False
    assert transaction.equals(transaction)

def test_payload(transaction):
    currentPath = pathlib.Path().resolve()

    alice_private_key_path = f"{currentPath}/beez/keys/alicePrivateKey.pem"
    bob_private_key_path = f"{currentPath}/beez/keys/bobPrivateKey.pem"

    alice_wallet = Wallet()
    alice_wallet.from_key(alice_private_key_path)
    bob_wallet = Wallet()
    bob_wallet.from_key(bob_private_key_path)

    transaction.sign("signature")
    assert transaction.payload() == {
        "id": transaction.identifier,
        "senderAddress": BeezUtils.address_from_public_key(alice_wallet.public_key_string()),
        "receiverAddress": BeezUtils.address_from_public_key(bob_wallet.public_key_string()),
        "amount": 10,
        "type": TransactionType.TRANSFER.name,
        "timestamp": transaction.timestamp,
        "signature": ""
    }