import random
from typing import Dict, List

from aiwolf import (AbstractPlayer, Agent, Content, GameInfo, GameSetting,
                    Judge, Role, Species, Status, Talk, Topic,
                    VoteContentBuilder)
from aiwolf.constant import AGENT_NONE

from const import CONTENT_SKIP


class Villager(AbstractPlayer):

    me: Agent
    """Agent number of self"""
    game_info: GameInfo
    """Information about current game."""
    game_setting: GameSetting
    """Settings of current game."""

    def __init__(self) -> None:
        self.me = AGENT_NONE
        self.game_info = None

    def initialize(self, game_info: GameInfo, game_setting: GameSetting) -> None:
        self.game_info = game_info
        self.game_setting = game_setting
        self.me = game_info.me
        # TODO

    def day_start(self) -> None:
        pass # TODO

    def update(self, game_info: GameInfo) -> None:
        self.game_info = game_info  # Update game information.
        pass # TODO

    def talk(self) -> Content:
        raise NotImplementedError() # TODO

    def vote(self) -> Agent:
        raise NotImplementedError() # TODO

    # these methods shiuld not be implemented in the Villager
    def attack(self) -> Agent:
        raise NotImplementedError()
    def divine(self) -> Agent:
        raise NotImplementedError()
    def guard(self) -> Agent:
        raise NotImplementedError()
    def whisper(self) -> Content:
        raise NotImplementedError()

    def finish(self) -> None:
        pass

    def is_alive(self, agent: Agent) -> bool:
        """Return whether the agent is alive.
        Args:
            agent: The agent.
        Returns:
            True if the agent is alive, otherwise false.
        """
        return self.game_info.status_map[agent] == Status.ALIVE

    def get_others(self, agent_list: List[Agent]) -> List[Agent]:
        """Return a list of agents excluding myself from the given list of agents.
        Args:
            agent_list: The list of agent.
        Returns:
            A list of agents excluding myself from agent_list.
        """
        return [a for a in agent_list if a != self.me]

    def get_alive(self, agent_list: List[Agent]) -> List[Agent]:
        """Return a list of alive agents contained in the given list of agents.
        Args:
            agent_list: The list of agents.
        Returns:
            A list of alive agents contained in agent_list.
        """
        return [a for a in agent_list if self.is_alive(a)]

    def get_alive_others(self, agent_list: List[Agent]) -> List[Agent]:
        """Return a list of alive agents that is contained in the given list of agents
        and is not equal to myself.
        Args:
            agent_list: The list of agents.
        Returns:
            A list of alie agents that is contained in agent_list
            and is not equal to mysef.
        """
        return self.get_alive(self.get_others(agent_list))

    def random_select(self, agent_list: List[Agent]) -> Agent:
        """Return one agent randomly chosen from the given list of agents.
        Args:
            agent_list: The list of agents.
        Returns:
            A agent randomly chosen from agent_list.
        """
        return random.choice(agent_list) if agent_list else AGENT_NONE