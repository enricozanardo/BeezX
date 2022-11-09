from __future__ import annotations
from flask_classful import FlaskView, route
from flask import Flask, jsonify, request
from waitress import serve
from loguru import logger
from typing import TYPE_CHECKING
import os
from whoosh.fields import Schema, TEXT, KEYWORD,ID
from whoosh.query import Term
from dotenv import load_dotenv
import json

from beez.index.IndexEngine import TxIndexEngine, TxpIndexEngine, BlockIndexEngine
load_dotenv()  # load .env

NODE_API_PORT = os.environ.get("NODE_API_PORT", default=8176)

if TYPE_CHECKING:
    from beez.node.BeezNode import BeezNode
    from beez.Types import Address
    from beez.transaction.Transaction import Transaction
    from beez.transaction.ChallengeTX import ChallengeTX

from beez.BeezUtils import BeezUtils
beezNode = None


class NodeAPI(FlaskView):

    def __init__(self):
        self.app = Flask(__name__) # create the Flask application
        # for testing index
    
    def start(self, nodeIP: Address, port=None):
        logger.info(f"Node API started at {nodeIP}:{NODE_API_PORT}")
        # register the application to routes
        NodeAPI.register(self.app, route_base="/")
        serve(self.app, host=nodeIP, port=port if port else NODE_API_PORT)
        # self.app.run(host=nodeIP, port=NODE_API_PORT)

    # find a way to use the properties of the node in the nodeAPI
    def injectNode(self, incjectedNode: BeezNode):
        global beezNode
        beezNode = incjectedNode

    @route("/txpindex", methods=['GET'])
    def txpindex(self):
        logger.info(f"Fetching indexed transactionpool transactions")
        fields_to_search = ["id", "type", "txp_encoded"]

        for q in ["TXP"]:
            print(f"Query:: {q}")
            print("\t", TxpIndexEngine.get_engine(Schema(id=ID(stored=True), type=KEYWORD(stored=True), txp_encoded=TEXT(stored=True))).query(q, fields_to_search, highlight=True))
            print("-"*70)

        txp_index_str = str(TxpIndexEngine.get_engine(Schema(id=ID(stored=True), type=KEYWORD(stored=True), txp_encoded=TEXT(stored=True))).query(q, fields_to_search, highlight=True))

        return txp_index_str, 200

    @route("/txindex", methods=['GET'])
    def txindex(self):
        logger.info(f"Fetching indexed transaction")
        fields_to_search = ["id", "type", "tx_encoded"]

        for q in ["TX"]:
            print(f"Query:: {q}")
            print("\t", TxIndexEngine.get_engine(Schema(id=ID(stored=True), type=KEYWORD(stored=True), tx_encoded=TEXT(stored=True))).query(q, fields_to_search, highlight=True))
            print("-"*70)

        tx_index_str = str(TxIndexEngine.get_engine(Schema(id=ID(stored=True), type=KEYWORD(stored=True), tx_encoded=TEXT(stored=True))).query(q, fields_to_search, highlight=True))

        return tx_index_str, 200

    @route("/blockindex", methods=['GET'])
    def blockindex(self):
        logger.info(f"Checking indexed blocks")
        fields_to_search = ["id", "type", "block_serialized"]

        for q in ["BL"]:
            print(f"Query:: {q}")
            print("\t", BlockIndexEngine.get_engine(Schema(id=ID(stored=True), type=KEYWORD(stored=True), block_encoded=TEXT(stored=True))).query(q, fields_to_search, highlight=True))
            print("-"*70)
        
        block_index_str = str(BlockIndexEngine.get_engine(Schema(id=ID(stored=True), type=KEYWORD(stored=True), block_encoded=TEXT(stored=True))).query(q, fields_to_search, highlight=True))

        return block_index_str, 200
    
    @route("/info", methods=['GET'])
    def info(self):
        logger.info(f"Provide some info about the Blockchain")
        return "This is Beez Blockchain!. 🦾 🐝 🐝 🐝 🦾", 200

    @route("/transaction", methods=['POST'])
    def transaction(self):
        values = request.get_json() # we aspect to receive json objects!

        if not 'transaction' in values:
            return 'Missing transaction value', 400

        tx: Transaction = BeezUtils.decode(values['transaction'])

        # manage the transaction on the Blockchain
        beezNode.handleTransaction(tx)

        response = {'message': 'Received transaction'}

        return jsonify(response), 201


    @route("/challenge", methods=['POST'])
    def challenge(self):
        values = request.get_json() # we aspect to receive json objects!

        if not 'challenge' in values:
            return 'Missing challenge value', 400

        tx: ChallengeTX = BeezUtils.decode(values['challenge'])

        # manage the transaction on the Blockchain
        beezNode.handleChallengeTX(tx)

        response = {'message': 'Received challenge'}

        return jsonify(response), 201

    
    @route("/transactionpool", methods=['GET'])
    def transactionPool(self):
        # Implement this
        logger.info(
            f"Send all the transactions that are on the transaction pool")
        transactions = {}

        # logger.info(f"Transactions: {node.transactionPool.transactions}")

        for idx, tx in enumerate(beezNode.transactionPool.transactions):
            logger.info(f"Transaction: {idx} : {tx.id}")
            transactions[idx] = tx.toJson()

        # logger.info(f"Transactions to Json: {transactions}")

        return jsonify(transactions), 200
    
    # @route("/challenges", methods=['GET'])
    # def challenges(self):
    #     # Implement this
    #     logger.info(
    #         f"Send all the challenges that are on the BeezKeeper")
        
    #     json_challenges = {}

    #     # json_challenges = json.dumps(beezNode.beezKeeper.challenges) 
    
    #     challenges = beezNode.blockchain.beezKeeper.challenges

    #     for challengeID, challengeTx in challenges.items():
    #         cTx : ChallengeTX = challengeTx

    #         # logger.info(f"{cTx.toJson()}")
    #         json_challenges[challengeID] = cTx.toJson()

    #     # logger.info(f"Challenges: {beezNode.beezKeeper.challenges}")

    #     return jsonify(json_challenges), 200
        
    @route("/blockchain", methods=['GET'])
    def blockchain(self):
        # TODO: Implement this
        logger.info(f"Blockchain called...")
        return beezNode.blockchain.toJson(), 200

