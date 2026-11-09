import json
from pathlib import Path
import tempfile
import unittest

import uncovr


class UncovrTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.assertEqual(uncovr.install(self.root), 0)

    def write_claim(self, record):
        (self.root / "product-context" / "evidence.jsonl").write_text(
            json.dumps(record) + "\n", encoding="utf-8"
        )

    def sample(self):
        return {
            "id": "BR-001", "kind": "business_rule",
            "summary": "A pending request can be approved.",
            "confidence": "confirmed", "business_validation": "pending",
            "evidence": [{
                "type": "code", "ref": "src/orders.py",
                "line_start": 1, "line_end": 2,
                "revision": "1234567abc"
            }]
        }

    def test_install_creates_six_artifacts_and_skills(self):
        for name in uncovr.ARTIFACTS:
            self.assertTrue((self.root / "product-context" / name).is_file())
        for skill in ("orchestrator", "explorer", "analyst", "validator"):
            self.assertTrue(
                (self.root / ".github/skills" / f"uncovr-{skill}" / "SKILL.md").is_file()
            )
        self.assertTrue((self.root / ".github/agents/uncovr.agent.md").is_file())

    def test_install_does_not_overwrite_user_changes(self):
        path = self.root / "product-context" / "overview.md"
        path.write_text("User-written content\n", encoding="utf-8")
        self.assertEqual(uncovr.install(self.root), 0)
        self.assertEqual(path.read_text(encoding="utf-8"), "User-written content\n")

    def test_valid_evidence_passes(self):
        source = self.root / "src/orders.py"
        source.parent.mkdir()
        source.write_text("def approve():\n    return True\n", encoding="utf-8")
        self.write_claim(self.sample())
        errors, warnings, counts = uncovr.validate(self.root)
        self.assertEqual(errors, [])
        self.assertEqual(counts["confirmed"], 1)

    def test_missing_source_fails(self):
        self.write_claim(self.sample())
        errors, _, _ = uncovr.validate(self.root)
        self.assertTrue(any("missing local source" in e for e in errors))

    def test_path_escape_fails(self):
        record = self.sample()
        record["evidence"][0]["ref"] = "../outside.py"
        self.write_claim(record)
        errors, _, _ = uncovr.validate(self.root)
        self.assertTrue(any("escapes repository" in e for e in errors))

    def test_approved_claim_requires_human_provenance(self):
        record = self.sample()
        record["confidence"] = "gap"
        record["business_validation"] = "approved"
        record["evidence"] = []
        self.write_claim(record)
        errors, _, _ = uncovr.validate(self.root)
        self.assertTrue(any("validated_by and validated_on" in e for e in errors))

    def test_confirmed_requires_technical_evidence(self):
        record = self.sample()
        record["evidence"] = [{"type": "interview", "ref": "Interview, Nov 2026"}]
        self.write_claim(record)
        errors, _, _ = uncovr.validate(self.root)
        self.assertTrue(any("lacks technical evidence" in e for e in errors))

    def test_duplicate_ids_rejected(self):
        record = self.sample()
        source = self.root / "src/orders.py"
        source.parent.mkdir()
        source.write_text("line 1\nline 2\n", encoding="utf-8")
        path = self.root / "product-context/evidence.jsonl"
        path.write_text(json.dumps(record) + "\n" + json.dumps(record) + "\n",
                        encoding="utf-8")
        errors, _, _ = uncovr.validate(self.root)
        self.assertTrue(any("duplicate claim id" in e for e in errors))


    def test_invalid_jsonl_rejected(self):
        (self.root / "product-context/evidence.jsonl").write_text(
            "not valid json\n", encoding="utf-8"
        )
        errors, _, _ = uncovr.validate(self.root)
        self.assertTrue(any("evidence.jsonl:1" in e for e in errors))

    def test_invalid_line_range_rejected(self):
        source = self.root / "src/orders.py"
        source.parent.mkdir()
        source.write_text("line 1\n", encoding="utf-8")
        record = self.sample()
        record["evidence"][0]["line_end"] = 99
        self.write_claim(record)
        errors, _, _ = uncovr.validate(self.root)
        self.assertTrue(any("line range exceeds" in e for e in errors))

    def test_unreferenced_claim_is_warning(self):
        source = self.root / "src/orders.py"
        source.parent.mkdir()
        source.write_text("line 1\nline 2\n", encoding="utf-8")
        self.write_claim(self.sample())
        errors, warnings, _ = uncovr.validate(self.root)
        self.assertFalse(errors)
        self.assertTrue(any("not referenced" in w for w in warnings))

    def test_scaffold_is_not_certified_complete(self):
        errors, warnings, counts = uncovr.validate(self.root)
        self.assertFalse(errors)
        self.assertTrue(warnings)
        self.assertEqual(sum(counts.values()), 0)


if __name__ == "__main__":
    unittest.main()
