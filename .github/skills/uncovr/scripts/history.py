#!/usr/bin/env python3
"""Where change concentrates in a repository, from its Git history.

Usage: python3 history.py [repository root] [--since 2.years] [--depth 2] [--top 20] [--json]

Standard library only and self-contained. Read-only: it runs `git rev-parse` and
`git log`, writes nothing and uses no network. It reports measured facts per module
(commits, churn, fix commits, ticket references, number of authors, last change);
it does not score risk and never prints who made a change.
"""
from __future__ import annotations

import argparse
from collections import defaultdict
import json
from pathlib import Path
import re
import subprocess
import sys

RECORD = "\x1e"
FIELD = "\x1f"
EXCLUDED_DIRS = {
    "node_modules", "vendor", "dist", "build", "target", ".venv", "venv", "__pycache__", ".git",
}
EXCLUDED_PREFIXES = ("product-context/", ".uncovr/", ".github/skills/uncovr/")
LOCKFILES = {
    "package-lock.json", "yarn.lock", "pnpm-lock.yaml", "poetry.lock", "Pipfile.lock",
    "Gemfile.lock", "composer.lock", "Cargo.lock", "go.sum", "uv.lock",
}
FIX = re.compile(
    r"^(fix|bugfix|hotfix)(\([^)]*\))?!?:|\b(fix(es|ed)?|bugs?|hotfix|defect|corrige|corrigir|corre[cç][aã]o)\b",
    re.IGNORECASE,
)
TICKET = re.compile(r"\b[A-Z][A-Z0-9]+-\d+\b|(?<![\w/])#\d+\b")


def git(root: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", "-C", str(root), *args], capture_output=True, text=True, check=False,
    )
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or f"git {' '.join(args)} failed")
    return result.stdout


def new_path(path: str) -> str:
    """Resolve numstat rename notation (`a => b`, `dir/{a => b}/f`) to the new path."""
    if "=>" not in path:
        return path
    if "{" in path and "}" in path:
        head, rest = path.split("{", 1)
        inner, tail = rest.split("}", 1)
        return (head + inner.split("=>", 1)[1].strip() + tail).replace("//", "/")
    return path.split("=>", 1)[1].strip()


def excluded(path: str) -> bool:
    parts = path.split("/")
    return (
        any(part in EXCLUDED_DIRS for part in parts[:-1])
        or parts[-1] in LOCKFILES
        or path.startswith(EXCLUDED_PREFIXES)
    )


def module_of(path: str, depth: int) -> str:
    directories = path.split("/")[:-1]
    return "/".join(directories[:depth]) if directories else "(root)"


def parse_log(text: str) -> list[dict]:
    """Commits as {sha, date, author, subject, files: [(path, added, deleted)]}."""
    commits = []
    for chunk in text.split(RECORD):
        if not chunk.strip():
            continue
        header, _, body = chunk.partition("\n")
        fields = header.split(FIELD)
        if len(fields) != 4:
            continue
        sha, date, author, subject = fields
        files = []
        for line in body.splitlines():
            parts = line.split("\t")
            if len(parts) != 3:
                continue
            added, deleted, path = parts
            files.append((
                new_path(path),
                int(added) if added.isdigit() else 0,
                int(deleted) if deleted.isdigit() else 0,
            ))
        commits.append({"sha": sha, "date": date, "author": author, "subject": subject, "files": files})
    return commits


def summarise(commits: list[dict], depth: int) -> list[dict]:
    modules: dict[str, dict] = defaultdict(lambda: {
        "commits": 0, "fix_commits": 0, "churn": 0, "tickets": set(), "authors": set(), "last_change": "",
    })
    for commit in commits:
        is_fix = bool(FIX.search(commit["subject"]))
        tickets = set(TICKET.findall(commit["subject"]))
        touched: dict[str, int] = defaultdict(int)
        for path, added, deleted in commit["files"]:
            if not excluded(path):
                touched[module_of(path, depth)] += added + deleted
        for module, churn in touched.items():
            entry = modules[module]
            entry["commits"] += 1
            entry["fix_commits"] += is_fix
            entry["churn"] += churn
            entry["tickets"] |= tickets
            entry["authors"].add(commit["author"])
            entry["last_change"] = max(entry["last_change"], commit["date"][:10])
    rows = []
    for module, entry in modules.items():
        rows.append({
            "module": module,
            "commits": entry["commits"],
            "fix_commits": entry["fix_commits"],
            "fix_ratio": round(entry["fix_commits"] / entry["commits"], 2),
            "churn": entry["churn"],
            "tickets": sorted(entry["tickets"]),
            "authors": len(entry["authors"]),
            "last_change": entry["last_change"],
        })
    return sorted(rows, key=lambda row: (-row["churn"], -row["commits"], row["module"]))


def history(root: Path, since: str, depth: int) -> dict:
    root = root.expanduser().resolve()
    head = git(root, "rev-parse", "HEAD").strip()
    shallow = git(root, "rev-parse", "--is-shallow-repository").strip() == "true"
    log = git(
        root, "log", "--no-merges", "--numstat", f"--since={since}",
        f"--format={RECORD}%H{FIELD}%aI{FIELD}%ae{FIELD}%s",
    )
    commits = parse_log(log)
    return {
        "revision": head,
        "since": since,
        "shallow": shallow,
        "commits": len(commits),
        "modules": summarise(commits, depth),
    }


def render(report: dict, top: int) -> str:
    lines = [
        f"History at {report['revision'][:12]} since {report['since']}: {report['commits']} commits (merges excluded).",
    ]
    if report["shallow"]:
        lines.append("WARN: shallow clone; older history is missing and counts are understated.")
    lines += [
        "",
        "| Module | Commits | Fix commits | Fix ratio | Churn (lines) | Authors | Last change | Tickets |",
        "| --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    for row in report["modules"][:top]:
        tickets = ", ".join(row["tickets"][:3]) + (" …" if len(row["tickets"]) > 3 else "")
        lines.append(
            f"| `{row['module']}` | {row['commits']} | {row['fix_commits']} | {row['fix_ratio']:.2f} "
            f"| {row['churn']} | {row['authors']} | {row['last_change']} | {tickets or '—'} |"
        )
    lines += [
        "",
        "Measured facts, not a risk score. Fix commits are detected from commit subjects and may be"
        " miscounted; a high count of authors or a single author is a question for the team, not a finding.",
    ]
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Where change concentrates, from Git history")
    parser.add_argument("target", nargs="?", default=".")
    parser.add_argument("--since", default="2.years")
    parser.add_argument("--depth", type=int, default=2)
    parser.add_argument("--top", type=int, default=20)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    try:
        report = history(Path(args.target), args.since, max(args.depth, 1))
    except (OSError, RuntimeError) as error:
        print(f"No Git history available: {error}", file=sys.stderr)
        return 2
    print(json.dumps(report, indent=2) if args.json else render(report, args.top))
    return 0


if __name__ == "__main__":
    sys.exit(main())
