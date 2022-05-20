import math
from collections import defaultdict

from state import log

# TODO: Make the a priori 4/14 adaptable to games with different numbers of people, and to using the medium ability to concretely identify the current numerator and denominator of this fraction.

# Given that a player predicted another's alignment, compute the odds that they are right.
# Taking into account the probability that they are mistaken based on past games, and the probability that they themselves are a wolf, and the probability that they are a wolf who is bussing.
def prob_given_player(player_accuracy_village, player_accuracy_werewolf, player_sus):
    return (player_sus * player_accuracy_werewolf)  +  ((1-player_sus) * player_accuracy_village)

'''
p(ww) * p(t | ww) + p(vv) * p(t | vv)

p(t | ww) = p(ww & t) / p(ww)
p(t | vv) = p(vv & t) / p(vv)
'''

prior = 4/15

# Given a series of T/F statements each with a priori probabilities of being true or false.
# Solves probability of all statements being true, given the constraint that either they are all-true or all-false.
def aggregate_probs(probs):
    if 1 in probs: return 1
    probs = [prob for prob in probs if prob != 0]
    #log(f'aggregating: {probs}')
    if len(probs) == 0: return 0.28571428571
    ratio_true = math.exp( (sum([math.log(prob)-math.log(prior) for prob in probs])+math.log(prior)) - (sum([math.log(1-prob)-math.log(1-prior) for prob in probs])+math.log(1-prior)) )
    prob_true = ratio_true / (ratio_true+1)
    return prob_true

'''
p(ww | aww) = p(aww & ww) / p(aww) = p(aww & ww)
p(~ww | aww) = p(aww & ~ww) / p(aww) = p(aww & ~ww)
'''

# Default a priori suspicion is 4/14 = 0.28571428571, the number of evil players out of the total number of players of unknown alignment in a 15-player game. This is a place where having a role estimation of our own could be plugged in quite well.
def vote_analysis(state, myid, myread, myaccuracy):
    probs_table = defaultdict(list)
    evil_probabilities = {target:0.28571428571 for target in state.player_list}
    for agentid in state.votes_current.keys():
        if agentid == myid:
            prob = myaccuracy
            target = myread
        else:
            prob = prob_given_player(state.get_player_accuracy(agentid, werewolf=False), state.get_player_accuracy(agentid, werewolf=True), 0.26666666666)
            target = state.votes_current[agentid]
        log(f'{agentid} sussing {target} with {prob} likelihood of correctness')
        probs_table[target].append(prob)
    for target in probs_table.keys():
        evil_probabilities[target] = aggregate_probs(probs_table[target])
    evil_probabilities[myid] = 0
    #log(f'pre-computed evil probabilities: {evil_probabilities}')
    return evil_probabilities