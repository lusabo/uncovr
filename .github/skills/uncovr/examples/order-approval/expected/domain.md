# Domain Model and Business Rules

## Glossary

| Term | Meaning observed in code | Business definition | Ambiguity | Claim IDs |
| --- | --- | --- | --- | --- |
| Request | An in-memory object with an ID, an amount, a requester and a status | A purchase request raised by an employee (README, not confirmed) | The currency of the amount is a gap | ARCH-001, CTX-001 |
| Requester | The string compared with the approver; tests use e-mail-like addresses | An employee (README, not confirmed) | None known | BR-001, CTX-001 |
| Approver | Any string other than the requester; above the limit, one ending in `@finance` | A manager (README, not confirmed) | The code checks no manager role | BR-001, BR-002, CTX-003 |
| Finance approver | An approver whose address ends in `@finance` | "Approval from finance", without saying who belongs to finance | Whether the address suffix is how finance is identified | BR-002 |
| Approval limit | Amounts strictly above 5000 need a finance approver | Requests above 10 000 need finance (README) | Contradicted: 5000 in code, 10 000 in the README | BR-002 |
| Status | `pending`, then `approved` or `rejected` | Gap: no source defines the statuses | None known | BR-003 |

## Central entities and relationships

A request belongs to one requester and is decided by one approver.

## Rules

| Rule ID | Trigger | Preconditions | Outcome | Exceptions | Evidence claim | Business validation |
| --- | --- | --- | --- | --- | --- | --- |
| BR-001 | Approve | Approver is not the requester | Approved | Refused for the requester | BR-001 | pending |
| BR-002 | Approve | Amount ≤ limit, or approver address ends in `@finance` | Approved | Refused above the limit; limit is 5000 in code, 10 000 in the README | BR-002 | pending |
| BR-003 | Approve or reject | Status is `pending` | Approved or rejected | Refused otherwise | BR-003 | pending |
| BR-004 | Reject | Status is `pending` | Rejected | None: anyone, the requester included, may reject | BR-004 | pending |

## States

`pending` → `approved` or `rejected`; no transition out of either (BR-003).

## Permissions

| Role | Action | Allowed | Condition | Evidence claim |
| --- | --- | --- | --- | --- |
| Requester | Approve own request | no | — | BR-001 |
| Requester | Reject own request | yes | pending | BR-004 |
| Approver | Approve | yes | amount ≤ limit | BR-002 |
| Finance approver (`@finance`) | Approve | yes | any amount | BR-002 |
| Any person | Reject | yes | pending | BR-004 |

Roles are inferred from addresses; there is no role model in the code (ARCH-001). Whether only managers may approve is open (CTX-003).

## Sensitive data

| Entity.field | Category | Stored in | Retention or deletion | Evidence claim |
| --- | --- | --- | --- | --- |
| Request.requester | personal (e-mail address) | memory only | none observed | ARCH-001 |
| approver (argument) | personal (e-mail address) | not stored | — | ARCH-001 |
