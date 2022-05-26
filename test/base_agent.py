# Base class for other agents to inherit.

import aiwolfpy
import aiwolfpy.contentbuilder as cb

from state import GameState

class Agent(object):
    def __init__(self, agent_name):
        self.state = GameState()
        self.name = agent_name

    def getName(self):
        return self.name

    def initialize(self, base_info, diff_data, game_setting):
        self.game_setting = game_setting
        self.id = base_info['agentIdx']
        self.role = base_info['myRole']
        self.state.player_list = list(range(1,game_setting['playerNum']+1))
        self.state.current_living_players = self.state.player_list.copy()
        self.state.roles_counts = game_setting['roleNumMap']

    def update(self, base_info, diff_data, request):
        self.state.update(diff_data, request)

    def dayStart(self):
        pass

    def talk(self):
        return cb.over()

    def whisper(self):
        return cb.over()

    def vote(self):
        return self.id

    def attack(self):
        return self.id

    def divine(self):
        return self.id

    def guard(self):
        return self.id

    def finish(self):
        pass