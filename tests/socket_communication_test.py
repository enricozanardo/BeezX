

from loguru import logger

from beez.socket.SocketCommunication import SocketCommunication

def test_socketCommunication():
    ip = "192.168.1.209"
    port = 8181

    socketCommunication = SocketCommunication(ip, port)
    socketCommunication.startSocketCommunication()

    assert socketCommunication.port == port
    assert socketCommunication.id != None