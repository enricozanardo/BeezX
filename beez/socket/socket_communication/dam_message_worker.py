import time
import threading
from loguru import logger

from beez.beez_utils import BeezUtils
from beez.socket.messages.message_junk_reply import MessageJunkReply
from beez.socket.messages.message_push_junk_reply import MessagePushJunkReply
from beez.socket.messages.message_push_junk import MessagePushJunk


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
            junk_reply = MessagePushJunkReply(self.p2p_handler.socket_connector, "push_junk_reply", junk_id=message.junk_id, ack=True)
            try:
                with open(f"{self.p2p_handler.beez_node.dam_asset_path}{message.junk_id}", "w+b") as outfile:
                    outfile.write(message.junk)
                if message.chunk_type == "primary":
                    logger.info(50*'#')
                    logger.info(f'GOT PRIMARY CHUNK {message.junk_id.split("-")[1]}')
                    if message.junk_id not in self.p2p_handler.beez_node.primary_chunks:
                        self.p2p_handler.beez_node.primary_chunks.append(message.junk_id)
                        # also push to backup node
                        self.p2p_handler.push_chunk_to_neighbor(message.junk_id, message.junk)
                    else:
                        logger.info(f'PRIMARY CHUNK {message.junk_id.split("-")[1]} is already stored')
                elif message.chunk_type == "backup":
                    logger.info(50*'#')
                    logger.info(f'GOT BACKUP CHUNK {message.junk_id.split("-")[1]}')
                    if message.junk_id not in self.p2p_handler.beez_node.backup_chunks:
                        self.p2p_handler.beez_node.backup_chunks.append(message.junk_id)
            except Exception as ex:
                junk_reply = MessagePushJunkReply(self.p2p_handler.socket_connector, "push_junk_reply", junk_id=message.junk_id, ack=False)
            encoded_junk_reply: str = BeezUtils.encode(junk_reply)
            self.p2p_handler.send(node, encoded_junk_reply)

            # mark task of working on message as done
            self.message_buffer.messages.task_done()
            