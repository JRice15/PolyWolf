# Takes a file containing the last few lines of the AutoStarter.sh output, and calculates some interesting observations based on those things.

import sys
import matplotlib.pyplot as plt
import numpy as np

with open(sys.argv[1],'r') as infile:
    text = infile.read()

lines = [line for line in text.split('\n') if line != '']
vals = [line.split('\t') for line in lines]

counts = {}
for line in vals:
    key = line[0]
    val = line[1:][:-1]
    val = [[int(i) for i in frac.split('/')] for frac in val]
    counts[key] = {}
    counts[key]['town win rate'] = (val[0][0] + val[1][0] + val[3][0] + val[4][0]) / (val[0][1] + val[1][1] + val[3][1] + val[4][1])
    counts[key]['evil win rate'] = (val[2][0] + val[5][0]) / (val[2][1] + val[5][1])
    counts[key]['town rate'] = (val[0][1] + val[1][1] + val[3][1] + val[4][1]) / sum([pair[1] for pair in val])
    counts[key]['win rate'] = line[-1]

for key in counts:
    print(f'{key}')
    print(f'\tWin Rate: {counts[key]["win rate"]}')
    print(f'\tTown Rate: {counts[key]["town rate"]}')
    print(f'\tTown Win Rate: {counts[key]["town win rate"]}')
    print(f'\tEvil Win Rate: {counts[key]["evil win rate"]}')

labels = counts.keys()
x = np.array([float(counts[key]['town rate']) for key in labels])
y = np.array([float(counts[key]['win rate']) for key in labels])

fig, ax = plt.subplots()
ax.scatter(x, y)

plt.xlabel("town rate")
plt.ylabel("win rate")

for i, txt in enumerate(labels):
    ax.annotate(txt, (x[i], y[i]))


title_string = "This is the title"
subtitle_string = "This is the subtitle"

plt.title(f"Covariance: {np.cov(x,y)[0][1]:.5f}", fontsize=10)
plt.show()

labels = counts.keys()
x = np.array([float(counts[key]['town win rate']) for key in labels])
y = np.array([float(counts[key]['win rate']) for key in labels])

fig, ax = plt.subplots()
ax.scatter(x, y)

plt.xlabel("town win rate")
plt.ylabel("win rate")

for i, txt in enumerate(labels):
    ax.annotate(txt, (x[i], y[i]))

plt.title(f"Covariance: {np.cov(x,y)[0][1]:.5f}", fontsize=10)
plt.show()