"""Utility functions used across the project."""

import json
import jsonpickle   # type: ignore
from Crypto.Hash import SHA512


class BeezUtils:
    """Utility class providing frequently used functions across the project."""
    @staticmethod
    def hash(data):
        """Takes arbitrary data and returns its corresponding SHA512 hash."""
        data_string = json.dumps(
            data, default=str, separators=(',', ':')
        )  # create a string representation of the data
        data_bytes = data_string.encode(
            "utf-8"
        )  # trasform the string data into a byte representation
        data_hash = SHA512.new(data_bytes)

        return data_hash

    # peers messages are made on bytes and we can encode and decode them

    @staticmethod
    def encode(object_to_encode):
        """Takes an arbitrary python objects and returns its pickled version."""
        encoded_object = jsonpickle.encode(object_to_encode, unpicklable=True)
        return encoded_object

    @staticmethod
    def decode(encoded_object):
        """Takes a pickled object and recreates the original object from it."""
        return jsonpickle.decode(encoded_object)
