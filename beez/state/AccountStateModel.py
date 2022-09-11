from __future__ import annotations
from typing import TYPE_CHECKING, Any, List, Dict
import threading
from loguru import logger
import time
from beez.BeezUtils import BeezUtils

from beez.index.IndexEngine import AccountModelEngine, BalancesModelEngine
from whoosh.fields import Schema, TEXT, NUMERIC,ID, KEYWORD

if TYPE_CHECKING:
    from beez.Types import PublicKeyString

class AccountStateModel():
    """
    The account state model keeps the states of the balances of the wallets in the Blockchain.
    Every time that a block is added to the Blockchain, the ASM will update the wallet balances based
    on the transactions accured.
    """
    def __init__(self):
        self.accounts_index_engine = AccountModelEngine.get_engine(Schema(id=ID(stored=True), type=KEYWORD(stored=True)))
        self.balance_index_engine = BalancesModelEngine.get_engine(Schema(id=ID(stored=True), type=KEYWORD(stored=True), account_id=TEXT(stored=True), balance=NUMERIC(stored=True)))

    def start(self):
        # start node threads... 
        statusThread = threading.Thread(target=self.status, args={})
        statusThread.start()

    def serialize(self) -> dict[str: Any]:
        return {"accounts": self.accounts(), "balances": self.balances()}

    @staticmethod
    def deserialize(serialized_balances, index=True):
        return AccountStateModel()._deserialize(serialized_balances, index)
    
    def _deserialize(self, serialized_balances, index=True):
        if index:
            # Remove all balances and accounts and load from serialized ones
            self.accounts_index_engine.delete_document("type", "ACCOUNT")
            self.balance_index_engine.delete_document("type", "BALANCE")
            logger.info("DESERIALIZING ACCOUNT STATE MODEL")
            for acc_id, bal in serialized_balances.items():
                self.updateBalance(acc_id, bal)
        return self

    def balances(self) -> dict[str, int]:
        balances: dict[str, int] = {}
        for balance_doc in self.balance_index_engine.query(q="BALANCE", fields=["type"], highlight=True):
            balances[balance_doc["account_id"]] = balance_doc["balance"]
        return balances

    def accounts(self) -> list[str]:
        accounts: list[str] = []
        for account_doc in self.accounts_index_engine.query(q="ACCOUNT", fields=["type"], highlight=True):
            accounts.append(account_doc["id"])
        return accounts

    def status(self):
         while True:
            logger.info(f'Account State Model Status {len(self.balance_index_engine.query(q="BALANCE", fields=["type"], highlight=True))}')

            for doc in self.balance_index_engine.query(q="BALANCE", fields=["type"], highlight=True):
                walletPublicKey : PublicKeyString = doc["account_id"]
                balance: int = doc["balance"]
                
                logger.info(f"Wallet: {walletPublicKey} balance: {str(balance)}")

            time.sleep(5)

    def addAccount(self, publicKeyString: PublicKeyString):
        id = BeezUtils.hash(publicKeyString.replace("'", "").replace("\n", "")).hexdigest()
        if len(self.accounts_index_engine.query(q=id, fields=["id"], highlight=True)) == 0:
            self.accounts_index_engine.index_documents([{"id":id, "type": "ACCOUNT"}])
            self.balance_index_engine.index_documents([{"id":id, "type": "BALANCE", "account_id": publicKeyString, "balance": 0}])
    
    def getBalance(self, publicKeyString: PublicKeyString):
        id = BeezUtils.hash(publicKeyString.replace("'", "").replace("\n", "")).hexdigest()
        if len(self.accounts_index_engine.query(q=id, fields=["id"], highlight=True)) == 0:
            self.addAccount(publicKeyString)
        return self.balance_index_engine.query(q=id, fields=["id"], highlight=True)[0]["balance"]

    def updateBalance(self, publicKeyString: PublicKeyString, amount: int):
        id = BeezUtils.hash(publicKeyString.replace("'", "").replace("\n", "")).hexdigest()
        if len(self.accounts_index_engine.query(q=id, fields=["id"], highlight=True)) == 0:
            self.addAccount(publicKeyString)

        old_balance = self.getBalance(publicKeyString)
        logger.info(f"BALANCE IS {old_balance+amount}")
        self.balance_index_engine.delete_document("id", id)
        self.balance_index_engine.index_documents([{"id": id, "type": "BALANCE", "account_id":publicKeyString, "balance": old_balance + amount}])

    
