from loguru import logger


from beez.node.beez_node import BeezNode

def test_node():
    logger.info(f"start testing node")
    beezNode = BeezNode()

    logger.info(f"Node info: CPU:{beezNode.cpus}, GPU: {beezNode.gpus}")

    beezNode.start_p2p()
    beezNode.start_api()

    assert beezNode.wallet != None