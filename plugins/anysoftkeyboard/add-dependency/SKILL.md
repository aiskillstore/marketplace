---
name: add-dependency
description: Add a new third-party dependency to the project following the version catalog and approval workflow.
---

# Add Third-Party Dependency

This skill outlines the necessary steps to validly adding a new dependency to the project.

## Workflow

1.  **Verify Necessity**:
    *   **Goal**: Ensure the dependency is absolutely necessary.
    *   **Action**: Avoid adding new third-party dependencies unless there is no tailored solution available or implementing it manually helps the project significantly.
    *   **Action**: You **MUST** get user approval before adding any new third-party dependency. Explain why it is needed and what alternatives were considered.

2.  **Find Latest Version**:
    *   **Goal**: Use the most up-to-date stable version.
    *   **Action**: Perform a web search to determine the latest stable version of the library.
    *   **Example**: `search_web(query="latest version of retrofit")`

3.  **Update Version Catalog**:
    *   **Goal**: Centralize dependency management.
    *   **Action**: Add the dependency to `gradle/libs.versions.toml`.
    *   **Format**:
        ```toml
        [versions]
        libraryName = "1.2.3"

        [libraries]
        library-artifact = { group = "com.example", name = "library-artifact", version.ref = "libraryName" }
        ```

4.  **Sync and Build**:
    *   **Goal**: Verify the dependency is resolved correctly.
    *   **Action**: Run a build or sync command to ensure the new dependency doesn't break the build.
    *   **Command**: `./gradlew assembleDebug` (or relevant task).

## Guidelines
- **Approval First**: Do not modify files before getting confirmation from the user (unless in a fully autonomous mode where this is pre-approved).
- **No Hardcoding**: Never put version numbers directly in `build.gradle.kts` files. Always use the version catalog (`libs.versions.toml`).
