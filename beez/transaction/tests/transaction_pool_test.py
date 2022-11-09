# pylint: skip-file
import pytest
import pathlib
import shutil

from beez.challenge.challenge import Challenge
from beez.wallet.wallet import Wallet
from beez.transaction.transaction_pool import TransactionPool
from beez.transaction.transaction_type import TransactionType

def clear_indices():
    shutil.rmtree("account_indices", ignore_errors=True)
    shutil.rmtree("balance_indices", ignore_errors=True)
    shutil.rmtree("blocks_indices", ignore_errors=True)
    shutil.rmtree("challenge_indices", ignore_errors=True)
    shutil.rmtree("pos_indices", ignore_errors=True)
    shutil.rmtree("txp_indices", ignore_errors=True)

def shared_function(a:int, b:int):
    return a+b

@pytest.fixture
def transaction_pool():
    yield TransactionPool()
    clear_indices()

def test_transaction_pool_creation(transaction_pool):
    assert transaction_pool is not None
    assert len(transaction_pool.transactions()) == 0

def test_transactions(transaction_pool):
    currentPath = pathlib.Path().resolve()

    genesis_private_key_path = f"{currentPath}/beez/keys/genesisPrivateKey.pem"
    alice_private_key_path = f"{currentPath}/beez/keys/alicePrivateKey.pem"

    genesis_wallet = Wallet()
    genesis_wallet.from_key(genesis_private_key_path)
    alice_wallet = Wallet()
    alice_wallet.from_key(alice_private_key_path)

    # set nodes wallet to be the genesis wallet in order to be able
    # to create new blocks

    exchange_tx = genesis_wallet.create_transaction(
        alice_wallet.public_key_string(), 100, TransactionType.EXCHANGE.name
    )
    transaction_pool.add_transaction(exchange_tx)
    assert len(transaction_pool.transactions()) == 1

def test_add_transaction(transaction_pool):
    currentPath = pathlib.Path().resolve()

    genesis_private_key_path = f"{currentPath}/beez/keys/genesisPrivateKey.pem"
    alice_private_key_path = f"{currentPath}/beez/keys/alicePrivateKey.pem"

    genesis_wallet = Wallet()
    genesis_wallet.from_key(genesis_private_key_path)
    alice_wallet = Wallet()
    alice_wallet.from_key(alice_private_key_path)

    # set nodes wallet to be the genesis wallet in order to be able
    # to create new blocks

    exchange_tx = genesis_wallet.create_transaction(
        alice_wallet.public_key_string(), 5, TransactionType.EXCHANGE.name
    )
    transaction_pool.add_transaction(exchange_tx)
    assert len(transaction_pool.transactions()) == 1
    assert transaction_pool.transactions()[0].amount == 5

def test_challenge_exists(transaction_pool):
    currentPath = pathlib.Path().resolve()

    genesis_private_key_path = f"{currentPath}/beez/keys/genesisPrivateKey.pem"
    alice_private_key_path = f"{currentPath}/beez/keys/alicePrivateKey.pem"

    genesis_wallet = Wallet()
    genesis_wallet.from_key(genesis_private_key_path)
    alice_wallet = Wallet()
    alice_wallet.from_key(alice_private_key_path)
    challenge = Challenge(shared_function, 5)
    challenge_tx = alice_wallet.create_challenge_transaction(10, TransactionType.CHALLENGE.name, challenge)

    assert transaction_pool.challenge_exists(challenge_tx) == False
    transaction_pool.add_transaction(challenge_tx)
    assert transaction_pool.challenge_exists(challenge_tx) == True

def test_transaction_exists(transaction_pool):
    currentPath = pathlib.Path().resolve()

    genesis_private_key_path = f"{currentPath}/beez/keys/genesisPrivateKey.pem"
    alice_private_key_path = f"{currentPath}/beez/keys/alicePrivateKey.pem"

    genesis_wallet = Wallet()
    genesis_wallet.from_key(genesis_private_key_path)
    alice_wallet = Wallet()
    alice_wallet.from_key(alice_private_key_path)
    exchange_tx = genesis_wallet.create_transaction(
        alice_wallet.public_key_string(), 5, TransactionType.EXCHANGE.name
    )

    assert transaction_pool.challenge_exists(exchange_tx) == False
    transaction_pool.add_transaction(exchange_tx)
    assert transaction_pool.challenge_exists(exchange_tx) == True

def test_remove_from_pool(transaction_pool):
    currentPath = pathlib.Path().resolve()

    genesis_private_key_path = f"{currentPath}/beez/keys/genesisPrivateKey.pem"
    alice_private_key_path = f"{currentPath}/beez/keys/alicePrivateKey.pem"

    genesis_wallet = Wallet()
    genesis_wallet.from_key(genesis_private_key_path)
    alice_wallet = Wallet()
    alice_wallet.from_key(alice_private_key_path)
    exchange_tx = genesis_wallet.create_transaction(
        alice_wallet.public_key_string(), 5, TransactionType.EXCHANGE.name
    )
    exchange_tx_2 = genesis_wallet.create_transaction(
        alice_wallet.public_key_string(), 10, TransactionType.EXCHANGE.name
    )
    transaction_pool.add_transaction(exchange_tx)
    transaction_pool.add_transaction(exchange_tx_2)
    assert len(transaction_pool.transactions()) == 2

    transaction_pool.remove_from_pool([exchange_tx])    
    assert len(transaction_pool.transactions()) == 1
    assert transaction_pool.transactions()[0].identifier == exchange_tx_2.identifier

def test_forger_required(transaction_pool):
    currentPath = pathlib.Path().resolve()

    genesis_private_key_path = f"{currentPath}/beez/keys/genesisPrivateKey.pem"
    alice_private_key_path = f"{currentPath}/beez/keys/alicePrivateKey.pem"

    genesis_wallet = Wallet()
    genesis_wallet.from_key(genesis_private_key_path)
    alice_wallet = Wallet()
    alice_wallet.from_key(alice_private_key_path)
    exchange_tx = genesis_wallet.create_transaction(
        alice_wallet.public_key_string(), 5, TransactionType.EXCHANGE.name
    )
    exchange_tx_2 = genesis_wallet.create_transaction(
        alice_wallet.public_key_string(), 10, TransactionType.EXCHANGE.name
    )
    exchange_tx_3 = genesis_wallet.create_transaction(
        alice_wallet.public_key_string(), 10, TransactionType.EXCHANGE.name
    )
    assert transaction_pool.forger_required() == False
    transaction_pool.add_transaction(exchange_tx)
    assert transaction_pool.forger_required() == False
    transaction_pool.add_transaction(exchange_tx_2)
    assert transaction_pool.forger_required() == False
    transaction_pool.add_transaction(exchange_tx_3)
    assert transaction_pool.forger_required() == True