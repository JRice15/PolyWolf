from policies.base_agenda import Agenda
from aiwolfpy import contentbuilder as cb

# Agent prioritizes killing people who might be the bodyguard, or sharing identities of saved people if you are a bodyguard.
class BodyguardPriority(Agenda):
    def __init__(self, agent):
        super().__init__(agent)
        self.weights['attack'] = 0.25
    # The bodyguard must die!
    def attack(self):
        if type(self.agent.estimator.predictions) == type(None): return None
        bg_probabilities = self.agent.estimator.predictions[:,0] # Column 0 = Bodyguard predictions
        bg_probabilities = {player_id:bg_probabilities[player_id-1] for player_id in self.agent.state.current_living_players}
        return bg_probabilities