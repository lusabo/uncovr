# Repository signals

What to look for in a repository, where it goes in the baseline, and how far to trust it. Consult it in stage 1 to plan what to inspect and in stage 2 to place each finding. The last column cites the related topic of the SWEBOK Guide v4.0 (IEEE Computer Society) as chapter, then section: `4.4.8` is chapter 4, section 4.8.

Fill a section only when a signal exists; otherwise write one line saying it was not observed and where you looked. Never fill a section from naming conventions alone.

| Signal | Where to look | Write to | Default confidence | SWEBOK v4 |
| --- | --- | --- | --- | --- |
| Business parameters | Environment variable reads, `.env.example`, settings and config files, constants with business meaning (limits, rates, deadlines) | `features.md` → *Variants, flags and parameters*: hard-coded or configurable, where set, default | `confirmed` that it exists; its business meaning `inferred` | 4.4.8 |
| Feature flags and variants | Flag SDK calls and flag files, checks on tenant, plan, edition or country, build variants | `features.md` → *Variants, flags and parameters* | `confirmed`; which variant is live is a `gap` | 3.3.8, 8.6.1 |
| Scheduled and background work | Cron files, scheduler configuration, job classes, queue consumers, webhook handlers | `features.md` → *Non-observable behavior* | `confirmed` | 6.1.4, 3.3.2 |
| Permissions | Role and permission enums, policy files, authorization decorators, middleware and guards, route-level checks | `domain.md` → *Permissions*: role × action | `confirmed` per check; the full matrix is only as complete as the routes reviewed | 13.4.1, 13.4.2 |
| Sensitive data | Schema, migration and model fields holding personal, financial, health or credential data; retention, anonymisation and deletion code; consent | `domain.md` → *Sensitive data* | `confirmed` per field; retention without code is a `gap` | 13.4.1, 14.1.7.10 |
| Observed acceptance criteria | `.feature` files, test names, parameterised tests (decision tables), boundary values in assertions, state-transition tests | `features.md` → *Observed acceptance criteria* | `confirmed` behavior; not business intent | 1.4.3, 5.3.1.2, 5.3.1.5, 5.3.1.7 |
| Known defects | Skipped, disabled or expected-failure tests and their reasons | A `gap` or `contradicted` claim and a question in `validation.md` | `gap` | 5.1.2.7 |
| Rule wording | Validation and error messages, translation catalogues | Evidence for the rule the message enforces | Supports `confirmed` only together with the code that raises it | 4.4.8 |
| Preconditions and invariants | Validators, schema constraints (required, length, range), assertions and guard clauses | `domain.md` → *Rules* | `confirmed` | 4.4.4, 11.1.4 |
| States | Status enums, state-machine definitions, transition tables | `domain.md` → *States* | `confirmed` | 4.4.7, 17.5 |
| Technology stack | Runtime version files and manifest fields (engines, `python_requires`, target framework), framework entry points, database drivers and migrations tool, messaging clients, build tool | `architecture.md` → *Technology stack*: one row per technology that shapes a change, never every library | `confirmed` as declared or imported; the version actually running is a `gap` | 2.2.1, 4.2.4 |
| Components and data flows | Entry points, module and service boundaries, data stores and the code that owns each table or collection, queues, caches, file storage | `architecture.md` → *Context and major components* and its *Main data flows* | `confirmed` per traced path; a boundary drawn from folder names alone is `inferred` | 4.4.1 |
| External systems | Outbound HTTP, SDK and messaging calls, connection settings naming hosts or services, webhooks received | `architecture.md` → *Inspection boundary* and the component's external dependencies | `confirmed` that the call or setting exists; the external system's behavior is a `gap` | 4.4.1 |
| Deployment and environments | Dockerfile, compose, Kubernetes and Helm, infrastructure as code, CI/CD pipelines, Procfile, release scripts | `architecture.md` → *Deployment and environments*: configuration found, execution observed, production not confirmed | `confirmed` as configured; observed execution needs `runtime` evidence; what runs in production is a `gap` | 6.3.2, 6.6.1, 2.2.1 |
| Release, storage and compatibility limits | Versioning and release configuration, supported-version declarations, API version prefixes, migrations that cannot be reversed, storage engines and volume settings | `architecture.md` → *Deployment and environments*, only when a source states the limit | `confirmed` as configured; a limit with no source is not recorded | 6.3.2, 6.6.1 |
| Integration contracts | OpenAPI, GraphQL, protobuf and event schemas, generated clients, outbound HTTP and messaging calls | `architecture.md` → *Integration contracts* | `confirmed`; who consumes an inbound API is a `gap` | 4.4.1 |
| Dependencies and licences | Manifests, lockfiles, vendored code, LICENSE and NOTICE files | `architecture.md` → *Change constraints*: only those that restrict a change | `confirmed` | 4.2.4, 14.1.7.4 |
| Known debt | `TODO`, `FIXME`, `HACK`, deprecation markers, suppressed lint rules, flags that are always on or off | `architecture.md` → *Known debt* | `confirmed` that the marker exists; never a requirement | 7.2.3.1 |
| Change history | `scripts/history.py`: commits, churn, fix commits, ticket references, number of authors and last change per module | `architecture.md` → *Regression hotspots*; ticket IDs as recorded intent | `confirmed` as measured at the revision; reading it as risk is `inferred` | 7.1.6, 7.2.4 |
| Recorded intent | CHANGELOG, release notes, ADRs, docs, ticket IDs in files | Origin of features and decisions, as `document` evidence; `traceability.md` → *Sources* with version or date | `inferred` at most; never proof of implementation | 1.2.1, 2.2.4, 8.6.2 |
| External references | Links and identifiers pointing outside the repository: wiki pages, specifications, tickets, dashboards | `traceability.md` → *Sources* as `indicated` or `inaccessible` unless opened | the pointer is `confirmed`; what the target says is a `gap` until consulted | 1.2.1, 8.6.2 |
| Declared purpose, users and objectives | README and product documents, onboarding and help pages, a Product Owner's answers | `overview.md` → *Purpose and users* and *Business objectives and unknowns*, as `assumption` claims | `inferred` at most; absent is a `gap`, never filled from capabilities | 1.2.1 |
| Business vocabulary | Glossaries and product documents for definitions; enums, entity fields, UI labels and messages for observed use | `domain.md` → *Glossary*: meaning observed in code apart from business definition | Observed meaning `confirmed` per claim; a definition `inferred` until a person confirms it; an undefined term is a `gap` | 1.2.1 |
| Measured outcomes | Analytics and telemetry event names, business metrics, alert rules | `overview.md` → *Business objectives and unknowns*, as clues | `inferred` at most | 6.4.2 |
| Ownership and contacts | CODEOWNERS and OWNERS teams, documented support or escalation teams | `overview.md` → *Who can clarify*: role or team, knowledge area, questions they could help clarify | `confirmed` as declared path review or contact; never business authority or approval | 2.1.2 |

## Guardrails

- Sensitive data: record entity, field and category only. Never copy values, sample records, secrets or connection strings.
- Authorship: never rank or name individual contributors; use teams from CODEOWNERS when declared. Neither CODEOWNERS, authors, contributors nor repository accounts show who holds business authority or may approve.
- Capabilities are not intent: what the code does never fills purpose, users, value, objectives or a roadmap.
- Tests show behavior, not intent: a test can encode a bug. A skipped test is a question, not a fact.
- Documents, analytics and ticket references are clues to intent; keep them `inferred` until a person confirms.
- Cost, value, priority and estimates cannot be read from a repository: ask them in `validation.md`.
- A checkout is not production: configuration, lockfiles and the recorded revision show what is declared, not what is deployed.
