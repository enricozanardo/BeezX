from __future__ import annotations
import time
from typing import TYPE_CHECKING, Dict, List
import os
from dotenv import load_dotenv
import socket
from loguru import logger
import GPUtil
import copy


from beez.Types import ChallengeID, PublicKeyString
from beez.challenge.ChallengeState import ChallengeState

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
from beez.socket.Message import Message
from beez.transaction.TransactionType import TransactionType
from beez.socket.MessageChallenge import MessageChallenge
from beez.challenge.ChallengeType import ChallengeType

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


    def handleChallengeClosed(self, closedChallenge: Challenge):
        logger.info(f"Manage the Closed Challenge")
        # remove the challenge from the Keeper
        self.blockchain.beezKeeper.delete(closedChallenge.id)
        # clean the transactionpool
        transactionInPool = len(self.transactionPool.transactions)
        logger.info(f"number of transactions in pool:  {transactionInPool}")

        for tx in self.transactionPool.transactions:
            logger.info(f"transaction in pool:  {tx.id} -- {tx.type}")


        logger.info(f"Challenges in Keeper???? {len(self.blockchain.beezKeeper.challenges.items())}")

        # Create a TX to REWARD the workers in the Blockchain
        challengeTX : ChallengeTX = self.wallet.createChallengeTransaction(closedChallenge.reward, TransactionType.CLOSED.name, closedChallenge)
        self.handleClosedChallengeTX(challengeTX)



    def handleChallengeOpen(self, challenge: Challenge):
        logger.info(f"Manage the challenge {challenge.id} -- STATE: {challenge.state}")

        # localChallenge = self.blockchain.beezKeeper.get(challenge.id)

        #TODO: remove doubles!!! add the worker to the list

        walletPubKey = str(self.wallet.publicKeyString()).strip()
        
        if walletPubKey in challenge.workers.keys():
            # Worker already present, increment the counter
            count = challenge.workers[walletPubKey] 
            challenge.workers[walletPubKey] = count + 1
        else:
            # add the new worker
            challenge.workers[walletPubKey] = 1
            

        logger.info(f"Challenge Iterations: {challenge.iteration}")

        if challenge.state == ChallengeState.OPEN.name:
            logger.info(f"Start the calculus!!!! only if the challenge is {ChallengeState.OPEN.name}")

            localChallenge = self.blockchain.beezKeeper.get(challenge.id)
            localChallengeCounter = localChallenge.counter

            incomingChallengeCounter = challenge.counter

            logger.info(f"localChallengeCounter = {localChallengeCounter}")
            logger.info(f"incomingChallengeCounter = {localChallengeCounter}")

            logger.info(f"incomingChallengeCounter {incomingChallengeCounter} -- iteration  {challenge.iteration}")

            if incomingChallengeCounter >= localChallengeCounter and incomingChallengeCounter <= challenge.iteration:
                logger.info(f"work on challenge = {challenge.id}")
                logger.info(f"challenge type {challenge.challengeType}")

                logger.info(f"challenge type {ChallengeType.CALCULUS.name}")

                # updatedChallenge = None

                if challenge.challengeType == ChallengeType.CALCULUS.name:

                    logger.warning(f"Do a Calculus!!!")
                    updatedChallenge = self.blockchain.beezKeeper.workOnChallenge(challenge)

                elif challenge.challengeType == ChallengeType.IRIS.name:
                    logger.warning(f"Do a IRIS MODEL TRAINING!!!")
                    updatedChallenge = self.blockchain.beezKeeper.workOnMLChallenge(challenge)

                if updatedChallenge is not None:
                    logger.info(f"A New Updated Challenge received back!!!")

                    if updatedChallenge.state == ChallengeState.OPEN.name:
                        logger.info(f"Challenge still open.. propagate it")

                        time.sleep(2)

                        message = MessageChallenge(self.p2p.socketConnector, MessageType.CHALLENGEOPEN.name, updatedChallenge)
                        encodedMessage = BeezUtils.encode(message)
                        self.p2p.broadcast(encodedMessage)

                    # elif updatedChallenge.state == ChallengeState.CLOSED.name:
                    #     logger.warning(f"Challenge closed.. create the Final TX")
                    #     logger.error(f"Final Result: {updatedChallenge.result}")

                    #     message = MessageChallenge(self.p2p.socketConnector, MessageType.CHALLENGECLOSED.name, updatedChallenge)
                    #     encodedMessage = BeezUtils.encode(message)
                    #     self.p2p.broadcast(encodedMessage)
            
            else:

                logger.info(f"skip or close challenge version: {challenge.id} -- {challenge.state}") 

                if challenge.state == ChallengeState.CLOSED.name:
                    logger.info(f"Challenge already closed... DO NOT DO SPAM the NETWORK!!")

                else: 
                    logger.warning(f"Close the Challenge! create the Final TX")

                    challenge.state == ChallengeState.CLOSED.name

                    # Update the localstete of the challenge
                    self.blockchain.beezKeeper.set(challenge)

                    localChallenge = self.blockchain.beezKeeper.get(challenge.id)                    
                    incomingResult = challenge.result

                    logger.error(f"Final Result: {incomingResult}")

                    message = MessageChallenge(self.p2p.socketConnector, MessageType.CHALLENGECLOSED.name, localChallenge)
                    encodedMessage = BeezUtils.encode(message)
                    self.p2p.broadcast(encodedMessage)
                

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

            if transaction.type != TransactionType.REWARD.name:
                # Bradcast new transactions and not the ones that are autogenerated...
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


            # For Peers
            # check the BeezKeeper
            challenges : Dict[ChallengeID : Challenge] = self.blockchain.beezKeeper.challenges
            challengesNumber = len(challenges.items())
            logger.info(f"Peer challenges.... {challengesNumber}")

            if challengesNumber > 0:
                self.acceptChallenges(challenges)
            

            # broadcast the block message
            message = MessageBlock(self.p2p.socketConnector, MessageType.BLOCK.name, block)
            encodedMessage = BeezUtils.encode(message)
            self.p2p.broadcast(encodedMessage)


    def acceptChallenges(self, challenges : Dict[ChallengeID : Challenge]):
        for idx, ch in challenges.items():
            challenge : Challenge = ch
            # logger.info(f"do something with the challenge: {idx}")
            # logger.info(f"do something with the challenge STATE: {challenge.state}")

            # get the localchallenge
            localChallenge = self.blockchain.beezKeeper.get(challenge.id)
            
            if not localChallenge:
                # add the challenge to the Keeper
                self.blockchain.beezKeeper.set(challenge)

            if challenge.state == ChallengeState.CREATED.name:
                # logger.info(f"Challenge {challenge.state}: Update challenge to OPEN!!!")

                if localChallenge.state == challenge.state:
                    # logger.info(f"Update the local Challenge {challenge.state} to {ChallengeState.OPEN.name}")
                    localChallenge.state = ChallengeState.OPEN.name

                    self.blockchain.beezKeeper.set(localChallenge)

                    message = MessageChallenge(self.p2p.socketConnector, MessageType.CHALLENGEOPEN.name, challenge)
                    encodedMessage = BeezUtils.encode(message)
                    self.p2p.broadcast(encodedMessage)


    def requestChain(self):
        # The node will send a message to request the updated Blockchain
        message = Message(self.p2p.socketConnector, MessageType.BLOCKCHAINREQUEST.name)
        encodedMessage = BeezUtils.encode(message)

        self.p2p.broadcast(encodedMessage)


    def handleClosedChallengeTX(self, challengeTx: ChallengeTX):
        challenge: Challenge = challengeTx.challenge
        
        logger.warning(f"Handle Closed Transaction: [To reward the workers....] {challenge.id}")

        data = challengeTx.payload()
        signature = challengeTx.signature
        signaturePublicKey = challengeTx.senderPublicKey

        # # # is valid?
        signatureValid = Wallet.signatureValid(
            data, signature, signaturePublicKey)

        # already exist in the transaction pool
        challengeTransactionExist = self.transactionPool.challengeExists(challengeTx)

        # already exist in the beezKeeper
        challengeBeezKeeperExist = self.blockchain.beezKeeper.challegeExists(challengeTx.challenge.id)

        logger.info(f"challengeBeezKeeperExist: {challengeBeezKeeperExist}")
        logger.info(f"challengeTx.challenge.id: {challengeTx.challenge.id}")
        logger.info(f"challengeTx ID: {challengeTx.id}")

        # already exist in the Blockchain
        transactionInBlock = self.blockchain.transactionExist(challengeTx)

        if not challengeTransactionExist and not transactionInBlock and not challengeBeezKeeperExist and signatureValid:
            # logger.info(f"add to the Transaction Pool!!!")
            self.transactionPool.addTransaction(challengeTx)

            # check if is time to forge a new Block
            forgingRequired = self.transactionPool.forgerRequired()
            if forgingRequired == True:
                logger.info(f"Forger required")
                self.forge()

            logger.info(f"########## Reward starts ###########")
            self.handleRewards(challenge.workers, challenge.reward)


    def handleRewards(self, workers: Dict[PublicKeyString: int], totalReward: int):
        logger.info(f"Pay workers!!!")
        # iterate to workers generate Rewarding transactions!!
        logger.info(f"workers??? {len(workers.items())}")

        # TODO: calculate the reward!
        totalCount = sum(workers.values())
       
        for pubKeyString, count in workers.items():
            publicKeyString : PublicKeyString = pubKeyString

            reward = int(totalReward / totalCount * count)
            rewardTX : Transaction = self.wallet.createTransaction(publicKeyString, reward, TransactionType.REWARD.name)
            self.handleTransaction(rewardTX)


    def handleChallengeTX(self, challengeTx: ChallengeTX):

        challenge: Challenge = challengeTx.challenge
        
        logger.info(f"Manage the challenge ID: {challenge.id}")

        data = challengeTx.payload()
        signature = challengeTx.signature
        signaturePublicKey = challengeTx.senderPublicKey

        # # # is valid?
        signatureValid = Wallet.signatureValid(
            data, signature, signaturePublicKey)

        # already exist in the transaction pool
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

            # For Forger
            # check the BeezKeeper
            # time.sleep(5)

            # challenges : Dict[ChallengeID : Challenge] = self.blockchain.beezKeeper.challenges
            # challengesNumber = len(challenges.items())
            # logger.info(f"Forger challenges.... {challengesNumber}")

            # if challengesNumber > 0:
            #     self.acceptChallenges(challenges)

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

                    self.transactionPool.removeFromPool(block.transactions)
                                    
            self.blockchain = localBlockchainCopy

        

    