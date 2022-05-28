import argparse
import csv
import glob
import os
import re
import sys

import numpy as np
import pandas as pd
import tensorflow as tf
from tensorflow.keras import backend as K

AGENT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPO_ROOT = os.path.dirname(AGENT_ROOT)
sys.path.append(AGENT_ROOT)

from const import ROLES_15_PLAYER, ROLES_5_PLAYER

CONST_FMT = ("day", "action")
# formats of columns past zero and one, which are always day and action
FORMATS = {
    # special action that are filtered out of the main df
    "status":   ("agent_id", "role", "status", "name"),
    "result":   ("human_remaining", "werewolf_remaining", "winning_team"),
    # talk actions
    "whisper":  ("idx", "turn", "agent_id", "content"),
    "talk":     ("idx", "turn", "agent_id", "content"),
    # other actions
    "execute":  ("target_id", "medium_result"),
    "divine":   ("agent_id", "target_id", "divine_result"),
    "attack":   ("target_id", "attack_success"),
    "guard":    ("agent_id", "target_id", "guarded_role"),
    "vote":     ("agent_id", "target_id"),
    "attackVote": ("agent_id", "target_id"),
    # custom log entries that only come from diff_data, not logs
    "dead": ("target_id",)
}

# all actions possible in parsed logs
ALL_ACTIONS = sorted([
    "talk",
    "vote",
    "execute",
    "guard",
    "medium_result",
    "divine",
    "divine_result",
    "whisper",
    "attack",
    "attack_result",
    "attackVote",
    "dead",
])

# what actions each role has visible to them
ALL_VISIBILITY = ["talk", "vote", "execute", "dead"]
ROLE_VISIBILITY = {
    "BODYGUARD": ["guard"],
    "MEDIUM": ["medium_result"],
    "SEER": ["divine", "divine_result",],
    "POSSESSED": [],
    "VILLAGER": [],
    "WEREWOLF": ["whisper", "attack", "attackVote"],
}

# load vocabulary
file = f"{AGENT_ROOT}/role_estimation/vocab.txt"
with open(file, "r") as f:
    VOCAB = f.readlines()
VOCAB = [w.strip() for w in VOCAB]
VOCAB = [w for w in VOCAB if len(w) and w[0] != "#"]
VOCAB = {v:i for i,v in enumerate(VOCAB)}

# total features
N_INPUT_FEATURES = 15 + 1 + len(ALL_ACTIONS) + len(VOCAB) # TODO 5 players


ROLE_LIST_15 = sorted(list(ROLES_15_PLAYER.keys()))
ROLE_LIST_5 = sorted(list(ROLES_5_PLAYER.keys()))



def content_to_tokens(content):
    """
    extract words and parentheses
    """
    return re.findall(r"\)|\(|[\]\[\w]+", content)

def fmtagent(num):
    return f"Agent[{num:>02}]"


def convert_log_to_df(log_rows, drop_skips=True):
    role_map = {}
    winner = None
    columns = ("action", "msg_start", "agent_id", "content")
    all_rows = []
    for row in log_rows:
        if len(row):
            action = row[1]
            fmt = CONST_FMT + FORMATS[action]
            parsed_row = dict(zip(fmt, row))

            # save roles on day zero
            if action == "status":
                if parsed_row["day"] == "0":
                    role_map[int(parsed_row["agent_id"])] = parsed_row["role"]
                continue

            if "agent_id" in parsed_row:
                parsed_row["agent_id"] = fmtagent(parsed_row["agent_id"])
            if "target_id" in parsed_row:
                parsed_row["target_id"] = fmtagent(parsed_row["target_id"])

            # get winner
            if action == "result":
                winner = parsed_row["winning_team"]
            
            # handle arbitrary text content
            elif action in ("talk", "whisper"):
                content = parsed_row["content"]
                # drop Overs and maybe Skips
                if content.lower() == "over" or (drop_skips and content.lower() == "skip"):
                    continue

                # turn DAY N into DAY
                content = re.sub(r"DAY \d+", "DAY", content)
                tokens = content_to_tokens(content)
                first = 1
                for tok in tokens:
                    new_row = [action, first, parsed_row["agent_id"], tok]
                    all_rows.append(new_row)
                    first = 0
            
            # actions that should result in multiple rows
            elif action == "execute":
                execute_row = ["execute", 1, np.nan, parsed_row['target_id']]
                medium_row = ["medium_result", 0, np.nan, parsed_row["medium_result"]]
                all_rows += [execute_row, medium_row]
            elif action == "divine":
                divine_row = ["divine", 1, parsed_row["agent_id"], parsed_row['target_id']]
                result_row = ["divine_result", 0, np.nan, parsed_row['divine_result']]
                all_rows += [divine_row, result_row]
            elif action == "attack":
                attack_row = ["attack", 1, np.nan, parsed_row['target_id']]
                all_rows.append(attack_row)
                if parsed_row["attack_success"] == "true":
                    dead_row = ["dead", 1, np.nan, parsed_row["target_id"]]
                    all_rows.append(dead_row)

            elif action == "dead":
                # check it wasn't already added by the attack action above
                if not len(all_rows) or all_rows[-1][0] != "dead":
                    all_rows.append(["dead", 1, np.nan, parsed_row["target_id"]])

            # other random results
            elif action == "guard":
                row = [action, 1, parsed_row["agent_id"], parsed_row["target_id"]]
                all_rows.append(row)
            elif action in ("vote", "attack", "attackVote"):
                row = [action, 1, parsed_row["agent_id"], parsed_row["target_id"]]
                all_rows.append(row)
            else:
                raise TypeError("Unhandled row: {}".format(parsed_row))

    df = pd.DataFrame(all_rows, columns=columns)
    # df["msg_start"] = df["msg_start"].astype(int)
    # df["action"] = df["action"].str.upper()

    return df, role_map, winner


def read_one_log(log_path, drop_skips=True):
    with open(log_path, newline='') as csvfile:
        log_reader = csv.reader(csvfile, delimiter=',')
        return convert_log_to_df(log_reader, drop_skips=drop_skips)
        



def read_logs(log_dir, drop_skips=True):
    """
    args:
        log_dir: path to folder containing *.log files (log_dir must end with a slash)
        drop_skips: remove "Skip" utterances
    returns:
        log dataframe, role map, winner
    """
    full_df = None
    full_roles = []
    logfiles = sorted(glob.glob(log_dir + "???.log"))
    if not len(logfiles):
        raise FileNotFoundError("No logs match " + log_dir + "???.log")
    for i,log in enumerate(logfiles):
        df, roles, _ = read_one_log(log,
                        drop_skips=drop_skips)

        full_roles.append(roles)
        # this adds a multiindex level to the df
        df = pd.concat([df], keys=[i], names=["game"])
        if full_df is None:
            full_df = df
        else:
            full_df = pd.concat([full_df, df], axis=0)
    
    full_roles = pd.DataFrame(full_roles)
    full_roles.index.name = "game"
    return full_df, full_roles


def one_hot_encode_log_features(df, sparse=False):
    """
    encode log df into one-hot vectors
    args:
        dataframe
    returns:
        tensorflow array
    """
    assert df.shape[-1] == 4
    actions = df["action"].map(ALL_ACTIONS.index).to_numpy()
    msg_start = df["msg_start"].to_numpy()
    agent_id = df["agent_id"].map(VOCAB.__getitem__, na_action='ignore').to_numpy()
    content = df["content"].map(VOCAB.__getitem__).to_numpy()

    if sparse:
        actions = tf.sparse.from_dense(actions)
        msg_start = tf.sparse.from_dense(msg_start)
        agent_id = tf.sparse.from_dense(agent_id)
        content = tf.sparse.from_dense(content)

    actions = tf.one_hot(actions, depth=len(ALL_ACTIONS))
    msg_start = tf.cast(tf.expand_dims(msg_start, axis=-1), K.floatx()) # already 0-1 coded
    agent_id = tf.one_hot(agent_id, depth=15) # TODO 5 players?
    content = tf.one_hot(content, depth=len(VOCAB))

    arr = tf.concat([actions, msg_start, agent_id, content], axis=-1)
    return arr

def one_hot_encode_role(my_role, n_players=15):
    """
    args:
        my_role: string, all caps role
    """
    if n_players == 15:
        role_list = ROLE_LIST_15
    else:
        role_list = ROLE_LIST_5
    return tf.one_hot(role_list.index(my_role), depth=len(role_list))


def one_hot_encode_id(my_id, n_players=15):
    """
    args:
        my_id: int, from 1 to 15 inclusive
    """
    return tf.one_hot(my_id-1, depth=n_players)



def filter_by_role(df, role):
    """
    return a dataframe with only the actions visible to this role
    """
    visible_actions = ALL_VISIBILITY + ROLE_VISIBILITY[role]
    return df[df["action"].apply(lambda x: x.lower() in visible_actions)]





if __name__ == "__main__":
    print(VOCAB)

    sim_dirs = glob.glob(f"{REPO_ROOT}/sims/15player_100game/random/*/logs/")
    log_df, roles_df = read_logs(sim_dirs[3], drop_skips=True)

    print(log_df)

    a = one_hot_encode_log_features(log_df.loc[0])

    print(a)
    print(a.shape)

    # print(roles_df)

    # print("combined average game length:", np.mean([len(log_df.loc[game]) for game in range(100)]))

    # vill_df = filter_by_role(log_df, "VILLAGER")
    # print("villager average game length:", np.mean([len(vill_df.loc[game]) for game in range(100)]))

    # werewolf_df = filter_by_role(log_df, "WEREWOLF")
    # print("werewolf average game length:", np.mean([len(werewolf_df.loc[game]) for game in range(100)]))
    
    # print(log_df["action"].drop_duplicates().reset_index(drop=True))