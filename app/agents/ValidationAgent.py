import datetime
from spade.agent import Agent
from spade.behaviour import CyclicBehaviour
from statistics import mode

from app.services.MessageService import MessageService
from app.services.Logger import Logger
from app.consts.Tags import Tags


class ValidationAgent(Agent):
    def __init__(self, jid, password, user_endpoint, verify_security=False):
        self.userEndpoint = user_endpoint
        self.logger = Logger('ValidationAgent')
        super().__init__(jid, password, verify_security)

    class ListeningBehav(CyclicBehaviour):
        def __init__(self, user_endpoint, logger):

            self.userEndpoint = user_endpoint
            self.messageService = MessageService()
            self.logger = logger
            self.knnResponse = dict()
            self.results = []
            self.labels = dict()
            self.query_count = None
            super().__init__()

        async def on_end(self):
            max(self.results, key=lambda knn: knn.weight)
            msg = self.messageService.create_message(self.userEndpoint, "inform", "content")
            await self.send(msg)
            await self.agent.stop()

        async def run(self):
            msg = await self.receive(timeout=1)
            if msg is not None:
                if msg.metadata[Tags.PHASE_TAG] == Tags.VALIDATE:
                    knn_result = self.messageService.decode_message_to_dict(msg.body)
                    self.logger.custom_message(
                        f'**KNN{knn_result[4]}** with {knn_result[3]} data Predicted {knn_result[0]}'
                        f' with weight: {knn_result[1]}'
                        f' for Query id {msg.metadata["index"]}  euclidean: {knn_result[2]}')

                    if msg.metadata["index"] not in self.knnResponse.keys():
                        self.knnResponse[msg.metadata["index"]] = list()

                    self.knnResponse[msg.metadata["index"]].append(knn_result)

                if msg.metadata[Tags.PHASE_TAG] == Tags.QUERYING:
                    true_label = self.messageService.decode_message_to_dict(msg.body)
                    self.logger.custom_message(f'Query id: {msg.metadata["index"]}; Real class: {true_label}')
                    self.labels[msg.metadata["index"]] = true_label

                if msg.metadata[Tags.PHASE_TAG] == Tags.KILL:
                    self.query_count = len(self.labels)

                if self.query_count is not None and self.query_count == len(self.knnResponse) and \
                        len(self.knnResponse[f'{self.query_count - 1}']) == len(self.knnResponse['0']):
                    results, accuracy = self.count_results()
                    self.logger.custom_message(f'Prediction {self.__get_results(results)}')
                    self.logger.custom_message(f'Original   {self.__get_results(self.labels.values())}')
                    self.logger.custom_message(f'{"{:.2f}".format(accuracy)}%')

        def __get_results(self, labels):
            result = ''
            for i, label in enumerate(labels):
                result += f'Query{i}: {label} '

            return result

        def count_results(self):
            classes = []
            results = []
            euclidean_distances = []
            counter = 0
            for key in self.knnResponse.keys():
                for val in self.knnResponse[key]:
                    classes.append(val[0])
                    euclidean_distances.append(val[2])
                multiplier = [5, 3, 2]
                for i in range(3):
                    index_of_min_value = euclidean_distances.index(min(euclidean_distances))
                    for _ in range(multiplier[i]):
                        classes.append(self.knnResponse[key][index_of_min_value][0])
                    euclidean_distances[index_of_min_value] = max(euclidean_distances) + 1
                try:
                    results.append(mode(classes))
                except:
                    results.append(5)
                if results[-1] == self.labels[key]:
                    counter += 1
                classes = []
                euclidean_distances = []

            return results, counter / len(results) * 100

    async def setup(self):
        self.logger.agent_started()
        print(f"ValidationAgent started at {datetime.datetime.now().time()}")
        behav = self.ListeningBehav(user_endpoint=self.userEndpoint, logger=self.logger)
        self.add_behaviour(behav)
