from loguru import logger

from beez.socket.socket_communication.socket_communication import SocketCommunication
from beez.node.beez_node import BeezNode

def test_socketCommunication():
    logger.info(f"start testing socket communication")
    beezNode = BeezNode()

    ip = "192.168.1.209"
    port = 8181

    socketCommunication = SocketCommunication(ip, port)
    socketCommunication.start_socket_communication(beezNode)

    assert socketCommunication.port == port
    assert socketCommunication.id != None