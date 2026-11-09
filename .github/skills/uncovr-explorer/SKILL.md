---
name: uncovr-explorer
description: Inventory an existing repository and identify high-level product capabilities, components, integrations and source/test entry points with code evidence. Use as the first stage of Uncovr reconstruction.
---

# Uncovr Explorer

## Goal

Create a **targeted map** of the system, not a file-by-file catalogue. Focus on product behavior and technical boundaries needed for assessing future changes.

## Steps

1. Inspect README and manifest files, source tree, framework and test configuration, runtime entry points, routing, schema/migrations, CI and integration adapters. Skip build outputs, generated/vendor folders and secrets.
2. Record main modules, owners if explicit, external services, data stores, API/event contracts and likely capability boundaries. Distinguish files that are only infrastructure from business-bearing code.
3. For each capability, identify potential entry points and tests. Prioritize central business workflows and branches with measurable behavior.
4. Read important paths only; sample dense modules before expanding scope. Record modules that cannot be inspected and why.
5. Write `product-context/architecture.md` and the verified inventory/technical baseline sections in `overview.md`. Add provisional feature names to `features.md` only where supported.
6. Create technical claims in `evidence.jsonl` and reference them from Markdown. Use the contract described in `.uncovr/evidence-contract.md` (installed copies can use README or the evidence examples in skill notes).

## Guardrails

- A folder/class name is **not** proof of product purpose or user intent.
- Don't invent missing system integrations or architecture decisions; write a gap instead.
- For local source evidence, quote relative file path, line range when feasible, and HEAD revision. Avoid evidence paths that leave the repository.
- Mark assumptions as `inferred`; never make business intent `approved` based on source alone.
- Do not change source code or run migrations/deployment.

## Completion

The PO should understand what areas exist, which ones were inspected and where to investigate functional behavior next.
