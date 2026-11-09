# MVP acceptance and evaluation

## v0.1 structural acceptance

- [ ] Install into a fresh existing repository without overwriting its files.
- [ ] Four discoverable Agent Skills and optional Copilot custom agent are available.
- [ ] Six Markdown templates plus evidence JSONL are scaffolded.
- [ ] Invalid IDs, duplicate claim IDs, missing files, escaping paths and inconsistent approval metadata are rejected.
- [ ] Checking a scaffold reports warnings rather than claiming the baseline is complete.
- [ ] Core tests run using only Python standard library.

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
