import json
from pathlib import Path
import re
import shutil
import tempfile
import unittest
import zipfile

import uncovr

SKILL = Path(__file__).resolve().parent.parent / uncovr.SKILL_DIR
FIXTURE = SKILL / "examples" / "order-approval"


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
        installed = self.root / uncovr.SKILL_DIR
        self.assertTrue((installed / "SKILL.md").is_file())
        self.assertTrue((installed / "scripts" / "check.py").is_file())
        for stage in ("explorer", "analyst", "validator", "evidence-contract"):
            self.assertTrue((installed / "references" / f"{stage}.md").is_file())
        for skipped in uncovr.INSTALL_SKIP:
            self.assertFalse((installed / skipped).exists())
        self.assertTrue((self.root / ".github/agents/uncovr.agent.md").is_file())
        self.assertTrue((self.root / ".github/agents/uncovr-validator.agent.md").is_file())

    def test_install_writes_manifest_with_hashes(self):
        manifest = json.loads((self.root / uncovr.MANIFEST).read_text(encoding="utf-8"))
        self.assertEqual(manifest["version"], uncovr.VERSION)
        for path in (f"{uncovr.SKILL_DIR}/SKILL.md", f"{uncovr.SKILL_DIR}/scripts/check.py",
                     ".github/agents/uncovr-validator.agent.md"):
            self.assertEqual(len(manifest["files"][path]), 64)
        self.assertEqual(uncovr.install_drift(self.root), [])

    def test_drift_reports_local_modification(self):
        relative = f"{uncovr.SKILL_DIR}/references/analyst.md"
        skill = self.root / relative
        skill.write_text(skill.read_text(encoding="utf-8") + "\nLocal note.\n", encoding="utf-8")
        drift = uncovr.install_drift(self.root)
        self.assertIn(f"{relative}: modified locally", drift)

    def test_drift_without_manifest_is_reported(self):
        (self.root / uncovr.MANIFEST).unlink()
        self.assertTrue(any("no .uncovr/manifest.json" in n for n in uncovr.install_drift(self.root)))

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


class StageCaseTests(unittest.TestCase):
    """The reference case of each AI stage: its expected baseline must hold structurally."""

    def test_expected_baseline_meets_stage_cases(self):
        cases = json.loads((FIXTURE / "cases.json").read_text(encoding="utf-8"))
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            shutil.copytree(FIXTURE / cases["fixture"], root, dirs_exist_ok=True)
            shutil.copytree(FIXTURE / cases["expected"], root / "product-context")
            errors, _, _ = uncovr.validate(root)
            self.assertEqual(errors, [])
            claims = {c["id"]: c for c in uncovr.load_claims(root)[0]}
            text = lambda name: (root / "product-context" / name).read_text(encoding="utf-8")
            for case in cases["stages"]:
                for claim_id, expected in case["claims"].items():
                    with self.subTest(stage=case["stage"], claim=claim_id):
                        self.assertEqual(claims[claim_id]["confidence"], expected["confidence"])
                        self.assertIn(claim_id, text(expected["in"]))
                for claim_id in case.get("questions", []):
                    self.assertIn(claim_id, text("validation.md").split("## Outstanding questions")[1])
            self.assertFalse([c for c in claims.values() if c["business_validation"] == "approved"])


class MarketplacePackageTests(unittest.TestCase):
    """The skill folder as the marketplace receives it: one ZIP, one top folder, text only."""

    def test_skill_folder_has_no_packaging_problems(self):
        self.assertEqual(uncovr.pack_problems(SKILL), [])

    def test_skill_md_frontmatter_has_name_and_trigger_description(self):
        text = (SKILL / "SKILL.md").read_text(encoding="utf-8")
        frontmatter = text.split("---")[1]
        self.assertRegex(frontmatter, r"(?m)^name: uncovr$")
        description = re.search(r"(?m)^description: (.+)$", frontmatter).group(1)
        self.assertIn("Use when", description)
        self.assertIn("Do not use", description)
        self.assertLessEqual(len(description), 1024)

    def test_skill_references_resolve_inside_the_skill(self):
        text = (SKILL / "SKILL.md").read_text(encoding="utf-8")
        for path in re.findall(r"`((?:references|assets|scripts|examples)/[^`]+)`", text):
            self.assertTrue((SKILL / path.rstrip("/")).exists(), path)
        self.assertNotIn(".uncovr/uncovr.py", text)
        self.assertNotIn(".github/", text)

    def test_evals_have_trigger_prompts_and_a_quality_case(self):
        evals = json.loads((SKILL / "evals" / "evals.json").read_text(encoding="utf-8"))
        self.assertGreaterEqual(len(evals["should_trigger"]), 5)
        self.assertGreaterEqual(len(evals["should_not_trigger"]), 3)
        self.assertTrue((SKILL / evals["quality"]["case"]).is_file())

    def test_pack_writes_one_top_folder_with_skill_md(self):
        with tempfile.TemporaryDirectory() as tmp, tempfile.TemporaryDirectory() as again:
            self.assertEqual(uncovr.pack(Path(tmp)), 0)
            with zipfile.ZipFile(Path(tmp) / "uncovr.zip") as archive:
                names = archive.namelist()
            self.assertIn("uncovr/SKILL.md", names)
            self.assertEqual({name.split("/")[0] for name in names}, {"uncovr"})
            self.assertFalse([n for n in names if "/." in n or "__pycache__" in n])
            uncovr.pack(Path(again))
            self.assertEqual((Path(tmp) / "uncovr.zip").read_bytes(), (Path(again) / "uncovr.zip").read_bytes())


if __name__ == "__main__":
    unittest.main()
