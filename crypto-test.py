from nacl.encoding import Base64Encoder
from nacl.signing import SigningKey
import codecs
from Crypto.Signature import eddsa
from Crypto.Signature import DSS
# from Crypto.Cipher import EDDSA
from Crypto.Cipher import AES
from beez.beez_utils import BeezUtils

from Crypto.PublicKey import ECC

if __name__ == '__main__':


    # Prepare tests for compatibility btw. Beezy and BeezX Ed25519 encrpytion
    import binascii
    data = {"lukas":123, "test": "funny"}
    data_hash = BeezUtils.hash(data)
    str_val_2 = data_hash.hexdigest().encode('utf-8')
    hex_val_2 = binascii.hexlify(str_val_2).decode('utf-8')

    # HANDLING FROM MNEMONIC SIGNATURES IN BEEZY (COPY VALUES FROM BEEZY LOGS)
    js_signature = "5080f3e041a700880fe9c77c12419b7e6de2ac4e0c44fc16e307dddb2fe1304449d429852665e7e13490e43fee19bdd938811b53c2bf14c6be2a474bae5c3900"
    sig_js_bytes = codecs.decode(js_signature, 'hex_codec')
    js_pub_key_hex = "302a300506032b657003210033d68a25a5118b21d6ae5bdd5ac438fadcb0b27a5683695ae0e84d6d23cf4913"
    binary_key = codecs.decode(js_pub_key_hex, 'hex_codec')
    key = ECC.import_key(binary_key, curve_name="ed25519")
    verifier = eddsa.new(key, 'rfc8032')
    print("### MNECMONIC KEYS TEST ###")
    try:
        verifier.verify(bytes.fromhex(hex_val_2), sig_js_bytes)
        print('ok')
    except ValueError:
        print('nok')

    # HANDLING FROM PEMFILE SIGNATURES IN BEEZY (COPY VALUES FROM BEEZY LOGS)
    js_signature = "c1e39e34a8609e98c5975777d8ce1d778e1e2f700d600c1fc72dcf70f8f140c658679d173e81db3b4b2dd4ece21aab1502ebc1d642af82f6bcddabb7ce53c007"
    sig_js_bytes = codecs.decode(js_signature, 'hex_codec')
    js_pub_key_hex = "302a300506032b6570032100de673081fd83ad62d1de643a976779f5b194eaa512b7042b967dbeaca94ac680"
    binary_key = codecs.decode(js_pub_key_hex, 'hex_codec')
    key = ECC.import_key(binary_key, curve_name="ed25519")
    verifier = eddsa.new(key, 'rfc8032')
    print("### PEM KEYS TEST ###")
    try:
        verifier.verify(bytes.fromhex(hex_val_2), sig_js_bytes)
        print('ok')
    except ValueError:
        print('nok')
