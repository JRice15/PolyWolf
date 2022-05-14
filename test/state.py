import os
from collections import Counter, defaultdict

def log(string):
    with open('log.txt','a') as outfile:
        outfile.write(string)
        outfile.write('\n')

def access_data(frame, *labels):
    return zip(*[frame[label].values for label in labels])

class GameState:
    def __init__(self):
        self.votes_current = defaultdict(int)
        self.votes_history = defaultdict(list)
        self.agent_vote_rating = Counter()
        self.agent_verbosity = Counter()
        try: os.remove('log.txt')
        except: pass
    def update(self, diff_data, request):
        if request == 'TALK':
            for speaker, content in access_data(diff_data, 'agent', 'text'):
                if content.startswith('VOTE Agent'):
                    speaker = int(speaker)
                    target = int(content.split('[')[1][:-1])
                    self.votes_current[speaker] = target
        if request == 'DAILY_INITIALIZE':
            actual_votes = {}
            for type, speaker, content in access_data(diff_data, 'type', 'agent', 'text'):
                if str(type) != 'vote': continue
                speaker = int(speaker)
                target = int(content.split('[')[1][:-1])
                actual_votes[speaker] = target
            for voter in actual_votes.values():
                self.votes_history[voter].append(actual_votes[voter])
            self.votes_current = {}
        if request == 'FINISH':
            pass
    def vote_tally(self):
        return Counter(self.votes_current.values())