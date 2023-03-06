"""Beez blockchain - beez node."""

from __future__ import annotations
from typing import TYPE_CHECKING, Optional
import os
from dotenv import load_dotenv
from loguru import logger
import GPUtil  # type: ignore


from whoosh.fields import Schema, TEXT, KEYWORD, ID  # type: ignore

from beez.node.basic_node import BasicNode
from beez.wallet.wallet import Wallet
from beez.socket.socket_communication.socket_communication import SocketCommunication
from beez.api.node_api import NodeAPI
from beez.transaction.transaction_pool import TransactionPool
from beez.socket.messages.message_transaction import MessageTransation
from beez.socket.messages.message_type import MessageType
from beez.socket.messages.message_challenge_transaction import MessageChallengeTransation
from beez.socket.messages.message_challenge import MessageChallenge
from beez.socket.messages.message_address_registration import MessageAddressRegistration
from beez.block.blockchain import Blockchain
from beez.socket.messages.message_block import MessageBlock
from beez.socket.messages.message_blockchain import MessageBlockchain
from beez.socket.messages.message import Message
from beez.beez_utils import BeezUtils
from beez.index.index_engine import AddressIndexEngine

if TYPE_CHECKING:
    from beez.transaction.transaction import Transaction
    from beez.transaction.challenge_tx import ChallengeTX
    from beez.challenge.challenge import Challenge
    from beez.block.block import Block

load_dotenv()  # load .env
P_2_P_PORT = int(os.getenv("P_2_P_PORT", 8122))  # pylint: disable=invalid-envvar-default


class BeezNode(BasicNode):  # pylint: disable=too-many-instance-attributes
    """Beez Node - represents the core blockchain node."""

    def __init__(self, key=None, port=None) -> None:
        BasicNode.__init__(
            self, key=key, port=port, communication_protocol=SocketCommunication
        )
        self.api = None
        self.transaction_pool = TransactionPool()
        self.gpus = GPUtil.getGPUs()
        self.cpus = os.cpu_count()
        self.blockchain = Blockchain()
        self.pending_blockchain_request = False
        self.pending_block_handling = False
        self.address_index = AddressIndexEngine.get_engine(
            Schema(
                id=ID(stored=True),
                type=KEYWORD(stored=True),
                public_key_pem=TEXT(stored=True),
                address=TEXT(stored=True),
            )
        )
        self.address_buffer = {}

        # eigene addresse registrieren
        self.handle_address_registration(self.wallet.public_key_string())

    def start_api(self, port=None):
        """Starts the nodes API."""
        self.api = NodeAPI()
        # Inject Node to NodeAPI
        self.api.inject_node(self)
        self.api.start(self.ip_address, port)

    def start_p2p(self):
        """Starts the p2p communication thread."""
        self.blockchain.in_memory_blocks = self.blockchain.blocks_from_index()
        if (
            len(self.blockchain.blocks()) > 0
            and self.blockchain.blocks()[-1].header is not None
        ):
            self.blockchain.account_state_model = self.blockchain.blocks()[
                -1
            ].header.account_state_model
            self.blockchain.block_count = self.blockchain.blocks()[-1].block_count
            self.blockchain.beez_keeper = self.blockchain.blocks()[-1].header.beez_keeper
        self.p2p.start_socket_communication(self)

    def get_registered_addresses(self) -> list[dict[str, str]]:
        """Returns a dict of address to public-key-hex mappings."""
        registrations = self.address_index.query(
            "ADDR", ["type", "public_key_pem", "address"], highlight=True
        )
        return registrations

    def get_public_key_from_address(self, address: str) -> Optional[str]:
        """Returns the corresponding public_key_pem for a given address or None"""
        registrations = self.address_index.query(
            "ADDR", ["type", "public_key_pem", "address"], highlight=True
        )
        public_key = None
        for doc in registrations:
            if doc["address"] == address:
                public_key = doc["public_key_pem"]
        return public_key

    # TODO: address request

    def handle_address_registration(self, public_key_pem: str, broadcast=True) -> str:
        """Handles an incomming address to public-key registration."""
        beez_address = BeezUtils.address_from_public_key(public_key_pem)
        # 1. check if mapping already in index
        public_key = self.get_public_key_from_address(beez_address)
        # 2. add to index if not already exists
        if not public_key and beez_address not in self.address_buffer:
            self.address_buffer[beez_address] = public_key_pem
            self.address_index.index_documents(
                [
                    {
                        "id": public_key_pem,
                        "type": "ADDR",
                        "public_key_pem": public_key_pem,
                        "address": beez_address,
                    }
                ]
            )
            # 3. broadcast between nodes
            if broadcast:
                address_registration_message = MessageAddressRegistration(
                    self.p2p.socket_connector,
                    MessageType.ADDRESSREGISTRATION,
                    public_key_pem,
                )
                encoded_message = BeezUtils.encode(address_registration_message)
                self.p2p.broadcast(encoded_message)
            self.address_buffer.pop(beez_address, None)
        return beez_address

    # Manage requests that come from the NodeAPI
    def handle_transaction(self, transaction: Transaction):
        """Handles an incomming transaction."""
        logger.info(f"Manage the transaction ID: {transaction.identifier}")

        data = transaction.payload()
        signature = transaction.signature
        signature_address = transaction.sender_address

        # # # is valid?
        # get public_key from address
        public_key = self.get_public_key_from_address(signature_address)
        signature_valid = Wallet.signature_valid(data, signature, public_key)

        # already exist in the transaction pool
        transaction_exist = self.transaction_pool.transaction_exists(transaction)

        # transaction covered
        transaction_covered = (
            self.blockchain.transaction_covered_inclusive_pool_transactions(
                transaction, self.transaction_pool.transactions()
            )
        )

        # already exist in the Blockchain
        # TODO: fix problem that deserialization of all blocks to check if tx exists
        transaction_in_block = self.blockchain.transaction_exist(transaction)

        if (
            not transaction_exist
            and not transaction_in_block
            and signature_valid
            and transaction_covered
        ):
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
        if not self.pending_block_handling and not self.pending_blockchain_request:
            self.pending_block_handling = True

            forger_address = block.forger_address
            forger_public_key = self.get_public_key_from_address(forger_address)
            block_hash = block.payload()
            signature = block.signature

            # checks all the possible validations!
            block_count_valid = self.blockchain.blockcount_valid(block)

            last_block_hash_valid = self.blockchain.last_blockhash_valid(block)
            forger_valid = self.blockchain.forger_valid(block)
            transaction_valid = self.blockchain.transaction_valid(block.transactions)

            signature_valid = Wallet.signature_valid(
                block_hash, signature, forger_public_key
            )

            logger.info(f"What is wrong? blockCountValid: {block_count_valid}")
            logger.info(f"What is wrong? last_block_hash_valid: {last_block_hash_valid}")
            logger.info(f"What is wrong? forger_valid: {forger_valid}")
            logger.info(f"What is wrong? transaction_valid: {transaction_valid}")
            logger.info(f"What is wrong? signature_valid: {signature_valid}")

            if (
                not block_count_valid
                and self.blockchain.blocks()[-1].block_count < block.block_count - 1
            ):
                # ask to peers their state of the blockchain
                self.request_chain()

            if (
                last_block_hash_valid
                and forger_valid
                and transaction_valid
                and signature_valid
            ):
                logger.info("About to add new block")

                # Add the block to the Blockchain
                self.blockchain.add_block(block)

                self.transaction_pool.remove_from_pool(block.transactions)

                # broadcast the block message
                message = MessageBlock(
                    self.p2p.socket_connector, MessageType.BLOCK, block.serialize()
                )
                encoded_message = BeezUtils.encode(message)
                self.p2p.broadcast(encoded_message)

            self.pending_block_handling = False

    def request_chain(self):
        """Requests the peer nodes to get their version of the blockchain."""
        if not self.pending_blockchain_request:
            # The node will send a message to request the updated Blockchain
            message = Message(self.p2p.socket_connector, MessageType.BLOCKCHAINREQUEST)
            encoded_message = BeezUtils.encode(message)

            self.pending_blockchain_request = True
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
        signature_address = challenge_tx.sender_address
        signature_public_key = self.get_public_key_from_address(signature_address)

        # # # is valid?
        signature_valid = Wallet.signature_valid(data, signature, signature_public_key)

        # already exist in the beezKeeper
        challenge_transaction_exist = self.transaction_pool.challenge_exists(challenge_tx)

        # already exist in the Blockchain
        transaction_in_block = self.blockchain.transaction_exist(challenge_tx)

        if (
            not challenge_transaction_exist
            and not transaction_in_block
            and signature_valid
        ):
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
            block = self.blockchain.mint_block(
                self.transaction_pool.transactions(), self.wallet
            )

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
        if self.pending_blockchain_request:
            # sync blockchain between peers in the network
            logger.info(
                "Iterate on the blockchain until to sync the local blockchain with the received one"
            )

            local_block_count = self.blockchain.blocks()[-1].block_count
            received_chain_block_count = blockchain.blocks()[-1].block_count

            if local_block_count < received_chain_block_count:
                for _, block in enumerate(blockchain.blocks()):
                    # we are interested only on blocks that are not in our blockchain
                    if block.block_count > local_block_count:
                        self.blockchain._append_block(  # pylint: disable=protected-access
                            block
                        )
                        logger.warning("Here is the problem?")
                        # Update the current version of the in-memory AccountStateModel
                        # and BeezKeeper
                        if block.header:
                            self.blockchain.account_state_model = (
                                block.header.account_state_model
                            )
                            self.blockchain.beez_keeper = block.header.beez_keeper

                        self.transaction_pool.remove_from_pool(block.transactions)
                    else:
                        # we have to clean up txpool
                        self.transaction_pool.remove_from_pool(block.transactions)
            self.pending_blockchain_request = False
