import os
import sys
import subprocess
import threading
import numpy as np
import time

out = sys.argv[1]

MULTIPROCESS_COUNT = 2 #26
 
sets_complete = 0
win_results = {}
acc_results = {}

def record_results():
	global sets_complete
	global win_results
	global acc_results
	with open(f'rounds_results/{out}.txt', 'w') as outfile:
		outfile.write(f'{sets_complete} GAME SETS COMPLETED\n')
		outfile.write('===\n')
		for key in win_results:
			vals = ['/'.join([str(i) for i in v]) for v in win_results[key]]
			outfile.write('\t'.join(vals)+'\t'+key+'\n')
		outfile.write('===')
		for key in acc_results:
			val = '/'.join([str(i) for i in acc_results[key]])
			outfile.write(val+'\t'+key)

def run_proc():
	global sets_complete
	global win_results
	global acc_results
	start = time.time()
	result = subprocess.run(["sh", "./AutoStarter.sh"], capture_output=True, text=True)
	output = result.stdout
	tail = output[-5000:]
	lines = tail.split('\n')[:-1][-15:]
	vals = [line.split('\t') for line in lines]
	for line in vals:
		key = line[0]
		if 'PolyWolf' in key: key = key.split('-')[0]
		val = line[1:][:-1]
		if key not in win_results.keys(): win_results[key] = np.array([[0]*2 for _ in range(6)], dtype=np.int32)
		win_results[key] += np.array([[int(i) for i in frac.split('/')] for frac in val], dtype=np.int32)
	lines = tail.split('\n')[:-1][-39:-24]
	vals = [line.split('\t') for line in lines]
	id_table = {}
	for line in vals:
		pid = int(val[0].split('[')[1].split(']')[0])
		if 'PolyWolf' in val[1]:
			log_id = val[1].split('-')[1]
			pid = val[1].split('-')[0]
		id_table[pid] = val[1]
	with open(f'python_trace/log{log_id}.txt', 'r') as infile:
		text = infile.read()
		tail = text[-1000:]
		lines = tail.split('\n')[:-1][-15:]
		for line in lines:
			vals = line.split(':')
			key = vals[0]
			acc = [int(val) for val in vals[1].split('/')]
			if key not in acc_results.keys(): acc_results[key] = np.array([0,0], dtype=np.int32)
			acc_results[key] += np.array(acc, dtype=np.int32)
	os.remove(f'python_trace/log{log_id}.txt')
	sets_complete += 1
	record_results()
	end = time.time()
	print(f'completed a round in {end - start} seconds')

running_procs = []

try:
	while True:
		time.sleep(3)
		while len(running_procs) < MULTIPROCESS_COUNT:
			proc = threading.Thread(target=run_proc)
			proc.start()
			running_procs.append(proc)
		time.sleep(3)
		finished = []
		for i, proc in enumerate(running_procs):
			if not proc.is_alive():
				finished.append(i)
		for i in finished:
			del running_procs[i]
except Exception as e:
	print(e)
	for proc in running_procs:
		proc.join()