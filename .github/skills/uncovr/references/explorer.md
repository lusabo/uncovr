# Stage 1 — Explorer

## Goal

Create a **targeted map** of the system, not a file-by-file catalogue. Focus on product behavior and technical boundaries needed for assessing future changes.

## Inputs

- The scope, module batch and exclusions confirmed at the scope checkpoint (`SKILL.md`).
- Git HEAD SHA recorded in `product-context/overview.md`, and `.uncovr/state.json`.
- The repository working tree.

## Steps

1. Inspect README and manifest files, source tree, framework and test configuration, runtime entry points, routing, schema/migrations, CI and integration adapters. Skip build outputs, generated/vendor folders and secrets. Use `repository-signals.md`, next to this file, as the checklist of what to look for: record each signal found, and the signals looked for but not observed.
2. Record main modules, owners if explicit, external services, data stores, API/event contracts and likely capability boundaries. Distinguish files that are only infrastructure from business-bearing code.
3. For each capability, identify potential entry points and tests. Prioritize central business workflows and branches with measurable behavior.
4. Read important paths only; sample dense modules before expanding scope. Record modules that cannot be inspected and why.
   When Git and a terminal are available, run `python3 scripts/history.py <repository root>` (the skill's script, read-only). It lists, per module, commits, churn, fix commits, ticket references, number of authors and last change. Use it to choose where to read first, and record the measured facts under *Regression hotspots* with `git` evidence naming the command, the revision and the module. It is not a risk score; a shallow clone understates it.
5. Write `product-context/architecture.md` (including *Deployment and environments*, *Change constraints* and *Known debt*) and the verified inventory/technical baseline sections in `overview.md`, with owners from CODEOWNERS when declared. Add provisional feature names to `features.md` only where supported.
6. Create technical claims in `evidence.jsonl` and reference them from Markdown. Use the contract in `evidence-contract.md`, next to this file.

## Guardrails

- A folder/class name is **not** proof of product purpose or user intent.
- Don't invent missing system integrations or architecture decisions; write a gap instead.
- For local source evidence, quote relative file path, line range when feasible, and HEAD revision. Avoid evidence paths that leave the repository.
- Mark assumptions as `inferred`.
- The boundaries in `SKILL.md` apply.

## Completion

The PO should understand what areas exist, which ones were inspected and where to investigate functional behavior next.
