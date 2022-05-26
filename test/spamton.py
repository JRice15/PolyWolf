# Agent that just floods the chat with completely random shit during the talk phase.
# Otherwise takes random actions and votes randomly.

import random

import aiwolfpy
import aiwolfpy.contentbuilder as cb

from base_agent import Agent

class SpamAgent(Agent):
    def talk(self):
        speech = random.choice(['attack','comingout','divine','divined','estimate','guard','guarded','identified','vote'])
        if speech in ('attack','divine','guard','guarded','vote'):
            args = [random.choice(self.state.player_list)]
        if speech in ('comingout','estimate'):
            args = [random.choice(self.state.player_list), random.choice(list(self.state.roles_counts.keys()))]
        if speech in ('divined','identified'):
            args = [random.choice(self.state.player_list), random.choice(['WEREWOLF','HUMAN'])]
        return cb.__dict__[speech](*args)

agent = SpamAgent('spamton')

if __name__ == '__main__':
    aiwolfpy.connect_parse(agent)
