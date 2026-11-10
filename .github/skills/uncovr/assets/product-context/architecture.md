# Architecture for Product Evolution

<!-- TODO: Describe boundaries and impact-relevant dependencies; avoid exhaustive class-level documentation. -->

## Context and major components
Describe applications, services, data stores, queues, and external actors.

## Integration contracts
Record inbound/outbound APIs, authentication, events, data ownership and compatibility constraints.

## Deployment and environments
Deployment units, environments and pipelines as configured in the repository; what actually runs in production is a gap until confirmed.

## Change constraints
Explain technology, dependency, licence, data or deployment restrictions when they matter to future changes.

## Known debt
TODO and FIXME markers, deprecations, suppressed checks and dead flags. Debt is a risk, never a requirement.

## Regression hotspots
Link affected claims, components and test evidence, and the change history from `scripts/history.py` when available; do not fabricate risk scoring.
