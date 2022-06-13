from policies.base_agenda import Agenda

# Todo: Bussing policy.
# Could instead make "analysis" an agenda that functions consistently across the board, but werewolf/possessed get special agendas that push back against that one.
# Hmmmmmmm

# Agent pretends to do follow what Analysis says, but without voting for any werewolves.
class FakeAnalysis(Agenda):
    def __init__(self, agent):
        super().__init__(agent)
        self.weights['vote'] = 0
        self.weights['attack'] = 0
        self.true_reads = None
    def reset(self):
        self.true_reads = None
    # Vote for suspicious people who aren't actually werewolves.
    def vote(self):
        if self.agent.role != 'WEREWOLF': return None
        self.true_reads = self.agent.estimator.vote_analysis_neural()
        fake_reads = self.true_reads.copy()
        for player in self.agent.state.confirmed:
            if self.agent.state.confirmed[player] == 'WEREWOLF':
                fake_reads[player] = 0
        return fake_reads
    # Attack trustworthy people.
    def attack(self):
        if self.true_reads:
            return {id:(1-self.true_reads[id]) if id != self.agent.id else 0 for id in self.true_reads}