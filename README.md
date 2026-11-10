# Uncovr

**From code to product context.** Uncovr helps teams about to change a legacy system — developers and Product Owners — reconstruct usable, traceable knowledge of an existing software product when the repository is the principal source of information.

Uncovr focuses on **what exists, how it behaves, which rules and dependencies matter, what is uncertain, and what needs human validation**. It does not generate new production code or pretend that source code explains the business intent behind every decision.

## What v0.3 contains

- **One Agent Skill, `uncovr`,** in `.github/skills/uncovr/`: the workflow in `SKILL.md`, the Explorer, Analyst and Validator stages in `references/`, artifact templates in `assets/`, a self-contained structural check in `scripts/`, a worked example in `examples/` and evals in `evals/`. The same folder is installed into VS Code and packaged for the Agensi marketplace.
- **Two optional VS Code agents:** **Uncovr** as entry point and **Uncovr Validator**, run as a subagent so the review happens in a separate context.
- **Six primary Markdown artifacts:** overview, feature catalog, domain, architecture, traceability, validation.
- **One evidence index:** JSONL claims with stable IDs, source provenance, confidence and separately recorded business validation.
- **One standard-library Python CLI:** non-destructive installation with a manifest, structural checks, status and marketplace packaging.
- **Unit tests, a reference case per AI stage and a CI workflow.**

> v0.3 is a working scaffold and validation toolkit. Actual functional reconstruction requires an AI agent or human reviewer with access to the target repository. No real target system has yet been analysed with this package.

## Quick start

Requirements: Python 3.10+; an existing repository; an agent runtime supporting project skills, such as GitHub Copilot in VS Code.

Supported environments: GitHub Copilot Chat in VS Code (the agents declare `target: vscode`) and Claude Code (the skill alone).

1. Clone/download this Uncovr repository.
2. Install Uncovr into a different local repository:

   ```bash
   python3 /path/to/uncovr/uncovr.py install /path/to/existing-project
   ```

3. Open the **existing project** in VS Code. In GitHub Copilot Chat, select the **Uncovr** agent if available, then ask:

   > Reconstruct the existing product context for this repository with Uncovr. Work incrementally and collect questions I need to validate as PO.

   Alternatively, ask your agent to read `.github/skills/uncovr/SKILL.md` and follow it.

4. After analysis, inspect `product-context/` and run, in the project:

   ```bash
   python3 .github/skills/uncovr/scripts/check.py .
   ```

   and, from the Uncovr checkout, `python3 /path/to/uncovr/uncovr.py status /path/to/existing-project`.

The install command **never overwrites** an existing path. It copies the skill without `examples/` and `evals/`, and records the installed version and a hash of each Uncovr file in `.uncovr/manifest.json`; `status` reports files that were modified locally and files whose version in this checkout differs. Updating is still manual: replace the reported files, then delete the manifest and re-run install to record the new version. Do not use this framework on repositories whose code you are not authorized to inspect. Review repository security policy and avoid sharing confidential sources with unauthorized model providers.

## Publish on Agensi

```bash
python3 uncovr.py pack            # writes dist/uncovr.zip
```

The ZIP holds one top folder, `uncovr/`, with `SKILL.md` at its root and text files only; `pack` refuses symlinks, binary files, a `SKILL.md` of 500 lines or more and scripts over 20 KB. The VS Code agents are not included: Agensi delivers skills through MCP and does not sell agents. Upload it in the Creator Dashboard, set the price, and use the skill's `README.md` and the `description` in `SKILL.md` for the listing. Before submitting, run `evals/evals.json` in Copilot and Claude Code and analyse at least one real repository.

## Uninstall

Run `status` first and keep any file it reports as modified locally if you want your changes. Then remove, from the target repository:

- `.github/agents/uncovr.agent.md` and `.github/agents/uncovr-validator.agent.md`
- `.github/skills/uncovr/`
- `.uncovr/`

`product-context/` is the baseline you produced: keep it, or delete it if it is no longer wanted. To replace a single component (for example one stage reference), edit or swap that file; `status` will then list it as modified locally.

## Folder layout

```text
.github/
  agents/                     VS Code only
    uncovr.agent.md
    uncovr-validator.agent.md
  skills/uncovr/              the skill: installed into VS Code, packed for Agensi
    SKILL.md
    README.md
    references/               explorer.md, analyst.md, validator.md, evidence-contract.md
    assets/product-context/   six templates + evidence.jsonl
    scripts/check.py          structural check, standard library only
    examples/order-approval/  reference case: app/, expected/ baseline, cases.json
    evals/evals.json          trigger prompts and quality criteria
uncovr.py                     install, check, status, pack
tests/test_uncovr.py
docs/
  architecture.md
  acceptance.md
  example-walkthrough.md
```

For an installed target, the six documents and `evidence.jsonl` reside in `product-context/`. `.uncovr/state.json` tracks operational progress and `.uncovr/manifest.json` records what was installed. For schema details see the [evidence contract](.github/skills/uncovr/references/evidence-contract.md).

## How confidence works

Technical confidence (`confirmed`, `inferred`, `gap`, `contradicted`) and business validation (`pending`, `approved`, `rejected`, `not_applicable`) are **different dimensions**. A confirmed code behavior may still be a bug or obsolete business rule. Human approval must be explicit, attributable and dated.

The CLI can verify that local referenced files exist and paths/line ranges are well formed. It **cannot** certify semantic validity or business truth. Running `check` on newly installed blank templates should produce warnings, not a completion signal.

## Test locally

```bash
python3 -m unittest discover -s tests -v
python3 -m py_compile uncovr.py .github/skills/uncovr/scripts/check.py
```

`.github/skills/uncovr/examples/order-approval/` is the reference case for the AI stages: a small app (`app/`), the baseline a good run produces (`expected/`) and, per stage, its input and expected outcome (`cases.json`). The unit tests check that the expected baseline holds. To evaluate the agents, install Uncovr into a copy of `app/`, run it, and compare `product-context/` with `expected/`: same claim IDs or equivalents, same confidence, `BR-002` left contradicted, and nothing approved.

## Pilot success criterion

A PO unfamiliar with the codebase can use the generated baseline to identify affected features, current business rules, critical dependencies, regression risks and unanswered stakeholder questions for a concrete future change. See [acceptance criteria](docs/acceptance.md) and [example](docs/example-walkthrough.md).

## Origins and scope

This is a deliberately smaller, PO-facing framework. Its conceptual inspiration includes [Reversa](https://github.com/sandeco/reversa), notably technical reconnaissance, discovery of implicit rules, traceability and explicit confidence. This implementation is written independently; Reversa's broader coding, migration, refactoring and documentation-portal teams are not included. Review the original project's terms before copying any of its source files or agent instructions into future versions.

**Owner:** Luciano Borges — ask him when something breaks or a change is proposed. Changes are recorded in [CHANGELOG.md](CHANGELOG.md).

**License:** proprietary; distribution through the Agensi marketplace is authorized. See [LICENSE](LICENSE).
