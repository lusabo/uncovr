# Stage 3 — Validator

## Goal

Challenge generated content as an **independent reviewer**, not a document polisher. Structural tool checks are necessary but not sufficient. Run in a context separate from the analysis whenever the agent allows it (`SKILL.md`, step 4).

## Inputs

- The six artifacts under `product-context/` and `evidence.jsonl` as written by the Explorer and Analyst.
- The recorded Git HEAD SHA, the confirmed scope, and the repository working tree.

## Review protocol

Four checks, in this order:

1. **Correctness.** Re-open the claimed file, lines, tests and revision rather than trusting the Analyst's prose. Flag stale paths, dirty-tree ambiguity, unexecuted assumptions and misleading assertions. Downgrade unsupported `confirmed` to `inferred` or `gap`, with reasons.
2. **Consistency.** Compare across features, rules, permissions, states and architecture: contradictory permissions, incompatible state transitions, a parameter documented with one value and coded with another. Where sources conflict, use `contradicted`; don't resolve arbitrarily.
3. **Traceability.** Check `traceability.md`: feature → rules → source/test and source → impacted features. Every high-criticality feature has rules and test evidence, or a recorded gap.
4. **Completeness.** Every signal in `repository-signals.md` is either recorded or marked as not observed; uncovered modules and alternative paths are listed under *Reviewed scope*.

Then:

5. Separate technical confirmation from current business legitimacy. Ask targeted questions to PO/SME about intent, exceptions, roles and product goals. Put first the questions that block a proposed change, then those about high-criticality features.
6. Update `validation.md` with findings, decisions, reviewers, dates and exclusions. Record approvals only as the boundaries in `SKILL.md` allow.
7. Run `python3 scripts/check.py <repository root>` (the skill's script) when possible. Report errors, warnings, claim counts, and the limits of structural checking.

## Review verdicts

- **Technically grounded**: local source or observable runtime evidence supports behavior for stated revision.
- **Needs clarification**: credible inference but intent or behavior remains uncertain.
- **Contradictory**: two sources disagree; PO and engineering should arbitrate.
- **Not reviewed**: no inspection performed; never imply coverage.

Never report a percentage of "business correctness" from Markdown completeness, claim counts, or an LLM score.

## Completion

Every claim in scope has been re-opened and carries one of the verdicts above; `validation.md` lists the findings and the prioritised questions; the structural check has run (or its absence is recorded). Hand back for the baseline-review checkpoint (`SKILL.md`, step 6).
