import pandas as pd
from spade.agent import Agent
from spade.behaviour import OneShotBehaviour
from spade.template import Template

from app.handlers.MessageHandler import MessageHandler


class KnnAgent(Agent):
    class RecvBehav(OneShotBehaviour):
        def __init__(self):
            super().__init__()
            self.data = pd.DataFrame()

        async def run(self):
            print("RecvBehav running")
            msg = await self.receive(timeout=10)  # wait for a message for 10 seconds
            if msg:
                msg_content_json = MessageHandler.decode_message_to_dict(messageJson=msg.body)
                self.data.append(pd.Series(msg_content_json), ignore_index=True)
                print("Message received with content: {}".format(msg_content_json))
            else:
                print("Did not received any message after 10 seconds")
            await self.agent.stop()

    async def setup(self):
        print("ReceiverAgent started")
        b = self.RecvBehav()
        template = Template()
        template.set_metadata("performative", "train_data")
        self.add_behaviour(b, template)
