<!--
  This is the upgrade plan template for Azure SDK migration.
  RUN_ID should be replaced with the actual run identifier.

  ## PLANNING RULES

  !!! DON'T REMOVE THIS COMMENT BLOCK BEFORE FINAL PLAN IS GENERATED AS IT CONTAINS IMPORTANT INSTRUCTIONS.

  ### Strategy
  - **Incremental upgrades**: Stepwise dependency upgrades to avoid large jumps breaking builds
  - **Minimal changes**: Only upgrade dependencies essential for compatibility
  - **Risk-first**: Handle EOL/challenging deps early in isolated steps
  - **Necessary/Meaningful steps only**: Each step MUST change code/config. NO steps for pure analysis/validation. Merge small related changes.

  ### Mandatory Steps
  - **Step 1 (MANDATORY)**: Setup Baseline - Run compile/test with current JDK, document results.
  - **Steps 2-N**: Upgrade steps - dependency order, high-risk early, isolated breaking changes
  - **Final step (MANDATORY)**: Final Validation - verify all goals met, all TODOs resolved, 100% tests pass

  ### Verification Expectations
  - **Steps 1-N (Setup/Upgrade)**: Focus on COMPILATION SUCCESS. Tests may fail during intermediate steps.
  - **Final Validation**: COMPILATION SUCCESS + 100% TEST PASS

  ### Efficiency (IMPORTANT)
  - **Targeted reads**: Use `grep` over full file reads; read specific sections, not entire files. Template files are large - only read the sections you need.
  - **Quiet commands**: Use `-q`, `--quiet` for build/test commands when appropriate
  - **Progressive writes**: Update plan.md incrementally, not at end
-->

# Upgrade Plan: <PROJECT_NAME> (<RUN_ID>)

- **Generated**: <datetime> <!-- replace with actual date and time when generating -->
- **HEAD Branch**: <current_branch> <!-- replace with actual head branch when generating -->
- **HEAD Commit ID**: <current_commit_id> <!-- replace with actual head commit id when generating -->

## Available Tools

<!--
  List ONLY the JDKs and build tools that are required/used during the upgrade (not all discovered ones).
  Use the environment detection results from Precheck to check availability.
  Mark build tools that need upgrading for JDK compatibility as "**<TO_BE_UPGRADED>**".
  If a wrapper (mvnw/gradlew) is present, also check the wrapper-defined version in
  `.mvn/wrapper/maven-wrapper.properties` or `gradle/wrapper/gradle-wrapper.properties`.

  NOTE: This section is finalized during Upgrade Path Design (after step sequence is known), not during Environment Analysis.

  SAMPLE:
  **JDKs**
  - JDK 1.8.0: /path/to/jdk-8 (current project JDK, used by step 1)

  **Build Tools**
  - Maven 3.9.6: /path/to/maven
  - Maven Wrapper: 3.8.1 → **<TO_BE_UPGRADED>** to 3.9.6+ (current version incompatible with project requirements)
-->

## Guidelines

<!--
  User-specified guidelines or constraints in bullet points for this upgrade.
  Extract these from the user's prompt if provided, or leave empty if none specified.
  These guidelines take precedence over default upgrade strategies.
-->

> Note: You can add any specific guidelines or constraints for the upgrade process here if needed, bullet points are preferred. <!-- this note is for users, NEVER remove it -->

## Upgrade Goals

<!--
  The primary goal is to replace all legacy Azure SDK dependencies (com.microsoft.azure.*) with their
  modern equivalents (com.azure.*). List any additional user-specified goals below.

  SAMPLE:
  - Replace all `com.microsoft.azure.*` dependencies with `com.azure.*` equivalents
  - Migrate source code to use modern Azure SDK APIs (builder pattern, Azure Identity)
-->

### Technology Stack

<!--
  Table of core dependencies and their compatibility with upgrade goals.
  IMPORTANT: Analyze ALL modules in multi-module projects, not just the root module.
  Only include: direct dependencies + those critical for upgrade compatibility.

  Columns:
  - Technology/Dependency: Name of the dependency
  - Current: Version currently in use
  - Modern Equivalent: The com.azure.* replacement (or N/A if not an Azure SDK dep)
  - Migration Notes: Notes on migration approach

  IMPORTANT: Include build tools (Maven/Gradle), wrappers, and key build plugins in this table.

  SAMPLE:
  | Technology/Dependency                    | Current | Modern Equivalent                          | Migration Notes                              |
  | ---------------------------------------- | ------- | ------------------------------------------ | -------------------------------------------- |
  | com.microsoft.azure:azure-mgmt-resources | 1.41.4  | com.azure.resourcemanager:azure-resourcemanager | Use azure-sdk-bom for version management |
  | com.microsoft.azure:azure-mgmt-storage   | 1.41.4  | com.azure.resourcemanager:azure-resourcemanager | Included in azure-resourcemanager        |
  | com.microsoft.azure:azure-client-authentication | 1.7.14 | com.azure:azure-identity             | Use ClientSecretCredential or DefaultAzureCredential |
  | Maven (wrapper)                          | 3.6.3   | -                                          | Check compatibility with project JDK         |
-->

| Technology/Dependency | Current | Modern Equivalent | Migration Notes |
| --------------------- | ------- | ----------------- | --------------- |

### Derived Upgrades

<!--
  Required upgrades inferred from the Azure SDK migration.
  Each derived upgrade must have a justification explaining WHY it's required.
  Common derivations:
  - Legacy auth (azure-client-authentication) → azure-identity
  - Legacy management (azure-mgmt-*) → azure-resourcemanager or specific azure-resourcemanager-* modules
  - Legacy data plane SDKs → modern com.azure equivalents
  - Add azure-sdk-bom for version management

  SAMPLE:
  - Add azure-sdk-bom for centralized version management of com.azure.* dependencies
  - Replace azure-client-authentication with azure-identity (modern authentication library)
  - Add jackson-databind if file-based authentication is used and Jackson is not already present
-->

## Upgrade Steps

<!--
  Step-by-step upgrade plan. Each step should follow this format:
  - **Step N: <Descriptive Title>**
    - **Rationale**: Why this step is needed and why at this position
    - **Changes to Make**: ≤5 bullet points (concise)
    - **Verification**: Command, JDK, Expected Result

  VERIFICATION EXPECTATIONS:
  - Steps 1-N (Setup and Upgrade steps): Focus on COMPILATION SUCCESS. Tests may fail during intermediate steps.
  - Final step: COMPILATION SUCCESS + TEST PASS through iterative fix loop.

  MANDATORY FIRST STEP:
  The first step MUST always be Setup Baseline.

  MANDATORY SETUP BASELINE STEP SAMPLE:

  - Step 1: Setup Baseline
    - **Rationale**: Establish pre-upgrade compile and test results to measure upgrade success against.
    - **Changes to Make**:
      - [ ] Run baseline compilation with current JDK
      - [ ] Run baseline tests with current JDK
    - **Verification**:
      - Command: `mvn clean compile test-compile -q && mvn clean test -q`
      - JDK: <current project JDK path>
      - Expected: Document SUCCESS/FAILURE, test pass rate (forms acceptance criteria)

  ---

  SAMPLE STEP (dependency migration):

  - Step N: Migrate Azure Management Dependencies
    - **Rationale**: Replace legacy com.microsoft.azure management dependencies with modern com.azure.resourcemanager equivalents.
    - **Changes to Make**:
      - [ ] Add azure-sdk-bom to dependencyManagement
      - [ ] Replace com.microsoft.azure:azure-mgmt-* with com.azure.resourcemanager:azure-resourcemanager
      - [ ] Remove com.microsoft.azure:azure-client-authentication, add com.azure:azure-identity
      - [ ] Fix compilation errors from API changes
    - **Verification**:
      - Command: `mvn clean test-compile -q`
      - JDK: <JDK path>
      - Expected: Compilation SUCCESS (tests may fail - will be fixed in Final Validation)

  ---

  MANDATORY FINAL STEP (must always be the last step):

  - Step N: Final Validation
    - **Rationale**: Verify all upgrade goals met, project compiles successfully, all tests pass.
    - **Changes to Make**:
      - [ ] Verify no legacy com.microsoft.azure.* dependencies remain
      - [ ] Resolve ALL TODOs and temporary workarounds from previous steps
      - [ ] Clean rebuild with current JDK
      - [ ] Fix any remaining compilation errors
      - [ ] Run full test suite and fix ALL test failures (iterative fix loop until 100% pass)
    - **Verification**:
      - Command: `mvn clean test -q`
      - JDK: <JDK path>
      - Expected: Compilation SUCCESS + 100% tests pass
-->

## Key Challenges

<!--
  Document high-risk areas that require special attention during upgrade.
  Each challenge should have a mitigation strategy. Be concise.
  Common challenges for Azure SDK migration:
  - Authentication pattern changes (file-based auth, service principal)
  - API surface changes (fluent builder patterns differ between legacy and modern)
  - Async/reactive pattern differences
  - Package structure changes (com.microsoft.azure.management.* → com.azure.resourcemanager.*)

  SAMPLE:
  - **Authentication Migration**
     - **Challenge**: Legacy code uses file-based authentication via Azure.authenticate(credentialFile). Modern SDK requires explicit credential construction.
     - **Strategy**: Read credential file with Jackson ObjectMapper, construct ClientSecretCredential, use AzureProfile for subscription context.
  - **Fluent API Changes**
     - **Challenge**: Method names and builder patterns differ between legacy and modern Azure Resource Manager.
     - **Strategy**: Follow the migration guide at https://aka.ms/java-track2-migration-guide for method-level mappings.
-->
