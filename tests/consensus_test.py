from loguru import logger
import string
import random
import pathlib

from beez.consensus.ProofOfStake import ProofOfStake
from beez.consensus.Lot import Lot
from beez.wallet.Wallet import Wallet

currentPath = pathlib.Path().resolve()
alicePrivateKeyPath = f"{currentPath}/beez/keys/alicePrivateKey.pem"

def test_consensus():
    logger.info(f"Test Proof of Stake Algorithm")
    # Import the alice private key
   

    # Generate a standard transaction
    AliceWallet = Wallet()
    AliceWallet.fromKey(alicePrivateKeyPath)

    # Generate a standard Wallet
    BobWallet = Wallet()

    pos = ProofOfStake()

    # Generate a standard transaction
    BobWallet = Wallet()
    JackWallet = Wallet()


    pos.update(BobWallet.publicKeyString(), 10)
    pos.update(AliceWallet.publicKeyString(), 100)

    bob_stakes = pos.get(BobWallet.publicKeyString())
    alice_stakes = pos.get(AliceWallet.publicKeyString())
    jack_stakes = pos.get(JackWallet.publicKeyString())


    logger.info(f"stakes: {pos.stakers}")
    logger.info(f"bob stakes: {bob_stakes}")
    logger.info(f"alice stakes: {alice_stakes}")
    logger.info(f"jack stakes: {jack_stakes}")

    assert bob_stakes == 10, "Bob must have 10 Stakes"
    assert alice_stakes == 100, "Alice must have 100 Stakes"
    assert jack_stakes == None, "Jack account must be None"


def test_lottery():
    logger.info(f"Test Lottery")

    AliceWallet = Wallet()
    AliceWallet.fromKey(alicePrivateKeyPath)

    lot = Lot(AliceWallet.publicKeyString(), 10, 'lastBlockHash')

    lotHash = lot.lotteryHash()

    logger.info(f"lot result: {lotHash}")

    assert lotHash == 'a2116741ed40a8b5224cbb9f3b1911cbc3e16c9e9d1c0118ffd50462e898be8a'


def getRandomString(length):
    letters = string.ascii_lowercase
    resultString = ''.join(random.choice(letters) for i in range(length))

    return resultString

def test_proportional_forger():
    pos = ProofOfStake()

    # Generate a standard transaction
    AliceWallet = Wallet()
    AliceWallet.fromKey(alicePrivateKeyPath)

    # Generate a standard Wallet
    BobWallet = Wallet()
    
    pos.update(AliceWallet.publicKeyString(), 100)
    pos.update(BobWallet.publicKeyString(), 100)

    logger.info(f"Test Proportional Forger: bob tokens: 100, alice tokens: 100")

    results = { "test": [] }

    for i in range(100):

        bobWins = 0
        AliceWins = 0

        for j in range(100):
            randomString = getRandomString(j)

            forger = pos.forger(randomString)

            if forger == BobWallet.publicKeyString():
                bobWins += 1
            elif forger == AliceWallet.publicKeyString():
                AliceWins += 1
        
        logger.info(f"bob won: {bobWins} times")
        logger.info(f"alice won: {AliceWins} times")

        difference = abs(bobWins - AliceWins)
        logger.info(f"difference: {difference}")
        
        results["test"].append({ f"{i}" : [{"bobWins" : bobWins}, {"AliceWins": AliceWins}, {"difference": difference}]})


    logger.info(f"Results: {results}")

    assert difference <= 8, f"Difference: {difference} .With the same number of tokens {bobWins} and {AliceWins} the selection must be more ore less equal"
