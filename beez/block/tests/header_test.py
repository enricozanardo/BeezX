# pylint: skip-file
import pytest
import shutil
from beez.block.block import Header
from beez.challenge.beez_keeper import BeezKeeper
from beez.state.account_state_model import AccountStateModel

def clear_indices():
    shutil.rmtree("account_indices", ignore_errors=True)
    shutil.rmtree("balance_indices", ignore_errors=True)
    shutil.rmtree("blocks_indices", ignore_errors=True)
    shutil.rmtree("challenge_indices", ignore_errors=True)
    shutil.rmtree("pos_indices", ignore_errors=True)

@pytest.fixture
def header():
    beez_keeper = BeezKeeper()
    account_state_model = AccountStateModel()
    yield Header(beez_keeper, account_state_model)
    clear_indices()

def test_header_creation():
    beez_keeper = BeezKeeper()
    account_state_model = AccountStateModel()
    local_header = Header(beez_keeper, account_state_model)
    assert local_header is not None
    assert local_header.beez_keeper == beez_keeper
    assert local_header.account_state_model == account_state_model

def test_serialize(header):
    expected_result = {
        "beezKeeper": {},
        "accountStateModel": {"accounts": [], "balances": {}}
    }
    assert header.serialize() == expected_result

def test_deserialize():
    header = Header.deserialize({}, {"accounts": [], "balances": {}})
    assert header.beez_keeper.challanges() == {}
    assert header.account_state_model.accounts() == []
    assert header.account_state_model.balances() == {}

def test_get_beez_keeper():
    beez_keeper = BeezKeeper()
    account_state_model = AccountStateModel()
    local_header = Header(beez_keeper, account_state_model)
    assert local_header.get_beez_keeper() == beez_keeper

def test_get_account_state_model():
    beez_keeper = BeezKeeper()
    account_state_model = AccountStateModel()
    local_header = Header(beez_keeper, account_state_model)
    assert local_header.get_account_state_model() == account_state_model
    clear_indices()
