from aiwolf import AbstractPlayer, Agent, Content, GameInfo, GameSetting, Role

from bodyguard import Bodyguard
from medium import Medium
from possessed import Possessed
from seer import Seer
from villager import Villager
from werewolf import Werewold


class RoleAssignPlayer(AbstractPlayer):

    villager: AbstractPlayer
    bodyguard: AbstractPlayer
    medium: AbstractPlayer
    seer: AbstractPlayer
    possessed: AbstractPlayer
    werewolf: AbstractPlayer
    player: AbstractPlayer

    def __init__(self) -> None:
        self.villager = Villager()
        self.bodyguard = Bodyguard()
        self.medium = Medium()
        self.seer = Seer()
        self.possessed = Possessed()
        self.werewolf = Werewolf()
        self.player = self.villager

    def attack(self) -> Agent:
        return self.player.attack()

    def day_start(self) -> None:
        self.player.day_start()

    def divine(self) -> Agent:
        return self.player.divine()

    def finish(self) -> None:
        self.player.finish()

    def guard(self) -> Agent:
        return self.player.guard()

    def initialize(self, game_info: GameInfo, game_setting: GameSetting) -> None:
        role = game_info.my_role
        if role == Role.VILLAGER:
            self.player = self.villager
        elif role == Role.BODYGUARD:
            self.player = self.bodyguard
        elif role == Role.MEDIUM:
            self.player = self.medium
        elif role == Role.SEER:
            self.player = self.seer
        elif role == Role.POSSESSED:
            self.player = self.possessed
        elif role == Role.WEREWOLF:
            self.player = self.werewolf
        self.player.initialize(game_info, game_setting)

    def talk(self) -> Content:
        return self.player.talk()

    def update(self, game_info: GameInfo) -> None:
        self.player.update(game_info)

    def vote(self) -> Agent:
        return self.player.vote()

    def whisper(self) -> Content:
        return self.player.whisper()
