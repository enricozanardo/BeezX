from __future__ import annotations
from typing import TYPE_CHECKING, List, Dict

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
    
