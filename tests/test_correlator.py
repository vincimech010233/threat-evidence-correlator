import unittest
import sys
import json
import copy
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from correlator import connect, correlate, ingest, instant, load, validate, markdown


def fixture():
    return json.loads(Path("examples/intelligence.json").read_text())


class CorrelationTests(unittest.TestCase):
    def test_fixture(self):
        r = correlate(fixture()["records"])
        self.assertEqual(r["groups"][0]["assessment"], "DISPUTED")
        self.assertEqual(
            r["groups"][0]["independent_lineage_groups"], [["e1", "e2"], ["e3"]]
        )
        self.assertEqual(r["groups"][1]["assessment"], "MULTIPLE_DECLARED_LINEAGES")
        self.assertTrue(
            any(q["assessment"] == "QUALIFIED_MATCH_REVIEW" for q in r["review_queue"])
        )

    def test_intermediate_ancestry(self):
        rows = fixture()["records"]
        root = copy.deepcopy(rows[0])
        mid = copy.deepcopy(rows[1])
        child = copy.deepcopy(rows[2])
        other = copy.deepcopy(rows[3])
        mid["source_group"] = "shared"
        child["derived_from"] = ["e2"]
        child["value"] = "new"
        other["entity"] = child["entity"]
        other["value"] = "new"
        other["source_group"] = "shared"
        root["predicate"] = "root-predicate"
        mid["predicate"] = "parent-predicate"
        r = correlate([root, mid, child, other])
        g = next(g for g in r["groups"] if g["predicate"] == "synthetic-feature")
        self.assertEqual(g["assessment"], "SINGLE_LINEAGE")

    def test_date_without_time_rejects(self):
        with self.assertRaises(ValueError):
            instant("2026-01-01Z")

    def test_nonoverlap(self):
        rows = fixture()["records"][:3]
        rows[2]["valid_from"] = "2026-01-02T00:00:00Z"
        rows[2]["valid_to"] = "2026-01-03T00:00:00Z"
        self.assertEqual(correlate(rows)["groups"][0]["contradictions"], [])

    def test_lineage_cycle_missing(self):
        for parent in ["e2", "missing"]:
            rows = fixture()["records"]
            rows[0]["derived_from"] = [parent]
            with self.assertRaises(ValueError):
                validate(rows)

    def test_unknown_not_independent(self):
        rows = fixture()["records"][4:]
        [r.update(source_group=None) for r in rows]
        self.assertEqual(correlate(rows)["groups"][0]["assessment"], "SINGLE_LINEAGE")

    def test_allegations(self):
        rows = fixture()["records"][4:]
        [r.update(claim_kind="allegation") for r in rows]
        self.assertEqual(correlate(rows)["groups"][0]["assessment"], "ALLEGATION_ONLY")

    def test_transaction_idempotence_and_conflict(self):
        db = connect(":memory:")
        b = fixture()
        self.assertEqual(ingest(db, b), 6)
        self.assertEqual(ingest(db, b), 6)
        b["records"][0]["value"] = "changed"
        with self.assertRaises(ValueError):
            ingest(db, b)
        self.assertEqual(load(db)[0]["value"], "present")
        self.assertEqual(len(load(db)), 6)

    def test_invalid_and_verification(self):
        for mutate in [
            lambda r: r.update(recorded_at="bad"),
            lambda r: r.update(claim_kind="verified_fact"),
            lambda r: r["entity"].update(kind="person"),
        ]:
            rows = fixture()["records"]
            mutate(rows[0])
            with self.assertRaises(ValueError):
                validate(rows)

    def test_determinism_and_escape(self):
        rows = fixture()["records"]
        self.assertEqual(correlate(rows), correlate(list(reversed(rows))))
        rows[0]["predicate"] = "<script>"
        self.assertNotIn("<script>", markdown(correlate(rows)))


if __name__ == "__main__":
    unittest.main()
