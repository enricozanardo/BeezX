from loguru import logger
from beez.node.BeezNode import BeezNode

if __name__ == "__main__":
    logger.info(f"Hi there.")
    node = BeezNode(key="/Users/lukashubl/tmp/BeezX/beez/keys/genesisPrivateKey.pem")
    # TODO: reload from Index
    node.startP2P(port=8122)
    node.startAPI()
