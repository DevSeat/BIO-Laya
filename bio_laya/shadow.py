"""Shadow-only BIO-Laya judge.

The judge proposes a best candidate but never applies a reorder and never writes
to any memory database.
"""

from __future__ import annotations

from typing import Any, Protocol

from .adapter import BioLayaAdapter
from .questions import ABSTAIN_ID
from .schemas import MemoryQuery, ShadowDecision


class PredictLike(Protocol):
    def predict(self, state: Any, questions: Any) -> dict:
        ...


class ShadowJudgeError(RuntimeError):
    pass


class BioLayaShadowJudge:
    def __init__(self, agent: PredictLike, *, adapter: BioLayaAdapter | None = None) -> None:
        self.agent = agent
        self.adapter = adapter or BioLayaAdapter()

    @staticmethod
    def _answer(result: dict, name: str) -> dict:
        try:
            answer = result["answers"][name]
        except (KeyError, TypeError) as exc:
            raise ShadowJudgeError(f"missing answer: {name}") from exc
        if not isinstance(answer, dict):
            raise ShadowJudgeError(f"invalid answer payload: {name}")
        return answer

    def evaluate(self, request: MemoryQuery) -> ShadowDecision:
        batch = self.adapter.build(request)
        result = self.agent.predict(batch.state, batch.questions)
        if not isinstance(result, dict):
            raise ShadowJudgeError("agent.predict() must return a dict")

        best = self._answer(result, "best_memory")
        proposed = best.get("choice")
        if proposed == ABSTAIN_ID:
            proposed = None
        elif proposed not in batch.candidate_ids:
            raise ShadowJudgeError(
                f"model selected unknown candidate {proposed!r}"
            )

        needs_review = self._answer(result, "needs_review").get("noul")
        conflict = self._answer(result, "has_conflict").get("noul")
        query_type = self._answer(result, "query_type").get("choice")

        try:
            confidence = float(best.get("confidence", 0.0))
            needs_review_probability = float(needs_review)
            conflict_probability = float(conflict)
        except (TypeError, ValueError) as exc:
            raise ShadowJudgeError("model returned non-numeric probability") from exc

        return ShadowDecision(
            baseline_memory_id=request.baseline_best_id,
            proposed_memory_id=proposed,
            confidence=confidence,
            needs_review_probability=needs_review_probability,
            conflict_probability=conflict_probability,
            query_type=query_type,
            model_name=result.get("model"),
            raw=result,
        )
