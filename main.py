from loguru import logger
from beez.node.beez_node import BeezNode
from beez.node.seed_node import SeedNode
import threading
import pathlib
import sys
import os
import time

def start_p2p_thread(node):
    node.start_p2p()

def start_api_thread(node, port):
    node.start_api(port)

if __name__ == "__main__":
    node_types = {'storage': BeezNode, 'seed': SeedNode}
    key_path = os.getenv("BEEZ_NODE_KEY_PATH", None)
    node_type = os.getenv("NODE_TYPE", "storage")
    api_startup_delay = int(os.getenv("API_STARTUP_DELAY", 20))

    if not key_path:
        logger.info("Can't start node, no path to private key set in env variable BEEZ_NODE_KEY_PATH")
        raise Exception("no key path given")

    currentPath = pathlib.Path().resolve()

    # genesis_private_key_path = f"{currentPath}/beez/keys/genesisPrivateKey.pem"
    # node = BeezNode(key="/Users/lukashubl/tmp/BeezX/beez/keys/alicePrivateKey.pem", port=5449)
    # node = SeedNode(key="/Users/lukashubl/tmp/BeezX/beez/keys/genesisPrivateKey.pem", port=5448)

    p2p_port = sys.argv[1] if len(sys.argv) > 1 else 5444
    api_port = sys.argv[2] if len(sys.argv) > 2 else 5445

    NODE = node_types[node_type]

    node = NODE(key=key_path)
    
    p2p_thread = threading.Thread(target=start_p2p_thread, args=(node, ))
    p2p_thread.start()

    logger.info('STARTUP DELAY ' + str(api_startup_delay))

    time.sleep(api_startup_delay)  # required for docker-compose since otherwise, p2p connection sometimes can't connect due to performance problems
    api_thread = threading.Thread(target=start_api_thread, args=(node, int(api_port), ))
    api_thread.start()
    
    
