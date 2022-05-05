import numpy as np
import pandas as pd
import argparse
import glob
import os, sys

import tensorflow as tf
from tensorflow import keras

AGENT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPO_ROOT = os.path.dirname(AGENT_ROOT)
sys.path.append(AGENT_ROOT)


def read_log(log_path):    
    with open(log_path, newline='') as csvfile:
        log_reader = csv.reader(csvfile, delimiter=',')
        agent_ = []
        day_ = []
        type_ = []
        idx_ = []
        turn_ = []
        text_ = []

        # for medium result
        medium = 0
        for row in log_reader:
            if row[1] == "status" and int(row[0]) == 0:
                agent_.append(int(row[2])), 
                day_.append(int(row[0])), 
                type_.append('initialize'), 
                idx_.append(int(row[2])), 
                turn_.append(0), 
                text_.append('COMINGOUT Agent[' + "{0:02d}".format(int(row[2])) + '] ' + row[3])
                # medium
                if row[3] == "MEDIUM":
                    medium = row[2]
            elif row[1] == "status":
                pass
            elif row[1] == "talk":
                agent_.append(int(row[4])), 
                day_.append(int(row[0])), 
                type_.append('talk'), 
                idx_.append(int(row[2])), 
                turn_.append(int(row[3])), 
                text_.append(row[5])
            elif row[1] == "whisper":
                agent_.append(int(row[4])), 
                day_.append(int(row[0])), 
                type_.append('whisper'), 
                idx_.append(int(row[2])), 
                turn_.append(int(row[3])), 
                text_.append(row[5])
            elif row[1] == "vote":
                agent_.append(int(row[3])), 
                day_.append(int(row[0])), 
                type_.append('vote'), 
                idx_.append(int(row[2])), 
                turn_.append(0), 
                text_.append('VOTE Agent[' + "{0:02d}".format(int(row[3])) + ']')
            elif row[1] == "attackVote":
                agent_.append(int(row[3])), 
                day_.append(int(row[0])), 
                type_.append('attack_vote'), 
                idx_.append(int(row[2])), 
                turn_.append(0), 
                text_.append('ATTACK Agent[' + "{0:02d}".format(int(row[3])) + ']')
            elif row[1] == "divine":
                agent_.append(int(row[3])), 
                day_.append(int(row[0])), 
                type_.append('divine'), 
                idx_.append(int(row[2])), 
                turn_.append(0), 
                text_.append('DIVINED Agent[' + "{0:02d}".format(int(row[3])) + '] ' + row[4])
            elif row[1] == "execute":
                # for all
                agent_.append(int(row[2])), 
                day_.append(int(row[0])), 
                type_.append('execute'), 
                idx_.append(0), 
                turn_.append(0), 
                text_.append('Over')
                # for medium
                res = 'HUMAN'
                if row[3] == 'WEREWOLF':
                    res = 'WEREWOLF'
                agent_.append(int(row[2])), 
                day_.append(int(row[0])), 
                type_.append('identify'), 
                idx_.append(medium), 
                turn_.append(0), 
                text_.append('IDENTIFIED Agent[' + "{0:02d}".format(int(row[2])) + '] ' + res)
            elif row[1] == "guard":
                agent_.append(int(row[3])), 
                day_.append(int(row[0])), 
                type_.append('guard'), 
                idx_.append(int(row[2])), 
                turn_.append(0), 
                text_.append('GUARDED Agent[' + "{0:02d}".format(int(row[3])) + ']')
            elif row[1] == "attack":
                agent_.append(int(row[2])), 
                day_.append(int(row[0])), 
                type_.append('attack'), 
                idx_.append(0), 
                turn_.append(0), 
                text_.append('ATTACK Agent[' + "{0:02d}".format(int(row[2])) + ']')
                if row[3] == 'true':
                    # dead
                    agent_.append(int(row[2])), 
                    day_.append(int(row[0])), 
                    type_.append('dead'), 
                    idx_.append(0), 
                    turn_.append(0), 
                    text_.append('Over')
            elif row[1] == "result":
                pass
            else:
                pass


    return pd.DataFrame({"day":day_, "type":type_, "idx":idx_, "turn":turn_, "agent":agent_, "text":text_})


# df = read_log(log_dir + "/000.log")

# print(df)

def read_log(path):
    df = pd.read_csv(path, header=None)
    df.columns = ["day", "type", "col2", "col3", "col4", "col5"]

    day_zero = df[df.day == 0]

    role_map = day_zero[day_zero.type == "status"] \
                .rename(columns={"col3": "role", "col5": "name"}) \
                .set_index("name")["role"] \
                .to_dict()

    print(role_map)

    result = df[df.type == "result"]["col4"].item()

    print(result)

    df = df[df.type.apply(lambda x: x not in ("status", "result"))]

    print(df)

    return df, result

log_dir = glob.glob(f"{REPO_ROOT}/sims/random/*/logs/")[0]
path = log_dir + "000.log"

read_log(path)

