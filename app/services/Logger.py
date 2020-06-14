import datetime, math

class Logger:
    Logs = []
    def __init__(self, name):
        self.name = name
        self.current_progress = 0

    def agent_started(self):
        Logger.Logs.append(f"[{datetime.datetime.now().time()}]{self.name}: Agent started.")
        self.__print_logs()

    def agent_run(self):
        Logger.Logs.append(f"[{datetime.datetime.now().time()}]{self.name}: Agent run.")
        self.__print_logs()

    def agent_subscribe(self, jid):
        Logger.Logs.append(f'[{datetime.datetime.now().time()}]{self.name}: Agent {jid} asked for subscription.')
        self.__print_logs()

        
    def agent_subscribed(self, jid):
        Logger.Logs.append(f'[{datetime.datetime.now().time()}]{self.name}: Agent {jid} has accepted the subscription.')
        self.__print_logs()


    def agent_created(self, agentName):
        Logger.Logs.append(f'[{datetime.datetime.now().time()}]{self.name}: {agentName} created.')
        self.__print_logs()


    def custom_message(self, message):
        Logger.Logs.append(f'[{datetime.datetime.now().time()}]{self.name}: {message}')
        self.__print_logs()


    def progress_message(self, progress):
        self.current_progress  = progress

        if(self.custom_message == 100):
            Logger.Logs.append('Bidding progress... Done.')
        else:
            self.__print_logs()

    def __print_logs(self):
        print(chr(27) + "[2J")
        for log in Logger.Logs:
            print(log)
        
        if self.current_progress < 100:
            progres = []
            [progres.append('=' if x < math.floor(self.current_progress*100) else '>' if x == math.floor(self.current_progress*100) else ' ') for x in range(100)]
            progres_text = ''.join(progres)
            print(f'Bidding progress {math.floor(self.current_progress*100)}% [{progres_text}]')
        