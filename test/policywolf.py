# An initial stab at a policy-based werewolf agent.
# Specify some list of paremters in a policy-space and it will play according to those settings.
# The goal is that a wide variety of possible rule-based approaches can be contained in the policy-space, and the best one can be searched for algorithmically.

from collections import defaultdict

import aiwolfpy
import aiwolfpy.contentbuilder as cb

from state import GameState, log
from prob import *

POLICY = {
    'w_sheep' : 1,
    'w_trailblazer' : 1,
    'w_vote_analysis' : 1,
}

# TODO: Remember past votes across multiple cycles in the same game. They are still useful if the voted-on player is still alive.
# TODO: Can potentially support multiple hypothetical agents, each making predictions and recording a track record for it.

class PolicyAgent(object):
    def __init__(self, agent_name, policy):
        self.state = GameState()
        self.my_name = agent_name
        self.my_vote = -1
        self.my_predictions = []
        self.total_predictions = 0
        self.correct_predictions = 0
        self.spoke = False
        self.policy = policy

    def choose_vote(self):
        #vote_weights = defaultdict(float)
        vote_weights = {player:0. for player in self.state.player_list}
        # Sheep rules
        total_count = sum(self.state.vote_tally().values())
        for agent, count in self.state.vote_tally().items():
            vote_weights[agent] += self.policy['w_sheep']*(count/total_count)
        # Trailblazer rules
        total_count = sum([1 for value in self.state.vote_tally().values() if value == 0])
        for agent, count in self.state.vote_tally().items():
            if count == 0: vote_weights[agent] += self.policy['w_trailblazer'] / total_count
        # Aggregate vote decision
        log(str(self.state.vote_tally()))
        log(str(vote_weights))
        vote = max(vote_weights, key=vote_weights.get)
        self.my_predictions.append(vote)
        # Votes probability analysis
        evil_probabilities = vote_analysis(self.state, self.id, vote, self.my_accuracy())
        log(f'computed evil probabilities: {evil_probabilities}')
        vote = max(evil_probabilities, key=evil_probabilities.get)
        return vote
    
    def my_accuracy(self):
        if self.total_predictions == 0: return 1 # Might as well assume our a priori is correct.
        #num = self.correct_predictions / self.total_predictions
        #if num > 1:
        #    log(f'OUTLIER: {self.correct_predictions}, {self.total_predictions}')
        return self.correct_predictions / self.total_predictions

    def getName(self):
        return self.my_name

    def initialize(self, base_info, diff_data, game_setting):
        self.game_setting = game_setting
        self.id = base_info['agentIdx']
        self.role = base_info['myRole']
        self.state.player_list = list(range(1,game_setting['playerNum']+1))

    def update(self, base_info, diff_data, request):
        self.state.update(diff_data, request)
        if request == 'FINISH':
            log('---FINISH---')
            log(str(diff_data))
            self.correct_predictions += self.state.get_prediction_accuracy(self.my_predictions)
            self.total_predictions += len(self.my_predictions)
            log(f'MY ACCURACY: {self.my_accuracy()}')
            for player in self.state.player_list:
                log(f'AGENT {player} ACCURACY: {self.state.get_player_accuracy(player)}')
            self.my_predictions = []

    def dayStart(self):
        pass

    def talk(self):
        try:
            target = self.choose_vote()
            if target and self.my_vote != target:
                self.my_vote = target
                return cb.vote(target)
        except: pass
        return cb.over()

    def whisper(self):
        return cb.over()

    def vote(self):
        return self.choose_vote()

    def attack(self):
        return self.id

    def divine(self):
        return self.id

    def guard(self):
        return self.id

    def finish(self):
        pass

agent = PolicyAgent('policy', POLICY)

if __name__ == '__main__':
    aiwolfpy.connect_parse(agent)
