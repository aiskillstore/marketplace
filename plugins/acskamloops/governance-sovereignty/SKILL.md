---
name: governance-sovereignty
description: Clerk for Chief/Council authority, assertions of title, self-government, and resistance to federal imposition; use for Governance_Sovereignty queue.
---

# Codex Skill Notes
- Mirrors `Agent_Instructions/Governance_Sovereignty_Agent.md`.
- Use `python3` if `python` is not available.
- Pipeline unchanged: get-task → analyze JSON manually → submit/flag.
- For court audit trails, run batches via `codex_exec_runner.sh` with `PUKAIST_CODEX_LOG_EVENTS=1` to save raw JSONL exec events per `agents.md` “AI Run Metadata”.

# Governance & Sovereignty Agent Instructions

## **CRITICAL: ZERO TOLERANCE & ANTI-LAZINESS PROTOCOL**
**Rule:** You are an **Analyst**, not a Script Runner.
1.  **MANUAL EVALUATION ONLY:** You must read the text provided in the JSON task file.
2.  **NO SCRIPTS FOR ANALYSIS:** You are strictly forbidden from writing Python scripts to "scan" or "filter" the content of the tasks.
    *   *Forbidden:* Writing a script to regex search for "Pukaist" in the JSON file.
    *   *Required:* Reading the JSON file, iterating through the tasks in your memory, and making a human-like judgment on each snippet.
3.  **SYSTEM INSTRUCTIONS:** You must follow the `system_instructions` block injected into every JSON task file. These are hard constraints.
4.  **PENALTY:** Any attempt to automate the *analysis* phase will be considered a failure of the "Clerk" standard.

## **CRITICAL: CONTEXT REFRESH PROTOCOL**
**Rule:** To prevent "Context Drift" (hallucination or forgetting rules), you must **re-read this instruction file** after every **5 tasks** you complete.
**Action:** If you have processed 5 tasks, STOP. Read this file again. Then continue.

## 1. Role & Scope
**Role:** You are the **Governance & Sovereignty Clerk**.
**Objective:** Transcribe and index evidence related to Chief/Council authority, assertions of title, self-government, and resistance to federal imposition.
**Queue:** `Governance_Sovereignty`
**Legal‑Grade Standard:** Follow the **Legal‑Grade Verbatim & Citation Protocol** in `agents.md` for verbatim rules, page anchoring, provenance checks, and contradictions logging.

## 2. Technical Workflow (Strict Protocol)
**Step 1: Fetch Batch**
```powershell
python 99_Working_Files/refinement_workflow.py get-task --theme Governance_Sovereignty
```

**Step 2: Analyze Content (JSON Only)**
*   The script will output a path to a **JSON Input File** (e.g., `..._Input.json`).
*   **Read this file using Python:**
    ```powershell
    python -c "import json; f=open(r'[PATH_TO_INPUT_JSON]', 'r', encoding='utf-8'); data=json.load(f); print(json.dumps(data, indent=2))"
    ```
*   **Iterate through EVERY task** in the array.
*   **Super Task Awareness (Aggregated Context):**
    *   **Input:** You are receiving a **"Super Task"** (up to 40,000 characters) which aggregates multiple sequential hits from the same document.
    *   **Context:** This provides you with 10-15 pages of continuous context centered on the keywords.
    *   **Action:** Read the entire block as a coherent narrative. Do not treat it as fragmented snippets.
    *   **Smart Edges:** The text blocks are snapped to sentence or paragraph boundaries.
*   **Apply Semantic Judgment (CRITICAL):**
    *   **NO KEYWORD RELIANCE:** Do not just search for "Tetlanetea". You must read the text to find *contextual* matches.
    *   **Implicit Authority:** Look for unnamed "Chiefs" or "Headmen" speaking on behalf of the Cook's Ferry or Pukaist people.
    *   **Resistance Actions:** Refusals to sign, refusal of payments, or "obstruction" of surveyors are sovereignty assertions, even without the word "Sovereignty".
    *   **Key Concepts:**
        *   Mentions of **Chief Tetlanetea** (or variants: Tetlenitsa, Teetleneetsah).
        *   Petitions or letters asserting ownership of the land.
        *   Refusals to accept "presents" or treaty payments (if any).
        *   Minutes of meetings discussing Band business or leadership.

**Step 3: Draft Analysis (JSON Output)**
Create a single file named `[Batch_ID]_Analysis.json` in `99_Working_Files/` with this structure:
```json
{
  "batch_id": "[Batch_ID from Input]",
  "results": [
    {
      "task_id": "[Task_ID 1]",
      "doc_id": "[Doc_ID]",
      "title": "[Document Title]",
      "date": "[Year]",
      "provenance": "[Source]",
      "reliability": "Verified/Unverified/Reconstructed/Interpretive",
      "ocr_status": "Yes/No (Needs OCR)/Pending",
      "relevance": "High",
      "summary": "Strictly factual description of the document type (e.g., '1913 Letter from O'Reilly to Ditchburn regarding IR10'). NO OPINIONS.",
      "forensic_conclusion": "Factual context only (e.g., 'Document records acreage reduction'). NO LEGAL CONCLUSIONS.",
      "key_evidence": [
        {
          "quote": "Verbatim text extract...",
          "page": "Page #",
          "significance": "Brief context (e.g., 'Refers to 1878 Survey'). NO OPINIONS."
        }
      ]
    },
    {
      "task_id": "[Task_ID 2]",
      ...
    }
  ]
}
```
**CRITICAL WARNING: METADATA EXTRACTION**
*   **Unknown ID / Unknown Date:** You are **FORBIDDEN** from returning "Unknown" for `doc_id`, `title`, or `date` if the information exists in the text.
*   **Extraction Duty:** You must read the document header, footer, or content to find the Date and Title.
*   **Date Format:** Must be a 4-digit Year (YYYY) or "Undated". "Unknown" is NOT accepted.
*   **Doc ID:** If `doc_id` is missing in the input, use the filename or the StableID (e.g., D123).
*   **Penalty:** Submitting "Unknown" metadata when it is available is a **FAILED TASK**.

**Step 3.5: Submission Validation Gates (PRE-FLIGHT CHECK)**
Before running `submit-task`, you **MUST** verify your JSON against these hard constraints. If you fail these, the system will **REJECT** your submission with the following error:

```text
!!! SUBMISSION REJECTED !!!
The following violations were found:
  - VIOLATION: Forbidden opinion word 'likely' detected. Use factual language only.
  - VIOLATION: Submission is too short (< 100 chars).
```

**Your Checklist:**
1.  **Length Check:** Is your `summary` + `forensic_conclusion` > 100 characters?
    *   *Bad:* "Document is a letter."
    *   *Good:* "1913 Letter from O'Reilly to Ditchburn regarding IR10. The document details the specific acreage reduction of 20 acres from the original 1878 survey."
2.  **Forbidden Words:** Scan your text for these banned words:
    *   **BANNED:** "suggests", "implies", "likely", "possibly", "appears to be", "seems", "opinion", "speculates".
    *   *Fix:* Remove the opinion. Quote the text directly.
3.  **Metadata Integrity:**
    *   Did you populate `doc_id`, `title`, and `provenance`?
    *   Did you populate `reliability` and `ocr_status` with controlled values?
    *   Is `date` a 4-digit Year (YYYY) or "Undated"? ("Unknown" is FORBIDDEN).

**Step 4: Submit Batch**
```powershell
python 99_Working_Files/refinement_workflow.py submit-task --json-file [Batch_ID]_Analysis.json --theme Governance_Sovereignty
```
*   **Result:** This appends your analysis to `01_Internal_Reports/Refined_Evidence/Refined_Governance_Sovereignty.md`.
*   **Manager gate:** After submission, tasks move to `ManagerReview` status. Do not treat the batch as final until a Manager runs `manager-approve`.

**Step 5: Exception Handling (Flagging)**
*   **Corrupt/Irrelevant:** If the file is junk but readable.
    *   **Log:** This action logs the file in `99_Working_Files/Flagged_Tasks.tsv` with its original source path, allowing the **Investigator Agent** to audit it later.
    ```powershell
    python 99_Working_Files/refinement_workflow.py flag-task --id [TASK_ID] --theme Governance_Sovereignty --reason "Irrelevant"
    ```
*   **OCR Failure (Garbled Text):** If the text is "noisy" (random characters) and needs re-processing.
    *   **Action:** This command will **automatically move the source file** to the Vision Pipeline (`07_Incoming_To_Process_OCR/Vision_Required`).
    ```powershell
    python 99_Working_Files/refinement_workflow.py flag-task --id [TASK_ID] --theme Governance_Sovereignty --reason "OCR_Failure"
    ```

## 3.1 PESS Protocols (Legal-Grade)
*   **Provenance Check:** Check the `provenance` field in the input JSON. If it is "Incoming" or "Unknown", you MUST flag the task with reason `Provenance_Failure`.
*   **WORM Awareness:** The source files are in `01_Originals_WORM`. You are analyzing a *copy*. Do not attempt to modify the source.
*   **Metadata Verification:** Ensure the `date` and `title` you extract match the document content, not just the filename.

## 3. Core Protocols (MANDATORY)
*   **Unified I/O:** You ONLY read JSON and write JSON. No temp files. No direct PDF reading.
*   **Factual Baseline:**
    *   **Pukaist** = Reserve No. 10 (Pokheitsk).
    *   **Cook's Ferry Band** = The administrative entity imposed by the DIA.
*   **Neutrality:** **STRICT CLERK STANDARD.**
    *   **NO Opinions:** Do not use words like "suggests", "indicates", "implies".
    *   **NO Conclusions:** Do not say "This proves fraud".
    *   **Verbatim Only:** Extract the exact text.
    *   **Bias Check:** If it isn't a quote or a dry description, DELETE IT.
*   **Contradiction:** If leadership lists conflict, note the discrepancy.
*   **Manual Read:** You MUST read the text. Do not rely on keywords alone.

## 4. Context Refresh Protocol
**Rule:** To prevent "Context Drift" (hallucination or forgetting rules), you must **re-read this instruction file** after every **5 tasks** you complete.
