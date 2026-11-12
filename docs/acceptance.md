# Acceptance and evaluation

## Automated gates

Run `python3 -B -m unittest discover -s tests -v` from the Uncovr checkout. The suite checks:

- Non-overwriting local installation of one skill and two optional VS Code agents, with six Markdown templates and an evidence index.
- Invalid IDs, duplicate claims, missing files, escaping evidence paths and inconsistent approval metadata.
- Markdown citations of claim IDs missing from the index, and architecture stack or component rows without a claim ID (warnings).
- Architecture guidance that separates inspected, unknown and external, and configured, observed and unconfirmed production deployment. These checks do not test an agent's conclusions.
- Overview and domain guidance that separates observed capabilities and meanings from declared intent and definitions, keeps unknowns as pending gaps and never derives business authority from repository metadata; a warning for `not_applicable` on business claims or gaps; and the reference case's declared, missing and conflicting sources. These checks do not test an agent's conclusions.
- Traceability and validation views checked against the index (warnings): files named per claim, source status and claim IDs, unopened sources cited as evidence, unlisted contradictions, decisions without a recorded human decision, reopenings without new evidence or a new question, and supersession; a malformed `supersedes` is an error. Synthetic cases cover no external source, an inaccessible source, an unresolved contradiction, a recorded decision and a justified reopening. These checks do not test whether a source says what a row claims, nor an agent's conclusions.
- Mermaid blocks (warnings): closed fence, supported diagram type, no styling, size, claim IDs cited in the block or the sentence before it, and non-confirmed confidence named; a baseline with no diagram raises none; the exporter copies fenced blocks unchanged for every target. These checks do not test whether a diagram is faithful, useful or renders.
- Scaffold warnings instead of a completion claim.
- The structural validity of the reference case, not an AI reconstruction of it.
- Deterministic packaging, skill metadata, internal references, file/size restrictions and exclusion of agent definitions.
- An explicit local/MCP execution contract and manual evaluation scenarios.
- Stage instruction contracts for UI evidence, bounded claims, atomic decisions and source conflicts, plus the structure of their manual regression cases. These checks do not test an agent's conclusions.
- Scripts taken from the ZIP, run unchanged under a different filename in an isolated temporary directory, with an explicit target path containing spaces and no installation or sibling package files.
- Successful and failing script executions, baseline preservation, and temporary cleanup by the test harness.
- Refusal of symlinked export destinations before changes to external files or an existing wiki.

The Python suite does not run an agent, call Agensi, measure trigger reliability, certify the meaning of a claim or prove that an agent follows temporary-file cleanup instructions. Its delivery tests simulate the documented script contract locally. No extra dependencies are required; the Git success tests are skipped if Git is unavailable.

## Manual agent evaluations

The [evaluation dataset](../.github/skills/uncovr/evals/evals.json) defines trigger, quality, decision-history, semantic-regression, incremental and Agensi-delivery cases. Record each execution's date, skill revision/diff, target revision, runtime/model, delivery mode, prompt, observed loading, criteria passed/failed, duration and limitations. Do not record credentials, personal paths or raw confidential sources.

- Use fresh chats and clean target copies for five positive and five negative trigger prompts. Recommended target: 5/5 positive and 0/5 negative. Do not name Uncovr or select its custom agent for this test.
- Run the quality case three to five times per environment being advertised. Use only the example's `app/` as the target; keep `expected/`, `cases.json` and evaluator notes outside the agent's available files. Compare equivalent claims and supporting sources, not exact prose.
- Extend a real baseline to a second existing workflow. Compare old records and documents against a snapshot unavailable to the agent, and distinguish deliberate reviewed corrections from lost content.
- Test a missing/empty repository, unavailable optional tools, an unavailable worker and a failed helper command. No unexecuted step may be reported as passed.
- Once the listing is live, run the Agensi-delivery case with no local Uncovr installation. Before publication, this remains unverified; unit tests are not a substitute.

### Semantic regression cases

Run `semantic_regressions.cases` in fresh, isolated copies of the pinned public target, three to five times per advertised environment. Use the specified scope and follow-up answers. Keep the dataset and evaluator expectations unavailable to the agent; never reuse or correct an original pilot baseline as part of these evaluations.

| Case | What must be demonstrated |
| --- | --- |
| `ui_feedback` | An excluded interface stays unreviewed. When included, the agent follows the actual warning and confirmation path and its conditions, without inferring UI absence from backend permission. Run both variants. |
| `bounded_notifications` | Explicit workflow events are distinguished from a direct automatic status update; exception handling agrees across the canonical claims and Markdown. Event emission is not delivery proof. |
| `atomic_decisions` | A compound input claim is split with stable IDs, mapping and history. A partial rejection affects only the decided assertion and its metadata; other business rules remain pending. |
| `source_conflicts` | Configuration and implementation are compared in the same context. Supported source facts stay intact, while the mismatch is visible in a contradicted claim, documents and counts even after a human chooses desired behavior. |

The atomic case's seed is deliberately imperfect input for the reviewer, not an approved baseline. The cases do not execute the target application. Record observed passes and failures only after an agent run; neither green contract tests nor a manually corrected pilot prove these behaviors.

## Local pilot record: 2026-11-11

Evidence: two user-provided exports of one continuing GitHub Copilot conversation, inspected alongside the local outputs and a small sample of sources. The exports, baseline contents and target code are not stored here or included in the marketplace package. This is an anonymized retrospective record, not a reproducible automated benchmark or an independent domain acceptance review.

- Target: [legacy OrangeHRM](https://github.com/orangehrm/legacy.orangehrm), revision `5d1661256a09ec3226bda48530f98175ac6cc006`.
- Skill version recorded by the installed state: 0.4.0, before the explicit 0.5.0 MCP contract.
- Runtime: GitHub Copilot in VS Code, built-in Agent mode. Model ID recorded by the exports: `copilot/gpt-6-astra`.
- Delivery: installed local skill and named Uncovr Validator. Both rounds shared one parent conversation; review workers used separate contexts. No Claude Code or Agensi execution was observed.
- Scope confirmations were explicit. Application, database and target-system tests were not executed; no wiki was requested.

| Observation | First round | Second round |
| --- | --- | --- |
| Scope | Absence request and approval workflow | Incremental attendance workflow |
| Added claims | 46 | 34 |
| Cumulative claims | 46 | 80 |
| Added confidence counts | 29 confirmed, 8 inferred, 4 gap, 5 contradicted | 21 confirmed, 7 inferred, 3 gap, 3 contradicted |
| New questions | 13 | 8 |
| Business approvals | 0 | 0 |
| Final phase | awaiting_human_review | awaiting_human_review |
| Exported agent elapsed time | About 81.1 minutes | About 63.4 minutes |
| Serialized tool events | 297 | 285 |
| File-read events | 191 | 179 |
| Review calls | Review and focused ratification | Review, ratification without a returned opinion, successful retry |
| User continuation events | One Continue to iterate | Two Try Again |

Timing is the sum of `elapsedMs` for the requests belonging to each round, excluding the export's separate waiting field. Tool counts are events serialized in those request responses, not token counts, billing measurements or proof of useful work.

Verified at the second export: all 46 original JSONL records remained identical; the complete old text of each of the six documents and the evidence index remained an unchanged prefix. All 13 original question rows were intact. The 80 IDs were unique, none business-approved, and the current files matched the exported final snapshots. The structural check passed without warnings; Git reported only the pre-existing untracked skill/state/output folders and no tracked source changes. This comparison demonstrates extension at the same target revision, not safe refresh after source changes.

The review changed conclusions rather than merely polishing prose: the first round narrowed the notification claim and the second corrected a duration summary to depend on UTC fields rather than record state. Sample source checks supported those corrections. This is not a semantic audit of all 80 claims. Reported review verdicts and the index's confidence counts are different measures.

Observed friction: long runs, repeated reads, invalid line references corrected by the checker, patch-context/order retries, and a failed ratification call recovered by retry. The accumulated validation document reached about 118,000 characters. These observations motivate efficiency and readability improvements; they do not establish the cause of runtime interruptions.

Remaining validation: the updated MCP contract, live Agensi delivery, Claude Code, independent repeated runs, source-change refresh, real runtime behavior and review by a Product Owner/domain specialist. The pilot is positive evidence for local discovery and incremental preservation, not marketplace approval or cross-agent certification.

## Local pilot record: Claude Code, 2026-11-11

Evidence: the target's outputs (`product-context/`, `.uncovr/state.json`), the skill files the run used, and the metadata of the Claude Code session log (version, model, timestamps and tool-call counts; no conversation content copied), inspected on 2026-11-12. The baseline contents and target code are not stored here or included in the marketplace package. This is a retrospective record of one run, not a reproducible benchmark or an independent domain acceptance review.

- Target: [legacy OrangeHRM](https://github.com/orangehrm/legacy.orangehrm), revision `5d1661256a09ec3226bda48530f98175ac6cc006`, in a separate clone from the Copilot pilot.
- Skill: the skill folder copied into the target's `.claude/skills/uncovr/`, without `uncovr.py install`, manifest, named agents, `examples/` or `evals/`. Its `SKILL.md` declares 0.5.0, but the copy matches no commit and not the 0.5.0 ZIP: 13 of its 17 files equal the ZIP, while `SKILL.md`, `references/analyst.md`, `references/validator.md` and `references/evidence-contract.md` differ. It is a pre-release working copy of 0.5.0.
- Runtime: Claude Code 2.1.317. Model ID recorded by the log: `claude-opus-5-5`.
- Delivery: local skill, loaded through Claude Code's skill mechanism (two `Skill` calls). No Agensi execution was observed.
- Scope: absence request and approval workflow of the leave plugin, with targeted reads of the core plugin's workflow and roles and of the workflow seed; confirmed explicitly by the owner acting as Product Owner. No wiki. Application, database and target-system tests were not executed.

| Observation | Value |
| --- | --- |
| Claims | 42: 19 business rules, 7 features, 6 architecture, 5 constraints, 5 assumptions |
| Confidence | 36 confirmed, 5 inferred, 1 gap, 0 contradicted |
| Business validation | 25 pending, 11 not_applicable, 6 rejected, 0 approved |
| Human decisions | 6 rejections, each with `validated_by` and `validated_on`, listed under *Decisions* in `validation.md`; two questions left open |
| Final phase | awaiting_human_review |
| Session span | About 106 minutes from first to last event (21:53–23:39 UTC), including the time the person took to answer |
| Main-session tool calls | 84 Bash, 16 Read, 8 Write, 4 Edit, 8 AskUserQuestion, 2 Agent, 2 Skill |
| Validation | One subagent in a separate context, about 7 minutes (53 Bash, 1 Read, 1 Write); `validation.md` records the review as independent |

Tool counts are calls serialized in the log, not token counts, billing measurements or proof of useful work.

Verified on 2026-11-12: Git reported no tracked change; only `.claude/`, `.uncovr/`, `product-context/` and an operating-system `.DS_Store` were untracked. The structural check of the copy that ran reports the structure valid without warnings. The current check reports it valid with two warnings: a `traceability.md` row for BR-020 names two files its evidence does not cite, a rule added after the run.

The rejections kept technical confidence apart from the business decision: rejected claims stayed `confirmed` or `inferred` ("inferred until reproduced in a test environment"), and no rejection was presented as proof of a defect. They were recorded on the claims themselves. The current evidence contract, added after this run, records each decision as a separate `decision` claim. This baseline predates that protocol and is not converted.

Remaining validation: live Agensi delivery, trigger reliability without naming the skill, repeated runs, version 0.6.0 itself, source-change refresh, real runtime behavior and review by a domain specialist. The run is positive evidence that the workflow, checkpoints, separate-context review and write boundary hold in Claude Code with a local skill, not marketplace approval or cross-agent certification.

## Pilot acceptance (requires a real target repository and humans)

Select a known system and one realistic proposed change. Ask an unfamiliar PO to identify:

1. Existing capabilities and actors involved.
2. Relevant current rules, exceptions and permission constraints.
3. Source paths and tests substantiating those behaviors.
4. Conflicts, non-observable intent, and decision questions for stakeholders.
5. Candidate integration and regression risks.

Compare these findings against a reference review by engineers and a domain specialist. Record precision of claims, missing critical behaviors, unanswered questions and elapsed PO review effort. Do **not** present estimated completeness percentages without a defensible evaluation method.

## Out of scope

Implementation plans, writing production code, migrations, deployments, autonomous defect fixing, generated full-system C4 detail, automatic acceptance of business assumptions and continuous background monitoring.
