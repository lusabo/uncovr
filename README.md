# Uncovr

**From code to product context.** Uncovr helps teams about to change a legacy system — developers and Product Owners — reconstruct usable, traceable knowledge of an existing software product when the repository is the principal source of information.

Uncovr focuses on **what exists, how it behaves, which rules and dependencies matter, what is uncertain, and what needs human validation**. It does not generate new production code or pretend that source code explains the business intent behind every decision.

This page is for people working on Uncovr. Buyers and users of the skill should read the [skill README](.github/skills/uncovr/README.md).

## What v0.6 contains

- **One Agent Skill, `uncovr`,** in `.github/skills/uncovr/`: the workflow in `SKILL.md`, the Explorer, Analyst and Validator stages in `references/`, artifact templates in `assets/`, three self-contained helper scripts in `scripts/`, a worked example in `examples/` and evals in `evals/`. The same folder is installed locally and packaged for the Agensi marketplace, both without `examples/` and `evals/`.
- **Two optional VS Code agents:** **Uncovr** as entry point and **Uncovr Validator**, run as a subagent so the review happens in a separate context.
- **Six primary Markdown artifacts:** overview, feature catalog, domain, architecture, traceability, validation.
- **One evidence index:** JSONL claims with stable IDs, source provenance, confidence and separately recorded business validation.
- **Optional LLM wiki:** the baseline published as an Open Knowledge Format v0.2 bundle for Obsidian, MkDocs or Google Knowledge Catalog, chosen at the scope checkpoint.
- **One standard-library Python CLI:** non-destructive installation with a manifest, structural checks, status and marketplace packaging.
- **Unit tests, isolated execution tests of scripts from the ZIP, manual agent evals and a CI workflow.**

## Validation status

Actual functional reconstruction requires an AI agent with access to the target repository and human review.

| Environment | Delivery | Version | Evidence |
| --- | --- | --- | --- |
| GitHub Copilot in VS Code | Local skill and named Validator | 0.4.0 | Two pilot rounds on legacy OrangeHRM: absence management, then an incremental attendance baseline |
| Claude Code | Local skill | Pre-release copy of 0.5.0 | One run on legacy OrangeHRM: absence management |
| Any agent through Agensi | MCP | — | Not yet verified end to end |

The [acceptance and evaluation record](docs/acceptance.md) separates automated checks, manual evaluations and the anonymized pilot observations. Private exports and target repositories are not included in the package.

## Quick start (local installation)

Requirements: Python 3.10+, an existing repository, and an agent that supports project skills — GitHub Copilot in VS Code or Claude Code.

1. Clone or download this Uncovr repository.
2. Install Uncovr into a different local repository:

   ```bash
   python3 /path/to/uncovr/uncovr.py install /path/to/existing-project
   ```

   For Claude Code, which reads project skills from `.claude/skills/`, copy `.github/skills/uncovr/` without `examples/` and `evals/` to `.claude/skills/uncovr/` in the project. The optional agents (`target: vscode`) are for VS Code only, and `status` does not track that copy.

3. Open the **existing project** in your agent. In GitHub Copilot Chat, select the **Uncovr** agent if available. Then ask:

   > Reconstruct the existing product context for this repository with Uncovr. Work incrementally and collect questions I need to validate as PO.

   Alternatively, ask your agent to read the installed `SKILL.md` and follow it.

4. After analysis, inspect `product-context/` and run, in the project:

   ```bash
   python3 -B .github/skills/uncovr/scripts/check.py .
   ```

   From the Uncovr checkout, `python3 /path/to/uncovr/uncovr.py status /path/to/existing-project` reports what was installed and what changed.

The install command **never overwrites** an existing path. It copies the skill without `examples/` and `evals/`, and records the installed version and a hash of each Uncovr file in `.uncovr/manifest.json`. `status` reports files that were modified locally and files whose version in this checkout differs. Updating is still manual: replace the reported files, then delete the manifest and re-run install to record the new version.

Do not use Uncovr on repositories whose code you are not authorized to inspect. Review the repository's security policy and avoid sharing confidential sources with unauthorized model providers.

## Use through Agensi

The buyer connects their repository-capable agent to Agensi, obtains access to the listing and asks it to use Uncovr. No Uncovr installer runs in the buyer's project: the agent loads the skill and its supporting text through MCP. Scripts execute unchanged in private temporary files, then are removed. Only the baseline and its progress state persist. See the [skill README](.github/skills/uncovr/README.md) for requirements and current validation limits.

## Publish on Agensi

1. Run the [evals](.github/skills/uncovr/evals/evals.json) in every environment you intend to advertise.
2. Commit, then build the package:

   ```bash
   python3 uncovr.py pack            # writes dist/uncovr.zip
   ```

3. Upload `dist/uncovr.zip` in the Creator Dashboard and set the price. Fill the listing from the skill's `README.md` and its frontmatter: description, summary, version, tags and use cases. `pack` does not choose a price, create a listing or certify compatibility.
4. After approval, verify the live skill through Agensi in each advertised environment, without a local installation. The local pilots do not prove the MCP delivery path.

What `pack` produces:

- One top folder, `uncovr/`, with `SKILL.md` at its root, the project's original `LICENSE` and text files only.
- It refuses symlinks, binary files, a `SKILL.md` of 500 lines or more and scripts over 20 KB.
- The VS Code agents are left out: Agensi delivers skills through MCP and does not sell agents.
- `examples/` and `evals/` are left out: they hold the expected answers, and a buyer's agent — or your own, when you verify the live skill — must not receive them.
- The archive is identical for identical sources. A version number cannot be reused on Agensi, so raise it before each upload.

## Uninstall

Run `status` first and keep any file it reports as modified locally if you want your changes. Then remove, from the target repository:

- `.github/agents/uncovr.agent.md` and `.github/agents/uncovr-validator.agent.md`
- `.github/skills/uncovr/` (or `.claude/skills/uncovr/` for Claude Code)
- `.uncovr/`

`product-context/` is the baseline you produced: keep it, or delete it if it is no longer wanted. To replace a single component (for example one stage reference), edit or swap that file; `status` will then list it as modified locally.

## Folder layout

```text
.github/
  agents/                     VS Code only
    uncovr.agent.md
    uncovr-validator.agent.md
  skills/uncovr/              the skill: installed locally, packed for Agensi
    SKILL.md
    README.md                 for buyers and users
    references/               explorer.md, analyst.md, validator.md,
                              evidence-contract.md, repository-signals.md
    assets/product-context/   six templates + evidence.jsonl
    scripts/                  check.py, history.py, okf.py (standard library only)
    examples/order-approval/  reference case: app/, expected/ baseline, cases.json (not shipped)
    evals/evals.json          trigger prompts and quality criteria (not shipped)
  workflows/ci.yml            unit tests, compilation, pack
uncovr.py                     install, check, status, pack
tests/test_uncovr.py
docs/
  architecture.md
  acceptance.md
  example-walkthrough.md
CHANGELOG.md
LICENSE
```

For an installed target, the six documents and `evidence.jsonl` reside in `product-context/`. `.uncovr/state.json` tracks operational progress and `.uncovr/manifest.json` records what was installed. For schema details see the [evidence contract](.github/skills/uncovr/references/evidence-contract.md).

## How confidence works

Technical confidence (`confirmed`, `inferred`, `gap`, `contradicted`) and business validation (`pending`, `approved`, `rejected`, `not_applicable`) are **different dimensions**. A confirmed code behavior may still be a bug or obsolete business rule. Human approval must be explicit, attributable and dated.

The CLI can verify that local referenced files exist and paths/line ranges are well formed. It **cannot** certify semantic validity or business truth. Running `check` on newly installed blank templates should produce warnings, not a completion signal.

## Test locally

```bash
python3 -m unittest discover -s tests -v
python3 -m py_compile uncovr.py .github/skills/uncovr/scripts/*.py
```

`.github/skills/uncovr/examples/order-approval/` is the reference case for the AI stages: a small app (`app/`), the baseline a good run produces (`expected/`) and, per stage, its input and expected outcome (`cases.json`). The unit tests check that the expected baseline holds.

To evaluate an agent, install Uncovr into a copy of `app/` alone, keeping `expected/` and `cases.json` out of the agent's reach. Run it, then compare `product-context/` with `expected/`: same claim IDs or equivalents, same confidence, `BR-002` left contradicted, and nothing approved.

## Pilot success criterion

A PO unfamiliar with the codebase can use the generated baseline to identify affected features, current business rules, critical dependencies, regression risks and unanswered stakeholder questions for a concrete future change. See [acceptance criteria](docs/acceptance.md) and [example](docs/example-walkthrough.md).

## Origins and scope

This is a deliberately smaller, PO-facing framework. Its conceptual inspiration includes [Reversa](https://github.com/sandeco/reversa), notably technical reconnaissance, discovery of implicit rules, traceability and explicit confidence. This implementation is written independently; Reversa's broader coding, migration, refactoring and documentation-portal teams are not included. Review the original project's terms before copying any of its source files or agent instructions into future versions.

**Owner:** Luciano Borges — ask him when something breaks or a change is proposed. Changes are recorded in [CHANGELOG.md](CHANGELOG.md).

**License:** proprietary; distribution through the Agensi marketplace is authorized. See [LICENSE](LICENSE).
