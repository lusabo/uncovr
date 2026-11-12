# Domain Model and Business Rules

<!-- TODO: Reconstruct domain terms and rules; separate observed code behavior from business approval. -->

## Glossary
Terms that matter to the scope. What the code does with a term is not what the business says it means.

| Term | Meaning observed in code | Business definition | Ambiguity | Claim IDs |
| --- | --- | --- | --- | --- |
| To investigate | Unknown | Gap until a business source defines it | Unknown | Pending |

- Meaning observed in code: what the code does with the term, from the claims that show it. Identifier names alone are not meanings.
- Business definition: only what a business source states, with its claim (`inferred`, `pending` until a person confirms it); otherwise `gap`. Never copy the observed meaning here.
- Ambiguity: where the two differ, a term with several meanings, or synonyms. A material disagreement for the same case is a `contradicted` claim; a difference that depends on unreviewed context is a question.

## Central entities and relationships
Add only relevant entities, with cardinality when verified. An `erDiagram` only for verified relationships.

## Rules
| Rule ID | Trigger | Preconditions | Outcome | Exceptions | Evidence claim | Business validation |
| --- | --- | --- | --- | --- | --- | --- |
| Pending | Unknown | Unknown | Unknown | Unknown | Pending | Pending |

## States
States and allowed transitions, when meaningful to product evolution. A `stateDiagram-v2` only when a sentence would not do; follow *Diagrams* in the evidence contract.

## Permissions
| Role | Action | Allowed | Condition | Evidence claim |
| --- | --- | --- | --- | --- |
| Not yet reviewed | | | | |

## Sensitive data
| Entity.field | Category | Stored in | Retention or deletion | Evidence claim |
| --- | --- | --- | --- | --- |
| Not yet reviewed | | | | |

Field names and categories only; never values.
