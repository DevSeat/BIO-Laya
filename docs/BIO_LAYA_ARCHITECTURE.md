# BIO-Laya Architecture v0.1

## Purpose

BIO-Laya is a domain-specialized fork of Laya for memory candidate judgment.

The first integration target is shadow-mode ranking: an external memory system retrieves a small top-K shortlist, BIO-Laya proposes which candidate is best, and evaluation code compares that proposal with the existing baseline.

BIO-Laya is not a memory database and does not own memory truth.

## Public repository boundary

This fork is public because it descends from a public GitHub repository.

Therefore this repository must never contain:

- private BIO Core source code
- production memory databases or exports
- user memory content
- secrets, keys, tokens, or recovery material
- proprietary training examples derived from private memory
- private checkpoints trained on confidential data
- production configuration that reveals private infrastructure

Only generic interfaces, synthetic fixtures, public benchmark adapters, and public-safe documentation belong here.

## v0.1 data flow

    External memory retrieval
            |
            v
    Top-K candidate shortlist
            |
            v
    BioLayaAdapter
            |
            +--> compact state
            +--> typed questions
            |
            v
    Laya decision checkpoint
            |
            v
    ShadowDecision
            |
            v
    win / loss / same_good / same_bad evaluation

There is deliberately no write path back into a memory store.

## Hard invariants

1. Shadow mode is the default and only v0.1 mode.
2. BIO-Laya never mutates candidate ordering in-place.
3. BIO-Laya never writes to a memory database.
4. BIO-Laya may abstain with the reserved __none__ choice.
5. Candidate count is capped at 20; the default shortlist is 8.
6. Private BIO implementation details stay outside this public fork.
7. A future production reranker requires benchmark evidence, calibration, and a baseline-protection policy before activation.

## Typed decisions

The initial judge emits four signals in one call:

- best_memory: candidate choice or abstain
- needs_review: probability that escalation/review is needed
- has_conflict: probability that relevant candidates conflict
- query_type: direct fact / preference / assistant recall / temporal update / multi-session / other

These are judgment signals, not memory truth.

## Why a separate bio_laya package?

The upstream laya package stays as intact as possible so upstream updates can be merged with less conflict. BIO-specific code lives under bio_laya/.

This also creates a clean future path:

    upstream Laya
        -> BIO-Laya adapter + datasets
        -> BIO-specialized fine-tuned checkpoint
        -> calibrated shadow evaluation
        -> optional guarded integration
