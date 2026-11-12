# Uncovr

Understand what a legacy system does before you change it.

## What this skill does

Uncovr reads an existing repository and writes a **Product Context Baseline** under `product-context/`: an overview, the feature catalogue, the domain and its business rules, the architecture that matters for change, traceability from rules to code and tests, and a validation sheet with the questions only a person can answer. Every claim has a stable ID and points to the file and lines it came from in `evidence.jsonl`.

It also brings out what is easy to miss in a legacy system: business parameters that are hard-coded or configurable, feature flags, scheduled jobs and background workers, who may do what (a role × action matrix), which fields hold personal data (names only, never values), the acceptance criteria the tests already assert, a compact technology stack, components with their boundaries and data flows, deployment, dependencies and known debt. The architecture says what was inspected, what stays unknown and what belongs to external systems, and keeps deployment configuration apart from observed execution: a checkout does not prove what runs in production. The overview keeps what the code does apart from the purpose, users and objectives a business source declares, marks what no source states as a gap, and lists the roles or teams that could clarify each question — never treating CODEOWNERS or commit history as business authority. The glossary shows each term's meaning in the code next to its business definition and any ambiguity. Each feature gets a criticality rating so the riskiest questions come first. Traceability can list the sources behind the claims — what was consulted, what was only pointed to and what could not be opened — and the validation sheet keeps open questions, recorded decisions and divergences between sources apart; a decision is reopened only when new evidence appears. Where a picture is clearer than text, a document can carry a small Mermaid diagram — components and flows, a journey or sequence, states, verified entities, or links between features and rules — drawn only from recorded claims, with their IDs in the sentence before it; many documents need none, and every document still reads correctly where Mermaid does not render. The checklist behind this, in `references/repository-signals.md`, follows the topics of the SWEBOK Guide v4.0.

It separates what the code shows (`confirmed`, `inferred`, `gap`, `contradicted`) from what the business has approved. It never approves anything for you, and it does not change your code.

## When it activates

Ask your agent things like:

- "I inherited this codebase. What does it actually do?"
- "Map the business rules the code enforces before we change the approval flow."
- "Rebuild the product context so the PO can plan the next version."

It does not activate to write or fix code, specify new features, or review a pull request.

## Use through Agensi

1. Open the repository in an agent that can read its files and write the baseline. Connect that agent to [Agensi through MCP](https://www.agensi.io/docs/mcp-setup) and obtain access to the listing.
2. Ask: "Use Uncovr to reconstruct the existing product context of this repository. Propose the scope before analysing."
3. Confirm the proposed scope and whether you want a wiki. Review the generated baseline and answer its outstanding questions; confirming the scope does not approve the business rules.

There is no local installation for Agensi delivery. The agent loads instructions, references and templates on demand. Helper scripts run unchanged in private temporary files and are removed afterwards. The persistent outputs are `product-context/` and `.uncovr/state.json`, not a copy of the skill, its templates or its scripts. Agensi does not clone the target repository or supply a Python runtime.

An independently installed local copy uses the same workflow, but resolves supporting files from its installed skill folder. The optional named VS Code agents are local conveniences, not Agensi requirements. When a separate worker is unavailable, the validation report must say that the review was not independent.

## How a run goes

1. **Scope.** The agent proposes what to analyse and waits for you to confirm.
2. **Explore, analyse, validate.** It maps the system, reconstructs features and rules with evidence, then reviews the result — in a separate context when your agent supports subagents.
3. **Review.** It stops with a summary and the questions for you. Nothing is marked approved until you say so.

For another feature, ask the agent to extend the existing baseline and confirm the additional scope. Existing findings, IDs, evidence, human edits and unanswered questions must be preserved. A changed implementation requires rechecking affected evidence, not silently carrying old approvals into new conclusions.

## Publish as an LLM wiki (optional)

At the start you can choose a wiki: **Obsidian**, **MkDocs** or **Google Knowledge Catalog**. Uncovr then also writes `product-context/wiki/`, an [Open Knowledge Format](https://github.com/GoogleCloudPlatform/open-knowledge-format) v0.2 bundle: the six documents plus one page per claim, linked to each other, with its sources, who verified it and whether it is still a draft. It is rebuilt from the baseline on every run, so corrections and approvals go to the baseline, not to the wiki.

| Target | What you get | What you do next |
| --- | --- | --- |
| Obsidian | Relative links, claim IDs as aliases | Open `product-context/wiki` as a vault |
| MkDocs | Relative links and `product-context/mkdocs.yml` | `mkdocs serve -f product-context/mkdocs.yml` |
| Google Knowledge Catalog | Bundle-root links, OKF as the catalog ingests it | Push it with Knowledge Catalog's OKF tooling in your Google Cloud project |

Mermaid blocks are copied unchanged. Obsidian renders them; plain MkDocs shows them as code unless a theme or plugin you choose renders them. Uncovr adds no renderer and no images.

Uncovr never publishes to a service; the last step is yours.

## Example

`examples/order-approval/` holds a small purchase-request app and the baseline a good run produces. One rule is deliberately contradictory — the code sets the approval limit at 5000, the README at 10 000 — and the expected baseline leaves it `contradicted` and asks you about it, instead of picking one.

## Requires

- An agent with repository read/search tools and permission to write `product-context/` and `.uncovr/state.json`.
- Agensi mode: an authenticated MCP connection and permission to create, execute and remove private temporary scripts. No skill installation or dependency installation is required.
- Optional: `git`, to pin revisions, read change history and link sources on GitHub.
- Python 3.10+ and a terminal for `scripts/check.py` (structure), `scripts/history.py` (change history) and `scripts/okf.py` (wiki export). Without Python, analysis can proceed with those steps explicitly unexecuted; a wiki cannot be exported. None of the scripts uses the network or prints author identities; only the wiki exporter writes project outputs, under `product-context/`.

## Compatibility and validation

Two local pilot rounds with GitHub Copilot in VS Code on version 0.4.0 covered an initial baseline and extension to a second workflow. They used local skill files and the optional named Validator, not Agensi delivery. They do not establish the quality of every claim or the reliability of the updated MCP contract.

Claude Code is a target environment but has not yet been evaluated. The full Agensi MCP workflow has not yet been verified. Local packaging and isolated-script tests are not end-to-end agent evaluations; do not interpret them as marketplace approval or cross-agent certification.

## Limits

The structural check proves that IDs, paths and line ranges are well formed — not that a claim is true. Completeness cannot be inferred from claim counts. Runtime-only behaviour and third-party integrations may remain gaps.
