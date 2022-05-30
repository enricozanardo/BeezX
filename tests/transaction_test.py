from time import sleep
from loguru import logger

import os
from dotenv import load_dotenv
import requests

from beez.transaction.Transaction import Transaction
from beez.transaction.TransactionType import TransactionType
from beez.wallet.Wallet import Wallet
from beez.node.BeezNode import BeezNode
from beez.BeezUtils import BeezUtils
from beez.Types import PublicKeyString, WalletAddress

load_dotenv()  # load .env

NODE_API_PORT = os.environ.get("NODE_API_PORT", default=8176)
URI = os.environ.get("FIRST_SERVER_IP", default="192.168.1.61")


# def test_transaction():
#     AliceWallet = Wallet()
#     BobWallet = Wallet()

#     senderWalletAddress = AliceWallet.address
#     receiverWalletAddress = BobWallet.address
#     amount = 10
#     type = TransactionType.TRANSFER
      
#     tx = Transaction(senderWalletAddress, receiverWalletAddress, amount, type)

#     assert tx.type == TransactionType.TRANSFER


def postTransaction(senderWallet: Wallet, receiverWallet: Wallet, amount, txType: TransactionType):

    tx = senderWallet.createTransaction(receiverWallet.publicKeyString(), amount, txType) 
    url = f"http://{URI}:{NODE_API_PORT}/transaction"

    package = {'transaction': BeezUtils.encode(tx)}
    request = requests.post(url, json=package)

    logger.info(f"ok?: {request}")


def test_send_transaction():

    # Generate a standard transaction
    AliceWallet = Wallet()
    BobWallet = Wallet()

    senderWalletAddress = AliceWallet.address
    receiverWalletAddress = BobWallet.address
    amount = 10
    type = TransactionType.TRANSFER

    postTransaction(AliceWallet, BobWallet, amount, type)

    # assert beezNode.ip == localIP
    assert 5 == 5