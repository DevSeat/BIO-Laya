"""Question builders for BIO-oriented memory judgment."""

from __future__ import annotations

from typing import Dict, Iterable

from .schemas import MemoryCandidate

ABSTAIN_ID = "__none__"
MAX_CHOICE_CANDIDATES = 20


def _criterion(candidate: MemoryCandidate, *, max_chars: int) -> str:
    fields = [
        f"title={candidate.title}",
        f"content={candidate.compact_content(max_chars)}",
    ]
    if candidate.memory_type:
        fields.append(f"type={candidate.memory_type}")
    if candidate.status:
        fields.append(f"status={candidate.status}")
    if candidate.updated_at:
        fields.append(f"updated_at={candidate.updated_at}")
    return " | ".join(fields)


def memory_judge_questions(
    candidates: Iterable[MemoryCandidate],
    *,
    max_chars_per_candidate: int = 320,
    allow_abstain: bool = True,
) -> Dict:
    """Build a stable typed-decision schema for a memory shortlist."""

    candidates = tuple(candidates)
    if not candidates:
        raise ValueError("at least one candidate is required")
    if len(candidates) > MAX_CHOICE_CANDIDATES:
        raise ValueError(
            f"BIO-Laya supports at most {MAX_CHOICE_CANDIDATES} candidates per judge pass"
        )

    criteria = {
        candidate.memory_id: _criterion(
            candidate, max_chars=max_chars_per_candidate
        )
        for candidate in candidates
    }
    if allow_abstain:
        criteria[ABSTAIN_ID] = (
            "None of the candidates is sufficiently relevant or trustworthy "
            "to represent the current answer."
        )

    return {
        "best_memory": {
            "type": "choice",
            "instructions": (
                "Choose the single memory candidate that best answers query. "
                "Prefer directly relevant, current, non-superseded information. "
                "Treat stale, contradicted, or weakly related memories cautiously. "
                "Do not invent facts that are absent from the candidates."
            ),
            "criteria": criteria,
        },
        "needs_review": {
            "type": "noul",
            "instructions": (
                "Do the candidates leave meaningful ambiguity, conflict, or insufficient "
                "evidence such that a higher-quality judge or human review is warranted?"
            ),
        },
        "has_conflict": {
            "type": "noul",
            "instructions": (
                "Do two or more candidate memories materially conflict about the answer "
                "or current state relevant to query?"
            ),
        },
        "query_type": {
            "type": "choice",
            "instructions": "Which memory-retrieval pattern best describes query?",
            "criteria": {
                "direct_fact": "a direct fact or stable user/project detail",
                "preference": "a user preference, taste, constraint, or recommendation context",
                "assistant_recall": "what an assistant previously said, produced, or recommended",
                "temporal_update": "current state, latest version, change, correction, or update",
                "multi_session": "information that must be connected across multiple interactions",
                "other": "none of the other categories clearly fits",
            },
        },
    }
