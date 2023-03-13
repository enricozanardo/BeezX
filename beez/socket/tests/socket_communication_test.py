# pylint: skip-file
import shutil
import time
import socket
from beez.socket.socket_connector import SocketConnector
from beez.node.beez_node import BeezNode
from beez.node.seed_node import SeedNode

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

def distinct_nodes(all_nodes):
    """Filter distinct nodes from list of all nodes. All nodes contain incoming and outgoing connections and may thus contain duplicates."""
    distinct_connections = []
    for node in all_nodes:
        append = True
        for distinct_connection in distinct_connections:
            if str(node.host) == str(distinct_connection.host) and str(node.port) == str(distinct_connection.port):
                append = False
        if append:
            distinct_connections.append(node)
    return distinct_connections


def test_connect_two_nodes():
    """Tests if a setup of one seed node and one storage node connect correctly."""
    try:
        clear_indices()
        ip = get_ip()
        seed_node = SeedNode(ip=ip, port=8111)
        seed_node.start_p2p()
        time.sleep(5)
        storage_node = BeezNode(ip=ip, port=5446, first_server_ip=ip, first_server_port=8111)
        storage_node.start_p2p()
        time.sleep(5)
        assert seed_node.p2p.socket_connector.port == 8111
        assert seed_node.port == 8111
        assert seed_node.get_ip() == ip
        storage_node_all_connections = distinct_nodes(storage_node.p2p.all_nodes)
        seed_node_all_connections = distinct_nodes(seed_node.p2p.all_nodes)
        assert len(storage_node_all_connections) == 1
        assert len(seed_node_all_connections) == 1
    finally:
        clear_indices()
        seed_node.stop()
        storage_node.stop()
        time.sleep(10)

def test_connect_three_nodes():
    """Tests if a setup of one seed node and two storage nodes connect correctly."""
    try:
        clear_indices()
        ip = get_ip()
        seed_node = SeedNode(ip=ip, port=8211)
        seed_node.start_p2p()
        time.sleep(5)
        storage_node = BeezNode(ip=ip, port=5546, first_server_ip=ip, first_server_port=8211)
        storage_node.start_p2p()
        time.sleep(5)
        storage_node_2 = BeezNode(ip=ip, port=5548, first_server_ip=ip, first_server_port=8211)
        storage_node_2.start_p2p()
        time.sleep(5)
        storage_node_all_connections = distinct_nodes(storage_node.p2p.all_nodes)
        storage_node_2_all_connections = distinct_nodes(storage_node_2.p2p.all_nodes)
        seed_node_all_connections = distinct_nodes(seed_node.p2p.all_nodes)
        assert len(storage_node_all_connections) == 2
        assert len(storage_node_2_all_connections) == 2
        assert len(seed_node_all_connections) == 2
    finally:
        clear_indices()
        seed_node.stop()
        storage_node.stop()
        storage_node_2.stop()
        time.sleep(10)
    
def test_reconnection_on_node_failure():
    """Tests if a setup of one seed node and two storage nodes after one storage node disconnects, connect correctly."""
    try:
        clear_indices()
        ip = get_ip()
        # Setup seed node and two storage nodes
        seed_node = SeedNode(ip=ip, port=8211)
        seed_node.start_p2p()
        time.sleep(5)
        storage_node = BeezNode(ip=ip, port=5546, first_server_ip=ip, first_server_port=8211)
        storage_node.start_p2p()
        time.sleep(5)
        storage_node_2 = BeezNode(ip=ip, port=5548, first_server_ip=ip, first_server_port=8211)
        storage_node_2.start_p2p()
        time.sleep(10)
        storage_node_all_connections = distinct_nodes(storage_node.p2p.all_nodes)
        storage_node_2_all_connections = distinct_nodes(storage_node_2.p2p.all_nodes)
        seed_node_all_connections = distinct_nodes(seed_node.p2p.all_nodes)
        assert len(storage_node_all_connections) == 2
        assert len(storage_node_2_all_connections) == 2
        assert len(seed_node_all_connections) == 2

        # stop one storage node and check if reconnection worked
        storage_node_2.stop()
        time.sleep(180)
        storage_node_all_connections = distinct_nodes(storage_node.p2p.all_nodes)
        seed_node_all_connections = distinct_nodes(seed_node.p2p.all_nodes)
        assert len(storage_node_all_connections) == 1
        assert len(seed_node_all_connections) == 1
        assert str(storage_node_all_connections[0].host) == str(ip)
        assert str(storage_node_all_connections[0].port) == str(8211)
    finally:
        clear_indices()
        seed_node.stop()
        storage_node.stop()
        time.sleep(10)
