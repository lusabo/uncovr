# Architecture for Product Evolution

## Context and major components

One module, `src/requests.py`, holds the request entity and the approve and reject operations (ARCH-001). There is no persistence, API or notification channel.

## Integration contracts

None observed (ARCH-001).

## Change constraints

The approval limit is a module constant; its intended value is contradicted (BR-002).

## Regression hotspots

The finance limit and the rejection path have no direct test (ARCH-002).
