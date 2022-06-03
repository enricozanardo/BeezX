from __future__ import annotations
from typing import TYPE_CHECKING, List, Optional
from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5
from Crypto.Hash import SHA256
from loguru import logger

from beez.block.Header import Header


if TYPE_CHECKING:
    from beez.Types import WalletAddress, PublicKeyString
    from beez.transaction.TransactionType import TransactionType
    
from beez.BeezUtils import BeezUtils
from beez.challenge.Challenge import Challenge
from beez.transaction.Transaction import Transaction
from beez.transaction.ChallengeTX import ChallengeTX
from beez.block.Block import Block

class Wallet():
    """
    The wallet is used by clients to allow them to perfom transactions into the Blockchain.
    """
    def __init__(self):
        # 1024 is the modulo that we are going to use.
        self.keyPair = RSA.generate(1024)
        self.generateAddress()
        logger.info(f"A Wallet is generated")

    def generateAddress(self):
        h = SHA256.new(self.keyPair.public_key().exportKey().hex().encode('utf-8'))
        self.address : WalletAddress = 'bz' + h.hexdigest()[0:42]
        logger.info(f"Address: {self.address}")

    
    def fromKey(self, file):
        key = ''
        with open(file, 'r') as keyfile:
            key = RSA.import_key(keyfile.read())
        self.keyPair = key

    def sign(self, data):
        dataHash = BeezUtils.hash(data)
        signatureSchemeObject = PKCS1_v1_5.new(self.keyPair)
        signature = signatureSchemeObject.sign(dataHash)

        return signature.hex()

    @staticmethod
    def signatureValid(data, signature, publicKeyString: PublicKeyString) -> bool:
        signature = bytes.fromhex(signature)
        dataHash = BeezUtils.hash(data)
        publicKey = RSA.importKey(publicKeyString)
        # providing the pubKey is able to validate the signature
        signatureSchemeObject = PKCS1_v1_5.new(publicKey)
        signatureValid = signatureSchemeObject.verify(dataHash, signature)

        return signatureValid

    def publicKeyString(self) -> PublicKeyString:
        publicKeyString: PublicKeyString = self.keyPair.publickey(
        ).exportKey('PEM').decode('utf-8')

        return publicKeyString

    # Manage Transaction 
    def createTransaction(self, receiver: PublicKeyString, amount, type: TransactionType) -> Transaction:
        transaction = Transaction(
            self.publicKeyString(), receiver, amount, type)
        signature = self.sign(transaction.payload())
        transaction.sign(signature)

        return transaction

    # Manage ChallengeTransation
    def createChallengeTransaction(self, amount, type: TransactionType, challenge: Challenge) -> ChallengeTX:
       
        challengeTransaction = ChallengeTX(
            self.publicKeyString(), self.publicKeyString(), amount, type, challenge)

        signature = self.sign(challengeTransaction.payload())

        challengeTransaction.sign(signature)

        return challengeTransaction

    # Manage Block creation
    def createBlock(self, header: Optional[Header], transactions: List[Transaction], lastHash: str, blockCounter: int) -> Block:
        block = Block(header, transactions, lastHash, self.publicKeyString(), blockCounter)

        signature = self.sign(block.payload())

        block.sign(signature)  # sign the Block

        return block
    
    