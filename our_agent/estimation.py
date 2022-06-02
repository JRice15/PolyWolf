import math
from collections import defaultdict

class Estimator:
    def __init__(self, state):
        self.state = state
    def prior(self, player):
        evils = self.state.roles_counts['WEREWOLF'] + self.state.roles_counts['POSSESSED']
        total = len(self.state.player_list)
        for player in self.state.confirmed.keys():
            if self.state.confirmed[player] == 'WEREWOLF':
                evils -= 1
            total -= 1
        if player == self.state.id:
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
        probs_table = defaultdict(list)
        for agentid in self.state.votes_current.keys():
            if agentid == self.id: continue
            prob = self.prob_given_player(self.state.get_player_accuracy(agentid, werewolf=False), self.state.get_player_accuracy(agentid, werewolf=True), self.estimate_suspicion(agentid))
            target = self.state.votes_current[agentid]
            probs_table[target].append(prob)
        for predictor in self.predictors:
            if self.state.games > self.policy['prior_cutoff']: prob = predictor.accuracy()
            else: prob = predictor.prior
            target = predictor.predictions[-1]
            probs_table[target].append(prob)
        evil_probabilities = {target:self.prior(target) for target in self.state.player_list}
        for target in probs_table.keys():
            evil_probabilities[target] = self.aggregate_probs(probs_table[target], evil_probabilities[target])
        return evil_probabilities
    def neural_inference(self):
        return 0