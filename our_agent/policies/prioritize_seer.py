from policies.base_agenda import Agenda
from aiwolfpy import contentbuilder as cb

import random

# Agent prioritizes the lives of those who it thinks might be the seer. Both to end them as a werewolf, or to protect them as a bodyguard.
class SeerPriority(Agenda):
    def __init__(self, agent):
        super().__init__(agent)
        self.weights['attack'] = 0
        self.weights['protect'] = 0
        #self.weights['vote'] = 0.05
    # The seer must die!
    def attack(self):
        if type(self.agent.estimator.predictions) == type(None): return None
        seer_probabilities = self.agent.estimator.predictions[:,3] # Column 3 = Seer predictions
        self.seer_probabilities = {player_id:seer_probabilities[player_id-1] for player_id in self.agent.state.current_living_players}
        return self.seer_probabilities
    # The seer must survive!
    def protect(self):
        return self.attack()
    # The seer must die!
    #def vote(self):
    #    if self.agent.role == 'WEREWOLF' or self.agent.role == 'POSSESSED':
    #        return self.seer_probabilities
    #    return None
