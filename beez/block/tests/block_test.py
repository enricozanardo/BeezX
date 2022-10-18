import pytest
from beez.block.Block import Block
from typing import cast
from beez.Types import PublicKeyString


@pytest.fixture
def testblock():
    # TODO: use real block
    return Block.genesis()

def test_genesis_block():
    genesis = Block.genesis()
    assert genesis.header is None
    assert genesis.transactions == []
    assert genesis.last_hash == "Hello Beezkeepers! 🐝"
    assert genesis.forger == "BeezAuthors: Enrico Zanardo 🤙🏽 & ⭐"
    assert genesis.signature == ""
    assert genesis.block_count == 0

def test_block_creation():
    block = Block(
        None,
        [],
        "Testhash",
        cast(PublicKeyString, "BeezAuthors: Lukas Hubl 🤙🏽 & ⭐"),
        0,
    )
    block.timestamp = (
        0  # every node will start with the same genesis Block
    )

    assert block is not None


def test_serialize(testblock):
    serialization = testblock.serialize()
    assert serialization == {
        "header": "",
        "transactions": [],
        "lastHash": "Hello Beezkeepers! 🐝",
        "forger": "BeezAuthors: Enrico Zanardo 🤙🏽 & ⭐",
        "blockCount": 0,
        "timestamp": 0,
        "signature": "",
    }

def test_deserialize():
    block = Block.deserialize({
        "header": "",
        "transactions": [],
        "lastHash": "Hello Beezkeepers! 🐝",
        "forger": "BeezAuthors: Enrico Zanardo 🤙🏽 & ⭐",
        "blockCount": 0,
        "timestamp": 0,
        "signature": "",
    }, index=False)
    assert block.header is None
    assert block.transactions == []
    assert block.last_hash == "Hello Beezkeepers! 🐝"
    assert block.forger == "BeezAuthors: Enrico Zanardo 🤙🏽 & ⭐"
    assert block.signature == ""
    assert block.block_count == 0

def test_to_json(testblock):
    json_block = testblock.to_json()
    assert json_block == {
        "transactions": [],
        "lastHash": "Hello Beezkeepers! 🐝",
        "forger": "BeezAuthors: Enrico Zanardo 🤙🏽 & ⭐",
        "blockCount": 0,
        "timestamp": 0,
        "signature": "",
    }

def test_payload(testblock):
    payload = testblock.payload()
    assert payload == {
        "transactions": [],
        "lastHash": "Hello Beezkeepers! 🐝",
        "forger": "BeezAuthors: Enrico Zanardo 🤙🏽 & ⭐",
        "blockCount": 0,
        "timestamp": 0,
        "signature": "",
    }

def test_sign(testblock):
    testblock.sign("test signature")
    assert testblock.signature == "test signature"


