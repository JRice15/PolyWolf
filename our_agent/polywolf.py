import numpy as np

import aiwolfpy
from aiwolfpy import contentbuilder as cb
from base_agent import Agent
from probability import Estimator

class PolyWolf(Agent):
    def __init__(self, agent_name):
        super().__init__(agent_name)
        self.my_vote = -1
        self.target = -1
        self.estimator = Estimator(self)
        self.reads = None
        self.agendas = []

    def update(self, base_info, diff_data, request):
        super().update(base_info, diff_data, request)
        self.estimator.update(base_info, diff_data, request)

    def choose_vote(self):
        self.reads = self.estimator.vote_analysis()
        #voting_values = {agenda.name:agenda.vote() for agenda in self.agendas}
        #aggregate_value = {id:self.weighted_average([voting_values[agenda][id] for agenda in voting_values.keys() if id in voting_values[agenda].keys()],[self.policy[agenda] for agenda in voting_values.keys() if id in voting_values[agenda].keys()]) for id in self.state.current_living_players}
        vote = max(self.reads, key=self.reads.get)
        return vote

    def talk(self):
        target = self.choose_vote()
        if target and self.my_vote != target:
            self.my_vote = target
            return cb.vote(target)
        return cb.over()

    def vote(self):
        return self.choose_vote()

agent = PolyWolf('PolyWolf')

if __name__ == '__main__':
    aiwolfpy.connect_parse(agent)