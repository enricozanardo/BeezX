import os
import time
import threading
from loguru import logger

from beez.beez_utils import BeezUtils
from beez.socket.messages.message_chunk_reply import MessageChunkReply
from beez.socket.messages.message_push_chunk_reply import MessagePushChunkReply
from beez.socket.messages.message_push_chunk import MessagePushChunk


class DamMessageWorker():

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
            chunk_reply = MessagePushChunkReply(self.p2p_handler.socket_connector, "push_chunk_reply", chunk_id=message.chunk_id, ack=True)
            try:
                filename = f"{self.p2p_handler.beez_node.dam_asset_path}{message.chunk_id}"
                with open(filename, "w+b") as outfile:
                    outfile.write(message.chunk)
                if not os.path.isfile(filename):
                    exception_message = "Could not write chunk to filesystem file."
                    logger.info(exception_message)
                    raise Exception(exception_message)
                if message.chunk_type == "primary":
                    logger.info(50*'#')
                    logger.info(f'GOT PRIMARY CHUNK {message.chunk_id.split("-")[1]}')
                    if message.chunk_id not in self.p2p_handler.beez_node.primary_chunks:
                        self.p2p_handler.beez_node.primary_chunks.append(message.chunk_id)
                        # also push to backup node
                        self.p2p_handler.push_chunk_to_neighbor(message.chunk_id, message.chunk)
                    else:
                        logger.info(f'PRIMARY CHUNK {message.chunk_id.split("-")[1]} is already stored')
                elif message.chunk_type == "backup":
                    logger.info(50*'#')
                    logger.info(f'GOT BACKUP CHUNK {message.chunk_id.split("-")[1]}')
                    if message.chunk_id not in self.p2p_handler.beez_node.backup_chunks:
                        self.p2p_handler.beez_node.backup_chunks.append(message.chunk_id)
            except Exception as ex:
                chunk_reply = MessagePushChunkReply(self.p2p_handler.socket_connector, "push_chunk_reply", chunk_id=message.chunk_id, ack=False)
            encoded_chunk_reply: str = BeezUtils.encode(chunk_reply)
            self.p2p_handler.send(node, encoded_chunk_reply)

            # mark task of working on message as done
            self.message_buffer.messages.task_done()

            time.sleep(0.1)
            