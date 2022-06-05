# When town-aligned, agent always votes for the (currently living) player the neural network predicts is most likely to be a werewolf.
# Otherwise takes random actions and does not communicate beyond stating its intended vote.

import numpy as np

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..')) # Because python relative imports are unfathomably garbage.

import aiwolfpy
from aiwolfpy import contentbuilder as cb
from base_agent import Agent

from role_estimation.load_rnn_estimator import RoleEstimatorRNN

class NeuralAgent(Agent):
    def __init__(self, agent_name):
        super().__init__(agent_name)
        self.my_vote = -1
        self.spoke = False
        self.role_estimator = RoleEstimatorRNN()
        self.predictions = None

    def update(self, base_info, diff_data, request):
        predictions = self.role_estimator.update_and_predict(base_info=base_info, diff_data=diff_data, request=request)
        if type(predictions) != type(None) and not predictions.empty:
            self.predictions = predictions.to_numpy()
            offset = max(abs(min(self.predictions.flatten())), abs(max(self.predictions.flatten())))
            for row in self.predictions:
                row += offset
                row /= sum(row)
        super().update(base_info, diff_data, request)

    def choose_vote(self):
        if self.role != 'WEREWOLF' and self.role != 'POSSESSED':
            if type(self.predictions) != type(None):
                suspicions = self.predictions[:,-1] + self.predictions[:,2]
                for i, _ in enumerate(suspicions):
                    if i not in self.state.current_living_players: suspicions[i] = -1
                id = np.argmax(suspicions) + 1
                return int(id)
        return self.id

    def talk(self):
        target = self.choose_vote()
        if target and self.my_vote != target:
            self.my_vote = target
            return cb.vote(target)
        return cb.over()

    def vote(self):
        return self.choose_vote()

agent = NeuralAgent('neural')

if __name__ == '__main__':
    aiwolfpy.connect_parse(agent)
