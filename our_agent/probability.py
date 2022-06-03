import math
from collections import defaultdict
import numpy as np

from role_estimation.load_rnn_estimator import RoleEstimatorRNN
from logger import log

# Possible ways to improve analysis:
#   -Analysis of past votes to determine connections, who could conceivably be in a three-wolf team and who *couldn't*, based on who voted for whom and the propensity of evil players to vote for teammates
#   -Addition of possessed probability to estimation of suspicion
#   -Use of the neural estimator probability directly in aggregate_probs
#   -Use of neural estimator probability in place of or in conjunction with prior(), averaged with prior() and/or offset so the distribution hits the same average as prior()

class Estimator:
    def __init__(self, agent):
        self.agent = agent
        self.state = self.agent.state
        self.role_estimator = RoleEstimatorRNN()
        self.predictions = None
        self.current_pred = None
        self.past_preds = []
        self.correct_preds = 0
        self.total_preds = 0
    def update(self, base_info, diff_data, request):
        self.predictions = self.role_estimator.update_and_predict(base_info=base_info, diff_data=diff_data, request=request)
        if type(self.predictions) != type(None) and not self.predictions.empty:
            self.predictions = self.predictions.to_numpy()
            offset = max(abs(min(self.predictions.flatten())), abs(max(self.predictions.flatten())))
            for row in self.predictions:
                row += offset
                row /= sum(row)
        if request == 'VOTE':
            self.past_preds.append(self.current_pred)
        if request == 'FINISH':
            log('---FINISH---')
            log(f'My ID: {self.agent.id}')
            self.correct_preds += self.state.get_prediction_accuracy(self.past_preds)
            self.total_preds += len(self.past_preds)
            self.past_preds = []
            log(f'PREDICTOR ACCURACY: {self.correct_preds/self.total_preds}')
            for player in self.state.player_list:
                log(f'AGENT {player} ACCURACY: {self.state.get_player_accuracy(player)}')
        if request == 'DAILY_INITIALIZE':
            if self.agent.role == 'BODYGUARD' and self.state.day > 1 and (not len(self.state.murdered_players.values()) or max(self.state.murdered_players.values()) != self.state.day):
                self.state.confirmed[self.agent.target] = 'HUMAN'
    def estimate_suspicions(self):
        suspicions = self.predictions[:,-1] + self.predictions[:,2] # Werewolf prob + possessed prob
        return {player_id:suspicions[player_id-1] for player_id in self.state.current_living_players}
    def prior(self, player):
        evils = self.state.roles_counts['WEREWOLF'] + self.state.roles_counts['POSSESSED']
        total = len(self.state.player_list)
        for player in self.state.confirmed.keys():
            if self.state.confirmed[player] == 'WEREWOLF':
                evils -= 1
            total -= 1
        if player == self.agent.id:
            return 0
        if player in self.state.confirmed.keys():
            if self.state.confirmed[player] == 'WEREWOLF':
                return 1
            return self.state.roles_counts['POSSESSED'] / total
        return evils / total
    def prob_given_player(self, player_accuracy_village, player_accuracy_werewolf, player_sus):
        if player_accuracy_werewolf == None: player_accuracy_werewolf = 0
        if player_accuracy_village == None: return None
        return (player_sus * player_accuracy_werewolf)  +  ((1-player_sus) * player_accuracy_village)
    def aggregate_probs(self, probs, prior):
        if 1 in probs or prior == 1: return 1
        if 0 in probs or prior == 0: return 0
        probs = [prob for prob in probs if prob != None]
        if len(probs) == 0: return prior
        ratio_true = math.exp( (sum([math.log(prob)-math.log(prior) for prob in probs])+math.log(prior)) - (sum([math.log(1-prob)-math.log(1-prior) for prob in probs])+math.log(1-prior)) )
        prob_true = ratio_true / (ratio_true+1)
        return prob_true
    def vote_analysis(self):
        if type(self.predictions) != type(None):
            neural_suspicions = self.estimate_suspicions()
        else:
            log('aaaaaaaaaaaaaaa')
            neural_suspicions = {pid:self.prior(pid) for pid in self.state.current_living_players}
        probs_table = defaultdict(list)
        for agentid in self.state.votes_current.keys():
            if agentid == self.agent.id: continue
            prob = self.prob_given_player(self.state.get_player_accuracy(agentid, werewolf=False), self.state.get_player_accuracy(agentid, werewolf=True), self.prior(agentid)) # neural_suspicions[agentid])
            target = self.state.votes_current[agentid]
            probs_table[target].append(prob)
        if self.state.games > 5: prob = (self.correct_preds / self.total_preds)
        else: prob = 1
        self.current_pred = max(neural_suspicions, key=neural_suspicions.get)
        probs_table[self.current_pred].append(prob)
        evil_probabilities = {target:self.prior(target) for target in self.state.player_list}
        for target in probs_table.keys():
            evil_probabilities[target] = self.aggregate_probs(probs_table[target], evil_probabilities[target])
        return evil_probabilities