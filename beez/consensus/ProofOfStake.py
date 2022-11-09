from __future__ import annotations
from optparse import Option
from typing import TYPE_CHECKING, Dict, List
from loguru import logger
import pathlib

if TYPE_CHECKING:
    from beez.Types import Stake, PublicKeyString

from beez.consensus.Lot import Lot
from beez.BeezUtils import BeezUtils
from beez.keys.GenesisPublicKey import GenesisPublicKey
from beez.index.IndexEngine import PosModelEngine
from whoosh.fields import Schema, TEXT, NUMERIC,ID, KEYWORD


class ProofOfStake():
    """
    keeps track of the stakes of each account
    """

    def __init__(self):
        self.stakers_index = PosModelEngine.get_engine(Schema(id=ID(stored=True), type=KEYWORD(stored=True), public_key_string=TEXT(stored=True), stake=NUMERIC(stored=True)))
        self.setGenesisNodeStake()

    def serialize(self):
        stakers: dict[str, int] = {}
        for stakers_doc in self.stakers_index.query(q="STAKE", fields=["type"], highlight=True):
            stakers[stakers_doc["public_key_string"]] = stakers_doc["stake"]
        return stakers
    
    def _deserialize(self, serialized_stakers):
        # delete stakers
        self.stakers_index.delete_document("type", "STAKE")
        for staker, stake in serialized_stakers.items():
            self.update(staker, stake)

    @staticmethod
    def deserialize(serialized_stakers):
        return ProofOfStake()._deserialize(serialized_stakers)

    def setGenesisNodeStake(self):
        # currentPath = pathlib.Path().resolve()
        # logger.info(f"currentPath: {currentPath}")

        # genisisPublicKey = open(f"{currentPath}/beez/keys/genesisPublicKey.pem", 'r').read()

        genisisPublicKey = GenesisPublicKey()


        # logger.info(f"GenesisublicKey: {genisisPublicKey}")
        # give to the genesis staker 1 stake to allow him to forge the initial Block
        self.update(genisisPublicKey.pubKey, 1)

    def stakers(self):
        stakers_public_keys = []
        docs = self.stakers_index.query(q="STAKE", fields=["type"], highlight=True)
        for doc in docs:
            stakers_public_keys.append(doc["public_key_string"])
        return stakers_public_keys
        

    def update(self, publicKeyString: PublicKeyString, stake: Stake):

        id = BeezUtils.hash(publicKeyString.replace("'", "").replace("\n", "")).hexdigest()

        if len(self.stakers_index.query(q=id, fields=["id"], highlight=True)) != 0:
            old_stake = self.get(id)
            self.stakers_index.delete_document("id", id)
            self.stakers_index.index_documents([{"id": id, "type": "STAKE", "public_key_string":publicKeyString, "stake": old_stake + stake}])
        else:
            self.stakers_index.index_documents([{"id": id, "type": "STAKE", "public_key_string":publicKeyString, "stake": stake}])


    def get(self, id) -> Option[Stake]:
        if len(self.stakers_index.query(q=id, fields=["id"], highlight=True)) == 0:
            return None
        return self.stakers_index.query(q=id, fields=["id"], highlight=True)[0]["stake"]

    
    def validatorLots(self, seed: str) -> List[Lot]:
        lots : List[Lot] = []
        for validator in self.stakers():
            for stake in range(self.get(BeezUtils.hash(validator.replace("'", "").replace("\n", "")).hexdigest())):
                lots.append(Lot(validator, stake + 1, seed))
        return lots

    def winnerLot(self, lots: List[Lot], seed: str) -> Lot:
        winnerLot: Lot = None
        leastOffSet = None
        # get the integer representation of a give hash
        referenceHashIntValue = int(BeezUtils.hash(seed).hexdigest(), 16)
        # fin the nearest lot
        for lot in lots:
            lotIntValue = int(lot.lotteryHash(), 16)
            offset = abs(lotIntValue-referenceHashIntValue)
            if leastOffSet is None or offset < leastOffSet:
                leastOffSet = offset
                winnerLot = lot

        return winnerLot 


    def forger(self, lastBlockHash: str):
        lots = self.validatorLots(lastBlockHash)
        winnerLot: Lot = self.winnerLot(lots, lastBlockHash)

        return winnerLot.publicKeyString