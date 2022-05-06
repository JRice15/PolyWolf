from aiwolf import Content, SkipContentBuilder
import os, sys

CONTENT_SKIP: Content = Content(SkipContentBuilder())

AGENT_ROOT = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(AGENT_ROOT)


ROLES_5_PLAYER = {
    "VILLAGER": 2,
    "SEER": 1,
    "POSSESSED": 1,
    "WEREWOLF": 1,
} # for 15 player games

ROLES_15_PLAYER = {
    "VILLAGER": 8,
    "SEER": 1,
    "MEDIUM": 1,
    "BODYGUARD": 1,
    "POSSESSED": 1,
    "WEREWOLF": 3,
} # for 15 player games
