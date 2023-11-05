from mnemonic import Mnemonic
import mnemonic
import unittest
from Crypto.PublicKey import ECC
from Crypto.Signature import eddsa
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ed25519
import ed25519
import bip39
import sys
import bip32utils
from bip_utils import Bip32Slip10Secp256k1, Bip39SeedGenerator, Bip44, Bip44Coins, Bip44ConfGetter
from Crypto.Hash import SHA512
import json

# setting path
sys.path.append('../../../')
from beez.beez_utils import BeezUtils
from beez.wallet.wallet import Wallet
import binascii
from bip_utils import (
    Bip39EntropyBitLen, Bip39EntropyGenerator, Bip39WordsNum, Bip39Languages, Bip39MnemonicGenerator,
    Bip39MnemonicEncoder
)


# generare le parole mnemoniche, chiave pubblica e privata, hash della pubblica
# importare parole

class TestWallet(unittest.TestCase):
    def test_creation_mnemoniche(self):
        mnemo = Mnemonic("english")
        words = mnemo.generate(strength=256)

        # mnemonic = Bip39MnemonicGenerator(Bip39Languages.ENGLISH).FromWordsNumber(Bip39WordsNum.WORDS_NUM_24)

        words = "about anchor parade crash drastic agent tomato behind engine april install inner salon cliff zero window depth long seed sword scene crouch route among"
        seed = mnemo.to_seed(words, passphrase="")

        key_pair = ECC.generate(curve="ed25519")

        print(f"\tWORDS: {words}")
        print(f"\tSEED: {seed}")

        """
        root_key = bip32utils.BIP32Key.fromEntropy(seed)
        root_address = root_key.Address()
        root_public_hex = str(root_key.PublicKey().hex())
        root_private_wif = root_key.WalletImportFormat()

        address_beez = BeezUtils.address_from_public_key(root_public_hex) # <-- OK

        print('DATA:')
        print(f'\tADDRESS: {root_address}')
        print(f'\tPUBLIC KEY : {root_public_hex}')
        print(f'\tPRIVATE KEY: {root_private_wif}\n')
        print(f'\tADDRESS BEEZ: {address_beez}\n')
        """

        """
        privKey, pubKey = ed25519.create_keypair()
        print("Private key (32 bytes):", privKey.to_ascii(encoding='hex'))
        print("Public key (32 bytes): ", pubKey.to_ascii(encoding='hex'))
        # msg = b'Message for Ed25519 signing'
        msg = b'\x02\x09' + bytes(words, 'ascii')
        signature = privKey.sign(msg, encoding='hex')
        print("Signature (64 bytes):", signature)

        try:
            pubKey.verify(signature, msg, encoding='hex')
            print("The signature is valid.")
        except:
            print("Invalid signature!")
        """

        """
        mnemo = Mnemonic("english")
        words = mnemo.generate(strength=256)
        print('words: ', words)
        private_key = Ed25519PrivateKey.generate()
        print('private_key: ', private_key)
        signature = private_key.sign(b"my authenticated message")
        print('signature: ', signature)
        public_key = private_key.public_key()
        print('public_key: ', public_key)
        # Raises InvalidSignature if verification fails
        public_key.verify(signature, b"my authenticated message")
        """

        """
        mnemo = Mnemonic("english")
        words = mnemo.generate(strength=256)
        print('words: ', words)
        key_pair = ECC.generate(curve="ed25519")
        path = 'myprivatekey.pem'
        f = open(path, 'wt')
        f.write(key_pair.export_key(format='PEM'))
        f.close()
        genesis_wallet = Wallet()
        genesis_wallet.from_key(path)
        signature = genesis_wallet.sign(mnemo)
        print('signature: ', signature)
        """


if __name__ == '__main__':
    unittest.main()
