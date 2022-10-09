from loguru import logger
import pathlib


from beez.node.beez_node import BeezNode
from beez.keys.genesis_public_key import GenesisPublicKey

def test_genesis_node():
    logger.info(f"start testing forger node")
    logger.info(f"based on the key used at when the blockchain starts..")

    currentPath = pathlib.Path().resolve()
    genesisPrivateKeyPath = f"{currentPath}/beez/keys/genesisPrivateKey.pem"

    beezNode = BeezNode(genesisPrivateKeyPath)

    logger.info(f"Genesis Node info: CPU:{beezNode.cpus}, GPU: {beezNode.gpus}")

    beezNode.start_p2p()
    beezNode.start_api()

    assert beezNode.wallet != None