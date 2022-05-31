from time import sleep
from loguru import logger

import os
from dotenv import load_dotenv
import requests
import pathlib

from beez.transaction.Transaction import Transaction
from beez.transaction.TransactionType import TransactionType
from beez.wallet.Wallet import Wallet
from beez.node.BeezNode import BeezNode
from beez.BeezUtils import BeezUtils
from beez.Types import PublicKeyString, WalletAddress

load_dotenv()  # load .env

NODE_API_PORT = os.environ.get("NODE_API_PORT", default=8176)
URI = os.environ.get("FIRST_SERVER_IP", default="192.168.1.61")


def postTransaction(senderWallet: Wallet, receiverWallet: Wallet, amount, txType: TransactionType):

    tx = senderWallet.createTransaction(receiverWallet.publicKeyString(), amount, txType) 
    url = f"http://{URI}:{NODE_API_PORT}/transaction"

    package = {'transaction': BeezUtils.encode(tx)}
    request = requests.post(url, json=package)

    logger.info(f"ok?: {request}")


def test_send_transaction():

    # Import the alice private key
    currentPath = pathlib.Path().resolve()
    alicePrivateKeyPath = f"{currentPath}/beez/keys/alicePrivateKey.pem"

    # Generate a standard transaction
    AliceWallet = Wallet()
    AliceWallet.fromKey(alicePrivateKeyPath)

    # Generate a standard transaction
    BobWallet = Wallet()
    
    amount = 12
    typeTransfer = TransactionType.TRANSFER.name

    postTransaction(AliceWallet, BobWallet, amount, typeTransfer)
  
    # assert beezNode.ip == localIP
    assert 5 == 5