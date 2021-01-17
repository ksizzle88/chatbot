import socket
import logging
from emoji import demojize
from multiprocessing import Pool,Process
from time import sleep
import json
# token = 'oauth:xw8vwfpz3miuqk76rno8ml8nzw3pef'
class ChatLogger():
    def __init__(self,config):
        self.server = config['server']
        self.port = config['port']
        self.nickname = config['nickname']
        self.token = config['token']
        self.channel = config['channel']
        self.controller = config['controller']
        logging.basicConfig(level=logging.DEBUG,
                format='%(asctime)s — %(message)s',
                datefmt='%Y-%m-%d_%H:%M:%S',
                handlers=[logging.FileHandler(f'..\data\chat_{self.channel}.log', encoding='utf-8')])

    def connect(self):
        sock = socket.socket()
        sock.connect((self.server,self.port))
        sock.send(f"PASS {self.token}\n".encode('utf-8'))
        sock.send(f"NICK {self.nickname}\n".encode('utf-8'))
        sock.send(f"JOIN {self.channel}\n".encode('utf-8'))
        self.sock = sock

    def disconnect(self):
        self.sock.close()

    def collect(self):
        print(f'turned on {self.channel}')
        for i in range(3):
            print(self.controller.status[self.channel[1:]])
            resp = self.sock.recv(2048).decode('utf-8')
            if resp.startswith('PING'):
                self.sock.send("PONG\n".encode('utf-8'))

            elif len(resp) > 0:
                logging.info(demojize(resp))
        print (f'shutting down {self.channel}')

    def run(self):
        errors = ['[WinError 10054] An existing connection was forcibly closed by the remote host',
                '[WinError 10053] An established connection was aborted by the software in your host machine']
        try:
            self.connect()
            self.collect()
        except Exception as e:
            print(f'chatbot error: {self.channel}')
            print(f'error code: {e}')
            if str(e) in errors:
                sleep(5)
                print('reconnecting')
                self.run()
            if self.sock: self.disconnect()

class Controller():
    config = {}
    config['server'] = 'irc.chat.twitch.tv'
    config['port'] = 6667
    config['nickname'] = 'rextramedium'
    config['token'] = 'oauth:unr65h5wpq9bn3r2s1yfzbp5ld5hk9'

    def __init__(self, file):
        self.config['controller'] = self
        if not file: file= 'status.json'
        self.file = file
        self.read_json() #sets self.status
        self.configs = []
        for channel in self.status:
            t = self.config.copy()
            t['channel'] = "#" + channel.lower()
            self.configs.append(t)

    def read_json(self):
        with open(self.file, 'r') as f:
            self.status = json.loads(f.read())
    def write_json(self):
        with open(self.file, 'w+') as f:
            json.dump(self.status, f)

    def turn_on_channel(self, channel):
        self.status[channel] = True
        config = self.configs[0]
        pool = Pool(len(self.configs))
        pool.map(run_logger,self.configs)
        print('iran')

    def turn_off_channel(self, channel):
        self.status[channel] = False

    def turn_all_on(self):
        self.status.update((k,True) for k in self.status)
    def turn_all_off(self):
        print('turning off all channels')
        self.status.update((k,False) for k in self.status)

def run_logger(config):
    chatlogger = ChatLogger(config)
    chatlogger.run()

if __name__ == '__main__':
    controller = Controller('status0.json')
    controller.turn_on_channel('imreallyimportant')
    controller.turn_all_off()








    #
    # config = {}
    # config['server'] = 'irc.chat.twitch.tv'
    # config['port'] = 6667
    # config['nickname'] = 'rextramedium'
    # config['token'] = 'oauth:unr65h5wpq9bn3r2s1yfzbp5ld5hk9'
    #
    # channels = [
    #             '27dollars',
    #             'ADifficultTruth',
    #             'AmyeC3',
    #             'BenjaminPDixon',
    #             'bleepblompBen',
    #             'BrantForLiberty',
    #             'central_committee',
    #             'ChudLogic',
    #             'ConcreteReporting',
    #             'DavidPakman',
    #             'Denims',
    #             'Destiny',
    #             'DocMidnight_',
    #             'DrHeemedOut',
    #             'DylanBurnsTV',
    #             'econgreg',
    #             'feministcritique',
    #             'HealthyGamer_GG',
    #             'iDanSimpson',
    #             'imreallyimportant',
    #             'j0elewis',
    #             'JohnnyScarlett',
    #             'LeftFlankVets',
    #             'LivPosting',
    #             'LumiRue',
    #             'M3thodsToMadness',
    #             'MartiniRita',
    #             'monkeyism',
    #             'redneq_tm',
    #             'patriotnews',
    #             'lctrfan',
    #             'bastiat',
    #             'redpill78',
    #             'brantforliberty',
    #             'lucidfoxx',
    #             'primecayes',
    #             ]
    #
    # configs = []
    # for channel in channels:
    #     t = config.copy()
    #     t['channel'] = "#" + channel.lower()
    #     configs.append(t)
    #
    # pool = Pool(len(configs))
    # pool.map(run_logger,configs)
