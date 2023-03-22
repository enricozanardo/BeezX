# pylint: skip-file
import shutil
import os
import pathlib
import requests
import threading
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

def start_api_thread(node, port):
    node.start_api(port)

def clear_directory(dir):
    if os.path.isdir(dir):
        shutil.rmtree(dir)


def test_connect_two_nodes():
    """Tests if a setup of one seed node and one storage node connect correctly."""
    try:
        clear_indices()
        ip = get_ip()
        seed_node = SeedNode(ip_address=ip, port=8111)
        seed_node.start_p2p()
        time.sleep(10)
        storage_node = BeezNode(ip_address=ip, port=5446, first_server_ip=ip, first_server_port=8111)
        storage_node.start_p2p()
        time.sleep(10)
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
        seed_node = SeedNode(ip_address=ip, port=8112)
        seed_node.start_p2p()
        time.sleep(10)
        storage_node = BeezNode(ip_address=ip, port=5547, first_server_ip=ip, first_server_port=8112)
        storage_node.start_p2p()
        time.sleep(10)
        storage_node_2 = BeezNode(ip_address=ip, port=5548, first_server_ip=ip, first_server_port=8112)
        storage_node_2.start_p2p()
        time.sleep(10)
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
        seed_node = SeedNode(ip_address=ip, port=8113)
        seed_node.start_p2p()
        time.sleep(10)
        storage_node = BeezNode(ip_address=ip, port=5549, first_server_ip=ip, first_server_port=8113)
        storage_node.start_p2p()
        time.sleep(10)
        storage_node_2 = BeezNode(ip_address=ip, port=5550, first_server_ip=ip, first_server_port=8113)
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
        time.sleep(120)
        storage_node_all_connections = distinct_nodes(storage_node.p2p.all_nodes)
        seed_node_all_connections = distinct_nodes(seed_node.p2p.all_nodes)
        assert len(storage_node_all_connections) == 1
        assert len(seed_node_all_connections) == 1
        assert str(storage_node_all_connections[0].host) == str(ip)
        assert str(storage_node_all_connections[0].port) == str(8113)
    finally:
        clear_indices()
        seed_node.stop()
        storage_node.stop()
        storage_node_2.stop()
        time.sleep(10)

def test_upload_asset():
    """Tests the upload of a sample text file."""
    try:
        currentPath = pathlib.Path().resolve()
        asset_path = f"{currentPath}/beez/socket/tests/digital_assets/test.txt"
        clear_indices()
        # Setup test network
        ip = get_ip()
        seed_node = SeedNode(ip_address=ip, port=8114)
        seed_node.start_p2p()
        time.sleep(20)
        dam_asset_path = f"{currentPath}/beez/socket/tests/digital_assets/nodeA/"
        clear_directory(dam_asset_path)
        os.makedirs(f"{currentPath}/beez/socket/tests/digital_assets/nodeA/")
        storage_node = BeezNode(ip_address=ip, port=5551, first_server_ip=ip, first_server_port=8114, dam_asset_path=dam_asset_path)
        storage_node.start_p2p()
        time.sleep(20)
        dam_asset_path = f"{currentPath}/beez/socket/tests/digital_assets/nodeB/"
        clear_directory(dam_asset_path)
        os.makedirs(f"{currentPath}/beez/socket/tests/digital_assets/nodeB/")
        storage_node_2 = BeezNode(ip_address=ip, port=5552, first_server_ip=ip, first_server_port=8114, dam_asset_path=dam_asset_path)
        storage_node_2.start_p2p()
        time.sleep(20)
        dam_asset_path = f"{currentPath}/beez/socket/tests/digital_assets/nodeC/"
        clear_directory(dam_asset_path)
        os.makedirs(f"{currentPath}/beez/socket/tests/digital_assets/nodeC/")
        storage_node_3 = BeezNode(ip_address=ip, port=5553, first_server_ip=ip, first_server_port=8114, dam_asset_path=dam_asset_path)
        storage_node_3.start_p2p()
        time.sleep(20)

        port = 8212
        api_thread = threading.Thread(target=start_api_thread, args=(seed_node, int(port), ))
        api_thread.daemon = True
        api_thread.start()
        time.sleep(20)
        
        # Upload asset via Seed Node API
        dfile = open(asset_path, mode="rb")
        url = f"http://{ip}:{port}/uploadasset"
        test_res = requests.post(url, files = {"file": dfile})
        assert test_res.ok
        time.sleep(10)
        assert len(storage_node.primary_chunks) == 2
        assert len(storage_node.backup_chunks) == 2
        chunk_parts = []
        backup_chunk_parts = []
        for chunk in storage_node.primary_chunks:
            chunk_parts.append(chunk.split('-')[1])
        for chunk in storage_node.backup_chunks:
            backup_chunk_parts.append(chunk.split('-')[1])
        assert chunk_parts == ["0.dap", "3.dap"]
        assert backup_chunk_parts == ["1.dap", "4.dap"]
        assert len(storage_node_2.primary_chunks) == 2
        chunk_parts = []
        for chunk in storage_node_2.primary_chunks:
            chunk_parts.append(chunk.split('-')[1])
        assert chunk_parts == ["1.dap", "4.dap"]
        assert len(storage_node_3.primary_chunks) == 1
        chunk_parts = []
        for chunk in storage_node_3.primary_chunks:
            chunk_parts.append(chunk.split('-')[1])
        assert chunk_parts == ["2.dap"]
    finally:
        clear_indices()
        seed_node.stop()
        storage_node.stop()
        storage_node_2.stop()
        storage_node_3.stop()
        time.sleep(10)

def test_move_asset_chunks_on_node_failure():
    """Tests the upload of a sample text file."""
    try:
        currentPath = pathlib.Path().resolve()
        asset_path = f"{currentPath}/beez/socket/tests/digital_assets/test.txt"
        clear_indices()
        # Setup test network
        ip = get_ip()
        seed_node = SeedNode(ip_address=ip, port=8115)
        seed_node.start_p2p()
        time.sleep(5)
        dam_asset_path = f"{currentPath}/beez/socket/tests/digital_assets/nodeA/"
        clear_directory(dam_asset_path)
        os.makedirs(f"{currentPath}/beez/socket/tests/digital_assets/nodeA/")
        storage_node = BeezNode(ip_address=ip, port=5554, first_server_ip=ip, first_server_port=8115, dam_asset_path=dam_asset_path)
        storage_node.start_p2p()
        time.sleep(5)
        dam_asset_path = f"{currentPath}/beez/socket/tests/digital_assets/nodeB/"
        clear_directory(dam_asset_path)
        os.makedirs(f"{currentPath}/beez/socket/tests/digital_assets/nodeB/")
        storage_node_2 = BeezNode(ip_address=ip, port=5555, first_server_ip=ip, first_server_port=8115, dam_asset_path=dam_asset_path)
        storage_node_2.start_p2p()
        time.sleep(5)
        dam_asset_path = f"{currentPath}/beez/socket/tests/digital_assets/nodeC/"
        clear_directory(dam_asset_path)
        os.makedirs(f"{currentPath}/beez/socket/tests/digital_assets/nodeC/")
        storage_node_3 = BeezNode(ip_address=ip, port=5556, first_server_ip=ip, first_server_port=8115, dam_asset_path=dam_asset_path)
        storage_node_3.start_p2p()
        time.sleep(5)

        port = 8213
        api_thread = threading.Thread(target=start_api_thread, args=(seed_node, int(port), ))
        api_thread.daemon = True
        api_thread.start()
        time.sleep(20)
        
        # Upload asset via Seed Node API
        dfile = open(asset_path, mode="rb")
        url = f"http://{ip}:{port}/uploadasset"
        test_res = requests.post(url, files = {"file": dfile})
        assert test_res.ok

        time.sleep(10)

        # stop storage_node_2
        storage_node_2.stop()
        time.sleep(120)

        # test storage_node
        assert len(storage_node.primary_chunks) == 2
        chunk_parts = []
        backup_chunk_parts = []
        for chunk in storage_node.primary_chunks:
            chunk_parts.append(chunk.split('-')[1])
        for chunk in storage_node.backup_chunks:
            backup_chunk_parts.append(chunk.split('-')[1])
        assert sorted(chunk_parts) == ["0.dap", "3.dap"]
        assert sorted(backup_chunk_parts) == ["1.dap", "2.dap", "4.dap"]

        # test storage_node_3
        assert len(storage_node_3.primary_chunks) == 3
        chunk_parts = []
        backup_chunk_parts = []
        for chunk in storage_node_3.primary_chunks:
            chunk_parts.append(chunk.split('-')[1])
        for chunk in storage_node_3.backup_chunks:
            backup_chunk_parts.append(chunk.split('-')[1])
        assert sorted(chunk_parts) == ["1.dap", "2.dap", "4.dap"]
        assert sorted(backup_chunk_parts) == ["0.dap", "3.dap"]
    finally:
        clear_indices()
        seed_node.stop()
        storage_node.stop()
        storage_node_2.stop()
        storage_node_3.stop()
        time.sleep(10)

def test_move_asset_chunks_on_node_failure_and_node_connection():
    """Tests the upload of a sample text file."""
    try:
        currentPath = pathlib.Path().resolve()
        asset_path = f"{currentPath}/beez/socket/tests/digital_assets/test.txt"
        clear_indices()
        # Setup test network
        ip = get_ip()
        seed_node = SeedNode(ip_address=ip, port=8116)
        seed_node.start_p2p()
        time.sleep(5)
        dam_asset_path = f"{currentPath}/beez/socket/tests/digital_assets/nodeA/"
        clear_directory(dam_asset_path)
        os.makedirs(f"{currentPath}/beez/socket/tests/digital_assets/nodeA/")
        storage_node = BeezNode(ip_address=ip, port=5557, first_server_ip=ip, first_server_port=8116, dam_asset_path=dam_asset_path)
        storage_node.start_p2p()
        time.sleep(5)
        dam_asset_path = f"{currentPath}/beez/socket/tests/digital_assets/nodeB/"
        clear_directory(dam_asset_path)
        os.makedirs(f"{currentPath}/beez/socket/tests/digital_assets/nodeB/")
        storage_node_2 = BeezNode(ip_address=ip, port=5558, first_server_ip=ip, first_server_port=8116, dam_asset_path=dam_asset_path)
        storage_node_2.start_p2p()
        time.sleep(5)
        dam_asset_path = f"{currentPath}/beez/socket/tests/digital_assets/nodeC/"
        clear_directory(dam_asset_path)
        os.makedirs(f"{currentPath}/beez/socket/tests/digital_assets/nodeC/")
        storage_node_3 = BeezNode(ip_address=ip, port=5559, first_server_ip=ip, first_server_port=8116, dam_asset_path=dam_asset_path)
        storage_node_3.start_p2p()
        time.sleep(5)
        dam_asset_path = f"{currentPath}/beez/socket/tests/digital_assets/nodeD/"
        clear_directory(dam_asset_path)
        os.makedirs(f"{currentPath}/beez/socket/tests/digital_assets/nodeD/")
        storage_node_4 = BeezNode(ip_address=ip, port=5560, first_server_ip=ip, first_server_port=8116, dam_asset_path=dam_asset_path)
        storage_node_4.start_p2p()
        time.sleep(5)

        port = 8214
        api_thread = threading.Thread(target=start_api_thread, args=(seed_node, int(port), ))
        api_thread.daemon = True
        api_thread.start()
        time.sleep(20)
        
        # Upload asset via Seed Node API
        dfile = open(asset_path, mode="rb")
        url = f"http://{ip}:{port}/uploadasset"
        test_res = requests.post(url, files = {"file": dfile})
        assert test_res.ok

        time.sleep(30)

        # Test initial chunk distribution
        # storage_node
        chunk_parts = []
        backup_chunk_parts = []
        for chunk in storage_node.primary_chunks:
            chunk_parts.append(chunk.split('-')[1])
        for chunk in storage_node.backup_chunks:
            backup_chunk_parts.append(chunk.split('-')[1])
        assert sorted(chunk_parts) == ["0.dap", "4.dap"]
        assert sorted(backup_chunk_parts) == ["1.dap"]

        # storage_node_2
        chunk_parts = []
        backup_chunk_parts = []
        for chunk in storage_node_2.primary_chunks:
            chunk_parts.append(chunk.split('-')[1])
        for chunk in storage_node_2.backup_chunks:
            backup_chunk_parts.append(chunk.split('-')[1])
        assert sorted(chunk_parts) == ["1.dap"]
        assert sorted(backup_chunk_parts) == ["2.dap"]

        # test storage_node_3
        chunk_parts = []
        backup_chunk_parts = []
        for chunk in storage_node_3.primary_chunks:
            chunk_parts.append(chunk.split('-')[1])
        for chunk in storage_node_3.backup_chunks:
            backup_chunk_parts.append(chunk.split('-')[1])
        assert sorted(chunk_parts) == ["2.dap"]
        assert sorted(backup_chunk_parts) == ["3.dap"]

        # test storage_node_4
        chunk_parts = []
        backup_chunk_parts = []
        for chunk in storage_node_4.primary_chunks:
            chunk_parts.append(chunk.split('-')[1])
        for chunk in storage_node_4.backup_chunks:
            backup_chunk_parts.append(chunk.split('-')[1])
        assert sorted(chunk_parts) == ["3.dap"]
        assert sorted(backup_chunk_parts) == ["0.dap", "4.dap"]

        # stop storage_node_2
        storage_node_2.stop()
        time.sleep(120)

        # Test chunk distribution after dead storage_node_2
        # storage_node
        chunk_parts = []
        backup_chunk_parts = []
        for chunk in storage_node.primary_chunks:
            chunk_parts.append(chunk.split('-')[1])
        for chunk in storage_node.backup_chunks:
            backup_chunk_parts.append(chunk.split('-')[1])
        assert sorted(chunk_parts) == ["0.dap", "4.dap"]
        assert sorted(backup_chunk_parts) == ["1.dap", "2.dap"]

        # test storage_node_3
        chunk_parts = []
        backup_chunk_parts = []
        for chunk in storage_node_3.primary_chunks:
            chunk_parts.append(chunk.split('-')[1])
        for chunk in storage_node_3.backup_chunks:
            backup_chunk_parts.append(chunk.split('-')[1])
        assert sorted(chunk_parts) == ["1.dap", "2.dap"]
        assert sorted(backup_chunk_parts) == ["3.dap"]

        # test storage_node_4
        chunk_parts = []
        backup_chunk_parts = []
        for chunk in storage_node_4.primary_chunks:
            chunk_parts.append(chunk.split('-')[1])
        for chunk in storage_node_4.backup_chunks:
            backup_chunk_parts.append(chunk.split('-')[1])
        assert sorted(chunk_parts) == ["3.dap"]
        assert sorted(backup_chunk_parts) == ["0.dap", "4.dap"]


        # start new node E
        dam_asset_path = f"{currentPath}/beez/socket/tests/digital_assets/nodeE/"
        clear_directory(dam_asset_path)
        os.makedirs(f"{currentPath}/beez/socket/tests/digital_assets/nodeE/")
        storage_node_5 = BeezNode(ip_address=ip, port=5561, first_server_ip=ip, first_server_port=8116, dam_asset_path=dam_asset_path)
        storage_node_5.start_p2p()
        time.sleep(120)

        # Test chunk distribution after connection of Node E
        # storage_node
        chunk_parts = []
        backup_chunk_parts = []
        for chunk in storage_node.primary_chunks:
            chunk_parts.append(chunk.split('-')[1])
        for chunk in storage_node.backup_chunks:
            backup_chunk_parts.append(chunk.split('-')[1])
        assert sorted(chunk_parts) == ["0.dap", "4.dap"]
        assert sorted(backup_chunk_parts) == ["1.dap", "2.dap"]

        # test storage_node_3
        chunk_parts = []
        backup_chunk_parts = []
        for chunk in storage_node_3.primary_chunks:
            chunk_parts.append(chunk.split('-')[1])
        for chunk in storage_node_3.backup_chunks:
            backup_chunk_parts.append(chunk.split('-')[1])
        assert sorted(chunk_parts) == ["1.dap", "2.dap"]
        assert sorted(backup_chunk_parts) == ["3.dap"]

        # test storage_node_4
        chunk_parts = []
        backup_chunk_parts = []
        for chunk in storage_node_4.primary_chunks:
            chunk_parts.append(chunk.split('-')[1])
        for chunk in storage_node_4.backup_chunks:
            backup_chunk_parts.append(chunk.split('-')[1])
        assert sorted(chunk_parts) == ["3.dap"]
        assert sorted(backup_chunk_parts) == []

        # test storage_node_5
        chunk_parts = []
        backup_chunk_parts = []
        for chunk in storage_node_5.primary_chunks:
            chunk_parts.append(chunk.split('-')[1])
        for chunk in storage_node_5.backup_chunks:
            backup_chunk_parts.append(chunk.split('-')[1])
        assert sorted(chunk_parts) == []
        assert sorted(backup_chunk_parts) == ["0.dap", "4.dap"]

    finally:
        clear_indices()
        seed_node.stop()
        storage_node.stop()
        storage_node_2.stop()
        storage_node_3.stop()
        storage_node_4.stop()
        storage_node_5.stop()
        time.sleep(10)

# def test_download_asset():
#     """Tests the download of a sample text file."""
#     try:
#         currentPath = pathlib.Path().resolve()
#         asset_path = f"{currentPath}/beez/socket/tests/digital_assets/test.txt"
#         clear_indices()
#         # Setup test network
#         ip = get_ip()
#         seed_node = SeedNode(ip_address=ip, port=8114)
#         seed_node.start_p2p()
#         time.sleep(20)
#         dam_asset_path = f"{currentPath}/beez/socket/tests/digital_assets/nodeA/"
#         clear_directory(dam_asset_path)
#         os.makedirs(f"{currentPath}/beez/socket/tests/digital_assets/nodeA/")
#         storage_node = BeezNode(ip_address=ip, port=5551, first_server_ip=ip, first_server_port=8114, dam_asset_path=dam_asset_path)
#         storage_node.start_p2p()
#         time.sleep(20)
#         dam_asset_path = f"{currentPath}/beez/socket/tests/digital_assets/nodeB/"
#         clear_directory(dam_asset_path)
#         os.makedirs(f"{currentPath}/beez/socket/tests/digital_assets/nodeB/")
#         storage_node_2 = BeezNode(ip_address=ip, port=5552, first_server_ip=ip, first_server_port=8114, dam_asset_path=dam_asset_path)
#         storage_node_2.start_p2p()
#         time.sleep(20)
#         dam_asset_path = f"{currentPath}/beez/socket/tests/digital_assets/nodeC/"
#         clear_directory(dam_asset_path)
#         os.makedirs(f"{currentPath}/beez/socket/tests/digital_assets/nodeC/")
#         storage_node_3 = BeezNode(ip_address=ip, port=5553, first_server_ip=ip, first_server_port=8114, dam_asset_path=dam_asset_path)
#         storage_node_3.start_p2p()
#         time.sleep(20)

#         port = 8212
#         api_thread = threading.Thread(target=start_api_thread, args=(seed_node, int(port), ))
#         api_thread.daemon = True
#         api_thread.start()
#         time.sleep(5)
        
#         # Upload asset via Seed Node API
#         dfile = open(asset_path, mode="rb")
#         url = f"http://{ip}:{port}/uploadasset"
#         test_res = requests.post(url, files = {"file": dfile})
#         assert test_res.ok
#         time.sleep(30)

#         # Download asset via Seed Node API
#         url = f"http://{ip}:{port}/downloadasset"
#         test_res = requests.post(url, files = {"filename": "test.txt"})
#         assert test_res.content == "hallo"
#         assert test_res.ok



#         # assert len(storage_node.primary_chunks) == 2
#         # assert len(storage_node.backup_chunks) == 2
#         # chunk_parts = []
#         # backup_chunk_parts = []
#         # for chunk in storage_node.primary_chunks:
#         #     chunk_parts.append(chunk.split('-')[1])
#         # for chunk in storage_node.backup_chunks:
#         #     backup_chunk_parts.append(chunk.split('-')[1])
#         # assert chunk_parts == ["0.dap", "3.dap"]
#         # assert backup_chunk_parts == ["1.dap", "4.dap"]
#         # assert len(storage_node_2.primary_chunks) == 2
#         # chunk_parts = []
#         # for chunk in storage_node_2.primary_chunks:
#         #     chunk_parts.append(chunk.split('-')[1])
#         # assert chunk_parts == ["1.dap", "4.dap"]
#         # assert len(storage_node_3.primary_chunks) == 1
#         # chunk_parts = []
#         # for chunk in storage_node_3.primary_chunks:
#         #     chunk_parts.append(chunk.split('-')[1])
#         # assert chunk_parts == ["2.dap"]
#     finally:
#         clear_indices()
#         seed_node.stop()
#         storage_node.stop()
#         storage_node_2.stop()
#         storage_node_3.stop()
#         time.sleep(10)
