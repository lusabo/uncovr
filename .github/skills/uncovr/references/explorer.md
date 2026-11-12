# Stage 1 — Explorer

## Goal

Create a **targeted map** of the system, not a file-by-file catalogue. Focus on product behavior and technical boundaries needed for assessing future changes.

## Inputs

- The scope, module batch and exclusions confirmed at the scope checkpoint (`SKILL.md`).
- Git HEAD SHA recorded in `product-context/overview.md`, and `.uncovr/state.json`.
- The repository working tree.
- The delivery context: local skill root or Agensi listing and file index. Resolve all supporting files and scripts through *Execution modes* in SKILL.md; a package path is not necessarily a local file.

## Steps

1. Inspect README and manifest files, source tree, framework and test configuration, runtime entry points, routing, schema/migrations, CI and integration adapters. Skip build outputs, generated/vendor folders and secrets. Use `repository-signals.md`, next to this file, as the checklist of what to look for: record each signal found, and the signals looked for but not observed.
2. Record main modules, owners if explicit, external services, data stores, API/event contracts and likely capability boundaries. Distinguish files that are only infrastructure from business-bearing code. For each component, note its responsibility, its boundary (entry points and the data it owns), the main data flows in and out, and the external dependencies its code actually calls.
3. For each capability, identify potential entry points and tests. Prioritize central business workflows and branches with measurable behavior.
4. Read important paths only; sample dense modules before expanding scope. Record modules that cannot be inspected and why.
   When Git, Python and a terminal are available, resolve and run `scripts/history.py` against the repository root through *Execution modes* in SKILL.md. It is read-only and lists, per module, commits, churn, fix commits, ticket references, number of authors and last change. Use it to choose where to read first, and record the measured facts under *Regression hotspots* with `git` evidence naming the command, the revision and the module. It is not a risk score; a shallow clone understates it.
5. Write `product-context/architecture.md` with the template's sections and the verified inventory/technical baseline sections in `overview.md`. Record teams declared in CODEOWNERS under *Who can clarify* in `overview.md`, with the paths they review: path review, not business authority. Add provisional feature names to `features.md` only where supported. In `architecture.md`:
   - *Inspection boundary*: what was inspected (revision, paths, commands run with permission), what remains unknown, and which systems are external. Their internals are out of reach, not absent.
   - *Technology stack*: a compact table of the technologies that shape a change — technology, role, the constraint that matters and the claim ID. Do not list every library; one row may rest on a manifest or an import.
   - *Context and major components*: one row per component with responsibility, boundary, external dependencies and claim ID, then the main data flows for the scope.
   - *Deployment and environments*: keep apart configuration found in the repository, execution observed with `runtime` evidence, and production, which stays a `gap` claim until runtime evidence from that environment or a person confirms it. Record release, storage and compatibility limits only when a cited source states them.
   Every table row and every deployment statement cites a claim ID from `evidence.jsonl`; the Markdown never carries the provenance itself.
6. Create technical claims in `evidence.jsonl` and reference them from Markdown. Draw a diagram only as *Diagrams* in `evidence-contract.md` allows, from those claims. Use the contract in `evidence-contract.md`, next to this file.

## Guardrails

- A folder/class name is **not** proof of product purpose or user intent.
- Don't invent missing system integrations or architecture decisions; write a gap instead.
- For local source evidence, quote relative file path, line range when feasible, and HEAD revision. Avoid evidence paths that leave the repository.
- Mark assumptions as `inferred`.
- A checkout does not prove the version in production: the recorded revision, lockfiles and deployment files show what is configured, not what is deployed. Do not run builds, containers or the system to find out; ask first, as `SKILL.md` requires.
- The boundaries in `SKILL.md` apply.

## Completion

The PO should understand what areas exist, which ones were inspected, what is unknown or belongs to external systems, and where to investigate functional behavior next.
