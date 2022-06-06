from loguru import logger
import pathlib


from beez.node.BeezNode import BeezNode
from beez.keys.GenesisPublicKey import GenesisPublicKey

def test_alice_node():
    logger.info(f"start testing alice node")
    logger.info(f"based on the Alice Private Key")

    currentPath = pathlib.Path().resolve()
    alicePrivateKeyPath = f"{currentPath}/beez/keys/alicePrivateKey.pem"

    beezNode = BeezNode(alicePrivateKeyPath)

    gpus = len(beezNode.gpus)

    logger.info(f"Genesis Node info: CPU:{beezNode.cpus}, GPU: {gpus}")

    beezNode.startP2P()
    beezNode.startAPI()

    assert beezNode.wallet != None