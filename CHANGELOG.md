# Changelog

All notable changes to Uncovr are recorded here. The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/); versions follow [Semantic Versioning](https://semver.org/).

## [Unreleased]

### Changed

- Analyst and Validator require UI evidence for user-visible claims, scope-aware exceptions to universal assertions, atomic claims with scoped human decisions, and consistent source-conflict reporting.
- The evidence contract defines claim splitting with stable IDs, decision provenance and preserved history; a human choice of desired behavior does not erase an implementation mismatch.
- The architecture template adds an inspection boundary (inspected, unknown, external) and a compact technology stack, and gives components their responsibility, boundary, data flows and external dependencies. Deployment separates configuration found, execution observed and production not confirmed; release, storage and compatibility limits need a source. Explorer, Analyst, Validator, the evidence contract and the repository-signals checklist follow, and the example records its stack and its unconfirmed deployment as claims. Existing baselines remain valid.
- The structural check warns when Markdown cites a claim ID missing from `evidence.jsonl`, and when a stack or component row in `architecture.md` cites no claim. The wiki exporter describes the new architecture sections.
- The overview separates observed capabilities from declared purpose, users, value and objectives, which need a business source and stay `pending`; unknowns are gaps. A new *Who can clarify* section lists roles or teams a source names, with their knowledge area and the questions they could help answer; CODEOWNERS, authors, contributors and accounts never establish business authority or approval. The domain glossary separates the meaning observed in code from the business definition and records ambiguities. The evidence contract, the repository-signals checklist, Explorer, Analyst, Validator, `SKILL.md` and the wiki exporter follow; the example records its declared purpose, missing objectives and the approver-as-manager ambiguity as `CTX-` assumption claims. No schema change: existing baselines remain valid.
- The structural check warns when `not_applicable` is used for a feature, business rule, assumption or gap.
- Traceability names for each claim only the files its evidence cites and adds an optional *Sources* view: purpose, scope consulted, version or date, status (`consulted`, `indicated`, `inaccessible`) and claim IDs. Only consulted sources are evidence; a document or ticket records intent, never implementation. The validation sheet keeps open questions apart from a new *Decisions* view and gives each divergence a row with the claims involved, each source's position, impact and the decision or `pending`. The evidence contract adds *Sources, decisions and reopening*: decisions are `decision` claims in `evidence.jsonl`, never edited or deleted, reopened only on new evidence recorded as its own claim, and replaced through the optional `supersedes` field. Analyst, Validator, `SKILL.md`, the repository-signals checklist, the example and the wiki exporter follow; the exporter marks superseded claims deprecated and links both ways. Existing baselines remain valid.
- The structural check warns when a traceability row names a file its claim's evidence does not cite, a source row has no valid status or claim ID, an indicated or inaccessible source is cited as evidence, a `contradicted` claim is not listed under divergences, a listed decision has no recorded human decision, a reopening cites no new evidence or is not asked again, or a superseded row disagrees with `supersedes`. A malformed `supersedes` is an error.

### Added

- Four manual semantic regression cases against a pinned public target, with isolated inputs, pass/fail criteria and a partial-decision seed. Existing pilot baselines remain untouched.
- Contract tests for the semantic guidance and evaluation definitions. These do not certify live agent behavior.
- Synthetic tests for a declared business source, a missing source and a conflict between declared definition and observed behavior, plus the independence of confidence and business approval. These do not certify live agent behavior.
- Optional Mermaid diagrams: the evidence contract adds *Diagrams* — which type answers which question per document, one small subject per diagram, plain fenced `mermaid` blocks preceded by a sentence citing claim IDs, inferred relations marked, gaps undrawn, nothing derived from names, configuration or plans, no charts of quantities, and none when text or a table is as clear. Templates, Explorer, Analyst and Validator point to it; the example adds one flowchart of the approve and reject checks and leaves architecture, states and traceability without one. The structural check warns about unclosed blocks, other diagram types, styling, oversized diagrams, diagrams citing no claim and non-confirmed claims drawn without naming their confidence. The wiki exporter no longer rewrites claim IDs inside fenced blocks, so Mermaid survives the export unchanged. Existing baselines remain valid.
- Synthetic tests for missing external sources, an inaccessible source, an unresolved contradiction, a recorded decision, a reopening with and without new evidence and a superseded decision, and a manual `decision_history` evaluation. These do not certify live agent behavior.

## [0.5.0] - 2026-11-11

### Added

- Explicit local and Agensi MCP delivery modes, on-demand file-index lookup, unchanged standalone scripts in private temporary directories, scoped cleanup and persistent-output boundaries.
- Native-worker review without requiring an installed named agent, with an explicit non-independent fallback.
- Isolated execution tests for scripts extracted from the ZIP, including failures, paths with spaces, baseline preservation and test-harness cleanup.
- Five positive and five negative manual trigger prompts, plus incremental-preservation and live Agensi-delivery evaluation criteria.
- An anonymized record of the two local 0.4.0 OrangeHRM pilot rounds in the development acceptance document, outside the package.
- Listing summary, version, tags, keywords and use cases. The marketplace ZIP includes the original project license without keeping a second source copy.

### Changed

- Stage references and optional local agents follow the shared execution contract. Buyer documentation distinguishes observed local pilots from unverified Claude Code and live MCP behavior.
- Baseline extension explicitly preserves unrelated claims, human edits and open questions. Local package tests are not presented as agent evaluations or marketplace approval.

### Fixed

- The wiki exporter rejects a symlinked `product-context/` directory or `product-context/mkdocs.yml` before rebuilding or writing output, preventing writes and deletions outside the repository. Regression tests cover all wiki targets, existing output and dangling config links, and verify that rejected exports leave files unchanged.

## [0.4.0] — 2026-11-10

### Added

- `scripts/okf.py`: publishes the baseline as an Open Knowledge Format v0.2 bundle in `product-context/wiki/` for the LLM wiki the user chose — Obsidian, MkDocs or Google Knowledge Catalog. The six documents get OKF frontmatter and links to one concept page per claim; each claim carries `type`, `sources` with footnotes, `generated`, `verified` (`human:` actor) when approved, `status`, and `confidence`, `business_validation` and `revision` as extension keys. Root and folder `index.md`, and a `log.md` kept across rebuilds.
- Targets: Obsidian (relative links, claim IDs as aliases), MkDocs (relative links, `product-context/mkdocs.yml`, never over a foreign one), Knowledge Catalog (bundle-root links). Source links on GitHub at the baseline revision, or `--source-url` for other hosts.
- The scope checkpoint asks for the wiki target and records it as `wiki_target` in `.uncovr/state.json`; the export runs after the structural check and again after approvals. It refuses to replace a `wiki/` folder it did not generate, and never publishes to a service.
- Tests: OKF conformance for every target, link style, provenance and trust fields, source URLs, MkDocs config, log kept, foreign folder refused, sources untouched.

## [0.3.0] — 2026-11-10

Ready for the Agensi marketplace.

### Changed

- The four skills are now one skill, `uncovr`, in `.github/skills/uncovr/`: the orchestrator is `SKILL.md`; Explorer, Analyst and Validator are `references/`; the evidence contract moved to `references/`, the templates to `assets/product-context/`, the reference case to `examples/order-approval/`. All paths inside the skill are relative to it.
- New `description` with "Use when" and "Do not use" triggers, aimed at teams about to change a legacy system.
- `SKILL.md` creates `product-context/` and `.uncovr/state.json` itself when missing, so the skill works without `install`; it writes the artifacts in the user's language and excludes its own files from analysis.
- The structural check moved to `scripts/check.py` (self-contained, standard library); `uncovr.py check` reuses it. `install` no longer copies `uncovr.py` or the evidence contract into `.uncovr/`, and skips `examples/` and `evals/`.
- LICENSE authorizes distribution through the Agensi marketplace.

### Added

- `uncovr.py pack`: deterministic `dist/uncovr.zip` with one top folder and text files only; refuses symlinks, binaries, a long `SKILL.md` and scripts over 20 KB.
- Skill `README.md`, `evals/evals.json` (5 trigger, 3 non-trigger prompts and quality criteria), edge cases for empty repositories and several products.
- `references/repository-signals.md`: what to look for in a repository and where it goes, with the related SWEBOK Guide v4.0 section numbers (cited, not reproduced) — business parameters, feature flags, background work, permissions, sensitive data, acceptance criteria from tests, skipped tests, deployment, contracts, dependencies and licences, known debt, recorded intent, analytics, ownership.
- Template sections: *Observed acceptance criteria* and *Variants, flags and parameters* (features), *States*, *Permissions* and *Sensitive data* (domain), *Deployment and environments* and *Known debt* (architecture), owners in the overview; a *Criticality* column for features; rules as trigger, preconditions, outcome and exceptions.
- The Validator reviews in four checks: correctness, consistency, traceability, completeness.
- `scripts/history.py` (standard library, read-only `git log`): commits, churn, fix commits, ticket references, number of authors and last change per module, for *Regression hotspots*. It reports measured facts, not a risk score, excludes the baseline, the skill, vendored folders and lockfiles, and never prints author identities. Allowed without asking, like `check.py`.
- The order-approval example follows the new sections; tests check that it covers every template section and that the signals reference points to sections that exist.
- Tests for packaging, frontmatter, references inside the skill and evals.

### Known incompatibilities

- Installations from 0.2.0 have four `uncovr-*` skill folders and `.uncovr/uncovr.py`; remove them and re-install.
- The VS Code agents are not part of the Agensi package; there the Validator runs as a subagent only if the buyer's agent supports one.

## [0.2.0] — 2026-11-10

Structural review against the Agentizr quality checklist.

### Added

- `Uncovr Validator` agent, run by `Uncovr` as a subagent so the validation happens in a separate context; when subagents are unavailable the review runs inline and is recorded as not independent.
- Two checkpoints in the orchestrator: scope confirmation before exploring, and baseline review at the end.
- *When a stage cannot proceed*: missing information, blocked stages (one retry), and work limited to the confirmed module batch.
- `.uncovr/manifest.json` with the installed version and a hash per file; `status` reports missing, locally modified and outdated files.
- Reference case `tests/fixtures/order-approval/` with the expected baseline and per-stage cases.
- *Inputs* in the Explorer, Analyst and Validator skills; *Completion* in the Validator.
- README sections for the supported environment, uninstalling, owner and license.

### Changed

- The agents declare `target: vscode` and an explicit `tools` list.
- Rules common to every stage live only in the orchestrator's *Inputs and boundaries*; the other files refer to them.
- The write limit is stated as instruction-only and checked with `git status --porcelain` before each checkpoint.
- Install copies files one by one, so a missing file inside an existing skill folder is added.

### Fixed

- Skills no longer refer to the Uncovr README, which is not installed in a target repository.

### Known incompatibilities

- `agents` and the `agent` tool are Local-harness (VS Code) settings; the Copilot harness ignores them, and the orchestrator then runs the Validator inline.
- Installations made with 0.1.0 have no manifest; `status` says so.

## [0.1.0]

- First version: four skills, the Uncovr agent, six Markdown templates and `evidence.jsonl`, the standard-library CLI (`install`, `check`, `status`), unit tests and CI.
