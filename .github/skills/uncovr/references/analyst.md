# Stage 2 — Analyst

## Goal

Translate observable application behavior into **PO-usable context**. Do not write product requirements for proposed future functionality.

## Inputs

- Explorer's output: `architecture.md`, provisional entries in `features.md` and `overview.md`, and its claims in `evidence.jsonl`.
- The confirmed scope and module batch, and the repository working tree.

## Steps

1. Start with Explorer's capability candidates and evidence references.
2. Trace major user/system actions through routes, services, domain functions, persistence and tests. Record triggers, preconditions, outcomes, failures, alternate paths and permissions.
3. Extract business vocabulary, central entities, states, invariants and rule conditions. Split complex rules into atomic claims with stable IDs (`F-001`, `BR-001`, `ARCH-001` etc.). Write each rule as trigger, preconditions, outcome and exceptions; validation and error messages help word it, the code that enforces it is the evidence.
4. For every substantive claim, add exactly one canonical JSONL record keyed by claim ID; a claim may have multiple distinct sources. Use `confidence` and `business_validation` as separate axes.
5. Write `product-context/features.md`, `domain.md` and `traceability.md`, placing each finding as `repository-signals.md` (next to this file) directs: observed acceptance criteria from tests, variants, flags and parameters, background work, the permission matrix and sensitive data. Rate each feature's criticality: **high** when it moves money, controls access, handles personal or regulated data, meets a legal obligation or changes data irreversibly; **medium** when users depend on it daily; **low** otherwise. Criticality orders the questions and the regression gaps; it is a rating, not a business decision. Update `overview.md` only where supported. Add missing-domain questions to `validation.md`.
6. Detect conflicting representations: e.g. route says allowed, test says denied, comment says deprecated. Classify `contradicted` and preserve both sources.

## Required claim structure

Each JSONL line contains `id`, `kind`, `summary`, `confidence`, `business_validation`, and `evidence` (array). Evidence entries use `type`, `ref`, optional `line_start`/`line_end`, and `revision` for Git-local sources. Allowed values and an example are in `evidence-contract.md`, next to this file.

`confirmed` means technically observed at a specific revision, not business-approved. `inferred` requires supporting evidence; `gap` may lack source; `contradicted` records opposing sources.

## Constraints

- Don't fabricate goals, stakeholders, user journeys or design rationale from identifier names.
- Avoid dumping entire algorithms, model schemas and all endpoints; document product-relevant rules and impact surfaces.
- Never silently convert a bug, accidental behavior or TODO into approved future requirements.
- Keep language legible to POs, adding implementation references only when needed for traceability.

## Completion

Each critical capability can be found in the catalogue; its rules, dependencies and unknowns are navigable by stable claim ID.
