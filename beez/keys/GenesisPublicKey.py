import pathlib

class GenesisPublicKey():
    """
    This key allow the Blockchain to start to forge the first block and protect the EXCHANGE transactions!
    """

    def __init__(self):
        currentPath = pathlib.Path().resolve()
        self.pubKey = open(f"{currentPath}/beez/keys/genesisPublicKey.pem", 'r').read()
        self.privKey = open(f"{currentPath}/beez/keys/genesisPrivateKey.pem", 'r').read()