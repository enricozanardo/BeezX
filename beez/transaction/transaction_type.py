"""Beez blockchain - transaction types"""

from enum import Enum


class TransactionType(Enum):
    """
    Define the types of transaction that will accur into the Blockchain

    EXCHANGE: The main wallet (owner of the tokens) will release some tokens to a wallet
    TRANSFER: Classical transaction between wallets inside the blockchain.
    STAKE: A node send a stake transaction to stake some tokens to increase the opportunity
    to become a Forger
    CHALLENGE: A node send a request to peers to collaborate to solve a given function
    ACCEPT: A node decide to accept the challenge
    UPDATE: The Keeper update the state of the Challenge to the Blockchain
    """

    EXCHANGE = "exchange"
    TRANSFER = "transfer"
    STAKE = "stake"
    CHALLENGE = "challenge"
    ACCEPT = "accept"
    UPDATE = "update"
