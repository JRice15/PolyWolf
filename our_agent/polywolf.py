import os
import numpy as np
from collections import defaultdict

import aiwolfpy
from aiwolfpy import contentbuilder as cb

from base_agent import Agent
from probability import Estimator
import logger

from policies.analysis import Analysis
from policies.fake_analysis import FakeAnalysis
from policies.troll_analysis import TrollAnalysis
from policies.adaptive_analysis import AdaptiveAnalysis
from policies.consolidation import Consolidation
from policies.dissent import Dissent
from policies.chaos import Chaos
from policies.pragmatism import Pragmatism
from policies.fear import Fear
from policies.prioritize_seer import SeerPriority
from policies.prioritize_medium import MediumPriority
from policies.prioritize_bodyguard import BodyguardPriority
from policies.honesty import Honesty
from policies.duplicity import Duplicity

policies = [Analysis, FakeAnalysis, TrollAnalysis, AdaptiveAnalysis, Consolidation, Dissent, Pragmatism, Fear, SeerPriority, MediumPriority, BodyguardPriority, Honesty, Duplicity]
#excluded: Chaos,

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
        if request == 'DAILY_INITIALIZE':
            logger.log(self.state.confirmed)

    def make_policy_decision(self, request):
        policy_values = defaultdict(float)
        for agenda in self.agendas:
            proposals = getattr(agenda, request)()
            if not proposals: continue
            #lower = min(proposals.values()) # If the agenda doesn't speak up for a decision, it is assumed to be of zero value to that agenda
            #proposals = {proposal:proposals[proposal]-lower for proposal in proposals}
            upper = max(proposals.values())
            if upper == 0: continue
            proposals = {proposal:proposals[proposal]/upper for proposal in proposals}
            for proposal in proposals:
                policy_values[proposal] += proposals[proposal] * agenda.weights[request]
        if policy_values:
            #logger.log(policy_values)
            decision = max(policy_values, key=policy_values.get)
            logger.log(f'role {self.role},\tday {self.state.day},\trequest {request},\tdecision {decision}')
            return decision
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
        target = self.make_policy_decision('attack') # Todo: could do some consolidating policy with other agents attack wishes
        if target: return cb.attack(target)
        return cb.over()

    def attack(self):
        self.target = self.make_policy_decision('attack')
        if self.target: return self.target
        return self.id

    def divine(self):
        self.target = self.make_policy_decision('scan')
        if self.target: return self.target
        return self.id

    def guard(self):
        self.target = self.make_policy_decision('protect')
        if self.target: return self.target
        return self.id

idx = logger.reserve_id()
logger.log(f'Reserved {idx}')

agent = PolyWolf(f'PolyWolf-{idx}')

if __name__ == '__main__':
    aiwolfpy.connect_parse(agent)