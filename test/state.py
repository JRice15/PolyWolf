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
        self.player_list = []
        self.votes_current = defaultdict(int)
        self.votes_history = defaultdict(list)
        self.voter_accuracy_village = Counter()
        self.voter_accuracy_wolf = Counter()
        self.votes_total_village = Counter()
        self.votes_total_wolf = Counter()
        #self.agent_verbosity = Counter()
        try: os.remove('log.txt')
        except: pass
    def get_agent(self, text):
        return int(text.split('[')[1].split(']')[0])
    def update(self, diff_data, request):
        if request == 'TALK':
            for speaker, content in access_data(diff_data, 'agent', 'text'):
                if content.startswith('VOTE Agent'):
                    speaker = int(speaker)
                    target = self.get_agent(content)
                    self.votes_current[speaker] = target
        if request == 'DAILY_INITIALIZE':
            actual_votes = {}
            for type, speaker, content in access_data(diff_data, 'type', 'idx', 'text'):
                if str(type) != 'vote': continue
                speaker = int(speaker)
                target = self.get_agent(content)
                actual_votes[speaker] = target
            for voter in actual_votes.keys():
                self.votes_history[voter].append(actual_votes[voter])
            self.votes_current = {}
        if request == 'FINISH':
            self.werewolves = []
            for flip in access_data(diff_data, 'text'):
                flip = flip[0]
                if flip.endswith('WEREWOLF') or flip.endswith('POSSESSED'):
                    self.werewolves.append(self.get_agent(flip))
            for voter in self.votes_history:
                for vote in self.votes_history[voter]:
                    if voter not in self.werewolves:
                        if vote in self.werewolves:
                            self.voter_accuracy_village[voter] += 1
                        self.votes_total_village[voter] += 1
                    else:
                        if vote in self.werewolves:
                            self.voter_accuracy_wolf[voter] += 1
                        self.votes_total_wolf[voter] += 1
            self.votes_history = defaultdict(list)
    def vote_tally(self):
        return Counter(self.votes_current.values())
    def get_player_accuracy(self,id,werewolf=False):
        try:
            if werewolf: return self.voter_accuracy_wolf[id] / self.votes_total_wolf[id]
            else: return self.voter_accuracy_village[id] / self.votes_total_village[id]
        except ZeroDivisionError:
            return 0.
    def get_prediction_accuracy(self, predictions):
        count = 0
        for prediction in predictions:
            if prediction in self.werewolves:
                count += 1
        return count