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
            # print(f'Knn run {self.number}')
            msg = await self.receive(timeout=5)
            if msg is None:
                return
            if msg.body == 'DONE':
                print(f'KNN {self.number} CHCE ROBIĆ MASZIN LERNING! Mam {len(self.knnService.data)} danych.')
                await self.agent.stop()
                return
            # print(f'Knn {self.number} dostał {msg.body}')
            if msg and msg.metadata[PhaseTag] == Bidding:
                row = self.messageService.decode_message_to_dict(message_json=msg.body)
                self.knnService.addData(row)
                cc = self.knnService.CalculateCenter()
                ccResponse = self.messageService.create_message(self.creatorJid, "center", cc, self.number)
                # print(f"Knn {self.number} chce wysłać {cc}")
                await self.send(ccResponse)
                return

            if msg and msg.metadata[PhaseTag] == Querying:
                row = self.messageService.decode_message_to_dict(message_json=msg.body)
                [most_common, num_most_common] = self.knnService.Knn(row)
                qResponse = self.messageService.create_message(Endpoints.VAGENT, "validate",
                                                               [most_common, num_most_common])

                await self.send(qResponse)
                return

        def on_subscribe(self, jid):
            self.logger.agent_subscribe(jid)
            self.presence.approve(jid)
            self.presence.subscribe(jid)

        def on_subscribed(self, jid):
            self.logger.agent_subscribed(jid)

    async def setup(self):
        knn_behav = self.KnnBehav(self.number, self.creatorJid, self.logger)
        template = self.knn_template()
        self.behav1 = knn_behav
        self.add_behaviour(knn_behav)
        self.logger.agent_started()

    def knn_template(self):
        template = Template()
        template.to = f'{self.jid}'
        template.sender = f'{self.creatorJid}'
        template.metadata = {'language': 'json'}

        return template
