# Takes a rounds.py file of collated results, and make graphs from it.

import sys
import matplotlib.pyplot as plt
import numpy as np
import matplotlib as mpl

import seaborn
seaborn.set()

LOOKUP = {
    0:'bodyguard',
    1:'medium',
    2:'possessed',
    3:'seer',
    4:'villager',
    5:'werewolf',
}

with open(sys.argv[1],'r') as infile:
    text = infile.read()

blocks = text.split('===')

lines = [line for line in blocks[1].split('\n') if line != '']
vals = [line.split('\t') for line in lines]

counts = {}
for line in vals:
    key = line[-1]
    val = line[:-1]
    val = [[int(i) for i in frac.split('/')] for frac in val]
    counts[key] = {}
    for role in LOOKUP:
        counts[key][f'{LOOKUP[role]} win rate'] = val[role][0] / val[role][1]
    counts[key]['town win rate'] = (val[0][0] + val[1][0] + val[3][0] + val[4][0]) / (val[0][1] + val[1][1] + val[3][1] + val[4][1])
    counts[key]['evil win rate'] = (val[2][0] + val[5][0]) / (val[2][1] + val[5][1])
    counts[key]['town rate'] = (val[0][1] + val[1][1] + val[3][1] + val[4][1]) / sum([pair[1] for pair in val])
    counts[key]['win rate'] = sum([pair[0] for pair in val]) / sum([pair[1] for pair in val])

# Graph 1: Town Rate vs. Win Rate
plt.rcParams.update({'font.size': 14})

labels = counts.keys()
x = np.array([float(counts[key]['town rate']) for key in labels])
y = np.array([float(counts[key]['win rate']) for key in labels])

fig, ax = plt.subplots()
ax.scatter(x, y)

plt.xlabel("town rate")
plt.ylabel("win rate")

for i, txt in enumerate(labels):
    ax.annotate(txt, (x[i], y[i]), fontsize=8)

plt.title(f"Pearson Correlation Coefficient: {np.corrcoef(x,y)[0][1]:.5f}", fontsize=16)
plt.show()

# Graph 2: Town Win Rate vs. Win Rate
plt.rcParams.update({'font.size': 14})

labels = counts.keys()
x = np.array([float(counts[key]['town win rate']) for key in labels])
y = np.array([float(counts[key]['win rate']) for key in labels])

fig, ax = plt.subplots()
ax.scatter(x, y)

plt.xlabel("town win rate")
plt.ylabel("win rate")

for i, txt in enumerate(labels):
    ax.annotate(txt, (x[i], y[i]), fontsize=8)

plt.title(f"Pearson Correlation Coefficient: {np.corrcoef(x,y)[0][1]:.5f}", fontsize=16)
plt.show()


# voting accuracy
voting = [line.strip().split("\t") for line in blocks[2].split("\n") if line.strip() != ""]
names = [x[1] for x in voting]
accs = [x[0].split("/") for x in voting]
accs = [int(x[0]) / int(x[1]) for x in accs]

sorted_accs = sorted(zip(names, accs), key=lambda x: x[1], reverse=False)
names, accs = zip(*sorted_accs)

bars = plt.barh(names, accs, align="center")
plt.xlim(min(accs) - 0.05, max(accs) + 0.08)
plt.xlabel("Voting accuracy")
plt.gca().bar_label(bars, fmt="%.3f", padding=3)
plt.tight_layout()
plt.show()
