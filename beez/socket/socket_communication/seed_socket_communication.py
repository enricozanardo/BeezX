"""Beez blockchain - seed socket communication."""

from __future__ import annotations
import json
from typing import TYPE_CHECKING, Any
import os
from dotenv import load_dotenv
from loguru import logger
from p2pnetwork.node import Node    # type: ignore
import threading
import time
from datetime import datetime
from copy import deepcopy

from beez.socket.socket_communication.base_socket_communication import BaseSocketCommunication
from beez.socket.socket_communication.dam_message_buffer import DamMessageBuffer
from beez.socket.socket_communication.dam_push_reply_worker import DamPushReplyWorker
from beez.socket.socket_connector import SocketConnector
from beez.beez_utils import BeezUtils
from beez.socket.messages.message_type import MessageType
from beez.socket.messages.message_available_peers import MessageAvailablePeers
from beez.socket.messages.message_health_request import MessageHealthRequest

if TYPE_CHECKING:
    from beez.types import Address
    from beez.socket.messages.message import Message


load_dotenv()  # load .env
LOCAL_TEST_IP = "192.168.1.209"
LOCAL_P2P_PORT = 5444

FIRST_SERVER_IP = os.getenv("FIRST_SERVER_IP", LOCAL_TEST_IP)   # pylint: disable=invalid-envvar-default
P_2_P_PORT = int(os.getenv("P_2_P_PORT", LOCAL_P2P_PORT))   # pylint: disable=invalid-envvar-default
LOCAL_INTERVALS = 20
INTERVALS = int(os.getenv("INTERVALS", LOCAL_INTERVALS))    # pylint: disable=invalid-envvar-default
LOCAL_DISCONNECT_INTERVALS = 300
DISCONNECT_INTERVALS = int(os.getenv("DISCONNECT_INTERVALS", LOCAL_DISCONNECT_INTERVALS))    # pylint: disable=invalid-envvar-default



class SeedSocketCommunication(BaseSocketCommunication):
    """
    This class manage the P2P communication for seed nodes.
    """

    def __init__(self, ip: Address, port: int):
        """Initialize seed socket communication."""
        BaseSocketCommunication.__init__(self, ip, port)   # pylint: disable=super-with-arguments
        self.node_health_status: dict[str, dict[str, Any]] = {}
        self.dead_nodes: list[str] = []
        self.beez_node = None
        self.health_checks_active = True
        self.dam_push_reply_buffer = DamMessageBuffer()
        self.dam_push_reply_worker = None

    def start_socket_communication(self, node):
        self.beez_node = node
        self.dam_push_reply_worker = DamPushReplyWorker(self.dam_push_reply_buffer, self)
        self.dam_push_reply_worker.start()
        self.start()

    def network_health_scan(self):
        """Execution thread to iteratively request the peers health status."""
        status_thread = threading.Thread(target=self.check_health, args={})
        status_thread.daemon = True
        status_thread.start()

    def available_peers_broadcast_thread(self):
        """Execution thread to iteratively broadcast the available peers."""
        peers_thread = threading.Thread(target=self.broadcast_available_peers, args={})
        peers_thread.daemon = True
        peers_thread.start()

    def check_health(self):
        """Checks the current health status of the connected nodes."""
        while self.health_checks_active:
            # logger.info("Current health status")
            # logger.info(self.node_health_status)

            node_disconnected: bool = False
            peers_to_pop_from_health_status: list[str] = []
            for peer_socket_connector, health_dict in self.node_health_status.items():
                now = datetime.now()
                if (now-health_dict["last_update"]).total_seconds() > DISCONNECT_INTERVALS:
                    logger.info(f"!!!! Node is not responding {peer_socket_connector}")
                    # close connection to node
                    nodes_to_disconnect: list[Node] = []
                    found_dead_node_in_all_nodes = False
                    for node in self.all_nodes:
                        # logger.info(f"{node.host}:{node.port}")
                        if f"{node.host}:{node.port}" == peer_socket_connector:
                            found_dead_node_in_all_nodes = True
                            nodes_to_disconnect.append(node)
                            self.dead_nodes.append(peer_socket_connector)

                    # also delete node from own_connections and node_health_status
                    for node in nodes_to_disconnect:
                        node_disconnected = True
                        for index,connection in enumerate(self.own_connections):                            
                            if f"{node.host}:{node.port}" == f"{connection.ip_address}:{connection.port}":
                                del self.own_connections[index]
                        self.own_connections.sort(key=lambda x: f"{x.ip_address}:{x.port}", reverse=True)
                        peers_to_pop_from_health_status.append(f"{node.host}:{node.port}")
                        self.node_disconnect_with_outbound_node(node)
                    
                    # if node stopped gracefully, the node is not in all_connections and thus in nodes_to_disconnect
                    #  anymore so it has to be deleted from own_connections and node_health_status
                    if not found_dead_node_in_all_nodes:
                        for index,connection in enumerate(self.own_connections):
                            if peer_socket_connector == f"{connection.ip_address}:{connection.port}":
                                del self.own_connections[index]
                                node_disconnected = True
                        self.own_connections.sort(key=lambda x: f"{x.ip_address}:{x.port}", reverse=True)
                        peers_to_pop_from_health_status.append(peer_socket_connector)

            for peer_to_pop_from_health_status in peers_to_pop_from_health_status:
                self.node_health_status.pop(peer_to_pop_from_health_status, None)
                        
            if node_disconnected:
                # TODO: Update file chunk metadata if new primaries and backup nodes assigned
                self.beez_node.update_digital_asset_metadata(self.get_available_peers())
                available_peers_message = self.create_available_peers_message()
                self.broadcast(available_peers_message)

            health_request_message = MessageHealthRequest(self.socket_connector, MessageType.HEALTHREQUEST)
            encoded_health_request_message: str = BeezUtils.encode(health_request_message)
            self.broadcast(encoded_health_request_message)
            time.sleep(INTERVALS)

    def get_available_peers(self):
        # calculate list of peers
        peers_list = {}
        for socket_connector in self.own_connections:
            peers_list[f"{socket_connector.ip_address}:{socket_connector.port}"] = 100   # TODO: calculate real health
        return peers_list

    def create_available_peers_message(self):
        """Create message containing information about the available peers in the system."""
        own_connector = self.socket_connector

        peers_list = self.get_available_peers()

        logger.info(peers_list)
        dead_peers = deepcopy(self.dead_nodes)
        message = MessageAvailablePeers(own_connector, MessageType.PEERSREQUEST, peers_list, dead_peers)
        self.dead_nodes = []

        # Encode the message since peers communicate with bytes!
        encoded_peers_message: str = BeezUtils.encode(message)
        return encoded_peers_message
    
    def broadcast_available_peers(self):
        """Broadcast the currently available peers."""
        encoded_peers_message = self.create_available_peers_message()
        self.broadcast(encoded_peers_message)
        time.sleep(60)


    def inbound_node_connected(self, node: Node):
        """Callback method of receiving requests from nodes."""
        logger.info("Storage node wants to connect - send list of peers")

        new_peer = True
        node_socket_connector = SocketConnector(node.host, node.port)

        for connection in self.own_connections:
            if connection.equals(node_socket_connector):
                # the node is itself
                new_peer = False

        if new_peer is True:
            # if is not itself add to the list of peers
            self.own_connections.append(node_socket_connector)
            self.own_connections.sort(key=lambda x: f"{x.ip_address}:{x.port}", reverse=True)
    
        encoded_peers_message = self.create_available_peers_message()
        self.broadcast(encoded_peers_message)

    def node_message(self, node: Node, data: Message):
        """Handle incomming p2p messages."""
        message = BeezUtils.decode(json.dumps(data))
        if message.message_type == MessageType.HEALTH:
            self.node_health_status[f"{node.host}:{node.port}"] = {
                "health_metric": message.health_status,
                "last_update": datetime.now(),
            }
        elif message.message_type == "junk_reply":
            logger.info(100*'#')
            logger.info(f'GOT CHUNK REPLY {message.junk_name}')
            junk = message.junk
            chunk_name = message.junk_name
            file_name = message.file_name
            self.beez_node.add_asset_junks(file_name, chunk_name, junk)
        elif message.message_type == "push_junk_reply":
            self.dam_push_reply_buffer.add_message(node, message)
