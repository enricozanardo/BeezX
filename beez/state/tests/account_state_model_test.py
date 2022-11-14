# pylint: skip-file
import pytest
import shutil
from beez.state.account_state_model import AccountStateModel
from beez.beez_utils import BeezUtils

def clear_indices():
    shutil.rmtree("account_indices", ignore_errors=True)
    shutil.rmtree("balance_indices", ignore_errors=True)
    shutil.rmtree("blocks_indices", ignore_errors=True)
    shutil.rmtree("challenge_indices", ignore_errors=True)
    shutil.rmtree("pos_indices", ignore_errors=True)


@pytest.fixture
def account_state_model():
    yield AccountStateModel()
    clear_indices()

def test_account_state_model_creation(account_state_model):
    assert account_state_model is not None
    assert account_state_model.balances() == {}

def test_serialize(account_state_model):
    account_state_model.update_balance("test_public_key", 120)
    assert account_state_model.serialize() == {"accounts": ["test_public_key"], "balances": {"test_public_key": 120}}

def test_deserialize():
    serialized_account_state_model = {"test_public_key": 110}
    local_account_state_model = AccountStateModel.deserialize(serialized_account_state_model)
    assert local_account_state_model is not None
    assert local_account_state_model.get_balance("test_public_key") == 110
    assert len(local_account_state_model.accounts()) == 1
    clear_indices()

def test_balances(account_state_model):
    account_state_model.update_balance("another_test", 20)
    assert account_state_model.balances() == {"another_test": 20}

def test_accounts(account_state_model):
    account_state_model.update_balance("another_test", 20)
    assert account_state_model.accounts() == ["another_test"]

def test_add_account(account_state_model):
    account_state_model.add_account("public_key")
    assert len(account_state_model.accounts()) == 1
    assert account_state_model.get_balance("public_key") == 0

def test_get_balance(account_state_model):
    account_state_model.add_account("public_key")
    assert len(account_state_model.accounts()) == 1
    assert account_state_model.get_balance("public_key") == 0

def test_update_balance(account_state_model):
    account_state_model.update_balance("public_key", 23)
    assert len(account_state_model.accounts()) == 1
    assert account_state_model.get_balance("public_key") == 23