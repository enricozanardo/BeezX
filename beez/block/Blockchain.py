from __future__ import annotations
from typing import TYPE_CHECKING, List
import pathlib

from loguru import logger

if TYPE_CHECKING:
    from beez.transaction.Transaction import Transaction
    from beez.Types import PublicKeyString
    from beez.wallet.Wallet import Wallet

from beez.block.Block import Block
from beez.BeezUtils import BeezUtils
from beez.state.AccountStateModel import AccountStateModel
from beez.consensus.ProofOfStake import ProofOfStake
from beez.transaction.TransactionType import TransactionType
from beez.challenge.Keeper import Keeper
from beez.transaction.ChallengeTX import ChallengeTX
from beez.keys.GenesisPublicKey import GenesisPublicKey


class Blockchain():
    """
    A Blockchain is a linked list of blocks
    """
    def __init__(self):
        self.blocks: List[Block] = [Block.genesis()]
        self.accountStateModel = AccountStateModel()
        self.pos = ProofOfStake()
        self.keeper = Keeper()
        self.genesisPubKey = GenesisPublicKey()

    def toJson(self):
        jsonBlockchain = {}
        jsonBloks = []
        for block in self.blocks:
            jsonBloks.append(block.toJson())
        jsonBlockchain['blocks'] = jsonBloks

        return jsonBlockchain

    def addBlock(self, block: Block):
        self.executeTransactions(block.transactions)
        if self.blocks[-1].blockCount < block.blockCount:
            self.blocks.append(block)

    def executeTransactions(self, transactions: List[Transaction]):
        for transaction in transactions:
            self.executeTransaction(transaction)
    
    def executeTransaction(self, transaction: Transaction):
        # case of Stake transaction [involve POS]
        if transaction.type == TransactionType.STAKE.name:
            sender = transaction.senderPublicKey
            receiver = transaction.receiverPublicKey
            if sender == receiver:
                amount = transaction.amount
                self.pos.update(sender, amount)
                self.accountStateModel.updateBalance(sender, -amount)

        # case of Challenge transaction [involve Keeper]
        elif transaction.type == TransactionType.CHALLENGE.name:
            sender = transaction.senderPublicKey
            receiver = transaction.receiverPublicKey
            if sender == receiver:
                # cast the kind of transaction
                challengeTX: ChallengeTX = transaction
                # Check with the Challenge Keeper
                challengeExists = self.keeper.challegeExists(challengeTX.id)

                if not challengeExists:
                    # Add the challenge to the Keeper and keep store the tokens to the keeper!
                    self.keeper.set(challengeTX) 
                else:
                    # check the state and update
                    # Update the Keeper!
                    self.keeper.update(challengeTX.id) 

                # Update the balance of the sender!
                self.accountStateModel.updateBalance(sender, -amount)

        else:
            # case of [TRANSACTION]
            sender = transaction.senderPublicKey
            receiver = transaction.receiverPublicKey
            amount: int = transaction.amount
            # first update the sender balance
            self.accountStateModel.updateBalance(sender, -amount)
            # second update the receiver balance
            self.accountStateModel.updateBalance(receiver, amount)

        
    def transactionExist(self, transaction: Transaction):
        # TODO: Find a better solution to check if a transaction already exist into the blockchain!
        for block in self.blocks:
            for blockTransaction in block.transactions:
                if transaction.equals(blockTransaction):
                    return True
        return False

    def nextForger(self):
        lastBlockHash = BeezUtils.hash(self.blocks[-1].payload()).hexdigest()
        nextForger = self.pos.forger(lastBlockHash)

        return nextForger
    
    def mintBlock(self, transactionsFromPool: List[Transaction], forgerWallet: Wallet) -> Block:
        # Check that the transaction are covered 
        coveredTransactions = self.getCoveredTransactionSet(transactionsFromPool)

        # check the type of transactions and do the right action
        self.executeTransactions(coveredTransactions)

        # create the Block
        newBlock = forgerWallet.createBlock(coveredTransactions, BeezUtils.hash(
            self.blocks[-1].payload()).hexdigest(), len(self.blocks))

        self.blocks.append(newBlock)

        return newBlock
    
    def getCoveredTransactionSet(self, transactionsFromPool: List[Transaction]) -> List[Transaction]:
        coveredTransactions: List[Transaction] = []
        for tx in transactionsFromPool:
            if self.transactionCovered(tx):
                coveredTransactions.append(tx)
            else:
                logger.info(
                    f"This transaction {tx.id} is not covered [no enogh tokes ({tx.amount}) into account {tx.receiverPublicKey}]")

        return coveredTransactions
        
    def transactionCovered(self, transaction: Transaction):
        """
        check if a transaction is covered (there are enough money into the account) by the AccountStateModel
        if the transaction is coming from the Exchange we do not check if it covered
        """

        if transaction.type == TransactionType.EXCHANGE.name:
            # Only genesis wallet can perform an EXCHANGE transaction
            genesisPubKeyString = str(self.genesisPubKey.pubKey).strip()
            genesisPubKeyString = str(transaction.senderPublicKey).strip()

            if genesisPubKeyString == genesisPubKeyString:
                logger.info(f"Do an EXCHANGE transfer")
                return True
            
            return False

        senderBalance = self.accountStateModel.getBalance(
            transaction.senderPublicKey)

        if senderBalance >= transaction.amount:
            return True
        else:
            return False