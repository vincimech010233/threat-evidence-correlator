# Threat Evidence Correlator

Intelligence analysts need to reconcile assertions without mistaking copied reports for independent corroboration. This Python/SQLite CLI ingests a deliberately restricted synthetic STIX-like profile, preserves immutable evidence IDs, UTC timestamps and provenance, normalizes entity names, detects overlapping contradictory assertions and produces an explainable analyst queue.

## Architecture, requirements and usage

Python 3.12 and bundled SQLite; no external packages. Validated import → transactional SQLite ledger (canonical payload and SHA256) → lineage graph → qualified entity groups → JSON/Markdown.

```sh
python3 -m unittest discover -s tests -v
python3 src/correlator.py --synthetic examples/intelligence.json results/lab.sqlite results/report.json results/report.md
```

Expected example: e1/e2 are one lineage, e3 contradicts their claim within the same interval, and e5/e6 match after name normalization with two declared lineages. Identical names in lab/other-lab remain separate with a QUALIFIED_MATCH_REVIEW item. Import is idempotent; changed payload under an existing ID rejects transactionally.

## Assessment rules and limitations

Half-open validity intervals [from,to) must overlap for contradiction. Shared source groups, artifacts or roots collapse transitively; unknown source groups are conservatively non-independent. MULTIPLE_DECLARED_LINEAGES remains INFERRED and is not a verified fact. Allegations stay ALLEGATION_ONLY; verified_fact is only an input assertion requiring a verification reference, not proof accepted by the tool. Every group remains in the review queue.

No full STIX support, probability calibration, fuzzy matching, freshness/decay model, targeting, real indicators, personal data or network activity. Synthetic software-family/campaign names only. Maximum 1000 records and 2 MB import; local database is excluded from Git. This offers transparent provenance teaching and small fixture analysis, not a replacement for threat intelligence platforms.

## Verification and publication

Evidence labels: VERIFIED = checked against a stated criterion; OBSERVED = measured execution; INFERRED = interpretation; HYPOTHESIS = proposed explanation; NOT_VERIFIED = missing evidence. Local status and executed commands are in `results/validation.json` and `docs/REVIEW.md`. Synthetic validation establishes implementation behavior, not production accuracy.

This is an independent Git repository with original MIT project code. Publication-gate evidence is in `results/publication-gate-20261012.json` and `docs/PUBLICATION_REVIEW.md`. The original local-delivery records are retained as historical evidence. CI uses public dependency registries and requires no secrets. See `docs/PROVENANCE.md` for dependency and advisory review scope.

## License

MIT; see LICENSE.

## Reproducing development checks

Optional public-registry dependency review: `python3 tools/dependency_audit.py .` writes `results/dependency-audit.json`. This developer check uses the free OSV API and is separate from offline application execution. Zero listed advisories does not prove absence of vulnerabilities. License evidence is in results/licenses.json and, for scientific projects, results/python-licenses.json.

Install `requirements-dev.txt` to run the recorded Ruff 0.17.0 source checks. Commands, actual versions, failed attempts, review corrections and measured peak RSS are retained in results/validation.json, results/tool-versions.json and docs/REVIEW.md. Check the GitHub Actions run for the exact commit before claiming hosted CI success; older local-delivery records retain their as-of NOT_VERIFIED status.
