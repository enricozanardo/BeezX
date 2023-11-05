from time import sleep

import os
from dotenv import load_dotenv
import requests
import pathlib

from beez.transaction.transaction_type import TransactionType
from beez.wallet.wallet_new import Wallet
from beez.beez_utils import BeezUtils

load_dotenv()  # load .env

NODE_API_PORT = os.environ.get("NODE_API_PORT", default=5445)
URI = os.environ.get("FIRST_SERVER_IP", default="127.0.0.1")


def postTransaction(senderWallet: Wallet, receiverWallet: Wallet, amount, txType: TransactionType, public_key):

    tx = senderWallet.create_transaction(receiverWallet.public_key_string(), amount, txType, public_key)
    url = f"http://{URI}:{NODE_API_PORT}/transaction"

    package = {'transaction': BeezUtils.encode(tx)}
    request = requests.post(url, json=package)

# CREA WALLET
# CHIAMARE FUNZIONE EXCHANGE



def test_send_transaction():

    # Import the alice private key
    currentPath = pathlib.Path().resolve()
    alicePrivateKeyPath = f"{currentPath}/beez/keys/alicePrivateKey.pem"

    # Generate a standard transaction
    AliceWallet = Wallet()
    AliceWallet.from_key(alicePrivateKeyPath)

    # Generate a standard transaction
    BobWallet = Wallet()
    
    amount = 50
    typeTransfer = TransactionType.TRANSFER.name
    # typeTransfer = TransactionType.EXCHANGE.name
    public_key = ""
    postTransaction(AliceWallet, BobWallet, amount, typeTransfer, public_key)
  
    # assert beezNode.ip == localIP
    assert 5 == 5

if __name__ == "__main__":
    currentPath = pathlib.Path().resolve()

    genesis_private_key_path = f"{currentPath}/beez/keys/genesisPrivateKey.pem"
    bob_private_key_path = f"{currentPath}/beez/keys/bobPrivateKey.pem"

    genesis_wallet = Wallet()
    genesis_wallet.from_key(genesis_private_key_path)
    bob_wallet = Wallet()
    bob_wallet.from_key(bob_private_key_path)

    postTransaction(genesis_wallet, bob_wallet, 100, TransactionType.EXCHANGE.name)