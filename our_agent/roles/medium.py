from collections import deque
from typing import Deque, List, Optional

from aiwolf import (Agent, ComingoutContentBuilder, Content, GameInfo,
                    GameSetting, IdentContentBuilder, Role, Species,
                    VoteContentBuilder)
from aiwolf.constant import AGENT_NONE

from const import CONTENT_SKIP
from roles.villager import Villager


class Medium(Villager):

    def __init__(self) -> None:
        super().__init__()

    def initialize(self, game_info: GameInfo, game_setting: GameSetting) -> None:
        super().initialize(game_info, game_setting)
        pass # TODO

    def day_start(self) -> None:
        super().day_start()
        pass # TODO

    def talk(self) -> Content:
        pass # TODO
