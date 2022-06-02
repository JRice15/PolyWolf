import os

try: os.remove('log.txt')
except: pass

def log(string):
    with open('log.txt','a') as outfile:
        outfile.write(string)
        outfile.write('\n')
