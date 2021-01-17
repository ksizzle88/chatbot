import pandas as pd
from datetime import datetime
import codecs
import re
import matplotlib.pyplot as plt
from matplotlib_venn import venn2
from math import isnan


def parse_chatlog(file):

    data = []
    with open(file, 'r', encoding='utf-8') as f:
        lines = f.read().split('\n\n\n')

        for line in lines:
            try:
                time_logged = line.split('—')[0].strip()
                time_logged = datetime.strptime(time_logged, '%Y-%m-%d_%H:%M:%S')

                username_message = line.split('—')[1:]
                username_message = '—'.join(username_message).strip()
    #             print(username_message)
                if 'PRIVMSG' in username_message:
                    time_logged = line.split('—')[0].strip()
                    time_logged = datetime.strptime(time_logged, '%Y-%m-%d_%H:%M:%S')
                    username = username_message[1:username_message.index('!')]
                    channel = username_message.split('PRIVMSG #')[1].split(' :')[0]
                    message = username_message.split('PRIVMSG #')[1].split(' :')[1]

                    d = {
                        'dt': time_logged,
                        'channel': channel,
                        'username': username,
                        'message': message
                    }

                    data.append(d)
            except Exception as e:
                print(line)

    return pd.DataFrame(data)

def combine_all_files():
    files =  [file for file in listdir('..\\data') if '#' in file]
    print(files)
    dfs = []
    for file in files:

        dfs.append(parse_chatlog('..\\data\\' + file))
    return pd.concat(dfs)

def classify_row(row,streams):
    x = bool(row['message_x'])
    y = bool(row['message_y'])

    if x and y: return 'both'
    if x and not y: return streams[0]
    if not x and y: return streams[1]

def compare_users(streams):
    assert len(streams) == 2
    files = [f'..\\data\\chat_#{stream}.log' for stream in streams]
    dfs = [parse_chatlog(file) for file in files]
    dfs = [df.groupby('username').count()['message'].sort_values(ascending=False).reset_index() for df in dfs]
#     data = [{k:v for k,v in df.groupby('username').count()['message'].sort_values(ascending=False).iteritems()} for df in dfs]
    joined = dfs[0].merge(dfs[1], how='outer', left_on='username', right_on='username').fillna(0)
    joined['total'] = joined['message_x']+joined['message_y']
    joined['stream'] = joined.apply(lambda row: classify_row(row,streams), axis=1)
    users = [df['username'].unique() for df in dfs]
    venn2([set(userlist) for userlist in users], set_labels = streams)

    return joined.sort_values('total', ascending=False)


if __name__ == '__main__':
    get_chat_dataframe('..\data\chat_#imreallyimportant.log').to_csv('..\\data\\test.csv')
