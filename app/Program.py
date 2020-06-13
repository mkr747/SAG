import time
from app.agents.UserAgent import UserAgent
from spade import quit_spade
import asyncio
asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())  # python-3.8.0a4

if __name__ == "__main__":
    user = UserAgent("user@localhost", "user", dataEndpoint = "data@localhost")
    start = user.start()
    start.result()
    while True:
        try:
            time.sleep(1)
        except KeyboardInterrupt:
            break
    
    user.stop()
    quit_spade()