"""Bounded synthetic provenance correlation; no STIX conformance or truth inference."""

import argparse
import datetime
import hashlib
import html
import json
import re
import sqlite3
import sys
import unicodedata
from collections import defaultdict
from pathlib import Path

FIELDS = {
    "id",
    "entity",
    "predicate",
    "value",
    "valid_from",
    "valid_to",
    "recorded_at",
    "source",
    "source_group",
    "artifact",
    "derived_from",
    "claim_kind",
    "verification_ref",
}


def text(s):
    if (
        not isinstance(s, str)
        or not s.strip()
        or len(s) > 512
        or any(ord(c) < 32 for c in s)
    ):
        raise ValueError("bounded nonempty text required")
    return s


def norm(s):
    return " ".join(unicodedata.normalize("NFC", text(s)).casefold().split())


def instant(s):
    if (
        not isinstance(s, str)
        or re.fullmatch(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d{1,6})?Z", s)
        is None
    ):
        raise ValueError("UTC timestamp ending Z required")
    return datetime.datetime.fromisoformat(s[:-1] + "+00:00")


def entity_key(e):
    if (
        not isinstance(e, dict)
        or set(e) != {"kind", "namespace", "name"}
        or e["kind"] not in {"software-family", "campaign"}
    ):
        raise ValueError("unsupported synthetic entity")
    return (e["kind"], norm(e["namespace"]), norm(e["name"]))


def lineage(records):
    by = {r["id"]: r for r in records}
    roots = {}
    remaining = set(by)
    while remaining:
        ready = sorted(
            k for k in remaining if all(p in roots for p in by[k]["derived_from"])
        )
        if not ready:
            raise ValueError("missing parent or cyclic evidence derivation")
        for k in ready:
            r = by[k]
            parents = r["derived_from"]
            roots[k] = set().union(*(roots[p] for p in parents)) | {k}
            remaining.remove(k)
    return roots


def validate(records):
    if not isinstance(records, list) or len(records) > 1000:
        raise ValueError("maximum 1000 records")
    ids = set()
    for r in records:
        if not isinstance(r, dict) or set(r) != FIELDS:
            raise ValueError("unsupported record fields")
        for k in ["id", "predicate", "value", "source", "artifact"]:
            text(r[k])
        if r["id"] in ids:
            raise ValueError("duplicate evidence id")
        ids.add(r["id"])
        entity_key(r["entity"])
        if r["source_group"] is not None:
            text(r["source_group"])
        if (
            not isinstance(r["derived_from"], list)
            or len(r["derived_from"]) > 1000
            or any(not isinstance(p, str) for p in r["derived_from"])
        ):
            raise ValueError("invalid parents")
        if r["claim_kind"] not in {"observation", "allegation", "verified_fact"}:
            raise ValueError("invalid claim kind")
        if r["claim_kind"] == "verified_fact":
            text(r["verification_ref"])
        elif r["verification_ref"] is not None:
            raise ValueError("verification reference requires verified_fact")
        start = instant(r["valid_from"])
        end = instant(r["valid_to"])
        instant(r["recorded_at"])
        if start >= end:
            raise ValueError("nonempty validity interval required")
    lineage(records)
    return records


def connect(path):
    db = sqlite3.connect(path)
    db.execute(
        "CREATE TABLE IF NOT EXISTS evidence (id TEXT PRIMARY KEY, payload TEXT NOT NULL, sha256 TEXT NOT NULL)"
    )
    return db


def ingest(db, bundle):
    if (
        not isinstance(bundle, dict)
        or set(bundle) != {"synthetic", "profile", "records"}
        or bundle["synthetic"] is not True
        or bundle["profile"] != "stix-like-fixture-v1"
    ):
        raise ValueError("synthetic fixture profile required")
    incoming = bundle["records"]
    if not isinstance(incoming, list):
        raise ValueError("records must be list")
    with db:
        existing = {r["id"]: r for r in load(db)}
        if len(incoming) > 1000:
            raise ValueError("maximum 1000 records")
        ids = set()
        for r in incoming:
            if not isinstance(r, dict) or "id" not in r or not isinstance(r["id"], str):
                raise ValueError("invalid record id")
            if r["id"] in ids:
                raise ValueError("duplicate id in import")
            ids.add(r["id"])
            if r["id"] in existing and existing[r["id"]] != r:
                raise ValueError("immutable evidence conflict")
            existing[r["id"]] = r
        validate(list(existing.values()))
        for r in incoming:
            payload = json.dumps(r, sort_keys=True, separators=(",", ":"))
            db.execute(
                "INSERT OR IGNORE INTO evidence VALUES (?,?,?)",
                (r["id"], payload, hashlib.sha256(payload.encode()).hexdigest()),
            )
    return len(load(db))


def load(db):
    return [
        json.loads(row[0])
        for row in db.execute("SELECT payload FROM evidence ORDER BY id")
    ]


def independent_groups(rows, all_records, roots):
    # Conservative connected components: shared declared group, artifact, or evidence ancestry.
    by = {r["id"]: r for r in all_records}
    families = {
        r["id"]: {by[k]["source_group"] or "UNKNOWN" for k in roots[r["id"]]}
        | {r["source_group"] or "UNKNOWN"}
        for r in rows
    }
    artifacts = {
        r["id"]: {by[k]["artifact"] for k in roots[r["id"]]} | {r["artifact"]}
        for r in rows
    }
    parent = list(range(len(rows)))

    def find(i):
        while parent[i] != i:
            parent[i] = parent[parent[i]]
            i = parent[i]
        return i

    for i, a in enumerate(rows):
        for j, b in enumerate(rows[:i]):
            if (
                families[a["id"]] & families[b["id"]]
                or artifacts[a["id"]] & artifacts[b["id"]]
                or roots[a["id"]] & roots[b["id"]]
            ):
                parent[find(i)] = find(j)
    return [
        sorted(rows[i]["id"] for i in range(len(rows)) if find(i) == g)
        for g in sorted({find(i) for i in range(len(rows))})
    ]


def correlate(records):
    validate(records)
    records = sorted(records, key=lambda r: r["id"])
    roots = lineage(records)
    groups = defaultdict(list)
    names = defaultdict(set)
    for r in records:
        e = entity_key(r["entity"])
        groups[(e, r["predicate"])].append(r)
        names[(e[0], e[2])].add(e[1])
    reports = []
    queue = []
    for (entity, predicate), rows in sorted(groups.items()):
        contradictions = []
        for i, a in enumerate(rows):
            for b in rows[:i]:
                if a["value"] != b["value"] and max(
                    instant(a["valid_from"]), instant(b["valid_from"])
                ) < min(instant(a["valid_to"]), instant(b["valid_to"])):
                    contradictions.append(sorted([a["id"], b["id"]]))
        independent = independent_groups(rows, records, roots)
        if contradictions:
            assessment = "DISPUTED"
        elif all(r["claim_kind"] == "allegation" for r in rows):
            assessment = "ALLEGATION_ONLY"
        elif len(independent) < 2:
            assessment = "SINGLE_LINEAGE"
        else:
            assessment = "MULTIPLE_DECLARED_LINEAGES"
        reason = {
            "DISPUTED": "Conflicting values overlap in validity time.",
            "ALLEGATION_ONLY": "Repeated allegations do not establish observations.",
            "SINGLE_LINEAGE": "Shared or unknown provenance prevents independent corroboration.",
            "MULTIPLE_DECLARED_LINEAGES": "Distinct declared roots support review; independence and truth are not externally verified.",
        }[assessment]
        result = {
            "entity": list(entity),
            "predicate": predicate,
            "classification": "INFERRED",
            "assessment": assessment,
            "reason": reason,
            "independent_lineage_groups": independent,
            "contradictions": sorted(contradictions),
            "assertions": rows,
        }
        reports.append(result)
        queue.append(
            {
                "entity": list(entity),
                "predicate": predicate,
                "action": reason,
                "assessment": assessment,
            }
        )
    for (kind, name), namespaces in sorted(names.items()):
        if len(namespaces) > 1:
            queue.append(
                {
                    "entity": [kind, name],
                    "assessment": "QUALIFIED_MATCH_REVIEW",
                    "action": "Same normalized name in distinct namespaces; do not merge.",
                    "namespaces": sorted(namespaces),
                }
            )
    return {
        "profile": "stix-like-fixture-v1",
        "synthetic": True,
        "classification": "INFERRED",
        "groups": reports,
        "review_queue": queue,
        "policy": "Names normalized with NFC/casefold/whitespace; namespace-qualified exact matches only. Conflicts require half-open time overlap. Source independence is supplied, not proven. No automatic verification or targeting.",
    }


def markdown(report):
    def esc(x):
        return (
            html.escape(str(x))
            .replace("`", "&#96;")
            .replace("[", "&#91;")
            .replace("]", "&#93;")
        )

    lines = [
        "# Threat Evidence Correlator",
        "",
        "INFERRED; synthetic assertions only.",
        "",
        esc(report["policy"]),
        "",
    ]
    for group in report["groups"]:
        lines.extend(
            [
                f"- **{esc(group['assessment'])}** {esc(group['entity'])} / {esc(group['predicate'])}: {esc(group['reason'])}",
                f"  Evidence: {esc([r['id'] for r in group['assertions']])}; lineage groups: {esc(group['independent_lineage_groups'])}; contradictions: {esc(group['contradictions'])}",
            ]
        )
    lines += ["", "## Analyst queue", ""] + [
        f"- {esc(q['assessment'])}: {esc(q['entity'])} — {esc(q['action'])}"
        for q in report["review_queue"]
    ]
    return "\n".join(lines) + "\n"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--synthetic", action="store_true", required=True)
    parser.add_argument("input")
    parser.add_argument("database")
    parser.add_argument("json_output")
    parser.add_argument("markdown_output")
    a = parser.parse_args()
    try:
        p = Path(a.input)
        if p.stat().st_size > 2_000_000:
            raise ValueError("input exceeds 2 MB")
        with connect(a.database) as db:
            ingest(db, json.loads(p.read_text()))
            report = correlate(load(db))
        Path(a.json_output).write_text(
            json.dumps(report, indent=2, sort_keys=True) + "\n"
        )
        Path(a.markdown_output).write_text(markdown(report))
    except (ValueError, TypeError, KeyError, OSError, sqlite3.Error) as e:
        print(e, file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
