"""Beez blockchain - wallet."""

from __future__ import annotations
from typing import TYPE_CHECKING, List, Optional
import binascii
import codecs
from Crypto.PublicKey import ECC
from Crypto.Signature import eddsa
from loguru import logger
from beez.utils.beez_crypto_utils import BeezCryptoUtils
from beez.utils.env_data import ENVData

from beez.block.header import Header

from beez.beez_utils import BeezUtils
from beez.challenge.challenge import Challenge
from beez.transaction.transaction import Transaction
from beez.transaction.challenge_tx import ChallengeTX
from beez.block.block import Block

if TYPE_CHECKING:
    from beez.types import WalletAddress, PublicKeyString
    from beez.transaction.transaction_type import TransactionType


class Wallet:
    """
    The wallet is used by clients to allow them to perfom
    transactions into the Blockchain.
    """
    __crypt_utils_obj: BeezCryptoUtils = None

    def __init__(self):
        mnemonic_words = ENVData.get_value('MNEMONIC_WORDS')
        self.__crypt_utils_obj = BeezCryptoUtils()
        self.__crypt_utils_obj.generate_keys_from_mnemonic_words(mnemonic_words)
        private_key = self.__crypt_utils_obj.get_private_key_str()
        public_key = self.__crypt_utils_obj.generate_public_key()
        self.key_pair = self.__crypt_utils_obj.get_public_key_str()

    def from_key(self, public_key):
        self.key_pair = public_key

    def sign(self, data):
        data_hash = BeezUtils.hash(data)
        encoded_hash_hex = data_hash.hexdigest().encode('utf-8')
        data_hex = binascii.hexlify(encoded_hash_hex).decode('utf-8')
        data_bytes = bytes.fromhex(data_hex)
        signature = self.__crypt_utils_obj.generate_signature(data_bytes)
        return signature

    def signature_is_valid(self, data, signature) -> bool:
        self.__crypt_utils_obj.load_signature(signature)
        return self.__crypt_utils_obj.verify_signature(data)

    @staticmethod
    def signature_valid(data, signature, public_key_string) -> bool:
        # Inizializza oggeto CryptoUtils
        crypt_utils_obj = BeezCryptoUtils()
        # Carica la public key
        crypt_utils_obj.load_public_key(public_key_string)
        # Carica la signature
        crypt_utils_obj.load_signature(signature)
        # converte la parola in hash
        test_data_hash = BeezUtils.hash(data)
        # converte la parola in bytes
        encoded_hash_hex = test_data_hash.hexdigest().encode('utf-8')
        data_hex = binascii.hexlify(encoded_hash_hex).decode('utf-8')
        data_bytes = bytes.fromhex(data_hex)
        # verifica la signature
        return crypt_utils_obj.verify_signature(data_bytes)

    def public_key_string(self) -> PublicKeyString:
        return self.key_pair

    def public_key_hex(self) -> str:
        """Returns the public key in hex format"""
        return self.key_pair.public_key().exportKey().hex()

    # Manage Transaction
    def create_transaction(
            self, receiver: str, amount, transaction_type: TransactionType, public_key: PublicKeyString
    ) -> Transaction:
        transaction = Transaction(
            self.__crypt_utils_obj.generate_address(self.public_key_string()),
            receiver,
            amount,
            transaction_type,
            public_key
        )
        signature = self.sign(transaction.payload())
        transaction.sign(signature)
        return transaction

    # Manage ChallengeTransation
    def create_challenge_transaction(
            self, amount, transaction_type: TransactionType, challenge: Challenge
    ) -> ChallengeTX:
        """Creates a new, signed challenge transaction."""
        challenge_transaction = ChallengeTX(
            self.__crypt_utils_obj.generate_address(self.public_key_string()),
            self.__crypt_utils_obj.generate_address(self.public_key_string()),
            amount,
            transaction_type,
            challenge,
        )
        signature = self.sign(challenge_transaction.payload())
        challenge_transaction.sign(signature)
        return challenge_transaction

    # Manage Block creation
    def create_block(
            self,
            header: Optional[Header],
            transactions: List[Transaction],
            last_hash: str,
            block_counter: int,
    ) -> Block:
        """Creates a new, signed block."""
        logger.info(f"CREATING A NEW BLOCK {header}")
        block = Block(
            header,
            transactions,
            last_hash,
            self.__crypt_utils_obj.generate_address(self.public_key_string()),
            block_counter,
        )
        signature = self.sign(block.payload())
        block.sign(signature)  # sign the Block
        return block
