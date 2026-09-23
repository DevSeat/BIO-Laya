# BIO-Laya Roadmap

## v0.1 — Public-safe shadow judge foundation

- [x] separate bio_laya package
- [x] typed memory candidate schema
- [x] compact shortlist adapter
- [x] abstain option
- [x] shadow-only judge
- [x] win/loss comparison helper
- [x] synthetic unit tests
- [x] GitHub CI disabled; verification is local-only
- [ ] benchmark row import/export format

Gate: no memory-store write path exists. All verification is run locally; GitHub Actions must not be used for test execution.

## v0.2 — Dataset contract

Create a public-safe training/evaluation record format.

Target fields:

    query
    candidate_ids
    candidate_texts
    baseline_order
    gold_memory_id
    query_type
    source_dataset
    split

Private production examples must stay in a separate private repository or private artifact store.

Add:

- JSONL schema/versioning
- deterministic train/dev/test split
- hard-negative representation
- duplicate/leakage checks
- dataset fingerprint

## v0.3 — Shadow benchmark harness

Measure:

- top-1 accuracy
- hit@K preservation
- win / loss / same_good / same_bad
- MRR delta
- abstain rate
- per-query-type accuracy
- latency
- calibration / ECE where applicable

Required rule: proposed ranking must remain report-only.

## v0.4 — BIO domain fine-tuning

Fine-tune a checkpoint for memory judgment rather than using generic zero-shot behavior.

Training emphasis:

- hard negatives near baseline rank 1
- stale vs current memory
- preference retrieval
- assistant-response recall
- temporal updates
- multi-session linking
- explicit abstention

Keep training data and any checkpoint containing private BIO-derived examples outside this public fork unless the data is explicitly cleared for publication.

## v0.5 — Calibration and baseline protection

- temperature calibration on held-out data
- confidence thresholds
- review/abstain thresholds
- baseline top-1 demotion guard
- regression budget by query type
- deterministic shadow reports

Gate proposal for guarded use:

    overall win > loss
    no unacceptable regression in protected categories
    calibration measured on held-out data
    latency within target
    fallback behavior tested

## v0.6 — Optional guarded rerank API

Only after v0.5 gates pass:

- explicit opt-in rerank method
- baseline-preserving fallback
- confidence gate
- audit payload
- feature flag default OFF

BIO-Laya should still not own governance or persistence.

## v1.0 — Specialized decision checkpoint

Target:

    generic Laya runtime
    + BIO memory judgment training
    + calibrated abstention
    + benchmark-proven ranking
    = BIO-Laya specialized decision engine

Long-term, the trained dataset and evaluation harness can also serve as a teacher/evidence base for a future independent JudgeMan model.
