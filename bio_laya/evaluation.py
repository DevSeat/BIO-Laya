"""Evaluation helpers for BIO-Laya shadow decisions."""

from __future__ import annotations

from dataclasses import dataclass

from .schemas import ShadowDecision


@dataclass(frozen=True)
class ShadowComparison:
    gold_memory_id: str
    baseline_correct: bool
    proposed_correct: bool
    outcome: str
    abstained: bool


def compare_with_gold(
    decision: ShadowDecision,
    gold_memory_id: str,
) -> ShadowComparison:
    if not gold_memory_id:
        raise ValueError("gold_memory_id must not be empty")

    baseline_correct = decision.baseline_memory_id == gold_memory_id
    proposed_correct = decision.proposed_memory_id == gold_memory_id

    if baseline_correct and proposed_correct:
        outcome = "same_good"
    elif not baseline_correct and proposed_correct:
        outcome = "win"
    elif baseline_correct and not proposed_correct:
        outcome = "loss"
    else:
        outcome = "same_bad"

    return ShadowComparison(
        gold_memory_id=gold_memory_id,
        baseline_correct=baseline_correct,
        proposed_correct=proposed_correct,
        outcome=outcome,
        abstained=decision.abstained,
    )
