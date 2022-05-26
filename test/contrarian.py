# Agent always votes for the agent with the least votes.
# Otherwise takes random actions and does not communicate beyond stating its intended vote.

import aiwolfpy
import aiwolfpy.contentbuilder as cb

from base_agent import Agent

class ContrarianAgent(Agent):
    def __init__(self, agent_name):
        super().__init__(agent_name)
        self.my_vote = -1
        self.spoke = False

    def talk(self):
        try:
            target = self.state.vote_tally().most_common()[-1][0]
            if target and self.my_vote != target:
                self.my_vote = target
                return cb.vote(target)
        except: pass
        return cb.over()

    def vote(self):
        try: return self.state.vote_tally().most_common()[-1][0]
        except: return self.id

agent = ContrarianAgent('contrarian')

if __name__ == '__main__':
    aiwolfpy.connect_parse(agent)
