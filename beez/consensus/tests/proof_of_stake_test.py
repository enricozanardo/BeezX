# pylint: skip-file
import pytest
import shutil
import pathlib
from beez.consensus.proof_of_stake import ProofOfStake
from beez.consensus.lot import Lot
from beez.wallet.wallet import Wallet
from beez.block.blockchain import Blockchain
from beez.keys.genesis_public_key import GenesisPublicKey
from beez.beez_utils import BeezUtils

def clear_indices():
    shutil.rmtree("account_indices", ignore_errors=True)
    shutil.rmtree("balance_indices", ignore_errors=True)
    shutil.rmtree("blocks_indices", ignore_errors=True)
    shutil.rmtree("challenge_indices", ignore_errors=True)
    shutil.rmtree("pos_indices", ignore_errors=True)

@pytest.fixture
def pos():
    yield ProofOfStake()
    clear_indices()

def test_pos_creation(pos):
    assert pos is not None
    assert pos.get(GenesisPublicKey().pub_key) == 1

def test_serialize(pos):
    assert pos.serialize() == {
        GenesisPublicKey().pub_key: 1
    }

def test_deserialize():
    local_pos = ProofOfStake.deserialize({
        GenesisPublicKey().pub_key: 25
    })
    assert local_pos is not None
    assert local_pos.get(GenesisPublicKey().pub_key) == 25

def test_set_genesis_node_stake():
    shutil.rmtree("pos_indices", ignore_errors=True)
    local_pos = ProofOfStake()
    assert local_pos.get(GenesisPublicKey().pub_key) == 1

def test_stakers(pos):
    assert len(pos.stakers()) == 1
    assert pos.stakers()[0] == GenesisPublicKey().pub_key

def test_update(pos):
    currentPath = pathlib.Path().resolve()
    alice_private_key_path = f"{currentPath}/beez/keys/alicePrivateKey.pem"
    alice_wallet = Wallet()
    alice_wallet.from_key(alice_private_key_path)

    pos.update(alice_wallet.public_key_string(), 25)

    assert pos.get(alice_wallet.public_key_string()) == 25
    assert len(pos.stakers()) == 2

def test_get(pos):
    assert pos.get(GenesisPublicKey().pub_key) == 1

def test_validator_lot(pos):
    assert len(pos.validator_lots("seed")) == 1
    assert pos.validator_lots("seed")[0].public_key_string == GenesisPublicKey().pub_key

def test_winner_lot(pos):
    currentPath = pathlib.Path().resolve()
    genesis_private_key_path = f"{currentPath}/beez/keys/genesisPrivateKey.pem"
    genesis_wallet = Wallet()
    genesis_wallet.from_key(genesis_private_key_path)
    blockchain = Blockchain()
    lot = Lot(genesis_wallet.public_key_string(), 3, BeezUtils.hash(blockchain.blocks()[-1].payload()).hexdigest())
    assert pos.winner_lot([lot], "seed_string") == lot

def test_forger(pos):
    blockchain = Blockchain()
    last_block_hash = BeezUtils.hash(blockchain.blocks()[-1].payload()).hexdigest()
    assert pos.forger(last_block_hash) == GenesisPublicKey().pub_key