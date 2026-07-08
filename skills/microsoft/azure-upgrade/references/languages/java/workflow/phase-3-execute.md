# Phase 3: Execute Upgrade Plan

Load this file when executing Phase 3. Refer back to [`upgrade-success-criteria`](../rules/upgrade-success-criteria.md) and [`upgrade-strategy`](../rules/upgrade-strategy.md) for success criteria and strategy, and [`../rules/troubleshooting.md`](../rules/troubleshooting.md) when failures occur.

## 1. Initialize

1. Read `plan.md` for step details
2. Update `progress.md`:
   - Replace `<RUN_ID>`, `<PROJECT_NAME>` and timestamp placeholders
   - Create step entries for each step in `plan.md` (per **Template compliance** rule)

## 2. Execute

For each step:

1. Read `plan.md` for step details and guidelines
2. Mark ⏳ in `progress.md`
3. Make changes as planned (use OpenRewrite if helpful, verify results)
   - Add TODOs for any deferred work, e.g., temporary workarounds
4. **Review Code Changes** (per rules in Progress Template): Verify sufficiency (all required changes present) and necessity (no unnecessary changes, functional behavior preserved, security controls maintained).
   - Add missing changes and revert unnecessary changes. Document any unavoidable behavior changes with justification.
5. Verify with specified command/JDK:
   - **Steps 1-N (Setup/Upgrade)**: Compilation must pass (including both main and test code, fix immediately if not). Test failures acceptable — document count.
   - **Final Validation Step**: Achieve **Upgrade Success Criteria** — iterative test & fix loop until 100% pass (or ≥ baseline). NO deferring. See [`../rules/troubleshooting.md`](../rules/troubleshooting.md) when stuck.
   - Build: `mvn clean test-compile` (or `./gradlew compileTestJava` for Gradle)
   - Test: `mvn clean test` (or `./gradlew test` for Gradle)
6. Commit on the `java-upgrade/{RUN_ID}` branch with message format (if git available; otherwise, log details in `progress.md`):
   - First line: `Step <x>: <title> - Compile: <result>` or `Step <x>: <title> - Compile: <result>, Tests: <pass>/<total> passed` (if tests run)
   - Body: Changes summary + concise known issues/limitations (≤5 lines)
   - **Security note**: If any security-related changes were made, include "Security: <change description and justification>"
7. Update `progress.md` with step details and mark ✅ or ❗

## 3. Complete

1. Validate all steps in `plan.md` have ✅ in `progress.md`
2. Validate all **Upgrade Success Criteria** are met, or otherwise go back to Final Validation step to fix
