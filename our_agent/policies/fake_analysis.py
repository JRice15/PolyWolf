from policies.base_agenda import Agenda
from aiwolfpy import contentbuilder as cb

# Agent pretends to do follow what Analysis says, but without voting for any werewolves.
class FakeAnalysis(Agenda):
    def __init__(self, agent):
        super().__init__(agent)
        self.weights['talk'] = 1
        self.weights['vote'] = 1
        self.weights['attack'] = 1
        self.true_reads = None
        self.last_vote = None
        self.last_day = None
    def reset(self):
        self.true_reads = None
        self.last_vote = None
        self.last_day = None
    # Announce who we are voting for, if we have anything new to say about that.
    def talk(self):
        if self.agent.my_vote and (self.last_vote != self.agent.my_vote or self.last_day != self.agent.state.day):
            self.last_vote = self.agent.my_vote
            self.last_day = self.agent.state.day
            return {cb.vote(self.agent.my_vote):1}
        return None
    # Vote for suspicious people who aren't actually werewolves.
    def vote(self):
        if self.agent.role != 'WEREWOLF': return None
        self.true_reads = self.agent.estimator.vote_analysis()
        fake_reads = self.true_reads.copy()
        for player in self.agent.state.confirmed:
            if self.agent.state.confirmed[player] == 'WEREWOLF':
                fake_reads[player] = 0
        return fake_reads
    # Attack trustworthy people.
    def attack(self):
        if self.true_reads:
            return {id:(1-self.true_reads[id]) if id != self.agent.id else 0 for id in self.true_reads}