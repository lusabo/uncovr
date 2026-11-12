# Architecture for Product Evolution

<!-- TODO: Describe boundaries and impact-relevant dependencies; avoid exhaustive class-level documentation. Every row and statement cites claim IDs from evidence.jsonl. -->

## Inspection boundary
- Inspected: revision, dirty tree, paths and configuration read; commands run, if any, with permission.
- Unknown: what the sources cannot show, as `gap` claims.
- External systems: services, stores and consumers outside the repository; their internals are not reviewed.

A checkout shows what is configured at a revision, not what runs in production.

## Technology stack
Only technologies that shape a change: runtime, framework, data store, messaging, build and deploy. Not a library inventory.

| Technology | Role in the system | Relevant constraint | Claim ID |
| --- | --- | --- | --- |
| Pending | Unknown | Unknown | Pending |

## Context and major components
Applications, services, data stores, queues and external actors, each with its responsibility and boundary.

| Component | Responsibility | Boundary (entry points, owned data) | External dependencies | Claim ID |
| --- | --- | --- | --- | --- |
| Pending | Unknown | Unknown | Unknown | Pending |

### Main data flows
Source → component → store or external system, for the flows that matter to the scope; cite claim IDs. A Mermaid `flowchart` may show components, boundaries and flows when a list is harder to follow; follow *Diagrams* in the evidence contract.

## Integration contracts
Record inbound/outbound APIs, authentication, events, data ownership and compatibility constraints.

## Deployment and environments
- Configuration found: deployment units, environments and pipelines as configured in the repository at the recorded revision.
- Execution observed: what was run or observed, where, when and how (`runtime` evidence); otherwise "nothing executed".
- Production not confirmed: deployed version, topology and settings stay a `gap` until runtime evidence or a person confirms them.
- Release, storage and compatibility limits: only those a cited source supports.

## Change constraints
Explain technology, dependency, licence, data or deployment restrictions when they matter to future changes.

## Known debt
TODO and FIXME markers, deprecations, suppressed checks and dead flags. Debt is a risk, never a requirement.

## Regression hotspots
Link affected claims, components and test evidence, and the change history from `scripts/history.py` when available; do not fabricate risk scoring.
