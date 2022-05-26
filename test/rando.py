# Agent behaves completely randomly and communicates the minimum possible amount with the server or the other agents.

import aiwolfpy
import aiwolfpy.contentbuilder as cb

from base_agent import Agent

class RandomAgent(Agent):
    pass

agent = RandomAgent('random')

if __name__ == '__main__':
    aiwolfpy.connect_parse(agent)
