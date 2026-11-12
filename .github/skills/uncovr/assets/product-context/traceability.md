# Bidirectional Traceability

<!-- TODO: Connect stable claims to source files, tests and related claims in both directions. Tables here are views: line ranges, revisions, confidence and approvals stay in evidence.jsonl. -->

| Claim ID | Feature or rule | Source files | Tests | Related claims | Impact note |
| --- | --- | --- | --- | --- | --- |
| Pending | Unknown | Unknown | Unknown | Unknown | Unknown |

Name only files that the claim's evidence in `evidence.jsonl` cites; line ranges and revisions stay there. A Mermaid diagram of features, rules and components is optional, only when clearer than this table.

## Sources
Optional: include it when a document, ticket, runtime observation, interview or external reference bears on a claim, or when a source was pointed to but not opened. A row per source, not per claim.

| Source | Purpose | Scope consulted | Version or date | Status | Claim IDs |
| --- | --- | --- | --- | --- | --- |
| Pending | Unknown | Unknown | Unknown | consulted | Pending |

Status is `consulted` (opened and read; only these appear as evidence in `evidence.jsonl`), `indicated` (named or linked by another source, not opened) or `inaccessible` (access attempted and refused or unavailable). A document or ticket records intent or a request, not what the code does.

## Procedure for future change requests
Start from a feature claim; follow its rules, integrations and data dependencies. Return uncertainties to PO/SME before specifying a future version.

## Coverage and known blind spots
Identify modules without mapped capabilities, and capabilities without verifiable evidence. Avoid presenting file coverage as behavioral coverage.
