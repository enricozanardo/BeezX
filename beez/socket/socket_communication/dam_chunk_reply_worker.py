import time
import threading
from loguru import logger

from beez.beez_utils import BeezUtils
from beez.socket.messages.message_chunk_reply import MessageChunkReply
from beez.socket.messages.message_push_chunk_reply import MessagePushChunkReply
from beez.socket.messages.message_push_chunk import MessagePushChunk


class DamChunkReplyWorker():

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
            logger.info(100*'#')
            logger.info(f'GOT CHUNK REPLY {message.chunk_name}')
            chunk = message.chunk
            chunk_name = message.chunk_name
            file_name = message.file_name
            self.p2p_handler.beez_node.add_asset_chunks(file_name, chunk_name, chunk)

            # mark task of working on message as done
            self.message_buffer.messages.task_done()
            
            time.sleep(0.1)