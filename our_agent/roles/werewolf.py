import random
from typing import List

from aiwolf import (Agent, AttackContentBuilder, ComingoutContentBuilder,
                    Content, GameInfo, GameSetting, Role, Species)
from aiwolf.constant import AGENT_NONE

from const import CONTENT_SKIP
from roles.possessed import Possessed


class Werewolf(Possessed):

    allies: List[Agent]
    """Allies."""
    humans: List[Agent]
    """Humans."""

    def __init__(self) -> None:
        super().__init__()
        self.allies = []
        self.humans = []

    def initialize(self, game_info: GameInfo, game_setting: GameSetting) -> None:
        super().initialize(game_info, game_setting)
        self.allies = list(self.game_info.role_map.keys())
        self.humans = [a for a in self.game_info.agent_list if a not in self.allies]
        
    def day_start(self) -> None:
        super().day_start()
        pass # TODO

    def whisper(self) -> Content:
        pass # TODO

    def attack(self) -> Agent:
        pass # TODO
