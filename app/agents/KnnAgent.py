import math 
import datetime
import pandas as pd
from services.Logger import Logger
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
    def __init__(self, jid, password, number, creatorJid, verify_security=False):
        super().__init__(jid, password, verify_security)
        self.logger = Logger(f'Knn{number}Agent')
        self.number = number
        self.creatorJid = creatorJid

    class KnnBehav(CyclicBehaviour):
        def __init__(self, number, creatorJid, logger):
            super().__init__()
            self.number = number
            self.creatorJid = creatorJid
            self.data = pd.DataFrame()
            self.knnService = KnnService()
            self.messageService = MessageService()
            self.logger = logger
        
        async def run(self):
            self.presence.on_subscribe = self.on_subscribe
            self.presence.on_subscribed = self.on_subscribed
            msg = await self.receive(timeout=None)
            if(msg is None):
                return
            
            if(msg and msg.metadata[PhaseTag] == Bidding):
                row = self.messageService.decode_message_to_dict(messageJson=msg.body)
                self.knnService.addData(row)
                cc = self.knnService.CalculateCenter()
                ccResponse = self.messageService.createMessage(self.creatorJid, "center", cc)
                ccResponse.set_metadata(KnnId, f'{self.number}')
                await self.send(ccResponse)
                return

            if(msg and msg.metadata[PhaseTag] == Querying):
                row = self.messageService.decode_message_to_dict(messageJson=msg.body)
                [most_common, num_most_common] = self.knnService.Knn(row)
                qResponse = self.messageService.createMessage(Endpoints.VAGENT, "validate", [most_common, num_most_common])
                
                await self.send(qResponse)
                return

        def on_subscribe(self, jid):
            self.logger.agent_subscribe(jid)
            self.presence.approve(jid)
            self.presence.subscribe(jid)

        def on_subscribed(self, jid):
            self.logger.agent_subscribed(jid)

    async def setup(self):
        knnBehav = self.KnnBehav(self.number, self.creatorJid, self.logger)
        template = self.knnTemplate(self.number, self.creatorJid)
        self.add_behaviour(knnBehav, template)
        self.logger.agent_started()
        

    def knnTemplate(self, number, creatorJid):
        template = Template()
        template.to = f'{self.jid}'
        template.sender = f'{self.creatorJid}'
        template.thread = f'{number}'
        
        return template