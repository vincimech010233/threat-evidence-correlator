# Acceptance criteria

1. Fixture distinguishes copied evidence, contradictions, normalized exact matches and qualified ambiguity.
2. Nonoverlapping differing values are not contradictions; unknown sources and allegations are not verification.
3. Missing/cyclic lineage and invalid timestamps/entity kinds reject.
4. SQLite import is transactional/idempotent; evidence IDs immutable.
5. Output deterministic under import permutations and Markdown escaped; eight unit/integration tests and CLI run pass.

All criteria must be executed locally or explicitly listed as unresolved. Reviewer acceptance is bounded by this profile.
