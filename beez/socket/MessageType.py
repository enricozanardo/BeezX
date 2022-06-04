from enum import Enum


class MessageType(Enum):
    """
    Define the types of messages that will accepted from the peers in the network

    DISCOVERY: To find peers on the network once connected
    TRANSACTION: Broadcast transactions to other peers using P2P
    BLOCK: Broadcast block to other peers using P2P
    BLOCKCHAINREQUEST: Ask to peers about the current state of the Blockchain
    BLOCKCHAIN: Send to the requesting node a copy of the Blockchain
    CHALLENGE: Broadcast the challenge to other peers using P2P
    """
    DISCOVERY = "discovery"
    TRANSACTION = "transaction"
    BLOCK = "block"
    BLOCKCHAINREQUEST = "blockchainrequest"
    BLOCKCHAIN = "blockchain"
    CHALLENGE = "challenge"
    