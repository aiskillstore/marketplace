# Execution Guidelines

- **Wrapper preference**: Use Maven Wrapper (`mvnw`/`mvnw.cmd`) or Gradle Wrapper (`gradlew`/`gradlew.bat`) when present in the project root, unless user explicitly specifies otherwise.
- **Template compliance**: Follow the HTML-comment instructions in the template reference files when creating and populating `.github/java-upgrade/{RUN_ID}/plan.md`, `progress.md`, `summary.md`. You may remove the HTML comments after populating each section.
- **Output directory**: All plan/progress/summary files are created under `.github/java-upgrade/{RUN_ID}/` in the project being migrated. Create this directory at the start of the run.
- **Uninterrupted run**: Complete each phase fully without pausing for user input.
- **Git**: If git is available, create a new branch `java-upgrade/{RUN_ID}` before starting the migration. Commit changes per step on this branch. If git is not available, log a warning and proceed — files remain uncommitted in the working directory. Use `N/A` for `<current_branch>` and `<current_commit_id>` placeholders.
