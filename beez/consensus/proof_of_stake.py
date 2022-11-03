"""Beez blockchain - proof of stake."""
from __future__ import annotations
from loguru import logger
from typing import TYPE_CHECKING, List, Optional, cast

from whoosh.fields import Schema, TEXT, NUMERIC, ID, KEYWORD    # type: ignore
from beez.consensus.Lot import Lot
from beez.beez_utils import BeezUtils
from beez.keys.genesis_public_key import GenesisPublicKey
from beez.index.index_engine import PosModelEngine

if TYPE_CHECKING:
    from beez.Types import Stake, PublicKeyString


class ProofOfStake:
    """
    keeps track of the stakes of each account
    """

    def __init__(self):
        self.stakers_index = PosModelEngine.get_engine(
            Schema(
                id=ID(stored=True),
                type=KEYWORD(stored=True),
                public_key_string=TEXT(stored=True),
                stake=NUMERIC(stored=True),
            )
        )
        self.set_genesis_node_stake()

    def serialize(self):
        """Serialize the PoS object to json format."""
        stakers: dict[str, int] = {}
        for stakers_doc in self.stakers_index.query(query="STAKE", fields=["type"], highlight=True):
            stakers[stakers_doc["public_key_string"]] = stakers_doc["stake"]
        return stakers

    def _deserialize(self, serialized_stakers):
        """Load PoS object from json serialization."""
        # delete stakers
        self.stakers_index.delete_document("type", "STAKE")
        for staker, stake in serialized_stakers.items():
            self.update(staker, stake)

    @staticmethod
    def deserialize(serialized_stakers):
        """Returns a new PoS object from a json serialization."""
        pos = ProofOfStake()
        pos._deserialize(serialized_stakers)  # pylint: disable=protected-access
        return pos

    def set_genesis_node_stake(self):
        """Sets the state of the genesis node."""
        # currentPath = pathlib.Path().resolve()
        # logger.info(f"currentPath: {currentPath}")

        # genisisPublicKey = open(f"{currentPath}/beez/keys/genesisPublicKey.pem", 'r').read()

        genesis_public_key = GenesisPublicKey()

        # logger.info(f"GenesisublicKey: {genisisPublicKey}")
        # give to the genesis staker 1 stake to allow him to forge the initial Block
        self.update(genesis_public_key.pub_key, 1)

    def stakers(self):
        """Returns the stakers public keys."""
        stakers_public_keys = []
        docs = self.stakers_index.query(query="STAKE", fields=["type"], highlight=True)
        for doc in docs:
            stakers_public_keys.append(doc["public_key_string"])
        return stakers_public_keys

    def update(self, public_key_string: PublicKeyString, stake: Stake):
        """Updates the stake of the given public key by stake."""

        identifier = BeezUtils.hash(
            public_key_string.replace("'", "").replace("\n", "")
        ).hexdigest()
        if len(self.stakers_index.query(query=identifier, fields=["id"], highlight=True)) != 0:
            old_stake = self.get(identifier)
            self.stakers_index.delete_document("id", identifier)
            self.stakers_index.index_documents(
                [
                    {
                        "id": identifier,
                        "type": "STAKE",
                        "public_key_string": public_key_string,
                        "stake": old_stake + stake,
                    }
                ]
            )
        else:
            self.stakers_index.index_documents(
                [
                    {
                        "id": identifier,
                        "type": "STAKE",
                        "public_key_string": public_key_string,
                        "stake": stake,
                    }
                ]
            )

    def get(self, identifier) -> "Stake":
        """Returns the stake of the given public key."""
        if len(self.stakers_index.query(query=identifier, fields=["id"], highlight=True)) == 0:
            return cast("Stake", 0)
        return self.stakers_index.query(query=identifier, fields=["id"], highlight=True)[0]["stake"]

    def validator_lots(self, seed: str) -> List[Lot]:
        "Returns the lots of all validators."
        lots: List[Lot] = []
        for validator in self.stakers():
            for stake in range(
                self.get(BeezUtils.hash(validator.replace("'", "").replace("\n", "")).hexdigest())
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
