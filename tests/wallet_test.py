from loguru import logger

from beez.wallet.wallet import Wallet

def test_wallet():
    wallet = Wallet()

    assert 5 == 5