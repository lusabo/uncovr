import importlib.util
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
import zipfile

import uncovr

SKILL = Path(__file__).resolve().parent.parent / uncovr.SKILL_DIR
FIXTURE = SKILL / "examples" / "order-approval"


def load_script(name):
    spec = importlib.util.spec_from_file_location(name, SKILL / "scripts" / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


history = load_script("history")
okf = load_script("okf")


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
        for skipped in uncovr.NOT_SHIPPED:
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

    def test_markdown_citing_a_missing_claim_is_warning(self):
        source = self.root / "src/orders.py"
        source.parent.mkdir()
        source.write_text("line 1\nline 2\n", encoding="utf-8")
        self.write_claim(self.sample())
        (self.root / "product-context/domain.md").write_text(
            "BR-001 and BR-009 apply; see ISO-8601.\n", encoding="utf-8")
        errors, warnings, _ = uncovr.validate(self.root)
        self.assertFalse(errors)
        self.assertIn("domain.md cites BR-009, which is not in evidence.jsonl", warnings)
        self.assertFalse([w for w in warnings if "ISO-8601" in w or "cites BR-001" in w])

    def test_architecture_rows_must_cite_a_claim(self):
        architecture = self.root / "product-context/architecture.md"
        scaffold = architecture.read_text(encoding="utf-8")
        _, warnings, _ = uncovr.validate(self.root)
        self.assertFalse([w for w in warnings if "cites no claim ID" in w])
        architecture.write_text(
            scaffold.split("<!--")[0]
            + "## Technology stack\n| Technology | Role | Constraint | Claim ID |\n| --- | --- | --- | --- |\n"
              "| PostgreSQL | Orders store | Version not declared | ARCH-001 |\n| Redis | Cache | None | |\n"
              "## Context and major components\n| Component | Responsibility | Boundary | External | Claim ID |\n"
              "| --- | --- | --- | --- | --- |\n| Billing | Invoices | API | Stripe | |\n"
              "## Deployment and environments\n| Unit | Where |\n| --- | --- |\n| web | unknown |\n",
            encoding="utf-8")
        _, warnings, _ = uncovr.validate(self.root)
        rows = sorted(w for w in warnings if "cites no claim ID" in w)
        self.assertEqual(rows, [
            "architecture.md: row 'Billing' in Context and major components cites no claim ID",
            "architecture.md: row 'Redis' in Technology stack cites no claim ID",
        ])


    def test_not_applicable_is_warning_for_business_claims_and_gaps(self):
        source = self.root / "src/orders.py"
        source.parent.mkdir()
        source.write_text("line 1\nline 2\n", encoding="utf-8")
        rule = dict(self.sample(), business_validation="not_applicable")
        gap = {"id": "ARCH-002", "kind": "architecture", "summary": "Runtime unknown.",
               "confidence": "gap", "business_validation": "not_applicable", "evidence": []}
        layout = dict(self.sample(), id="ARCH-001", kind="architecture",
                      business_validation="not_applicable")
        (self.root / "product-context/evidence.jsonl").write_text(
            "".join(json.dumps(r) + "\n" for r in (rule, gap, layout)), encoding="utf-8")
        errors, warnings, _ = uncovr.validate(self.root)
        self.assertFalse(errors)
        flagged = sorted(w.split(": ")[1].split(" ")[0] for w in warnings if "is not_applicable" in w)
        self.assertEqual(flagged, ["ARCH-002", "BR-001"])

    def test_declared_intent_keeps_confidence_and_approval_independent(self):
        record = {
            "id": "CTX-001", "kind": "assumption",
            "summary": "Synthetic case: the product is declared to serve internal buyers.",
            "confidence": "inferred", "business_validation": "approved",
            "validated_by": "Synthetic PO (test fixture)", "validated_on": "2026-01-01",
            "evidence": [{"type": "interview", "ref": "Synthetic interview (test fixture)"}],
        }
        self.write_claim(record)
        errors, warnings, _ = uncovr.validate(self.root)
        self.assertEqual(errors, [])
        self.assertFalse([w for w in warnings if "is not_applicable" in w])
        record["confidence"] = "confirmed"
        self.write_claim(record)
        errors, _, _ = uncovr.validate(self.root)
        self.assertTrue(any("lacks technical evidence" in e for e in errors))

    # Traceability and validation views. Identities are synthetic test fixtures.
    DECISION = {"id": "DEC-001", "kind": "decision", "summary": "Synthetic case: the limit is 5000.",
                "confidence": "inferred", "business_validation": "approved",
                "validated_by": "Synthetic PO (test fixture)", "validated_on": "2026-01-01",
                "evidence": [{"type": "interview", "ref": "Synthetic interview (test fixture), 2026-01-01"}]}

    def views(self, records, trace="", sources="", questions="", decisions="None recorded.",
              contradictions=""):
        source = self.root / "src/orders.py"
        source.parent.mkdir(exist_ok=True)
        source.write_text("line 1\nline 2\n", encoding="utf-8")
        context = self.root / "product-context"
        (context / "evidence.jsonl").write_text(
            "".join(json.dumps(r) + "\n" for r in records), encoding="utf-8")
        header = "| Claim ID | Feature or rule | Source files | Tests | Related claims | Impact note |\n| --- | --- | --- | --- | --- | --- |\n"
        source_header = "| Source | Purpose | Scope consulted | Version or date | Status | Claim IDs |\n| --- | --- | --- | --- | --- | --- |\n"
        (context / "traceability.md").write_text(
            f"# Traceability\n\n{header}{trace}\n## Sources\n{source_header if sources else ''}{sources}\n",
            encoding="utf-8")
        decision_header = "| Decision claim | Covers | Outcome | Status | Reopening reason |\n| --- | --- | --- | --- | --- |\n"
        (context / "validation.md").write_text(
            f"# Validation\n\n## Outstanding questions\n{questions}\n"
            f"## Decisions\n{decision_header if '|' in decisions else ''}{decisions}\n"
            f"## Contradictions and review outcomes\n{contradictions}\n", encoding="utf-8")
        errors, warnings, _ = uncovr.validate(self.root)
        return errors, [w for w in warnings if w.startswith(("traceability.md", "validation.md"))]

    def test_sources_view_without_external_sources_or_with_an_inaccessible_one(self):
        rule = self.sample()
        self.assertEqual(self.views([rule], trace="| BR-001 | Approve | `src/orders.py` | none | — | — |\n"),
                         ([], []))
        gap = {"id": "CTX-001", "kind": "assumption", "confidence": "gap", "business_validation": "pending",
               "summary": "Synthetic case: the linked policy could not be opened.",
               "evidence": [{"type": "document", "ref": "README.md (Policy link)"}]}
        row = "| Policy wiki | Declared limit | Not opened | Unknown | inaccessible | CTX-001 |\n"
        self.assertEqual(self.views([rule, gap], sources=row), ([], []))
        cited = dict(gap, evidence=[{"type": "document", "ref": "Policy wiki (section 2)"}])
        bad = row + "| Ticket 12 | Request | Unknown | Unknown | maybe | none |\n"
        _, warnings = self.views([rule, cited], sources=bad)
        self.assertEqual(warnings, [
            "traceability.md: source 'Policy wiki' is inaccessible but cited as evidence in evidence.jsonl",
            "traceability.md: source 'Ticket 12' needs status consulted, indicated or inaccessible",
            "traceability.md: source 'Ticket 12' cites no claim ID",
        ])

    def test_traceability_names_only_files_the_evidence_cites(self):
        _, warnings = self.views([self.sample()],
                                 trace="| BR-001 | Approve | `src/billing.py` | `tests/` | — | — |\n")
        self.assertEqual(warnings, [
            "traceability.md: BR-001 names src/billing.py, which its evidence in evidence.jsonl does not cite",
            "traceability.md: BR-001 names tests/, which its evidence in evidence.jsonl does not cite",
        ])

    def test_unresolved_contradiction_must_be_listed(self):
        conflict = dict(self.sample(), confidence="contradicted")
        _, warnings = self.views([conflict])
        self.assertEqual(warnings, ["validation.md: contradicted BR-001 is not listed "
                                    "under Contradictions and review outcomes"])
        row = ("| Divergence | Claims involved | Source positions | Impact | Decision or status |\n"
               "| --- | --- | --- | --- | --- |\n| Limit | BR-001 | Code: 5000. README: 10 000. | High | pending |\n")
        self.assertEqual(self.views([conflict], contradictions=row), ([], []))

    def test_decision_row_needs_a_recorded_human_decision(self):
        row = "| DEC-001 | BR-001 | Limit is 5000 | in force | — |\n"
        self.assertEqual(self.views([self.sample(), self.DECISION], decisions=row), ([], []))
        pending = dict(self.DECISION, business_validation="pending")
        del pending["validated_by"], pending["validated_on"]
        _, warnings = self.views([self.sample(), pending], decisions=row)
        self.assertEqual(len(warnings), 1)
        self.assertIn("DEC-001 is listed as a decision but evidence.jsonl records no human decision", warnings[0])

    def test_reopening_requires_new_evidence_and_a_new_question(self):
        newer = dict(self.sample(), id="BR-002", summary="Synthetic case: the limit changed at a newer revision.",
                     evidence=[dict(self.sample()["evidence"][0], revision="89abcdef0")])
        claims = [self.sample(), self.DECISION, newer]
        reopened = "| DEC-001 | BR-001 | Limit is 5000 | reopened | BR-002: limit changed in code |\n"
        question = "| DEC-001, BR-002 | Does the decision still hold? | High | PO/SME | Open |\n"
        self.assertEqual(self.views(claims, decisions=reopened, questions=question), ([], []))
        _, warnings = self.views(claims, decisions="| DEC-001 | BR-001 | Limit is 5000 | reopened | changed mind |\n")
        self.assertEqual(warnings, [
            "validation.md: reopened DEC-001 needs the claim ID of the new evidence as its reason",
            "validation.md: reopened DEC-001 is not asked again under Outstanding questions",
        ])

    def test_supersedes_must_name_other_existing_claims(self):
        newer = dict(self.DECISION, id="DEC-002", supersedes=["DEC-001"])
        rows = "| DEC-001 | BR-001 | Limit is 5000 | superseded by DEC-002 | — |\n"
        self.assertEqual(self.views([self.sample(), self.DECISION, newer], decisions=rows), ([], []))
        for value, message in ((["DEC-009"], "supersedes unknown DEC-009"),
                               (["DEC-002"], "must be an array of other claim IDs"),
                               ("DEC-001", "must be an array of other claim IDs")):
            with self.subTest(supersedes=value):
                errors, _ = self.views([self.sample(), self.DECISION, dict(newer, supersedes=value)])
                self.assertTrue(any(message in e for e in errors), errors)
        _, warnings = self.views([self.sample(), self.DECISION, dict(newer, supersedes=[])], decisions=rows)
        self.assertEqual(warnings, ["validation.md: DEC-002 does not list DEC-001 in supersedes"])

    def diagram_warnings(self, features):
        source = self.root / "src/orders.py"
        source.parent.mkdir(exist_ok=True)
        source.write_text("line 1\nline 2\n", encoding="utf-8")
        inferred = dict(self.sample(), id="BR-002", confidence="inferred",
                        summary="Synthetic case: approval probably notifies billing.")
        (self.root / "product-context/evidence.jsonl").write_text(
            "".join(json.dumps(r) + "\n" for r in (self.sample(), inferred)), encoding="utf-8")
        (self.root / "product-context/features.md").write_text(features, encoding="utf-8")
        errors, warnings, _ = uncovr.validate(self.root)
        self.assertEqual(errors, [])
        return [w for w in warnings if "Mermaid block" in w]

    def test_baseline_without_diagrams_has_no_diagram_warnings(self):
        self.assertEqual(self.diagram_warnings("# Features\n\nApproval is one step (BR-001); no diagram.\n"), [])

    def test_mermaid_blocks_cite_claims_and_name_their_confidence(self):
        good = ("# Features\n\nApproval, confirmed (BR-001); billing is inferred (BR-002).\n\n"
                "```mermaid\nflowchart LR\n  A[Approve] --> B[Approved]\n  B -.->|inferred| C[Billing]\n```\n")
        self.assertEqual(self.diagram_warnings(good), [])
        bad = ("# Features\n\nApproval and billing (BR-001, BR-002).\n\n"
               "```mermaid\nflowchart LR\n  A --> C\n  style A fill:#f00\n```\n\n"
               "No claim here.\n\n```mermaid\npie title Approvals\n  \"yes\" : 3\n```\n\n"
               "```mermaid\nflowchart LR\n  A --> B\n")
        self.assertEqual(self.diagram_warnings(bad), [
            "features.md: Mermaid block at line 5 uses themes, styles or click handlers",
            "features.md: Mermaid block at line 5 draws BR-002 without saying it is inferred",
            "features.md: Mermaid block at line 13 is a 'pie' diagram; use flowchart, sequenceDiagram, "
            "stateDiagram-v2 or erDiagram, and no charts of quantities",
            "features.md: Mermaid block at line 13 cites no claim ID in it or in the sentence before it",
            "features.md: Mermaid block at line 18 is not closed",
        ])


class StageCaseTests(unittest.TestCase):
    """Reference baselines and stage instruction contracts, not live agent behavior."""

    def test_expected_baseline_meets_stage_cases(self):
        cases = json.loads((FIXTURE / "cases.json").read_text(encoding="utf-8"))
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            shutil.copytree(FIXTURE / cases["fixture"], root, dirs_exist_ok=True)
            shutil.copytree(FIXTURE / cases["expected"], root / "product-context")
            errors, warnings, _ = uncovr.validate(root)
            self.assertEqual(errors, [])
            self.assertFalse([w for w in warnings if "pin a Git revision" not in w], warnings)
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

    def test_expected_baseline_has_every_template_section(self):
        templates = SKILL / "assets" / "product-context"
        for name in uncovr.ARTIFACTS:
            headings = re.findall(r"(?m)^## .+$", (templates / name).read_text(encoding="utf-8"))
            expected = (FIXTURE / "expected" / name).read_text(encoding="utf-8")
            for heading in headings:
                with self.subTest(file=name, heading=heading):
                    self.assertRegex(expected, rf"(?m)^{re.escape(heading)}$")

    def test_signals_reference_points_to_template_sections(self):
        signals = (SKILL / "references" / "repository-signals.md").read_text(encoding="utf-8")
        templates = SKILL / "assets" / "product-context"
        for name, section in re.findall(r"`(\w+\.md)` → \*([^*]+)\*", signals):
            with self.subTest(file=name, section=section):
                self.assertRegex((templates / name).read_text(encoding="utf-8"),
                                 rf"(?m)^## {re.escape(section)}$")

    def test_architecture_guidance_separates_inspected_configured_and_production(self):
        texts = {name: (SKILL / "references" / f"{name}.md").read_text(encoding="utf-8")
                 for name in ("explorer", "validator", "evidence-contract", "repository-signals")}
        template = (SKILL / "assets" / "product-context" / "architecture.md").read_text(encoding="utf-8")
        required = {
            "explorer": ("*Inspection boundary*", "Do not list every library", "cites a claim ID",
                         "A checkout does not prove the version in production"),
            "validator": ("configuration found, execution observed and production apart",
                          "a checkout does not prove the version in production"),
            "evidence-contract": ("**Configuration found**", "**Execution observed**",
                                  "**Production not confirmed**", "**External systems**",
                                  "only with a source that states the limit"),
            "repository-signals": ("configuration found, execution observed, production not confirmed",
                                   "never every library", "A checkout is not production"),
        }
        for name, phrases in required.items():
            for phrase in phrases:
                with self.subTest(file=name, phrase=phrase):
                    self.assertIn(phrase, texts[name])
        for heading in ("Inspection boundary", "Technology stack", "Context and major components",
                        "Deployment and environments"):
            with self.subTest(heading=heading):
                self.assertRegex(template, rf"(?m)^## {heading}$")
        self.assertIn("| Technology | Role in the system | Relevant constraint | Claim ID |", template)
        for label in ("Configuration found", "Execution observed", "Production not confirmed"):
            with self.subTest(label=label):
                self.assertIn(f"- {label}:", template)

    def test_analyst_semantic_guardrails(self):
        analyst = (SKILL / "references" / "analyst.md").read_text(encoding="utf-8")
        required = {
            "ui_evidence": ("UI path", "outside the confirmed scope", "unreviewed"),
            "bounded_claims": ("universal and absence claims", "direct state updates",
                               "inspected paths", "not proof of downstream delivery"),
            "atomic_decisions": ("independent business decisions", "old-to-new ID mapping",
                                 "undecided business rules remain `pending`"),
            "source_conflicts": ("same trigger, actor, state, configuration and revision",
                                 "separate `contradicted` claim", "both sources"),
            "question_premises": ("Do not phrase an `inferred` or `gap` premise as a fact",),
        }
        for guardrail, phrases in required.items():
            with self.subTest(guardrail=guardrail):
                for phrase in phrases:
                    self.assertIn(phrase, analyst)

    def test_validator_semantic_guardrails(self):
        validator = (SKILL / "references" / "validator.md").read_text(encoding="utf-8")
        required = (
            "UI claims require the client path, templates and activation conditions",
            "An excluded interface is unreviewed",
            "falsify universal and absence claims",
            "event emission from downstream delivery",
            "partial decision has not spread approval or rejection",
            "Reconcile conflicts in prose with the canonical evidence index",
            "keep review verdict counts separate",
        )
        for phrase in required:
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, validator)

    def test_scoped_decision_semantic_guardrails(self):
        skill = (SKILL / "SKILL.md").read_text(encoding="utf-8")
        contract = (SKILL / "references" / "evidence-contract.md").read_text(encoding="utf-8")
        self.assertIn("before recording a partial approval or rejection", skill)
        self.assertIn("do not present `inferred` or `gap` premises as facts", skill)
        required = (
            "old-to-new ID mapping", "allocate unused IDs", "preserving the prior decision history",
            "`business_validation`, `validated_by` and `validated_on` only to assertions explicitly covered",
            "Undecided business rules remain `pending`",
            "same trigger, actor, state, configuration and revision",
            "separate `contradicted` claim citing both sources",
            "A human choice settles desired behavior, not technical agreement",
        )
        for phrase in required:
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, contract)

    def test_example_separates_declared_intent_unknowns_and_conflicts(self):
        expected = FIXTURE / "expected"
        claims = {c["id"]: c for c in map(json.loads, (expected / "evidence.jsonl")
                  .read_text(encoding="utf-8").splitlines()) if c}
        declared, unknown, conflict = claims["CTX-001"], claims["CTX-002"], claims["BR-002"]
        self.assertEqual((declared["kind"], declared["confidence"], declared["business_validation"]),
                         ("assumption", "inferred", "pending"))
        self.assertEqual({e["type"] for e in declared["evidence"]}, {"document"})
        self.assertEqual((unknown["confidence"], unknown["business_validation"], unknown["evidence"]),
                         ("gap", "pending", []))
        self.assertEqual(conflict["confidence"], "contradicted")
        self.assertTrue({"code", "document"} <= {e["type"] for e in conflict["evidence"]})
        for claim in claims.values():
            with self.subTest(claim=claim["id"]):
                self.assertNotEqual(claim["business_validation"], "approved")
                if claim["kind"] in ("feature", "business_rule", "assumption") or claim["confidence"] == "gap":
                    self.assertNotEqual(claim["business_validation"], "not_applicable")
        overview = (expected / "overview.md").read_text(encoding="utf-8")
        section = lambda name: overview.split(f"## {name}\n")[1].split("\n## ")[0]
        self.assertEqual(set(re.findall(r"\b[A-Z]+-\d{3}\b", section("Product capabilities"))),
                         {"F-001", "F-002", "F-003"})
        self.assertIn("CTX-001", section("Purpose and users"))
        self.assertIn("CTX-002", section("Business objectives and unknowns"))
        self.assertNotRegex(section("Who can clarify"), r"@\w")
        self.assertIn("the Product Owner designates", section("Who can clarify"))
        glossary = (expected / "domain.md").read_text(encoding="utf-8").split("## Glossary\n")[1].split("\n## ")[0]
        for claim_id in ("CTX-003", "BR-002"):
            self.assertIn(claim_id, glossary)

    def test_overview_and_domain_guidance_separates_observed_declared_and_unknown(self):
        files = {
            "overview": SKILL / "assets/product-context/overview.md",
            "domain": SKILL / "assets/product-context/domain.md",
            "evidence-contract": SKILL / "references/evidence-contract.md",
            "analyst": SKILL / "references/analyst.md",
            "validator": SKILL / "references/validator.md",
            "repository-signals": SKILL / "references/repository-signals.md",
            "SKILL": SKILL / "SKILL.md",
        }
        required = {
            "overview": ("A capability is not a purpose, a value or a plan", "Declared only", "Observed only",
                         "is not a roadmap item", "CODEOWNERS declares who reviews paths, not who holds business authority"),
            "domain": ("| Term | Meaning observed in code | Business definition | Ambiguity | Claim IDs |",
                       "Never copy the observed meaning here"),
            "evidence-contract": ("## Declared intent, definitions and people", "Behavior is not intent",
                                  "an approved definition stays `inferred`", "missing intent is `gap` and `pending`",
                                  "not evidence of business authority, knowledge or approval"),
            "analyst": ("Don't turn existing behavior into business intent or a roadmap",
                        "Use `not_applicable` only with a reason"),
            "validator": ("that `not_applicable` has a reason",
                          "The Product Owner designates who decides each question"),
            "repository-signals": ("Capabilities are not intent", "never business authority or approval"),
            "SKILL": ("never establish business authority or approval",),
        }
        for name, phrases in required.items():
            text = files[name].read_text(encoding="utf-8")
            for phrase in phrases:
                with self.subTest(file=name, phrase=phrase):
                    self.assertIn(phrase, text)

    def test_example_views_reference_canonical_records(self):
        expected = FIXTURE / "expected"
        trace = (expected / "traceability.md").read_text(encoding="utf-8")
        review = (expected / "validation.md").read_text(encoding="utf-8")
        sources = trace.split("## Sources\n")[1].split("\n## ")[0]
        statuses = re.findall(r"\| (consulted|indicated|inaccessible) \|", sources)
        self.assertEqual(statuses, ["consulted"] * 3)
        self.assertIn("No external source is indicated or consulted", sources)
        section = lambda name: review.split(f"## {name}\n")[1].split("\n## ")[0]
        self.assertIn("None recorded.", section("Decisions"))
        divergence = section("Contradictions and review outcomes")
        self.assertIn("| BR-002 |", divergence)
        self.assertIn("pending", divergence)
        for field in ("validated_by", "validated_on", "Synthetic", "line_start"):
            self.assertNotIn(field, trace + review)

    def test_traceability_and_validation_guidance_keeps_sources_and_decisions_canonical(self):
        files = {
            "traceability": SKILL / "assets/product-context/traceability.md",
            "validation": SKILL / "assets/product-context/validation.md",
            "evidence-contract": SKILL / "references/evidence-contract.md",
            "analyst": SKILL / "references/analyst.md",
            "validator": SKILL / "references/validator.md",
            "repository-signals": SKILL / "references/repository-signals.md",
            "SKILL": SKILL / "SKILL.md",
        }
        required = {
            "traceability": ("| Source | Purpose | Scope consulted | Version or date | Status | Claim IDs |",
                             "only these appear as evidence in `evidence.jsonl`",
                             "A document or ticket records intent or a request, not what the code does"),
            "validation": ("## Decisions", "| Divergence | Claims involved | Source positions | Impact | Decision or status |",
                           "who decided and when stay in evidence.jsonl", "never removed"),
            "evidence-contract": ("## Sources, decisions and reopening", "Consulted sources only",
                                  "Intent is not implementation", "never edit or delete a recorded decision",
                                  "A person changing their mind without new evidence is a new decision",
                                  "`supersedes`"),
            "analyst": ("never cite an unopened source as evidence",),
            "validator": ("must not appear as evidence", "reopen it only for new evidence"),
            "repository-signals": ("| External references |", "never proof of implementation"),
            "SKILL": ("reopen them only on new evidence",),
        }
        for name, phrases in required.items():
            text = files[name].read_text(encoding="utf-8")
            for phrase in phrases:
                with self.subTest(file=name, phrase=phrase):
                    self.assertIn(phrase, text)

    def test_example_draws_one_diagram_where_it_helps(self):
        expected = FIXTURE / "expected"
        blocks = {name: re.findall(r"```mermaid\n(.*?)```", (expected / name).read_text(encoding="utf-8"), re.S)
                  for name in uncovr.ARTIFACTS}
        self.assertEqual({name: len(found) for name, found in blocks.items() if found}, {"features.md": 1})
        diagram = blocks["features.md"][0]
        self.assertTrue(diagram.startswith("flowchart"))
        self.assertIn("BR-002 contradicted", diagram)
        self.assertNotIn("F-003", diagram)

    def test_diagram_guidance_keeps_diagrams_as_views_of_claims(self):
        files = {
            "evidence-contract": SKILL / "references/evidence-contract.md",
            "explorer": SKILL / "references/explorer.md",
            "analyst": SKILL / "references/analyst.md",
            "validator": SKILL / "references/validator.md",
            "architecture": SKILL / "assets/product-context/architecture.md",
            "features": SKILL / "assets/product-context/features.md",
            "domain": SKILL / "assets/product-context/domain.md",
            "traceability": SKILL / "assets/product-context/traceability.md",
        }
        required = {
            "evidence-contract": ("## Diagrams", "never a source of its own", "a document may have none",
                                  "Do not derive cardinality, execution order or transitions from names",
                                  "No charts of quantities", "leave a gap undrawn"),
            "explorer": ("*Diagrams* in `evidence-contract.md`",),
            "analyst": ("*Diagrams* in `evidence-contract.md`",),
            "validator": ("remove a diagram that adds nothing to the text",),
            "architecture": ("`flowchart`",),
            "features": ("`sequenceDiagram` when the order of interactions matters",),
            "domain": ("`stateDiagram-v2`", "`erDiagram` only for verified relationships"),
            "traceability": ("only when clearer than this table",),
        }
        for name, phrases in required.items():
            text = files[name].read_text(encoding="utf-8")
            for phrase in phrases:
                with self.subTest(file=name, phrase=phrase):
                    self.assertIn(phrase, text)

    def test_semantic_regression_evaluations(self):
        dataset = json.loads((SKILL / "evals" / "evals.json").read_text(encoding="utf-8"))
        regressions = dataset["semantic_regressions"]
        self.assertRegex(regressions["revision"], r"^[0-9a-f]{40}$")
        self.assertIn("outside the agent's accessible files", regressions["setup"])
        self.assertIn("Never reuse or modify an existing pilot baseline", regressions["setup"])
        cases = regressions["cases"]
        self.assertEqual(len(cases), 4)
        self.assertEqual({case["id"] for case in cases}, {
            "ui_feedback", "bounded_notifications", "atomic_decisions", "source_conflicts"
        })
        for case in cases:
            with self.subTest(case=case["id"]):
                for field in ("input", "prompt", "source_refs", "pass_when", "fail_when"):
                    self.assertTrue(case[field], field)
                for reference in case["source_refs"]:
                    self.assertFalse(Path(reference).is_absolute())
                    self.assertNotIn("..", Path(reference).parts)
        atomic = next(case for case in cases if case["id"] == "atomic_decisions")
        seed = atomic["seed_claim"]
        self.assertEqual(seed["confidence"], "inferred")
        self.assertEqual(seed["business_validation"], "pending")
        self.assertNotIn("validated_by", seed)
        self.assertNotIn("validated_on", seed)
        for evidence in seed["evidence"]:
            self.assertEqual(evidence["revision"], regressions["revision"])
            self.assertIn(evidence["ref"], atomic["source_refs"])
        self.assertIn("Reject only", atomic["follow_up"])
        self.assertIn("Evaluation PO", atomic["follow_up"])


class HistoryTests(unittest.TestCase):
    """scripts/history.py: measured change per module, without naming anyone."""

    LOG = (
        "\x1eaaa\x1f2026-01-02T10:00:00+00:00\x1fana@example.com\x1ffix: refuse self-approval (PAY-12)\n"
        "4\t1\tsrc/requests.py\n"
        "10\t0\tpackage-lock.json\n"
        "2\t2\tproduct-context/domain.md\n"
        "\x1ebbb\x1f2026-02-03T10:00:00+00:00\x1fbob@example.com\x1ffeat: add rejection #7\n"
        "6\t0\tsrc/requests.py\n"
        "3\t1\tsrc/{old => api}/routes.py\n"
        "-\t-\tdocs/diagram.png\n"
        "1\t0\t.github/skills/uncovr/SKILL.md\n"
    )

    def test_new_path_resolves_renames(self):
        self.assertEqual(history.new_path("src/{old => api}/routes.py"), "src/api/routes.py")
        self.assertEqual(history.new_path("a.py => b.py"), "b.py")
        self.assertEqual(history.new_path("src/x.py"), "src/x.py")

    def test_summary_counts_fixes_tickets_and_authors_per_module(self):
        rows = {row["module"]: row for row in history.summarise(history.parse_log(self.LOG), depth=1)}
        self.assertEqual(set(rows), {"src", "docs"})
        src = rows["src"]
        self.assertEqual((src["commits"], src["fix_commits"], src["churn"], src["authors"]), (2, 1, 15, 2))
        self.assertEqual(src["fix_ratio"], 0.5)
        self.assertEqual(src["tickets"], ["#7", "PAY-12"])
        self.assertEqual(src["last_change"], "2026-02-03")
        self.assertNotIn("ana@example.com", json.dumps(rows))

    def test_depth_splits_modules(self):
        rows = {row["module"] for row in history.summarise(history.parse_log(self.LOG), depth=2)}
        self.assertIn("src/api", rows)

    def test_only_the_root_baseline_is_excluded(self):
        self.assertTrue(history.excluded("product-context/domain.md"))
        self.assertFalse(history.excluded("templates/product-context/domain.md"))
        self.assertTrue(history.excluded("web/node_modules/x/index.js"))

    @unittest.skipUnless(shutil.which("git"), "git not installed")
    def test_reads_a_real_repository_without_writing(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            env = {**os.environ, "GIT_AUTHOR_NAME": "Ana", "GIT_AUTHOR_EMAIL": "ana@example.com",
                   "GIT_COMMITTER_NAME": "Ana", "GIT_COMMITTER_EMAIL": "ana@example.com"}
            run = lambda *args: subprocess.run(["git", "-C", tmp, *args], check=True, env=env,
                                               capture_output=True)
            run("init", "-q")
            (root / "src").mkdir()
            (root / "src" / "app.py").write_text("a = 1\n", encoding="utf-8")
            run("add", ".")
            run("commit", "-q", "-m", "feat: first")
            (root / "src" / "app.py").write_text("a = 2\n", encoding="utf-8")
            run("commit", "-q", "-am", "fix: correct a")
            before = sorted(p.name for p in root.rglob("*") if ".git" not in p.parts)
            report = history.history(root, "10.years", 2)
            self.assertEqual(report["commits"], 2)
            self.assertEqual(report["modules"][0]["module"], "src")
            self.assertEqual(report["modules"][0]["fix_commits"], 1)
            rendered = history.render(report, 20)
            self.assertNotIn("ana@example.com", rendered)
            self.assertNotIn("Ana", rendered)
            self.assertEqual(before, sorted(p.name for p in root.rglob("*") if ".git" not in p.parts))


class OkfExportTests(unittest.TestCase):
    """scripts/okf.py: the baseline as an OKF v0.2 bundle for the wiki the user chose."""

    AT = "2026-11-10T12:00:00Z"

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        shutil.copytree(FIXTURE / "app", self.root, dirs_exist_ok=True)
        shutil.copytree(FIXTURE / "expected", self.root / "product-context")
        self.wiki = self.root / "product-context" / "wiki"

    def export(self, target, **kwargs):
        return okf.export(self.root, target, at=self.AT, **kwargs)

    def test_every_target_produces_a_conformant_bundle(self):
        for target in okf.TARGETS:
            with self.subTest(target=target):
                bundle, _ = self.export(target)
                self.assertEqual(okf.conformance(bundle), [])
                self.assertIn('okf_version: "0.2"', (bundle / "index.md").read_text(encoding="utf-8"))
                for page in ("rules/br-002.md", "features/f-001.md", "architecture/arch-001.md", "domain.md"):
                    self.assertTrue((bundle / page).is_file(), page)

    def test_links_follow_the_target(self):
        self.export("obsidian")
        domain = (self.wiki / "domain.md").read_text(encoding="utf-8")
        self.assertIn("[BR-001](rules/br-001.md)", domain)
        architecture = (self.wiki / "architecture.md").read_text(encoding="utf-8")
        self.assertIn("| [ARCH-003](architecture/arch-003.md) |", architecture)
        self.assertIn("(configured, observed, unconfirmed)", architecture)
        rule = (self.wiki / "rules" / "br-001.md").read_text(encoding="utf-8")
        self.assertIn('aliases: ["BR-001"]', rule)
        self.assertIn("[Domain Model](../domain.md)", rule)
        self.export("knowledge-catalog")
        domain = (self.wiki / "domain.md").read_text(encoding="utf-8")
        self.assertIn("[BR-001](/rules/br-001.md)", domain)
        self.assertNotIn("aliases", (self.wiki / "rules" / "br-001.md").read_text(encoding="utf-8"))

    def test_claim_carries_provenance_trust_and_uncovr_fields(self):
        evidence = self.root / "product-context" / "evidence.jsonl"
        records = [json.loads(line) for line in evidence.read_text(encoding="utf-8").splitlines()]
        for record in records:
            if record["id"] == "BR-001":
                record.update(business_validation="approved", validated_by="Synthetic PO (test fixture)",
                              validated_on="2026-11-10")
        evidence.write_text("\n".join(json.dumps(r) for r in records) + "\n", encoding="utf-8")
        self.export("mkdocs", source_url="https://example.com/repo/{revision}/{path}#L{start}-{end}")
        approved = (self.wiki / "rules" / "br-001.md").read_text(encoding="utf-8")
        self.assertIn('status: "stable"', approved)
        self.assertIn('verified: { by: "human:synthetic-po-test-fixture", at: "2026-11-10T00:00:00Z" }', approved)
        self.assertIn('generated: { by: "uncovr/', approved)
        contradicted = (self.wiki / "rules" / "br-002.md").read_text(encoding="utf-8")
        self.assertIn('status: "draft"', contradicted)
        self.assertIn('confidence: "contradicted"', contradicted)
        self.assertIn("[^s1]: code: src/requests.py", contradicted)
        self.assertTrue(okf.GENERATOR.endswith(uncovr.VERSION))

    def test_mermaid_blocks_are_copied_unchanged(self):
        source = (self.root / "product-context" / "features.md").read_text(encoding="utf-8")
        block = re.search(r"```mermaid\n.*?```\n", source, re.S).group(0)
        for target in okf.TARGETS:
            with self.subTest(target=target):
                self.export(target)
                exported = (self.wiki / "features.md").read_text(encoding="utf-8")
                self.assertIn(block, exported)
                self.assertNotIn("](", block)
                self.assertRegex(exported, r"\(\[F-001\]\(/?features/f-001\.md\), \[F-002\]")

    def test_superseded_decision_is_deprecated_and_linked(self):
        evidence = self.root / "product-context" / "evidence.jsonl"
        base = {"kind": "decision", "confidence": "inferred", "business_validation": "approved",
                "validated_by": "Synthetic PO (test fixture)", "validated_on": "2026-11-10",
                "evidence": [{"type": "interview", "ref": "Synthetic interview (test fixture)"}]}
        first = dict(base, id="DEC-001", summary="Synthetic case: the limit is 5000.")
        second = dict(base, id="DEC-002", summary="Synthetic case: the limit is 8000.", supersedes=["DEC-001"])
        with evidence.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(first) + "\n" + json.dumps(second) + "\n")
        self.export("mkdocs")
        old, new = (self.wiki / "decisions" / "dec-001.md"), (self.wiki / "decisions" / "dec-002.md")
        old_text, new_text = old.read_text(encoding="utf-8"), new.read_text(encoding="utf-8")
        self.assertIn('status: "deprecated"', old_text)
        self.assertIn("Superseded by: [DEC-002](dec-002.md)", old_text)
        self.assertIn('status: "stable"', new_text)
        self.assertIn("Supersedes: [DEC-001](dec-001.md)", new_text)
        self.assertNotIn("the business rejected it", old_text + new_text)

    def test_source_urls_need_a_revision_and_a_template(self):
        claim = {"evidence": [{"type": "code", "ref": "src/a.py", "line_start": 2, "line_end": 4}]}
        template = "https://github.com/o/r/blob/{revision}/{path}#L{start}-L{end}"
        self.assertEqual(okf.source_entries(claim, template, "abc1234")[0]["resource"],
                         "https://github.com/o/r/blob/abc1234/src/a.py#L2-L4")
        self.assertEqual(okf.source_entries(claim, None, None)[0]["resource"], "src/a.py#L2-L4")

    def test_mkdocs_config_only_for_mkdocs_and_never_over_a_foreign_one(self):
        config = self.root / "product-context" / "mkdocs.yml"
        self.export("obsidian")
        self.assertFalse(config.exists())
        self.export("mkdocs")
        self.assertIn("docs_dir: wiki", config.read_text(encoding="utf-8"))
        config.write_text("site_name: mine\n", encoding="utf-8")
        _, notes = self.export("mkdocs")
        self.assertEqual(config.read_text(encoding="utf-8"), "site_name: mine\n")
        self.assertTrue(any("not Uncovr's" in note for note in notes))

    def test_rebuild_keeps_the_log_and_refuses_a_foreign_folder(self):
        self.export("obsidian")
        log = self.wiki / "log.md"
        log.write_text("# Update Log\n\n## 2026-01-01\n* **Update**: earlier export.\n", encoding="utf-8")
        self.export("obsidian")
        text = log.read_text(encoding="utf-8")
        self.assertLess(text.index("## 2026-11-10"), text.index("## 2026-01-01"))
        shutil.rmtree(self.wiki)
        self.wiki.mkdir()
        (self.wiki / "notes.md").write_text("mine\n", encoding="utf-8")
        with self.assertRaises(RuntimeError):
            self.export("obsidian")
        self.assertTrue((self.wiki / "notes.md").is_file())

    def test_sources_outside_the_wiki_are_untouched(self):
        before = {p: p.read_bytes() for p in (self.root / "product-context").glob("*.*")}
        self.export("knowledge-catalog")
        self.assertEqual(before, {p: p.read_bytes() for p in before})

    def test_export_refuses_symlinked_product_context(self):
        context = self.root / "product-context"
        original = self.root / "original-context"
        context.rename(original)
        for target in okf.TARGETS:
            for existing_wiki in (False, True):
                with self.subTest(target=target, existing_wiki=existing_wiki), tempfile.TemporaryDirectory() as tmp:
                    outside = Path(tmp)
                    shutil.copytree(original, outside, dirs_exist_ok=True)
                    if existing_wiki:
                        (outside / "wiki").mkdir()
                        (outside / "wiki" / "index.md").write_text(okf.MARKER + "\n", encoding="utf-8")
                        (outside / "wiki" / "notes.md").write_text("Keep this file.\n", encoding="utf-8")
                    before = {path.relative_to(outside): path.read_bytes()
                              for path in outside.rglob("*") if path.is_file()}
                    context.symlink_to(outside, target_is_directory=True)
                    try:
                        with self.assertRaisesRegex(RuntimeError, r"product-context/.*symlink"):
                            self.export(target)
                        self.assertEqual(before, {path.relative_to(outside): path.read_bytes()
                                                  for path in outside.rglob("*") if path.is_file()})
                        self.assertTrue(context.is_symlink())
                    finally:
                        context.unlink()

    def test_export_refuses_symlinked_mkdocs_config_before_rebuilding(self):
        self.export("obsidian")
        before = {path.relative_to(self.wiki): path.read_bytes()
                  for path in self.wiki.rglob("*") if path.is_file()}
        config = self.root / "product-context" / "mkdocs.yml"
        for existing_target in (False, True):
            with self.subTest(existing_target=existing_target), tempfile.TemporaryDirectory() as tmp:
                outside = Path(tmp) / "mkdocs.yml"
                content = okf.MKDOCS_MARKER + "\nsite_name: keep this\n"
                if existing_target:
                    outside.write_text(content, encoding="utf-8")
                config.symlink_to(outside)
                try:
                    with self.assertRaisesRegex(RuntimeError, r"mkdocs\.yml.*symlink"):
                        self.export("mkdocs")
                    self.assertEqual(outside.exists(), existing_target)
                    if existing_target:
                        self.assertEqual(outside.read_text(encoding="utf-8"), content)
                    self.assertEqual(before, {path.relative_to(self.wiki): path.read_bytes()
                                              for path in self.wiki.rglob("*") if path.is_file()})
                    self.assertTrue(config.is_symlink())
                finally:
                    config.unlink()


class MarketplacePackageTests(unittest.TestCase):
    """The skill folder as the marketplace receives it: one ZIP, one top folder, text only."""

    def _run_packaged_script(self, archive, name, target, *arguments):
        payload = archive.read(f"uncovr/scripts/{name}")
        with tempfile.TemporaryDirectory(prefix="uncovr-script-") as temporary:
            directory = Path(temporary)
            script = directory / "delivered.py"
            script.write_bytes(payload)
            result = subprocess.run(
                [sys.executable, "-B", str(script), str(target), *arguments],
                cwd=directory, capture_output=True, text=True, timeout=30,
                env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"},
            )
            self.assertEqual(script.read_bytes(), payload)
            self.assertEqual(sorted(path.name for path in directory.iterdir()), ["delivered.py"])
        self.assertFalse(directory.exists())
        return result

    def test_packaged_scripts_run_without_installation_and_preserve_baseline(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            target = root / "project with spaces"
            shutil.copytree(FIXTURE / "app", target)
            shutil.copytree(FIXTURE / "expected", target / "product-context")
            before = {path.relative_to(target): path.read_bytes()
                      for path in target.rglob("*") if path.is_file()}
            self.assertEqual(uncovr.pack(root / "package"), 0)
            with zipfile.ZipFile(root / "package" / "uncovr.zip") as archive:
                result = self._run_packaged_script(archive, "check.py", target)
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
                self.assertIn("STRUCTURE VALID", result.stdout)
                for mode in okf.TARGETS:
                    with self.subTest(mode=mode):
                        result = self._run_packaged_script(archive, "okf.py", target, "--target", mode)
                        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
                        self.assertTrue((target / "product-context/wiki/index.md").is_file())
                        self.assertEqual(okf.conformance(target / "product-context/wiki"), [])
            self.assertEqual(before, {relative: (target / relative).read_bytes() for relative in before})
            self.assertFalse((target / ".github").exists())
            self.assertFalse((target / uncovr.MANIFEST).exists())

    @unittest.skipUnless(shutil.which("git"), "git not installed")
    def test_packaged_history_runs_without_installation(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            target = root / "repository with spaces"
            shutil.copytree(FIXTURE / "app", target)
            env = {**os.environ, "GIT_AUTHOR_NAME": "Test Author", "GIT_AUTHOR_EMAIL": "test@example.invalid",
                   "GIT_COMMITTER_NAME": "Test Author", "GIT_COMMITTER_EMAIL": "test@example.invalid"}
            for arguments in (("init", "-q"), ("add", "."), ("-c", "commit.gpgSign=false", "commit", "-q", "-m", "feat: fixture")):
                subprocess.run(["git", "-C", str(target), *arguments], env=env,
                               check=True, capture_output=True, timeout=30)
            before = {path.relative_to(target): path.read_bytes()
                      for path in target.rglob("*") if path.is_file()}
            self.assertEqual(uncovr.pack(root / "package"), 0)
            with zipfile.ZipFile(root / "package" / "uncovr.zip") as archive:
                result = self._run_packaged_script(archive, "history.py", target,
                                                   "--since", "1970-01-01", "--json")
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertEqual(json.loads(result.stdout)["commits"], 1)
            self.assertNotIn("test@example.invalid", result.stdout)
            self.assertEqual(before, {path.relative_to(target): path.read_bytes()
                                      for path in target.rglob("*") if path.is_file()})

    def test_packaged_script_failures_leave_no_temporary_files(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            target = root / "missing repository"
            self.assertEqual(uncovr.pack(root / "package"), 0)
            with zipfile.ZipFile(root / "package" / "uncovr.zip") as archive:
                cases = (
                    ("check.py", (), 2, "Target directory does not exist"),
                    ("history.py", (), 2, "No Git history available"),
                    ("okf.py", ("--target", "obsidian"), 1, "product-context/ not found"),
                )
                for name, arguments, exit_code, message in cases:
                    with self.subTest(script=name):
                        result = self._run_packaged_script(archive, name, target, *arguments)
                        self.assertEqual(result.returncode, exit_code, result.stdout + result.stderr)
                        self.assertIn(message, result.stdout + result.stderr)
            self.assertFalse(target.exists())

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
        self.assertRegex(frontmatter, rf'(?m)^version: "{re.escape(uncovr.VERSION)}"$')
        summary = re.search(r"(?m)^summary: (.+)$", frontmatter).group(1)
        self.assertLessEqual(len(summary), 300)

    def test_skill_references_resolve_inside_the_skill(self):
        text = (SKILL / "SKILL.md").read_text(encoding="utf-8")
        for path in re.findall(r"`((?:references|assets|scripts|examples)/[^`]+)`", text):
            self.assertTrue((SKILL / path.rstrip("/")).exists(), path)
        self.assertNotIn(".uncovr/uncovr.py", text)
        self.assertNotIn(".github/", text)

    def test_skill_defines_local_and_mcp_execution(self):
        text = (SKILL / "SKILL.md").read_text(encoding="utf-8")
        for clause in (
            "### Local installation", "### Agensi (MCP)",
            'get_skill({ slug, file: "<path from the returned index>" })',
            "Do not run the Uncovr installer",
            "unchanged in a private temporary directory outside the repository",
            "Each script must run without sibling files",
            "including after a failed run", "Only persistent write destinations",
        ):
            with self.subTest(clause=clause):
                self.assertIn(clause, text)

    def test_stage_commands_use_the_execution_contract(self):
        for relative in ("SKILL.md", "references/explorer.md", "references/validator.md"):
            with self.subTest(file=relative):
                text = (SKILL / relative).read_text(encoding="utf-8")
                self.assertIn("Execution modes", text)
                self.assertNotRegex(text, r"python3(?: -B)? scripts/")

    def test_marketplace_review_does_not_require_an_installed_agent(self):
        text = (SKILL / "SKILL.md").read_text(encoding="utf-8")
        for clause in ("native subagent capability", "not required in Agensi", "use a generic worker",
                       "Do not create or install an agent definition", "review was not independent"):
            with self.subTest(clause=clause):
                self.assertIn(clause, text)

    def test_buyer_readme_explains_delivery_and_validation_limits(self):
        text = (SKILL / "README.md").read_text(encoding="utf-8")
        for clause in ("## Use through Agensi", "no local installation", "Python 3.10+",
                       "## Compatibility and validation", "end-to-end agent evaluations"):
            with self.subTest(clause=clause):
                self.assertIn(clause, text)

    def test_evals_have_trigger_prompts_and_a_quality_case(self):
        evals = json.loads((SKILL / "evals" / "evals.json").read_text(encoding="utf-8"))
        self.assertGreaterEqual(len(evals["should_trigger"]), 5)
        self.assertGreaterEqual(len(evals["should_not_trigger"]), 5)
        self.assertTrue((SKILL / evals["quality"]["case"]).is_file())
        for scenario in ("incremental", "agensi_delivery"):
            with self.subTest(scenario=scenario):
                self.assertTrue(evals[scenario]["input"])
                self.assertTrue(evals[scenario]["pass_when"])

    def test_pack_writes_one_top_folder_with_skill_md(self):
        with tempfile.TemporaryDirectory() as tmp, tempfile.TemporaryDirectory() as again:
            self.assertEqual(uncovr.pack(Path(tmp)), 0)
            with zipfile.ZipFile(Path(tmp) / "uncovr.zip") as archive:
                names = archive.namelist()
                self.assertEqual(archive.read("uncovr/LICENSE"), (SKILL.parents[2] / "LICENSE").read_bytes())
                expected = {f"uncovr/{path.relative_to(SKILL).as_posix()}"
                            for path in uncovr._shipped_files(SKILL)} | {"uncovr/LICENSE"}
                self.assertEqual(set(names), expected)
                self.assertEqual(len(names), len(set(names)))
                # Expected answers must not reach an agent under evaluation.
                self.assertFalse([n for n in names if n.startswith(("uncovr/examples/", "uncovr/evals/"))])
            self.assertIn("uncovr/SKILL.md", names)
            self.assertEqual({name.split("/")[0] for name in names}, {"uncovr"})
            self.assertFalse([n for n in names if "/." in n or "__pycache__" in n])
            self.assertFalse([name for name in names if name.endswith(".agent.md")])
            uncovr.pack(Path(again))
            self.assertEqual((Path(tmp) / "uncovr.zip").read_bytes(), (Path(again) / "uncovr.zip").read_bytes())


if __name__ == "__main__":
    unittest.main()
