import itertools
import datetime
from spade.agent import Agent
from spade.behaviour import CyclicBehaviour
from spade.message import Message
from app.services.MessageService import MessageService
from app.models.KnnResponse import KnnResponse
from operator import itemgetter
from statistics import mode

class ValidationAgent(Agent):
    def __init__(self, jid, password, userEndpoint, verify_security=False):
        self.userEndpoint = userEndpoint
        super().__init__(jid, password, verify_security)

    class ListeningBehav(CyclicBehaviour):
        def __init__(self, userEndpoint):
            self.userEndpoint = userEndpoint
            self.messageService = MessageService()
            self.knnResponse = dict()
            self.results = []
            self.labels = dict()
            self.query_count = None
            super().__init__()

        def countResults(self):
            classes = []
            results = []
            counter = 0
            for key in self.knnResponse.keys():
                for val in self.knnResponse[key]:
                    classes.append(val[0])
                results.append(mode(classes))
                if results[-1] == self.labels[key]:
                    counter += 1
                classes = []
            return results, counter/len(results) * 100


        async def on_end(self):
            max(self.results, key=lambda knn: knn.weight)
            msg = self.messageService.create_message(self.userEndpoint, "inform", "content")
            await self.send(msg)
            await self.agent.stop()


        async def run(self):
            print('Val czeka')
            msg = await self.receive(timeout=1)
            if msg is not None:
                if msg.metadata['phase'] == 'validate':
                    knnResult = self.messageService.decode_message_to_dict(msg.body)
                    print(f'Val odebrał {knnResult} dla query o indeksie: {msg.metadata["index"]}')
                    if msg.metadata["index"] not in self.knnResponse.keys():
                        self.knnResponse[msg.metadata["index"]] = list()
                    self.knnResponse[msg.metadata["index"]].append(knnResult)
                if msg.metadata['phase'] == 'Querying':
                    trueLabel = self.messageService.decode_message_to_dict(msg.body)
                    print(f'Data mówi że query o indeksie {msg.metadata["index"]} ma klase: {trueLabel}')
                    self.labels[msg.metadata["index"]] = trueLabel
                if msg.metadata['phase'] == 'Kill':
                    self.query_count = len(self.labels)
                if self.query_count is not None and self.query_count == len(self.knnResponse) and len(self.knnResponse[f'{self.query_count-1}']) == len(self.knnResponse['0']):
               #     if self.query_count == len(self.knnResponse):
               #         if len(self.knnResponse[f'{self.query_count-1}']) == len(self.knnResponse[0]):
                    results, skutecznosc_xd = self.countResults()
                    print(results)
                    print(self.labels)
                    print(skutecznosc_xd)

              #  self.knnResponse.append(knnResult)
              #  self.countResults()

    async def setup(self):
        print(f"ValidationAgent started at {datetime.datetime.now().time()}")
        behav = self.ListeningBehav(userEndpoint = self.userEndpoint)
        self.add_behaviour(behav)
