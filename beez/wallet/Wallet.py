from __future__ import annotations
from typing import TYPE_CHECKING
from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5
from Crypto.Hash import SHA256
from loguru import logger

from beez.transaction.Transaction import Transaction

if TYPE_CHECKING:
    from beez.Types import WalletAddress, PublicKeyString

from beez.BeezUtils import BeezUtils

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

    def publicKeyString(self) -> PublicKeyString:
        publicKeyString: PublicKeyString = self.keyPair.publickey(
        ).exportKey('PEM').decode('utf-8')

        return publicKeyString