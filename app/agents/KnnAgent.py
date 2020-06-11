import math 
import datetime
import pandas as pd
from collections import Counter
from spade.agent import Agent
from spade.behaviour import CyclicBehaviour, OneShotBehaviour
from spade.template import Template
from services.MessageService import MessageService
from services.KnnService import KnnService
from services.Endpoints import Endpoints

Querying = "Querying"
Bidding = "Bidding"
PhaseTag = "phase"
KnnId = "number"

class KnnAgent(Agent):
    class KnnBehav(CyclicBehaviour):
        def __init__(self, number, creatorJid):
            super().__init__()
            self.number = number
            self.creatorJid = creatorJid
            self.data = pd.DataFrame()
            self.knnService = KnnService()
            self.messageService = MessageService()
            self.presence.on_subscribe = self.on_subscribe
            self.presence.on_subscribed = self.on_subscribed
        
        async def run(self):
            msg = await self.receive(timeout=None)
            if(msg.metadata[PhaseTag] == Bidding):
                row = self.messageService.decode_message_to_dict(messageJson=msg.body)
                self.knnService.addData(row)
                cc = self.knnService.CalculateCenter()
                ccResponse = self.messageService.createMessage(self.creatorJid, "center", cc)
                ccResponse.set_metadata(KnnId, self.number)
                
                await self.send(ccResponse)

            if(msg.metadata[PhaseTag] == Querying):
                row = self.messageService.decode_message_to_dict(messageJson=msg.body)
                [most_common, num_most_common] = self.knnService.Knn(row)
                qResponse = self.messageService.createMessage(Endpoints.VAGENT, "validate", [most_common, num_most_common])
                
                await self.send(qResponse)

        def on_subscribe(self, jid):
            print(f'[{datetime.datetime.now().time()}]Knn{self.number}Agent: Agent {jid} asked for subscription.')
            self.presence.approve(jid)
            self.presence.subscribe(jid)

        def on_subscribed(self, jid):
            print(f'[{datetime.datetime.now().time()}]Knn{self.number}Agent: Agent {jid} has accepted the subscription.')

    def __init__(self, jid, password, number, creatorJid, verify_security=False):
        super.__init__(jid, password, verify_security)
        self.number = number
        self.creatorJid = creatorJid

    def setup(self):
        knnBehav = self.KnnBehav(self.number, self.creatorJid)
        template = self.knnTemplate(self.number, self.creatorJid)
        self.add_behaviour(knnBehav, template)
        print(f'[{datetime.datetime.now().time()}]Knn{self.number}Agent: Agent started')
        

    def knnTemplate(self, number, creatorJid):
        template = Template()
        template.sender = creatorJid
        template.metadata = {KnnId: number}
        
        return template