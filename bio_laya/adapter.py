"""Adapter from an external memory shortlist to Laya state/questions."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Tuple

from .questions import memory_judge_questions
from .schemas import MemoryQuery


@dataclass(frozen=True)
class BioLayaBatch:
    state: Dict[str, Any]
    questions: Dict[str, Any]
    candidate_ids: Tuple[str, ...]


class BioLayaAdapter:
    """Builds a compact Laya request without touching the source memory store."""

    def __init__(
        self,
        *,
        max_candidates: int = 8,
        max_chars_per_candidate: int = 320,
        allow_abstain: bool = True,
    ) -> None:
        if not 1 <= max_candidates <= 20:
            raise ValueError("max_candidates must be between 1 and 20")
        if max_chars_per_candidate < 32:
            raise ValueError("max_chars_per_candidate must be >= 32")
        self.max_candidates = max_candidates
        self.max_chars_per_candidate = max_chars_per_candidate
        self.allow_abstain = allow_abstain

    def build(self, request: MemoryQuery) -> BioLayaBatch:
        ordered = tuple(
            sorted(request.candidates, key=lambda item: item.baseline_rank)
        )[: self.max_candidates]

        state_candidates = []
        for candidate in ordered:
            state_candidates.append(
                {
                    "memory_id": candidate.memory_id,
                    "baseline_rank": candidate.baseline_rank,
                    "title": candidate.title,
                    "content": candidate.compact_content(
                        self.max_chars_per_candidate
                    ),
                    "memory_type": candidate.memory_type,
                    "status": candidate.status,
                    "updated_at": candidate.updated_at,
                    "importance": candidate.importance,
                    "confidence": candidate.confidence,
                    "source": candidate.source,
                }
            )

        state = {
            "query": request.query,
            "project": request.project,
            "namespace": request.namespace,
            "as_of": request.as_of,
            "baseline_order": [item.memory_id for item in ordered],
            "candidates": state_candidates,
        }

        questions = memory_judge_questions(
            ordered,
            max_chars_per_candidate=self.max_chars_per_candidate,
            allow_abstain=self.allow_abstain,
        )
        return BioLayaBatch(
            state=state,
            questions=questions,
            candidate_ids=tuple(item.memory_id for item in ordered),
        )
