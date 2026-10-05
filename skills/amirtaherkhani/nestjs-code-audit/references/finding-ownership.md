# Finding Ownership and Deduplication

Assign one primary owner to each root cause. Supporting skills may add impact or verification requirements, but they do not create duplicate findings.

| Evidence | Primary owner | Supporting handoff |
| --- | --- | --- |
| Module cycle, deep import, broad export, cross-feature write | Architecture | OOP may shape collaborators; Features may test wiring/runtime impact |
| Domain/application imports NestJS, ORM, transport, or vendor types | Architecture | OOP reviews the abstraction; Features owns boundary mapping |
| God service, hidden dependency, repeated conditional variation, invariant leakage | OOP/design | Architecture confirms capability ownership; Features confirms lifecycle |
| Guard/pipe/interceptor/filter misuse, public error or API contract | Runtime | OOP models internal failure types; Architecture owns transaction effects |
| Validation, authorization, tenant escape, secret or response leakage | Security | Architecture establishes trust/data ownership; OOP encapsulates policy |
| Missing boundary test, wrong test layer, flaky lifecycle cleanup | Testing | Architecture owns boundary assertions; OOP owns object behavior |
| Compiler parser/type error or ESLint diagnostic | Toolchain | Route the remedy to another owner only when the root cause is semantic |
| Query latency, event-loop blocking, capacity, retry, queue, shutdown | Runtime | Architecture decides service/data boundary changes if measurements justify them |

## Root-cause examples

- An HTTP exception imported by a domain policy is one architecture boundary finding. The runtime skill supplies the transport-mapping remedy; do not add a second OOP and third error-handling finding for the same import.
- A broad `SharedModule` export that enables five cross-feature repository writes is one architecture root cause with multiple evidence locations, unless the writes have independently different risks or owners.
- Fifty lint diagnostics caused by one invalid parser configuration are one toolchain configuration finding plus any diagnostics that remain after configuration is corrected.

## Conflict disposition

If evidence is insufficient to choose an owner or prove impact, place the item under **Needs verification**. The report should prefer a smaller set of defensible findings over a large inventory of possible smells.
