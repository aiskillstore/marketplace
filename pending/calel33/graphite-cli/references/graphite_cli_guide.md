If you need more context starts here:https://graphite.dev/docs/cli-overview
This guide will walk you through the fundamental Graphite CLI commands and the stacked diff workflow. The goal is to provide a comprehensive, step-by-step approach to adopting this methodology confidently, moving away from large, monolithic pull requests (PRs) toward small, manageable, dependent changes.

---

## I. Understanding the Stacked Diff Workflow

The stacked diff workflow is a development methodology where large engineering tasks are broken down into a series of small, incremental, and logically cohesive code changes. Each change (or "diff") is stored as a distinct Git branch that builds directly on the previous one, forming a **Directed Acyclic Graph (DAG)** of dependencies.

### Why use Stacked Diffs?

*   **Reduced Cognitive Load:** Reviewers only need to focus on a small, self-contained change in each diff, making reviews faster and more thorough.
*   **Improved Iteration Speed:** Feedback on one layer can be addressed and integrated without blocking progress on other, higher layers in the stack.
*   **Gradual Integration:** Issues are detected earlier because foundational changes are reviewed and stabilized before subsequent diffs build upon them.
*   **Dependency Management:** Tools like Graphite automate the tedious process of dependency tracking and rebasing (restacking), which would be manual and complex in plain Git.

---

## II. Initial Setup and Configuration

Before starting, you must install and initialize the Graphite CLI.

### Step 1: Install and Authenticate

1.  **Install the CLI:** (Consult Graphite documentation for specific installation methods, such as `brew install withgraphite/tap/graphite` or `npm install -g @withgraphite/graphite-cli@stable`).
2.  **Authenticate with GitHub:** Use the `gt auth` command to provide your auth token, allowing Graphite to create and update PRs on your behalf.

### Step 2: Initialize the Repository

Navigate to your Git repository and run `gt init`.

| Command | Description |
| :--- | :--- |
| `gt init` | Initializes Graphite in the repository. You will be prompted to select your **trunk branch** (usually `main` or `master`), which serves as the root of all your stacks and where PRs merge into. |
| `gt config` | Use this to customize settings like shell completion, branch naming prefixes, or submission behaviors. |

---

## III. Basic Workflow: Creating a Single PR

The commands used for a single PR are the foundation for stacking. Graphite wraps several common Git commands into single `gt` actions.

### 1. Start on Trunk and Make Changes

1.  **Checkout Trunk:** Ensure you are on the base branch (e.g., `main`).
    ```bash
    gt checkout main  # Use gt co main (alias)
    ```
2.  **Make Changes:** Modify files in your working directory.

### 2. Commit and Create the Branch

The `gt create` command replaces `git add`, `git checkout -b`, and `git commit`.

| Command | Alias/Flags | Description | Example |
| :--- | :--- | :--- | :--- |
| `gt create` | `gt c` | Creates a new branch stacked on top of the current branch and commits staged changes. If no branch name is specified, Graphite generates one from the commit message. | `gt create -m "Initial feature part 1"` |
| `gt create` | `-am <MESSAGE>` | Shorthand to **a**ll-stage unstaged changes, and specify a **m**essage. | `gt c -am "feat: Add new user model"` |

**Example Sequence (Create):**
```bash
# 1. Ensure changes are unstaged in your working directory (e.g., created activity_feed.js)
# 2. Commit changes and create a branch in one step:
gt create --all --message "feat(api): Add new API method for fetching users"
# The new branch is now checked out.
```

### 3. Submit for Review

Use `gt submit` to push the branch and create a pull request on GitHub.

| Command | Description | Example |
| :--- | :--- | :--- |
| `gt submit` | Idempotently force pushes the current branch to GitHub, creating or updating its distinct pull request. | `gt submit -d` (Submit as a draft PR) |
| `gt pr` | Opens the pull request page for the current branch in your default browser. | `gt pr` |

### 4. Respond to Review Feedback (Iteration)

To update your branch after review, use `gt modify` (alias `gt m`), which automatically handles the update and restacks any dependent branches above it.

| Command | Alias/Flags | Description | Example |
| :--- | :--- | :--- | :--- |
| `gt modify` | `gt m -a` | **Amends** the existing commit on the current branch with all new staged or unstaged changes. This is the recommended approach for single-commit branches. | `gt m -a` |
| `gt modify` | `-c -a -m <MESSAGE>` | Creates an entirely new **c**ommit instead of amending the existing one. | `gt m -cam "Add fix for bug #123"` |
| `gt submit` | | Push the newly modified branch and update the existing remote PR. | `gt submit` |

---

## IV. Core Workflow: Creating and Managing a Stack

The stacked diff workflow begins when you need to break a large feature into a sequence of smaller, dependent PRs.

### 1. Creating the Stack

Start by creating the first, foundational branch (Part 1) off the trunk. Then, subsequent branches are built directly on top of the previous branch.

1.  **Checkout Parent Branch (Part 1):** Ensure you are on the top-most branch of your stack so far.
    ```bash
    gt checkout first_pr_branch
    ```
2.  **Make Changes (Part 2):** Introduce the next set of incremental changes (e.g., using the new API method created in Part 1).
    ```bash
    # Update frontend to use the API from PR 1
    echo "update frontend code" > frontend/UsersPage.tsx
    ```
3.  **Create the Next Branch (Part 2):** Use `gt create`. Since you ran this command while `first_pr_branch` was checked out, `second_pr_branch` automatically stacks on top of it.
    ```bash
    gt create -am "feat(frontend): Load and show a list of users"
    ```
4.  **Repeat:** Continue using `gt create` on the currently checked-out branch to build Part 3, Part 4, and so on.

### 2. Submitting the Entire Stack

To submit all dependent branches as distinct pull requests (PRs) simultaneously, use the `--stack` flag or its alias.

| Command | Alias | Description | Example |
| :--- | :--- | :--- | :--- |
| `gt submit --stack` | `gt ss` | Force pushes all branches in the current stack, from trunk up to the current branch, creating or updating a distinct PR for each one. | `gt ss --reviewers alice,bob` |

### 3. Visualizing and Navigating the Stack

Use the log commands to see the dependency structure and navigation commands to move quickly within the stack.

| Command | Alias | Function |
| :--- | :--- | :--- |
| `gt log short` | `gt ls` | Displays all tracked branches and their dependency relationships in a minimized format. |
| `gt checkout` | `gt co` | Opens an interactive selector to choose a branch to check out. |
| `gt up` | `gt u` | Switches to the child branch (upstack). |
| `gt down` | `gt d` | Switches to the parent branch (downstack). |
| `gt top` | `gt t` | Switches to the highest branch (tip) of the current stack. |
| `gt bottom` | `gt b` | Switches to the lowest branch (base, not including the trunk) of the current stack. |
| `gt checkout --trunk` | `gt co -t` | Switches to the main/trunk branch. |

---

## V. Synchronization and Conflict Management

As other changes merge into the trunk, you must synchronize your stack to remain up-to-date and maintain dependency integrity.

### 1. Synchronizing with Remote Changes

Use `gt sync` frequently throughout your workflow to ensure you are working on the most up-to-date version of your base branch.

| Command | Flags | Actions Performed by `gt sync` |
| :--- | :--- | :--- |
| `gt sync` | | 1. **Pulls** the latest changes into the trunk branch (`main`). 2. **Restacks** (rebases) all open PRs/branches onto the newest changes from the trunk. 3. **Prompts** to delete any local branches that have already been merged/closed remotely. |

### 2. Resolving Conflicts (Restacking)

If `gt sync` or `gt modify` encounters conflicts during the automatic restacking process, the operation will halt.

1.  **Resolve Conflicts:** Graphite instructs you to resolve the listed merge conflicts using the standard Git conflict resolution flow.
2.  **Stage Changes:** Mark them as resolved using `gt add .`.
3.  **Continue:** Run `gt continue` to continue the previously halted Graphite command and complete the restack.

### 3. Absorbing Changes Across the Stack

If you have unstaged changes that belong to different commits downstack (e.g., reviewer feedback that affects Part 1, Part 2, and Part 3), use `gt absorb`.

| Command | Flags | Description |
| :--- | :--- | :--- |
| `gt absorb` | `-a` | **Automatically applies unstaged changes** to the relevant commits in the current stack. It finds the closest downstack commit that the change hunk can be applied to deterministically. |

---

## VI. Merging and Cleanup

Once review and CI checks pass, you are ready to merge.

### 1. Merging the Stack

1.  **Merge via UI (Recommended):** Checkout the top branch (`gt top`) and open the PR (`gt pr`). Use the **Merge** button in the Graphite UI to merge the stack.
2.  **Merge via CLI:** Use `gt merge` to merge the associated pull requests from trunk up to the current branch via Graphite.

### 2. Post-Merge Cleanup

After the stack has been merged into the trunk branch, run `gt sync` one last time.

```bash
gt sync
```
This pulls the final merged changes, and Graphite automatically detects which local branches are now stale and prompts you to delete them, keeping your repository clean.

---

## VII. Advanced Stack Management and Collaboration

The CLI provides advanced tools for changing the structure of your work and collaborating with teammates.

### 1. Manipulating the Stack Structure

| Command | Purpose | Example |
| :--- | :--- | :--- |
| `gt move` | **Rebases** the current branch and all its recursive children onto a new parent branch. This is how you change a branch's dependency. | Checkout `branch_A`, then run: `gt move --onto main` to make A depend directly on main. |
| `gt reorder` | Opens an interactive editor to manually change the dependency sequence (order) of branches between trunk and the current branch. | `gt reorder` |
| `gt create --insert` | Creates a new branch and automatically **inserts** it into the stack between the current branch and its child, restacking the descendants. | `gt create -aim "inserted_refactor"` |
| `gt fold` | **Combines** the current branch's changes into its parent, updates dependencies, and deletes the folded branch. | `gt fold` |
| `gt split` | Splits the current branch (either by commit boundaries or by selecting hunks) into two or more new branches. | `gt split --by-hunk` |

### 2. Collaborating on Shared Stacks

You can easily pull down a coworker’s stack to build upon their work or review their changes locally.

| Command | Purpose | Notes |
| :--- | :--- | :--- |
| `gt get <BRANCH_NAME>` | **Fetches a remote stack** locally. This syncs the specified branch and all branches that it depends on (downstack). | Recommended for developers who work on more than one machine. |
| `gt freeze [BRANCH]` | **Prevents local modifications** (including restacks) to a branch, even though you can still sync remote changes to it. Useful when building on a coworker’s work. | Branches pulled with `gt get` are frozen by default. |
| `gt unfreeze [BRANCH]` | Enables local modifications to a previously frozen branch. | |
| `gt track [BRANCH]` | **Starts tracking** a Git branch created outside of the Graphite workflow. You must let Graphite know its parent to manage dependencies correctly. | Use `git rebase` first to ensure the desired parent is in its history, then run `gt track`. |
| `gt trunk --add` | Used to configure additional long-lived base branches (multitrunk support), such as `release-v10`, allowing you to stack PRs against different bases. | `gt trunk --add release-v10` |