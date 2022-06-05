# Takes a rounds.py file of collated results, and make graphs from it.

import sys
import matplotlib.pyplot as plt
import numpy as np
import matplotlib as mpl

import pandas as pd
import seaborn


ROLES = [
    'Bodyguard',
    'Medium',
    'Possessed',
    'Seer',
    'Villager',
    'Werewolf',
]

GOOD = ["Bodyguard", "Medium", "Seer", "Villager"]
EVIL = ["Werewolf", "Possessed"]


# ROLE_MAP = {
#     'Bodyguard':
#     'Medium':
#     'Possessed':
#     'Seer':
#     'Villager':
#     'Werewolf':
# }

with open(sys.argv[1],'r') as infile:
    text = infile.read()

blocks = text.split('===')

lines = [line for line in blocks[1].split('\n') if line != '']
vals = [line.split('\t') for line in lines]

df = pd.DataFrame(vals, columns=ROLES + ["name"])
df = df.set_index("name")

print(df)

win_counts = df.applymap(lambda x: int(x.split("/")[0]))
play_counts = df.applymap(lambda x: int(x.split("/")[1]))


# overall win rate
overall = win_counts.sum(axis=1) / play_counts.sum(axis=1)
overall = overall.sort_values(ascending=False)
colors = ["forestgreen" if x == "PolyWolf" else "darkturquoise" for x in overall.index]
seaborn.barplot(y=overall.index, x=overall.values, palette=colors)
plt.title("Overall win rate")
plt.tight_layout()
plt.show()


# role-wise win rates
win_rates = win_counts / play_counts
win_rates["color"] = ["forestgreen" if x == "PolyWolf" else "darkturquoise" for x in win_rates.index]
for col in ROLES:
    win_rates = win_rates.sort_values(by=col, ascending=False)
    seaborn.barplot(data=win_rates, y=win_rates.index, x=col, palette=win_rates["color"])
    plt.title(col + " win rate")
    plt.tight_layout()
    plt.show()
