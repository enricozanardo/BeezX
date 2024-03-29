from loguru import logger


import os
from dotenv import load_dotenv
import requests
import pathlib

from beez.transaction.transaction import Transaction
from beez.transaction.transaction_type import TransactionType
from beez.wallet.wallet import Wallet
from beez.beez_utils import BeezUtils
from beez.types import WalletAddress
from beez.challenge.challenge import Challenge
from beez.transaction.challenge_tx import ChallengeTX

# for function
import random

load_dotenv()  # load .env

NODE_API_PORT = os.environ.get("NODE_API_PORT", default=8176)
URI = os.environ.get("FIRST_SERVER_IP", default="192.168.1.61")


def postChallengeTransaction(senderWallet: Wallet, amount, txType: TransactionType, challenge: Challenge):

    tx = senderWallet.create_challenge_transaction(amount, txType, challenge) 
    url = f"http://{URI}:{NODE_API_PORT}/challenge"

    package = {'challenge': BeezUtils.encode(tx)}
    request = requests.post(url, json=package)

    logger.info(f"ok?: {request}")


def sum(a: int,b: int):
    """
    Returns the sum of two given integers.

    Parameters:
        a (int): The first value
        b (int): The second value

    Returns:
        sum (int): The sum of the two inputs.
    """
    return a + b


def test_send_challenge_transaction():
    # Before to test Alice wallet must have some Tokens into the wallet!
    # Run exchange_transcation_test before!!!

    # Import the alice private key
    currentPath = pathlib.Path().resolve()
    alicePrivateKeyPath = f"{currentPath}/beez/keys/alicePrivateKey.pem"

    # Generate a standard transaction
    AliceWallet = Wallet()
    AliceWallet.from_key(alicePrivateKeyPath)

    reward = 8
    type = TransactionType.CHALLENGE.name

    # Define the challenge
    challenge = Challenge(sum, reward)

    postChallengeTransaction(AliceWallet, reward, type, challenge)

    # assert beezNode.ip == localIP
    assert 5 == 5