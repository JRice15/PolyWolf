from policies.base_agenda import Agenda

'''
# Agent that pushes to maximize the impact of actions, by not wasting them on people who are likely to die. Unless the point of the action is to stop them from dying, in which case, use the action on somebody with a lower life expectancy.
class Pragmatism(Agenda):
    def __init__(self, agent):
        super().__init__(agent)
        self.weights['protect'] = 0
        self.weights['scan'] = 0
    # Scan people who aren't gonna die on you.
    def scan(self):
        self.values = {}
        for agentid in self.agent.state.current_living_players:
            if len(self.agent.state.lifespans[agentid]):
                self.values[agentid] = sum(self.agent.state.lifespans[agentid]) / len(self.agent.state.lifespans[agentid])
        if self.values: return self.values
        return None
    # Protect people who are gonna die on you.
    def protect(self):
        self.values = {}
        for agentid in self.agent.state.current_living_players:
            if self.agent.state.human_games_played[agentid]:
                self.values[agentid] = self.agent.state.killed_count[agentid] / self.agent.state.human_games_played[agentid]
        if self.values: return self.values
        return None
'''

# Agent that votes for the other agent it estimates is least likely to help our side win, whether due to evilness or incompetence.
class Pragmatism(Agenda):
    def __init__(self, agent):
        super().__init__(agent)
        self.weights['vote'] = 10
        self.weights['attack'] = 0
        self.weights['protect'] = 0
    def estimate_utility(self):
        if self.state.games < 10: return None
        if self.agent.role == 'WEREWOLF' or self.agent.role == 'POSSESSED':
            return self.agent.estimator.loss_analysis(alignment='EVIL')
        else:
            return self.agent.estimator.loss_analysis(alignment='GOOD')
    # Vote for people with the greatest chance of making us lose.
    def vote(self):
        if self.agent.role == 'WEREWOLF': return None
        return self.estimate_utility()
    # Kill people with the greatest chance of making us lose.
    def attack(self):
        return self.estimate_utility()
    # Protect people with the greatest chance of making us win.
    def protect(self):
        utilities = self.estimate_utility()
        if utilities: return {pid:1-utilities[pid] for pid in utilities}
        return None