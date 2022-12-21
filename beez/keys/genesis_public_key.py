"""Test public key."""

import pathlib

class GenesisPublicKey:     # pylint: disable=too-few-public-methods
    """
    This key allow the Blockchain to start to forge the first block
    and protect the EXCHANGE transactions!
    """

    def __init__(self):
        current_path = pathlib.Path().resolve()
        self.pub_key = open(    # pylint: disable=consider-using-with
            f"{current_path}/beez/keys/genesisPublicKey.pem", "r", encoding="utf-8"
        ).read()
        self.priv_key = open(   # pylint: disable=consider-using-with
            f"{current_path}/beez/keys/genesisPrivateKey.pem", "r", encoding="utf-8"
        ).read()
        self.private_key_path = f"{current_path}/beez/keys/genesisPrivateKey.pem"
