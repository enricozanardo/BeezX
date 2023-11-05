from __future__ import annotations
from mnemonic import Mnemonic
import binascii
import codecs
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey, Ed25519PublicKey
from cryptography.exceptions import InvalidSignature
from hashlib import sha256


class BeezCryptoUtils:
    _private_key_obj: Ed25519PrivateKey = None
    _public_key_obj: Ed25519PublicKey = None
    _mnemonic_obj: Mnemonic = None
    _words: str = None
    _address: str = None
    _seeds: bytes = None
    _signature: bytes = None

    def __init__(self, language="english"):
        self._mnemonic_obj = Mnemonic(language)

    def generate_keys_from_mnemonic_words(self, words=None):
        self._words = words
        if words is None:
            self._words = self.generate_mnemonic()
        self.words_to_seed()
        self.generate_private_key()
        self.generate_public_key()

    def generate_mnemonic(self, strength: int = 256) -> str:
        self._words = self._mnemonic_obj.generate(strength=strength)
        return self._words

    def get_words(self) -> str:
        return self._words

    def load_mnemonic(self, words: str) -> str:
        """
        Carica le WORDS
        """
        self._words = words
        return self._words

    def words_to_seed(self) -> bytes:
        """
        Converte le mnemonic in seed
        """
        if self._words is None:
            raise ValueError('Mnemonic not loaded or generated')
        self._seeds = self._mnemonic_obj.to_seed(self._words)
        return self._seeds

    def get_seeds(self) -> bytes:
        """
        Ritorna le seeds
        """
        return self._seeds

    def generate_private_key(self, seeds: bytes = None) -> Ed25519PrivateKey:
        """
        Genera la Private KEY
        """
        if self._seeds is None and seeds is None:
            raise ValueError('Seeds not generated')
        if seeds:
            self._seeds = seeds
        self._private_key_obj = Ed25519PrivateKey.from_private_bytes(self._seeds[32:])
        return self._private_key_obj

    def get_private_key(self) -> Ed25519PrivateKey:
        """
        Ritorna la Private Key se generata
        """
        return self._private_key_obj

    def load_public_key(self, public_key: str):
        public_key_bytes_bin = codecs.decode(public_key, 'hex_codec')
        self._public_key_obj = Ed25519PublicKey.from_public_bytes(data=public_key_bytes_bin)

    def get_private_key_str(self) -> str | None:
        """
        Ritorna la Private KEY come stringa se generata
        """
        if self._private_key_obj is None:
            return None
        return binascii.hexlify(self._private_key_obj.private_bytes_raw()).decode("utf-8")

    def generate_public_key(self, private_key: Ed25519PrivateKey = None) -> Ed25519PublicKey:
        """
        Genera la Public Key
        """
        if self._private_key_obj is None and private_key is None:
            raise ValueError('Private Key not generated')
        if private_key:
            self._private_key_obj = private_key
        self._public_key_obj = self._private_key_obj.public_key()
        return self._public_key_obj

    def get_public_key(self) -> Ed25519PublicKey:
        """
        Ritorna la Public Key se generata
        """
        return self._public_key_obj

    def get_public_key_str(self) -> str | None:
        """
        Ritorna la Public KEY come stringa se generata
        """
        if self._public_key_obj is None:
            return None
        return binascii.hexlify(self._public_key_obj.public_bytes_raw()).decode("utf-8")

    def generate_signature(self, message: bytes) -> bytes:
        """
        Genera la signature
        """
        self._signature = self._private_key_obj.sign(message)
        return self._signature

    def load_signature(self, signature: bytes) -> None:
        """
        Carica una signature
        """
        self._signature = signature

    def get_signature(self) -> bytes:
        """
        Ritorna la signature
        """
        return self._signature

    def verify_signature(self, message: bytes):
        """
        Verifica se la signature è valida
        """
        try:
            self._public_key_obj.verify(self._signature, message)
            return True
        except InvalidSignature as e:
            return False

    def generate_address(self, public_key: str = None) -> str:
        """
        Genera l'address Beez partendo dalla Public Key
        """
        hash_value = self.__create_hash(public_key)
        checksum = self.__generate_checksum_char(hash_value)
        self._address = f"bzx{hash_value[0:38]}{checksum}"
        return self._address

    def is_valid_address(self, address: str, public_key: str):
        """
        Verifica se l'indirizzo è valido
        """
        address_generate = self.generate_address(public_key)
        if address == address_generate:
            return True
        return False

    def is_my_address(self, address: str) -> bool:
        """
        Verifica se l'indirizzo è il proprio
        """
        if self._address is not None and self._address == address:
            return True
        return False

    def get_address(self) -> str:
        """
        Ritorna l'indirzzo se generato
        """
        return self._address

    def __create_hash(self, publick_key: str = None) -> str:
        """
        Converte la Public Key in Hash per generare l'indirizzo
        """
        if publick_key:
            str_encode = publick_key.encode("utf-8")
        else:
            str_encode = self.get_public_key_str().encode("utf-8")
        sha_str = sha256(str_encode).hexdigest()
        return sha_str

    def __generate_checksum_char(self, characters: str) -> str:
        """
        Genera il checksum per la validazione dell'address
        """
        cks = 0
        i = 0

        while (i < len(characters)):
            cks ^= ord(characters[i])
            i += 1
        checksum = f'{cks:04}'
        return checksum
