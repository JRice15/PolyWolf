# Agent behaves completely randomly and communicates the minimum possible amount with the server or the other agents.

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..')) # Because python relative imports are unfathomably garbage.

import aiwolfpy
from aiwolfpy import contentbuilder as cb
from base_agent import Agent

class RandomAgent(Agent):
    pass

agent = RandomAgent('random')

if __name__ == '__main__':
    aiwolfpy.connect_parse(agent)
