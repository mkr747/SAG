import datetime
from spade.agent import Agent
from spade.behaviour import CyclicBehaviour


class ValidationAgent(Agent):
    class ListeningBehav(CyclicBehaviour):
        def __init__(self, userEndpoint):
            super().__init__()

        async def on_end(self):
            pass


        async def run(self):
            pass

    async def setup(self, userEndpoint):
        print(f"UserAgent started at {datetime.datetime.now().time()}")
        behav = self.ListeningBehav(userEndpoint = userEndpoint)
        self.add_behaviour(behav)
