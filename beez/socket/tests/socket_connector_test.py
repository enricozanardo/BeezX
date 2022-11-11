# pylint: skip-file
from beez.socket.socket_connector import SocketConnector


def test_socket_connector_creation():
    socket_connector = SocketConnector("127.0.0.1", 3333)
    assert socket_connector is not None
    assert socket_connector.ip_address == "127.0.0.1"
    assert socket_connector.port == 3333

def test_equals():
    socket_connector_1 = SocketConnector("127.0.0.1", 2222)
    socket_connector_2 = SocketConnector("127.0.0.1", 2223)
    assert socket_connector_1.equals(socket_connector_1) == True
    assert socket_connector_2.equals(socket_connector_1) == False

