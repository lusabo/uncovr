# Domain Model and Business Rules

## Glossary

- **Request**: a purchase request with an amount, a requester and a status.
- **Approver**: the person deciding a request, identified by an address.

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

Roles are inferred from addresses; there is no role model in the code (ARCH-001).

## Sensitive data

| Entity.field | Category | Stored in | Retention or deletion | Evidence claim |
| --- | --- | --- | --- | --- |
| Request.requester | personal (e-mail address) | memory only | none observed | ARCH-001 |
| approver (argument) | personal (e-mail address) | not stored | — | ARCH-001 |
