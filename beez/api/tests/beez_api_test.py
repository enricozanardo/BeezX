# pylint: skip-file
import shutil
import time
import requests
import threading
import socket
from beez.node.seed_node import SeedNode
from beez.node.beez_node import BeezNode

def clear_indices():
    shutil.rmtree("account_indices", ignore_errors=True)
    shutil.rmtree("balance_indices", ignore_errors=True)
    shutil.rmtree("blocks_indices", ignore_errors=True)
    shutil.rmtree("challenge_indices", ignore_errors=True)
    shutil.rmtree("pos_indices", ignore_errors=True)
    shutil.rmtree("txp_indices", ignore_errors=True)
    shutil.rmtree("address_indices", ignore_errors=True)

def get_ip():
    """Return IP of node."""
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        sock.connect(("8.8.8.8", 53))
        node_address= sock.getsockname()[0]
        return node_address

def start_api_thread(node, port):
    node.start_api(port)

def test_connected_nodes():
    """Tests the nodes endpoint for connected nodes."""
    try:
        clear_indices()
        ip = get_ip()
        port = 8312
        seed_node = SeedNode(ip_address=ip, port=8311)
        seed_node.start_p2p()
        time.sleep(10)
        storage_node_1 = BeezNode(ip_address=ip, port=5646, first_server_ip=ip, first_server_port=8311)
        storage_node_1.start_p2p()
        time.sleep(5)
        api_thread = threading.Thread(target=start_api_thread, args=(storage_node_1, int(port), ))
        api_thread.daemon = True
        api_thread.start()
        time.sleep(5)
        response = requests.get(f'http://{ip}:{port}/connectednodes')

        assert response.status_code == 200
        assert response.json() == {'connected_nodes': {ip: 8311}}
    finally:
        clear_indices()
        seed_node.stop()
        storage_node_1.stop()
        time.sleep(10)