from beez.transaction.Transaction import Transaction
from beez.transaction.TransactionType import TransactionType
from beez.wallet.Wallet import Wallet


def test_transaction():
    AliceWallet = Wallet()
    BobWallet = Wallet()

    senderWalletAddress = AliceWallet.address
    receiverWalletAddress = BobWallet.address
    amount = 10
    type = TransactionType.TRANSFER
      
    tx = Transaction(senderWalletAddress, receiverWalletAddress, amount, type)

    assert tx.type == TransactionType.TRANSFER