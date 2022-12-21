"""Beez blockchain - proof of stake."""
from __future__ import annotations
from typing import TYPE_CHECKING, List, Optional, cast

from whoosh.fields import Schema, TEXT, KEYWORD, ID, NUMERIC  # type: ignore
from beez.consensus.lot import Lot
from beez.beez_utils import BeezUtils
from beez.keys.genesis_public_key import GenesisPublicKey
from beez.wallet.wallet import Wallet


if TYPE_CHECKING:
    from beez.types import Stake, PublicKeyString


class ProofOfStake:
    """
    keeps track of the stakes of each account
    """

    def __init__(self, add_genesis=True):
        self.stake_index = PosModelEngine.get_engine(
            Schema(
                id=ID(stored=True),
                type=KEYWORD(stored=True),
                account_id=TEXT(stored=True),
                stake=NUMERIC(stored=True),
            )
        )
        if add_genesis:
            self.set_genesis_node_stake()

    def serialize(self):
        """Serialize the PoS object to json format."""
        stake_state = {}
        stake_docs = self.stake_index.query(
            query="STAKE", fields=["type"], highlight=True
        )
        for doc in stake_docs:
            stake_state[doc["account_id"]] = doc["stake"]
        return stake_state

    def _deserialize(
        self, serialized_stakers, index=True
    ):  # pylint: disable=unused-argument
        """Load PoS object from json serialization."""
        for staker, stake in serialized_stakers.items():
            self.update(staker, stake)

    @staticmethod
    def deserialize(serialized_stakers, index=True):
        """Returns a new PoS object from a json serialization."""
        pos = ProofOfStake(add_genesis=False)
        pos._deserialize(serialized_stakers, index)  # pylint: disable=protected-access
        return pos

    def set_genesis_node_stake(self):
        """Sets the state of the genesis node."""
        genesis_wallet = Wallet()
        genesis_wallet.from_pem(GenesisPublicKey().priv_key)
        self.update(genesis_wallet.public_key_string(), 1)

    def stakers(self) -> list[str]:
        """Returns the stakers public keys."""
        staker_public_keys = []
        stake_docs = self.stake_index.query(
            query="STAKE", fields=["type"], highlight=True
        )
        for doc in stake_docs:
            staker_public_keys.append(doc["account_id"])
        return staker_public_keys

    def update(
        self, public_key_string: PublicKeyString, stake: Stake
    ):
        """Updates the stake of the given public key by stake."""
        key_id = BeezUtils.hash(
            public_key_string.replace("'", "").replace("\n", "")
        ).hexdigest()
        if (
            len(self.stake_index.query(query=key_id, fields=["id"], highlight=True))
            == 0
        ):
            self.stake_index.index_documents(
                [
                    {
                        "id": key_id,
                        "type": "STAKE",
                        "account_id": public_key_string,
                        "stake": stake,
                    }
                ]
            )
        else:
            old_stake = self.get(public_key_string)
            self.stake_index.delete_document("id", key_id)
            self.stake_index.index_documents(
                [
                    {
                        "id": key_id,
                        "type": "STAKE",
                        "account_id": public_key_string,
                        "stake": old_stake + stake,
                    }
                ]
            )

    def get(self, identifier) -> "Stake":
        """Returns the stake of the given public key."""
        key_id = BeezUtils.hash(
            identifier.replace("'", "").replace("\n", "")
        ).hexdigest()
        if len(self.stake_index.query(query=key_id, fields=["id"], highlight=True)) == 0:
            self.update(id, 0)
        return cast(
            "Stake",
            int(
                self.stake_index.query(query=key_id, fields=["id"], highlight=True)[
                    0
                ]["stake"]
            ),
        )

    def validator_lots(self, seed: str) -> List[Lot]:
        "Returns the lots of all validators."
        lots: List[Lot] = []
        for validator in self.stakers():
            for stake in range(self.get(validator)):
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
