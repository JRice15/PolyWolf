# Agent always votes for the agent with the least votes.
# Otherwise takes random actions and does not communicate beyond stating its intended vote.

import aiwolfpy
import aiwolfpy.contentbuilder as cb

from state import GameState, log

class ContrarianAgent(object):
    def __init__(self, agent_name):
        self.state = GameState()
        self.my_name = agent_name
        self.my_vote = -1
        self.spoke = False

    def getName(self):
        return self.my_name

    def initialize(self, base_info, diff_data, game_setting):
        self.game_setting = game_setting
        self.id = base_info['agentIdx']

    def update(self, base_info, diff_data, request):
        self.state.update(diff_data, request)

    def dayStart(self):
        pass

    def talk(self):
        try:
            target = self.state.vote_tally().most_common()[-1][0]
            log(f's: {target}')
            if target and self.my_vote != target:
                self.my_vote = target
                return cb.vote(target)
        except: pass
        return cb.over()

    def whisper(self):
        return cb.over()

    def vote(self):
        return self.state.vote_tally().most_common()[-1][0]

    def attack(self):
        return self.id

    def divine(self):
        return self.id

    def guard(self):
        return self.id

    def finish(self):
        pass

agent = ContrarianAgent('contrarian')

if __name__ == '__main__':
    aiwolfpy.connect_parse(agent)
