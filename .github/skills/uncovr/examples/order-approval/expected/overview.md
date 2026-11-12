# Product Overview

## Purpose and users

Declared by the README, not confirmed by a person (CTX-001): employees raise purchase requests, a manager approves or rejects them, and finance approves requests above a limit. Other users, personas and the product's context are a gap.

## Product capabilities

Observed in the code:

- Approve a pending request (F-001).
- Reject a pending request (F-002).

Notifying the requester of a rejection is not implemented; the TODO is not a plan (F-003).

## Business objectives and unknowns

No source states objectives, expected value or success measures (CTX-002). The approval limit is contradicted (BR-002), and whether only managers may approve depends on callers outside the repository (CTX-003).

## Who can clarify

No source names a team or role to consult: no CODEOWNERS, contacts or ownership notes. The README names managers and finance as approving functions (CTX-001), not as contacts; the Product Owner designates who answers each question in `validation.md`.

## Baseline

- Revision: gap — the fixture has no Git metadata.
- Scope: whole repository (`src/`, `tests/`, `README.md`), confirmed by the Product Owner.
- Exclusions: none.
