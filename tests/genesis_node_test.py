from loguru import logger
import pathlib


from beez.node.BeezNode import BeezNode
from beez.keys.GenesisPublicKey import GenesisPublicKey

def test_genesis_node():
    logger.info(f"start testing forger node")
    logger.info(f"based on the key used at when the blockchain starts..")

    currentPath = pathlib.Path().resolve()
    genesisPrivateKeyPath = f"{currentPath}/beez/keys/genesisPrivateKey.pem"

    beezNode = BeezNode(genesisPrivateKeyPath)

    gpus = len(beezNode.gpus)

    logger.info(f"Genesis Node info: CPU:{beezNode.cpus}, GPU: {gpus}")

    beezNode.startP2P()
    beezNode.startAPI()

    assert beezNode.wallet != None