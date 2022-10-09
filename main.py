from loguru import logger
from beez.node.beez_node import BeezNode
import threading
import sys

def startP2P(node, port):
    node.startP2P(port)

def startAPI(node, port):
    node.startAPI(port)

if __name__ == "__main__":
    node = BeezNode(key="/Users/lukashubl/tmp/BeezX/beez/keys/genesisPrivateKey.pem")

    p2p_port = sys.argv[1] if len(sys.argv) > 1 else None
    api_port = sys.argv[2] if len(sys.argv) > 2 else None
    
    p2p_thread = threading.Thread(target=startP2P, args=(node, int(p2p_port), ))
    p2p_thread.start()

    api_thread = threading.Thread(target=startAPI, args=(node, int(api_port), ))
    api_thread.start()
    
    
