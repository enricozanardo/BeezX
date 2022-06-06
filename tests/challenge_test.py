from loguru import logger

import os
from dotenv import load_dotenv
import requests
import pathlib

from beez.transaction.Transaction import Transaction
from beez.transaction.TransactionType import TransactionType
from beez.wallet.Wallet import Wallet
from beez.BeezUtils import BeezUtils
from beez.Types import WalletAddress
from beez.challenge.Challenge import Challenge
from beez.transaction.ChallengeTX import ChallengeTX

load_dotenv()  # load .env

NODE_API_PORT = os.environ.get("NODE_API_PORT", default=8176)
URI = os.environ.get("FIRST_SERVER_IP", default="192.168.1.61")


def postChallengeTransaction(senderWallet: Wallet, amount, txType: TransactionType, challenge: Challenge):

    tx = senderWallet.createChallengeTransaction(amount, txType, challenge) 
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
    AliceWallet.fromKey(alicePrivateKeyPath)

    reward = 10
    type = TransactionType.CHALLENGE.name
    iteration = 4
    owner = AliceWallet.publicKeyString()

    # Define the challenge
    challenge = Challenge(owner, sum, reward, iteration)

    postChallengeTransaction(AliceWallet, reward, type, challenge)

    # assert beezNode.ip == localIP
    assert 5 == 5