from __future__ import annotations
from typing import TYPE_CHECKING
import os
from dotenv import load_dotenv
import socket
from loguru import logger
import GPUtil
import copy

load_dotenv()  # load .env
P_2_P_PORT = int(os.getenv('P_2_P_PORT', 8122))

if TYPE_CHECKING:
    from beez.Types import Address
    from beez.transaction.Transaction import Transaction
    from beez.transaction.ChallengeTX import ChallengeTX
    from beez.challenge.Challenge import Challenge
    from beez.block.Block import Block
    
from beez.BeezUtils import BeezUtils
from beez.wallet.Wallet import Wallet
from beez.socket.SocketCommunication import SocketCommunication
from beez.api.NodeAPI import NodeAPI
from beez.transaction.TransactionPool import TransactionPool
from beez.socket.MessageTransaction import MessageTransation
from beez.socket.MessageType import MessageType
from beez.socket.MessageChallengeTransaction import MessageChallengeTransation
from beez.block.Blockchain import Blockchain
from beez.socket.MessageBlock import MessageBlock
from beez.socket.MessageBlockchain import MessageBlockchain
from beez.socket.MessageBeezKeeper import MessageBeezKeeper
from beez.challenge.BeezKeeper import BeezKeeper
from beez.socket.Message import Message
from beez.transaction.TransactionType import TransactionType

class BeezNode():

    def __init__(self, key=None) -> None:
        self.p2p = None
        self.ip = self.getIP()
        self.port = int(P_2_P_PORT)
        self.wallet = Wallet()
        self.transactionPool = TransactionPool()
        self.gpus = GPUtil.getGPUs()
        self.cpus = os.cpu_count()
        self.blockchain = Blockchain()
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

        logger.info(f"Manage the transaction ID: {transaction.id}")

        data = transaction.payload()
        signature = transaction.signature
        signaturePublicKey = transaction.senderPublicKey

        # # # is valid?
        signatureValid = Wallet.signatureValid(
            data, signature, signaturePublicKey)

        # already exist in the transaction pool
        transactionExist = self.transactionPool.transactionExists(transaction)

        # already exist in the Blockchain
        transactionInBlock = self.blockchain.transactionExist(transaction)

        if not transactionExist and not transactionInBlock and signatureValid:
            # logger.info(f"add to the pool!!!")
            self.transactionPool.addTransaction(transaction)
            # Propagate the transaction to other peers
            message = MessageTransation(self.p2p.socketConnector, MessageType.TRANSACTION.name, transaction)

            encodedMessage = BeezUtils.encode(message)

            self.p2p.broadcast(encodedMessage)
        
            # check if is time to forge a new Block
            forgingRequired = self.transactionPool.forgerRequired()
            if forgingRequired == True:
                logger.info(f"Forger required")
                self.forge()

    def handleBlock(self, block: Block):
        logger.info(f"Manage the Block: {block.blockCount}")
        forger = block.forger
        blockHash = block.payload()
        signature = block.signature

        # checks all the possible validations!
        blockCountValid = self.blockchain.blockCountValid(block)

        lastBlockHashValid = self.blockchain.lastBlockHashValid(block)
        forgerValid = self.blockchain.forgerValid(block)
        transactionValid = self.blockchain.transactionValid(block.transactions)

        signatureValid = Wallet.signatureValid(blockHash, signature, forger)

        if not blockCountValid:
            # ask to peers their state of the blockchain
            logger.info("Request the updated version of the Blockchain")
            self.requestChain()

        if lastBlockHashValid and forgerValid and transactionValid and signatureValid:

            # Add the block to the Blockchain
            self.blockchain.addBlock(block)

            self.transactionPool.removeFromPool(block.transactions)

            # broadcast the block message
            message = MessageBlock(self.p2p.socketConnector, MessageType.BLOCK.name, block)
            encodedMessage = BeezUtils.encode(message)
            self.p2p.broadcast(encodedMessage)

    def requestChain(self):
        # The node will send a message to request the updated Blockchain
        message = Message(self.p2p.socketConnector, MessageType.BLOCKCHAINREQUEST.name)
        encodedMessage = BeezUtils.encode(message)

        self.p2p.broadcast(encodedMessage)
        
    def requestKeeper(self):
        # The node will send a message to request the updated Keeper
        message = Message(self.p2p.socketConnector, MessageType.KEEPERREQUEST.name)
        encodedMessage = BeezUtils.encode(message)

        self.p2p.broadcast(encodedMessage)


    def handleChallengeTX(self, challengeTx: ChallengeTX):

        challenge: Challenge = challengeTx.challenge
        
        logger.info(f"Manage the challenge ID: {challenge.id}")

        data = challengeTx.payload()
        signature = challengeTx.signature
        signaturePublicKey = challengeTx.senderPublicKey

        # # # is valid?
        signatureValid = Wallet.signatureValid(
            data, signature, signaturePublicKey)

        # already exist in the beezKeeper
        challengeTransactionExist = self.transactionPool.challengeExists(challengeTx)

        # already exist in the Blockchain
        transactionInBlock = self.blockchain.transactionExist(challengeTx)

        if not challengeTransactionExist and not transactionInBlock and signatureValid:
            # logger.info(f"add to the Transaction Pool!!!")
            self.transactionPool.addTransaction(challengeTx)
            # Propagate the transaction to other peers
            message = MessageChallengeTransation(self.p2p.socketConnector, MessageType.CHALLENGE.name, challengeTx)

            encodedMessage = BeezUtils.encode(message)
            self.p2p.broadcast(encodedMessage)

            # check if is time to forge a new Block
            forgingRequired = self.transactionPool.forgerRequired()
            if forgingRequired == True:
                logger.info(f"Forger required")
                self.forge()

        

            # logger.info(f"challenge function: {challengeTx.challenge.sharedFunction.__doc__}")

            # sharedfunction = challengeTx.challenge.sharedFunction
            # logger.info(f"challenge function: {type(sharedfunction)}")
            # result = sharedfunction(2,3)

            # logger.info(f"result: {result}")


    def forge(self):
        logger.info(f"Forger called")
        # Elect the next forger
        forger = self.blockchain.nextForger()

        forgerString = str(forger).strip()
        thisWalletString = str(self.wallet.publicKeyString()).strip()

        if forgerString == thisWalletString:
            logger.info(f"I'm the next forger")

            # mint the new Block
            block = self.blockchain.mintBlock(self.transactionPool.transactions, self.wallet)

            # clean the transaction pool
            self.transactionPool.removeFromPool(block.transactions)

            # broadcast the block to the network and the current state of the ChallengeKeeper!!!!
            message = MessageBlock(self.p2p.socketConnector, MessageType.BLOCK.name, block)
            encodedMessage = BeezUtils.encode(message)
            self.p2p.broadcast(encodedMessage)
            
        else:
            logger.info(f"I'm not the forger")  

    def handleBlockchainRequest(self, requestingNode: BeezNode):
        # send the updated version of the blockchain to the node that made the request
        message = MessageBlockchain(self.p2p.socketConnector, MessageType.BLOCKCHAIN.name, self.blockchain)
        encodedMessage = BeezUtils.encode(message)
        self.p2p.send(requestingNode, encodedMessage)
        
    def handleBlockchain(self, blockchain: Blockchain):
        # sync blockchain between peers in the network
        logger.info(f"Iterate on the blockchain until to sync the local blockchain with the received one")
        localBlockchainCopy = copy.deepcopy(self.blockchain)
        localBlockCount = len(localBlockchainCopy.blocks)
        receivedChainBlockCount = len(blockchain.blocks)

        if localBlockCount <= receivedChainBlockCount:
            for blockNumber, block in enumerate(blockchain.blocks):
                # we are interested only on blocks that are not in our blockchain
                if blockNumber >= localBlockCount:
                    localBlockchainCopy.addBlock(block)
                     # Update the current version of the in-memory AccountStateModel and BeezKeeper
                    self.blockchain.accountStateModel = block.header.accountStateModel
                    self.blockchain.beezKeeper = block.header.beezKeeper

                    self.transactionPool.removeFromPool(block.transactions)
            self.blockchain = localBlockchainCopy

        

    