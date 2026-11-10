# Bidirectional Traceability

| Claim | Source | Test |
| --- | --- | --- |
| F-001 | `src/requests.py` 14–22 | `tests/test_requests.py` 7–9 |
| F-002 | `src/requests.py` 25–30 | none |
| BR-001 | `src/requests.py` 17–18 | `tests/test_requests.py` 11–13 |
| BR-002 | `src/requests.py` 3, 19–20; `README.md` | none |
| BR-003 | `src/requests.py` 15–16, 27–28 | `tests/test_requests.py` 15–18 |
| BR-004 | `src/requests.py` 25–30 | none |

## Procedure for future change requests

Find the affected rule IDs above, then the module and tests listed for them; a rule without a test needs one before the change (ARCH-002).

## Coverage and known blind spots

Whole repository reviewed. No test for BR-002 or F-002 (ARCH-002).
