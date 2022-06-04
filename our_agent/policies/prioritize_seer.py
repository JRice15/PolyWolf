from policies.base_agenda import Agenda

# Agent prioritizes the lives of those who it thinks might be the seer. Both to end them as a werewolf, or to protect them as a bodyguard.
class SeerPriority(Agenda):
    def __init__(self, agent):
        super().__init__(agent)
        self.weights['attack'] = 1
        self.weights['protect'] = 1
    # The seer must die!
    def attack(self):
        if type(self.agent.estimator.predictions) == type(None): return None
        seer_probabilities = self.agent.estimator.predictions[:,3] # Column 3 = Seer predictions
        seer_probabilities = {player_id:seer_probabilities[player_id-1] for player_id in self.agent.state.current_living_players}
        return seer_probabilities
    # The seer must survive!
    def protect(self):
        return self.attack()