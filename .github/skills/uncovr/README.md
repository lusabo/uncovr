# Uncovr

**Understand what a legacy system does before you change it.**

Uncovr is an Agent Skill. Point your AI agent at an existing repository and it writes a **Product Context Baseline**: what the system does, which business rules it enforces, how it is built, where change is risky and what nobody has written down. Every statement points to the code, test or document it came from, and nothing is treated as approved until a person says so.

It reads your code; it never changes it.

## Who it is for

- **Developers** who inherited a codebase and must change it safely.
- **Product Owners** who need to know what the product does today before planning the next version.
- **Teams** preparing a concrete change — "let managers delegate approvals", "add a second currency" — who want to see which features, rules and dependencies it touches.

## Get started in three steps

1. Open the repository you want to understand in an agent that can read its files and write new ones (for example GitHub Copilot in VS Code). Make sure the skill is available to it — through Agensi or a local installation, both described below.
2. Ask:

   > Use Uncovr to reconstruct the existing product context of this repository. Propose the scope before analysing.

3. Answer the agent at its two stops:
   - **Scope:** confirm or change what it proposes to analyse, and say whether you also want a wiki.
   - **Review:** read the baseline it wrote and answer its open questions.

That is the whole loop. The rest of this page explains what you get and how to read it.

## What you get

Everything is written to `product-context/` in your repository, in the language you write in.

| File | Answers the question |
| --- | --- |
| `overview.md` | What is this product, what was analysed, and who could clarify what is still unknown? |
| `features.md` | What can users do today, and which features are the riskiest to touch? |
| `domain.md` | Which business terms and rules does the code enforce, who may do what, and which fields hold personal data? |
| `architecture.md` | How is it built, what does it depend on, how is it deployed, and where does change concentrate? |
| `traceability.md` | Which files and tests support each rule, and which sources were consulted? |
| `validation.md` | What must a person decide, what was already decided, and where do sources disagree? |
| `evidence.jsonl` | The index behind all of the above: one claim per line, with its sources. |

Progress is kept in `.uncovr/state.json`, so a run can be resumed or extended later. If you asked for one, `product-context/wiki/` holds the wiki (see *Publish as an LLM wiki*).

### What it looks for

Beyond features and rules, Uncovr brings out what is easy to miss in a legacy system. The checklist behind it, in `references/repository-signals.md`, follows the topics of the SWEBOK Guide v4.0.

- **Behaviour:** business parameters (hard-coded or configurable), feature flags, scheduled jobs and background workers, and the acceptance criteria the tests already assert.
- **Access and data:** who may do what (a role × action matrix) and which fields hold personal data — names only, never values.
- **Structure:** a compact technology stack, components with their boundaries and data flows, dependencies, deployment and known debt.
- **Risk:** a criticality rating per feature, so the riskiest questions come first, and where changes and fixes concentrate in the Git history.
- **Context:** the purpose, users and objectives a business source declares, kept apart from what the code shows; a glossary that puts each term's meaning in the code next to its business definition and any ambiguity.

## How to read a claim

Each statement in the baseline is a **claim** with a stable ID — `F-` for features, `BR-` for business rules, `ARCH-` for architecture, `CTX-` for context assumptions. The documents cite the ID; `evidence.jsonl` holds the details. From the bundled example:

```json
{"id": "BR-002", "kind": "business_rule",
 "summary": "Requests above the approval limit need an approver whose address ends in @finance; the code sets the limit at 5000, the README at 10 000.",
 "confidence": "contradicted", "business_validation": "pending",
 "evidence": [{"type": "code", "ref": "src/requests.py", "line_start": 3, "line_end": 3},
              {"type": "code", "ref": "src/requests.py", "line_start": 19, "line_end": 20},
              {"type": "document", "ref": "README.md (Purchase requests)"}]}
```

Every claim carries **two separate labels**. Keep them apart: code that clearly does something may still be a bug or an obsolete rule.

| `confidence` — what the sources show | `business_validation` — what a person decided |
| --- | --- |
| `confirmed`: directly shown by code, tests or configuration | `pending`: nobody has decided yet (the default) |
| `inferred`: plausible from partial signals | `approved`: a named person accepted it, on a recorded date |
| `gap`: no source supports a statement | `rejected`: a named person declined it |
| `contradicted`: sources disagree | `not_applicable`: no business decision applies, e.g. a technical fact |

Uncovr only ever sets the left column. The right column changes only when you answer — and it records who answered and when. CODEOWNERS, commit authors and repository accounts never count as business approval.

## How a run goes

| Stage | What the agent does | What you do |
| --- | --- | --- |
| 1. Scope | Proposes what to analyse, which modules first and what to exclude. | **Confirm or change it**, and choose a wiki or none. Nothing is explored before you confirm. |
| 2. Explore | Maps the system: modules, entry points, stack, configuration, history. | Nothing. |
| 3. Analyse | Reconstructs features, journeys and rules, each with evidence. | Nothing. |
| 4. Validate | Re-checks the baseline — in a separate context when your agent supports subagents — and runs a structural check. | Nothing. |
| 5. Review | Stops with a summary and a prioritised list of questions. | **Answer the questions.** Approve, reject or correct claims. |

Confirming the scope does not approve any business rule. When a question is answered, it moves to *Decisions* in `validation.md`; a decision is reopened only when new evidence appears.

**Extending later.** For another feature or module, ask the agent to extend the existing baseline and confirm the additional scope. Existing findings, IDs, evidence, human edits and unanswered questions are preserved. If the implementation changed, the affected evidence is rechecked rather than old approvals carried silently into new conclusions.

**Diagrams.** Where a picture is clearer than text, a document can carry a small Mermaid diagram — components and flows, a journey or sequence, states, verified entities, or links between features and rules. It is drawn only from recorded claims, whose IDs appear in the sentence before it. Many documents need none, and every document still reads correctly where Mermaid does not render.

## When it activates

Ask your agent things like:

- "I inherited this codebase. What does it actually do?"
- "Map the business rules the code enforces before we change the approval flow."
- "Rebuild the product context so the PO can plan the next version."

It does **not** activate to write or fix code, specify new features, or review a pull request.

## Use through Agensi

1. Open the repository in an agent that can read its files and write the baseline. Connect that agent to [Agensi through MCP](https://www.agensi.io/docs/mcp-setup) and obtain access to the listing.
2. Ask: "Use Uncovr to reconstruct the existing product context of this repository. Propose the scope before analysing."
3. Confirm the proposed scope and whether you want a wiki. Review the generated baseline and answer its outstanding questions.

There is no local installation for Agensi delivery:

- The agent loads instructions, references and templates on demand.
- Helper scripts run unchanged in private temporary files and are removed afterwards.
- The only persistent outputs are `product-context/` and `.uncovr/state.json` — not a copy of the skill, its templates or its scripts.
- Agensi does not clone the target repository or supply a Python runtime.

An independently installed local copy follows the same workflow but reads its supporting files from its installed skill folder. The optional named VS Code agents (**Uncovr** and **Uncovr Validator**) are local conveniences, not Agensi requirements. When a separate worker is unavailable, the validation report says that the review was not independent.

## Publish as an LLM wiki (optional)

At the scope stop you can choose a wiki: **Obsidian**, **MkDocs** or **Google Knowledge Catalog**. Uncovr then also writes `product-context/wiki/`, an [Open Knowledge Format](https://github.com/GoogleCloudPlatform/open-knowledge-format) v0.2 bundle: the six documents plus one page per claim, linked to each other, with its sources, who verified it and whether it is still a draft.

| Target | What you get | What you do next |
| --- | --- | --- |
| Obsidian | Relative links, claim IDs as aliases | Open `product-context/wiki` as a vault |
| MkDocs | Relative links and `product-context/mkdocs.yml` | `mkdocs serve -f product-context/mkdocs.yml` |
| Google Knowledge Catalog | Bundle-root links, OKF as the catalog ingests it | Push it with Knowledge Catalog's OKF tooling in your Google Cloud project |

Keep in mind:

- The wiki is rebuilt from the baseline on every run. Make corrections and approvals in the baseline, never in the wiki.
- Mermaid blocks are copied unchanged. Obsidian renders them; plain MkDocs shows them as code unless a theme or plugin you choose renders them. Uncovr adds no renderer and no images.
- Uncovr never publishes to a service; the last step is yours.

## Try it on the example first

`examples/order-approval/` holds a small purchase-request app (`app/`) and the baseline a good run produces (`expected/`). It is the quickest way to see what to expect:

- Start with `expected/overview.md`, then `expected/validation.md` to see the questions a PO would be asked.
- One rule is deliberately contradictory: the code sets the approval limit at 5000, the README at 10 000. The expected baseline leaves `BR-002` `contradicted` and asks you about it, instead of picking one.
- Some claims stay `gap` — for example, rejection notifications that are only a TODO — and none is business-approved.

## Requires

- An agent with repository read/search tools and permission to write `product-context/` and `.uncovr/state.json`.
- Agensi mode: an authenticated MCP connection and permission to create, execute and remove private temporary scripts. No skill installation or dependency installation is required.
- Optional: `git`, to pin revisions, read change history and link sources on GitHub.
- Optional: Python 3.10+ and a terminal for the helper scripts. None of them uses the network or prints author identities.

| Script | Purpose | Writes |
| --- | --- | --- |
| `scripts/check.py` | Checks the baseline's structure | Nothing |
| `scripts/history.py` | Measures where change and fixes concentrate in Git history | Nothing |
| `scripts/okf.py` | Exports the wiki | Only `product-context/wiki/` and `product-context/mkdocs.yml` |

Without Python, analysis still proceeds and the baseline says which steps were not executed; a wiki cannot be exported.

## Compatibility and validation

Two local pilot rounds with GitHub Copilot in VS Code on version 0.4.0 covered an initial baseline and extension to a second workflow. They used local skill files and the optional named Validator, not Agensi delivery. They do not establish the quality of every claim or the reliability of the updated MCP contract.

Claude Code is a target environment but has not yet been evaluated. The full Agensi MCP workflow has not yet been verified. Local packaging and isolated-script tests are not end-to-end agent evaluations; do not interpret them as marketplace approval or cross-agent certification.

## Limits

- The structural check proves that IDs, paths and line ranges are well formed — not that a claim is true.
- Completeness cannot be inferred from claim counts.
- Runtime-only behaviour and third-party integrations may remain gaps. A checkout shows deployment configuration, not what actually runs in production.
- Uncovr describes the system as it is and never changes its code. It does not produce implementation plans or task lists unless you ask for them separately.

## Glossary

- **Baseline:** the set of documents in `product-context/` plus `evidence.jsonl`, describing the system as it is at a recorded Git revision.
- **Claim:** one testable statement with a stable ID, a confidence, a business validation and its evidence.
- **Evidence:** a pointer to where a claim comes from — a file and line range, a test, configuration, Git history or a named document.
- **Gap:** something the sources do not show. Uncovr records it and asks; it never guesses.
- **Decision:** a person's answer to a question, recorded with who decided and when, and kept even if later replaced.
