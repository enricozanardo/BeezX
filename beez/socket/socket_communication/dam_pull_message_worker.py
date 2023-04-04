import time
import threading
from loguru import logger

from beez.beez_utils import BeezUtils
from beez.socket.messages.message_chunk_reply import MessageChunkReply
from beez.socket.messages.message_push_chunk_reply import MessagePushChunkReply
from beez.socket.messages.message_push_chunk import MessagePushChunk


class DamPullMessageWorker():

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
            node, message = self.message_buffer.messages.get()

            # process message
            content = b''
            with open(f"{self.p2p_handler.beez_node.dam_asset_path}{message.chunk_name}", "rb") as infile:
                content = infile.read()
            chunk_reply = MessageChunkReply(self.p2p_handler.socket_connector, "chunk_reply", message.file_name, message.chunk_name, content)
            encoded_chunk_reply: str = BeezUtils.encode(chunk_reply)
            logger.info('sending the file')
            self.p2p_handler.send(node, encoded_chunk_reply)

            # mark task of working on message as done
            self.message_buffer.messages.task_done()
            
            time.sleep(0.1)