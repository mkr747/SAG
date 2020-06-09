import itertools
import datetime
from spade.agent import Agent
from spade.behaviour import CyclicBehaviour
from ..handlers.MessageHandler import MessageHandler
from ..models.KnnResponse import KnnResponse
from operator import itemgetter

class ValidationAgent(Agent):
    class ListeningBehav(CyclicBehaviour):
        def __init__(self, userEndpoint):
            self.userEndpoint = userEndpoint
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
            MessageHandler.createMessage(self.userEndpoint, "inform", "content")
            await self.agent.stop()


        async def run(self):
            msg = await self.receive(timeout=None)
            knnResult = MessageHandler.decodeMessageToObject(msg)
            self.knnResponse.append(knnResult)
            self.countResults()

    async def setup(self, userEndpoint):
        print(f"ValidationAgent started at {datetime.datetime.now().time()}")
        behav = self.ListeningBehav(userEndpoint = userEndpoint)
        self.add_behaviour(behav)
