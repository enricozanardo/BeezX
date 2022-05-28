from __future__ import annotations
from typing import TYPE_CHECKING, List
import threading
import time
from loguru import logger
import os
from dotenv import load_dotenv

from beez.socket.SocketConnector import SocketConnector
from beez.socket.MessageType import MessageType
from beez.socket.MessageOwnConnections import MessageOwnConnections
from beez.BeezUtils import BeezUtils

if TYPE_CHECKING:
    from beez.socket.SocketCommunication import SocketCommunication
    from p2pnetwork.node import Node

load_dotenv()  # load .env
LOCAL_INTERVALS = 10
INTERVALS = int(os.getenv('INTERVALS', LOCAL_INTERVALS))


class PeerDiscoveryHandler():
    """
    A Socket Communication submodule that frequently checks if there are new peers in the network.
    """

    def __init__(self, socketCommunication: SocketCommunication) -> None:
        self.socketCommunication = socketCommunication

    
    def start(self):
        # start node threads... 
        statusThread = threading.Thread(target=self.status, args={})
        statusThread.start()

        discoveryThread = threading.Thread(target=self.discovery, args={})
        discoveryThread.start()


    """
    Display the nodes that are connected to a node
    """
    def status(self):
        while True:
            logger.info(f"Current connections:")
            for connection in self.socketCommunication.ownConnections:
                logger.info(f"Peer: {str(connection.ip)}:{str(connection.ip)}")

            time.sleep(INTERVALS)


    def discovery(self):
         while True:
            logger.info(f"discovery")
            handshakeMessage = self.handshakeMessage()
            # Broadcast the message
            self.socketCommunication.broadcast(handshakeMessage)

            time.sleep(INTERVALS)

    # send a message to a specific node
    def handshake(self, connectedNode: Node):
        """
        exchange of information between nodes.
        """
        handshakeMessage = self.handshakeMessage() # create the message of type DISCOVERY
        self.socketCommunication.send(connectedNode, handshakeMessage)

        
    def handshakeMessage(self):
        """
        Define the specific content of the Discovery message that will be shared between peers.
        Here, what is important is to share the knowed peers
        """
        ownConnector = self.socketCommunication.socketConnector
        ownConnections = self.socketCommunication.ownConnections
        messageType = MessageType.DISCOVERY.name

        message = MessageOwnConnections(ownConnector, messageType, ownConnections)

        # Encode the message since peers communicate with bytes!
        encodedMessage: str = BeezUtils.encode(message)

        return encodedMessage

    def handleMessage(self, message: MessageOwnConnections):
        peerSocketConnector = message.senderConnector
        peerConnectionList: List[SocketConnector] = message.ownConnections
        newPeer = True

        for connection in self.socketCommunication.ownConnections:
            if connection.equals(peerSocketConnector):
                # the node is itself
                newPeer = False
        
        if newPeer == True:
           # if is not itself add to the list of peers
           self.socketCommunication.ownConnections.append(peerSocketConnector)  

        # Check if in the peersPeerList there are new peers and connect to them
        for connectionPeer in peerConnectionList:
            peerKnow = False
            for connection in self.socketCommunication.ownConnections:
                if connection.equals(connectionPeer):
                    peerKnow == True
            if not peerKnow and not connectionPeer.equals(self.socketCommunication.socketConnector):
                self.socketCommunication.connect_with_node(connectionPeer.ip, connectionPeer.port)
