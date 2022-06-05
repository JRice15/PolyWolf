import subprocess
import numpy as np

results = {}

def print_results():
	global results
	for key in results:
		vals = ['/'.join([str(i) for i in v]) for v in results[key]]
		print('\t'.join(vals)+'\t'+key)

for i in range(1000):
	result = subprocess.run(['sh','./AutoStarter.sh'], capture_output=True, text=True)
	output = result.stdout
	tail = output[-1000:]
	lines = tail.split('\n')[:-1][-15:]
	vals = [line.split('\t') for line in lines]
	for line in vals:
		key = line[0]
		val = line[1:][:-1]
		if key not in results.keys(): results[key] = np.array([[0]*2 for _ in range(6)], dtype=np.int32)
		results[key] += np.array([[int(i) for i in frac.split('/')] for frac in val], dtype=np.int32)
	if i % 20 == 0: print_results()
