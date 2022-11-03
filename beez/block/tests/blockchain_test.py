import pathlib
import shutil
import pytest
from beez.block.Blockchain import Blockchain
from beez.block.Block import Block
from beez.wallet.Wallet import Wallet
from beez.transaction.transaction_type import TransactionType
from typing import cast
from beez.Types import PublicKeyString
from beez.beez_utils import BeezUtils

def remove_blockchain():
    shutil.rmtree("account_indices")
    shutil.rmtree("balance_indices")
    shutil.rmtree("blocks_indices")
    shutil.rmtree("challenge_indices")
    shutil.rmtree("pos_indices")
    
@pytest.fixture(scope="function")
def blockchain():
    yield Blockchain()
    remove_blockchain()

def test_blockchain_creation(blockchain):
    assert blockchain is not None

def test_serialize(blockchain):
    assert blockchain.serialize() == {
        "blocks": [{'header': {'beezKeeper': {}, 'accountStateModel': {'accounts': [], 'balances': {}}}, 'transactions': [], 'lastHash': 'Hello Beezkeepers! 🐝', 'forger': 'BeezAuthors: Enrico Zanardo 🤙🏽 & ⭐', 'blockCount': 0, 'timestamp': 0, 'signature': ''}],
        "accountStateModel": {"accounts": [], "balances": {}},
        "pos": {'-----BEGIN PUBLIC KEY-----\nMIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQDUJ+yqg8M03TmNrDw2R2aif/nm\nsm+O2jOnGYbag+iwFJk8fqWjvA3M1axx3vmfcMIYBE+PTy2ih2pjGVB5U0XLME6a\nCwK6GwFsfvGsvn9VJXv77CnzFj4dJVp6OcmQyvD7WA0MU1yMl1IlTW/d9P7AQ9PG\nNUDwi2X/mpSlrGovKwIDAQAB\n-----END PUBLIC KEY-----': 1},
        "beezKeeper": {},
        "genesisPublicKey": "-----BEGIN PUBLIC KEY-----\nMIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQDUJ+yqg8M03TmNrDw2R2aif/nm\nsm+O2jOnGYbag+iwFJk8fqWjvA3M1axx3vmfcMIYBE+PTy2ih2pjGVB5U0XLME6a\nCwK6GwFsfvGsvn9VJXv77CnzFj4dJVp6OcmQyvD7WA0MU1yMl1IlTW/d9P7AQ9PG\nNUDwi2X/mpSlrGovKwIDAQAB\n-----END PUBLIC KEY-----",
    }

def test_deserialize(blockchain):
    deserialized_blockchain = Blockchain.deserialize({
        "blocks": [{'header': {'beezKeeper': {}, 'accountStateModel': {'accounts': [], 'balances': {}}}, 'transactions': [], 'lastHash': 'Hello Beezkeepers! 🐝', 'forger': 'BeezAuthors: Enrico Zanardo 🤙🏽 & ⭐', 'blockCount': 0, 'timestamp': 0, 'signature': ''}],
        "accountStateModel": {"accounts": [], "balances": {}},
        "pos": {'-----BEGIN PUBLIC KEY-----\nMIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQDUJ+yqg8M03TmNrDw2R2aif/nm\nsm+O2jOnGYbag+iwFJk8fqWjvA3M1axx3vmfcMIYBE+PTy2ih2pjGVB5U0XLME6a\nCwK6GwFsfvGsvn9VJXv77CnzFj4dJVp6OcmQyvD7WA0MU1yMl1IlTW/d9P7AQ9PG\nNUDwi2X/mpSlrGovKwIDAQAB\n-----END PUBLIC KEY-----': 1},
        "beezKeeper": {},
        "genesisPublicKey": "-----BEGIN PUBLIC KEY-----\nMIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQDUJ+yqg8M03TmNrDw2R2aif/nm\nsm+O2jOnGYbag+iwFJk8fqWjvA3M1axx3vmfcMIYBE+PTy2ih2pjGVB5U0XLME6a\nCwK6GwFsfvGsvn9VJXv77CnzFj4dJVp6OcmQyvD7WA0MU1yMl1IlTW/d9P7AQ9PG\nNUDwi2X/mpSlrGovKwIDAQAB\n-----END PUBLIC KEY-----",
    })

    assert blockchain.serialize() == deserialized_blockchain.serialize()

def test_blocks(blockchain):
    blocks = blockchain.blocks()
    assert len(blocks) == 1
    assert blocks[0].header.beez_keeper.serialize() == {}
    assert blocks[0].header.account_state_model.serialize() == {
        "accounts": [],
        "balances": {}
    }
    assert blocks[0].transactions == []
    assert blocks[0].last_hash == 'Hello Beezkeepers! 🐝'
    assert blocks[0].forger == "BeezAuthors: Enrico Zanardo 🤙🏽 & ⭐"
    assert blocks[0].block_count == 0
    assert blocks[0].timestamp == 0
    assert blocks[0].signature == ""

def test_to_json(blockchain):
    json_blockchain = blockchain.to_json()
    json_blocks = json_blockchain['blocks']
    assert len(json_blocks) == 1
    assert json_blocks[0]["transactions"] == []
    assert json_blocks[0]["lastHash"] == 'Hello Beezkeepers! 🐝'
    assert json_blocks[0]["forger"] == "BeezAuthors: Enrico Zanardo 🤙🏽 & ⭐"
    assert json_blocks[0]["blockCount"] == 0
    assert json_blocks[0]["timestamp"] == 0
    assert json_blocks[0]["signature"] == ""

def test_append_genesis():
    blockchain = Blockchain()
    assert len(blockchain.blocks()) == 1

def test_add_block(blockchain):
    """ will not be added and last_hash invalid."""
    new_block = Block(
        None,
        [],
        "should be false",
        cast(PublicKeyString, "Another public key string"),
        1,
    )
    new_block.timestamp = (1)
    blockchain.add_block(new_block)

    assert len(blockchain.blocks()) == 1

    new_block = Block(
        None,
        [],
        BeezUtils.hash(blockchain.blocks()[-1].payload()).hexdigest(),
        cast(PublicKeyString, "Another fake public key string"),
        1,
    )
    new_block.timestamp = (1)
    blockchain.add_block(new_block)

    assert len(blockchain.blocks()) == 2

def test_execute_transactions(blockchain):
    currentPath = pathlib.Path().resolve()

    genesis_private_key_path = f"{currentPath}/beez/keys/genesisPrivateKey.pem"
    alice_private_key_path = f"{currentPath}/beez/keys/alicePrivateKey.pem"
    bob_private_key_path = f"{currentPath}/beez/keys/bobPrivateKey.pem"

    genesis_wallet = Wallet()
    genesis_wallet.from_key(genesis_private_key_path)
    alice_wallet = Wallet()
    alice_wallet.from_key(alice_private_key_path)
    bob_wallet = Wallet()
    bob_wallet.from_key(bob_private_key_path)

    exchange_tx = genesis_wallet.create_transaction(alice_wallet.public_key_string(), 100, TransactionType.EXCHANGE)
    transfer_tx = alice_wallet.create_transaction(bob_wallet.public_key_string(), 50, TransactionType.TRANSFER)

    blockchain.execute_transactions([exchange_tx, transfer_tx])
    assert blockchain.account_state_model.get_balance(alice_wallet.public_key_string()) == 50
    assert blockchain.account_state_model.get_balance(bob_wallet.public_key_string()) == 50

def test_transaction_exists(blockchain):
    currentPath = pathlib.Path().resolve()

    genesis_private_key_path = f"{currentPath}/beez/keys/genesisPrivateKey.pem"
    alice_private_key_path = f"{currentPath}/beez/keys/alicePrivateKey.pem"

    genesis_wallet = Wallet()
    genesis_wallet.from_key(genesis_private_key_path)
    alice_wallet = Wallet()
    alice_wallet.from_key(alice_private_key_path)

    exchange_tx = genesis_wallet.create_transaction(alice_wallet.public_key_string(), 100, TransactionType.EXCHANGE.name)
    new_exchange_tx = genesis_wallet.create_transaction(alice_wallet.public_key_string(), 200, TransactionType.EXCHANGE.name)

    new_block = Block(
        None,
        [exchange_tx],
        BeezUtils.hash(blockchain.blocks()[-1].payload()).hexdigest(),
        cast(PublicKeyString, "Another fake public key string"),
        2,
    )
    new_block.timestamp = (1)
    blockchain.add_block(new_block)

    # assert len(blockchain.blocks()) == 2
    assert blockchain.transaction_exist(exchange_tx) == True
    assert blockchain.transaction_exist(new_exchange_tx) == False

def test_next_forger(blockchain):
    currentPath = pathlib.Path().resolve()
    genesis_private_key_path = f"{currentPath}/beez/keys/genesisPrivateKey.pem"

    genesis_wallet = Wallet()
    genesis_wallet.from_key(genesis_private_key_path)

    assert blockchain.next_forger() == genesis_wallet.public_key_string()

def test_mint_block(blockchain):
    currentPath = pathlib.Path().resolve()
    genesis_private_key_path = f"{currentPath}/beez/keys/genesisPrivateKey.pem"
    alice_private_key_path = f"{currentPath}/beez/keys/alicePrivateKey.pem"

    genesis_wallet = Wallet()
    genesis_wallet.from_key(genesis_private_key_path)
    alice_wallet = Wallet()
    alice_wallet.from_key(alice_private_key_path)

    exchange_tx = genesis_wallet.create_transaction(alice_wallet.public_key_string(), 100, TransactionType.EXCHANGE.name)
    new_exchange_tx = genesis_wallet.create_transaction(alice_wallet.public_key_string(), 200, TransactionType.EXCHANGE.name)

    new_block = blockchain.mint_block([exchange_tx, new_exchange_tx], genesis_wallet)

    assert new_block.transactions == [exchange_tx, new_exchange_tx]
    assert new_block.forger == genesis_wallet.public_key_string()
    assert new_block.block_count == 1

def test_get_covered_transactionset(blockchain):
    currentPath = pathlib.Path().resolve()

    genesis_private_key_path = f"{currentPath}/beez/keys/genesisPrivateKey.pem"
    alice_private_key_path = f"{currentPath}/beez/keys/alicePrivateKey.pem"
    bob_private_key_path = f"{currentPath}/beez/keys/bobPrivateKey.pem"

    genesis_wallet = Wallet()
    genesis_wallet.from_key(genesis_private_key_path)
    alice_wallet = Wallet()
    alice_wallet.from_key(alice_private_key_path)
    bob_wallet = Wallet()
    bob_wallet.from_key(bob_private_key_path)

    exchange_tx = genesis_wallet.create_transaction(alice_wallet.public_key_string(), 100, TransactionType.EXCHANGE.name)
    exchange_tx_2 = genesis_wallet.create_transaction(alice_wallet.public_key_string(), 100, TransactionType.EXCHANGE.name)
    transfer_tx = alice_wallet.create_transaction(bob_wallet.public_key_string(), 50, TransactionType.TRANSFER.name)

    covered_tx = blockchain.get_covered_transactionset([exchange_tx, exchange_tx_2, transfer_tx])

    assert len(covered_tx) == 2
    assert covered_tx[0] == exchange_tx
    assert covered_tx[1] == exchange_tx_2

def test_transaction_covered(blockchain):
    currentPath = pathlib.Path().resolve()

    genesis_private_key_path = f"{currentPath}/beez/keys/genesisPrivateKey.pem"
    alice_private_key_path = f"{currentPath}/beez/keys/alicePrivateKey.pem"
    bob_private_key_path = f"{currentPath}/beez/keys/bobPrivateKey.pem"

    genesis_wallet = Wallet()
    genesis_wallet.from_key(genesis_private_key_path)
    alice_wallet = Wallet()
    alice_wallet.from_key(alice_private_key_path)
    bob_wallet = Wallet()
    bob_wallet.from_key(bob_private_key_path)

    exchange_tx = genesis_wallet.create_transaction(alice_wallet.public_key_string(), 100, TransactionType.EXCHANGE.name)
    exchange_tx_2 = genesis_wallet.create_transaction(alice_wallet.public_key_string(), 100, TransactionType.EXCHANGE.name)
    transfer_tx = alice_wallet.create_transaction(bob_wallet.public_key_string(), 50, TransactionType.TRANSFER.name)

    assert blockchain.transaction_covered(exchange_tx) == True
    assert blockchain.transaction_covered(exchange_tx_2) == True
    assert blockchain.transaction_covered(transfer_tx) == False

def test_blockcount_valid(blockchain):
    invalid_block = Block(
        None,
        [],
        BeezUtils.hash(blockchain.blocks()[-1].payload()).hexdigest(),
        cast(PublicKeyString, "Another fake public key string"),
        2,
    )
    invalid_block.timestamp = (1)

    valid_block = Block(
        None,
        [],
        BeezUtils.hash(blockchain.blocks()[-1].payload()).hexdigest(),
        cast(PublicKeyString, "Another fake public key string"),
        1,
    )
    valid_block.timestamp = (1)

    assert blockchain.blockcount_valid(invalid_block) == False
    assert blockchain.blockcount_valid(valid_block) == True

def test_last_blockhash_valid(blockchain):
    invalid_block = Block(
        None,
        [],
        "invalid_hash",
        cast(PublicKeyString, "Another fake public key string"),
        2,
    )
    invalid_block.timestamp = (1)

    valid_block = Block(
        None,
        [],
        BeezUtils.hash(blockchain.blocks()[-1].payload()).hexdigest(),
        cast(PublicKeyString, "Another fake public key string"),
        1,
    )
    valid_block.timestamp = (1)

    assert blockchain.last_blockhash_valid(invalid_block) == False
    assert blockchain.last_blockhash_valid(valid_block) == True

def test_forger_valid(blockchain):
    invalid_block = Block(
        None,
        [],
        "invalid_hash",
        cast(PublicKeyString, "Another fake public key string"),
        2,
    )
    invalid_block.timestamp = (1)

    assert blockchain.forger_valid(invalid_block) == False

    currentPath = pathlib.Path().resolve()

    genesis_private_key_path = f"{currentPath}/beez/keys/genesisPrivateKey.pem"
    genesis_wallet = Wallet()
    genesis_wallet.from_key(genesis_private_key_path)

    valid_block = Block(
        None,
        [],
        "invalid_hash",
        genesis_wallet.public_key_string(),
        2,
    )
    valid_block.timestamp = (1)

    assert blockchain.forger_valid(valid_block) == True

def test_transaction_valid(blockchain):
    currentPath = pathlib.Path().resolve()

    genesis_private_key_path = f"{currentPath}/beez/keys/genesisPrivateKey.pem"
    alice_private_key_path = f"{currentPath}/beez/keys/alicePrivateKey.pem"
    bob_private_key_path = f"{currentPath}/beez/keys/bobPrivateKey.pem"

    genesis_wallet = Wallet()
    genesis_wallet.from_key(genesis_private_key_path)
    alice_wallet = Wallet()
    alice_wallet.from_key(alice_private_key_path)
    bob_wallet = Wallet()
    bob_wallet.from_key(bob_private_key_path)

    exchange_tx = genesis_wallet.create_transaction(alice_wallet.public_key_string(), 100, TransactionType.EXCHANGE.name)
    exchange_tx_2 = genesis_wallet.create_transaction(alice_wallet.public_key_string(), 100, TransactionType.EXCHANGE.name)
    transfer_tx = alice_wallet.create_transaction(bob_wallet.public_key_string(), 50, TransactionType.TRANSFER.name)

    assert blockchain.transaction_valid([exchange_tx,exchange_tx_2,transfer_tx]) == False
    assert blockchain.transaction_valid([exchange_tx,exchange_tx_2]) == True
    
