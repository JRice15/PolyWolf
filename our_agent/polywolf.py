import numpy as np
from collections import defaultdict

import aiwolfpy
from aiwolfpy import contentbuilder as cb

from base_agent import Agent
from probability import Estimator

from policies.analysis import Analysis
from policies.fake_analysis import FakeAnalysis
from policies.dissent import Dissent
from policies.pragmatism import Pragmatism
from policies.prioritize_seer import SeerPriority
from policies.prioritize_medium import MediumPriority
from policies.prioritize_bodyguard import BodyguardPriority

policies = [Analysis, FakeAnalysis, Dissent, Pragmatism, SeerPriority, MediumPriority, BodyguardPriority]

class PolyWolf(Agent):
    def __init__(self, agent_name):
        super().__init__(agent_name)
        self.my_vote = -1
        self.target = -1
        self.estimator = Estimator(self)
        self.agendas = [policy(self) for policy in policies]

    def update(self, base_info, diff_data, request):
        super().update(base_info, diff_data, request)
        self.estimator.update(base_info, diff_data, request)
        if request == 'FINISH':
            for agenda in self.agendas: agenda.reset()

    def make_policy_decision(self, request):
        policy_values = defaultdict(float)
        for agenda in self.agendas:
            proposals = getattr(agenda, request)()
            if proposals == None: continue
            for proposal in proposals:
                policy_values[proposal] += proposals[proposal] * agenda.weights[request]
        if policy_values:
            return max(policy_values, key=policy_values.get)
        return None

    def choose_vote(self):
        decision = self.make_policy_decision('vote')
        if decision: return decision
        return self.id

    def talk(self):
        self.my_vote = self.choose_vote()
        decision = self.make_policy_decision('talk')
        if decision: return decision
        return cb.over()

    def vote(self):
        return self.choose_vote()

    def whisper(self):
        target = self.make_policy_decision('attack')
        if target: return cb.attack(target)
        return cb.over()

    def attack(self):
        target = self.make_policy_decision('attack')
        if target: return target
        return self.id

    def divine(self):
        target = self.make_policy_decision('scan')
        if target: return target
        return self.id

    def guard(self):
        target = self.make_policy_decision('protect')
        if target: return target
        return self.id

agent = PolyWolf('PolyWolf')

if __name__ == '__main__':
    aiwolfpy.connect_parse(agent)