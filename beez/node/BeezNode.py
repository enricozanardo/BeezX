from __future__ import annotations
from typing import TYPE_CHECKING
import os
from dotenv import load_dotenv
import socket
from loguru import logger
import GPUtil

load_dotenv()  # load .env
P_2_P_PORT = int(os.getenv('P_2_P_PORT', 8122))

if TYPE_CHECKING:
    from beez.Types import Address
    from beez.transaction.Transaction import Transaction
    from beez.transaction.ChallengeTX import ChallengeTX
    

from beez.BeezUtils import BeezUtils
from beez.wallet.Wallet import Wallet
from beez.socket.SocketCommunication import SocketCommunication
from beez.api.NodeAPI import NodeAPI
from beez.transaction.TransactionPool import TransactionPool
from beez.challenge.Keeper import Keeper
from beez.socket.MessageTransaction import MessageTransation
from beez.socket.MessageType import MessageType
from beez.socket.MessageChallengeTransaction import MessageChallengeTransation

class BeezNode():

    def __init__(self, key=None) -> None:
        self.p2p = None
        self.ip = self.getIP()
        self.port = int(P_2_P_PORT)
        self.wallet = Wallet()
        self.transactionPool = TransactionPool()
        self.keeper = Keeper()
        self.gpus = GPUtil.getGPUs()
        self.cpus = os.cpu_count()
        if key is not None:
            self.wallet.fromKey(key)

    def getIP(self) -> Address:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect(('8.8.8.8', 53))
            nodeAddress: Address = s.getsockname()[0]
            logger.info(f"Node IP: {nodeAddress}")

            return nodeAddress

    def startP2P(self):
        self.p2p = SocketCommunication(self.ip, self.port)
        self.p2p.startSocketCommunication(self)

    def startAPI(self):
        self.api = NodeAPI()
        # Inject Node to NodeAPI
        self.api.injectNode(self)
        self.api.start(self.ip)


    # Manage requests that come from the NodeAPI
    def handleTransaction(self, transaction: Transaction):

        # TODO: is valid?
        logger.info(f"Manage the transaction ID: {transaction.id}")

        # already exist in the transaction pool
        transactionExist = self.transactionPool.transactionExists(transaction)

        logger.info(f"transactionExist?: {transactionExist}")

        if not transactionExist:
            # logger.info(f"add to the pool!!!")
            self.transactionPool.addTransaction(transaction)
            # Propagate the transaction to other peers
            message = MessageTransation(self.p2p.socketConnector, MessageType.TRANSACTION.name, transaction)

            encodedMessage = BeezUtils.encode(message)
            self.p2p.broadcast(encodedMessage)
        
        # TODO: check if is time to forge




    def handleChallengeTX(self, challengeTx: ChallengeTX):

        logger.info(f"Manage the challenge ID: {challengeTx.id}")

        # already exist in the transaction pool
        transactionExist = self.transactionPool.transactionExists(challengeTx)

        logger.info(f"transactionExist?: {transactionExist}")

        if not transactionExist:
             # logger.info(f"add to the pool!!!")
            self.keeper.set(challengeTx)
            # Propagate the transaction to other peers
            message = MessageChallengeTransation(self.p2p.socketConnector, MessageType.CHALLENGE.name, challengeTx)

            encodedMessage = BeezUtils.encode(message)
            self.p2p.broadcast(encodedMessage)

        # TODO: check if is time to forge

        logger.info(f"challenge function: {challengeTx.challenge.sharedFunction.__doc__}")

        sharedfunction = challengeTx.challenge.sharedFunction
        logger.info(f"challenge function: {type(sharedfunction)}")
        result = sharedfunction(2,3)

        logger.info(f"result: {result}")



