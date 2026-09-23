"""Typed public contracts for BIO-Laya shadow ranking."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping, Optional, Tuple


@dataclass(frozen=True)
class MemoryCandidate:
    """A compact candidate passed from an external memory system.

    BIO-Laya does not fetch or mutate memories. Callers provide a shortlist that
    is already safe to expose to the judge.
    """

    memory_id: str
    title: str
    content: str
    baseline_rank: int
    memory_type: Optional[str] = None
    status: Optional[str] = None
    updated_at: Optional[str] = None
    importance: Optional[float] = None
    confidence: Optional[float] = None
    source: Optional[str] = None
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.memory_id.strip():
            raise ValueError("memory_id must not be empty")
        if self.baseline_rank < 1:
            raise ValueError("baseline_rank must be >= 1")

    def compact_content(self, max_chars: int) -> str:
        text = " ".join(self.content.split())
        if len(text) <= max_chars:
            return text
        if max_chars < 2:
            return text[:max_chars]
        return text[: max_chars - 1] + "…"


@dataclass(frozen=True)
class MemoryQuery:
    """One query plus the baseline retrieval shortlist."""

    query: str
    candidates: Tuple[MemoryCandidate, ...]
    project: Optional[str] = None
    namespace: Optional[str] = None
    as_of: Optional[str] = None
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.query.strip():
            raise ValueError("query must not be empty")
        if not self.candidates:
            raise ValueError("at least one memory candidate is required")
        ids = [candidate.memory_id for candidate in self.candidates]
        if len(ids) != len(set(ids)):
            raise ValueError("memory candidate ids must be unique")

    @property
    def baseline_order(self) -> Tuple[str, ...]:
        return tuple(
            candidate.memory_id
            for candidate in sorted(self.candidates, key=lambda item: item.baseline_rank)
        )

    @property
    def baseline_best_id(self) -> str:
        return self.baseline_order[0]


@dataclass(frozen=True)
class ShadowDecision:
    """A non-mutating proposal produced by BIO-Laya."""

    baseline_memory_id: str
    proposed_memory_id: Optional[str]
    confidence: float
    needs_review_probability: float
    conflict_probability: float
    query_type: Optional[str]
    model_name: Optional[str]
    raw: Mapping[str, Any] = field(default_factory=dict)

    @property
    def changed(self) -> bool:
        return self.proposed_memory_id != self.baseline_memory_id

    @property
    def abstained(self) -> bool:
        return self.proposed_memory_id is None
