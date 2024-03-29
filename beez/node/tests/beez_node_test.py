# pylint: skip-file
import pytest
import pathlib
import shutil
import time
from beez.node.beez_node import BeezNode
from beez.beez_utils import BeezUtils
from beez.wallet.wallet import Wallet
from beez.block.block import Block
from beez.block.blockchain import Blockchain
from beez.transaction.challenge_tx import ChallengeTX
from beez.socket.messages.message_type import MessageType
from beez.challenge.challenge import Challenge
from typing import cast
from beez.types import PublicKeyString
from beez.transaction.transaction_type import TransactionType
from beez.socket.socket_communication.base_socket_communication import BaseSocketCommunication

def clear_indices():
    shutil.rmtree("account_indices", ignore_errors=True)
    shutil.rmtree("balance_indices", ignore_errors=True)
    shutil.rmtree("blocks_indices", ignore_errors=True)
    shutil.rmtree("challenge_indices", ignore_errors=True)
    shutil.rmtree("pos_indices", ignore_errors=True)
    shutil.rmtree("txp_indices", ignore_errors=True)
    shutil.rmtree("address_indices", ignore_errors=True)

def shared_func(a: int, b: int):
    return a+b

@pytest.fixture
def node():
    yield BeezNode()
    clear_indices()

def test_communication_protocol():
    node = BeezNode(port=3997)
    assert isinstance(node.p2p, BaseSocketCommunication)

def test_handle_transaction():
    clear_indices()
    node = BeezNode(port=4000)
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

    # set nodes wallet to be the genesis wallet in order to be able
    # to create new blocks
    node.wallet = genesis_wallet

    exchange_tx = genesis_wallet.create_transaction(
        BeezUtils.address_from_public_key(alice_wallet.public_key_string()), 100, TransactionType.EXCHANGE.name
    )
    exchange_tx_2 = genesis_wallet.create_transaction(
        BeezUtils.address_from_public_key(alice_wallet.public_key_string()), 200, TransactionType.EXCHANGE.name
    )
    exchange_tx_3 = genesis_wallet.create_transaction(
        BeezUtils.address_from_public_key(alice_wallet.public_key_string()), 300, TransactionType.EXCHANGE.name
    )
    transfer_tx = alice_wallet.create_transaction(
        BeezUtils.address_from_public_key(bob_wallet.public_key_string()), 50, TransactionType.TRANSFER.name
    )
    uncovered_tx = alice_wallet.create_transaction(
        BeezUtils.address_from_public_key(bob_wallet.public_key_string()), 5000, TransactionType.TRANSFER.name
    )
    node.handle_address_registration(alice_wallet.public_key_string())
    node.handle_address_registration(genesis_wallet.public_key_string())
    node.handle_address_registration(bob_wallet.public_key_string())
    node.handle_transaction(exchange_tx)
    node.handle_transaction(exchange_tx_2)
    node.handle_transaction(exchange_tx_3)
    node.handle_transaction(transfer_tx)

    node.handle_transaction(uncovered_tx)
    assert len(node.transaction_pool.transactions()) == 0
    assert len(node.blockchain.blocks()) == 5
    assert len(node.blockchain.blocks()[1].transactions) == 1

    clear_indices()

def test_handle_block():
    node = BeezNode(port=4001)
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

    # set nodes wallet to be the genesis wallet in order to be able
    # to create new blocks
    node.wallet = genesis_wallet

    exchange_tx = genesis_wallet.create_transaction(
        BeezUtils.address_from_public_key(alice_wallet.public_key_string()), 100, TransactionType.EXCHANGE.name
    )
    exchange_tx_2 = genesis_wallet.create_transaction(
        BeezUtils.address_from_public_key(alice_wallet.public_key_string()), 200, TransactionType.EXCHANGE.name
    )
    exchange_tx_3 = genesis_wallet.create_transaction(
        BeezUtils.address_from_public_key(alice_wallet.public_key_string()), 300, TransactionType.EXCHANGE.name
    )
    transfer_tx = alice_wallet.create_transaction(
        BeezUtils.address_from_public_key(alice_wallet.public_key_string()), 50, TransactionType.TRANSFER.name
    )

    node.handle_address_registration(alice_wallet.public_key_string())
    node.handle_address_registration(genesis_wallet.public_key_string())
    node.handle_address_registration(bob_wallet.public_key_string())
    node.handle_transaction(exchange_tx)
    node.handle_transaction(exchange_tx_2)
    node.handle_transaction(exchange_tx_3)

    block = genesis_wallet.create_block(None, [transfer_tx], BeezUtils.hash(node.blockchain.blocks()[-1].payload()).hexdigest(), 4)
    invalid_block = genesis_wallet.create_block(None, [transfer_tx], BeezUtils.hash(node.blockchain.blocks()[-1].payload()).hexdigest(), 4)
    node.handle_block(block)
    node.handle_block(invalid_block)
    assert len(node.blockchain.blocks()) == 5
    assert len(node.blockchain.blocks()[-1].transactions) == 1
    assert node.blockchain.blocks()[-1].transactions[0].identifier == transfer_tx.identifier
    clear_indices()

def test_handle_challenge_tx():
    node = BeezNode(port=4002)
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

    # set nodes wallet to be the genesis wallet in order to be able
    # to create new blocks
    node.wallet = genesis_wallet

    exchange_tx = genesis_wallet.create_transaction(
        BeezUtils.address_from_public_key(alice_wallet.public_key_string()), 100, TransactionType.EXCHANGE.name
    )
    exchange_tx_2 = genesis_wallet.create_transaction(
        BeezUtils.address_from_public_key(alice_wallet.public_key_string()), 200, TransactionType.EXCHANGE.name
    )
    exchange_tx_3 = genesis_wallet.create_transaction(
        BeezUtils.address_from_public_key(alice_wallet.public_key_string()), 200, TransactionType.EXCHANGE.name
    )
    exchange_tx_4 = genesis_wallet.create_transaction(
        BeezUtils.address_from_public_key(alice_wallet.public_key_string()), 200, TransactionType.EXCHANGE.name
    )
    exchange_tx_5 = genesis_wallet.create_transaction(
        BeezUtils.address_from_public_key(alice_wallet.public_key_string()), 200, TransactionType.EXCHANGE.name
    )
    node.handle_address_registration(alice_wallet.public_key_string())
    node.handle_address_registration(genesis_wallet.public_key_string())
    node.handle_address_registration(bob_wallet.public_key_string())
    node.handle_transaction(exchange_tx)
    node.handle_transaction(exchange_tx_2)
    node.handle_transaction(exchange_tx_3)
    node.handle_transaction(exchange_tx_4)
    node.handle_transaction(exchange_tx_5)

    challenge = Challenge(shared_func, 5)
    challenge_tx = alice_wallet.create_challenge_transaction(10, TransactionType.CHALLENGE.name, challenge)
    node.handle_challenge_tx(challenge_tx)
    
    assert len(node.blockchain.blocks()) == 7
    assert len(node.blockchain.blocks()[-1].transactions) == 1

    last_block_tx_ids = []
    for tx in node.blockchain.blocks()[-1].transactions:
        last_block_tx_ids.append(tx.identifier)

    assert challenge_tx.identifier in last_block_tx_ids
    assert exchange_tx_5.identifier not in last_block_tx_ids
    assert exchange_tx_4.identifier not in last_block_tx_ids

    clear_indices()

def test_forge():
    node = BeezNode(port=4003)
    currentPath = pathlib.Path().resolve()

    genesis_private_key_path = f"{currentPath}/beez/keys/genesisPrivateKey.pem"
    alice_private_key_path = f"{currentPath}/beez/keys/alicePrivateKey.pem"

    genesis_wallet = Wallet()
    genesis_wallet.from_key(genesis_private_key_path)
    alice_wallet = Wallet()
    alice_wallet.from_key(alice_private_key_path)

    # set nodes wallet to be the genesis wallet in order to be able
    # to create new blocks
    node.wallet = genesis_wallet

    exchange_tx = genesis_wallet.create_transaction(
        BeezUtils.address_from_public_key(alice_wallet.public_key_string()), 100, TransactionType.EXCHANGE.name
    )
    exchange_tx_2 = genesis_wallet.create_transaction(
        BeezUtils.address_from_public_key(alice_wallet.public_key_string()), 200, TransactionType.EXCHANGE.name
    )
    node.handle_address_registration(alice_wallet.public_key_string())
    node.handle_address_registration(genesis_wallet.public_key_string())
    node.handle_transaction(exchange_tx)
    node.handle_transaction(exchange_tx_2)

    node.forge()

    assert len(node.blockchain.blocks()) == 4
    assert len(node.transaction_pool.transactions()) == 0
    clear_indices()

def test_handle_blockchain():
    node = BeezNode(port=4004)
    currentPath = pathlib.Path().resolve()

    genesis_private_key_path = f"{currentPath}/beez/keys/genesisPrivateKey.pem"
    alice_private_key_path = f"{currentPath}/beez/keys/alicePrivateKey.pem"

    genesis_wallet = Wallet()
    genesis_wallet.from_key(genesis_private_key_path)
    alice_wallet = Wallet()
    alice_wallet.from_key(alice_private_key_path)

    # set nodes wallet to be the genesis wallet in order to be able
    # to create new blocks
    node.wallet = genesis_wallet

    exchange_tx = genesis_wallet.create_transaction(
        BeezUtils.address_from_public_key(alice_wallet.public_key_string()), 100, TransactionType.EXCHANGE.name
    )
    node.handle_address_registration(genesis_wallet.public_key_string())
    node.handle_address_registration(alice_wallet.public_key_string())
    node.handle_transaction(exchange_tx)

    local_blockchain = Blockchain()
    local_blockchain.in_memory_blocks = local_blockchain.blocks_from_index()
    block = Block(
        None,
        [exchange_tx],
        BeezUtils.hash(local_blockchain.blocks()[-1].payload()).hexdigest(),
        BeezUtils.address_from_public_key(genesis_wallet.public_key_string()),
        1,
    )
    local_blockchain.add_block(block)
    

    # should be added to the node's blockchain
    node.pending_blockchain_request = True
    node.handle_blockchain(local_blockchain)
    # should not be added, already exists
    node.pending_blockchain_request = True
    node.handle_blockchain(local_blockchain)

    assert len(node.blockchain.blocks()) == 2
    clear_indices()

# def test_handle_address_registration():
#     node = BeezNode(port=4005)

#     assert node.get_public_key_from_address("bzx302a300506032b657003210033d68a25a5118b21d6ae5bdd5ac438fadcb0b27a5683695ae0e84d6d23cf4913") is None
    
#     node.handle_address_registration(
#         public_key_hex="302a300506032b657003210033d68a25a5118b21d6ae5bdd5ac438fadcb0b27a5683695ae0e84d6d23cf4913",
#     )
#     assert node.get_public_key_from_address(BeezUtils.address_from_public_key("302a300506032b657003210033d68a25a5118b21d6ae5bdd5ac438fadcb0b27a5683695ae0e84d6d23cf4913")) == "302a300506032b657003210033d68a25a5118b21d6ae5bdd5ac438fadcb0b27a5683695ae0e84d6d23cf4913"
#     clear_indices()

# def test_get_registered_addresses():
#     clear_indices()
#     node = BeezNode(port=4006)
#     assert node.get_registered_addresses() == []
#     node.handle_address_registration(
#         public_key_hex="302a300506032b657003210033d68a25a5118b21d6ae5bdd5ac438fadcb0b27a5683695ae0e84d6d23cf4913",
#     )
#     assert len(node.get_registered_addresses()) == 1
#     registration = node.get_registered_addresses()[0]
#     assert registration["id"] == "302a300506032b657003210033d68a25a5118b21d6ae5bdd5ac438fadcb0b27a5683695ae0e84d6d23cf4913"
#     assert registration["public_key_hex"] == "302a300506032b657003210033d68a25a5118b21d6ae5bdd5ac438fadcb0b27a5683695ae0e84d6d23cf4913"
#     assert registration["address"] == BeezUtils.address_from_public_key("302a300506032b657003210033d68a25a5118b21d6ae5bdd5ac438fadcb0b27a5683695ae0e84d6d23cf4913")
#     clear_indices()