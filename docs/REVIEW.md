# Critical review — Threat Evidence Correlator

Reviewer: separate agent using the developer's model, not an independent model or external audit. Scope: authorized offline synthetic records, provenance graph, temporal rules, SQLite imports and reports. No personal investigations, operational targeting or external collection.

VERIFIED: **VALIDATED_LOCAL** for the bounded criteria in `docs/ACCEPTANCE.md`, after two substantive corrections. The initial implementation was rejected pending the fixes below. Production confidence, full STIX support and externally established source independence remain NOT_VERIFIED. Manual publication additionally requires final repository/privacy/artifact checks.

## Retained findings and fixes

1. **Intermediate provenance was omitted.** OBSERVED: the graph used root and current source/artifact sets but omitted intermediate ancestors. A four-record chain with an intermediate shared source incorrectly classified child and another matching assertion as MULTIPLE_DECLARED_LINEAGES. Correction: provenance sets propagate all ancestors. VERIFIED: the saved counterexample now produces SINGLE_LINEAGE with child/other in one connected component; added regression passes.
2. **Date-only input bypassed the UTC timestamp boundary.** OBSERVED: `2026-01-01Z` parsed as a naive datetime without UTC timezone. Correction: require full date, T, seconds, optional fractional seconds and Z before parsing. VERIFIED: the saved date-only counterexample now raises the explicit timestamp validation error; added regression passes.

Original failing observations and report remain in `results/reviewer-fixtures/observations.json` and `intermediate-lineage-report.json`; corrected evidence is separately named in `retest-observations.json` and `intermediate-lineage-retest-report.json`.

## Independent execution and inspection

OBSERVED: initial eight tests passed despite the two defects. After corrections, `python3 -m unittest discover -s tests -v` passed ten tests; `python3 -m compileall -q src tests` passed. Reviewer executed the CLI against the synthetic fixture with a local SQLite database and fresh JSON/Markdown outputs, exit 0.

OBSERVED: a mixed import containing a new record followed by an immutable existing-ID conflict rejected and left all six original records unchanged; no new record was retained. Stored canonical payload SHA256 values matched independently recomputed digests. See `transaction-observations.json`. This verifies the executed import/digest behavior, not resistance to external database tampering.

VERIFIED by inspection and executed tests: exact namespace-qualified NFC/casefold/whitespace name matching; no fuzzy entity merge; contradictions require differing exact values and overlapping half-open intervals; boundary-touching intervals are nonoverlapping; missing parents/cycles reject. Shared source groups, artifacts and ancestry collapse transitively. Allegations and unknown provenance cannot become verified facts. Every group remains in the analyst queue. SQL values use parameterized statements; Markdown escapes supplied text. Record ordering and fixture import idempotence pass.

## Credibility, security and limits

INFERRED: preventing copied evidence from masquerading as corroboration is a credible analyst problem; the transparent synthetic graph and retained assertions provide portfolio value. Declared lineages are input metadata, not evidence of actual source independence or truth. verified_fact requires a supplied reference but does not promote that assertion to tool-verified status. No confidence probability is calibrated. Exact predicate/value text and namespace decisions can require analyst interpretation.

VERIFIED by inspection: strict synthetic profile and CLI scope flag; entity kinds restricted to software-family/campaign; no network/enrichment/targeting code; at most 1000 records and 2 MB/import. The marker and entity labels are supplied assertions, not proof of synthetic origin. UTC validity overlap is modeled; freshness/decay, derivation chronology and production throughput remain NOT_VERIFIED. Local SQLite data is excluded from Git.

OBSERVED: MIT license and standard-library-only implementation with dependency/provenance records. Research acknowledges mature intelligence platforms and includes public provenance-overlap history and historical security-advisory/CVE/fix/credit references; no new vulnerability or novelty claim is accepted. The reviewer inspected that record, not every linked remote history. Full legal/supply-chain review and authorship beyond supplied development evidence are NOT_VERIFIED. CI configuration needs no credentials; hosted execution is NOT_VERIFIED.

Follow-up: retain ancestry counterexamples and the input-assertion distinction when extending this teaching tool. Expanding to real intelligence, fuzzy entities or confidence calibration would require a new explicit scope and validation gate.
