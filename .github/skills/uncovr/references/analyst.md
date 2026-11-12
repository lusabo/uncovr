# Stage 2 — Analyst

## Goal

Translate observable application behavior into **PO-usable context**. Do not write product requirements for proposed future functionality.

## Inputs

- Explorer's output: `architecture.md`, provisional entries in `features.md` and `overview.md`, and its claims in `evidence.jsonl`.
- The confirmed scope and module batch, and the repository working tree.

## Steps

1. Start with Explorer's capability candidates and evidence references.
2. Trace major user/system actions through routes, services, domain functions, persistence and tests. Record triggers, preconditions, outcomes, failures, alternate paths and permissions. For claims about warnings, confirmations, visible actions or client-side blocking, inspect the UI path and its activation conditions as well as the backend. If that path is outside the confirmed scope, mark the interface as unreviewed and ask to confirm a scope extension; do not infer missing UI behavior from backend code alone.
3. Extract business vocabulary, central entities, states, invariants and rule conditions. Split complex rules into atomic claims with stable IDs (`F-001`, `BR-001`, `ARCH-001` etc.). Assertions that need different confidence levels or independent business decisions must be separate claims. When splitting existing claims, record the old-to-new ID mapping and preserve a decision only on the assertion it actually covered; undecided business rules remain `pending`. Follow the identity and decision rules in `evidence-contract.md`. Write each rule as trigger, preconditions, outcome and exceptions; validation and error messages help word it, the code that enforces it is the evidence. For each glossary term, keep the meaning observed in code apart from the business definition a document, interview or Product Owner answer states, and record where they differ.
4. For every substantive claim, add exactly one canonical JSONL record keyed by claim ID; a claim may have multiple distinct sources. Use `confidence` and `business_validation` as separate axes. Challenge universal and absence claims (such as "every", "always", "never" or "no"): look for alternate callers, direct state updates, background jobs, error paths and configuration branches within scope. Bound the assertion to the inspected paths and record exceptions or unreviewed paths. Emitting an event is not proof of downstream delivery.
5. Write `product-context/features.md`, `domain.md` and `traceability.md`, placing each finding as `repository-signals.md` (next to this file) directs: observed acceptance criteria from tests, variants, flags and parameters, background work, the permission matrix and sensitive data. Rate each feature's criticality: **high** when it moves money, controls access, handles personal or regulated data, meets a legal obligation or changes data irreversibly; **medium** when users depend on it daily; **low** otherwise. Criticality orders the questions and the regression gaps; it is a rating, not a business decision. Update `overview.md` only where supported: observed capabilities by feature ID; purpose, users, value and objectives only from a declared business source, as `assumption` claims, otherwise as gaps; roles or teams a source names, with their knowledge area and the questions they could help clarify. Follow *Declared intent, definitions and people* in `evidence-contract.md`. In `traceability.md`, name for each claim only the files its evidence cites; add the *Sources* view when documents, tickets, runtime observations, interviews or external references bear on a claim, marking each `consulted`, `indicated` or `inaccessible`, and never cite an unopened source as evidence. Add missing-domain questions to `validation.md`. Add a Mermaid diagram only where *Diagrams* in `evidence-contract.md` says it helps, drawn from claims already recorded. When tracing reveals a data flow, data store or external dependency that `architecture.md` lacks, add a claim and a focused row or flow there, without rewriting the Explorer's text; an external call proves the call, not what the other system does with it.
6. Detect conflicting representations: e.g. route says allowed, test says denied, comment says deprecated. Compare the same trigger, actor, state, configuration and revision before calling it a contradiction. A known exception or a different context is not automatically a conflict. Where supported facts about each source are separate claims, preserve them and record their material disagreement in a separate `contradicted` claim citing both sources; reuse an existing divergence ID when applicable. Keep the divergence consistent across the evidence index, affected Markdown and final counts, and give it a row under *Contradictions and review outcomes* in `validation.md`: claims involved, what each source says, impact, and the decision claim or `pending`. A human choice of desired behavior does not change the implementation evidence.

## Required claim structure

Each JSONL line contains `id`, `kind`, `summary`, `confidence`, `business_validation`, and `evidence` (array). Evidence entries use `type`, `ref`, optional `line_start`/`line_end`, and `revision` for Git-local sources. Allowed values and an example are in `evidence-contract.md`, next to this file.

`confirmed` means technically observed at a specific revision, not business-approved. `inferred` requires supporting evidence; `gap` may lack source; `contradicted` records opposing sources.

## Constraints

- Don't fabricate goals, stakeholders, user journeys or design rationale from identifier names.
- Don't turn existing behavior into business intent or a roadmap, and don't infer business authority or approval from CODEOWNERS, authors, contributors or repository accounts.
- Use `not_applicable` only with a reason; unknown intent is a `gap` and stays `pending`. Technical confidence and business validation are independent.
- Avoid dumping entire algorithms, model schemas and all endpoints; document product-relevant rules and impact surfaces.
- Never silently convert a bug, accidental behavior or TODO into approved future requirements.
- Tie each PO question to claim IDs and retain the premise's confidence and scope. Do not phrase an `inferred` or `gap` premise as a fact.
- Keep language legible to POs, adding implementation references only when needed for traceability.

## Completion

Each critical capability can be found in the catalogue; its rules, dependencies and unknowns are navigable by stable claim ID.
