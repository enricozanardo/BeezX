"""Utility functions used across the project."""

import json
import typing
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

    @staticmethod
    def tx_binary_search(all_tx_hash: typing.List[str], current_tx_hash: str) -> bool:
        """
        Binary search method for searching if a transaction is or not in the pool transactions.
        Time complexity: O(log(n))

        --Parameters
         - all_tx_hash: (List[str]) list of the UIDs for all the transactions already in the
           pool transactions
         - current_tx_has: (str) the transaction UID to be searched.

        --Return
         - True if the current tx is already present
         - False if the current tx is not present
        """
        # sort the txs hash
        all_tx_hash = sorted(all_tx_hash)
        # Use binary search to find the transaction with the given hash in the sorted list
        low, high = 0, len(all_tx_hash) - 1
        while low <= high:
            mid = (low + high) // 2
            if all_tx_hash[mid] == current_tx_hash:  # pylint: disable=no-else-return
                return True
            elif all_tx_hash[mid] < current_tx_hash:
                low = mid + 1
            else:
                high = mid - 1
        return False
