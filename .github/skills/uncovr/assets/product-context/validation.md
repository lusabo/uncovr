# Validation, Confidence and Open Questions

<!-- TODO: Review evidence and record targeted questions for humans; do not approve business intent on their behalf. Tables here reference claim IDs; who decided and when stay in evidence.jsonl. -->

## Confidence
- confirmed: technical behavior directly evidenced; not necessarily business-approved
- inferred: plausible interpretation from partial technical signals
- gap: insufficient support for a statement
- contradicted: sources conflict

## Outstanding questions
Open questions only, blocking ones first. A question answered by a person moves to *Decisions*; a reopened decision comes back here citing the decision and the new evidence.

| Claim ID | Question | Impact | Decision owner | Status |
| --- | --- | --- | --- | --- |
| Pending | Unknown | Unknown | PO/SME | Open |

## Decisions
Human decisions recorded as `decision` claims in `evidence.jsonl`, never removed. Write "None recorded." when there are none.

| Decision claim | Covers | Outcome | Status | Reopening reason |
| --- | --- | --- | --- | --- |
| Pending | Pending | Unknown | in force | — |

Status is `in force`, `reopened` (new evidence, cited by claim ID, bears on the decided case) or `superseded by <ID>`.

## Contradictions and review outcomes
One row per `contradicted` claim, then rejected assertions, downgrades and review dates.

| Divergence | Claims involved | Source positions | Impact | Decision or status |
| --- | --- | --- | --- | --- |
| Pending | Pending | Unknown | Unknown | pending |

A decision settles the desired behavior, not the mismatch: the row stays until fresh evidence shows the sources agree.

## Reviewed scope
Specify examined modules, evidence freshness and excluded or unverified areas.
