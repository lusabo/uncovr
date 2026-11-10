# Uncovr

Understand what a legacy system does before you change it.

## What this skill does

Uncovr reads an existing repository and writes a **Product Context Baseline** under `product-context/`: an overview, the feature catalogue, the domain and its business rules, the architecture that matters for change, traceability from rules to code and tests, and a validation sheet with the questions only a person can answer. Every claim has a stable ID and points to the file and lines it came from in `evidence.jsonl`.

It also brings out what is easy to miss in a legacy system: business parameters that are hard-coded or configurable, feature flags, scheduled jobs and background workers, who may do what (a role × action matrix), which fields hold personal data (names only, never values), the acceptance criteria the tests already assert, deployment, dependencies and known debt. Each feature gets a criticality rating so the riskiest questions come first. The checklist behind this, in `references/repository-signals.md`, follows the topics of the SWEBOK Guide v4.0.

It separates what the code shows (`confirmed`, `inferred`, `gap`, `contradicted`) from what the business has approved. It never approves anything for you, and it does not change your code.

## When it activates

Ask your agent things like:

- "I inherited this codebase. What does it actually do?"
- "Map the business rules the code enforces before we change the approval flow."
- "Rebuild the product context so the PO can plan the next version."

It does not activate to write or fix code, specify new features, or review a pull request.

## How a run goes

1. **Scope.** The agent proposes what to analyse and waits for you to confirm.
2. **Explore, analyse, validate.** It maps the system, reconstructs features and rules with evidence, then reviews the result — in a separate context when your agent supports subagents.
3. **Review.** It stops with a summary and the questions for you. Nothing is marked approved until you say so.

## Example

`examples/order-approval/` holds a small purchase-request app and the baseline a good run produces. One rule is deliberately contradictory — the code sets the approval limit at 5000, the README at 10 000 — and the expected baseline leaves it `contradicted` and asks you about it, instead of picking one.

## Requires

- Read access to the repository.
- Optional: `git`, to pin the revision of every source and to read the change history; `python3` 3.10+, to run `scripts/check.py`, a structural check, and `scripts/history.py`, which measures commits, churn, fix commits and ticket references per module. Both are read-only, write nothing, use no network, and never print who made a change.

Works with GitHub Copilot (VS Code) and Claude Code.

## Limits

The structural check proves that IDs, paths and line ranges are well formed — not that a claim is true. Completeness cannot be inferred from claim counts. Runtime-only behaviour and third-party integrations may remain gaps.
