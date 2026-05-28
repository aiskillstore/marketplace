---
name: patent-assistant
description: Assists R&D teams with patent technical disclosure drafting and patent/novelty search analysis; use when users ask to write a patent disclosure, structure an invention description, search related patents, or assess novelty.
license: MIT
author: AIPOCH
---
> **Source**: [https://github.com/aipoch/medical-research-skills](https://github.com/aipoch/medical-research-skills)

## When to Use

Use this skill in the following scenarios:

1. **Drafting a patent technical disclosure** from an inventor’s informal or incomplete technical description.
2. **Structuring an invention description** into standard patent-style sections (field, background, summary, embodiments, drawings).
3. **Preparing for a novelty search** by extracting keywords, synonyms, and IPC suggestions from a technical solution.
4. **Finding related patents** and producing a similarity comparison against the user’s key technical features.
5. **Improving patent readiness** by identifying missing technical details and proposing claim-writing directions (non-legal, for drafting support).

## Key Features

- Converts colloquial technical descriptions into a **structured patent technical disclosure document**.
- Uses a **guided information-collection checklist** to fill gaps (problem, prior art defects, core solution, features, effects).
- Generates a disclosure with a consistent **section template** (Title, Field, Background, Summary, Detailed Description, Drawings, Keywords).
- Performs **multi-platform patent search orchestration** via a CLI script and supports optional similarity analysis.
- Produces **novelty-oriented analysis**: similarity ranking, key-feature comparison, and preliminary novelty judgment.
- Provides **post-draft optimization suggestions** (claim directions, expansion ideas, missing details to supplement).

## Dependencies

- Python `>= 3.9`
- (Optional, if enabled by the project) Common Python packages for HTTP parsing and analysis, such as:
  - `requests >= 2.28`
  - `beautifulsoup4 >= 4.11`
  - `lxml >= 4.9`

> Note: Exact runtime dependencies may vary depending on how `scripts/patent_search.py` is implemented in your repository.

## Example Usage

### 1) Generate a Patent Technical Disclosure Document

**User prompt**
```text
Help me write a patent disclosure document:
I designed a system that uses an on-device model to detect abnormal vibration patterns in industrial motors.
It compresses sensor streams, runs anomaly detection locally, and only uploads event snippets to reduce bandwidth.
```

**Expected output (Markdown disclosure template)**
```markdown
# Patent Technical Disclosure Document

## I. Title of Invention
A method and system for on-device vibration anomaly detection and event-based uploading for industrial motors

## II. Technical Field
The present invention relates to the technical field of industrial equipment monitoring, and specifically relates to on-device vibration signal processing and anomaly detection.

## III. Background Art
### 3.1 Description of Existing Technology
Existing solutions typically stream high-frequency vibration data to a cloud platform for centralized analysis, or use threshold-based alarms on edge devices.

### 3.2 Defects of Existing Technology
The existing technology has the following problems:
1. High bandwidth and storage costs due to continuous raw data uploading.
2. High latency for cloud-based detection, which may delay fault response.
3. Threshold-based edge alarms have poor adaptability across different motor types and operating conditions.

## IV. Summary of Invention
### 4.1 Technical Problem to be Solved
The technical problem to be solved by the present invention is reducing bandwidth and latency while maintaining reliable anomaly detection for motor vibration monitoring.

### 4.2 Technical Solution
To solve the above technical problem, the present invention adopts the following technical solution:
- Collect vibration sensor data from an industrial motor using an edge device.
- Perform stream compression/feature extraction on the edge device to obtain compact representations.
- Execute an on-device anomaly detection model to identify abnormal vibration patterns.
- When an anomaly is detected, generate an event snippet containing a time window of raw/feature data and metadata (timestamp, motor ID, operating state).
- Upload only the event snippet (and optionally periodic summaries) to a remote server for storage, visualization, and further diagnosis.

### 4.3 Beneficial Effects
By adopting the technical solution of the present invention, the following beneficial effects are achieved:
1. Significantly reduced network bandwidth usage by avoiding continuous raw data uploads.
2. Faster anomaly response due to local inference and event-triggered reporting.
3. Improved detection robustness compared with fixed thresholds by using a learned model.

## V. Detailed Description
### 5.1 Embodiment 1
An edge device connected to an accelerometer samples vibration at a preset rate, computes spectral features, and runs an anomaly model. Upon detection, it uploads a 5-second window around the event plus operating metadata.

### 5.2 Embodiment 2 (Optional)
The anomaly model is periodically updated using federated or scheduled offline training, while inference remains on-device.

## VI. Description of Drawings
Suggestions for drawing the following figures:
- Figure 1: System architecture (sensor, edge device, network, server).
- Figure 2: On-device processing pipeline (sampling → compression/features → anomaly detection → event packaging → upload).

## VII. Keywords
vibration monitoring; anomaly detection; edge computing; event-based upload; industrial motor; signal compression
```

### 2) Run a Patent Search (CLI)

**Basic search (default platform: Google Patents)**
```bash
python scripts/patent_search.py "vibration anomaly detection edge event-based upload" --limit 20
```

**Parallel search across all supported platforms (recommended)**
```bash
python scripts/patent_search.py "vibration anomaly detection edge event-based upload" -s all -p
```

**Search specific platforms**
```bash
python scripts/patent_search.py "vibration anomaly detection edge event-based upload" -s google,cnipa,innojoy
```

**Search with similarity analysis**
```bash
python scripts/patent_search.py "vibration anomaly detection edge event-based upload" -s all -p -a
```

**Expected search output (conceptual)**
- Related patents list (patent number, title, abstract)
- Similarity ranking and key-feature overlap
- Preliminary novelty judgment (non-binding)

## Implementation Details

### 1) Disclosure Document Generation Workflow

1. **Information collection (ask if missing)**
   - What technical problem is solved?
   - What are the defects of existing solutions (prior art)?
   - What is the core idea of the solution?
   - What are the key technical features (modules/steps/parameters)?
   - What beneficial effects are achieved and why?

2. **Document synthesis**
   - Produce a disclosure using the fixed section template:
     - Title of Invention
     - Technical Field
     - Background Art (existing tech + defects)
     - Summary (problem, solution, effects)
     - Detailed Description (embodiments/variants)
     - Drawings suggestions
     - Keywords

3. **Optimization suggestions**
   - Claim-writing directions (e.g., independent claim scope + dependent claim fallbacks)
   - Expansion directions (alternative embodiments, parameter ranges, optional modules)
   - Missing technical details to supplement (interfaces, data formats, thresholds, model training/inference constraints)

### 2) Patent Search Workflow

1. **Keyword extraction**
   - Core technical terms (components, steps, objectives)
   - Synonyms/near-synonyms (e.g., “edge” vs “on-device”, “anomaly” vs “fault detection”)
   - IPC suggestions (high-level guidance based on domain)

2. **Search execution**
   - Use `scripts/patent_search.py` to query one or multiple platforms.
   - Supported platform parameters:
     - `google`, `lens`, `innojoy`, `baidu`, `espacenet`, `cnipa`, `all`

3. **Result analysis**
   - Rank results by technical similarity (based on title/abstract/claims when available)
   - Compare key features against the user’s solution (feature-by-feature mapping)
   - Provide a preliminary novelty judgment and highlight the closest references

### 3) Common IPC Suggestions (Reference)

| Field | IPC Classification |
|------|---------------------|
| Computer Software | G06F |
| Artificial Intelligence | G06N |
| Image Processing | G06T |
| Communication | H04L, H04W |
| Database / Information Retrieval | G06F 16/ |
| Internet of Things | H04L 67/ |
| Blockchain / Cryptographic protocols in networks | H04L 9/, G06Q |

### 4) Usage Notes / Constraints

- Generated disclosures are **drafting aids** and should be reviewed and completed by the inventor.
- Automated search results **do not replace** a formal novelty search by professional institutions.
- Claims drafting is specialized; consider review by a qualified patent attorney.
- Confirm confidentiality and avoid premature public disclosure before filing.