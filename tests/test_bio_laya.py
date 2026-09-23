import pytest

from bio_laya import (
    BioLayaAdapter,
    BioLayaShadowJudge,
    MemoryCandidate,
    MemoryQuery,
    compare_with_gold,
)


def candidate(memory_id, rank, *, status="active"):
    return MemoryCandidate(
        memory_id=memory_id,
        title=f"title-{memory_id}",
        content=f"content for {memory_id}",
        baseline_rank=rank,
        status=status,
    )


def request():
    return MemoryQuery(
        query="What is the current project state?",
        candidates=(candidate("m2", 2), candidate("m1", 1), candidate("m3", 3)),
        project="demo",
    )


class FakeAgent:
    def __init__(self, choice="m2"):
        self.choice = choice

    def predict(self, state, questions):
        assert state["baseline_order"] == ["m1", "m2", "m3"]
        assert "best_memory" in questions
        return {
            "model": "fake-bio-laya",
            "answers": {
                "best_memory": {
                    "type": "choice",
                    "choice": self.choice,
                    "confidence": 0.87,
                },
                "needs_review": {"type": "noul", "noul": 0.2},
                "has_conflict": {"type": "noul", "noul": 0.1},
                "query_type": {
                    "type": "choice",
                    "choice": "temporal_update",
                },
            },
        }


def test_adapter_preserves_baseline_order_without_mutating_input():
    req = request()
    batch = BioLayaAdapter(max_candidates=3).build(req)
    assert batch.candidate_ids == ("m1", "m2", "m3")
    assert tuple(item.memory_id for item in req.candidates) == ("m2", "m1", "m3")


def test_adapter_caps_shortlist():
    batch = BioLayaAdapter(max_candidates=2).build(request())
    assert batch.candidate_ids == ("m1", "m2")
    assert set(batch.questions["best_memory"]["criteria"]) == {"m1", "m2", "__none__"}


def test_shadow_judge_only_proposes_change():
    decision = BioLayaShadowJudge(FakeAgent("m2")).evaluate(request())
    assert decision.baseline_memory_id == "m1"
    assert decision.proposed_memory_id == "m2"
    assert decision.changed is True
    assert decision.query_type == "temporal_update"


def test_shadow_comparison_win_loss_states():
    decision = BioLayaShadowJudge(FakeAgent("m2")).evaluate(request())
    assert compare_with_gold(decision, "m2").outcome == "win"
    assert compare_with_gold(decision, "m1").outcome == "loss"


def test_duplicate_candidate_ids_rejected():
    with pytest.raises(ValueError):
        MemoryQuery(
            query="q",
            candidates=(candidate("same", 1), candidate("same", 2)),
        )


def test_adapter_rejects_oversized_config():
    with pytest.raises(ValueError):
        BioLayaAdapter(max_candidates=21)
