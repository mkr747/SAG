import json
from collections import namedtuple
from spade.message import Message


class MessageService:
    @staticmethod
    def decodeMessageToObject(messageJson):
        return namedtuple('X', messageJson.keys())(*messageJson.values())

    @staticmethod
    def decode_message_to_dict(messageJson):
        return json.loads(messageJson)

    @staticmethod
    def createMessage(receiverJid, phase, content):
        msg = Message(to=receiverJid)
        msg.set_metadata("phase", phase)
        msg.set_metadata("language", "json")
        msg.body = json.dumps(content)
        
        return msg

    @staticmethod
    def create_message_from_data_frame(receiverJid, phase, content, thread='None'):
        msg = Message(to=receiverJid)
        msg.set_metadata("phase", phase)
        msg.set_metadata("language", "json")
        msg.thread = f'{thread}'
        msg.body = content

        return msg
