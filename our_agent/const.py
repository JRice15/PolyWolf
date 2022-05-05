from aiwolf import Content, Judge, SkipContentBuilder
import os, sys

CONTENT_SKIP: Content = Content(SkipContentBuilder())

JUDGE_EMPTY: Judge = Judge()

AGENT_ROOT = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(AGENT_ROOT)