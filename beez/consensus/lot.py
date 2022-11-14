"""Beez blockchain - lot."""

from __future__ import annotations
from typing import TYPE_CHECKING
from beez.beez_utils import BeezUtils

if TYPE_CHECKING:
    from beez.types import PublicKeyString, Stake


class Lot:  # pylint: disable=too-few-public-methods
    """
    Randomly select a Peer that will become the Forger of a pool of Transactions

    publicKeyString: The publicKeyString of the node that wants to become a forger
    iteration: correspond on the numner of tokens that are staked by the node
    lastBlockHash: needed to be sure for witch block the forger can add the next Block
    """

    def __init__(self, public_key_string: PublicKeyString, iteration: Stake, last_block_hash: str):
        self.public_key_string = public_key_string
        self.iteration = iteration
        self.last_block_hash = last_block_hash

    def lottery_hash(self):
        """Returning the lots corresponding hash."""
        hash_data = self.public_key_string + self.last_block_hash
        for _ in range(self.iteration):
            hash_data = BeezUtils.hash(hash_data).hexdigest()

        return hash_data
