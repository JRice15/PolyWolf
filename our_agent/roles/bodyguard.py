from typing import List

from aiwolf import Agent, GameInfo, GameSetting, Role, Species
from aiwolf.constant import AGENT_NONE

from roles.villager import Villager


class Bodyguard(Villager):

    to_be_guarded: Agent

    def __init__(self) -> None:
        super().__init__()

    def initialize(self, game_info: GameInfo, game_setting: GameSetting) -> None:
        super().initialize(game_info, game_setting)

    def guard(self) -> Agent:
        pass # TODO
