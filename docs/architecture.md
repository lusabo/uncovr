# Uncovr architecture — minimal viable framework

## Design goal

Turn an existing codebase into a **Product Context Baseline** that a Product Owner can understand, validate, and reuse for the next product version.

```
source code + tests + config + Git history
                    |
              Orchestrator
                    |
             Explorer (map)
                    |
             Analyst (interpret)
                    |
             Validator (challenge)
                    |
     six Markdown artifacts + evidence.jsonl
                    |
       PO/SME questions and decisions
                    |
        future discovery / impact analysis
```

These are **four logical agent roles** in one skill, not four simultaneously-running services. The agent follows `SKILL.md` and its `references/` sequentially; the Validator runs in a separate context when the agent supports subagents (in VS Code, the `Uncovr Validator` agent). The order and the two checkpoints (scope, baseline review) are followed by instruction; no engine enforces them. A single session is sufficient for a small repository; larger codebases should be reviewed module by module and resumed using `.uncovr/state.json`.

## Distribution

- `.github/skills/uncovr/`: the single source of the skill — `SKILL.md`, `references/` (stages, evidence contract, repository signals), `assets/`, `scripts/check.py`, `scripts/history.py` and `scripts/okf.py`, `examples/`, `evals/`. Paths inside it are relative to the skill, so it works wherever it is installed or served.
- `.github/agents/uncovr.agent.md` and `uncovr-validator.agent.md`: VS Code only; entry point and Validator subagent.
- `uncovr.py`: standard-library CLI. `install` copies the skill (without `examples/` and `evals/`) and the agents into a repository and records `.uncovr/manifest.json`; `status` reports drift; `check` reuses `scripts/check.py`; `pack` writes `dist/uncovr.zip` for the Agensi marketplace (one top folder, text only; agents excluded, since Agensi sells skills only).
- `docs/`: architecture, acceptance and an example walkthrough for maintainers.

No database, API server, hosted LLM, MCP server, project-code mutation, or framework-specific CLI is required for v0.3. Agent model inference and repository traversal depend on the user's chosen agent runtime.

## State versus product knowledge

`.uncovr/state.json` is an operational checkpoint, not a canonical product fact. It holds phase, baseline revision, inspected modules, last validation date and the chosen wiki target. The six Markdown artifacts are the reader-facing context; `evidence.jsonl` is the canonical claim provenance index. Git versioning provides history.

`product-context/wiki/` is a derived view: `scripts/okf.py` rebuilds it from the artifacts and `evidence.jsonl` as an Open Knowledge Format v0.2 bundle. Claim kind maps to the OKF `type`, evidence to `sources` with footnotes, a human approval to `verified` (`human:` actor), pending or approved to `status`; `confidence`, `business_validation` and the Git revision stay as extension keys, because OKF has no field for confidence and `stale_after` is a date, not a revision. The target — Obsidian, MkDocs or Google Knowledge Catalog — only changes link style, aliases and the MkDocs config. The export never publishes to a service.

## Limitations

- The CLI is not an automatic static analyzer: it cannot reconstruct rules without an AI agent or human investigation.
- Completeness cannot be inferred from counts of files, claims, or tests.
- Technical proof of behavior does not establish why it was intended or whether it should persist.
- Changes to source after the recorded revision require a new check and possibly updated evidence.
- Runtime-only and third-party integrations may remain unknown until appropriately authorized investigation.

## Planned evolution

A later `impact` workflow can consume the baseline to identify candidate affected features, rules, modules and missing evidence for a proposed change. It must never automatically convert a guess into an approved requirement or generate code in the baseline phase.
