from __future__ import annotations
from flask_classful import FlaskView, route
from flask import Flask, jsonify, request
from waitress import serve
from loguru import logger
from typing import TYPE_CHECKING
import os
from dotenv import load_dotenv

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
    
    def start(self, nodeIP: Address):
        logger.info(f"Node API started at {nodeIP}:{NODE_API_PORT}")
        # register the application to routes
        NodeAPI.register(self.app, route_base="/")
        serve(self.app, host=nodeIP, port=NODE_API_PORT)
        # self.app.run(host=nodeIP, port=NODE_API_PORT)

    # find a way to use the properties of the node in the nodeAPI
    def injectNode(self, incjectedNode: BeezNode):
        global beezNode
        beezNode = incjectedNode

    
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

