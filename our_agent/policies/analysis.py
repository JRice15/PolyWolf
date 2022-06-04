from policies.base_agenda import Agenda
from aiwolfpy import contentbuilder as cb

# Agent pushes for rational decisions acting on our best estimations of how suspicious other players are.
class Analysis(Agenda):
    def __init__(self, agent):
        super().__init__(agent)
        self.weights['talk'] = 1
        self.weights['vote'] = 1
        self.weights['protect'] = 1
        self.weights['scan'] = 1
        self.reads = None
        self.last_vote = None
        self.last_day = None
    def reset(self):
        self.reads = None
        self.last_vote = None
        self.last_day = None
    # Announce who we are voting for, if we have anything new to say about that.
    def talk(self):
        if self.agent.my_vote and (self.last_vote != self.agent.my_vote or self.last_day != self.agent.state.day):
            self.last_vote = self.agent.my_vote
            self.last_day = self.agent.state.day
            return {cb.vote(self.agent.my_vote):1}
        return None
    # Vote for suspicious people.
    def vote(self):
        if self.agent.role == 'WEREWOLF' or self.agent.role == 'POSSESSED': return None
        if len(self.agent.state.player_list) > 8:
            self.reads = self.agent.estimator.vote_analysis()
        else:
            return None # Todo: Implement analysis rules for 5-player games.
        self.reads[self.agent.id] = 0
        return self.reads
    # Protect trustworthy people.
    def protect(self):
        if self.reads:
            return {id:(1-self.reads[id]) if id != self.agent.id else 0 for id in self.reads}
    # Scan suspicious people.
    def scan(self):
        if self.reads:
            return self.reads