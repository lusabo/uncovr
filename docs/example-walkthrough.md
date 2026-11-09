# Example: preparing a new version

Suppose a legacy request-management application exists and a PO asks:

> Let managers delegate approvals while they are away.

**Explorer** identifies approval routes, authorization middleware, persistence models, notifications and tests; all supported by repository paths. **Analyst** traces the current approval journey, rules and exceptions, assigns stable IDs, and records claims in JSONL. **Validator** rechecks the paths, challenges inferences, identifies missing tests and asks whether delegating approval is legally or operationally acceptable.

Example future impact analysis (not a requirement or approved design):

| Existing element | Possible consequence | Required next action |
| --- | --- | --- |
| Authorization rule `BR-001` | Delegated actor may need explicit permission | Validate policy with business and security |
| Approval feature `F-002` | New delegated approval pathway | Review journey and exception conditions |
| Notifications `F-003` | Original manager may need notification | Confirm intended communication |
| Audit trail `ARCH-004` | Delegator and delegate may require separate attribution | Ask compliance/security |

If rules are not evidenced, they must remain inferred or gaps. The baseline does not decide to implement the change; it makes discovery and specification safer.
