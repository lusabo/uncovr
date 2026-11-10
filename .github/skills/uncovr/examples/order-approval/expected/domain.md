# Domain Model and Business Rules

## Glossary

- **Request**: a purchase request with an amount, a requester and a status.
- **Approver**: the person deciding a request, identified by an address.

## Central entities and relationships

A request belongs to one requester and is decided by one approver.

## Rules

| ID | Rule | Confidence |
| --- | --- | --- |
| BR-001 | A requester cannot approve their own request. | confirmed |
| BR-002 | Above the approval limit, only a finance approver may approve; the limit is 5000 in code, 10 000 in the README. | contradicted |
| BR-003 | Only a pending request can be approved or rejected. | confirmed |
| BR-004 | A requester can reject their own request (no check in reject). | confirmed |

## States and permissions

`pending` → `approved` or `rejected` (BR-003). Permissions: BR-001, BR-002, BR-004.
