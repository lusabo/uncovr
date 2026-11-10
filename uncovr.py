#!/usr/bin/env python3
"""Uncovr: install, check and package the evidence-first product context skill."""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import shutil
import sys
import zipfile

VERSION = "0.4.0"
MANIFEST = ".uncovr/manifest.json"
SKILL_NAME = "uncovr"
SKILL_DIR = ".github/skills/uncovr"
INSTALL_SKIP = ("examples", "evals")
SKILL_MD_MAX_LINES = 500
SCRIPT_MAX_BYTES = 20_000


def _load_check():
    path = Path(__file__).resolve().parent / SKILL_DIR / "scripts" / "check.py"
    spec = importlib.util.spec_from_file_location("uncovr_check", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


# The structural check ships inside the skill; this CLI reuses it rather than keeping a copy.
_check = _load_check()
ARTIFACTS = _check.ARTIFACTS
load_claims = _check.load_claims
validate = _check.validate
check = _check.check


def _copy_if_missing(source: Path, destination: Path, created: list[str]) -> None:
    if destination.exists():
        return
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, destination)
    created.append(str(destination))


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _source_root() -> Path | None:
    root = Path(__file__).resolve().parent
    return root if (root / SKILL_DIR / "SKILL.md").is_file() else None


def _package_files(skill: Path) -> list[Path]:
    """Files of the skill folder, without hidden files or caches."""
    return [
        path for path in sorted(skill.rglob("*"))
        if path.is_file() and not any(
            part.startswith(".") or part == "__pycache__" for part in path.relative_to(skill).parts
        )
    ]


def _managed_files(source_root: Path) -> list[tuple[Path, str]]:
    """Package files that Uncovr installs and owns, paired with their path in a target."""
    skill = source_root / SKILL_DIR
    pairs = [
        (path, f"{SKILL_DIR}/{path.relative_to(skill).as_posix()}")
        for path in _package_files(skill)
        if path.relative_to(skill).parts[0] not in INSTALL_SKIP
    ]
    pairs += [
        (path, path.relative_to(source_root).as_posix())
        for path in sorted((source_root / ".github" / "agents").glob("*.agent.md"))
    ]
    return pairs


def install(target: Path) -> int:
    """Install skills and blank context artifacts without replacing user files."""
    target = target.expanduser().resolve()
    if not target.is_dir():
        print(f"Target directory does not exist: {target}", file=sys.stderr)
        return 2
    source_root = _source_root()
    if source_root is None:
        print("Install must be run from the Uncovr source checkout.", file=sys.stderr)
        return 2
    created: list[str] = []
    managed = _managed_files(source_root)
    for source, relative in managed:
        _copy_if_missing(source, target / relative, created)
    for template in sorted((source_root / SKILL_DIR / "assets" / "product-context").iterdir()):
        _copy_if_missing(template, target / "product-context" / template.name, created)
    manifest = target / MANIFEST
    if not manifest.exists():
        manifest.parent.mkdir(parents=True, exist_ok=True)
        manifest.write_text(json.dumps({
            "version": VERSION,
            "files": {relative: _sha256(source) for source, relative in managed},
        }, indent=2) + "\n", encoding="utf-8")
        created.append(str(manifest))
    state = target / ".uncovr" / "state.json"
    if not state.exists():
        state.parent.mkdir(parents=True, exist_ok=True)
        state.write_text(json.dumps({
            "version": VERSION, "phase": "initialized", "baseline_revision": None,
            "modules_reviewed": [], "last_validation": None, "wiki_target": None
        }, indent=2) + "\n", encoding="utf-8")
        created.append(str(state))
    print(f"Uncovr installed: {len(created)} new paths. Existing files were not overwritten.")
    print("In Copilot, select the Uncovr agent, then ask to reconstruct this repository.")
    print(f"Structural check: python3 {SKILL_DIR}/scripts/check.py .")
    return 0


def pack_problems(skill: Path) -> list[str]:
    """Reasons the skill folder would fail the marketplace's structure and file-type checks."""
    problems: list[str] = []
    if not (skill / "SKILL.md").is_file():
        return ["SKILL.md missing"]
    for path in sorted(skill.rglob("*")):
        if path.is_symlink():
            problems.append(f"{path.relative_to(skill).as_posix()}: symlink")
    for path in _package_files(skill):
        relative = path.relative_to(skill).as_posix()
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeError:
            problems.append(f"{relative}: not a text file")
            continue
        if relative == "SKILL.md" and len(text.splitlines()) >= SKILL_MD_MAX_LINES:
            problems.append(f"SKILL.md: {len(text.splitlines())} lines (keep under {SKILL_MD_MAX_LINES})")
        if relative.startswith("scripts/") and len(text.encode("utf-8")) > SCRIPT_MAX_BYTES:
            problems.append(f"{relative}: larger than {SCRIPT_MAX_BYTES} bytes")
    return problems


def pack(out: Path) -> int:
    """Write <out>/uncovr.zip: one top folder with SKILL.md at its root, text files only."""
    source_root = _source_root()
    if source_root is None:
        print("Pack must be run from the Uncovr source checkout.", file=sys.stderr)
        return 2
    skill = source_root / SKILL_DIR
    problems = pack_problems(skill)
    for problem in problems:
        print(f"ERROR: {problem}")
    if problems:
        return 1
    out = out.expanduser().resolve()
    out.mkdir(parents=True, exist_ok=True)
    archive = out / f"{SKILL_NAME}.zip"
    files = _package_files(skill)
    with zipfile.ZipFile(archive, "w", zipfile.ZIP_DEFLATED) as zf:
        for path in files:
            # Fixed timestamp and mode keep the archive identical for identical sources.
            info = zipfile.ZipInfo(f"{SKILL_NAME}/{path.relative_to(skill).as_posix()}", (1980, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o644 << 16
            zf.writestr(info, path.read_bytes())
    print(f"Packed {len(files)} files into {archive}")
    return 0


def install_drift(root: Path) -> list[str]:
    """Differences between the installed files, their manifest and, from a source checkout, the package."""
    root = root.expanduser().resolve()
    manifest = root / MANIFEST
    if not manifest.is_file():
        return [f"no {MANIFEST}: installed before 0.2.0 or by hand; versions cannot be compared"]
    try:
        data = json.loads(manifest.read_text(encoding="utf-8"))
        files = data["files"]
        if not isinstance(files, dict):
            raise ValueError("files must be an object")
    except (OSError, ValueError, KeyError, TypeError) as error:
        return [f"invalid {MANIFEST}: {error}"]
    notes: list[str] = []
    if data.get("version") != VERSION:
        notes.append(f"installed version {data.get('version')} differs from this Uncovr ({VERSION})")
    source_root = _source_root()
    package = {relative: source for source, relative in _managed_files(source_root)} if source_root else {}
    for relative, digest in sorted(files.items()):
        path = (root / relative).resolve()
        if root not in path.parents:
            notes.append(f"{relative}: path escapes repository")
            continue
        if not path.is_file():
            notes.append(f"{relative}: missing")
            continue
        if _sha256(path) != digest:
            notes.append(f"{relative}: modified locally")
        if relative in package and _sha256(package[relative]) != digest:
            notes.append(f"{relative}: the package has a different version")
    for relative in sorted(set(package) - set(files)):
        notes.append(f"{relative}: in the package, not installed")
    return notes


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
    drift = install_drift(root)
    for note in drift:
        print(f"INSTALL: {note}")
    if not drift:
        print("INSTALL: files match the manifest")
    print("NOTE: status is descriptive, not a semantic quality certification.")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Uncovr product context toolkit")
    parser.add_argument("--version", action="version", version=VERSION)
    sub = parser.add_subparsers(dest="command", required=True)
    for name in ("install", "check", "status"):
        command = sub.add_parser(name)
        command.add_argument("target", nargs="?", default=".")
    sub.add_parser("pack", help="write the marketplace ZIP").add_argument("target", nargs="?", default="dist")
    args = parser.parse_args()
    commands = {"install": install, "check": check, "status": status, "pack": pack}
    return commands[args.command](Path(args.target))


if __name__ == "__main__":
    sys.exit(main())
