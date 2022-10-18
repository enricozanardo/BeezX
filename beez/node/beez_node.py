"""Beez blockchain - beez node."""

from __future__ import annotations
from typing import TYPE_CHECKING
import os
import socket
from dotenv import load_dotenv
from loguru import logger
import GPUtil   # type: ignore

from beez.beez_utils import BeezUtils
from beez.wallet.wallet import Wallet
from beez.socket.socket_communication import SocketCommunication
from beez.api.node_api import NodeAPI
from beez.transaction.transaction_pool import TransactionPool
from beez.socket.message_transaction import MessageTransation
from beez.socket.message_type import MessageType
from beez.socket.message_challenge_transaction import MessageChallengeTransation
from beez.socket.message_challenge import MessageChallenge
from beez.block.blockchain import Blockchain
from beez.socket.message_block import MessageBlock
from beez.socket.message_blockchain import MessageBlockchain
from beez.socket.message import Message

if TYPE_CHECKING:
    from beez.types import Address
    from beez.transaction.transaction import Transaction
    from beez.transaction.challenge_tx import ChallengeTX
    from beez.challenge.challenge import Challenge
    from beez.block.block import Block

load_dotenv()  # load .env
P_2_P_PORT = int(os.getenv("P_2_P_PORT", 8122))     # pylint: disable=invalid-envvar-default


class BeezNode:     # pylint: disable=too-many-instance-attributes
    """Beez Node - represents the core blockchain node."""

    def __init__(self, key=None, port=None) -> None:
        self.api = None
        self.ip_address = self.get_ip()
        self.port = int(P_2_P_PORT)
        self.wallet = Wallet()
        self.transaction_pool = TransactionPool()
        self.gpus = GPUtil.getGPUs()
        self.cpus = os.cpu_count()
        self.blockchain = Blockchain()
        self.p2p = SocketCommunication(self.ip_address, port if port else self.port)

        if key is not None:
            self.wallet.from_key(key)

    def get_ip(self) -> Address:
        """Return IP of node."""
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            sock.connect(("8.8.8.8", 53))
            node_address: Address = sock.getsockname()[0]
            logger.info(f"Node IP: {node_address}")

            return node_address

    def start_p2p(self):
        """Starts the p2p communication thread."""
        self.p2p.start_socket_communication(self)

    def start_api(self, port=None):
        """Starts the nodes API."""
        self.api = NodeAPI()
        # Inject Node to NodeAPI
        self.api.inject_node(self)
        self.api.start(self.ip_address, port)

    # Manage requests that come from the NodeAPI
    def handle_transaction(self, transaction: Transaction):
        """Handles an incomming transaction."""
        logger.info(f"Manage the transaction ID: {transaction.identifier}")

        data = transaction.payload()
        signature = transaction.signature
        signature_public_key = transaction.sender_public_key

        # # # is valid?
        signature_valid = Wallet.signature_valid(data, signature, signature_public_key)

        # already exist in the transaction pool
        transaction_exist = self.transaction_pool.transaction_exists(transaction)

        # already exist in the Blockchain
        transaction_in_block = self.blockchain.transaction_exist(transaction)

        if not transaction_exist and not transaction_in_block and signature_valid:
            self.transaction_pool.add_transaction(transaction)

            # Propagate the transaction to other peers
            message = MessageTransation(
                self.p2p.socket_connector, MessageType.TRANSACTION, transaction
            )

            encoded_message = BeezUtils.encode(message)

            self.p2p.broadcast(encoded_message)

            # check if is time to forge a new Block
            forging_required = self.transaction_pool.forger_required()
            if forging_required:
                logger.info("Forger required")
                self.forge()

    def handle_block(self, block: Block):
        """Handles incomming block."""
        forger = block.forger
        block_hash = block.payload()
        signature = block.signature

        # checks all the possible validations!
        block_count_valid = self.blockchain.blockcount_valid(block)

        last_block_hash_valid = self.blockchain.last_blockhash_valid(block)
        forger_valid = self.blockchain.forger_valid(block)
        transaction_valid = self.blockchain.transaction_valid(block.transactions)

        signature_valid = Wallet.signature_valid(block_hash, signature, forger)

        logger.info(f"What is wrong? blockCountValid: {block_count_valid}")

        if not block_count_valid:
            # ask to peers their state of the blockchain
            self.request_chain()

        if last_block_hash_valid and forger_valid and transaction_valid and signature_valid:

            # Add the block to the Blockchain
            self.blockchain.add_block(block)

            self.transaction_pool.remove_from_pool(block.transactions)

            # broadcast the block message
            message = MessageBlock(
                self.p2p.socket_connector, MessageType.BLOCK, block.serialize()
            )
            encoded_message = BeezUtils.encode(message)
            self.p2p.broadcast(encoded_message)


    def request_chain(self):
        """Requests the peer nodes to get their version of the blockchain."""
        # The node will send a message to request the updated Blockchain
        message = Message(self.p2p.socket_connector, MessageType.BLOCKCHAINREQUEST)
        encoded_message = BeezUtils.encode(message)

        self.p2p.broadcast(encoded_message)

    def handle_challenge_update(self, challenge: Challenge):
        """Handles an challenge update message."""
        message = MessageChallenge(
            self.p2p.socket_connector, MessageType.CHALLENGEUPDATE, challenge
        )
        encoded_message = BeezUtils.encode(message)
        self.p2p.broadcast(encoded_message)

    def handle_challenge_tx(self, challenge_tx: ChallengeTX):
        """Handles an incomming challenge transaction."""
        challenge: Challenge = challenge_tx.challenge
        logger.info(f"Manage the challenge ID: {challenge.identifier}")

        data = challenge_tx.payload()
        signature = challenge_tx.signature
        signature_public_key = challenge_tx.sender_public_key

        # # # is valid?
        signature_valid = Wallet.signature_valid(data, signature, signature_public_key)

        # already exist in the beezKeeper
        challenge_transaction_exist = self.transaction_pool.challenge_exists(challenge_tx)

        # already exist in the Blockchain
        transaction_in_block = self.blockchain.transaction_exist(challenge_tx)

        if not challenge_transaction_exist and not transaction_in_block and signature_valid:
            # logger.info(f"add to the Transaction Pool!!!")
            self.transaction_pool.add_transaction(challenge_tx)
            # Propagate the transaction to other peers
            message = MessageChallengeTransation(
                self.p2p.socket_connector, MessageType.CHALLENGE, challenge_tx
            )
            encoded_message = BeezUtils.encode(message)
            self.p2p.broadcast(encoded_message)

            # check if is time to forge a new Block
            forging_required = self.transaction_pool.forger_required()
            if forging_required:
                logger.info("Forger required")
                self.forge()

    def forge(self):
        """Forging a new block."""
        logger.info("Forger called")
        # Elect the next forger
        forger = self.blockchain.next_forger()

        forger_string = str(forger).strip()
        this_wallet_string = str(self.wallet.public_key_string()).strip()

        if forger_string == this_wallet_string:
            logger.info("I'm the next forger")

            # mint the new Block
            block = self.blockchain.mint_block(self.transaction_pool.transactions(), self.wallet)

            # clean the transaction pool
            self.transaction_pool.remove_from_pool(block.transactions)

            # Update the current version of the in-memory AccountStateModel and BeezKeeper
            logger.info("GO!!!!!!")
            self.blockchain.account_state_model = block.header.account_state_model
            self.blockchain.beez_keeper = block.header.beez_keeper

            # broadcast the block to the network and the current state of the ChallengeKeeper!!!!
            message = MessageBlock(
                self.p2p.socket_connector, MessageType.BLOCK, block.serialize()
            )
            encoded_message = BeezUtils.encode(message)
            self.p2p.broadcast(encoded_message)

        else:
            logger.info("I'm not the forger")

    def handle_blockchain_request(self, requesting_node: BeezNode):
        """Handles request from other node to get this version of the blockchain."""
        # send the updated version of the blockchain to the node that made the request
        message = MessageBlockchain(
            self.p2p.socket_connector, MessageType.BLOCKCHAIN, self.blockchain.serialize()
        )
        encoded_message = BeezUtils.encode(message)
        self.p2p.send(requesting_node, encoded_message)

    def handle_blockchain(self, blockchain: Blockchain):
        """Handles an incomming blockchain message."""
        # sync blockchain between peers in the network
        logger.info(
            "Iterate on the blockchain until to sync the local blockchain with the received one"
        )
        # localBlockchainCopy = copy.deepcopy(self.blockchain)
        # localBlockCount = len(localBlockchainCopy.blocks())
        local_block_count = len(self.blockchain.blocks())
        received_chain_block_count = len(blockchain.blocks())

        if local_block_count <= received_chain_block_count:
            for block_number, block in enumerate(blockchain.blocks()):
                # we are interested only on blocks that are not in our blockchain
                if block_number >= local_block_count:
                    self.blockchain.append_block(block)
                    logger.warning("Here is the problem?")
                    # Update the current version of the in-memory AccountStateModel and BeezKeeper
                    self.blockchain.account_state_model = block.header.accountStateModel
                    self.blockchain.beez_keeper = block.header.beezKeeper

                    self.transaction_pool.remove_from_pool(block.transactions)
