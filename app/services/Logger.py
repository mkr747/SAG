import datetime
import math
import os


class Logger:
    Logs = []
    Current_progress = 0

    def __init__(self, name):
        self.name = name

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

    def agent_created(self, agent_name):
        Logger.Logs.append(f'[{datetime.datetime.now().time()}]{self.name}: {agent_name} created.')
        self.__print_logs()

    def custom_message(self, message):
        Logger.Logs.append(f'[{datetime.datetime.now().time()}]{self.name}: {message}')
        self.__print_logs()

    def progress_message(self, progress):
        Logger.Current_progress = progress

        if Logger.Current_progress == 1:
            Logger.Logs.append('Bidding progress... Done.')
        else:
            self.__print_logs()

    def __print_logs(self):
        print(chr(27) + "[2J")
        print('\n' * 10)
        os.system('cls||clear')
        for log in Logger.Logs:
            print(log)
        if Logger.Current_progress < 1:
            progress = []
            [progress.append('=' if x < math.floor(Logger.Current_progress*100) else '>' if x == math.floor(Logger.Current_progress*100) else ' ') for x in range(100)]
            progress_text = ''.join(progress)
            print(f'Bidding progress {math.floor(Logger.Current_progress*100)}% [{progress_text}]')
