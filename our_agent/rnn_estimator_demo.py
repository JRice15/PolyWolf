import logging
import random
import time
import os

import aiwolfpy
import aiwolfpy.contentbuilder as cb
from role_estimation.load_rnn_estimator import RoleEstimatorRNN

os.makedir("logs", exist_ok=True)

logging.basicConfig(
    filename=f'logs/rnn_demo_{time.time()}.log', 
    level=logging.DEBUG,
    filemode="w")



class EstimatorDemo(object):

    def __init__(self, agent_name):
        self.myname = agent_name
        self.role_estimator = RoleEstimatorRNN()
        self.role_predictions = None

    def getName(self):
        return self.myname

    def initialize(self, base_info, diff_data, game_setting):
        self.id = base_info['agentIdx']

    def update(self, base_info, diff_data, request):
        # role_predictions is a dataframe, where the columns are each of the 6 roles
        # and the index is the 15 agent ids. The values in each cell are a predicted value
        # for how likely that agent it to be that role. The values are not probabilities
        # (they can be negative, or greater than one), but larger always means more likely.
        # They can be turned into probabilities too if you need that, lemme know
        self.role_predictions = self.role_estimator.update_and_predict(
                base_info=base_info, 
                diff_data=diff_data, 
                request=request
            )
        
    def dayStart(self):
        pass

    def talk(self):
        return "VOTE Agent[01]"

    def whisper(self):
        return "VOTE Agent[01]"

    def vote(self):
        return 1

    def attack(self):
        return 1

    def divine(self):
        return 1

    def guard(self):
        return 1

    def finish(self):
        pass

agent = EstimatorDemo('estimator_demo')

if __name__ == '__main__':
    aiwolfpy.connect_parse(agent)
