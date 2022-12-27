"""Beez blockchain - wallet."""

from __future__ import annotations
from typing import TYPE_CHECKING, List, Optional
from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5
from loguru import logger

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

    def __init__(self):
        # 1024 is the modulo that we are going to use.
        self.key_pair = RSA.generate(1024)
        logger.info("A Wallet is generated")

    def from_key(self, file):
        """Creates a new wallet from a given key."""
        key = ""
        with open(file, "r", encoding="utf-8") as keyfile:
            key = RSA.import_key(keyfile.read())
        self.key_pair = key

    def sign(self, data):
        "Creates a signature based on the given data."
        data_hash = BeezUtils.hash(data)
        signature_scheme_object = PKCS1_v1_5.new(self.key_pair)
        signature = signature_scheme_object.sign(data_hash)

        return signature.hex()

    @staticmethod
    def signature_valid(data, signature, public_key_string: PublicKeyString) -> bool:
        """Checks if a given signature is valid based on data and public key."""
        signature = bytes.fromhex(signature)
        data_hash = BeezUtils.hash(data)
        public_key = RSA.importKey(public_key_string)
        # providing the pubKey is able to validate the signature
        signature_scheme_object = PKCS1_v1_5.new(public_key)
        signature_valid = signature_scheme_object.verify(data_hash, signature)  # type: ignore # pylint: disable=not-callable

        return signature_valid

    def public_key_string(self) -> PublicKeyString:
        """Returns the public key in string format."""
        public_key_string: PublicKeyString = (
            self.key_pair.publickey().exportKey("PEM").decode("utf-8")
        )
        return public_key_string

    def public_key_hex(self) -> str:
        """Returns the public key in hex format"""
        return self.key_pair.public_key().exportKey().hex()

    # Manage Transaction
    def create_transaction(
        self, receiver: str, amount, transaction_type: TransactionType
    ) -> Transaction:
        """Creates a new, signed transaction."""
        transaction = Transaction(
            BeezUtils.address_from_public_key(self.public_key_string()),
            receiver,
            amount,
            transaction_type,
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
            BeezUtils.address_from_public_key(self.public_key_string()),
            BeezUtils.address_from_public_key(self.public_key_string()),
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
            BeezUtils.address_from_public_key(self.public_key_string()),
            block_counter,
        )

        signature = self.sign(block.payload())

        block.sign(signature)  # sign the Block

        return block
