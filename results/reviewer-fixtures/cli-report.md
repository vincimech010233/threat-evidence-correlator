# Threat Evidence Correlator

INFERRED; synthetic assertions only.

Names normalized with NFC/casefold/whitespace; namespace-qualified exact matches only. Conflicts require half-open time overlap. Source independence is supplied, not proven. No automatic verification or targeting.

- **DISPUTED** &#91;&#x27;software-family&#x27;, &#x27;lab&#x27;, &#x27;copper moth&#x27;&#93; / synthetic-feature: Conflicting values overlap in validity time.
  Evidence: &#91;&#x27;e1&#x27;, &#x27;e2&#x27;, &#x27;e3&#x27;&#93;; lineage groups: &#91;&#91;&#x27;e1&#x27;, &#x27;e2&#x27;&#93;, &#91;&#x27;e3&#x27;&#93;&#93;; contradictions: &#91;&#91;&#x27;e1&#x27;, &#x27;e3&#x27;&#93;, &#91;&#x27;e2&#x27;, &#x27;e3&#x27;&#93;&#93;
- **MULTIPLE_DECLARED_LINEAGES** &#91;&#x27;software-family&#x27;, &#x27;lab&#x27;, &#x27;silver kite&#x27;&#93; / synthetic-feature: Distinct declared roots support review; independence and truth are not externally verified.
  Evidence: &#91;&#x27;e5&#x27;, &#x27;e6&#x27;&#93;; lineage groups: &#91;&#91;&#x27;e5&#x27;&#93;, &#91;&#x27;e6&#x27;&#93;&#93;; contradictions: &#91;&#93;
- **SINGLE_LINEAGE** &#91;&#x27;software-family&#x27;, &#x27;other-lab&#x27;, &#x27;copper moth&#x27;&#93; / synthetic-feature: Shared or unknown provenance prevents independent corroboration.
  Evidence: &#91;&#x27;e4&#x27;&#93;; lineage groups: &#91;&#91;&#x27;e4&#x27;&#93;&#93;; contradictions: &#91;&#93;

## Analyst queue

- DISPUTED: &#91;&#x27;software-family&#x27;, &#x27;lab&#x27;, &#x27;copper moth&#x27;&#93; — Conflicting values overlap in validity time.
- MULTIPLE_DECLARED_LINEAGES: &#91;&#x27;software-family&#x27;, &#x27;lab&#x27;, &#x27;silver kite&#x27;&#93; — Distinct declared roots support review; independence and truth are not externally verified.
- SINGLE_LINEAGE: &#91;&#x27;software-family&#x27;, &#x27;other-lab&#x27;, &#x27;copper moth&#x27;&#93; — Shared or unknown provenance prevents independent corroboration.
- QUALIFIED_MATCH_REVIEW: &#91;&#x27;software-family&#x27;, &#x27;copper moth&#x27;&#93; — Same normalized name in distinct namespaces; do not merge.
