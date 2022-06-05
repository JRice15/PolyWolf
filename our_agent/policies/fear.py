from policies.base_agenda import Agenda

# Agent pushes to kill off players who historically have a high win rate on the opposite team.
class Fear(Agenda):
    def __init__(self, agent):
        super().__init__(agent)
        self.weights['vote'] = 0.05
        self.weights['attack'] = 1
        self.weights['scan'] = 1
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
    # Vote for threatening people.
    def vote(self):
        return self.get_threats()
    # Attack threatening people.
    def attack(self):
        return self.get_threats()
    # Scan threatening people.
    def scan(self):
        return self.get_threats()