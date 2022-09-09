from loguru import logger
from beez.node.BeezNode import BeezNode
import threading

def startP2P(node):
    node.startP2P()

def startAPI(node):
    node.startAPI()

if __name__ == "__main__":
    logger.info(f"Hi there.")
    node = BeezNode(key="/Users/lukashubl/tmp/BeezX/beez/keys/genesisPrivateKey.pem")
    
    p2p_thread = threading.Thread(target=startP2P, args=(node,))
    p2p_thread.start()

    api_thread = threading.Thread(target=startAPI, args=(node,))
    api_thread.start()
    
    
