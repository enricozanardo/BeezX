# from time import sleep
# from loguru import logger

# import os
# from dotenv import load_dotenv
import requests
# import pycurl
import os
import pathlib

import sys
sys.path.insert(0, "/Users/lukashubl/tmp/BeezX/")


from beez.transaction.transaction import Transaction
from beez.transaction.transaction_type import TransactionType
from beez.wallet.wallet import Wallet
from beez.node.beez_node import BeezNode
from beez.beez_utils import BeezUtils
from beez.types import PublicKeyString, WalletAddress

# load_dotenv()  # load .env

# NODE_API_PORT = os.environ.get("NODE_API_PORT", default=8176)
# URI = os.environ.get("FIRST_SERVER_IP", default="192.168.1.61")


def upload_file():
    
    currentPath = pathlib.Path().resolve()

    alice_private_key_path = "/Users/lukashubl/tmp/BeezX/beez/keys/alicePrivateKey.pem"

    alice_wallet = Wallet()
    alice_wallet.from_key(alice_private_key_path)

    asset_upload_transaction = alice_wallet.create_transaction(
        BeezUtils.address_from_public_key(alice_wallet.public_key_string()), 0, TransactionType.DAMUPLOAD.name
    )

    package = {'transaction': BeezUtils.encode(asset_upload_transaction)}



    dfile = open("/Users/lukashubl/tmp/BeezX/tests/test.png", mode="rb")
    url = "http://127.0.0.1:5445/uploadasset"
    import json

    payload = package
    files   = [
                ('transaction', ('transaction', json.dumps(payload), 'application/json')),
                ('file', ("dam", dfile))
            ]


    test_res = requests.post(url, files = files, json={'lukas': 'test'})
    print(test_res.text)
    print(test_res)
    if test_res.ok:
        print(" File uploaded successfully ! ")
        print(test_res.text)
    else:
        print(" Please Upload again ! ")


if __name__ == "__main__":
    print('UPLAODING FILE')
    upload_file()