"""Beez blockchain - proof of stake."""
from __future__ import annotations
from typing import TYPE_CHECKING, List, Optional, cast

from beez.consensus.lot import Lot
from beez.beez_utils import BeezUtils
from beez.keys.genesis_public_key import GenesisPublicKey

if TYPE_CHECKING:
    from beez.types import Stake, PublicKeyString


class ProofOfStake:
    """
    keeps track of the stakes of each account
    """

    def __init__(self):
        self.stakers_state: dict[str, int] = {}
        self.set_genesis_node_stake()

    def serialize(self):
        """Serialize the PoS object to json format."""
        return self.stakers_state

    def _deserialize(self, serialized_stakers, index=True):  # pylint: disable=unused-argument
        """Load PoS object from json serialization."""
        for staker, stake in serialized_stakers.items():
            self.update(staker, stake, rewrite=True)

    @staticmethod
    def deserialize(serialized_stakers, index=True):
        """Returns a new PoS object from a json serialization."""
        pos = ProofOfStake()
        pos._deserialize(serialized_stakers, index)  # pylint: disable=protected-access
        return pos

    def set_genesis_node_stake(self):
        """Sets the state of the genesis node."""
        genesis_public_key = GenesisPublicKey()
        # give to the genesis staker 1 stake to allow him to forge the initial Block
        self.update(genesis_public_key.pub_key, 1)

    def stakers(self) -> list[str]:
        """Returns the stakers public keys."""
        return list(self.stakers_state.keys())

    def update(self, public_key_string: PublicKeyString, stake: Stake, rewrite: bool=False):
        """Updates the stake of the given public key by stake."""
        if not rewrite and public_key_string in self.stakers_state.keys():  # pylint: disable=consider-iterating-dictionary
            self.stakers_state[public_key_string] += stake
        else:
            self.stakers_state[public_key_string] = stake

    def get(self, identifier) -> "Stake":
        """Returns the stake of the given public key."""
        if identifier in self.stakers_state.keys():  # pylint: disable=consider-iterating-dictionary
            return self.stakers_state[identifier]
        return cast("Stake", 0)

    def validator_lots(self, seed: str) -> List[Lot]:
        "Returns the lots of all validators."
        lots: List[Lot] = []
        for validator in self.stakers():
            for stake in range(
                self.get(validator)
            ):
                lots.append(Lot(validator, cast("Stake", stake + 1), seed))
        return lots

    def winner_lot(self, lots: List[Lot], seed: str) -> Optional[Lot]:
        """Returns the winner lot for the next block mint."""
        winner_lot: Optional[Lot] = None
        least_offset = None
        # get the integer representation of a give hash
        reference_hash_int_value = int(BeezUtils.hash(seed).hexdigest(), 16)
        # fin the nearest lot
        for lot in lots:
            lot_int_value = int(lot.lottery_hash(), 16)
            offset = abs(lot_int_value - reference_hash_int_value)
            if least_offset is None or offset < least_offset:
                least_offset = offset
                winner_lot = lot

        return winner_lot

    def forger(self, last_block_hash: str) -> Optional[str]:
        """Returns the public key of the next forger."""
        lots = self.validator_lots(last_block_hash)
        winner_lot: Optional[Lot] = self.winner_lot(lots, last_block_hash)

        return winner_lot.public_key_string if winner_lot else None
