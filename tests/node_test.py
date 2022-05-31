from loguru import logger


from beez.node.BeezNode import BeezNode

def test_node():
    logger.info(f"start testing node")
    beezNode = BeezNode()

    logger.info(f"Node info: CPU:{beezNode.cpus}, GPU: {beezNode.gpus}")

    beezNode.startP2P()
    beezNode.startAPI()

    assert beezNode.wallet != None