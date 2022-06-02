from __future__ import annotations
from typing import TYPE_CHECKING, List, Dict
import threading
from loguru import logger
import time

if TYPE_CHECKING:
    from beez.Types import PublicKeyString

class AccountStateModel():
    """
    The account state model keeps the states of the balances of the wallets in the Blockchain.
    Every time that a block is added to the Blockchain, the ASM will update the wallet balances based
    on the transactions accured.
    """
    def __init__(self):
        #TODO: move to a stored version!

        # collect all the account's publicKeyString
        self.accounts: List[PublicKeyString] = []
        # collect all the balaces of each publicKey
        self.balances: Dict[PublicKeyString:int] = {}

    def start(self):
        # start node threads... 
        statusThread = threading.Thread(target=self.status, args={})
        statusThread.start()

    def status(self):
         while True:
            logger.info(f"Account State Model Status {len(self.balances.items())}")
            for key, value in self.balances.items():
                
                walletPublicKey : PublicKeyString = key
                balance: int = value
                
                logger.info(f"Wallet: {walletPublicKey} balance: {str(balance)}")

            # challengeStatusMessage = self.challengeStatusMessage()
            # # Broadcast the message
            # self.socketCommunication.broadcast(challengeStatusMessage)

            time.sleep(5)

    def addAccount(self, publicKeyString: PublicKeyString):
        if not publicKeyString in self.accounts:
            self.accounts.append(publicKeyString)
            self.balances[publicKeyString] = 0
    
    def getBalance(self, publicKeyString: PublicKeyString):
        if publicKeyString not in self.accounts:
            self.addAccount(publicKeyString)
        return self.balances[publicKeyString]

    def updateBalance(self, publicKeyString: PublicKeyString, amount: int):
        if publicKeyString is not self.accounts:
            self.addAccount(publicKeyString)
        self.balances[publicKeyString] += amount
    
