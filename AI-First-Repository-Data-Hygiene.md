# AI-First Repository & Data Hygiene

## Research and design packet for AI-native and agent-assisted software projects

Prepared 6 September 2026. A reusable design reference, not a prescribed technology stack or an implementation mandate.

### Editorial and evidence note

This generalized edition reconstructs the packet from the referenced conversation, its 45-item reading corpus, and the three user-supplied web archives. The earlier generated Markdown attachment was not available through the conversation export. The synthesis is therefore a fresh consolidation rather than a line-by-line revision of that file. Appendices A and B preserve the supplied article text; their original examples, terminology, model names, and opinions remain attributable to their authors. Page navigation and subscription controls are excluded. The two partial Provencher archives are joined in reading order.

The recommendations below are design judgments informed by the corpus. Standards document specific concepts or mechanisms; engineering reports describe experience in particular environments; papers and benchmarks establish results under their own experimental conditions. None establishes a universal repository architecture. The corpus is retained as a reading program, not a claim that every source has been independently revalidated for this edition.

## 1. Purpose and governing principle

An AI-first repository should make useful work easy to discover, perform, verify, and resume. Its quality depends on canonical ownership, appropriate representation, provenance, validation, reproducibility, and selective context—not the number of agents, databases, instructions, or workflow stages it contains.

**Simple changes must remain simple. Complexity must justify itself.** Every persistent instruction, required artifact, abstraction, handoff, validation step, and approval gate should address an observed failure or a material risk. Remove mechanisms whose cost exceeds their demonstrated value. This is a design constraint, not permission to skip necessary safeguards.

Anthropic recommends starting with the simplest workable solution and increasing complexity only when outcomes justify it. Its engineering account is useful support for evaluating agent workflows on results and operational cost rather than sophistication. [Building effective agents](https://www.anthropic.com/engineering/building-effective-agents)

A request to change a button label should normally require inspecting the relevant component, making the edit, checking the affected result, and reporting completion. It should not automatically trigger a repository audit, several skills, a planning document, a full test suite, multiple approvals, and a handoff report.

Use this packet selectively. A small utility may need only clear instructions, ordinary source files, and targeted checks. A collaborative application may need durable state, explicit ownership, and stronger recovery controls. A large data pipeline may justify more extensive lineage. The same principles apply without requiring identical machinery.

## 2. Separate responsibilities before choosing formats

| Responsibility | Question it answers | Suitable starting point |
|---|---|---|
| Instructions and authority | What may the agent do, and what defines completion? | Short repository instructions and scoped rules |
| Specialized workflow guidance | What unusual knowledge does this task require? | A selectively loaded skill, reference, or tool help |
| Application and domain state | What is true now? | Existing authoritative service or transactional datastore |
| Work coordination | What is active, blocked, or complete? | Existing issue tracker, compact task record, or structured local state |
| Durable agent memory | What verified experience should help later work? | Small curated records with evidence, scope, and expiry |
| Knowledge and rationale | What should a person or agent read and understand? | Markdown, source documents, and concise decision records |
| Events and diagnostics | What happened? | Structured logs or append-oriented records |
| Artifacts | What was produced, from which inputs? | Native files plus appropriate manifests and lineage |
| Derived indexes and views | How can authoritative information be found or displayed? | Rebuildable search indexes, caches, and exports |

These are logical responsibilities, not mandatory folders, services, or tables. One component can serve several roles if its ownership and behavior remain clear. Do not create another state store when an existing system already provides the required authoritative record.

## 3. Representation follows semantics

Markdown is appropriate for prose, explanations, research, design rationale, and reviewable human-authored knowledge. Agents can search and interpret it. A document does not become unsuitable merely because an agent reads it.

Use structured representations when consumers need reliable filtering, joins, validation, updates, or transactions. SQLite can be a good local application-state format; a server database may better fit shared deployment and concurrent-write requirements. JSON is useful for interchange, JSON Lines for append-oriented events, and TOML or YAML for configuration when supported by the existing toolchain. Select formats for actual operations and deployment constraints.

| Information | Reasonable representation | Main caveat |
|---|---|---|
| Architectural reasoning | Markdown decision record | State whether it is accepted, superseded, or proposed |
| Small stable settings | Existing configuration format | Validate types and allowed values |
| Related mutable records | Relational database | Enforce relationships and transaction boundaries |
| Machine output exchanged between tools | Schema-validated JSON | A JSON blob alone does not establish semantic correctness |
| Ordered diagnostic events | Structured logging or JSON Lines | Define retention and avoid secrets |
| Large analytical tables | Columnar files or analytical datastore | Preserve schema, units, and partition meaning |
| Images, audio, and other binaries | Native asset format | Track identity, ownership, and derivation |
| Search embeddings | Derived index | Preserve links to authoritative source versions |
| Office documents and PDFs | Ingestion, collaboration, interoperability, or delivery formats | Preserve originals; extracted text may lose structure |

Office and PDF formats are usually poor choices for canonical internal machine state. They may nevertheless be authoritative external source documents or the user's chosen authoring format. Preserve that authority and retain the original alongside any normalized extraction. Never quietly elevate an extracted approximation or exported report into the source of truth.

## 4. Canonical ownership and data hygiene

For each meaningful category of data, identify one authoritative owner and representation. A status repeated in an issue tracker, database, and Markdown report must have a defined authority and refresh direction. Derived copies should identify their source and freshness; they should not become competing editable masters.

Start with a short inventory when ambiguity exists:

| Category | Canonical owner | Identity/version | Derived consumers | Recovery method |
|---|---|---|---|---|
| Source code | Repository | Commit and path | Build outputs | Version control plus remote copy |
| Runtime records | Application datastore | Record ID and revision | UI and reports | Consistent backup and restore |
| Reference document | Source registry or authoritative service | Source ID and captured version | Extracted text and search index | Retained original or retrievable snapshot |
| Generated artifact | Artifact store | Artifact ID and content hash | Published export | Retain output or regenerate where feasible |

Use stable identifiers independent of display names and file paths. Distinguish identity from version: the same logical record can have several revisions. Record units, timestamp conventions, null semantics, and enumerated states where ambiguity would cause errors. Validate data at entry points and enforce critical constraints in the authoritative layer.

Deduplicate using identifiers or explicit matching rules; a hash detects identical bytes, not equivalent meaning. Keep originals and normalized derivatives distinguishable. Define whether deletion removes, restricts, or invalidates dependent objects. Make imports repeatable without creating duplicate records, and make partial failures visible and recoverable.

Data hygiene includes privacy and lifecycle management. Avoid storing credentials or unnecessary personal information in logs, memory, fixtures, or source control. Apply access and retention rules to derived copies too. More persistent memory is not automatically better memory.

## 5. Prefer mechanical safeguards

Enforce important boundaries through types, schemas, foreign keys, transactions, tests, linters, dependency rules, and narrowly scoped tool permissions where practical. These controls reduce reliance on reminders and repeated discussion. The objective is to make invalid states difficult to create while permitting autonomy inside established boundaries.

For example, a generic artifact-reference relationship can prevent accidental deletion of a referenced source:

```sql
PRAGMA foreign_keys = ON;

CREATE TABLE sources (
    id TEXT PRIMARY KEY NOT NULL
);

CREATE TABLE artifact_sources (
    artifact_id TEXT NOT NULL,
    source_id TEXT NOT NULL REFERENCES sources(id) ON DELETE RESTRICT,
    PRIMARY KEY (artifact_id, source_id)
);
```

This is a focused illustration, not a complete schema. SQLite foreign-key enforcement must be enabled and verified for each connection; merely declaring a constraint is insufficient in configurations where enforcement is off. [SQLite foreign-key documentation](https://www.sqlite.org/foreignkeys.html)

Mechanical enforcement also has costs. A brittle rule can block valid work. Test safeguards against the actual failure they address, provide actionable errors, and remove redundant checks. Do not replace a procedural checklist with an equally excessive collection of automated gates.

## 6. Task friction tiers

Choose the lightest workflow sufficient for the actual effects, uncertainty, and reversibility of the task. These tiers are an internal routing aid, not another form the user must fill out. Scope changes can justify changing tiers; a one-line production permission change can carry more risk than a large isolated refactor.

| Tier | Typical task | Expected process | When to involve the user |
|---|---|---|---|
| 0 — Trivial and local | Typo, label, isolated presentation adjustment | Inspect relevant material, edit, perform a proportional check, finish | Only if intended wording or effect cannot be inferred |
| 1 — Bounded implementation | Local bug fix, small feature, contained query correction | Read affected code and nearby contracts, implement, run targeted validation | Missing product decision or action beyond existing authority |
| 2 — Architectural or broadly coupled | Shared API behavior, ownership boundary, substantial data-model change | Investigate dependencies, compare a few options, record consequential rationale, validate affected interfaces and recovery | A material unresolved tradeoff requiring user judgment |
| 3 — Destructive or externally consequential | Irrecoverable deletion, production access changes, irreversible publication | Establish exact scope and authority, prepare recovery where possible, validate, execute and verify within authorization | Before an action whose consequences exceed granted authority |

Do not re-request permission for already authorized work. A risk tier does not itself require repeated approvals. Plans, decision records, and broad test runs should be added only when they help manage real complexity. Completion means the requested outcome is implemented and proportionately verified, with remaining limitations reported honestly.

Assess friction with a small sample of representative tasks: time to first useful action, unnecessary context loaded, user interruptions, redundant artifacts, repeated tests, recovery effort, and defect rate. Prefer periodic sampling over building a measurement platform. Evaluate reliability gained per unit of complexity and friction introduced.

## 7. Instructions, skills, and selective context

Keep globally loaded instructions short and durable: project purpose, authoritative entry points, important constraints, permission boundaries, and completion expectations. Put task-specific detail near the relevant component or in a narrowly triggered skill. Use existing tool conventions rather than inventing a parallel instruction hierarchy.

A skill should solve a recurring specialized problem. Its description should make applicability clear; its root should expose enough information to select the relevant supporting material. Avoid overlapping triggers, duplicated policies, broad demands to read everything, and model-specific assumptions presented as timeless rules.

Context should be assembled for the task: current request, relevant files, applicable constraints, and only the state or evidence needed to proceed. A compact startup summary may help resumable work, but it should report source and freshness, omit unrelated history, and degrade gracefully when optional memory is unavailable. Do not turn startup into an expensive mandatory scan.

Keep retrieved documents, tool outputs, and saved observations distinct from governing instructions. An article or historical note can contain imperative language without gaining authority over the current task. Scope retrieved memory by project, branch or environment when relevant, and recheck volatile facts against the current system.

## 8. Agent memory and coordination

Memory is a lifecycle, not a file extension. Separate temporary work state, diagnostic events, tentative observations, verified reusable knowledge, and accepted decisions. Persistence alone does not establish truth or relevance.

A minimal reusable memory record might contain an ID, concise observation, supporting evidence, scope, creation time, verification status, and an invalidation condition. Add fields only when a consumer needs them. For changing external behavior, record the relevant version and a review date. Prefer links to authoritative facts over copied descriptions that will drift.

Promote a recurring observation only after checking its evidence and applicability. A repeated failure can justify a regression test or a tooling fix; a durable architectural decision can justify a short decision record; a repeated specialized process can justify a skill. Do not indefinitely preserve the same rule in memory, instructions, and documentation as independent authorities.

Retire superseded observations, deduplicate similar entries, and prevent summaries from erasing uncertainty. High retrieval frequency is evidence of use, not proof of correctness. Error capture should distinguish expected failures from actionable defects, redact sensitive data, and have a retention policy.

For multi-agent work, define ownership of writable resources, completion criteria, cancellation, and conflict handling before relying on shared state. A database is not by itself a scheduling or locking protocol. Use parallel agents only where independent work and coordination costs justify them; ordinary tasks need no mandatory handoff machinery.

Evaluate memory against a simple baseline: can representative tasks resume correctly and avoid known mistakes with the existing repository and search? Add richer retrieval only when it improves that outcome at acceptable latency and maintenance cost.

## 9. Provenance, lineage, and reproducibility

W3C PROV supplies a useful conceptual vocabulary: entities, activities, and responsible agents, linked through generation, use, and derivation. A project can borrow these concepts without implementing an ontology service. [PROV-DM](https://www.w3.org/TR/prov-dm/)

```text
Original reference (entity)
        ↓ used by
Extraction run (activity) ← extractor/version (responsible software)
        ↓ generates
Normalized text (entity)
        ↓ used by
Analysis run (activity) ← model/tool configuration
        ↓ generates
Report (entity) → exported document (derived entity)
```

For consequential generated artifacts, record the source identities and versions or hashes, relevant extraction locations, transformation or prompt-template version, tool/model identity and available configuration, code revision, run ID, timestamp, and output hash. Record the exact submitted context when permissible and necessary for investigation; otherwise record protected references and the limits this places on replay.

Scale detail to the use case. A disposable preview may need little metadata; an externally relied-upon report needs enough lineage to investigate its claims. Provenance tells us where an output came from, not whether the source was accurate or the model's inference valid. Distinguish source statements, derived conclusions, and unresolved uncertainty.

Distinguish three reproducibility goals:

1. **Traceability:** reconstruct which inputs and processes produced the artifact.
2. **Replayability:** rerun the documented process with available inputs and tools.
3. **Deterministic reproduction:** produce identical bytes under controlled conditions.

AI generation can meet the first goal without guaranteeing the third. Seeds and recorded settings do not ensure deterministic output from a changing hosted model. Preserve actual outputs and verification results when exact historical evidence matters. For deterministic transformations, control hidden inputs such as dependency versions, timestamps, locale, ordering, and randomness. The corpus includes Reproducible Builds and SLSA as deeper references, not universal compliance requirements.

## 10. Git, runtime state, recovery, and portability

Let Git own source history, reviewed configuration, schemas, and authored documentation where appropriate. Let the application datastore own runtime records. Avoid inventing a second version-control system inside a memory database; reference commits when needed. Keep generated caches rebuildable and distinguish intentional checked-in artifacts from accidental output clutter.

A repository commit is not a consistent backup of a running database. Use an appropriate database backup mechanism, retain necessary assets, and verify that restoration recovers a usable system. Define acceptable loss and recovery time based on the project's needs. Protect recovery copies against the same failure modes as primary data where practical.

Local-first design can improve ownership, offline use, and portability, but local storage is not a universal requirement. Collaborative or hosted applications may need centrally managed services. Prefer exportable formats and documented ownership so the system remains understandable and recoverable regardless of hosting arrangement. Introduce synchronization, remote databases, or distributed coordination only for actual requirements.

## 11. Evidence-based challenges to the source articles

| Claim or recommendation | What is useful | Challenge and evidence | Generalized design implication |
|---|---|---|---|
| Han: replace agent-facing Markdown with database memory | Repeated structured state benefits from queryable records | Letta's filesystem memory benchmark supplies a counterexample to universal database superiority; its findings are benchmark-specific | Compare candidate representations on real retrieval and update tasks |
| Han: three tables provide typed coordination | A compact prototype can reduce document sprawl | The supplied schema constrains some labels but stores coordination content as text; it does not validate payload semantics or enforce all lifecycle relationships | Add only the constraints and transaction rules the workload requires |
| Han: ambient startup context avoids retrieval friction | Resumption can be faster with a concise relevant summary | Unfiltered history can introduce stale facts and unnecessary tokens; retrieval quality and freshness remain separate problems | Bound and scope startup context, with authoritative references |
| Han: durable learnings accumulate value | Evidence from previous work can prevent repeated errors | Permanence does not prevent obsolete advice, duplication, or sensitive-data retention | Use verification, invalidation, consolidation, and deletion |
| Han: the database becomes the source of truth | Explicit authority reduces conflicting state | Prose rationale and accepted decisions still benefit from reviewable documents; the corpus includes ADR practice | Assign authority by information category rather than consumer type |
| Provencher: reduce accumulated scaffolding | Redundant global instructions can obstruct simple work | The supplied article itself notes differences between models; reliable boundaries and specialized constraints may still matter | Remove obsolete ceremony using representative task checks |
| Provencher: allow more local autonomy | Clear completion and authority boundaries reduce needless stopping | Capability does not grant authority for irreversible or external actions | Define effects the agent may authorize itself, preserving existing user intent |
| Either article treated as a universal architecture | Both reveal useful failure modes | Practitioner accounts are not controlled proof across all projects; Anthropic explicitly advocates adding complexity only as needed | Adopt the smallest effective mechanism and revisit it as evidence changes |

The filesystem comparison is a reason to test alternatives, not a claim that files always win. [Letta memory benchmark](https://www.letta.com/blog/benchmarking-ai-agent-memory/)

Similarly, FAIR principles, PROV, data-product ownership, and supply-chain provenance offer reusable concepts without implying that a small project needs enterprise governance, a knowledge graph, or a full attestation service.

## 12. Candidate generic repository structure

This is a menu of responsibilities. Preserve an existing coherent framework layout; create only the portions the project needs. Runtime stores and external sources may live outside the checkout.

```text
project/
├── README.md                 # Purpose and practical entry points
├── AGENTS.md                 # Concise durable agent guidance, if supported
├── src/                      # Application and domain implementation
├── tests/                    # Proportional automated verification
├── docs/
│   ├── architecture/         # Current boundaries and system explanation
│   ├── decisions/            # Consequential accepted decisions
│   └── reference/            # Human-readable supporting knowledge
├── schemas/                  # Data contracts where needed
├── scripts/                  # Small deterministic operational tools
├── skills/                   # Optional; use the tool's actual discovery path
├── data/
│   ├── README.md             # Ownership, location, retention, recovery
│   └── fixtures/             # Safe, reviewable test inputs
├── assets/                   # Native assets owned by this project
└── artifacts/                # Optional generated outputs and manifests
```

The tree deliberately does not mandate a memory database, vector index, orchestration framework, agent team, source registry service, or elaborate documentation system. Add those when an observed need justifies them. Label generated paths and configure version-control exclusions deliberately. Protect user-supplied and synchronized reference material from incidental edits.

## 13. Open research questions

These thirteen questions keep the design provisional. Resolve those that affect the next concrete decision; do not turn them into prerequisites for ordinary work.

1. Which information is actually queried or updated structurally, and which benefits most from authored prose?
2. Where does the current project have conflicting authoritative copies, and what is the smallest correction?
3. At what workload do database-backed memory and retrieval outperform repository search and compact files?
4. What evidence is sufficient to promote an observation into durable memory, a test, a decision record, or a skill?
5. How should stale, contradictory, or sensitive memory be invalidated and removed?
6. What startup context improves resumption without increasing distraction or latency?
7. Which model-dependent instructions remain beneficial across the agents that actually use the repository?
8. Which invariants can be enforced mechanically with less friction than procedural rules?
9. What provenance detail is necessary for the project's real review, debugging, and trust requirements?
10. Which outputs require exact reproduction, and where are traceability and retained outputs sufficient?
11. Which requirements justify local-first operation, shared services, or synchronization?
12. When does parallel agent work improve outcomes enough to offset conflicts, handoffs, and supervision?
13. What task sample and measures will reveal whether a proposed safeguard reduces errors without making simple work unnecessarily difficult?

## 14. Generic future repository audit brief

The following brief can be supplied to an agent with access to any future repository.

> Audit this repository against the principles in this packet. The assignment is diagnostic and does not authorize a rewrite or implementation changes.
>
> Begin with the project's actual purpose, existing conventions, current user needs, and representative tasks. Read selectively. Do not assume the candidate directory tree or a Markdown/SQLite split is the desired architecture.
>
> Identify where instructions, application state, work coordination, memory, knowledge, diagnostics, and artifacts currently live. Record canonical ownership, duplicated authority, validation gaps, and important recovery dependencies. Use concrete file, record, or workflow evidence. Distinguish observed defects from plausible risks and unknowns.
>
> Inspect globally loaded instructions and skill triggers for obsolete assumptions, conflicting boundaries, unnecessary reading, repeated approvals, and excessive testing or documentation requirements. Trace at least one simple task and one consequential task to assess whether friction matches risk. Do not run destructive operations or expose sensitive records to perform the audit.
>
> Evaluate storage choices against actual query patterns, update frequency, concurrency, review needs, and portability. Examine provenance and reproducibility where outputs depend on external sources or generative processes. Check whether important invariants are enforced by the system or depend on remembering prose rules. Assess backup and recovery evidence without claiming an unperformed restore test succeeded.
>
> Return a concise findings report: what already works; specific gaps and supporting evidence; a small prioritized set of improvements; expected reliability benefit, friction cost, and proportionate verification for each; and unresolved questions that materially affect decisions. Classify components as keep, simplify, strengthen, investigate, or retire where that distinction is useful.
>
> Explicitly identify technologies and patterns this project should not adopt yet. Consider whether existing tools or deleting redundant ceremony solve the problem before proposing new infrastructure. Do not produce speculative implementation stages, mandatory agent teams, or additional tracking documents without demonstrated need. Recommend the smallest useful next action. Preserve the user's existing authorization boundaries and leave implementation for a separately authorized task.

## 15. Research and reading corpus

The original 45 entries are retained below. Priorities are reading guidance, not mandatory prerequisites. Titles and URLs are carried forward from the conversation; consult the source before relying on version-sensitive implementation details. Summaries describe what to investigate, not independently established conclusions. User-supplied article text appears in the appendices; external works are linked rather than reproduced.


| # | Resource | Importance | What we are looking for |
|---|---|---|---|
| — | **AI repositories and context engineering** | | |
| 1 | **Eric Provencher — Rethinking skills and prompts for GPT-6 Astra** | Essential | Minimal instructions, progressive disclosure, decision boundaries |
| 2 | **Aria X. Han — Stop Writing Markdown, Start Writing Memory** | Essential, but challenge critically | Structured memory, startup state, database vs. document storage |
| 3 | [OpenAI — Harness engineering: leveraging Codex in an agent-first world](https://openai.com/index/harness-engineering/) | Essential | Repository as system of record, small `AGENTS.md`, mechanical architectural enforcement |
| 4 | [Anthropic — Effective context engineering for AI agents](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents) | Essential | Context selection, context pollution, retrieval |
| 5 | [Anthropic — Effective harnesses for long-running agents](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents) | Essential | State between sessions, handoffs, long-running development |
| 6 | [Anthropic — Harness design for long-running application development](https://www.anthropic.com/engineering/harness-design-long-running-apps) | High | Planner/generator/evaluator roles, autonomous project work |
| 7 | [Agent Skills specification](https://agentskills.io/specification) | Essential | Formal structure of skills and progressive disclosure |
| 8 | [GitHub — Repository custom instructions](https://docs.github.com/en/copilot/how-tos/copilot-on-github/customize-copilot/add-custom-instructions/add-repository-instructions) | High | Repository-wide vs. scoped instructions |
| 9 | [GitHub — Agent Skills](https://docs.github.com/en/copilot/how-tos/copilot-on-github/customize-copilot/customize-cloud-agent/add-skills) | High | Practical skill boundaries |
| 10 | [VS Code — Context engineering guide](https://code.visualstudio.com/docs/agents/guides/context-engineering-guide) | High | Practical context architecture |
| 11 | [Anthropic — Building Effective Agents](https://www.anthropic.com/engineering/building-effective-agents) | Essential | Strong anti-overengineering counterweight |
| 12 | [Anthropic — Agent Skills engineering](https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills) | High | Why skills exist and where they belong |
| — | **Memory architecture** | | |
| 13 | [Memory for Autonomous LLM Agents: Mechanisms, Evaluation, and Emerging Frontiers](https://arxiv.org/abs/2603.07670) | Essential | Modern memory taxonomy and write/manage/read lifecycle |
| 14 | [Memory in the Age of AI Agents](https://arxiv.org/abs/2512.13564) | Essential | Memory vs. context vs. RAG |
| 15 | [From Storage to Experience: Survey of LLM Agent Memory](https://arxiv.org/abs/2605.06716) | High | Storage → reflection → experience |
| 16 | [Survey on Memory Mechanisms of LLM Agents](https://arxiv.org/abs/2404.13501) | Background | Historical development of agent memory |
| 17 | [Letta — Is a Filesystem All You Need?](https://www.letta.com/blog/benchmarking-ai-agent-memory/) | Essential | Critical counterargument to database-first memory |
| 18 | [A-MEM: Agentic Memory for LLM Agents](https://arxiv.org/abs/2502.12110) | High | Linked note/Zettelkasten approach |
| 19 | [Mem0: Production-Ready AI Agents with Long-Term Memory](https://arxiv.org/abs/2504.19413) | High | Extraction, consolidation and selective retrieval |
| 20 | [Reflexion](https://arxiv.org/abs/2303.11366) | High | Episodic learning from previous attempts |
| — | **Data stewardship and machine-actionable data** | | |
| 21 | [FAIR Guiding Principles](https://www.nature.com/articles/sdata201618) | **Essential** | Findable, Accessible, Interoperable, Reusable data |
| 22 | [W3C PROV Data Model](https://www.w3.org/TR/prov-dm/) | **Essential** | Formal provenance model: Entity, Activity, Agent |
| 23 | [W3C PROV-O Ontology](https://www.w3.org/TR/prov-o/) | Reference | Machine representation of provenance |
| — | **Local-first architecture** | | |
| 24 | [Ink & Switch — Local-first software: You own your data, in spite of the cloud](https://www.inkandswitch.com/essay/local-first/) | **Essential** | Data ownership, offline operation, longevity, local canonical state |
| — | **Database architecture** | | |
| 25 | [SQLite — SQLite as an Application File Format](https://www.sqlite.org/appfileformat.html) | **Essential** | Why SQLite is appropriate for local application state |
| 26 | [SQLite — STRICT Tables](https://www.sqlite.org/stricttables.html) | Essential implementation reference | Preventing weakly typed garbage |
| 27 | [SQLite — Foreign Keys](https://www.sqlite.org/foreignkeys.html) | Essential implementation reference | Referential integrity |
| 28 | [SQLite — Backup API](https://www.sqlite.org/backup.html) | High | Safe database backup and recovery |
| 29 | [Fowler/Sadalage — Evolutionary Database Design](https://martinfowler.com/articles/evodb.html) | **Essential** | Disciplined schema evolution and change tracking |
| 30 | **Refactoring Databases**, Ambler & Sadalage | High | Disciplined database evolution |
| — | **Architecture documentation** | | |
| 31 | [Michael Nygard — Documenting Architecture Decisions](https://cognitect.com/blog/2011/11/15/documenting-architecture-decisions) | **Essential** | Architecture Decision Records rather than huge architecture documents |
| — | **Reproducibility and artifact lineage** | | |
| 32 | [Reproducible Builds — Definition](https://reproducible-builds.org/docs/definition/) | **Essential** | Same input + environment + process → identical artifact |
| 33 | [Reproducible Builds — Documentation](https://reproducible-builds.org/docs/) | High | Timestamps, randomness, environment, ordering and hidden inputs |
| 34 | [SLSA — Provenance](https://slsa.dev/spec/v1.2/provenance) | High | Verifiable “where, when, and how” artifact production |
| 35 | [NIST — Software Bill of Materials guidance](https://www.nist.gov/itl/executive-order-14028-improving-nations-cybersecurity/software-supply-chain-security-guidance-20) | Medium | Component and dependency lineage |
| — | **Version control and content-addressed storage** | | |
| 36 | [Git Book — Git Objects](https://git-scm.com/book/en/v2/Git-Internals-Git-Objects) | High | Content hashes, immutable objects, avoiding duplicate version systems |
| 37 | [Git Internals — Plumbing and Porcelain](https://git-scm.com/book/en/v2/Git-Internals-Plumbing-and-Porcelain) | Medium | What Git already owns vs. what our DB should own |
| — | **Logs and event records** | | |
| 38 | [OpenTelemetry — Logs Data Model](https://opentelemetry.io/docs/specs/otel/logs/data-model/) | **High** | Structured logs with defined semantics rather than miscellaneous text logs |
| 39 | [JSON Lines specification](https://jsonlines.org/) | High | Append-oriented structured events and logs |
| 40 | [RFC 8259 — JSON](https://www.rfc-editor.org/rfc/rfc8259.html) | Reference | Canonical interchange format |
| — | **Plain-text representations** | | |
| 41 | [RFC 7763 — text/markdown](https://datatracker.ietf.org/doc/html/rfc7763) | Reference | Markdown as a standardized plain-text media family |
| 42 | [TOML specification](https://toml.io/en/) | Reference | Human-readable configuration |
| 43 | [YAML 1.2.2 specification](https://yaml.org/spec/1.2.2/) | Reference | Alternative structured configuration |
| — | **Data-product thinking and ownership** | | |
| 44 | [Data Mesh Principles and Logical Architecture](https://martinfowler.com/articles/data-mesh-principles.html) | High, selectively applicable | Domain ownership, data products, computational governance |
| 45 | [Designing Data Products](https://martinfowler.com/articles/designing-data-products.html) | High | Discoverable, understandable, trustworthy data interfaces |


## Appendix A — Eric Provencher

**Rethinking skills and prompts for GPT-6 Astra**

By Eric Provencher (@pvncher). [Original post](https://x.com/pvncher/status/2095991462416490862).

Source: the two user-supplied X web archives. Full supplied article body, joined in reading order with formatting normalized. Embedded illustrations are not transcribed; article prose is preserved. Statements about particular models are the author’s claims in the supplied source, not independently verified product guidance.

Coding agents have come a long way, and best practices are changing fast. What used to require a lot of handholding and scaffolding no longer does.

If you’ve been using agents in your projects over the last year, you’ve likely accumulated a lot of bloated instructions as you worked to steer the models toward good outcomes. With each release, it’s been worth revisiting those assumptions, but with GPT-6 Astra, that’s more important than ever.

These instructions can take many forms, with Skills, AGENTS.md, and your task prompts all shaping how the model gets work done.

### Skill files

One form these instructions can take, is with skill files, which are essentially prompts stored as markdown files, sometimes with bundled scripts. Generally, they are most useful for guidance around a workflow the model only needs for certain tasks, or instructions for using a plugin.

Many people default to downloading a lot of skills into their projects, but that’s a mistake. Each skill comes with a name and description that are loaded into the model’s context so it knows when to use them. Many descriptions are far too long, and when you add too many skills, Codex starts shortening their descriptions to fit. The model ends up seeing less of each description, making it harder to know which skill to pick.

Worse, descriptions can contradict each other or have too much “pick me” energy, leading the model to load instructions that don’t actually help the task.

If you’ve ever asked Codex to create a skill, it probably used the $skill-creator skill. We recently updated its guidance in a few ways to help mitigate many of the failure modes we've seen in practice.

First, skill descriptions should be as short as possible while making it clear when the model should use them.

Here the bad skill description can push the model to use it anytime it touches anything related to a database, vs only when it has to handle a migration.

Second, one of the key markers of a useful skill is progressive disclosure. Reading a skill takes up context, bringing you closer to compaction and introducing guidance that may not apply to the task. For skills with multiple workflows, make the root document a minimal router that points to supporting docs and scripts. Give the model enough guidance to know where to look without forcing it to read things that don’t matter in the moment.

Third, many skills were written as elaborate itineraries or recipes. Models have gotten much better at understanding nuance and ambiguity, so overly specific guidance can now hinder results where it previously helped.

Repository skills also guide other contributors’ agents, which may use different models. Guidance that helps Sol or Luna may overconstrain GPT-6 Astra, so consider which models will use the instructions you leave behind.

### AGENTS.md

Because AGENTS.md applies whenever the model works in your repository, revisit each instruction and ask whether the task still needs it.

Requiring a stack of docs or a full repo map before every edit is excessive for a typo fix. GPT-6 Astra can work out what it needs to read without being pushed to review the whole project before every change.

Prompting the model to read files before every edit, is a great way to burn context and slow work down. Pointing to some docs can still be helpful however, so long as it is contextual. Be sure to keep your docs updated too!

Previous models needed encouragement to run tests and check their work. GPT-6 Astra does that on its own, so the same instructions can lead to unnecessary testing.

GPT-6 Astra is thorough, but it can be more tentative about how far to take a task. Sometimes it needs a little push to keep going. You can use AGENTS.md to give it permission for a specific workflow you know is safe, such as a local test suite:

The local tests use disposable fixtures and have no production access. Run them, fix failures caused by the requested change, and rerun affected tests without asking for approval at each step.

### Decision boundaries

Pay careful attention to how you describe boundaries. If a previous model did things on your behalf without permission, you may have added strong language to make it ask first. That can be useful, but GPT-6 Astra has much better judgment, and you should treat it as such. It also takes your boundaries seriously and may stop work where you’d actually be happy for it to continue.

### Persistence

If you’re used to GPT-5.6 Sol taking a request and continuing for long stretches, GPT-6 Astra can feel more tentative about when to stop. It may reach a first implementation and come back for your review while there’s still work to do.

This is where it helps to define completion before starting. If the task includes getting the implementation running, inspecting the result, and fixing what fails, make that part of the request. A requirement to stop for review after the first implementation will pull the model toward an earlier stopping point, so check whether that’s a decision you actually need to make.

If you want it to keep exploring beyond a first pass, say what you want explored and where it should stop.

A new model is a good opportunity to clean your house. Ask GPT-6 Astra to do an audit based on what was discussed in this article, then go build something you wouldn’t have attempted before!

## Appendix B — Aria Han

**Stop Writing Markdown. Start Writing Memory.**

By Aria Han, 20 February 2026. [Original article](https://medium.com/@ariaxhan/stop-writing-markdown-start-writing-memory-e4a69c57caa9).

Source: the user-supplied Medium web archive. Full supplied article body with formatting normalized and site controls omitted. Code examples are reproduced as supplied, not endorsed as production-ready implementations.

### Stop Writing Markdown. Start Writing Memory.

Since I’ve been coding with AI, it’s always been one big blob of markdown files. It’s the default in all the agentic coding platforms for “planning” mode, and widely accepted as the canonical way to plan and execute a coding task with agentic AI.

Research summaries. Architecture plans. Debug traces. Session notes. Feature requirement distillations. Each one dutifully generated by an AI agent, each one formatted for human consumption, each one completely unqueryable by the very agents that created them.

We’ve settled for a system where machines talk to machines through human-readable documents. Like passing notes in class by printing them first.

### The Markdown Problem

Here’s what happens when you use AI agents to code:

You ask an agent to plan a feature. It writes feature-plan.md. Implementation happens. The plan sits there, never again referenced, slowly drifting from reality. By week three, it’s archaeological artifact.

This is the default behavior of every AI coding assistant. Generate markdown. Pile it up. Hope someone reads it.

The fundamental problem: markdown is a human-readable format being used for machine-to-machine communication.Your agents generate structured knowledge, then immediately flatten it into prose that only humans can parse efficiently.

### The Inversion

What if you use a database as a communication layer?

Not storage you dump things into. Not a backup system. The actual protocol agents use to coordinate.

I rebuilt my agent workflow around a single SQLite file. Three tables: context, learnings, and errors. No markdown generation unless a human explicitly needs to read something.

I call it AgentDB. It changed everything.

### The Startup Hook

Before diving into the schema, here’s what makes this actually work: the session startup hook.

When I open Claude Code, before I type anything, a hook runs. It reads from the database, from git, from the file system (whatever I’ve configured) and injects the result directly into the session context. It’s unique to each folder/repo.

Here’s a sample:

```text
## Git State
Branch: feat/streaming-responses
Changes: M src/chat/stream.ts, M src/api/completions.ts
Recent:
 a3f7c21 feat(chat): SSE streaming for long responses
 8b2e4d9 fix(context): token count before truncation
## Active Contracts
| ID | Goal | Status |
| CR-031 | Streaming responses for messages >500 tokens | in_progress |
| CR-028 | Context window management for long threads | blocked |
## Recent Learnings
| Category | Summary |
| failure | ReadableStream must be returned, not piped |
| pattern | Chunked transfer encoding requires explicit headers |
| gotcha | Vercel edge functions have 25s timeout, not 30s |
## Recent Errors
| Tool | Error |
| Edit | File not found: src/old-path.ts |
| Bash | npm test exit code 1 |
## Active Agents
- steady-pulse (branch: feat/streaming-responses)
- quick-spark (branch: main)
```

The agent sees this before I say a word. It knows what changed recently. It knows what patterns I’ve discovered. It knows what errors occurred. It knows what I was working on.

This is ambient context. No retrieval step. No “let me check my notes.” The context is present before you ask.

The hook can read from anything:
- The database (learnings, checkpoints, contracts, errors)
- Git (branch, commits, file changes)
- File system (folder structure, counts, specific files)
- External APIs (if you want)

The database is the storage layer. The startup hook is the delivery layer. Together, they create ambient context that survives sessions without manual effort.

### The Three Tables

Now let’s look at what gets stored.

context: The Communication Protocol

This replaced every “Hey here’s what I found” markdown file.

```text
-- CONTEXT: Work state (ephemeral per-contract)
-- Types: contract, checkpoint, handoff, verdict

CREATE TABLE IF NOT EXISTS context (
 id TEXT PRIMARY KEY,
 ts TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ','now')),
 type TEXT NOT NULL CHECK(type IN ('contract', 'checkpoint', 'handoff', 'verdict')),
 contract_id TEXT, - links context entries to a contract
 agent TEXT, - which agent wrote this (orchestrator, surgeon, adversary)
 content TEXT NOT NULL - JSON blob
);
```

When the orchestrator assigns work, it writes a contract. The surgeon reads that, writes checkpoints as it works. The adversary reads the contract, checkpoints, and the implementation to write a verdict. All context can easily be transferred to a fresh conversation with handoffs.

All through the database. All queryable. All with typed structure.

No copy-paste relay. No “let me summarize what the previous agent said.” Each agent queries what it needs and writes what the next one will need.

learnings: Knowledge That Compounds

This is where the markdown graveyard problem gets solved.

```text
-- LEARNINGS: Cross-session memory (survives forever)
-- Read these at session start to avoid repeating mistakes

CREATE TABLE IF NOT EXISTS learnings (
 id TEXT PRIMARY KEY,
 ts TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ','now')),
 type TEXT NOT NULL CHECK(type IN ('failure', 'pattern', 'gotcha', 'preference')),
 insight TEXT NOT NULL,
 evidence TEXT,
 domain TEXT, - e.g., 'auth', 'database', 'frontend'
 hit_count INTEGER DEFAULT 0,
 last_hit TEXT
);
```

When an agent discovers something (API returns 500 on expired tokens; this library doesn’t handle concurrent requests; always validate before calling that endpoint) it writes a learning. Typed. Categorized. Queryable.

Recent failures surface automatically at session start. Patterns with high hit counts stay visible. Gotchas resurface before you hit them again.

errors: Automatic Failure Capture

This one is different. Agents don’t write to it directly; hooks do.

I can assign Claude Code the most complex, architecture-spanning task, and the biggest issues won’t be the logic. They’ll be: figuring out how to cd into the right directory, reading a file that moved, calling an MCP tool with the wrong parameters.

These tool errors seem harmless. They compound. One failed Edit leads to a retry, which leads to a different approach, which leads to confusion about what state the file is in. An hour later, you’re debugging the debug session.

```text
-- ERRORS: Automatic capture of failures
CREATE TABLE IF NOT EXISTS errors (
 id INTEGER PRIMARY KEY AUTOINCREMENT,
 ts TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ','now')),
 tool TEXT NOT NULL,
 error TEXT NOT NULL,
 file TEXT,
 context TEXT
);
```

This table captures tool failures automatically via hooks. Edit can’t find a file? Logged. Bash returns non-zero? Logged. MCP server returns an error? Logged. The agent doesn’t decide whether to record it. The system does.

Next session, the startup hook surfaces recent errors: “Edit failed on src/old-path.ts.” The agent immediately knows that file moved or was deleted. It doesn’t waste twenty minutes trying the same path.

Learnings are intentional: “I discovered this pattern.” Errors are automatic: “this tool call broke.” Both matter. Only one requires the agent to remember to write it down.

### The Agent Lifecycle

With the schema in place, here’s how agents actually use it. I made a lightweight Python CLI so they don’t have to deal with SQL syntax.

Session start:

```text
agentdb read-start
```

The agent gets: recent failures to avoid, active patterns, the last checkpoint, any active contract, recent errors. One command. Everything needed to resume.

During work, when something is learned:

```text
agentdb learn failure "Stripe webhook returns 200 but event.verified is false" "found in logs"
agentdb learn pattern "always check verified flag explicitly" "fixed 3 bugs"
```

Session end:

```text
agentdb write-end '{"did":"implemented webhook handler","next":"add retry logic","blocked":""}'
```

This writes a checkpoint. Tomorrow, `read-start` shows exactly where things left off.

Before complex work:

```text
agentdb contract '{"goal":"timeout message after 5s","scope":["src/auth/login.ts"],"constraints":["no new deps"]}'
```

You don’t run these commands. The agents do. The hooks are non-negotiable: every artifact reads on start, writes on end.

### The Point

Here’s the bigger insight:

Representation is the bottleneck.

Not intelligence. Not scale. Not model size. How you structure information for machine consumption determines what machines can do with it.

Markdown is optimized for human eyes. Great for documentation you’ll read. Terrible for knowledge agents need to query.

SQL is optimized for structured retrieval. Terrible for prose. Perfect for typed knowledge with categories, timestamps, hit counts, relationships.

The endless markdown files weren’t a storage problem. They were a representation problem. Information structured for the wrong consumer.

When I switched to SQLite, I didn’t add capabilities. I removed friction. Agents could suddenly query exactly what they needed instead of scanning documents hoping to find relevant passages.

This generalizes beyond agent coordination. Every time you’re tempted to generate a markdown report, ask: who consumes this? If it’s another machine, the answer probably isn’t prose.

### Where This Goes

The database becomes the source of truth. Markdown becomes a rendering layer: something you generate FROM the database when humans need to read it, not something you store.

Session summaries? Query the context table, format as prose.

What did we learn this week? Query learnings, render as bullet points.

What’s the status of this project? Query context for active contracts, generate markdown.

The inversion: markdown is output, not storage. The database is storage. Machines talk to machines through structured queries. Humans get rendered views when they ask.

This is where agentic systems are heading. Not smarter models generating better prose. Smarter architectures where machines communicate in formats optimized for machines.

One SQLite file. Three tables. Zero rotting markdown.

AgentDB is part of the Kernel Claude Code plugin for self-evolving configuration and multi-agent coordination. It comes with the AgentDB and all the agents, commands, hooks, and more detailed in this article.
