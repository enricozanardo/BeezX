"""Beez Blockchain - blockchain."""

from __future__ import annotations
from typing import TYPE_CHECKING, List

from loguru import logger

from whoosh.fields import Schema, TEXT, KEYWORD, ID
from beez.block.block import Block
from beez.beez_utils import BeezUtils
from beez.state.account_state_model import AccountStateModel
from beez.consensus.proof_of_stake import ProofOfStake
from beez.transaction.transaction_type import TransactionType
from beez.transaction.challenge_tx import ChallengeTX
from beez.keys.genesis_public_key import GenesisPublicKey
from beez.block.header import Header
from beez.challenge.beez_keeper import BeezKeeper
from beez.index.index_engine import BlockIndexEngine


if TYPE_CHECKING:
    from beez.transaction.transaction import Transaction
    from beez.wallet.wallet import Wallet
    from beez.challenge.challenge import Challenge


class Blockchain:
    """
    A Blockchain is a linked list of blocks
    """

    def __init__(self):
        self.blocks_index = BlockIndexEngine.get_engine(
            Schema(
                id=ID(stored=True),
                type=KEYWORD(stored=True),
                block_serialized=TEXT(stored=True),
            )
        )

        self.account_state_model = AccountStateModel()
        self.pos = ProofOfStake()
        self.beez_keeper = BeezKeeper()
        self.genesis_public_key = GenesisPublicKey()

        self.append_genesis(Block.genesis())

        # for testing...
        # self.accountStateModel.start()

    def serialize(self):
        """Serialize the blockchain to json."""
        serialized_chain = {
            "blocks": [block.serialize() for block in self.blocks()],
            "accountStateModel": self.account_state_model.serialize(),
            "pos": self.pos.serialize(),
            "beezKeeper": self.beez_keeper.serialize(),
            "genesisPublicKey": self.genesis_public_key,
        }
        return serialized_chain

    def _deserialize(self, serialized_blockchain):
        """Deserialize the blockchain and return a blockchain object."""
        # delete all blocks
        self.blocks_index.delete_document("type", "BL")
        # add the blocks
        for block in serialized_blockchain["blocks"]:
            self.append_block(Block.deserialize(block))
        self.account_state_model = AccountStateModel.deserialize(
            serialized_blockchain["accountStateModel"]["balances"]
        )
        self.pos = ProofOfStake.deserialize(serialized_blockchain["pos"])
        self.beez_keeper = BeezKeeper.deserialize(serialized_blockchain["beezKeeper"])
        self.genesis_public_key = serialized_blockchain["genesisPublicKey"]
        return self

    @staticmethod
    def deserialize(serialized_blockchain):
        """Public deserialize class method."""
        return Blockchain()._deserialize(serialized_blockchain)  # pylint: disable=protected-access

    def blocks(self):
        """Returning all the blocks from the current state."""
        blocks = []
        block_docs = self.blocks_index.query(query="BL", fields=["type"], highlight=True)
        for doc in block_docs:
            blocks.append(Block.deserialize(doc["block_serialized"], index=False))
        blocks = sorted(blocks, key=lambda block: block.blockCount)
        return blocks

    def to_json(self):
        """Returning the blockchain in json format."""
        json_blockchain = {}
        json_blocks = []
        for block in self.blocks():
            json_blocks.append(block.toJson())
        json_blockchain["blocks"] = json_blocks

        return json_blockchain

    def append_genesis(self, block: Block):
        """Append the first block, genesis, to the blockchain."""
        if len(self.blocks_index.query("BL", ["type"])) == 0:
            header = Header(self.beez_keeper, self.account_state_model)
            block.header = header
            self.append_block(block)

    def append_block(self, block: Block):
        """Append a block to the blockchain state."""
        self.blocks_index.index_documents(
            [
                {
                    "id": str(block.block_count),
                    "type": "BL",
                    "block_serialized": str(block.serialize()),
                }
            ]
        )

    def add_block(self, block: Block):
        """Prepare the appending of a new block by executing its corresponding transactions."""
        self.execute_transactions(block.transactions)
        if self.blocks()[-1].blockCount < block.block_count:
            self.append_block(block)

    def execute_transactions(self, transactions: List[Transaction]):
        """Executes a list of transactions."""
        for transaction in transactions:
            self.execute_transaction(transaction)

    def execute_transaction(self, transaction: Transaction):
        """Executes a single transaction."""
        logger.info(f"Execute transaction of type: {transaction.transaction_type}")

        # case of Stake transaction [involve POS]
        if transaction.transaction_type == TransactionType.STAKE.name:
            logger.info("STAKE")
            sender = transaction.sender_public_key
            receiver = transaction.receiver_public_key
            if sender == receiver:
                amount = transaction.amount
                self.pos.update(sender, amount)
                self.account_state_model.update_balance(sender, -amount)

        # case of Challenge transaction [involve beezKeeper]
        elif transaction.transaction_type == TransactionType.CHALLENGE.name:
            logger.info("CHALLENGE")
            # cast the kind of transaction
            challenge_transaction: ChallengeTX = transaction
            sender = challenge_transaction.sender_public_key
            receiver = transaction.receiver_public_key
            if sender == receiver:
                # Check with the challenge Keeeper
                challenge: Challenge = challenge_transaction.challenge
                challenge_exists = self.beez_keeper.challege_exists(challenge.identifier)
                logger.info(f"challengeExists: {challenge_exists}")

                if not challenge_exists:
                    # Update the challenge to the beezKeeper and keep store the
                    # tokens to the keeper!
                    self.beez_keeper.set(challenge)

                logger.info(f"beezKeeper challenges {len(self.beez_keeper.challanges().items())}")

                # Update the balance of the sender!
                amount = challenge_transaction.amount
                self.account_state_model.update_balance(sender, -amount)

        else:
            # case of [TRANSACTION]
            logger.info("OTHER")
            sender = transaction.sender_public_key
            receiver = transaction.receiver_public_key
            amount: int = transaction.amount
            # first update the sender balance
            self.account_state_model.update_balance(sender, -amount)
            # second update the receiver balance
            self.account_state_model.update_balance(receiver, amount)

    def transaction_exist(self, transaction: Transaction):
        """Check if a given transaction exists in the current blockchain state."""
        # TODO: Find a better solution to check if a transaction already exist into the blockchain!
        for block in self.blocks():
            for block_transaction in block.transactions:
                if transaction.equals(block_transaction):
                    return True
        return False

    def next_forger(self):
        """Returns the forger for of the next block."""
        latest_blockhash = BeezUtils.hash(self.blocks()[-1].payload()).hexdigest()
        next_forger = self.pos.forger(latest_blockhash)

        return next_forger

    def mint_block(self, transction_from_pool: List[Transaction], forger_wallet: Wallet) -> Block:
        """Mints a new block, appends it to the blockchain and returns it."""
        # Check that the transaction are covered
        covered_transactions = self.get_covered_transactionset(transction_from_pool)

        # check the type of transactions and do the right action
        self.execute_transactions(covered_transactions)

        # Get the updated version of the in-memory objects and create the Block Header
        header = Header(self.beez_keeper, self.account_state_model)

        logger.info(f"Header: {len(header.beez_keeper.challanges().items())}")

        # create the Block
        new_block = forger_wallet.create_block(
            header,
            covered_transactions,
            BeezUtils.hash(self.blocks()[-1].payload()).hexdigest(),
            len(self.blocks()),
        )

        self.append_block(new_block)

        return new_block

    def get_covered_transactionset(
        self, transactions_from_pool: List[Transaction]
    ) -> List[Transaction]:
        """Returns the subset of covered transactions from all transactions in
        the current transaction pool state."""
        covered_transactions: List[Transaction] = []
        for transaction in transactions_from_pool:
            if self.transaction_covered(transaction):
                covered_transactions.append(transaction)
            else:
                logger.info(
                    f"""This transaction {transaction.identifier} is not covered
                    [no enogh tokes ({transaction.amount})]"""
                )

        return covered_transactions

    def transaction_covered(self, transaction: Transaction):
        """
        check if a transaction is covered (there are enough money into the account)
        by the AccountStateModelif the transaction is coming from the Exchange we do
        not check if it covered
        """

        if transaction.transaction_type == TransactionType.EXCHANGE.name:
            # Only genesis wallet can perform an EXCHANGE transaction
            # genesisPubKeyString = str(self.genesisPubKey.pubKey).strip()
            # genesisPubKeyString = str(transaction.senderPublicKey).strip()

            # if genesisPubKeyString == genesisPubKeyString:
            #     logger.info(f"Do an EXCHANGE transfer")
            #     return True

            # return False
            return True

        sender_balance = self.account_state_model.get_balance(transaction.sender_public_key)

        if sender_balance >= transaction.amount:
            return True
        return False

    def blockcount_valid(self, block: Block):
        """Returns wheter a given block could be the next block based on its block count."""
        if self.blocks()[-1].blockCount == block.block_count - 1:
            return True
        return False

    def last_blockhash_valid(self, block: Block):
        """Returns whether the last block hash of a given block is valid in respect to
        its current blockchain state."""
        latest_blockchain_hash = BeezUtils.hash(self.blocks()[-1].payload()).hexdigest()
        if latest_blockchain_hash == block.last_hash:
            return True
        return False

    def forger_valid(self, block: Block):
        """Checks if the forger of a given block is valid."""
        forger_public_key = str(self.pos.forger(block.last_hash)).strip()
        proposed_block_forger = str(block.forger).strip()

        if forger_public_key == proposed_block_forger:
            return True
        return False

    def transaction_valid(self, transactions: List[Transaction]):
        """Checks if a the covered transactions of a list of transactions are valid."""
        covered_transactions = self.get_covered_transactionset(transactions)
        # if the lenght are equal than nodes are not cheating
        if len(covered_transactions) == len(transactions):
            return True
        return False
