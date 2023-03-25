import threading
from loguru import logger

from beez.beez_utils import BeezUtils
from beez.socket.messages.message_junk_reply import MessageJunkReply
from beez.socket.messages.message_push_junk_reply import MessagePushJunkReply
from beez.socket.messages.message_push_junk import MessagePushJunk


class DamPushReplyWorker():

    def __init__(self, message_buffer, p2p_handler):
        self.message_buffer = message_buffer
        self.p2p_handler = p2p_handler

    def start(self):
        processing_thread = threading.Thread(target=self.process, args={})
        processing_thread.daemon = True
        processing_thread.start()

    def process(self):
        while True:
            # get next message from queue
            _, message = self.message_buffer.messages.get()

            # process message
            junk_id = str(message.junk_id)
            asset_hash = junk_id.rsplit("-", 1)[0]
            ack = message.ack
            if ack:
                self.p2p_handler.beez_node.pending_chunks[asset_hash][junk_id]["status"] = False

            # mark task of working on message as done
            self.message_buffer.messages.task_done()

            
            
            