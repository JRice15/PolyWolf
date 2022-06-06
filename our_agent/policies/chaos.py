from policies.base_agenda import Agenda
from aiwolfpy import contentbuilder as cb
import random

# Agent floods the chat with random nonsense for the first few games, to throw off prediction methods used by other agents.
class Chaos(Agenda):
    def __init__(self, agent):
        super().__init__(agent)
        self.weights['talk'] = 10
    # Spam!
    # Fun fact: the first time we ran this, it crashed our own predictor, due to making outlandish claims about roles that never get used in the AIWolf setup.
    def talk(self):
        if self.agent.state.games == 1:
            speech = random.choice(['attack','comingout','divine','divined','estimate','guard','guarded','identified','vote'])
            if speech in ('attack','divine','guard','guarded','vote'):
                args = [random.choice(self.agent.state.player_list)]
            if speech in ('comingout','estimate'):
                args = [random.choice(self.agent.state.player_list), random.choice(list(self.agent.state.roles_counts.keys()))]
            if speech in ('divined','identified'):
                args = [random.choice(self.agent.state.player_list), random.choice(['WEREWOLF','HUMAN'])]
            return {cb.__dict__[speech](*args):1}
        return None