# pylint: skip-file
from beez.node.seed_node import SeedNode
from beez.socket.socket_communication.seed_socket_communication import SeedSocketCommunication

def test_communication_protocol():
    node = SeedNode(port=3998)
    assert isinstance(node.p2p, SeedSocketCommunication)