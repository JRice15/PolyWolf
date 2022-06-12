import glob
import os
import random
import sys
import time
import logging
import argparse
from pprint import pprint
from collections import defaultdict

import numpy as np
import pandas as pd
import tensorflow as tf

if len(tf.config.list_physical_devices('GPU')):
    config = tf.compat.v1.ConfigProto()
    config.gpu_options.allow_growth = True
    session = tf.compat.v1.Session(config=config)

from sklearn.model_selection import train_test_split
from tensorflow import keras
from tensorflow.keras import Model
from tensorflow.keras import backend as K
from tensorflow.keras import callbacks, layers
from tensorflow.keras.preprocessing.sequence import pad_sequences
from tqdm import tqdm

AGENT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPO_ROOT = os.path.dirname(AGENT_ROOT)
sys.path.append(AGENT_ROOT)

from const import ROLES_5_PLAYER, ROLES_15_PLAYER

from role_estimation.data_loader import (N_INPUT_FEATURES, filter_by_role,
                                         one_hot_encode_log_features, convert_log_to_df,
                                         one_hot_encode_id, one_hot_encode_role, ROLE_LIST_15, ROLE_LIST_5)
from role_estimation.rnn_utils import MyConcat


def parse_diff_data(diff_data):
    # column indexes
    DAY = 0
    TYPE = 1
    IDX = 2
    TURN = 3
    AGENT = 4
    TEXT = 5

    output_rows = []
    # if we are medium
    all_rows = diff_data.values
    for index, row in enumerate(all_rows):
        if row[TYPE] == "execute":
            if index+1 < len(all_rows) and all_rows[index+1,TYPE] == "identify":
                # if we are medium
                # set execute text to role identified
                executed_role = all_rows[index+1, TEXT].split()[-1]
            else:
                executed_role = "ANY"
            # convert to log execute format (day, type, text)
            row = [row[DAY], "execute", row[AGENT], executed_role]
        
        elif row[TYPE] == "identify":
            # don't include this row type
            continue
    
        elif row[TYPE] == "divine":
            # convert to log format (day, type, agent, target, race)
            race = row[TEXT].split()[-1]
            row = [row[DAY], "divine", row[IDX], row[AGENT], race]
    
        elif row[TYPE] == "guard":
            # log format (day, type, agent, target, role (unknown))
            row = [row[DAY], "guard", row[IDX], row[AGENT], "N/A-Guard"]

        elif row[TYPE] == "vote":
            # convert to (day, type, agent, target)
            row = [row[DAY], "vote", row[IDX], row[AGENT]]
        
        elif row[TYPE] == "attack":
            # convert to log format (day, type, target, success)
            if index+1 < len(all_rows):
                success = str(all_rows[index+1,TYPE] == "dead").lower()
            else:
                success = "false"
            row = [row[DAY], "attack", row[AGENT], success]

        elif row[TYPE] == "attack_vote":
            # convert to log format (day, type, agent, target)
            row = [row[DAY], "attackVote", row[IDX], row[AGENT]]

        elif row[TYPE] == "dead":
            # convert to log format (day, type, target)
            row = [row[DAY], "dead", row[AGENT]]

        elif row[TYPE] == "finish":
            raise ValueError("Finish messages should never reach here")

        output_rows.append(row)

    df, role_map, winner = convert_log_to_df(output_rows)
    return df



class RoleEstimatorRNN():

    def __init__(self):
        self.model = tf.keras.models.load_model(
                f"{AGENT_ROOT}/role_estimation/pretrained_model.h5",
                custom_objects={"MyConcat": MyConcat})
        self.my_agent_id = None
        self.my_role = None
        self.game_num = 1

        self.latest_predictions = None
        self.rolewise_accs = defaultdict(lambda: defaultdict(lambda: [])) # dict maps role to dict mapping day to list of accuracies
        self.agentwise_accs = defaultdict(lambda: defaultdict(lambda: [])) # dict maps agentid to dict mapping day to list of accuracies

        self.game_start()

    def game_start(self):
        # preds at end of each day
        self.day_end_preds = []
        # rnn states for the game (with batchsize of 1)
        self.rnn_states = tf.zeros((1,) + self.model.get_layer("rnn_states").output.shape[1:])

    def game_end(self, diff_data):
        logging.info(f"{self.my_agent_id}, {self.my_role}")
        real_roles = diff_data["text"].apply(lambda x: x.split()[-1])
        real_roles.index = diff_data["agent"]
        for day,pred_df in enumerate(self.day_end_preds):
            if pred_df is None:
                continue
            # role-wise
            for role,count in ROLES_15_PLAYER.items():
                preds = pred_df[role].nlargest(n=count).index
                real = real_roles[real_roles == role].index
                acc = np.mean([x in real for x in preds])
                self.rolewise_accs[role][day].append(acc)
            # agent-wise
            for agent in real_roles.index:
                pred = pred_df.columns[pred_df.loc[agent].argmax()]
                true = real_roles.loc[agent]
                self.agentwise_accs[agent][day].append(pred == true)
        # display
        logging.info(f"\nGame {self.game_num} accuracies:")
        logging.info(f"per role:")
        rolewise_df = pd.DataFrame(self.rolewise_accs).applymap(np.mean).sort_index()
        rolewise_df.index.name = "day"
        logging.info("\n" + str(rolewise_df))
        logging.info(f"per agent:")
        agentwise_df = pd.DataFrame(self.agentwise_accs).applymap(np.mean).sort_index()
        agentwise_df.index.name = "day"
        logging.info("\n" + str(agentwise_df))

        self.game_num += 1

    
    def update_and_predict(self, *, base_info, diff_data, request):
        self.my_agent_id = base_info["agentIdx"]
        self.my_role = base_info["myRole"]

        if (request == "FINISH"):
            self.game_end(diff_data)
            self.game_start()
            return self.latest_predictions

        if len(diff_data):
            diff_data = parse_diff_data(diff_data)

            # make sure it wasn't just "Over"'s and such
            if len(diff_data):
                # convert dataframe to tf array
                input_features = one_hot_encode_log_features(diff_data)
                my_role = one_hot_encode_role(self.my_role)
                my_id = one_hot_encode_id(self.my_agent_id)

                inputs = {
                    "features": input_features[tf.newaxis], # add 1-size batch dims
                    "my_role": my_role[tf.newaxis],
                    "my_id": my_id[tf.newaxis],
                    "rnn_states": self.rnn_states,
                }

                outputs = self.model(inputs)
                self.rnn_states = outputs["rnn_states"]
                preds = outputs["preds"][0,-1].numpy() # select first (only) batch, and last step for most up-to-date predictions predictions

                self.latest_predictions = pd.DataFrame(preds, columns=ROLE_LIST_15, index=range(1,16))

        if request == "DAILY_FINISH":
            self.day_end_preds.append(self.latest_predictions)

        return self.latest_predictions


