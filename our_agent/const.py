from aiwolf import Content, SkipContentBuilder
import os, sys

CONTENT_SKIP: Content = Content(SkipContentBuilder())

AGENT_ROOT = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(AGENT_ROOT)
