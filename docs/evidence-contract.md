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

When `business_validation` is `approved`, also record `validated_by` and `validated_on` (date; human-supplied). A code-confirmed behavior is **not** thereby a currently accepted business rule.

Each evidence entry has `type` and `ref`. `type` is `code`, `test`, `config`, `git`, `runtime`, `document`, or `interview`. For `code`/`test`/`config`, `ref` is a repository-relative path. Include integer `line_start` and `line_end` together when practical. Include Git `revision` (7–40 hexadecimal characters) on local technical evidence. An unknown revision triggers a warning.

External references (`git`, `runtime`, `document`, `interview`) are textual locators with enough information to independently retrieve the source; do not include secrets, personal data, or full interview transcripts. A Git commit is a *clue* to an original decision, not proof of its rationale.

The included CLI verifies record shape, IDs, required fields, local paths, line ranges and cross-references. It does **not** inspect whether a source supports a claim semantically, verify commit existence, execute tests, or approve business intent.

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
