# Architecture for Product Evolution

## Inspection boundary

- Inspected: the whole repository — `src/requests.py`, `tests/test_requests.py` and `README.md`. Revision not pinned (no Git metadata). Nothing was executed, the tests included (ARCH-004).
- Unknown: the Python version, the callers of `approve()` and `reject()`, and whether and where the code is deployed (ARCH-004).
- External systems: none called from the code (ARCH-001). The requester notification the TODO mentions does not exist (F-003).

## Technology stack

| Technology | Role in the system | Relevant constraint | Claim ID |
| --- | --- | --- | --- |
| Python, standard library only | Request logic and its `unittest` tests | No Python version declared (ARCH-004); no third-party dependency to upgrade or license | ARCH-003 |

## Context and major components

| Component | Responsibility | Boundary (entry points, owned data) | External dependencies | Claim ID |
| --- | --- | --- | --- | --- |
| `src/requests.py` | Request entity; approve and reject with the status, self-approval and limit checks (BR-001, BR-002, BR-003) | `approve()` and `reject()`; owns `Request.status` in memory, no persistence | None | ARCH-001 |

### Main data flows

1. Caller → `approve(request, approver)` → status, self-approval and limit checks → `request.status` set to `approved` in memory (F-001).
2. Caller → `reject(request, approver)` → status check → `request.status` set to `rejected`; nothing leaves the module (F-002, F-003).

## Integration contracts

None observed (ARCH-001).

## Deployment and environments

- Configuration found: none — no Dockerfile, CI, packaging or infrastructure files (ARCH-004).
- Execution observed: none; the tests were not run (ARCH-004).
- Production not confirmed: whether, where and at which revision the code runs is unknown (ARCH-004).
- Release, storage and compatibility limits: none stated by a source; requests live only in memory (ARCH-001).

## Change constraints

The approval limit is a hard-coded module constant; its intended value is contradicted (BR-002). No third-party dependencies (ARCH-003).

## Known debt

`TODO: notify the requester` in `reject()` (F-003).

## Regression hotspots

The finance limit and the rejection path have no direct test (ARCH-002). Change history not measured: the example has no Git metadata.
