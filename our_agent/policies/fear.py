from policies.base_agenda import Agenda

'''
# Agent pushes to kill off players who historically have a high win rate on the opposite team.
class Fear(Agenda):
    def __init__(self, agent):
        super().__init__(agent)
        self.weights['vote'] = 0
        self.weights['attack'] = 0
        #self.weights['protect'] = 0
        self.weights['scan'] = 0
    def get_winrates(self):
        winrates = {}
        for player in self.state.current_living_players:
            if self.state.games > 1:
                winrates[player] = (self.agent.state.wins_good[player]+self.agent.state.wins_evil[player]) / (self.agent.state.games_good[player]+self.agent.state.games_evil[player])
        return winrates
    def get_threats(self):
        threats = {}
        if self.agent.role == 'WEREWOLF' or self.agent.role == 'POSSESSED':
            for player in self.agent.state.current_living_players:
                if self.agent.state.games_good[player] > 20:
                    threats[player] = self.agent.state.wins_good[player] / self.agent.state.games_good[player]
                else: threats[player] = 0.6
        else:
            for player in self.agent.state.current_living_players:
                if self.agent.state.games_evil[player] > 20:
                    threats[player] = self.agent.state.wins_evil[player] / self.agent.state.games_evil[player]
                else: threats[player] = 0.2
        threats[self.agent.id] = 0
        return threats
    def get_expected_threats(self):
        threats = {}
        if self.agent.role == 'WEREWOLF' or self.agent.role == 'POSSESSED':
            for player in self.agent.state.current_living_players:
                if self.agent.state.games_good[player] > 20:
                    threats[player] = self.agent.state.wins_good[player] / self.agent.state.games_good[player]
                else: threats[player] = 0.6
        else:
            for player in self.agent.state.current_living_players:
                if self.agent.state.games_evil[player] > 10 and self.agent.state.games_good[player] > 10:
                    threats[player] = (self.agent.state.wins_evil[player] / self.agent.state.games_evil[player]) / (self.agent.state.wins_good[player]+1 / self.agent.state.games_good[player]+1)
                else: threats[player] = 0.35
        threats[self.agent.id] = 0
        return threats
    # Vote for threatening people.
    def vote(self):
        return self.get_threats()
    # Attack threatening people.
    def attack(self):
        return self.get_threats()
    # Scan threatening people.
    def scan(self):
        return self.get_threats()
    # Don't protect threatening people.
    #def protect(self):
    #    threats = self.get_expected_threats()
    #    top = max(threats.values())
    #    return {player:top-threats[player] for player in threats}
'''

# Could potentially be split into two policies:
#   -Target people who are likely to make you lose
#   -Target people with a high win rate just to drag them down

class Fear(Agenda):
    def __init__(self, agent):
        super().__init__(agent)
        self.weights['vote'] = 1
        self.weights['attack'] = 0
    def get_winrates(self):
        winrates = {}
        for player in self.state.current_living_players:
            if self.state.games > 1:
                winrates[player] = (self.agent.state.wins_good[player]+self.agent.state.wins_evil[player]) / (self.agent.state.games_good[player]+self.agent.state.games_evil[player])
        return winrates
    # Vote for threatening people.
    def vote(self):
        return self.get_winrates()
    # Attack threatening people.
    def attack(self):
        return self.get_winrates()
    # Scan threatening people.