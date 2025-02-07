from policies.base_agenda import Agenda
from collections import defaultdict

# Agent pushes to consolidate the voting pool, to push through suspicions that already have some votes on them.
class Consolidation(Agenda):
    def __init__(self, agent):
        super().__init__(agent)
        self.weights['vote'] = 0.05
    # Sheep!
    def vote(self):
        tally = self.agent.state.vote_tally()
        if not tally: return None
        vote_maximum = tally.most_common()[0][1]
        if vote_maximum == 0: return None
        values = defaultdict(float)
        for agent in tally:
            if agent == self.agent.id: continue
            values[agent] = tally[agent] / vote_maximum
        return values