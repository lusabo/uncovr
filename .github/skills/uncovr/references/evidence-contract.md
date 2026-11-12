# Evidence contract — v0.1

Uncovr is **evidence-first**. Its assertions live in one JSON object per line of `product-context/evidence.jsonl`. The six human-oriented Markdown artifacts cite stable claim IDs rather than duplicating canonical evidence records.

## Schema

Required claim fields:

| Field | Type | Allowed values / rules |
| --- | --- | --- |
| `id` | string | Unique, stable ID such as `F-001`, `BR-001`, `ARCH-001` |
| `kind` | string | `feature`, `business_rule`, `architecture`, `constraint`, `decision`, `assumption` |
| `summary` | string | Non-empty, one testable assertion |
| `confidence` | string | `confirmed`, `inferred`, `gap`, `contradicted` |
| `business_validation` | string | `pending`, `approved`, `rejected`, `not_applicable` |
| `evidence` | array | Evidence entries; empty only for `gap` |

Optional field: `supersedes`, an array of earlier claim IDs whose assertion this claim replaces, used for a new decision after a reopened one (see *Sources, decisions and reopening*). Baselines without it remain valid.

When `business_validation` is `approved`, also record `validated_by` and `validated_on` (date; human-supplied). A code-confirmed behavior is **not** thereby a currently accepted business rule.

Each evidence entry has `type` and `ref`. `type` is `code`, `test`, `config`, `git`, `runtime`, `document`, or `interview`. For `code`/`test`/`config`, `ref` is a repository-relative path. Include integer `line_start` and `line_end` together when practical. Include Git `revision` (7–40 hexadecimal characters) on local technical evidence. An unknown revision triggers a warning.

External references (`git`, `runtime`, `document`, `interview`) are textual locators with enough information to independently retrieve the source; do not include secrets, personal data, or full interview transcripts. A Git commit is a *clue* to an original decision, not proof of its rationale.

The included CLI verifies record shape, IDs, required fields, local paths, line ranges and cross-references, including claim IDs cited in the Markdown that are missing from the index, and whether the traceability and validation views agree with the index: files named for a claim, source status, contradictions listed, decisions backed by a recorded human decision, and reopenings citing new evidence; and the form of Mermaid blocks (closed fence, supported type, claim IDs cited, non-confirmed confidence named), not whether a diagram is right. It does **not** inspect whether a source supports a claim semantically, verify commit existence, execute tests, or approve business intent.

## Atomic claims and scoped decisions

One claim must be independently testable and decidable. Split assertions that need different confidence levels or independent human decisions before applying approval or rejection to a compound claim.

For an existing claim, propose a focused correction rather than silently replacing its meaning:

1. Keep an existing ID only for an assertion it already covered; allocate unused IDs for the separated assertions. Record the old-to-new ID mapping, the reason and the original decision scope in `validation.md`, preserving the prior decision history.
2. Give each resulting claim its own supporting evidence and confidence. Update the affected Markdown and cross-references; do not delete unrelated claims, human edits or questions.
3. Carry `business_validation`, `validated_by` and `validated_on` only to assertions explicitly covered by the human decision. Undecided business rules remain `pending` without inherited approval or rejection metadata. If the answer's scope is ambiguous, ask instead of assigning it to every clause.

For example, a confirmed date-range validation and an inferred time-validation failure need separate claims. Rejecting the suspected time failure does not reject the date rule or confirm that the failure has been reproduced.

## Source conflicts

Compare sources for the same trigger, actor, state, configuration and revision. A conditional exception, an unreviewed path, or a warning that still permits an operation is not by itself a contradiction.

Keep independently supported facts about configuration and implementation as `confirmed`. If they materially disagree about the same case, record a separate `contradicted` claim citing both sources and the conditions of the mismatch; reuse an existing disagreement claim when it already covers that comparison. Do not hide the disagreement only in prose or manufacture a conflict between different contexts.

Reference its ID in the affected artifacts and keep the index, review findings and final confidence counts consistent. A human choice settles desired behavior, not technical agreement: keep the implementation mismatch visible until fresh evidence supports its resolution. Record that decision without retroactively changing what the reviewed revision did.

## Declared intent, definitions and people

Observed behavior and declared intent are separate claims; neither is rewritten as the other.

- **Observed**: capabilities, rules and the meaning a term has in the code are `feature`, `business_rule` or `architecture` claims with technical evidence. Behavior is not intent: do not turn it into a purpose, a value or a roadmap item.
- **Declared**: purpose, intended users, value, objectives and business definitions of terms are `assumption` claims citing the `document` or `interview` that states them, with IDs such as `CTX-001`. Their confidence is `inferred` at most, since only technical evidence confirms. A person confirms them through `business_validation`; an approved definition stays `inferred`, because the two axes are independent.
- **Unknown**: when no source states the intent or definition, record a `gap` claim with `pending` and empty evidence when it matters to a rule, a question or a planned change; otherwise label it a gap in the Markdown.
- **Declared versus observed**: when a business source and the code disagree about the same case, follow *Source conflicts*. When the difference depends on context outside the reviewed scope, record an `inferred` claim and a question instead.
- **`not_applicable`**: only for a technical fact that no business decision could approve or reject, such as a module layout or a library in use; give the reason in `validation.md` unless it is obvious. Never for a `feature`, `business_rule` or `assumption`, nor for an unknown: missing intent is `gap` and `pending`.
- **People**: record roles and teams, never individuals. CODEOWNERS, commit authors, contributors and repository accounts show who reviews or changed files; they are not evidence of business authority, knowledge or approval. `validated_by` names the person who actually decided, as the Product Owner records it, never someone inferred from the repository.

## Sources, decisions and reopening

`evidence.jsonl` is the only canonical record of evidence and decisions. The tables in `traceability.md` and `validation.md` are views: they cite claim IDs and name files, and never carry their own line ranges, confidence, `validated_by` or `validated_on`.

- **Consulted sources only**: an evidence entry means the source was opened and read at the stated revision or version. A source that another source merely names or links is `indicated`; one whose access failed is `inaccessible`. Neither becomes an evidence entry. List it in the *Sources* view of `traceability.md` and, when it matters, record a `gap` claim naming it, with the pointer that names it as evidence if that pointer was consulted. Do not request credentials or copy whole documents; cite the section consulted.
- **Version or date**: for `document`, `interview`, `runtime` and `git` sources, put the version, date or revision in `ref` when known, for example `Approvals policy, v3, 2026-05-01, section 2`; otherwise say it is unknown in the *Sources* view.
- **Intent is not implementation**: a document, ticket, commit message or interview shows what someone stated or requested. It never makes a behavior `confirmed`; that needs `code`, `test`, `config` or `runtime` evidence.
- **Divergences**: each `contradicted` claim has a row in *Contradictions and review outcomes* naming the claims involved, what each source says, the impact and the decision claim or `pending`.
- **Decisions**: record a human answer as a `decision` claim citing the `interview` or `document` locator where it was given, with `business_validation` `approved` (or `rejected` when the person declines the proposal), `validated_by` and `validated_on` exactly as the person or the Product Owner supplied them. Its confidence is `inferred`: it states intent, not implementation. Only then list it under *Decisions* and move the question out of *Outstanding questions*. Apply a decision to other claims only within its scope, as *Atomic claims and scoped decisions* requires.
- **Reopening**: never edit or delete a recorded decision. Reopen it only when new evidence bears on the decided case — a changed implementation at a newer revision, a newly consulted source, or a contradiction the decision did not consider. Record that evidence as its own claim, mark the decision `reopened` in *Decisions* with the reason and that claim ID, and ask the question again under *Outstanding questions* citing both. A person changing their mind without new evidence is a new decision they give, not a reopening by the agent. When the person decides again, record a new `decision` claim with `supersedes` naming the earlier one, and mark that one `superseded by <ID>`.

## Diagrams

A Mermaid diagram is a view of claims already in `evidence.jsonl`, never a source of its own. Add one only where it answers a question the text or a table answers less clearly; a document may have none, and a short sentence or table is preferred when it is as clear.

| Document | Question | Mermaid type |
| --- | --- | --- |
| `architecture.md` | Which components, boundaries, external dependencies and data flows? | `flowchart` |
| `features.md` | What path does a journey take; in what order do actors interact, when order matters? | `flowchart`, `sequenceDiagram` |
| `domain.md` | Which states and transitions; which entities and relationships, when verified? | `stateDiagram-v2`, `erDiagram` |
| `traceability.md` | How features, rules and components relate, only when clearer than the table | `flowchart` |

- One subject per diagram, about a dozen nodes at most; split anything harder to read. Use plain syntax in a fenced block marked `mermaid`, without themes, styles, click handlers or HTML. No charts of quantities (`pie`, `xychart-beta`, `sankey-beta`, `quadrantChart`, `gantt`).
- Precede it with a sentence saying what it shows and the claim IDs it draws on, so the document reads the same where Mermaid does not render. Name the confidence of every claim drawn that is not `confirmed`, in the label or that sentence.
- Every node and edge comes from a cited claim. Draw an inferred relation with a dotted edge (`-.->`) and say so; leave a gap undrawn and name it in the text. Do not derive cardinality, execution order or transitions from names, configuration from a run, or planned behavior from a TODO or document.

## Architecture and deployment claims

Stack, component, data-flow and deployment statements in `architecture.md` cite claim IDs like any other assertion; the provenance stays here.

- **Configuration found**: `config` or `code` evidence at the recorded revision. `confirmed` means configured, not deployed.
- **Execution observed**: `runtime` evidence whose `ref` names what ran, the environment, the date and how it was observed (command, health endpoint, log excerpt location), without secrets or hosts that should stay private. Run nothing without the permission `SKILL.md` requires.
- **Production not confirmed**: the deployed revision, topology and settings are a `gap` until `runtime` evidence from that environment exists. A `document` or `interview` source raises it to `inferred` at most. A checkout, its lockfiles and the recorded HEAD do not prove the version in production.
- **External systems**: a call site or connection setting confirms the dependency, not the other system's behavior, availability or version; record those as `gap` and say who owns them.
- **Release, storage and compatibility limits**: use kind `constraint`, only with a source that states the limit.

## Example (illustrative, not a claim about a real system)

```json
{"id":"BR-001","kind":"business_rule","summary":"A pending request may be approved by an authorized manager.","confidence":"confirmed","business_validation":"pending","evidence":[{"type":"code","ref":"src/requests.py","line_start":20,"line_end":27,"revision":"a1b2c3d4"},{"type":"test","ref":"tests/test_requests.py","line_start":8,"line_end":22,"revision":"a1b2c3d4"}]}
```

This example belongs in `evidence.jsonl` as exactly one line. The related rule in `domain.md` must reference `BR-001`; the technical sources in this example must actually exist when run in a target repository.

## Confidence rules

- `confirmed`: direct and sufficient *technical* evidence of observable behavior. A function name or comment by itself is not sufficient.
- `inferred`: a plausible hypothesis with some evidence; requires a follow-up or experiment.
- `gap`: unknown, missing evidence, or unobservable intent.
- `contradicted`: material sources disagree; cite all accessible sides.

Do not generate fake evidence to satisfy the checker. If a claim cannot be supported, downgrade it to `gap`. Neither a high count of confirmed claims nor a clean checker result establishes that the product context is complete.
