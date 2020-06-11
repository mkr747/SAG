import time
from agents.UserAgent import UserAgent

if __name__ == "__main__":
    user = UserAgent("user@localhost", "user", dataEndpoint = "data@localhost")
    user.start()
    while True:
        try:
            time.sleep(1)
        except KeyboardInterrupt:
            break
    
    user.stop()