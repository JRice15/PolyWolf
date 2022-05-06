import numpy as np
import pandas as pd
import argparse
import glob
import os, sys
import csv


AGENT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPO_ROOT = os.path.dirname(AGENT_ROOT)
sys.path.append(AGENT_ROOT)

CONST_FMT = ("day", "type")
# formats of columns past zero and one, which are always day and type
FORMATS = {
    # special types that are filtered out of the main df
    "status": ("agent_id", "role", "status", "name"),
    "result": ("human_remaining", "werewolf_remaining", "result"),
    # regular actions
    "whisper": ("idx", "turn", "agent_id", "content"),
    "divine": ("agent_id", "target_id", "divine_result"),
    "talk": ("idx", "turn", "agent_id", "content"),
    "vote": ("agent_id", "target_id"),
    "execute": ("target_id", "role"),
    "guard": ("agent_id", "target_id", "role"),
    "attackVote": ("agent_id", "target_id"),
    "attack": ("target_id", "attack_success"),
}
# datatypes for each column, if not string
DTYPES = {
    "day": int,
    "idx": float,
    "turn": float,
    "agent_id": float,
    "target_id": float,
}

def read_one_log(log_path):
    with open(log_path, newline='') as csvfile:
        log_reader = csv.reader(csvfile, delimiter=',')
        
        role_map = {}
        winner = None
        parsed_rows = []
        for row in log_reader:
            if len(row):
                kind = row[1]
                fmt = CONST_FMT + FORMATS[kind]
                parsed = dict(zip(fmt, row))
                # save roles on day zero
                if kind == "status":
                    if parsed["day"] == "0":
                        role_map[int(parsed["agent_id"])] = parsed["role"]
                elif kind == "result":
                    winner = parsed["result"]
                else:
                    parsed_rows.append(parsed)

    df = pd.DataFrame(parsed_rows)
    for col, dtype in DTYPES.items():
        df[col] = df[col].astype(dtype)
    
    def str2bool(x):
        if x == "true":
            return True
        elif x == "false":
            return False
        return x
    df.attack_success = df.attack_success.apply(str2bool)

    return df, role_map, winner

def read_logs(log_dir):
    """
    args:
        log_dir: path to folder containing *.log files (log_dir must end with a slash)
    returns:
        log dataframe, role map, winner
    """
    full_df = None
    full_roles = []
    logfiles = sorted(glob.glob(log_dir + "???.log"))
    if not len(logfiles):
        raise FileNotFoundError("No logs match " + log_dir + "???.log")
    for i,log in enumerate(logfiles):
        df, roles, _ = read_one_log(log)
        full_roles.append(roles)
        # this adds a multiindex level to the df
        df = pd.concat([df], keys=[i], names=["game"])
        if full_df is None:
            full_df = df
        else:
            full_df = pd.concat([full_df, df], axis=0)
    
    full_roles = pd.DataFrame(full_roles)
    full_roles.index.name = "game_num"
    return full_df, full_roles


if __name__ == "__main__":
    sim_dirs = glob.glob(f"{REPO_ROOT}/sims/15player_100game/random/*/logs/")

    log_df, roles_df = read_logs(sim_dirs[0])

    print(log_df)
    print(roles_df)