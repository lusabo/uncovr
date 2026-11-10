# Architecture for Product Evolution

## Context and major components

One module, `src/requests.py`, holds the request entity and the approve and reject operations (ARCH-001). There is no persistence, API or notification channel.

## Integration contracts

None observed (ARCH-001).

## Deployment and environments

Not observed: no Dockerfile, CI, infrastructure or deployment configuration in the repository (ARCH-001).

## Change constraints

The approval limit is a hard-coded module constant; its intended value is contradicted (BR-002). No third-party dependencies.

## Known debt

`TODO: notify the requester` in `reject()` (F-003).

## Regression hotspots

The finance limit and the rejection path have no direct test (ARCH-002). Change history not measured: the example has no Git metadata.
