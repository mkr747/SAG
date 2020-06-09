import time, json
import pandas as pd
from spade.agent import Agent
from spade.behaviour import OneShotBehaviour
from spade.message import Message
from spade.template import Template
from mlxtend.preprocessing import minmax_scaling

from app.handlers.MessageHandler import MessageHandler
from app.agents.KnnAgent import KnnAgent

agent_creds = [
    ("receiver@localhost", "user"),
    ("knn2@localhost", "user"),
    ("knn3@localhost", "user"),
    ("knn4@localhost", "user"),
    ("knn5@localhost", "user"),
    ("knn6@localhost", "user"),
]


class DataAgent(Agent):
    class InformBehav(OneShotBehaviour):
        def __init__(self):
            super().__init__()
            self.raw_data = None
            self.data = None
            self.scaled_data = None
            self.grouped_data = None
            self.agent_count = 0

        async def run(self):
            print("Run data agent")
            self.__get_data("..\\..\\data\\winequality-red.csv")
            await self.__split_dataset()
            await self.agent.stop()

        def __get_data(self, filepath):
            try:
                self.raw_data = pd.read_csv(filepath, sep=",")
                self.labels = self.raw_data[self.raw_data.columns[-1]]
                self.data = self.raw_data.iloc[:, :-1]
                self.scaled_data = minmax_scaling(self.data, self.data.columns)
            except IOError as e:
                print(f'Cannot open file. {e}')

        async def __split_dataset(self):
            for row in self.scaled_data.iterrows():
                if self.grouped_data is None:
                    await self.__create_new_agent()
                    await self.__send_row(0, row[0])
                    self.agent_count += 1
                    return
                else:
                    for df in self.grouped_data:
                        pass

        async def __create_new_agent(self):
            agent = KnnAgent(*agent_creds[self.agent_count])
            await agent.start(auto_register=False)

        async def __send_row(self, agent_index, row_index):
            msg = MessageHandler.create_message_from_data_frame(agent_creds[agent_index][0],
                                                                "train_data", self.raw_data.iloc[row_index].to_json())
            await self.send(msg)
            print("Message sent!")

    async def setup(self):
        print("DataAgent started")
        b = self.InformBehav()
        self.add_behaviour(b)


if __name__ == "__main__":
    data_agent = DataAgent("sender@localhost", "user")
    data_agent.start()

    while data_agent.is_alive():
        try:
            time.sleep(1)
        except KeyboardInterrupt:
            data_agent.stop()
            break
    print("Agents finished")
