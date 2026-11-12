# Product Overview

<!-- TODO: Reconstruct only what sources support; label unknown business intent explicitly. -->

What the code does and what the business says it is for are kept apart. A capability is not a purpose, a value or a plan.

## Purpose and users
Declared only: the purpose, intended users and value as a cited business source states them — a document, an interview or a Product Owner answer — with its claim ID. Such a claim is `inferred` at most and `pending` until a person confirms it. Actors seen in the code belong in `domain.md` → *Permissions*. Where no source states them, write that they are a gap and cite the gap claim. Do not invent personas or goals.

## Product capabilities
Observed only: what the code does in the reviewed scope, one line per feature ID from `features.md`. Do not word a capability as a goal, a benefit or a plan; a TODO, a disabled flag or an unused route is not a roadmap item.

## Business objectives and unknowns
Declared objectives and expected value, each with its source and claim ID. Analytics events and documents are clues (`inferred`), not confirmation. Then the unknowns, as `gap` claims tied to questions in `validation.md`.

## Who can clarify
Roles or teams a source names — CODEOWNERS teams, documented contacts, a Product Owner answer — as a table of role or team, knowledge area, questions they could help clarify (claim IDs) and source. Without such a source, say so in one line.

CODEOWNERS declares who reviews paths, not who holds business authority. Never list commit authors, contributors or repository accounts, and never infer from them who may decide or approve. The Product Owner designates who decides each question.

## Baseline
- Repository: unknown
- Git revision: unknown
- Scope and exclusions: unknown
- Last reviewed: unknown
