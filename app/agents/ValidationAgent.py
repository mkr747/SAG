import itertools
import datetime
from spade.agent import Agent
from spade.behaviour import CyclicBehaviour
from spade.message import Message
from app.services.MessageService import MessageService
from app.models.KnnResponse import KnnResponse
from operator import itemgetter

class ValidationAgent(Agent):
    def __init__(self, jid, password, userEndpoint, verify_security=False):
        self.userEndpoint = userEndpoint
        super().__init__(jid, password, verify_security)

    class ListeningBehav(CyclicBehaviour):
        def __init__(self, userEndpoint):
            self.userEndpoint = userEndpoint
            self.messageService = MessageService()
            self.knnResponse = []
            self.results = []
            super().__init__()

        def countResults(self):
            sortedResults = sorted(self.knnResponse, key=itemgetter('label'))
            self.results = []

            for key, group in itertools.groupby(sortedResults, key = lambda x:x['label']):
                sum = 0
                for elem in group:
                    sum += elem
                self.results.append(KnnResponse(key, sum))

        async def on_end(self):
            max(self.results, key=lambda knn: knn.weight)
            msg = self.messageService.create_message(self.userEndpoint, "inform", "content")
            await self.send(msg)
            await self.agent.stop()


        async def run(self):
            msg = await self.receive(timeout=None)
            knnResult = self.messageService.decode_message_to_object(msg)
            self.knnResponse.append(knnResult)
            self.countResults()

    async def setup(self):
        print(f"ValidationAgent started at {datetime.datetime.now().time()}")
        behav = self.ListeningBehav(userEndpoint = self.userEndpoint)
        self.add_behaviour(behav)
