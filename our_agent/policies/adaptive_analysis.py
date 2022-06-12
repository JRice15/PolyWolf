from policies.base_agenda import Agenda
import math

# Correct voting analysis is more important towards the end of the day, and towards the end of the game.
class AdaptiveAnalysis(Agenda):
    def __init__(self, agent):
        super().__init__(agent)
        self.weights['vote'] = 1
        self.weight_factor = self.weights['vote']
        self.reads = None
    def reset(self):
        self.weights['vote'] = self.weight_factor
        self.reads = None
    # Vote for suspicious people. Adapt our own weights.
    def vote(self):
        if self.agent.role == 'WEREWOLF' or self.agent.role == 'POSSESSED': return None
        self.weights['vote'] = math.sqrt(len(self.agent.state.player_list)-len(self.agent.state.current_living_players))
        self.weights['vote'] *= ((10-self.agent.state.talks_remaining)/7)
        self.weights['vote'] *= self.weight_factor
        if len(self.agent.state.player_list) > 8:
            self.reads = self.agent.estimator.vote_analysis_aggregate()
        else:
            return None # Todo: Implement analysis rules for 5-player games.
        self.reads[self.agent.id] = 0
        return self.reads