from loguru import logger
import pathlib


from beez.node.BeezNode import BeezNode

def test_genesis_node():
    logger.info(f"start testing forger node")
    logger.info(f"based on the key used at when the blockchain starts..")

    currentPath = pathlib.Path().resolve()
    # logger.info(f"currentPath: {currentPath}")

    genesisPrivateKeyPath = f"{currentPath}/beez/keys/genesisPrivateKey.pem"

    beezNode = BeezNode(genesisPrivateKeyPath)

    logger.info(f"Genesis Node info: CPU:{beezNode.cpus}, GPU: {beezNode.gpus}")

    beezNode.startP2P()
    beezNode.startAPI()

    assert beezNode.wallet != None