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

These are **four logical agent roles**, not four simultaneously-running services. By default, the host agent follows the skills sequentially. A single session is sufficient for a small repository; larger codebases should be reviewed module by module and resumed using `.uncovr/state.json`.

## Distribution

- `.github/skills/uncovr-{orchestrator,explorer,analyst,validator}/SKILL.md`: portable Agent Skills, intentionally using only a minimal frontmatter contract.
- `.github/agents/uncovr.agent.md`: optional explicit entry point in compatible GitHub Copilot clients.
- `uncovr.py`: standard-library CLI; installs skills and scaffolds context; checks structured evidence without executing application code.
- `templates/product-context`: six human-readable documents and one evidence index.
- `docs/`: contracts and examples for maintainers. During installation, the evidence contract is copied into `.uncovr/evidence-contract.md`.

No database, API server, hosted LLM, MCP server, project-code mutation, or framework-specific CLI is required for v0.1. Agent model inference and repository traversal depend on the user's chosen agent runtime.

## State versus product knowledge

`.uncovr/state.json` is an operational checkpoint, not a canonical product fact. It holds phase, baseline revision, inspected modules, and last validation date. The six Markdown artifacts are the reader-facing context; `evidence.jsonl` is the canonical claim provenance index. Git versioning provides history.

## Limitations

- The CLI is not an automatic static analyzer: it cannot reconstruct rules without an AI agent or human investigation.
- Completeness cannot be inferred from counts of files, claims, or tests.
- Technical proof of behavior does not establish why it was intended or whether it should persist.
- Changes to source after the recorded revision require a new check and possibly updated evidence.
- Runtime-only and third-party integrations may remain unknown until appropriately authorized investigation.

## Planned evolution

A later `impact` workflow can consume the baseline to identify candidate affected features, rules, modules and missing evidence for a proposed change. It must never automatically convert a guess into an approved requirement or generate code in the baseline phase.
