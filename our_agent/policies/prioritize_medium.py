from policies.base_agenda import Agenda

# Agent prioritizes the lives of those who it thinks might be the medium. Both to end them as a werewolf, or to protect them as a bodyguard.
class MediumPriority(Agenda):
    def __init__(self, agent):
        super().__init__(agent)
        self.weights['attack'] = 0.25
        self.weights['protect'] = 0.25
    # The medium must die!
    def attack(self):
        if type(self.agent.estimator.predictions) == type(None): return None
        med_probabilities = self.agent.estimator.predictions[:,1] # Column 1 = Medium predictions
        med_probabilities = {player_id:med_probabilities[player_id-1] for player_id in self.agent.state.current_living_players}
        return med_probabilities
    # The medium must survive!
    def protect(self):
        return self.attack()
    # TODO: Implement something to claim medium and disprove any fake seers.