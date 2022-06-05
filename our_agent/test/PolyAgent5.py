# When town-aligned, agent always votes for the (currently living) player the neural network predicts is most likely to be a werewolf.
# Otherwise takes random actions and does not communicate beyond stating its intended vote.

#from black import diff
from operator import contains
import numpy as np
import random

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..')) # Because python relative imports are unfathomably garbage.

import aiwolfpy
from aiwolfpy import contentbuilder as cb
from base_agent import Agent

from role_estimation.load_rnn_estimator import RoleEstimatorRNN

class PolyAgent5(Agent):
    def __init__(self, agent_name):
        super().__init__(agent_name)
        self.my_vote = -1
        self.spoke = False
        self.role_estimator = RoleEstimatorRNN()
        self.predictions = None
        self.talk_turn = 0
        self.day = 0

    def initialize(self, base_info, diff_data, game_setting):
        super().initialize(base_info, diff_data, game_setting)
        self.base_info = base_info
        self.diff_data = diff_data
        self.myid = int(base_info["agentIdx"])
        self.myrole = base_info["myRole"]
        self.check_alive()
        self.fake_seers = set()
        self.initial_fake_seers = set()
        self.divined = []
        self.divined_wolf = -1
        self.claimed_target = -1
        self.real_target = -1
        
    def check_alive(self):
        result = []
        for i in self.base_info["remainTalkMap"].keys():
            if self.base_info["statusMap"][i] == "ALIVE":
                result.append(int(i))
        result = list(
            set(result) - {self.myid})
        self.others_living = result

    def update(self, base_info, diff_data, request):
        self.base_info = base_info
        self.diff_data = diff_data
        self.check_alive()
        self.fake_seers = self.fake_seers & set(self.others_living)

        #NN Stuff
        self.predictions = self.role_estimator.update_and_predict(base_info=base_info, diff_data=diff_data, request=request)
        if type(self.predictions) != type(None) and not self.predictions.empty:
            self.predictions = self.predictions.to_numpy()
            offset = max(abs(min(self.predictions.flatten())), abs(max(self.predictions.flatten())))
            for row in self.predictions:
                row += offset
                row /= sum(row)
        else: 
            self.predictions = None
        super().update(base_info, diff_data, request)
        #End NN Stuff
    
        if request == "TALK":
            for i in range(diff_data.shape[0]):
                if diff_data["type"][i] == "talk":
                    if ("COMINGOUT" and "SEER") in diff_data["text"][i]: 
                        agent_claiming_seer = int(diff_data["text"][i].split()[1][6:8])
                        if (self.myrole == "SEER") and (agent_claiming_seer != self.myid):
                            self.fake_seers.add(int(diff_data["text"][i].split()[1][6:8]))

        if request == "DAILY_INITIALIZE":
            for i in range(diff_data.shape[0]):
                if diff_data["type"][i] == "divine":
                    self.divined.append(diff_data["text"][i])
                    if self.divined[-1].split()[2] == "WEREWOLF":
                        self.divined_wolf = int(self.divined[-1].split()[1][6:8])

    def choose_vote(self):
        if self.role != 'WEREWOLF' and self.role != 'POSSESSED':
            if type(self.predictions) != type(None):
                suspicions = self.predictions[:,-1]
                for i, _ in enumerate(suspicions):
                    if i not in self.state.current_living_players: suspicions[i] = -1
                id = np.argmax(suspicions)
                return int(id)
        return self.id

    def talk(self):
        self.talk_turn += 1
        self.check_alive()
        
        if self.myrole == 'SEER':
            if self.talk_turn > 2 and self.talk_turn < 13:
                return cb.vote(self.claimed_target)
            if self.talk_turn >= 13:
                return "Over"

            if self.day == 1:
                print("SEER day 1")
                if self.talk_turn == 1:
                    return cb.comingout(self.myid, self.myrole)
                if self.talk_turn == 2:
                    print("SEER day 1 turn 2")
                    self.initial_fake_seers.update(self.fake_seers)
                    if self.divined_wolf != -1:
                        self.claimed_target = self.divined_wolf
                        return cb.divined(self.divined_wolf, "WEREWOLF")
                    else: 
                        if len(self.fake_seers) > 0:
                            # Don't know who WW is, target a fake seer by lying about divine results
                            self.claimed_target = random.choice(list(self.fake_seers))
                            return cb.divined(self.claimed_target, "WEREWOLF")
                        else:
                            # pick a random target that is not confirmed human
                            self.claimed_target = random.choice(list(set(self.others_living) - set(self.divined)))
                            return cb.divined(self.claimed_target, "WEREWOLF")

            if self.day == 2:
                print("SEER day 2")
                if self.talk_turn == 1:
                    if len(self.initial_fake_seers) == 2:
                        if len(self.fake_seers) == 2:
                            return cb.comingout(self.myid, "WEREWOLF")
                        elif len(self.fake_seers) == 1:
                            return cb.comingout(self.myid, self.myrole)
                    elif len(self.initial_fake_seers) == 1:
                        if len(self.fake_seers) == 1:
                            return cb.comingout(self.myid, "POSSESSED")
                        elif len(self.fake_seers) == 0:
                            return cb.comingout(self.myid, self.myrole)
                if self.talk_turn == 2:
                    if len(self.initial_fake_seers) == 2:
                        if len(self.fake_seers) == 2:
                            self.claimed_target = random.choice(self.others_living)
                            return cb.vote(self.claimed_target)
                        elif len(self.fake_seers) == 1:
                            if self.divined_wolf == -1:
                                # The WW is the agent that has not been divined
                                self.divined_wolf = (set(self.others_living) - {int(self.divined[-1].split()[1][6:8])}).pop()
                            self.claimed_target = self.divined_wolf
                            return cb.divined(self.divined_wolf, "WEREWOLF")
                    elif len(self.initial_fake_seers) == 1:
                        if len(self.fake_seers) == 1:
                            self.claimed_target = self.fake_seers.pop()
                            self.real_target = (set(self.others_living) - {int(self.claimed_target)}).pop()
                            return cb.vote(self.claimed_target)
                        elif len(self.fake_seers) == 0:
                            if self.divined_wolf == -1:
                                # The WW is the agent that has not been divined
                                self.divined_wolf = (set(self.others_living) - {int(self.divined[-1].split()[1][6:8])}).pop()
                            self.claimed_target = self.divined_wolf
                            return cb.divined(self.divined_wolf, "WEREWOLF")

        target = self.choose_vote()
        if target and self.my_vote != target:
            self.my_vote = target
            return cb.vote(target)
        return cb.over()

    def vote(self):
        if self.myrole == "SEER":
            if self.real_target != -1:
                return self.real_target
            else:
                return self.claimed_target
        return self.choose_vote()

    def divine(self):
        return random.choice(list(set(self.others_living)-set(self.divined)))

    def dayStart(self):
        self.talk_turn = 0
        self.day = self.base_info["day"]
        return None

agent = PolyAgent5('PolyAgent5')

if __name__ == '__main__':
    aiwolfpy.connect_parse(agent)
