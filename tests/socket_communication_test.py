from loguru import logger

from beez.socket.SocketCommunication import SocketCommunication
from beez.node.BeezNode import BeezNode

def test_socketCommunication():
    logger.info(f"start testing socket communication")
    beezNode = BeezNode()

    ip = "192.168.1.209"
    port = 8181

    socketCommunication = SocketCommunication(ip, port)
    socketCommunication.startSocketCommunication(beezNode)

    assert socketCommunication.port == port
    assert socketCommunication.id != None