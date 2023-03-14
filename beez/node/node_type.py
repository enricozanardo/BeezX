"""Beez blockchain - node types."""

from enum import Enum


class NodeType(Enum):
    """
    Define the types of nodes in the beez blockchain network

    SEED: Seed nodes as managing nodes to orchestrate peer discovery and DAM scheduling
    STORAGE: Storage nodes to store DAM data and blockchain ledger
    """
    SEED = "seed"
    STORAGE = "storage"
    