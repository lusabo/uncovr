#!/usr/bin/env python3
"""Structural check of an Uncovr Product Context Baseline.

Usage: python3 check.py [repository root]   (default: current directory)

Standard library only and self-contained: it reads product-context/ and the files
the evidence cites inside the given repository, writes nothing and uses no network.
It checks structure, not whether a claim is true.
"""
from __future__ import annotations

import argparse
from collections import Counter
import json
from pathlib import Path
import re
import sys

ARTIFACTS = (
    "overview.md", "features.md", "domain.md",
    "architecture.md", "traceability.md", "validation.md",
)
CONFIDENCE = {"confirmed", "inferred", "gap", "contradicted"}
KINDS = {"feature", "business_rule", "architecture", "constraint", "decision", "assumption"}
BUSINESS = {"pending", "approved", "rejected", "not_applicable"}
# Claims whose meaning is a business matter; not_applicable never fits them.
BUSINESS_KINDS = {"feature", "business_rule", "assumption"}
LOCAL_SOURCES = {"code", "test", "config"}
OTHER_SOURCES = {"git", "runtime", "document", "interview"}
CLAIM_ID = re.compile(r"^[A-Z][A-Z0-9]*-[0-9]{3,}$")
MENTION = re.compile(r"\b([A-Z][A-Z0-9]*-[0-9]{3,})\b")
TABLE_SEPARATOR = re.compile(r"^\|\s*:?-{3,}")
# Rows of these architecture.md tables must each cite a claim from evidence.jsonl.
CITED_TABLES = ("Technology stack", "Context and major components")
REVISION = re.compile(r"^[0-9a-f]{7,40}$")
SOURCE_STATUS = {"consulted", "indicated", "inaccessible"}
BACKTICKED = re.compile(r"`([^`]+)`")
MERMAID_OPEN = re.compile(r"^[ \t]*(`{3,}|~{3,})[ \t]*mermaid[ \t]*$")
DIAGRAM_TYPES = {"flowchart", "graph", "sequenceDiagram", "stateDiagram-v2", "stateDiagram", "erDiagram"}
DIAGRAM_DECORATION = ("%%{", "style ", "classDef ", "click ", "linkStyle ")
DIAGRAM_MAX_LINES = 20


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


def section(text: str, heading: str) -> str:
    match = re.search(rf"(?m)^## {re.escape(heading)}[ \t]*$", text)
    if not match:
        return ""
    end = re.search(r"(?m)^## ", text[match.end():])
    return text[match.end():match.end() + end.start()] if end else text[match.end():]


def table(text: str, heading: str) -> list[list[str]]:
    """Body rows of the table under a heading, as lists of cells."""
    lines = [line.strip() for line in section(text, heading).splitlines()
             if line.strip().startswith("|")]
    if len(lines) >= 2 and TABLE_SEPARATOR.match(lines[1]):
        lines = lines[2:]
    return [[cell.strip() for cell in line.strip("|").split("|")] for line in lines]


def reference_warnings(documents: dict[str, str], ids: set[str]) -> list[str]:
    """Claim IDs cited in Markdown but absent from the index, and architecture rows citing none."""
    warnings: list[str] = []
    prefixes = {claim.split("-")[0] for claim in ids}
    for filename, content in documents.items():
        for cited in sorted(set(MENTION.findall(content))):
            if cited not in ids and cited.split("-")[0] in prefixes:
                warnings.append(f"{filename} cites {cited}, which is not in evidence.jsonl")
    architecture = documents.get("architecture.md", "")
    if "<!-- TODO:" in architecture:
        return warnings
    for heading in CITED_TABLES:
        for row in table(architecture, heading):
            if not MENTION.search(" ".join(row)):
                warnings.append(f"architecture.md: row '{row[0]}' in {heading} cites no claim ID")
    return warnings


def refs(record: dict) -> list[str]:
    return [item["ref"] for item in record.get("evidence") or []
            if isinstance(item, dict) and isinstance(item.get("ref"), str)]


def recorded_decision(record: dict | None) -> bool:
    return bool(record) and record.get("kind") == "decision" \
        and record.get("business_validation") in {"approved", "rejected"} \
        and all(isinstance(record.get(key), str) and record[key].strip()
                for key in ("validated_by", "validated_on"))


def view_warnings(documents: dict[str, str], records: dict[str, dict]) -> list[str]:
    """Where the traceability and validation views disagree with evidence.jsonl."""
    warnings: list[str] = []
    trace = documents.get("traceability.md", "")
    if trace and "<!-- TODO:" not in trace:
        # The main claim table precedes the first "## " heading.
        for row in table("## Main\n" + trace.split("\n## ")[0], "Main"):
            record = records.get(row[0].strip("`*"))
            if not record or len(row) < 4:
                continue
            files = {ref.split(" (")[0] for ref in refs(record)}
            for cited in BACKTICKED.findall(" ".join(row[2:4])):
                path = cited.split(":")[0].rstrip("/")
                if "/" in cited or "." in path:
                    if path not in files and not any(f.startswith(path + "/") for f in files):
                        warnings.append(f"traceability.md: {row[0]} names {cited}, "
                                        "which its evidence in evidence.jsonl does not cite")
        for row in table(trace, "Sources"):
            label = row[0].strip("`")
            status = row[4].strip("` ").lower() if len(row) > 4 else ""
            if status not in SOURCE_STATUS:
                warnings.append(f"traceability.md: source '{label}' needs status consulted, "
                                "indicated or inaccessible")
            if not MENTION.search(row[-1]):
                warnings.append(f"traceability.md: source '{label}' cites no claim ID")
            if status in {"indicated", "inaccessible"} and any(
                    ref == label or ref.startswith(label + " ")
                    for record in records.values() for ref in refs(record)):
                warnings.append(f"traceability.md: source '{label}' is {status} "
                                "but cited as evidence in evidence.jsonl")
    review = documents.get("validation.md", "")
    if not review or "<!-- TODO:" in review:
        return warnings
    contradictions = section(review, "Contradictions and review outcomes")
    questions = section(review, "Outstanding questions")
    for claim, record in records.items():
        if record.get("confidence") == "contradicted" and claim not in contradictions:
            warnings.append(f"validation.md: contradicted {claim} is not listed "
                            "under Contradictions and review outcomes")
    for row in table(review, "Decisions"):
        decided = MENTION.findall(row[0])
        if not decided:
            warnings.append(f"validation.md: decision row '{row[0]}' cites no decision claim")
        for claim in decided:
            if claim in records and not recorded_decision(records[claim]):
                warnings.append(f"validation.md: {claim} is listed as a decision but evidence.jsonl "
                                "records no human decision (kind decision, approved or rejected, "
                                "validated_by, validated_on)")
        status = row[3].lower() if len(row) > 3 else ""
        reason = row[4] if len(row) > 4 else ""
        if status.startswith("reopened"):
            if not set(MENTION.findall(reason)) - set(decided):
                warnings.append(f"validation.md: reopened {row[0]} needs the claim ID "
                                "of the new evidence as its reason")
            if not any(claim in questions for claim in decided):
                warnings.append(f"validation.md: reopened {row[0]} is not asked again "
                                "under Outstanding questions")
        elif status.startswith("superseded"):
            for newer in MENTION.findall(row[3]):
                if newer in records and not set(decided) & set(records[newer].get("supersedes") or []):
                    warnings.append(f"validation.md: {newer} does not list {row[0]} in supersedes")
    return warnings


def diagram_warnings(documents: dict[str, str], records: dict[str, dict]) -> list[str]:
    """Form of Mermaid blocks; whether a diagram is right is for the reviewer."""
    warnings: list[str] = []
    for filename, content in documents.items():
        lines = content.splitlines()
        index = 0
        while index < len(lines):
            opened = MERMAID_OPEN.match(lines[index])
            index += 1
            if not opened:
                continue
            where = f"{filename}: Mermaid block at line {index}"
            start, fence = index, opened.group(1)
            while index < len(lines) and lines[index].strip() != fence:
                index += 1
            if index == len(lines):
                warnings.append(f"{where} is not closed")
                break
            body = [line.strip() for line in lines[start:index] if line.strip()]
            index += 1
            before = start - 1
            while before > 0 and not lines[before - 1].strip():
                before -= 1
            caption = []
            while before > 0 and lines[before - 1].strip() and not lines[before - 1].startswith("#"):
                caption.insert(0, lines[before - 1])
                before -= 1
            text = " ".join(body + caption)
            first = next((line for line in body if not line.startswith("%%")), "")
            kind = first.split()[0] if first else ""
            if kind not in DIAGRAM_TYPES:
                warnings.append(f"{where} is a '{kind}' diagram; use flowchart, sequenceDiagram, "
                                "stateDiagram-v2 or erDiagram, and no charts of quantities")
            if any(line.startswith(DIAGRAM_DECORATION) for line in body):
                warnings.append(f"{where} uses themes, styles or click handlers")
            if len(body) > DIAGRAM_MAX_LINES:
                warnings.append(f"{where} has {len(body)} lines; split it")
            cited = [claim for claim in dict.fromkeys(MENTION.findall(text)) if claim in records]
            if not cited:
                warnings.append(f"{where} cites no claim ID in it or in the sentence before it")
            for claim in cited:
                confidence = str(records[claim].get("confidence"))
                if confidence != "confirmed" and confidence not in text.lower():
                    warnings.append(f"{where} draws {claim} without saying it is {confidence}")
    return warnings


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
        elif business == "not_applicable" and (kind in BUSINESS_KINDS or confidence == "gap"):
            warnings.append(f"{where}: {claim} is not_applicable; business claims and unknowns stay pending")
        if not isinstance(record.get("summary"), str) or not record["summary"].strip():
            errors.append(f"{where}: missing summary for {claim}")
        if business == "approved" and not (
            isinstance(record.get("validated_by"), str) and record["validated_by"].strip()
            and isinstance(record.get("validated_on"), str) and record["validated_on"].strip()
        ):
            errors.append(f"{where}: approved claim {claim} needs validated_by and validated_on")
        supersedes = record.get("supersedes")
        if supersedes is not None and (
            not isinstance(supersedes, list) or claim in supersedes
            or not all(isinstance(item, str) and CLAIM_ID.fullmatch(item) for item in supersedes)
        ):
            errors.append(f"{where}: supersedes for {claim} must be an array of other claim IDs")
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
    records = {record["id"]: record for record in claims
               if isinstance(record.get("id"), str) and record["id"] in ids}
    for claim, record in records.items():
        unknown = [item for item in record.get("supersedes") or []
                   if isinstance(item, str) and item not in ids]
        if isinstance(record.get("supersedes"), list) and unknown:
            errors.append(f"evidence.jsonl: {claim} supersedes unknown {', '.join(unknown)}")
    warnings.extend(reference_warnings(documents, ids))
    warnings.extend(view_warnings(documents, records))
    warnings.extend(diagram_warnings(documents, records))
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


def main() -> int:
    parser = argparse.ArgumentParser(description="Structural check of an Uncovr baseline")
    parser.add_argument("target", nargs="?", default=".")
    return check(Path(parser.parse_args().target))


if __name__ == "__main__":
    sys.exit(main())
