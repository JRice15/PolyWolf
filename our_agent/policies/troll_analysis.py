from policies.base_agenda import Agenda

# Agent votes for the most trustworthy people (for possessed play).
class TrollAnalysis(Agenda):
    def __init__(self, agent):
        super().__init__(agent)
        self.weights['vote'] = 0
    # Vote for villagers!
    def vote(self):
        if self.agent.role != 'POSSESSED': return None
        reads = self.agent.estimator.vote_analysis_neural()
        return {id:(1-reads[id]) if id != self.agent.id else 0 for id in reads}