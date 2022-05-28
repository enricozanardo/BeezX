from Crypto.Hash import SHA256
import json
import jsonpickle
from loguru import logger

class BeezUtils():

    @staticmethod
    def hash(data):
        dataString = json.dumps(data, default=str) # create a string representation of the data
        dataBytes = dataString.encode('utf-8') # trasform the string data into a byte representation
        dataHash = SHA256.new(dataBytes)

        return dataHash

    # peers messages are made on bytes and we can encode and decode them

    @staticmethod
    def encode(objectToEncode):
        encodedObject = jsonpickle.encode(objectToEncode, unpicklable=True)
        return encodedObject

    @staticmethod
    def decode(encodedObject):
        return jsonpickle.decode(encodedObject)
