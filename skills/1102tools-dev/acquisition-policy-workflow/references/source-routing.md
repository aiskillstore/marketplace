# Source routing and operations

## Source roles

- **eCFR:** codified Title 48 baseline, section structure, version history, definitions, and section-level comparison. Resolve the latest available title date before describing content as current.
- **Acquisition.gov:** RFO model text, issuance/update dates, posted agency deviations, and official RFO guidance. The index establishes that a document is posted; the deviation PDF establishes its scope and effective terms.
- **Federal Register:** official publication history, proposed and final rules, effective dates, corrections, withdrawals, notices, public inspection, RINs, and FAR/DFARS cases.
- **Regulations.gov:** docket metadata, related documents, public comments, attachments, and comment-period evidence.
- **Supplied documents:** internal or additional policy evidence. They never become public-query text and do not silently override published sources.

## Minimal call paths

### Current codified text

1. Resolve the latest eCFR date.
2. Retrieve the exact section, subpart, part, clause, or definition.
3. Check Federal Register only if the user asks about a recent amendment or the known effective date is newer than the available eCFR date.

### Agency RFO status

1. List Acquisition.gov deviations by agency and FAR part.
2. Retrieve every matching deviation document when duplicates or multi-part documents exist.
3. Extract scope, effective date, transition treatment, exclusions, incorporated model text, and supersession terms.
4. Retrieve the corresponding model part and eCFR baseline.
5. Check Federal Register only when a related codification or recent effective change matters.

Absence from the posted index means `no posted deviation located`, not proof that no agency deviation exists anywhere.

### Rulemaking history

1. Use Federal Register case history or document search.
2. Separate documents whose title directly names the case from recurring Unified Agenda entries that merely list it.
3. Use Regulations.gov for the docket, related documents, attachments, and comments.
4. Use eCFR only after a final rule is effective and codified, or to compare the baseline.

### Open comment periods

Use Federal Register for topic-filtered comment periods and deadlines. Confirm the docket and related documents in Regulations.gov when a docket exists. Check both FAR and DARS agency codes for FAR/DFARS pipeline views.

### Public-comment analysis

Define and record:

- Docket and controlling proposed rule.
- Search terms and submitter categories.
- Date and document filters.
- Returned count, reviewed count, exclusions, attachments reviewed, and retrieval limits.
- Whether the sample is targeted, convenience, top-result, or complete.

Organization-keyword searches can surface associations, chambers, coalitions, and institutes, but they are targeted discovery and not an exhaustive census.

## Query safety

Allowed public parameters include agency names, public FAR/DFARS citations, FAR case numbers, RINs, docket IDs, Federal Register document numbers, dates, and sanitized topic terms already public.

Never send document text, internal acquisition descriptions, proposed strategy, source-selection material, proprietary details, PII, CUI, credentials, local paths, intranet URLs, signed URLs, or private-storage URLs.

## Completeness labels

- **Complete for approved published-source scope:** all sources required by the approved question were available and reconciled.
- **Published-source status with limitation:** a required source was partial, ambiguous, duplicated, scanned, or unavailable.
- **Codified baseline only:** only eCFR evidence was available.
- **Rulemaking pipeline only:** only Federal Register/Regulations.gov evidence was requested or available.
- **User-document supplement:** supplied policy evidence was analyzed but not independently verified as published or controlling.
