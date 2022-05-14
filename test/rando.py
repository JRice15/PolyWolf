# Agent behaves completely randomly and communicates the minimum possible amount with the server or the other agents.

import aiwolfpy
import aiwolfpy.contentbuilder as cb

class RandomAgent(object):
    def __init__(self, agent_name):
        self.myname = agent_name

    def getName(self):
        return self.myname

    def initialize(self, base_info, diff_data, game_setting):
        self.id = base_info['agentIdx']

    def update(self, base_info, diff_data, request):
        pass

    def dayStart(self):
        pass

    def talk(self):
        return cb.over()

    def whisper(self):
        return cb.over()

    def vote(self):
        return self.id

    def attack(self):
        return self.id

    def divine(self):
        return self.id

    def guard(self):
        return self.id

    def finish(self):
        pass

agent = RandomAgent('random')

if __name__ == '__main__':
    aiwolfpy.connect_parse(agent)
