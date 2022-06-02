import numpy as np

import aiwolfpy
from aiwolfpy import contentbuilder as cb
from base_agent import Agent

from role_estimation.load_rnn_estimator import RoleEstimatorRNN

class PolyWolf(Agent):
    def __init__(self, agent_name):
        super().__init__(agent_name)
        self.my_vote = -1
        self.target = -1
        self.role_estimator = RoleEstimatorRNN()
        self.predictions = None
        self.probabilities = None
        self.agendas = []

    def update(self, base_info, diff_data, request):
        self.predictions = self.role_estimator.update_and_predict(base_info=base_info, diff_data=diff_data, request=request)
        if type(self.predictions) != type(None) and not self.predictions.empty:
            self.predictions = self.predictions.to_numpy()
            offset = max(abs(min(self.predictions.flatten())), abs(max(self.predictions.flatten())))
            for row in self.predictions:
                row += offset
                row /= sum(row)
        else: self.predictions = None
        super().update(base_info, diff_data, request)
        if request == 'DAILY_INITIALIZE':
            if self.role == 'BODYGUARD' and self.state.day > 1 and max(self.state.murdered_players.values()) != self.state.day:
                self.state.confirmed[self.target] = 'HUMAN'

    def choose_vote(self):
        if self.role != 'WEREWOLF' and self.role != 'POSSESSED':
            if type(self.predictions) != type(None):
                suspicions = self.predictions[:,-1]
                for i, _ in enumerate(suspicions):
                    if i not in self.state.current_living_players: suspicions[i] = -1
                id = np.argmax(suspicions)+1
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

agent = PolyWolf('PolyWolf')

if __name__ == '__main__':
    aiwolfpy.connect_parse(agent)