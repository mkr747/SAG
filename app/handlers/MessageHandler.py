import json
from collections import namedtuple
from spade.message import Message

class MessageHandler:
    @staticmethod
    def decodeMessageToObject(messageJson):
        return namedtuple('X', messageJson.keys())(*messageJson.values())

    @staticmethod
    def createMessage(receiverJid, performative, content):
        msg = Message(to = receiverJid)
        msg.set_metadata("performative", performative)
        msg.set_metadata("language", "json")
        msg.body = json.dumps(content)
        
        return msg