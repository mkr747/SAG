import pandas as pd
from spade.agent import Agent
from spade.behaviour import CyclicBehaviour

from app.services.MessageService import MessageService
from app.agents.KnnAgent import KnnAgent
from app.consts.Endpoints import Endpoints
from app.services.Logger import Logger
from app.services.KnnService import KnnService
from app.consts.Tags import Tags
from app.consts.Configuration import Configuration


class DataAgent(Agent):
    def __init__(self, jid, password, threshold, knn_agents_limit, verify_security=False):
        super().__init__(jid, password, verify_security)
        self.logger = Logger('DataAgent')
        self.knn_agents_limit = knn_agents_limit
        self.threshold = threshold

    class BiddingBehav(CyclicBehaviour):
        def __init__(self, threshold, knn_agents_limit, logger):
            super().__init__()
            self.data = None
            self.threshold_data = list()
            self.norm = dict()
            self.scaled_data_with_labels = None
            self.knn_agents = {}
            self.agent_count = 0
            self.threshold = threshold
            self.knn_agents_limit = knn_agents_limit
            self.logger = logger
            self.messageService = MessageService()
            self.processed_data_index = 0
            self.processed_knn_agent = 1
            self.test_scaled_data = None
            self.test_scaled_data_with_labels = None
            self.processed_test_data_index = 0

        def on_subscribe(self, jid):
            self.presence.approve(jid)
            self.presence.subscribe(jid)

        async def run(self):
            self.presence.on_subscribe = self.on_subscribe
            self.__get_data(Configuration.TRAIN_DATA)
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

        def __get_data_from_file(self, file_path):
            try:
                raw_data = pd.read_csv(file_path, sep=",")
                labels = raw_data[raw_data.columns[-1]]
                data = raw_data.iloc[:, :-1]

                return [raw_data, data, labels]
            except IOError as e:
                self.logger.custom_message(f'Cannot open file. {e}')

        def __get_data(self, file_path):
            raw_data, self.data, labels = self.__get_data_from_file(file_path)
            self.scaled_data_with_labels = self.__normalize_data(self.data)
            self.scaled_data_with_labels['quality'] = labels

        def __get_test_data(self, file_path):
            raw_data, data, labels = self.__get_data_from_file(file_path)
            self.test_scaled_data = self.__normalize_data(data)
            self.test_scaled_data_with_labels = self.test_scaled_data.copy()
            self.test_scaled_data_with_labels['quality'] = labels

        def __normalize_data(self, data):
            for columnName, columnData in data.iteritems():
                if len(self.norm) is not len(self.data.columns):
                    self.norm[columnName] = max(columnData)
                data[columnName] = data[columnName] / self.norm[columnName]

            return data

        async def __split_dataset(self):
            row = self.scaled_data_with_labels.iloc[self.processed_data_index]
            assigned = False

            if len(self.knn_agents) > 0:
                self.threshold_data.append(KnnService.get_euclidean_measure(self.knn_agents[self.processed_knn_agent][Tags.CENTER], row[:-1]))
                if KnnService.get_euclidean_measure(self.knn_agents[self.processed_knn_agent][Tags.CENTER], row[:-1]) < self.threshold\
                        or self.processed_knn_agent == self.knn_agents_limit:
                    if self.processed_knn_agent == self.knn_agents_limit:
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
            self.logger.progress_message(self.processed_data_index / len(self.scaled_data_with_labels))

        async def __create_new_agent(self, number, row):
            agent = KnnAgent(f'knn{number}@localhost', Endpoints.PASS, number, Endpoints.DAGENT)
            await agent.start(auto_register=True)
            #agent.web.start(hostname="localhost", port="10000")
            self.logger.agent_created(f'Knn{number}Agent')
            if agent.is_alive():
                await self.__send_row(number, row)
                self.knn_agents.setdefault(number, {"Agent": agent, Tags.CENTER: 0})
                await self.__wait_for_center(number)

        async def __wait_for_center(self, number):
            cc_response = await self.receive(timeout=5)
            if cc_response is None:
                return

            if cc_response.metadata[Tags.PHASE_TAG] == Tags.CENTER:
                self.knn_agents[number][Tags.CENTER] = MessageService.decode_message_to_dict(cc_response.body)

        async def __send_row(self, agent_index, row):
            msg = self.messageService.create_message_from_data_frame(f'knn{agent_index}@localhost',
                                                                     Tags.BIDDING,
                                                                     row.to_json(),
                                                                     agent_index)
            await self.send(msg)

        async def __send_train_data(self):
            self.__get_test_data(Configuration.TEST_DATA)
            row = self.test_scaled_data.iloc[self.processed_test_data_index]
            for agent_index in range(self.agent_count):
                msg = self.messageService.create_message_from_data_frame(f'knn{agent_index + 1}@localhost',
                                                                         Tags.QUERYING,
                                                                         row.to_json(),
                                                                         agent_index)
                msg.set_metadata('index', f'{self.processed_test_data_index}')
                await self.send(msg)

            msg = self.messageService.create_message_from_data_frame(Endpoints.VAGENT,
                                                                     Tags.QUERYING,
                                                                     f'{self.test_scaled_data_with_labels.iloc[self.processed_test_data_index]["quality"]}')
            msg.set_metadata('index', f'{self.processed_test_data_index}')
            await self.send(msg)

            self.processed_test_data_index += 1

    async def setup(self):
        b = self.BiddingBehav(threshold=self.threshold, logger=self.logger, knn_agents_limit=self.knn_agents_limit)
        self.add_behaviour(b)
        self.logger.agent_started()