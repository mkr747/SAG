import time, json, datetime
import pandas as pd
from spade.agent import Agent
from spade.behaviour import OneShotBehaviour, CyclicBehaviour
from spade.message import Message
from spade.template import Template
from spade import quit_spade
from mlxtend.preprocessing import minmax_scaling

from app.services.MessageService import MessageService
from app.agents.KnnAgent import KnnAgent
from app.services.Endpoints import Endpoints
from app.services.Logger import Logger
from app.services.KnnService import KnnService

Querying = "Querying"
Bidding = "Bidding"
PhaseTag = "phase"
KnnId = "number"
center = "center"


class DataAgent(Agent):
    class BiddingBehav(CyclicBehaviour):
        def __init__(self, threshold, logger):
            super().__init__()
            self.raw_data = None
            self.data = None
            self.threshold_data = list()
            self.norm = dict()
            self.scaled_data_with_labels = None
            self.test_data = None
            self.knn_agents = {}
            self.agent_count = 0
            self.threshold = threshold
            self.logger = logger
            self.messageService = MessageService()
            self.processed_data_index = 0
            self.processed_knn_agent = 1
            self.test_scaled_data = None
            self.test_scaled_data_with_labels = None
            self.processed_test_data_index = 0

        def on_subscribe(self, jid):
            # print(f'[{datetime.datetime.now().time()}]DataAgent: Agent {jid} asked for subscription.')
            self.presence.approve(jid)
            self.presence.subscribe(jid)

        def on_subscribed(self, jid):
            print(f'[{datetime.datetime.now().time()}]DataAgent: Agent {jid} has accepted the subscription.')

        async def run(self):
            self.presence.on_subscribe = self.on_subscribe
            self.presence.on_subscribed = self.on_subscribed
            # print(f'[{datetime.datetime.now().time()}]DataAgent: Data agent run')
            self.__get_data("..\\data\\winequality-white.csv")
            if self.processed_data_index < len(self.scaled_data_with_labels):
                await self.__split_dataset()
            else:
                await self.__send_train_data()
                if self.processed_test_data_index == len(self.test_scaled_data_with_labels):
                    await self.on_end()

        async def on_end(self):
            msg = self.messageService.create_message_from_data_frame(Endpoints.VAGENT, 'Kill', '')
            await self.send(msg)
            await self.agent.stop()

        def __get_data(self, filepath):
            try:
                self.raw_data = pd.read_csv(filepath, sep=",")
                self.labels = self.raw_data[self.raw_data.columns[-1]]
                self.data = self.raw_data.iloc[:, :-1]
                self.scaled_data_with_labels = self.__normalize_data(self.data)
                self.scaled_data_with_labels['quality'] = self.labels
            except IOError as e:
                self.logger.custom_message(f'Cannot open file. {e}')

        def __get_test_data(self, filepath):
            try:
                raw_data = pd.read_csv(filepath, sep=",")
                labels = raw_data[raw_data.columns[-1]]
                data = raw_data.iloc[:, :-1]
                self.test_scaled_data = self.__normalize_data(data)
                self.test_scaled_data_with_labels = self.test_scaled_data.copy()
                self.test_scaled_data_with_labels['quality'] = labels
            except IOError as e:
                self.logger.custom_message(f'Cannot open file. {e}')

        def __normalize_data(self, data):

            for columnName, columnData in data.iteritems():
                if len(self.norm) is not len(self.data.columns):
                    self.norm[columnName] = max(columnData)
                data[columnName] = data[columnName] / self.norm[columnName]

       #     data[:, data.columns] = (data[:, data.columns] * self.norm[data.columns])
            return data

        async def __split_dataset(self):
            row = self.scaled_data_with_labels.iloc[self.processed_data_index]
            print(f'processing: { round(100 * self.processed_data_index / len(self.scaled_data_with_labels))} %')
            assigned = False

            if len(self.knn_agents) > 0:
                #print(f"Euclides {KnnService.GetEuclidesMeasure(self.knn_agents[self.processed_knn_agent][center], row[:-1])}")
                self.threshold_data.append(KnnService.GetEuclidesMeasure(self.knn_agents[self.processed_knn_agent][center], row[:-1]))
                if KnnService.GetEuclidesMeasure(self.knn_agents[self.processed_knn_agent][center], row[:-1]) < 0.29 or self.processed_knn_agent == 60:
                    if self.processed_knn_agent == 60:
                        self.processed_knn_agent = self.threshold_data.index(min(self.threshold_data)) + 1
                    await self.__send_row(self.processed_knn_agent, row)
                    await self.__wait_for_center(self.processed_knn_agent)
                    assigned = True

                if len(self.knn_agents) == self.processed_knn_agent or assigned:
                    self.processed_knn_agent = 1
                    self.threshold_data = list()
                else:
                    self.processed_knn_agent += 1
                    return

            if not assigned:
                self.agent_count += 1
                await self.__create_new_agent(self.agent_count, row)

            self.processed_data_index += 1

        async def __create_new_agent(self, number, row):
            agent = KnnAgent(f'knn{number}@localhost', Endpoints.PASS, number, Endpoints.DAGENT)
            await agent.start(auto_register=True)
            agent.web.start(hostname="localhost", port="10000")
            self.logger.agent_created(f'Knn{number}Agent')
            if agent.is_alive():
                await self.__send_row(number, row)
                self.knn_agents.setdefault(number, {"Agent": agent, center: 0})
                await self.__wait_for_center(number)

        async def __wait_for_center(self, number):
            # print("Data czeka na centrum")
            ccResponse = await self.receive(timeout=5)

            if ccResponse is None:
                return
            # print(f"Centrum: {ccResponse.body} od {ccResponse.thread}")
            if ccResponse.metadata['phase'] == 'center':
                self.knn_agents[number][center] = MessageService.decode_message_to_dict(ccResponse.body)

        async def __send_row(self, agent_index, row):
            # print(f'Data wysyła rowa do {agent_index}')
            msg = self.messageService.create_message_from_data_frame(f'knn{agent_index}@localhost', Bidding, row.to_json(),
                                                                     agent_index)
            await self.send(msg)

        async def __send_train_data(self):
            self.__get_test_data("..\\data\\winequality-white-test.csv")
            row = self.test_scaled_data.iloc[self.processed_test_data_index]

            for agent_index in range(self.agent_count):
                msg = self.messageService.create_message_from_data_frame(f'knn{agent_index + 1}@localhost', Querying, row.to_json(),
                                                                         agent_index)
                msg.set_metadata('index', f'{self.processed_test_data_index}')
                await self.send(msg)

            msg = self.messageService.create_message_from_data_frame(Endpoints.VAGENT, Querying, f'{self.test_scaled_data_with_labels.iloc[self.processed_test_data_index]["quality"]}')
            msg.set_metadata('index', f'{self.processed_test_data_index}')
            await self.send(msg)

            self.processed_test_data_index += 1

    def __init__(self, jid, password, threshold, verify_security=False):
        super().__init__(jid, password, verify_security)
        self.logger = Logger('DataAgent')
        self.threshold = threshold

    async def setup(self):
        b = self.BiddingBehav(self.threshold, self.logger)
        self.add_behaviour(b)
        self.logger.agent_started()