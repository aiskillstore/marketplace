# Example: Complete Section Task Description

This is a real example of a well-structured task for a doc writer agent.

---

## Task

Write Section 3.1 "Blockchain L3 Rollup Benchmark (02)" of `/Users/user/project/design.md`.

## Required Skill

**MUST use doc writer skill** - Invoke `document-skills:doc-coauthoring` skill before writing.

## Context

Project `02_blockchain_l3_rollup_benchmark` is the core benchmarking infrastructure for measuring EVM transaction throughput and latency. Uses K6 load testing with custom xk6-ethereum Go extension.

## Scope

- Purpose: EVM transaction throughput and latency measurement
- Architecture diagram: K6 → xk6 extensions → EVM → InfluxDB → Grafana
- Key benchmark scripts: `erc20-rate.ts`, `eth-rate.ts`, `user-decrypt.ts`, `public-decrypt.ts`, `arbitrary-execution.ts`
- Helper modules: `init.ts`, `scenarios.ts`, `metrics.ts`
- Test modes: Load testing (constant-arrival-rate) vs Stress testing (ramping)
- Smart contracts: `ArbitraryExecution.sol`, `MyToken.sol`
- Metrics collected and interpretation

## Source Files to Reference

- `02_blockchain_l3_rollup_benchmark/README.md`
- `02_blockchain_l3_rollup_benchmark/CLAUDE.md` (detailed technical guide)
- `02_blockchain_l3_rollup_benchmark/scripts/*.ts`
- `02_blockchain_l3_rollup_benchmark/helpers/*.ts`
- `02_blockchain_l3_rollup_benchmark/contracts/src/*.sol`

## Output

Edit `/Users/user/project/design.md` Section 3.1. Create ASCII architecture diagram. Include code block examples where helpful.

## Delegation Rule

This is a large section. If it exceeds 800 words, break into subsections and create new VK tasks using vibe_kanban MCP tools (project_id: 54fa5480-fe6c-4c54-b855-79c4950e90dc):

- 3.1.1 Architecture Overview
- 3.1.2 Benchmark Scripts Reference
- 3.1.3 Metrics and Analysis

## VK Task ID: 371c1d4b-2dd6-40e4-8e9b-f752cfbe5a8f

When done, this task should be marked as "inreview" in VK.

---

## Why This Task Works

## Clear Context

- Names the specific project directory
- States the technology stack
- Describes the purpose concisely

## Explicit Skill Requirement

- Doc writer knows to invoke the coauthoring skill
- Establishes quality expectations

## Bounded Scope

- Bullet list of specific topics
- Clear what to include
- Implicit what NOT to include

## Actionable Source Files

- Specific paths to read
- Brief descriptions of each file's relevance

## Concrete Output

- Exact file to edit
- Which placeholder to replace
- Format expectations (diagrams, code blocks)

## Cascading Delegation

- Word limit trigger (800 words)
- Specific subsection breakdown
- MCP tool reference with project_id
- Enables recursive task creation

## Tracking

- VK task ID for status updates
- Clear completion criteria (mark as inreview)
