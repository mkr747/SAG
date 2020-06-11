import json
from collections import namedtuple
from spade.message import Message


class MessageService:
    @staticmethod
    def decode_message_to_object(message_json):
        return namedtuple('X', message_json.keys())(*message_json.values())

    @staticmethod
    def decode_message_to_dict(message_json):
        return json.loads(message_json)

    @staticmethod
    def create_message(receiver_jid, phase, content, thread='None'):
        msg = Message(to=receiver_jid)
        msg.set_metadata("phase", phase)
        msg.set_metadata("language", "json")
        msg.thread = f'{thread}'
        msg.body = json.dumps(content)
        
        return msg

    @staticmethod
    def create_message_from_data_frame(receiver_jid, phase, content, thread='None'):
        msg = Message(to=receiver_jid)
        msg.set_metadata("phase", phase)
        msg.set_metadata("language", "json")
        msg.thread = f'{thread}'
        msg.body = content

        return msg
