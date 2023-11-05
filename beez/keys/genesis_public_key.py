"""Test public key."""

import pathlib
from beez.utils.beez_crypto_utils import BeezCryptoUtils
from beez.utils.env_data import ENVData


class GenesisPublicKey:  # pylint: disable=too-few-public-methods
    """
    This key allow the Blockchain to start to forge the first block
    and protect the EXCHANGE transactions!
    """

    def __init__(self):
        mnemonic_words = ENVData.get_value('MNEMONIC_GENESIS_WORDS')
        crypt_utils_obj = BeezCryptoUtils()
        crypt_utils_obj.generate_keys_from_mnemonic_words(mnemonic_words)
        self.priv_key = crypt_utils_obj.get_private_key_str()
        public_key = crypt_utils_obj.generate_public_key()
        self.pub_key = crypt_utils_obj.get_public_key_str()

        """
        current_path = pathlib.Path().resolve()
        self.pub_key = open(    # pylint: disable=consider-using-with
            f"{current_path}/beez/keys/genesisPublicKey.pem", "r", encoding="utf-8"
        ).read()
        self.priv_key = open(   # pylint: disable=consider-using-with
            f"{current_path}/beez/keys/genesisPrivateKey.pem", "r", encoding="utf-8"
        ).read()
        """
