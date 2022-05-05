import pandas as pd
import numpy as np
import glob
import argparse

def strip_num(x):
    return x.rstrip("0123456789")

def init_df(root):
    df = pd.read_csv(root+"000.log", header=None)

    roles_df = df[(df[0] == 0) & (df[1] == "status")]

    names = roles_df[5].to_list()
    names = sorted(list(set([strip_num(x) for x in names])))
    roles = sorted(list(set(roles_df[3].to_list())))

    data = np.zeros((len(names), len(roles)))
    plays_df = pd.DataFrame(data.copy(), columns=roles, index=names)
    wins_df = pd.DataFrame(data.copy(), columns=roles, index=names)

    return plays_df, wins_df

def analyze_logs(root):
    plays_df, wins_df = init_df(root)

    for file in glob.glob(root+"*.log"):
        df = pd.read_csv(file, header=None)
        winning_team = df[df[1] == "result"][4].item()
        roles_df = df[(df[0] == 0) & (df[1] == "status")]

        names = roles_df[5].to_list()
        names = [strip_num(x) for x in names]
        roles = roles_df[3].to_list()
        for name,role in zip(names, roles):
            plays_df.loc[name, role] += 1
            if winning_team == 'WEREWOLF':
                if role in ('POSSESSED', 'WEREWOLF'):
                    wins_df.loc[name, role] += 1
            else:
                if role not in ('POSSESSED', 'WEREWOLF'):
                    wins_df.loc[name, role] += 1

    plays_df["total"] = plays_df.sum(axis=1)
    wins_df["total"] = wins_df.sum(axis=1)

    print("Wins:")
    print(wins_df)
    print("Plays:")
    print(plays_df)

    avg_df = wins_df / plays_df

    print("Winning pcts:")
    print(avg_df)
    print(avg_df[["total"]])

 

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("path",help="path to logs dir")
    ARGS = parser.parse_args()
    analyze_logs(ARGS.path)
