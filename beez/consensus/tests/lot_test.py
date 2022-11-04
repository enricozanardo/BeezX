# pylint: skip-file
import pytest
import shutil
import pathlib
from beez.consensus.lot import Lot
from beez.wallet.wallet import Wallet
from beez.block.blockchain import Blockchain
from beez.beez_utils import BeezUtils

def clear_indices():
    shutil.rmtree("account_indices", ignore_errors=True)
    shutil.rmtree("balance_indices", ignore_errors=True)
    shutil.rmtree("blocks_indices", ignore_errors=True)
    shutil.rmtree("challenge_indices", ignore_errors=True)
    shutil.rmtree("pos_indices", ignore_errors=True)

def get_genesis_wallet():
    currentPath = pathlib.Path().resolve()
    genesis_private_key_path = f"{currentPath}/beez/keys/genesisPrivateKey.pem"
    genesis_wallet = Wallet()
    genesis_wallet.from_key(genesis_private_key_path)
    return genesis_wallet

def create_lot(blockchain):
    genesis_wallet = get_genesis_wallet()
    return Lot(genesis_wallet.public_key_string(), 3, BeezUtils.hash(blockchain.blocks()[-1].payload()).hexdigest())
    
def test_lot_creation():
    blockchain = Blockchain()
    lot = create_lot(blockchain)
    assert lot is not None
    assert lot.public_key_string == get_genesis_wallet().public_key_string()
    assert lot.iteration == 3
    assert lot.last_block_hash == BeezUtils.hash(blockchain.blocks()[-1].payload()).hexdigest()
    clear_indices()

def test_lottery_hash():
    blockchain = Blockchain()
    lot = create_lot(blockchain)
    assert lot.lottery_hash() != ""
    clear_indices()