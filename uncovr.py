#!/usr/bin/env python3
"""Uncovr: install and structurally validate evidence-first product context."""
from __future__ import annotations

import argparse
from collections import Counter
import json
from pathlib import Path
import re
import shutil
import sys

VERSION = "0.1.0"
ARTIFACTS = (
    "overview.md", "features.md", "domain.md",
    "architecture.md", "traceability.md", "validation.md",
)
CONFIDENCE = {"confirmed", "inferred", "gap", "contradicted"}
KINDS = {"feature", "business_rule", "architecture", "constraint", "decision", "assumption"}
BUSINESS = {"pending", "approved", "rejected", "not_applicable"}
LOCAL_SOURCES = {"code", "test", "config"}
OTHER_SOURCES = {"git", "runtime", "document", "interview"}
CLAIM_ID = re.compile(r"^[A-Z][A-Z0-9]*-[0-9]{3,}$")
REVISION = re.compile(r"^[0-9a-f]{7,40}$")


def _copy_if_missing(source: Path, destination: Path, created: list[str]) -> None:
    if destination.exists():
        return
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, destination)
    created.append(str(destination))


def install(target: Path) -> int:
    """Install skills and blank context artifacts without replacing user files."""
    target = target.expanduser().resolve()
    if not target.is_dir():
        print(f"Target directory does not exist: {target}", file=sys.stderr)
        return 2
    source_root = Path(__file__).resolve().parent
    if not (source_root / "templates" / "product-context").is_dir():
        print("Install must be run from the Uncovr source checkout.", file=sys.stderr)
        return 2
    created: list[str] = []
    for skill in sorted((source_root / ".github" / "skills").iterdir()):
        if skill.is_dir():
            destination = target / ".github" / "skills" / skill.name
            if not destination.exists():
                shutil.copytree(skill, destination)
                created.append(str(destination))
    _copy_if_missing(
        source_root / ".github" / "agents" / "uncovr.agent.md",
        target / ".github" / "agents" / "uncovr.agent.md", created
    )
    for template in sorted((source_root / "templates" / "product-context").iterdir()):
        _copy_if_missing(template, target / "product-context" / template.name, created)
    _copy_if_missing(source_root / "uncovr.py", target / ".uncovr" / "uncovr.py", created)
    _copy_if_missing(source_root / "docs" / "evidence-contract.md",
                     target / ".uncovr" / "evidence-contract.md", created)
    state = target / ".uncovr" / "state.json"
    if not state.exists():
        state.parent.mkdir(parents=True, exist_ok=True)
        state.write_text(json.dumps({
            "version": VERSION, "phase": "initialized", "baseline_revision": None,
            "modules_reviewed": [], "last_validation": None
        }, indent=2) + "\n", encoding="utf-8")
        created.append(str(state))
    print(f"Uncovr installed: {len(created)} new paths. Existing files were not overwritten.")
    print("In Copilot, select the Uncovr agent, then ask to reconstruct this repository.")
    print("Structural check: python3 .uncovr/uncovr.py check .")
    return 0


def load_claims(root: Path) -> tuple[list[dict], list[str]]:
    evidence_file = root / "product-context" / "evidence.jsonl"
    errors: list[str] = []
    claims: list[dict] = []
    if not evidence_file.is_file():
        return claims, ["Missing product-context/evidence.jsonl"]
    for line_number, line in enumerate(evidence_file.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        try:
            record = json.loads(line)
            if not isinstance(record, dict):
                raise ValueError("record must be an object")
            claims.append(record)
        except ValueError as error:
            errors.append(f"evidence.jsonl:{line_number}: {error}")
    return claims, errors


def validate(target: Path) -> tuple[list[str], list[str], Counter]:
    """Perform structural checks; not an endorsement of semantic correctness."""
    root = target.expanduser().resolve()
    errors: list[str] = []
    warnings: list[str] = []
    counts: Counter = Counter()
    context = root / "product-context"
    documents: dict[str, str] = {}
    for filename in ARTIFACTS:
        path = context / filename
        if not path.is_file():
            errors.append(f"Missing product-context/{filename}")
            continue
        content = path.read_text(encoding="utf-8")
        documents[filename] = content
        if "<!-- TODO:" in content:
            warnings.append(f"{filename} still contains its scaffold placeholder")
    claims, parse_errors = load_claims(root)
    errors.extend(parse_errors)
    ids: set[str] = set()
    for row, record in enumerate(claims, 1):
        claim = record.get("id")
        where = f"evidence.jsonl:record {row}"
        if not isinstance(claim, str) or not CLAIM_ID.fullmatch(claim):
            errors.append(f"{where}: invalid claim id")
            continue
        if claim in ids:
            errors.append(f"{where}: duplicate claim id {claim}")
        ids.add(claim)
        kind = record.get("kind")
        confidence = record.get("confidence")
        business = record.get("business_validation")
        if kind not in KINDS:
            errors.append(f"{where}: invalid kind for {claim}")
        if confidence not in CONFIDENCE:
            errors.append(f"{where}: invalid confidence for {claim}")
        else:
            counts[confidence] += 1
        if business not in BUSINESS:
            errors.append(f"{where}: invalid business_validation for {claim}")
        if not isinstance(record.get("summary"), str) or not record["summary"].strip():
            errors.append(f"{where}: missing summary for {claim}")
        if business == "approved" and not (
            isinstance(record.get("validated_by"), str) and record["validated_by"].strip()
            and isinstance(record.get("validated_on"), str) and record["validated_on"].strip()
        ):
            errors.append(f"{where}: approved claim {claim} needs validated_by and validated_on")
        evidence = record.get("evidence")
        if not isinstance(evidence, list):
            errors.append(f"{where}: evidence must be an array for {claim}")
            continue
        if confidence in {"confirmed", "inferred", "contradicted"} and not evidence:
            errors.append(f"{where}: {claim} has no evidence")
        if confidence == "confirmed" and not any(
            isinstance(item, dict) and item.get("type") in {"code", "test", "config", "runtime"}
            for item in evidence
        ):
            errors.append(f"{where}: confirmed {claim} lacks technical evidence")
        for index, item in enumerate(evidence, 1):
            prefix = f"{where}: {claim} evidence {index}"
            if not isinstance(item, dict):
                errors.append(f"{prefix} must be an object")
                continue
            evidence_type = item.get("type")
            ref = item.get("ref")
            if evidence_type not in LOCAL_SOURCES | OTHER_SOURCES:
                errors.append(f"{prefix}: invalid type")
            if not isinstance(ref, str) or not ref.strip():
                errors.append(f"{prefix}: missing ref")
                continue
            if evidence_type in LOCAL_SOURCES:
                relative = Path(ref)
                absolute = (root / relative).resolve()
                if relative.is_absolute() or (absolute != root and root not in absolute.parents):
                    errors.append(f"{prefix}: reference escapes repository")
                    continue
                if not absolute.is_file():
                    errors.append(f"{prefix}: missing local source {ref}")
                    continue
                start, end = item.get("line_start"), item.get("line_end")
                if (start is None) != (end is None):
                    errors.append(f"{prefix}: both line_start and line_end are required")
                elif start is not None:
                    if type(start) is not int or type(end) is not int or start < 1 or end < start:
                        errors.append(f"{prefix}: invalid line range")
                    else:
                        try:
                            line_count = len(absolute.read_text(encoding="utf-8").splitlines())
                            if end > line_count:
                                errors.append(f"{prefix}: line range exceeds {ref} ({line_count} lines)")
                        except UnicodeError:
                            warnings.append(f"{prefix}: could not inspect non-text source {ref}")
                revision = item.get("revision")
                if not isinstance(revision, str) or not REVISION.fullmatch(revision):
                    warnings.append(f"{prefix}: pin a Git revision for reproducible evidence")
        if not any(claim in doc for doc in documents.values()):
            warnings.append(f"{claim} is not referenced in any of the six Markdown artifacts")
    if not claims:
        warnings.append("No evidence claims yet; the baseline is not ready for use")
    return errors, warnings, counts


def check(target: Path) -> int:
    if not target.is_dir():
        print(f"Target directory does not exist: {target}", file=sys.stderr)
        return 2
    errors, warnings, counts = validate(target)
    for error in errors:
        print(f"ERROR: {error}")
    for warning in warnings:
        print(f"WARN: {warning}")
    print(f"Claims: {sum(counts.values())} | confirmed={counts['confirmed']} "
          f"inferred={counts['inferred']} gap={counts['gap']} "
          f"contradicted={counts['contradicted']}")
    if errors:
        print("INVALID: fix structural errors before review.")
        return 1
    if warnings:
        print("STRUCTURE VALID WITH WARNINGS: human validation remains required.")
        return 0
    print("STRUCTURE VALID: this does not certify business correctness.")
    return 0


def status(target: Path) -> int:
    root = target.expanduser().resolve()
    state = root / ".uncovr" / "state.json"
    if not state.is_file():
        print("Uncovr not installed here.", file=sys.stderr)
        return 2
    try:
        data = json.loads(state.read_text(encoding="utf-8"))
    except (OSError, ValueError) as error:
        print(f"Invalid state: {error}", file=sys.stderr)
        return 1
    _, _, counts = validate(root)
    print(f"Phase: {data.get('phase', 'unknown')}")
    print(f"Baseline revision: {data.get('baseline_revision') or 'unrecorded'}")
    print(f"Reviewed modules: {len(data.get('modules_reviewed', []))}")
    print(f"Evidence: {dict(counts)}")
    print("NOTE: status is descriptive, not a semantic quality certification.")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Uncovr product context toolkit")
    parser.add_argument("--version", action="version", version=VERSION)
    sub = parser.add_subparsers(dest="command", required=True)
    for name in ("install", "check", "status"):
        command = sub.add_parser(name)
        command.add_argument("target", nargs="?", default=".")
    args = parser.parse_args()
    return {"install": install, "check": check, "status": status}[args.command](Path(args.target))


if __name__ == "__main__":
    sys.exit(main())
