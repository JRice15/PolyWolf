from policies.base_agenda import Agenda

# Agent prioritizes killing people who might be the bodyguard.
class BodyguardPriority(Agenda):
    def __init__(self, agent):
        super().__init__(agent)
        self.weights['attack'] = 1
    # The bodyguard must die!
    def attack(self):
        if type(self.agent.estimator.predictions) == type(None): return None
        bg_probabilities = self.agent.estimator.predictions[:,0] # Column 0 = Bodyguard predictions
        bg_probabilities = {player_id:bg_probabilities[player_id-1] for player_id in self.agent.state.current_living_players}
        return bg_probabilities