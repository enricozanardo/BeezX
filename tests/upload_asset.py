# from time import sleep
# from loguru import logger

# import os
# from dotenv import load_dotenv
import requests
# import pycurl
import os
import pathlib

# from beez.transaction.transaction import Transaction
from beez.transaction.transaction_type import TransactionType
from beez.wallet.wallet import Wallet
# from beez.node.beez_node import BeezNode
from beez.beez_utils import BeezUtils
# from beez.types import PublicKeyString, WalletAddress

# load_dotenv()  # load .env

# NODE_API_PORT = os.environ.get("NODE_API_PORT", default=8176)
# URI = os.environ.get("FIRST_SERVER_IP", default="192.168.1.61")


def upload_file():
    
    # currentPath = pathlib.Path().resolve()

    # alice_private_key_path = f"{currentPath}/beez/keys/alicePrivateKey.pem"

    # alice_wallet = Wallet()
    # alice_wallet.from_key(alice_private_key_path)

    # asset_upload_transaction = alice_wallet.create_transaction(
    #     BeezUtils.address_from_public_key(bob_wallet.public_key_string()), 50, TransactionType.TRANSFER.name
    # )


    # # Initialize pycurl
    # c = pycurl.Curl()
    # c.setopt(pycurl.URL, "http://127.0.0.1:5445/uploadasset")
    # c.setopt(pycurl.UPLOAD, 1)

    # # Two versions with the same semantics here, but the filereader version
    # # is useful when you have to process the data which is read before returning
    # c.setopt(pycurl.READFUNCTION, open("test.png", 'rb').read)

    # # Set size of file to be uploaded.
    # filesize = os.path.getsize("test.png")
    # c.setopt(pycurl.INFILESIZE, filesize)

    # # Start transfer
    # print('Uploading file %s to url %s' % ("test.png", "http://127.0.0.1:5445/uploadasset"))
    # c.perform()
    # c.close()

    dfile = open("test.png", mode="rb")
    url = "http://127.0.0.1:5445/uploadasset"
    # test = requests.get("http://127.0.0.1:5446/connectednodes")
    # print(test)
    test_res = requests.post(url, files = {"file": dfile})
    print(test_res)
    if test_res.ok:
        print(" File uploaded successfully ! ")
        print(test_res.text)
    else:
        print(" Please Upload again ! ")


# def postTransaction(senderWallet: Wallet, receiverWallet: Wallet, amount, txType: TransactionType):

#     tx = senderWallet.create_transaction(receiverWallet.public_key_string(), amount, txType) 
#     url = f"http://{URI}:{NODE_API_PORT}/transaction"
#     logger.info(url)

#     package = {'transaction': BeezUtils.encode(tx)}
#     request = requests.post(url, json=package)

#     logger.info(package)

#     logger.info(f"ok?: {request}")


# def test_exchange_transaction():

#     # Import the genesis private key
#     currentPath = pathlib.Path().resolve()

#     genesisPrivateKeyPath = f"{currentPath}/beez/keys/genesisPrivateKey.pem"
#     alicePrivateKeyPath = f"{currentPath}/beez/keys/alicePrivateKey.pem"

#     GenesisWallet = Wallet()
#     GenesisWallet.from_key(genesisPrivateKeyPath)
#     AliceWallet = Wallet()
#     AliceWallet.from_key(alicePrivateKeyPath)
    
#     amountEx = 100

#     typeExchange = TransactionType.EXCHANGE.name

#     postTransaction(GenesisWallet, AliceWallet, amountEx, typeExchange)
   
#     # assert beezNode.ip == localIP
#     assert 5 == 5

if __name__ == "__main__":
    print('UPLAODING FILE')
    upload_file()