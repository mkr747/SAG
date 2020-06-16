from spade.behaviour import OneShotBehaviour
from spade.agent import Agent

from app.agents.DataAgent import DataAgent
from app.services.Logger import Logger
from app.consts.Endpoints import Endpoints
from app.agents.ValidationAgent import ValidationAgent
from app.consts.Configuration import Configuration


class UserAgent(Agent):
    def __init__(self, jid, password, data_endpoint, verify_security=False):
        super().__init__(jid, password, verify_security)
        self.dataEndpoint = data_endpoint
        self.logger = Logger("UserAgent")

    class UserBehav(OneShotBehaviour):
        def __init__(self, data_endpoint, logger):
            self.logger = logger
            self.dataEndpoint = data_endpoint
            super().__init__()

        async def on_end(self):
            pass

        async def run(self):
            self.logger.agent_run()
            threshold = Configuration.THRESHOLD
            knn_agents = Configuration.KNN_AGENTS
            data_agent = DataAgent(Endpoints.DAGENT, Endpoints.PASS, threshold, knn_agents)
            self.logger.agent_created("DataAgent")
            await data_agent.start()
            #data_agent.web.start(hostname="localhost", port="10001")
            validation_agent = ValidationAgent(Endpoints.VAGENT, Endpoints.PASS, Endpoints.UAGENT)
            self.logger.agent_created("ValidationAgent")
            await validation_agent.start()
            
    async def setup(self):
        self.logger.agent_started()
        behav = self.UserBehav(data_endpoint=self.dataEndpoint, logger=self.logger)
        self.add_behaviour(behav)

