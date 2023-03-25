import queue
from p2pnetwork.node import Node    # type: ignore

from beez.socket.messages.message import Message

class DamMessageBuffer():
    def __init__(self):
        self.messages = queue.Queue()

    def add_message(self, node: Node, message: Message):
        self.messages.put((node, message))

