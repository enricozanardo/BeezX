# pylint: skip-file
from beez.node.seed_node import SeedNode
from beez.socket.socket_communication.base_socket_communication import BaseSocketCommunication

def test_communication_protocol():
    node = SeedNode(port=3996)
    assert isinstance(node.p2p, BaseSocketCommunication)