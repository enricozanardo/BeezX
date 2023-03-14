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


def test_empty_peers_list():
    """Tests if a setup of one seed node and one storage node connect correctly."""
    try:
        clear_indices()
        ip = get_ip()
        port = 8112
        seed_node = SeedNode(ip_address=ip, port=8111)
        seed_node.start_p2p()
        time.sleep(5)
        api_thread = threading.Thread(target=start_api_thread, args=(seed_node, int(port), ))
        api_thread.daemon = True
        api_thread.start()
        time.sleep(5)
        print(f'http://{ip}:{port}/clusterhealth')
        response = requests.get(f'http://{ip}:{port}/clusterhealth')

        assert response.status_code == 200
        assert response.json() == {'cluster_health': {}}
    finally:
        clear_indices()
        seed_node.stop()
        time.sleep(10)

def test_non_empty_peer_list():
    """Tests the seed nodes cluster health endpoint when there are active connections."""
    try:
        clear_indices()
        ip = get_ip()
        port = 8612
        seed_node = SeedNode(ip_address=ip, port=8611)
        seed_node.start_p2p()
        time.sleep(10)
        storage_node_1 = BeezNode(ip_address=ip, port=5746, first_server_ip=ip, first_server_port=8611)
        storage_node_1.start_p2p()
        time.sleep(5)
        api_thread = threading.Thread(target=start_api_thread, args=(seed_node, int(port), ))
        api_thread.daemon = True
        api_thread.start()
        time.sleep(5)
        print(f'http://{ip}:{port}/clusterhealth')
        response = requests.get(f'http://{ip}:{port}/clusterhealth')

        assert response.status_code == 200
        assert response.json() != {'cluster_health': {}}
        assert len(response.json()['cluster_health'].keys()) == 1 
        assert list(response.json()['cluster_health'].keys())[0] == f"{ip}:5746"
    finally:
        clear_indices()
        seed_node.stop()
        storage_node_1.stop()
        time.sleep(10)
