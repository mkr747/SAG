import time, json, datetime
import pandas as pd
from spade.agent import Agent
from spade.behaviour import OneShotBehaviour
from spade.message import Message
from spade.template import Template
from spade import quit_spade
from mlxtend.preprocessing import minmax_scaling

from services.MessageService import MessageService
from agents.KnnAgent import KnnAgent
from services.Endpoints import Endpoints
from services.Logger import Logger
from services.KnnService import KnnService
Querying = "Querying"
Bidding = "Bidding"
PhaseTag = "phase"
KnnId = "number"
Center = "Center"


class DataAgent(Agent):
    class BiddingBehav(OneShotBehaviour):
        def __init__(self, threshold, logger):
            super().__init__()
            self.raw_data = None
            self.data = None
            self.scaled_data = None
            self.scaled_data_with_labels = None
            self.knn_agents = {}
            self.agent_count = 0
            self.threshold = threshold
            self.logger = logger
            self.messageService = MessageService()

        def on_subscribe(self, jid):
            print(f'[{datetime.datetime.now().time()}]DataAgent: Agent {jid} asked for subscription.')
            self.presence.approve(jid)
            self.presence.subscribe(jid)

        def on_subscribed(self, jid):
            print(f'[{datetime.datetime.now().time()}]DataAgent: Agent {jid} has accepted the subscription.')

        async def run(self):
            self.presence.on_subscribe = self.on_subscribe
            self.presence.on_subscribed = self.on_subscribed
            print(f'[{datetime.datetime.now().time()}]DataAgent: Data agent run')
            self.__get_data("..\\data\\winequality-red.csv")
            await self.__split_dataset()

        async def on_end(self):
            await self.agent.stop()

        def __get_data(self, filepath):
            try:
                self.raw_data = pd.read_csv(filepath, sep=",")
                self.labels = self.raw_data[self.raw_data.columns[-1]]
                self.data = self.raw_data.iloc[:, :-1]
                self.scaled_data = minmax_scaling(self.data, self.data.columns)
                self.scaled_data_with_labels = self.scaled_data.copy()
                self.scaled_data_with_labels['quality'] = self.labels
            except IOError as e:
                self.logger.custom_message(f'Cannot open file. {e}')

        async def __split_dataset(self):
            for index, row in self.scaled_data_with_labels.iterrows():
                assigned = False
                for key in self.knn_agents:
                    if KnnService.GetEuclidesMeasure(self.knn_agents[key][Center], row[:-1]) < self.threshold:
                        await self.__send_row(key, row)
                        await self.__wait_for_center(key)
                        assigned = True

                if not assigned:
                    self.agent_count += 1
                    self.logger
                    await self.__create_new_agent(self.agent_count, row)

        async def __create_new_agent(self, number, row):
            agent = KnnAgent(Endpoints.KAGENT, Endpoints.PASS, number, Endpoints.DAGENT)
            await agent.start()
            self.logger.agent_created(f'Knn{number}Agent')
            await self.__send_row(number, row)
            self.logger.custom_message(f'Data sent: {row}')
            self.knn_agents.setdefault(number, { "Agent": agent, Center: 0 })
            await self.__wait_for_center(number)
            self.logger.custom_message(f'Ceneter provided for: Knn{number}; Center = {self.knn_agents[number]}')

            return True

        async def __wait_for_center(self, number):
            while True:
                ccResponse = await self.receive(timeout=None)
                if ccResponse is None:
                    continue
                
                print(ccResponse)
                if(ccResponse.metadata[KnnId] == f'{number}'):
                    print(f'AAAAAAAAAAAAAAAAAAAAAAAAAA: {ccResponse.body}')
                    self.knn_agents[number][Center] = ccResponse.body

        async def __send_row(self, agent_index, row):
            msg = self.messageService.create_message_from_data_frame(Endpoints.KAGENT, Bidding, row.to_json(), agent_index)
            await self.send(msg)

    def __init__(self, jid, password, threshold, verify_security=False):
        super().__init__(jid, password, verify_security)
        self.logger = Logger('DataAgent')
        self.threshold = threshold

    async def setup(self):
        b = self.BiddingBehav(self.threshold, self.logger)
        template = self.data_template()
        self.add_behaviour(b, template)
        self.logger.agent_started()

    def data_template(self):
        template = Template()
        template.to = f'{self.jid}'
        template.sender = f'{Endpoints.KAGENT}'
        template.metadata={'phase': 'center', 'language': 'json'}
        print(template)
        return template
