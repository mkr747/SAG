import time
from agents.UserAgent import UserAgent
from spade import quit_spade

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