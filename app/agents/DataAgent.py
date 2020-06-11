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

Querying = "Querying"
Bidding = "Bidding"
PhaseTag = "phase"
KnnId = "number"
Center = "Center"

class DataAgent(Agent):
    class BiddingBehav(OneShotBehaviour):
        def __init__(self, threshhold, logger):
            super().__init__()
            self.raw_data = None
            self.data = None
            self.scaled_data = None
            self.knn_agents = {}
            self.agent_count = 0
            self.threshhold = threshhold
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
            await self.agent.stop()

        def __get_data(self, filepath):
            try:
                self.raw_data = pd.read_csv(filepath, sep=",")
                self.labels = self.raw_data[self.raw_data.columns[-1]]
                self.data = self.raw_data.iloc[:, :-1]
                self.scaled_data = minmax_scaling(self.data, self.data.columns)
            except IOError as e:
                self.logger.custom_message(f'Cannot open file. {e}')

        async def __split_dataset(self):
            for row in self.scaled_data.iterrows():
                assigned = False
                for key in self.knn_agents:
                    if self.knn_agents[key][Center] < self.threshhold:
                        await self.__send_row(key, row[0])
                        await self.__wait_for_center(key)
                        assigned = True
                
                if assigned == False:
                    self.agent_count += 1
                    print(f'new one with key {self.agent_count}')
                    await self.__create_new_agent(self.agent_count)
                    await self.__send_row(self.agent_count, row[0])
                    await self.__wait_for_center(self.agent_count)

        async def __create_new_agent(self, number):
            agent = KnnAgent(Endpoints.KAGENT, Endpoints.PASS, number, Endpoints.DAGENT)
            await agent.start()
            self.logger.agent_created(f'Knn{number}Agent')
            self.knn_agents.setdefault(number, { "Agent": agent, Center: 0 })
            print(self.knn_agents)

        async def __wait_for_center(self, number):
            ccResponse = await self.receive(timeout=10)
            if(ccResponse.metadata[KnnId] == number):
                self.knn_agents[number][Center] = ccResponse.body

        async def __send_row(self, agent_index, row_index):
            msg = self.messageService.create_message_from_data_frame(Endpoints.KAGENT, Bidding, self.scaled_data.iloc[row_index].to_json(), agent_index)

            await self.send(msg)

    def __init__(self, jid, password, threshhold, verify_security=False):
        super().__init__(jid, password, verify_security)
        self.logger = Logger('DataAgent')
        self.threshhold = threshhold

    async def setup(self):
        b = self.BiddingBehav(self.threshhold, self.logger)
        self.add_behaviour(b)
        self.logger.agent_started()