import datetime, time
from app.agents.DataAgent import DataAgent
from app.services.Logger import Logger
from app.services.Endpoints import Endpoints
from spade.agent import Agent
from spade.behaviour import OneShotBehaviour



class UserAgent(Agent):
    def __init__(self, jid, password, dataEndpoint, verify_security=False):
        super().__init__(jid, password, verify_security)
        self.dataEndpoint = dataEndpoint
        self.logger = Logger("UserAgent")


    class UserBehav(OneShotBehaviour):
        def __init__(self, dataEndpoint, logger):
            self.logger = logger
            self.dataEndpoint = dataEndpoint
            super().__init__()

        async def on_end(self):
            pass

        async def run(self):
            self.logger.agent_run()
            threshhold = 0.5
            dataAgent = DataAgent(Endpoints.DAGENT, Endpoints.PASS, threshhold)
            self.logger.agent_created("DataAgent")
            await dataAgent.start()
            dataAgent.web.start(hostname="localhost", port="10001")
            
    async def setup(self):
        self.logger.agent_started()
        behav = self.UserBehav(dataEndpoint = self.dataEndpoint, logger = self.logger)
        self.add_behaviour(behav)

