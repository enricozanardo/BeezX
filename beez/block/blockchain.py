"""Beez Blockchain - blockchain."""

from __future__ import annotations
from typing import TYPE_CHECKING, List, cast, Optional

from loguru import logger

from whoosh.fields import Schema, TEXT, KEYWORD, ID  # type: ignore
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

    def __init__(self, index=True):
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
        self.genesis_public_key = GenesisPublicKey().pub_key
        self.block_count = -1
        self.in_memory_blocks: List[Block] = []

        self.append_genesis(Block.genesis(), index)

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

    def _deserialize(self, serialized_blockchain, index=True):
        """Deserialize the blockchain and return a blockchain object."""
        # delete all blocks
        if index:
            self.blocks_index.delete_document("type", "BL")
        # add the blocks
        for block in serialized_blockchain["blocks"]:
            if block["blockCount"] == 0:
                self._append_block(
                    Block.deserialize(block, index), index=index, genesis=True
                )
            else:
                self._append_block(
                    Block.deserialize(block, index), index=index, genesis=False
                )
        self.account_state_model = AccountStateModel.deserialize(
            serialized_blockchain["accountStateModel"]["balances"], index
        )
        self.pos = ProofOfStake.deserialize(serialized_blockchain["pos"], index)
        self.beez_keeper = BeezKeeper.deserialize(serialized_blockchain["beezKeeper"])
        self.genesis_public_key = serialized_blockchain["genesisPublicKey"]
        return self

    @staticmethod
    def deserialize(serialized_blockchain, index=True):
        """Public deserialize class method."""
        return Blockchain(index=index)._deserialize(  # pylint: disable=protected-access
            serialized_blockchain, index=index
        )

    def blocks_from_index(self):
        """Returning all the blocks from the current state."""
        blocks = []
        block_docs = self.blocks_index.query(query="BL", fields=["type"], highlight=True)
        for doc in block_docs:
            blocks.append(Block.deserialize(doc["block_serialized"], index=False))
        blocks = sorted(blocks, key=lambda block: block.block_count)
        return blocks

    def blocks(self):
        """Returning all the blocks from the current state."""
        blocks = self.in_memory_blocks
        blocks = sorted(blocks, key=lambda block: block.block_count)
        return blocks

    def to_json(self):
        """Returning the blockchain in json format."""
        json_blockchain = {}
        json_blocks = []
        for block in self.blocks():
            json_blocks.append(block.to_json())
        json_blockchain["blocks"] = json_blocks

        return json_blockchain

    def append_genesis(self, block: Block, index=True):
        """Append the first block, genesis, to the blockchain."""
        if len(self.blocks_index.query("BL", ["type"])) == 0:
            header = Header(self.beez_keeper, self.account_state_model)
            block.header = header
            self._append_block(block, genesis=True, index=index)

    def _append_block(self, block: Block, genesis=False, index=True):
        """Append a block to the blockchain state. Should only be used internally."""
        if genesis or (
            len(self.blocks()) > 0 and block.block_count > self.blocks()[-1].block_count
        ):
            self.block_count += 1
            if index:
                before_index_block_count = len(self.blocks_from_index())
                while len(self.blocks_from_index()) == before_index_block_count:
                    self.blocks_index.index_documents(
                        [
                            {
                                "id": str(block.block_count),
                                "type": "BL",
                                "block_serialized": str(block.serialize()),
                            }
                        ]
                    )
            self.in_memory_blocks.append(block)

    def add_block(self, block: Block):
        """Prepare the appending of a new block by executing its corresponding transactions."""
        latest_block = self.blocks()[-1]
        if (
            latest_block.block_count < block.block_count
            and BeezUtils.hash(latest_block.payload()).hexdigest() == block.last_hash
        ):
            self.execute_transactions(block.transactions)
            self._append_block(block)

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
            sender = transaction.sender_address
            receiver = transaction.receiver_address
            if sender == receiver:
                amount: int = transaction.amount
                self.pos.update(sender, amount)
                self.account_state_model.update_balance(sender, -amount)

        # case of Challenge transaction [involve beezKeeper]
        elif transaction.transaction_type == TransactionType.CHALLENGE.name:
            logger.info("CHALLENGE")
            # cast the kind of transaction
            challenge_transaction: ChallengeTX = cast(ChallengeTX, transaction)
            sender = challenge_transaction.sender_address
            receiver = transaction.receiver_address
            if sender == receiver:
                # Check with the challenge Keeeper
                challenge: Challenge = challenge_transaction.challenge
                challenge_exists = self.beez_keeper.challege_exists(challenge.identifier)
                logger.info(f"challengeExists: {challenge_exists}")

                if not challenge_exists:
                    # Update the challenge to the beezKeeper and keep store the
                    # tokens to the keeper!
                    self.beez_keeper.set(challenge)

                logger.info(
                    f"beezKeeper challenges {len(self.beez_keeper.challanges().items())}"
                )

                # Update the balance of the sender!
                amount = challenge_transaction.amount
                self.account_state_model.update_balance(sender, -amount)

        else:
            # case of [TRANSACTION]
            sender = transaction.sender_address
            receiver = transaction.receiver_address
            tx_amount: int = transaction.amount
            # first update the sender balance
            self.account_state_model.update_balance(sender, -tx_amount)
            # second update the receiver balance
            self.account_state_model.update_balance(receiver, tx_amount)

    def transaction_exist(self, transaction: Transaction):
        """Check if a given transaction exists in the current blockchain state."""
        # TODO: Find a better solution to check if a transaction already exist into the blockchain!
        response = []
        for block in self.blocks():
            all_tx_hash = list(map(lambda x: x.identifier, block.transactions))
            response.append(BeezUtils.tx_binary_search(all_tx_hash, transaction.identifier))
        return any(response)


    def next_forger(self) -> Optional[str]:
        """Returns the forger for of the next block."""
        latest_blockhash = BeezUtils.hash(self.blocks()[-1].payload()).hexdigest()
        next_forger = self.pos.forger(latest_blockhash)

        return next_forger

    def mint_block(
        self, transction_from_pool: List[Transaction], forger_wallet: Wallet
    ) -> Block:
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
            self.block_count + 1,
        )

        self._append_block(new_block)

        return new_block

    def get_covered_transactionset(
        self, transactions_from_pool: List[Transaction]
    ) -> List[Transaction]:
        """Returns the subset of covered transactions from all transactions in
        the current transaction pool state."""
        covered_transactions: list[Transaction] = []
        added_transaction_ids: list[str] = []
        for transaction in transactions_from_pool:
            if (
                self.transaction_covered(transaction)
                and transaction.identifier not in added_transaction_ids
            ):
                covered_transactions.append(transaction)
                # to make sure duplicates will be not added to the block twice
                added_transaction_ids.append(transaction.identifier)
            else:
                logger.info(
                    f"""This transaction {transaction.identifier} is not covered
                    [no enogh tokes ({transaction.amount})] or already added to covered
                    transactions."""
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

        sender_balance = self.account_state_model.get_balance(
            transaction.sender_address
        )

        if sender_balance >= transaction.amount:
            return True
        return False

    def transaction_covered_inclusive_pool_transactions(
        self,
        transaction: Transaction,
        pool_transactions: List[Transaction]
    ):
        """
        Check if a transaction is covered also keeping the transactions within the
        transaction pool in mind.
        """
        if transaction.transaction_type == TransactionType.EXCHANGE.name:
            return True
        sender_balance = self.account_state_model.get_balance(
            transaction.sender_address
        )
        sender_outgoing_from_pool = 0
        for pool_transaction in pool_transactions:
            if pool_transaction.sender_address == transaction.sender_address:
                sender_outgoing_from_pool += transaction.amount
        return sender_balance >= sender_outgoing_from_pool + transaction.amount


    def blockcount_valid(self, block: Block):
        """Returns wheter a given block could be the next block based on its block count."""
        if self.blocks()[-1].block_count == block.block_count - 1:
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
        proposed_block_forger = str(block.forger_address).strip()

        if BeezUtils.address_from_public_key(forger_public_key) == proposed_block_forger:
            return True
        return False

    def transaction_valid(self, transactions: List[Transaction]):
        """Checks if a the covered transactions of a list of transactions are valid."""
        covered_transactions = self.get_covered_transactionset(transactions)
        # if the lenght are equal than nodes are not cheating
        if len(covered_transactions) == len(transactions):
            return True
        return False
