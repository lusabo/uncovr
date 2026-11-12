# Bidirectional Traceability

| Claim ID | Feature or rule | Source files | Tests | Related claims | Impact note |
| --- | --- | --- | --- | --- | --- |
| F-001 | Approve a pending request | `src/requests.py` | `tests/test_requests.py` | BR-001, BR-002, BR-003 | Authorises spending; any change touches the three rules |
| F-002 | Reject a pending request | `src/requests.py` | none | BR-003, BR-004 | Untested (ARCH-002) |
| BR-001 | Requester cannot approve own request | `src/requests.py` | `tests/test_requests.py` | F-001, BR-004 | Rejection does not apply it (BR-004) |
| BR-002 | Finance approves above the limit | `src/requests.py`, `README.md` | none | F-001 | Limit disputed; untested |
| BR-003 | Only pending requests change status | `src/requests.py` | `tests/test_requests.py` | F-001, F-002 | Shared by approve and reject |
| BR-004 | Anyone may reject, the requester included | `src/requests.py` | none | F-002, BR-001 | Untested; may be unintended |

Line ranges and the revision of each reference are in `evidence.jsonl`.

## Sources

| Source | Purpose | Scope consulted | Version or date | Status | Claim IDs |
| --- | --- | --- | --- | --- | --- |
| `src/requests.py` | Implemented behavior | Whole file | Unknown: no Git metadata | consulted | ARCH-001, ARCH-003, F-001, F-002, F-003, BR-001, BR-002, BR-003, BR-004, CTX-003 |
| `tests/test_requests.py` | Tested behavior | Whole file | Unknown: no Git metadata | consulted | ARCH-002, ARCH-003, F-001, BR-001, BR-003 |
| `README.md` | Declared purpose, users and finance limit | Section *Purchase requests* | Unknown: no Git metadata | consulted | CTX-001, CTX-003, BR-002 |

No external source is indicated or consulted: the README links nothing, and no ticket, specification or deployment record was supplied. The README states intent; it does not show what the code does.

## Procedure for future change requests

Find the affected rule IDs above, then the module and tests listed for them; a rule without a test needs one before the change (ARCH-002).

## Coverage and known blind spots

Whole repository reviewed. No test for BR-002, BR-004 or F-002 (ARCH-002). Nothing outside the repository was consulted, so deployment stays a gap (ARCH-004).
