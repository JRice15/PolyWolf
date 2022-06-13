import os
import sys
import fcntl
import random
import subprocess
import threading
import numpy as np
import time
from filelock import FileLock

out = sys.argv[1]

MULTIPROCESS_COUNT = 1 #26
 
sets_complete = 0
win_results = {}
acc_results = {}
port = random.randint(1,1000)

with open('AutoStarter.template', 'r') as infile:
	template = infile.read()

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
		outfile.write('===\n')
		for key in acc_results:
			val = '/'.join([str(i) for i in acc_results[key]])
			outfile.write(val+'\t'+key+'\n')

def run_proc():
	global sets_complete
	global win_results
	global acc_results
	global port
	start = time.time()
	with FileLock('AutoStarter.ini'):
		with open('AutoStarter.ini','w') as outfile:
			outfile.write(f'port={10000+port}\n')
			outfile.write(template)
			outfile.write(f'PolyWolf,python,../our_agent/polywolf.py\n') #-{out}
			#port += 1
	print('LOCK HANDLED SUCCESSFULLY')
	with subprocess.Popen(["sh", "./AutoStarter.sh"], stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.PIPE) as process:
		try:
			stdout, stderr = process.communicate(timeout=500)
		except subprocess.TimeoutExpired:
			print('TIMEOUT EXPIRED')
			process.kill()
			print('PROCESS KILLED')
			
			fd = process.stdout.fileno()
			fl = fcntl.fcntl(fd, fcntl.F_GETFL)
			fcntl.fcntl(fd, fcntl.F_SETFL, fl | os.O_NONBLOCK)

			fd = process.stderr.fileno()
			fl = fcntl.fcntl(fd, fcntl.F_GETFL)
			fcntl.fcntl(fd, fcntl.F_SETFL, fl | os.O_NONBLOCK)

			stdout = process.stdout.read()
			stderr = process.stdout.read()
			print('OUTPUT RETRIEVED')
			#stdout, stderr = process.communicate()
			#print(stdout[-5000:].decode("utf-8"))
			#print(stderr[-5000:].decode("utf-8"))
		except Exception:
			print('Aaaaaaaaaaaaaa')
			process.kill()
			process.wait()
			raise
	#result = subprocess.run(["sh", "./AutoStarter.sh"], capture_output=True, text=True, timeout=400)
	output = stdout #result.stdout
	tail = output[-5000:].decode("utf-8")
	print(tail)
	print('\n\n')
	print(stderr.decode('utf-8'))
	print('\n')
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
		pid = int(line[0].split('[')[1].split(']')[0])
		id_table[pid] = line[1]
		if 'PolyWolf' in line[1]:
			log_id = line[1].split('-')[1]
			id_table[pid] = line[1].split('-')[0]
	print(id_table)
	with open(f'python_trace/log{log_id}.txt', 'r') as infile:
		text = infile.read()
		tail = text[-1000:]
		lines = tail.split('\n')[:-1][-15:]
		for line in lines:
			vals = line.split(':')
			key = int(vals[0])
			acc = [int(val) for val in vals[1].split('/')]
			if id_table[key] not in acc_results.keys(): acc_results[id_table[key]] = np.array([0,0], dtype=np.int32)
			acc_results[id_table[key]] += np.array(acc, dtype=np.int32)
	os.remove(f'python_trace/log{log_id}.txt')
	sets_complete += 1
	record_results()
	end = time.time()
	print(f'completed a round in {end - start} seconds')

running_procs = []

try:
	while True:
		time.sleep(3)
		print(len(running_procs))
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