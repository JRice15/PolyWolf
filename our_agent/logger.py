import os

filename = ''

def reserve_id():
    global filename
    idx = 0
    while os.path.exists(f'python_trace/log{idx}.txt'):
        idx += 1
    filename = f'python_trace/log{idx}.txt'
    with open(filename,'w') as outfile:
        outfile.write('')
    return idx

def log(string):
    with open(filename,'a') as outfile:
        outfile.write(str(string))
        outfile.write('\n')
