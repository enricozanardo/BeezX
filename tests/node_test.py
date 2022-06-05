from loguru import logger


from beez.node.BeezNode import BeezNode

def test_node():
    logger.info(f"start testing node")
    beezNode = BeezNode()

    gpus = len(beezNode.gpus)

    logger.info(f"Node info: CPU:{beezNode.cpus}, GPU: {gpus}")

    beezNode.startP2P()
    beezNode.startAPI()

    assert beezNode.wallet != None