from policies.base_agenda import Agenda

# Agent that pushes to maximize the impact of actions, by not wasting them on people who are likely to die. Unless the point of the action is to stop them from dying, in which case, use the action on somebody with a lower life expectancy.
class Pragmatism(Agenda):
    def __init__(self, agent):
        super().__init__(agent)
        self.weights['protect'] = 0.25
        self.weights['scan'] = 0.05
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