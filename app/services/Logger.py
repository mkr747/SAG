import datetime

class Logger:
    def __init__(self, name):
        self.name = name

    def agent_started(self):
        print(f"[{datetime.datetime.now().time()}]{self.name}: Agent started.")

    def agent_run(self):
        print(f"[{datetime.datetime.now().time()}]{self.name}: Agent run.")

    def agent_subscribe(self, jid):
        print(f'[{datetime.datetime.now().time()}]{self.name}: Agent {jid} asked for subscription.')
        
    def agent_subscribed(self, jid):
        print(f'[{datetime.datetime.now().time()}]{self.name}: Agent {jid} has accepted the subscription.')

    def agent_created(self, agentName):
        print(f'[{datetime.datetime.now().time()}]{self.name}: {agentName} created.')

    def custom_message(self, message):
        print(f'[{datetime.datetime.now().time()}]{self.name}: {message}')