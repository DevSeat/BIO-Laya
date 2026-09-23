"""Public-safe BIO-Laya adapter layer.

This package intentionally contains no BIO Core implementation, database access,
or private memory data. It only defines typed contracts for feeding already-
retrieved memory candidates into a Laya decision model in shadow mode.
"""

from .adapter import BioLayaAdapter, BioLayaBatch
from .evaluation import ShadowComparison, compare_with_gold
from .schemas import MemoryCandidate, MemoryQuery, ShadowDecision
from .shadow import BioLayaShadowJudge, ShadowJudgeError

__all__ = [
    "BioLayaAdapter",
    "BioLayaBatch",
    "BioLayaShadowJudge",
    "MemoryCandidate",
    "MemoryQuery",
    "ShadowComparison",
    "ShadowDecision",
    "ShadowJudgeError",
    "compare_with_gold",
]
