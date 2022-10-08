"""The nodes API to get and post information from and to the Beez blockchain."""
from __future__ import annotations
import os
from typing import TYPE_CHECKING
from flask_classful import FlaskView, route
from flask import Flask, jsonify, request
from waitress import serve
from loguru import logger
from whoosh.fields import Schema, TEXT, KEYWORD, ID
from dotenv import load_dotenv
from beez.beez_utils import BeezUtils

from beez.index.IndexEngine import (
    TxIndexEngine,
    TxpIndexEngine,
    BlockIndexEngine,
)

load_dotenv()  # load .env

NODE_API_PORT = os.environ.get("NODE_API_PORT", default=8176)

if TYPE_CHECKING:
    from beez.node.BeezNode import BeezNode
    from beez.Types import Address
    from beez.transaction.Transaction import Transaction
    from beez.transaction.ChallengeTX import ChallengeTX

BEEZ_NODE = None


class NodeAPI(FlaskView):
    """NodeAPI class which represents the HTTP communication interface."""
    def __init__(self):
        self.app = Flask(__name__)  # create the Flask application
        # for testing index

    def start(self, node_ip: Address, port=None):
        """Starting the nodes api."""
        logger.info(f"Node API started at {node_ip}:{NODE_API_PORT}")
        # register the application to routes
        NodeAPI.register(self.app, route_base="/")
        serve(self.app, host=node_ip, port=port if port else NODE_API_PORT)
        # self.app.run(host=nodeIP, port=NODE_API_PORT)

    # find a way to use the properties of the node in the nodeAPI
    def inject_node(self, incjected_node: BeezNode):
        """Inject the node object of this Blockchain instance and make it
        available for the endpoints."""
        global BEEZ_NODE    # pylint: disable=global-statement
        BEEZ_NODE = incjected_node

    @route("/txpindex", methods=["GET"])
    def txpindex(self):
        """Returns the current state of the transaction pool"""
        logger.info("Fetching indexed transactionpool transactions")
        fields_to_search = ["id", "type", "txp_encoded"]

        for query in ["TXP"]:
            print(f"Query:: {query}")
            print(
                "\t",
                TxpIndexEngine.get_engine(
                    Schema(
                        id=ID(stored=True),
                        type=KEYWORD(stored=True),
                        txp_encoded=TEXT(stored=True),
                    )
                ).query(query, fields_to_search, highlight=True),
            )
            print("-" * 70)

        txp_index_str = str(
            TxpIndexEngine.get_engine(
                Schema(
                    id=ID(stored=True),
                    type=KEYWORD(stored=True),
                    txp_encoded=TEXT(stored=True),
                )
            ).query(query, fields_to_search, highlight=True)
        )

        return txp_index_str, 200

    @route("/txindex", methods=["GET"])
    def txindex(self):
        """Returns the current state of the transactions."""
        logger.info("Fetching indexed transaction")
        fields_to_search = ["id", "type", "tx_encoded"]

        for query in ["TX"]:
            print(f"Query:: {query}")
            print(
                "\t",
                TxIndexEngine.get_engine(
                    Schema(
                        id=ID(stored=True),
                        type=KEYWORD(stored=True),
                        tx_encoded=TEXT(stored=True),
                    )
                ).query(query, fields_to_search, highlight=True),
            )
            print("-" * 70)

        tx_index_str = str(
            TxIndexEngine.get_engine(
                Schema(
                    id=ID(stored=True),
                    type=KEYWORD(stored=True),
                    tx_encoded=TEXT(stored=True),
                )
            ).query(query, fields_to_search, highlight=True)
        )

        return tx_index_str, 200

    @route("/blockindex", methods=["GET"])
    def blockindex(self):
        """Returns the current state of the blocks."""
        logger.info("Checking indexed blocks")
        fields_to_search = ["id", "type", "block_serialized"]

        for query in ["BL"]:
            print(f"Query:: {query}")
            print(
                "\t",
                BlockIndexEngine.get_engine(
                    Schema(
                        id=ID(stored=True),
                        type=KEYWORD(stored=True),
                        block_encoded=TEXT(stored=True),
                    )
                ).query(query, fields_to_search, highlight=True),
            )
            print("-" * 70)

        block_index_str = str(
            BlockIndexEngine.get_engine(
                Schema(
                    id=ID(stored=True),
                    type=KEYWORD(stored=True),
                    block_encoded=TEXT(stored=True),
                )
            ).query(query, fields_to_search, highlight=True)
        )

        return block_index_str, 200

    @route("/info", methods=["GET"])
    def info(self):
        """Returns general information about the Beez blockchain."""
        logger.info("Provide some info about the Blockchain")
        return "This is Beez Blockchain!. 🦾 🐝 🐝 🐝 🦾", 200

    @route("/transaction", methods=["POST"])
    def transaction(self):
        """Post a transaction to the blockchain."""
        values = request.get_json()  # we aspect to receive json objects!

        if not "transaction" in values:
            return "Missing transaction value", 400

        transaction: Transaction = BeezUtils.decode(values["transaction"])

        # manage the transaction on the Blockchain
        BEEZ_NODE.handleTransaction(transaction)

        response = {"message": "Received transaction"}

        return jsonify(response), 201

    @route("/challenge", methods=["POST"])
    def challenge(self):
        """Post a challenge to the blockchain."""
        values = request.get_json()  # we aspect to receive json objects!

        if not "challenge" in values:
            return "Missing challenge value", 400

        transaction: ChallengeTX = BeezUtils.decode(values["challenge"])

        # manage the transaction on the Blockchain
        BEEZ_NODE.handleChallengeTX(transaction)

        response = {"message": "Received challenge"}

        return jsonify(response), 201

    @route("/transactionpool", methods=["GET"])
    def transaction_pool(self):
        """Returns the current state of the in-memory transaction pool"""
        # Implement this
        logger.info(
            "Send all the transactions that are on the transaction pool"
        )
        transactions = {}

        # logger.info(f"Transactions: {node.transactionPool.transactions}")

        for idx, transaction in enumerate(
            BEEZ_NODE.transactionPool.transactions
        ):
            logger.info(f"Transaction: {idx} : {transaction.id}")
            transactions[idx] = transaction.toJson()

        # logger.info(f"Transactions to Json: {transactions}")

        return jsonify(transactions), 200

    # @route("/challenges", methods=['GET'])
    # def challenges(self):
    #     # Implement this
    #     logger.info(
    #         f"Send all the challenges that are on the BeezKeeper")

    #     json_challenges = {}

    #     # json_challenges = json.dumps(BEEZ_NODE.beezKeeper.challenges)

    #     challenges = BEEZ_NODE.blockchain.beezKeeper.challenges

    #     for challengeID, challengeTx in challenges.items():
    #         cTx : ChallengeTX = challengeTx

    #         # logger.info(f"{cTx.toJson()}")
    #         json_challenges[challengeID] = cTx.toJson()

    #     # logger.info(f"Challenges: {BEEZ_NODE.beezKeeper.challenges}")

    #     return jsonify(json_challenges), 200

    @route("/blockchain", methods=["GET"])
    def blockchain(self):
        """Returns the state of the in-memory blockchain."""
        logger.info("Blockchain called...")
        return BEEZ_NODE.blockchain.toJson(), 200
