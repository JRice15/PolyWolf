# Agent always votes for the agent with the most votes.
# Otherwise takes random actions and does not communicate beyond stating its intended vote.

import random

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..')) # Because python relative imports are unfathomably garbage.

import aiwolfpy
from aiwolfpy import contentbuilder as cb
from base_agent import Agent

class SheepAgent(Agent):
    def __init__(self, agent_name):
        super().__init__(agent_name)
        self.my_vote = -1

    def choose_vote(self):
        try: return self.state.vote_tally().most_common()[0][0]
        except: return random.choice(self.state.current_living_players)

    def talk(self):
        target = self.choose_vote()
        if target != self.id and target != self.my_vote:
            self.my_vote = target
            return cb.vote(target)
        return cb.over()

    def vote(self):
        return self.choose_vote()

agent = SheepAgent('sheep')

if __name__ == '__main__':
    aiwolfpy.connect_parse(agent)
