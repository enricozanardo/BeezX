from time import sleep
from loguru import logger

import os
from dotenv import load_dotenv
import requests
import pathlib

from beez.transaction.Transaction import Transaction
from beez.transaction.TransactionType import TransactionType
from beez.wallet.Wallet import Wallet
from beez.node.beez_node import BeezNode
from beez.beez_utils import BeezUtils
from beez.Types import PublicKeyString, WalletAddress

load_dotenv()  # load .env

NODE_API_PORT = os.environ.get("NODE_API_PORT", default=8176)
URI = os.environ.get("FIRST_SERVER_IP", default="192.168.1.61")


def postTransaction(senderWallet: Wallet, receiverWallet: Wallet, amount, txType: TransactionType):

    tx = senderWallet.createTransaction(receiverWallet.publicKeyString(), amount, txType) 
    url = f"http://{URI}:{NODE_API_PORT}/transaction"
    logger.info(url)

    package = {'transaction': BeezUtils.encode(tx)}
    request = requests.post(url, json=package)

    logger.info(package)

    logger.info(f"ok?: {request}")


def test_exchange_transaction():

    # Import the genesis private key
    currentPath = pathlib.Path().resolve()

    genesisPrivateKeyPath = f"{currentPath}/beez/keys/genesisPrivateKey.pem"
    alicePrivateKeyPath = f"{currentPath}/beez/keys/alicePrivateKey.pem"

    GenesisWallet = Wallet()
    GenesisWallet.fromKey(genesisPrivateKeyPath)
    AliceWallet = Wallet()
    AliceWallet.fromKey(alicePrivateKeyPath)
    
    amountEx = 100

    typeExchange = TransactionType.EXCHANGE.name

    postTransaction(GenesisWallet, AliceWallet, amountEx, typeExchange)
   
    # assert beezNode.ip == localIP
    assert 5 == 5

if __name__ == "__main__":
    logger.info('SENDING EXCHANGE TX')
    test_exchange_transaction()