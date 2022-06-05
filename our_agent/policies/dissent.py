from policies.base_agenda import Agenda
from collections import defaultdict

# Agent pushes to diversify and divide the voting pool, voting for agents with the least number of votes.
class Dissent(Agenda):
    def __init__(self, agent):
        super().__init__(agent)
        self.weights['vote'] = 0.03
    # Be contrary!
    def vote(self):
        tally = self.agent.state.vote_tally()
        if not tally: return None
        vote_minimum = tally.most_common()[-1][1]
        values = defaultdict(float)
        for agent in tally:
            if agent == self.agent.id: continue
            if tally[agent] == vote_minimum:
                values[agent] = 1.
        return values