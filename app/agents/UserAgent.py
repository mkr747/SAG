import datetime
from spade.agent import Agent
from spade.behaviour import CyclicBehaviour


class UserAgent(Agent):
    def __init__(self, jid, password, dataEndpoint, verify_security=False):
        self.dataEndpoint = dataEndpoint
        super().__init__(jid, password, verify_security)

    class UserBehav(CyclicBehaviour):
        def __init__(self, dataEndpoint):
            self.dataEndpoint = dataEndpoint
            super().__init__()

        async def on_end(self):
            pass

        async def run(self):
            pass

    async def setup(self, dataEndpoint):
        print(f"[{datetime.datetime.now().time()}]UserAgent: Agent started.")
        behav = self.UserBehav(dataEndpoint = self.dataEndpoint)
        self.add_behaviour(behav)
