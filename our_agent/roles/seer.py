from collections import deque
from typing import Deque, List, Optional

from aiwolf import (Agent, ComingoutContentBuilder, Content,
                    DivinedResultContentBuilder, GameInfo, GameSetting,
                    Role, Species, VoteContentBuilder)
from aiwolf.constant import AGENT_NONE

from const import CONTENT_SKIP
from roles.villager import Villager


class Seer(Villager):

    not_divined_agents: List[Agent]
    """Agents that have not been divined."""
    werewolves: List[Agent]
    """Found werewolves."""

    def __init__(self) -> None:
        super().__init__()
        self.not_divined_agents = []
        self.werewolves = []

    def initialize(self, game_info: GameInfo, game_setting: GameSetting) -> None:
        super().initialize(game_info, game_setting)
        self.not_divined_agents = self.get_others(self.game_info.agent_list)
        self.werewolves.clear()

    def day_start(self) -> None:
        super().day_start()
        pass # TODO handle divine result

    def talk(self) -> Content:
        pass # TODO

    def divine(self) -> Agent:
        # TODO better rule
        # Divine a agent randomly chosen from undivined agents.
        target: Agent = self.random_select(self.not_divined_agents)
        return target if target != AGENT_NONE else self.me
