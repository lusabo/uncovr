# Stage 3 — Validator

## Goal

Challenge generated content as an **independent reviewer**, not a document polisher. Structural tool checks are necessary but not sufficient. Run in a context separate from the analysis whenever the agent allows it (`SKILL.md`, step 4).

## Inputs

- The six artifacts under `product-context/` and `evidence.jsonl` as written by the Explorer and Analyst.
- The recorded Git HEAD SHA, the confirmed scope, and the repository working tree.
- The delivery context: local skill root or Agensi listing and file index, plus the *Execution modes* and *Inputs and boundaries* from SKILL.md. Resolve supporting files and scripts through that contract; do not install the skill to review the baseline.

## Review protocol

Four checks, in this order:

1. **Correctness.** Re-open the claimed file, lines, tests and revision rather than trusting the Analyst's prose. Flag stale paths, dirty-tree ambiguity, unexecuted assumptions and misleading assertions. Downgrade unsupported `confirmed` to `inferred` or `gap`, with reasons. UI claims require the client path, templates and activation conditions, not just backend evidence. An excluded interface is unreviewed, not proof of a missing warning or restriction; request a scope extension before inspecting it. Try to falsify universal and absence claims with alternate callers, direct state updates, background jobs, error paths and configuration branches within scope. Record exceptions and distinguish event emission from downstream delivery. In `architecture.md`, check that each stack and component row cites a claim whose evidence supports it, that the stack stays compact, and that deployment keeps configuration found, execution observed and production apart: a checkout does not prove the version in production, so a production statement without `runtime` evidence from that environment is a `gap`. Remove release, storage or compatibility limits that no cited source states.
2. **Consistency.** Check each Mermaid diagram against the claims it cites: no node, edge, order, transition or cardinality they do not support, inferred edges marked, gaps undrawn; remove a diagram that adds nothing to the text. Compare across features, rules, permissions, states and architecture: contradictory permissions, incompatible state transitions, a parameter documented with one value and coded with another. Compare like-for-like contexts and follow the source-conflict protocol in `evidence-contract.md`; known exceptions are not automatically contradictions. Where material sources conflict, use `contradicted`; don't resolve arbitrarily or relabel supported source facts merely to change the totals.
3. **Traceability.** Check `traceability.md`: feature → rules → source/test and source → impacted features. Every high-criticality feature has rules and test evidence, or a recorded gap. The files named for a claim are those its evidence cites. In the *Sources* view, re-open what is marked `consulted`; a source that was only `indicated` or is `inaccessible` must not appear as evidence, and a document or ticket must not be the only support of an implemented behavior.
4. **Completeness.** Every signal in `repository-signals.md` is either recorded or marked as not observed; uncovered modules and alternative paths are listed under *Reviewed scope*. The *Inspection boundary* in `architecture.md` agrees with that scope and names what is unknown and which systems are external.

Then:

5. Separate technical confirmation from current business legitimacy. Check atomic claims and scoped decisions against `evidence-contract.md`: different confidence levels or independent human decisions must not share one claim. Verify that a partial decision has not spread approval or rejection to undecided assertions. Ask targeted questions to PO/SME about intent, exceptions, roles and product goals, citing claim IDs and retaining uncertainty in each premise. Put first the questions that block a proposed change, then those about high-criticality features. In `overview.md` and the glossary, check that observed capabilities and meanings are not presented as declared purpose, value, objectives or definitions; that every declared statement cites its business source and stays `pending` until a person decides; that unknowns are gaps; that `not_applicable` has a reason; and that no role, team or person is given business authority because of CODEOWNERS or repository history. The Product Owner designates who decides each question.
6. Update `validation.md` with findings, references to decision claims, review dates and exclusions; who decided and when stay in `evidence.jsonl`. Record approvals only as the boundaries in `SKILL.md` allow. Reconcile conflicts in prose with the canonical evidence index and the affected Markdown; do not report no material contradictions while documenting an unresolved source disagreement. A decision about desired behavior is not evidence that the implementation changed. Keep open questions and recorded decisions apart, following *Sources, decisions and reopening* in `evidence-contract.md`: a decision is listed only when a `decision` claim records the person's answer; never edit or delete one; reopen it only for new evidence bearing on the decided case, recorded as its own claim and cited as the reason.
7. When Python and a terminal are available, resolve and run `scripts/check.py` against the repository root through *Execution modes* in SKILL.md. Otherwise record that the check was not run. Report errors, warnings, claim counts, and the limits of structural checking. Derive confidence counts from the canonical index and keep review verdict counts separate.

## Review verdicts

- **Technically grounded**: local source or observable runtime evidence supports behavior for stated revision.
- **Needs clarification**: credible inference but intent or behavior remains uncertain.
- **Contradictory**: two sources disagree; PO and engineering should arbitrate.
- **Not reviewed**: no inspection performed; never imply coverage.

Never report a percentage of "business correctness" from Markdown completeness, claim counts, or an LLM score.

## Completion

Every claim in scope has been re-opened and carries one of the verdicts above; `validation.md` lists the findings and the prioritised questions; the structural check has run (or its absence is recorded). Hand back for the baseline-review checkpoint (`SKILL.md`, step 6).
