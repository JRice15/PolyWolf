from collections import Counter, defaultdict

def access_data(frame, *labels):
    return zip(*[frame[label].values for label in labels])

# A record of the game state, from the perspective of a single agent.
class GameState:
    def __init__(self):
        self.day = 0
        self.games = 0
        self.roles_counts = {}                  # dict of {role name : count}
        self.player_list = []
        self.current_living_players = []        # list of player ids
        self.executed_players = {}              # dict of {player id : day of demise}
        self.murdered_players = {}
        self.last_attacked_player = -1
        self.confirmed = {}                     # dict of {player id : species}
        self.votes_current = {}                 # dict of {voter id : target id}
        self.votes_history = defaultdict(list)  # dict of {voter id : [target ids list]}
        # Tracking the rate other agents voted for werewolves / possessed.
        self.voter_accuracy_good = Counter()
        self.voter_accuracy_evil = Counter()
        self.votes_total_good = Counter()
        self.votes_total_evil = Counter()
        # Tracking the rate other agents have won, based on alignment.
        self.wins_good = Counter()
        self.wins_evil = Counter()
        self.games_good = Counter()
        self.games_evil = Counter()
        # Tracking how often other agents die under various circumstances.
        self.lifespans = defaultdict(list)
        self.killed_count = Counter()
        self.human_games_played = Counter()
    def get_agent(self, text):
        return int(text.split('[')[1].split(']')[0])
    def update(self, diff_data, request):
        if request == 'TALK':
            for speaker, content in access_data(diff_data, 'agent', 'text'):
                if content.startswith('VOTE Agent'):
                    speaker = int(speaker)
                    target = self.get_agent(content)
                    self.votes_current[speaker] = target
        elif request == 'VOTE':
            pass
        elif request == 'WHISPER':
            pass
        elif request == 'ATTACK':
            pass
        elif request == 'GUARD':
            pass
        elif request == 'DIVINE':
            pass
        elif request == 'DAILY_INITIALIZE':
            self.day += 1
            self.last_attacked_player = -1
            actual_votes = {}
            for event, agent, speaker, content in access_data(diff_data, 'type', 'agent', 'idx', 'text'):
                event = str(event)
                if event == 'attack':
                    self.last_attacked_player = agent
                if event == 'dead' or event == 'execute':
                    self.current_living_players.remove(agent)
                    self.lifespans[agent].append(self.day)
                    if event == 'dead':
                        self.murdered_players[agent] = self.day
                        self.killed_count[agent] += 1
                    if event == 'execute': self.executed_players[agent] = self.day
                if event == 'identify':
                    deceased = self.get_agent(content)
                    self.confirmed[deceased] = content.split(' ')[-1]
                if event == 'divine':
                    scanned = self.get_agent(content)
                    self.confirmed[scanned] = content.split(' ')[-1]
                if event == 'vote':
                    speaker = int(speaker)
                    target = self.get_agent(content)
                    actual_votes[speaker] = target
            for voter in actual_votes.keys():
                self.votes_history[voter].append(actual_votes[voter])
            self.votes_current = {}
        elif request == 'DAILY_FINISH':
            pass
        elif request == 'FINISH':
            self.games += 1
            self.evils = []
            town_wins = True
            for flip in access_data(diff_data, 'text'):
                flip = flip[0]
                if flip.endswith('WEREWOLF') or flip.endswith('POSSESSED'):
                    self.evils.append(self.get_agent(flip))
                if not flip.endswith('WEREWOLF'):
                    self.human_games_played[self.get_agent(flip)] += 1
                elif self.get_agent(flip) in self.current_living_players:
                    town_wins = False
            for player in self.player_list:
                if player in self.evils:
                    self.games_evil[player] += 1
                    if not town_wins:
                        self.wins_evil[player] += 1
                else:
                    self.games_good[player] += 1
                    if town_wins:
                        self.wins_good += 1
            for voter in self.votes_history:
                for vote in self.votes_history[voter]:
                    if voter not in self.evils:
                        if vote in self.evils:
                            self.voter_accuracy_good[voter] += 1
                        self.votes_total_good[voter] += 1
                    else:
                        if vote in self.evils:
                            self.voter_accuracy_evil[voter] += 1
                        self.votes_total_evil[voter] += 1
            self.votes_history = defaultdict(list)
            for player_id in self.current_living_players:
                self.lifespans[player_id].append(self.day+1)
            self.current_living_players = self.player_list.copy()
            self.executed_players = {}
            self.murdered_players = {}
            self.confirmed = {}
            self.day = 0
        else:
            raise RuntimeError
    def vote_tally(self):
        return Counter(self.votes_current.values())
    def get_player_accuracy(self,id,werewolf=False):
        try:
            if werewolf: return self.voter_accuracy_evil[id] / self.votes_total_evil[id]
            else: return self.voter_accuracy_good[id] / self.votes_total_good[id]
        except ZeroDivisionError:
            return None
    def get_prediction_accuracy(self, predictions):
        count = 0
        for prediction in predictions:
            if prediction in self.evils:
                count += 1
        return count