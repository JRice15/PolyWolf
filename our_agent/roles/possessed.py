import random
from collections import deque
from typing import Deque, List

from aiwolf import (Agent, ComingoutContentBuilder, Content,
                    DivinedResultContentBuilder, GameInfo, GameSetting,
                    IdentContentBuilder, Judge, Role, Species,
                    VoteContentBuilder)
from aiwolf.constant import AGENT_NONE

from const import CONTENT_SKIP, JUDGE_EMPTY
from villager import Villager


class Possessed(Villager):

    def __init__(self) -> None:
        super().__init__()

    def initialize(self, game_info: GameInfo, game_setting: GameSetting) -> None:
        super().initialize(game_info, game_setting)
        self.num_wolves = game_setting.role_num_map.get(Role.WEREWOLF, 0)

    def day_start(self) -> None:
        super().day_start()
        pass # TODO

    def talk(self) -> Content:
        pass # TODO
