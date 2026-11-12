# Validation, Confidence and Open Questions

## Confidence

Confirmed: ARCH-001, ARCH-002, ARCH-003, F-001, F-002, BR-001, BR-003, BR-004. Inferred: CTX-001, CTX-003. Gap: F-003, ARCH-004, CTX-002. Contradicted: BR-002. No claim is business-approved.

ARCH-001 to ARCH-003 are `not_applicable` for business validation: they state the module layout, the tests' scope and the standard-library stack, which no business decision approves. Every other claim is `pending`, the README's declarations (CTX-001, CTX-003) included.

## Outstanding questions

| Claim ID | Question | Impact | Decision owner | Status |
| --- | --- | --- | --- | --- |
| BR-002 | Is the finance limit 5000, as the code says, or 10 000, as the README says? Does an `@finance` address identify the finance function? | Blocks any change to approvals | Product Owner, with engineering | Open |
| CTX-003 | Must the approver be a manager, as the README says? The code accepts anyone other than the requester; is a manager check expected elsewhere? | Who may authorise spending | Product Owner | Open |
| BR-004 | May a requester reject their own request, or should rejecting follow BR-001? | Possible unintended asymmetry | Product Owner | Open |
| F-003 | Should the requester be notified of a rejection, and how? | Unfinished feature | Product Owner | Open |
| ARCH-004 | Is this code deployed, and if so where, on which Python version and at which revision? The repository cannot show it. | Whether findings describe production | Engineering | Open |
| CTX-001, CTX-002 | Does the README's description of purpose and users still hold, and what is the product expected to achieve? | Framing of every future change | Product Owner | Open |

## Decisions

None recorded. No person has answered a question yet.

## Contradictions and review outcomes

| Divergence | Claims involved | Source positions | Impact | Decision or status |
| --- | --- | --- | --- | --- |
| Finance approval limit | BR-002 | Code (`src/requests.py`): above 5000 needs an `@finance` approver. README: above 10 000 needs finance. | Requests between 5000 and 10 000 follow the code, which may not be the intended rule | pending: question BR-002 |

- ARCH-002 — the finance limit, rejection and BR-004 have no regression test.

## Reviewed scope

Whole repository; no exclusions; no blocked stage. Revision not pinned (no Git metadata). Nothing executed; production not confirmed (ARCH-004).
