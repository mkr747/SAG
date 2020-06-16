import pandas as pd
from spade.agent import Agent
from spade.behaviour import CyclicBehaviour

from app.services.Logger import Logger
from app.services.MessageService import MessageService
from app.services.KnnService import KnnService
from app.consts.Endpoints import Endpoints
from app.consts.Tags import Tags


class KnnAgent(Agent):
    def __init__(self, jid, password, number, creator_jid, verify_security=False):
        super().__init__(jid, password, verify_security)
        self.logger = Logger(f'Knn{number}Agent')
        self.number = number
        self.creatorJid = creator_jid

    class KnnBehav(CyclicBehaviour):
        def __init__(self, number, creator_jid, logger):
            super().__init__()
            self.number = number
            self.creatorJid = creator_jid
            self.data = pd.DataFrame()
            self.knnService = KnnService()
            self.messageService = MessageService()
            self.logger = logger

        async def run(self):
            msg = await self.receive(timeout=5)
            if msg is None:
                return

            if msg.body == Tags.DONE:
                self.logger.custom_message('Killed')
                await self.agent.stop()
                return

            if msg and msg.metadata[Tags.PHASE_TAG] == Tags.BIDDING:
                row = self.messageService.decode_message_to_dict(message_json=msg.body)
                self.knnService.add_data(row)
                cc = self.knnService.calculate_center(row)
                cc_response = self.messageService.create_message(self.creatorJid, Tags.CENTER, cc, self.number)
                await self.send(cc_response)

                return

            if msg and msg.metadata[Tags.PHASE_TAG] == Tags.QUERYING:
                row = self.messageService.decode_message_to_dict(message_json=msg.body)
                if len(self.knnService.data) >= 5:
                    [label, weight] = self.knnService.knn(row)
                    euclidean_distance = self.knnService.get_euclidean_measure(self.knnService.center, list(row.values()))
                    q_response = self.messageService.create_message(Endpoints.VAGENT, Tags.VALIDATE, [label, weight, euclidean_distance, len(self.knnService.data), self.number])
                    q_response.set_metadata('index', msg.metadata['index'])
                    self.logger.custom_message(f'Sufficient amount of data: {len(self.knnService.data)} - sending to validate')
                    await self.send(q_response)
                else:
                    self.logger.custom_message(f'Insufficient amount of data: {len(self.knnService.data)}')

                return

        def on_subscribe(self, jid):
            self.logger.agent_subscribe(jid)
            self.presence.approve(jid)
            self.presence.subscribe(jid)

        def on_subscribed(self, jid):
            self.logger.agent_subscribed(jid)

    async def setup(self):
        knn_behav = self.KnnBehav(self.number, self.creatorJid, self.logger)
        self.behav1 = knn_behav
        self.add_behaviour(knn_behav)
        self.logger.agent_started()

