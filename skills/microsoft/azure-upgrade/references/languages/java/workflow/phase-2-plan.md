# Phase 2: Generate Upgrade Plan

Load this file when executing Phase 2. Refer back to [`upgrade-success-criteria`](../rules/upgrade-success-criteria.md) and [`upgrade-strategy`](../rules/upgrade-strategy.md) for success criteria and strategy, and [`../rules/troubleshooting.md`](../rules/troubleshooting.md) when failures occur.

## 1. Initialize

1. Update `plan.md`: replace all remaining placeholders
2. Extract user-specified guidelines from prompt into "Guidelines" section (bulleted list; leave empty if none)

## 2. Environment Analysis

1. Read HTML comments in "Available Tools" section of `plan.md` to understand rules and expected format
2. Record discovered JDK versions and paths
3. Detect wrapper presence; if wrapper exists, read wrapper properties to determine build tool version
4. Check build tool version compatibility with JDK — flag incompatible versions for upgrade

## 3. Dependency Analysis

1. Read HTML comments in "Technology Stack" and "Derived Upgrades" sections of `plan.md` to understand rules and expected format
2. Identify core tech stack across **ALL modules** (direct deps + upgrade-critical deps)
3. Include build tool (Maven/Gradle) and build plugins (`maven-compiler-plugin`, `maven-surefire-plugin`, etc.) in the technology stack analysis
4. Flag EOL dependencies (high priority for upgrade)
5. Consult the Migration Guidelines for package mappings and migration guides
6. Populate "Technology Stack" and "Derived Upgrades"

## 4. Upgrade Path Design

1. Read HTML comments in "Key Challenges" and "Upgrade Steps" sections of `plan.md` to understand rules and expected format
2. For incompatible deps, prefer: Replacement > Adaptation > Rewrite
3. Finalize "Available Tools" section based on the planned step sequence
4. Design step sequence:
   - **Step 1 (MANDATORY)**: Setup Baseline — run compile/test with current JDK, document results
   - **Steps 2-N**: Upgrade steps — dependency order, high-risk early, isolated breaking changes. Compilation must pass (both main and test code); test failures documented for Final Validation.
   - **Final step (MANDATORY)**: Final Validation — verify all goals met, all TODOs resolved, achieve **Upgrade Success Criteria** through iterative test & fix loop.
5. Identify high-risk areas for "Key Challenges" section
6. Write steps following format in `plan.md`

## 5. Plan Review

1. Verify all placeholders filled in `plan.md`, check for missing coverage/infeasibility/limitations
2. Revise plan as needed for completeness and feasibility; document unfixable limitations in "Plan Review" section
3. Ensure all sections of `plan.md` are fully populated (per **Template compliance** rule) and all HTML comments removed

After plan generation, proceed directly to execution — create `.github/java-upgrade/{RUN_ID}/progress.md` from the Progress Template, replace placeholders, and begin execution. Log the migration plan, then proceed without pausing for confirmation.
