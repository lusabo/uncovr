# Uncovr

**From code to product context.** Uncovr helps a Product Owner reconstruct usable, traceable knowledge of an existing software product when the repository is the principal source of information.

Uncovr focuses on **what exists, how it behaves, which rules and dependencies matter, what is uncertain, and what needs human validation**. It does not generate new production code or pretend that source code explains the business intent behind every decision.

## What v0.1 contains

- **Four roles:** Orchestrator, Explorer, Analyst, Validator. Packaged as portable Agent Skills for a repository using GitHub Copilot or another compatible runtime.
- **Six primary Markdown artifacts:** overview, feature catalog, domain, architecture, traceability, validation.
- **One evidence index:** JSONL claims with stable IDs, source provenance, confidence and separately recorded business validation.
- **One standard-library Python CLI:** non-destructive installation, structural checks and status display.
- **Unit tests and a CI workflow.**

> v0.1 is a working scaffold and validation toolkit. Actual functional reconstruction requires an AI agent or human reviewer with access to the target repository. No real target system has yet been analysed with this package.

## Quick start

Requirements: Python 3.10+; an existing repository; an agent runtime supporting project skills, such as GitHub Copilot in VS Code.

1. Clone/download this Uncovr repository.
2. Install Uncovr into a different local repository:

   ```bash
   python3 /path/to/uncovr/uncovr.py install /path/to/existing-project
   ```

3. Open the **existing project** in VS Code. In GitHub Copilot Chat, select the **Uncovr** agent if available, then ask:

   > Reconstruct the existing product context for this repository with Uncovr. Work incrementally and collect questions I need to validate as PO.

   Alternatively, ask your agent to read `.github/skills/uncovr-orchestrator/SKILL.md` and follow it.

4. After analysis, inspect `product-context/` and run:

   ```bash
   python3 .uncovr/uncovr.py check .
   python3 .uncovr/uncovr.py status .
   ```

The install command **never overwrites** an existing path. Subsequent updates to installed skills are manual in v0.1; re-running install will skip existing files. Do not use this framework on repositories whose code you are not authorized to inspect. Review repository security policy and avoid sharing confidential sources with unauthorized model providers.

## Folder layout

```text
.github/
  agents/uncovr.agent.md
  skills/
    uncovr-orchestrator/SKILL.md
    uncovr-explorer/SKILL.md
    uncovr-analyst/SKILL.md
    uncovr-validator/SKILL.md
uncovr.py
templates/product-context/
  overview.md
  features.md
  domain.md
  architecture.md
  traceability.md
  validation.md
  evidence.jsonl

docs/
  architecture.md
  evidence-contract.md
  acceptance.md
  example-walkthrough.md
```

For an installed target, the six documents and `evidence.jsonl` reside in `product-context/`. `.uncovr/state.json` tracks operational progress and `.uncovr/uncovr.py` provides local checks. For schema details see [evidence contract](docs/evidence-contract.md).

## How confidence works

Technical confidence (`confirmed`, `inferred`, `gap`, `contradicted`) and business validation (`pending`, `approved`, `rejected`, `not_applicable`) are **different dimensions**. A confirmed code behavior may still be a bug or obsolete business rule. Human approval must be explicit, attributable and dated.

The CLI can verify that local referenced files exist and paths/line ranges are well formed. It **cannot** certify semantic validity or business truth. Running `check` on newly installed blank templates should produce warnings, not a completion signal.

## Test locally

```bash
python3 -m unittest discover -s tests -v
python3 -m py_compile uncovr.py
```

## Pilot success criterion

A PO unfamiliar with the codebase can use the generated baseline to identify affected features, current business rules, critical dependencies, regression risks and unanswered stakeholder questions for a concrete future change. See [acceptance criteria](docs/acceptance.md) and [example](docs/example-walkthrough.md).

## Origins and scope

This is a deliberately smaller, PO-facing framework. Its conceptual inspiration includes [Reversa](https://github.com/sandeco/reversa), notably technical reconnaissance, discovery of implicit rules, traceability and explicit confidence. This implementation is written independently; Reversa's broader coding, migration, refactoring and documentation-portal teams are not included. Review the original project's terms before copying any of its source files or agent instructions into future versions.

**License:** not yet selected. Do not assume reuse rights beyond those granted by applicable law until a license is added by the repository owner.
