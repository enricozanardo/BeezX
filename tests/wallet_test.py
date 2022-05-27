from loguru import logger

from beez.wallet.Wallet import Wallet

def test_wallet():
    wallet = Wallet()

    assert 5 == 5