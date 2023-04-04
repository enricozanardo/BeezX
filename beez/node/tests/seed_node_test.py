# pylint: skip-file
import pathlib
import shutil
import socket
import time
import os
import threading
import requests
from beez.beez_utils import BeezUtils
from beez.node.seed_node import SeedNode
from beez.node.beez_node import BeezNode
from beez.socket.socket_communication.seed_socket_communication import SeedSocketCommunication


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

def clear_directory(dir):
    if os.path.isdir(dir):
        shutil.rmtree(dir)

def test_communication_protocol():
    node = SeedNode(port=3500)
    assert isinstance(node.p2p, SeedSocketCommunication)

def test_split_digital_asset_in_chunks():
    """Tests splitting digital assets in chunks."""
    node = SeedNode(port=3501)
    parts = node.split_digital_asset_in_chunks(5000*"a")
    assert len(parts) == 1
    assert parts[0] == 5000*"a"
    parts = node.split_digital_asset_in_chunks(5001*"a")
    assert len(parts) == 2
    assert parts[0] == 2501*"a"
    assert parts[1] == 2500*"a"
    parts = node.split_digital_asset_in_chunks(10000*"a")
    assert len(parts) == 2
    assert parts[0] == 5000*"a"
    assert parts[1] == 5000*"a"
    parts = node.split_digital_asset_in_chunks(10001*"a")
    assert len(parts) == 5
    parts = node.split_digital_asset_in_chunks(100000*"a")
    assert len(parts) == 5
    parts = node.split_digital_asset_in_chunks(100001*"a")
    assert len(parts) == 10
    parts = node.split_digital_asset_in_chunks(1000000*"a")
    assert len(parts) == 10
    parts = node.split_digital_asset_in_chunks(1000001*"a")
    assert len(parts) == 25
    parts = node.split_digital_asset_in_chunks(10000000*"a")
    assert len(parts) == 25
    parts = node.split_digital_asset_in_chunks(10000001*"a")
    assert len(parts) == 50

def test_assign_chunks_to_nodes():
    """Tests the assignment of a predefined number of chunks to available nodes."""
    node = SeedNode(port=3502)
    nodes = [1,2,3]
    chunks = ["a", "b", "c", "d", "e"]
    assigned_chunks = node.assign_chunks_to_nodes(chunks, nodes)
    assert assigned_chunks == {1:{0: "a", 3: "d"}, 2:{1:"b", 4: "e"}, 3: {2: "c"}}

def test_digital_asset_metadata():
    """Tests whether the digital asset metadata is updated correctly."""
    try:
        currentPath = pathlib.Path().resolve()
        asset_path = f"{currentPath}/beez/socket/tests/digital_assets/test.txt"
        clear_indices()
        # Setup test network
        ip = get_ip()
        seed_node = SeedNode(ip_address=ip, port=3503)
        seed_node.start_p2p()
        time.sleep(5)
        dam_asset_path = f"{currentPath}/beez/socket/tests/digital_assets/nodeA/"
        clear_directory(dam_asset_path)
        os.makedirs(f"{currentPath}/beez/socket/tests/digital_assets/nodeA/")
        storage_node = BeezNode(ip_address=ip, port=3504, first_server_ip=ip, first_server_port=3503, dam_asset_path=dam_asset_path)
        storage_node.start_p2p()
        time.sleep(5)
        dam_asset_path = f"{currentPath}/beez/socket/tests/digital_assets/nodeB/"
        clear_directory(dam_asset_path)
        os.makedirs(f"{currentPath}/beez/socket/tests/digital_assets/nodeB/")
        storage_node_2 = BeezNode(ip_address=ip, port=3505, first_server_ip=ip, first_server_port=3503, dam_asset_path=dam_asset_path)
        storage_node_2.start_p2p()
        time.sleep(10)
        dam_asset_path = f"{currentPath}/beez/socket/tests/digital_assets/nodeC/"
        clear_directory(dam_asset_path)
        os.makedirs(f"{currentPath}/beez/socket/tests/digital_assets/nodeC/")
        storage_node_3 = BeezNode(ip_address=ip, port=3506, first_server_ip=ip, first_server_port=3503, dam_asset_path=dam_asset_path)
        storage_node_3.start_p2p()
        time.sleep(5)
        time.sleep(10)

        port = 3507
        api_thread = threading.Thread(target=start_api_thread, args=(seed_node, int(port), ))
        api_thread.daemon = True
        api_thread.start()
        time.sleep(5)
        
        # Upload asset via Seed Node API
        dfile = open(asset_path, mode="rb")
        url = f"http://{ip}:{port}/uploadasset"
        test_res = requests.post(url, files = {"file": dfile})
        assert test_res.ok

        time.sleep(10)

        digital_asset_metadata = seed_node.digital_asset_metadata
        file_content = b''
        with open(asset_path, mode="rb") as infile:
            file_content = infile.read()

        assert "test.txt" in list(digital_asset_metadata.keys())
        assert digital_asset_metadata["test.txt"] == {
            "fileName": "test.txt",
            "fileHash": BeezUtils.hash(file_content).hexdigest(),
            "numOfChunks": 5,
            "chunkLocations": {
                f"{ip}:{3504}": [0,3],
                f"{ip}:{3505}": [1,4],
                f"{ip}:{3506}": [2]
            }
        }
    finally:
        clear_indices()
        seed_node.stop()
        storage_node.stop()
        storage_node_2.stop()
        storage_node_3.stop()
        time.sleep(10)

def test_digital_asset_metadata_after_node_outage():
    """Tests digital_asset_metadata after node outage."""
    try:
        currentPath = pathlib.Path().resolve()
        asset_path = f"{currentPath}/beez/socket/tests/digital_assets/test.txt"
        clear_indices()
        # Setup test network
        ip = get_ip()
        seed_node = SeedNode(ip_address=ip, port=3508)
        seed_node.start_p2p()
        time.sleep(5)
        dam_asset_path = f"{currentPath}/beez/socket/tests/digital_assets/nodeA/"
        clear_directory(dam_asset_path)
        os.makedirs(f"{currentPath}/beez/socket/tests/digital_assets/nodeA/")
        storage_node = BeezNode(ip_address=ip, port=3509, first_server_ip=ip, first_server_port=3508, dam_asset_path=dam_asset_path)
        storage_node.start_p2p()
        time.sleep(5)
        dam_asset_path = f"{currentPath}/beez/socket/tests/digital_assets/nodeB/"
        clear_directory(dam_asset_path)
        os.makedirs(f"{currentPath}/beez/socket/tests/digital_assets/nodeB/")
        storage_node_2 = BeezNode(ip_address=ip, port=3510, first_server_ip=ip, first_server_port=3508, dam_asset_path=dam_asset_path)
        storage_node_2.start_p2p()
        time.sleep(10)
        dam_asset_path = f"{currentPath}/beez/socket/tests/digital_assets/nodeC/"
        clear_directory(dam_asset_path)
        os.makedirs(f"{currentPath}/beez/socket/tests/digital_assets/nodeC/")
        storage_node_3 = BeezNode(ip_address=ip, port=3511, first_server_ip=ip, first_server_port=3508, dam_asset_path=dam_asset_path)
        storage_node_3.start_p2p()
        time.sleep(5)
        time.sleep(10)

        port = 3512
        api_thread = threading.Thread(target=start_api_thread, args=(seed_node, int(port), ))
        api_thread.daemon = True
        api_thread.start()
        time.sleep(5)
        
        # Upload asset via Seed Node API
        dfile = open(asset_path, mode="rb")
        url = f"http://{ip}:{port}/uploadasset"
        test_res = requests.post(url, files = {"file": dfile})
        assert test_res.ok

        time.sleep(30)

        # stop storage_node_2
        storage_node_2.stop()
        time.sleep(120)

        time.sleep(10)

        digital_asset_metadata = seed_node.digital_asset_metadata

        assert "test.txt" in list(digital_asset_metadata.keys())
        assert digital_asset_metadata["test.txt"]["chunkLocations"] == {
            f"{ip}:{3509}": [0,3],
            f"{ip}:{3511}": [1,2,4],
        }

    finally:
        clear_indices()
        seed_node.stop()
        storage_node.stop()
        storage_node_2.stop()
        storage_node_3.stop()
        time.sleep(10)