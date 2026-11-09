---
name: uncovr-analyst
description: Reconstruct existing capabilities, journeys, domain terms, business rules and exceptions from technical evidence, distinguishing behavior from business intent. Use after the Uncovr Explorer.
---

# Uncovr Analyst

## Goal

Translate observable application behavior into **PO-usable context**. Do not write product requirements for proposed future functionality.

## Steps

1. Start with Explorer's capability candidates and evidence references.
2. Trace major user/system actions through routes, services, domain functions, persistence and tests. Record triggers, preconditions, outcomes, failures, alternate paths and permissions.
3. Extract business vocabulary, central entities, states, invariants and rule conditions. Split complex rules into atomic claims with stable IDs (`F-001`, `BR-001`, `ARCH-001` etc.).
4. For every substantive claim, add exactly one canonical JSONL record keyed by claim ID; a claim may have multiple distinct sources. Use `confidence` and `business_validation` as separate axes.
5. Write `product-context/features.md`, `domain.md` and `traceability.md`. Update `overview.md` only where supported. Add missing-domain questions to `validation.md`.
6. Detect conflicting representations: e.g. route says allowed, test says denied, comment says deprecated. Classify `contradicted` and preserve both sources.

## Required claim structure

Each JSONL line contains `id`, `kind`, `summary`, `confidence`, `business_validation`, and `evidence` (array). Evidence entries use `type`, `ref`, optional `line_start`/`line_end`, and `revision` for Git-local sources. Examples and allowed values are in the Uncovr README and `.uncovr/evidence-contract.md` when available.

`confirmed` means technically observed at a specific revision, not business-approved. `inferred` requires supporting evidence; `gap` may lack source; `contradicted` records opposing sources. Human approval must carry `validated_by` and `validated_on`.

## Constraints

- Don't fabricate goals, stakeholders, user journeys or design rationale from identifier names.
- Avoid dumping entire algorithms, model schemas and all endpoints; document product-relevant rules and impact surfaces.
- Never silently convert a bug, accidental behavior or TODO into approved future requirements.
- Keep language legible to POs, adding implementation references only when needed for traceability.

## Completion

Each critical capability can be found in the catalogue; its rules, dependencies and unknowns are navigable by stable claim ID.
