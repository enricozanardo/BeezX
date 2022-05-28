from loguru import logger


from beez.node.BeezNode import BeezNode

def test_node():
    logger.info(f"start testing node")
    beezNode = BeezNode()

    localIP = "192.168.1.209"

    beezNode.startP2P()

    assert beezNode.ip == localIP
    assert beezNode.wallet != None