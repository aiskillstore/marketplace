# Linear CLI Skill QA

Prompt for Claude Code to verify skill documentation accuracy.

## Usage

From the repo root, start a Claude Code session with the QA prompt pre-filled:

```bash
claude "$(cat skills/linear/QA.md | sed -n '/^~~~$/,/^~~~$/p' | sed '1d;$d')"
```

Or manually: start a new session and paste the prompt below.

---

## Prompt

~~~
I need to QA the linear-cli skill to verify the documentation is accurate.

## Step 1: INVOKE THE SKILL FIRST

**STOP. DO NOT RUN ANY COMMANDS YET.**

Your VERY FIRST action must be to invoke the skill using the Skill tool:

```
Skill tool: skill: "linear-cli:linear"
```

This loads the documentation you will be testing. Do NOT read skill files directly from the repo - this simulates how agents actually use the skill in practice.

**Invoke the skill NOW before proceeding to Step 2.**

## Step 2: Pre-flight Checks

After the skill documentation has loaded, run these checks and confirm with me:

1. Run `linear --version` and compare against `git describe --tags --always --dirty`:
   - Version should match the current commit (e.g., `v0.1.0` or `v0.1.0-5-gabc1234`)
   - If the repo is dirty (`-dirty` suffix), confirm with me whether this is acceptable
   - If versions don't match, the binary may be stale - rebuild with `zig build`
2. Run `linear auth test` - is a test API key configured?
3. Run `linear teams list` - which team should I use for testing?
4. Do I have permission to create/delete test issues and projects in this workspace?

Stop and wait for my answers before proceeding to Step 3.

## Step 3: Test Scope

After I confirm:
1. Review the expanded skill documentation from Step 1
2. Verify every documented command produces the expected output

Note: The skill includes references to additional files (graphql-recipes.md, troubleshooting.md). Test those recipes as well.

## Test Plan

### Phase 1: Quick Recipes (SKILL.md)
Test each recipe exactly as documented:
- [ ] `linear issues list --team TEAM_KEY --human-time`
- [ ] `linear search "keyword" --team TEAM_KEY --limit 5`
- [ ] `linear issue create --team TEAM_KEY --title "QA Test" --yes`
- [ ] `linear issue view IDENTIFIER`
- [ ] `linear issue view IDENTIFIER --json`
- [ ] `linear teams list`
- [ ] `linear auth test`
- [ ] `linear projects list --team TEAM_KEY --state planned --limit 5`

### Phase 2: Command Reference Table
Verify each command in the table works:
- [ ] `linear issues list`
- [ ] `linear search "keyword"`
- [ ] `linear issue view ID`
- [ ] `linear issue create` (with required flags)
- [ ] `linear issue update ID` (with at least one field)
- [ ] `linear issue link ID` (with relation flag - accepts TEAM-NUMBER or UUID)
- [ ] `linear issue comment ID --body "text" --yes`
- [ ] `linear issue delete ID` (dry-run first)
- [ ] `linear teams list`
- [ ] `linear me`
- [ ] `linear gql`
- [ ] `linear help CMD`
- [ ] `linear projects list` (state filters resolve via projectStatuses)
- [ ] `linear project view ID|SLUG`
- [ ] `linear project create --team TEAM_ID --name "QA Project" --state planned --yes`
- [ ] `linear project update ID|SLUG --state started --yes`
- [ ] `linear project delete ID|SLUG --yes`
- [ ] `linear project add-issue PROJECT_ID ISSUE_ID --yes` / `remove-issue` with --yes

### Phase 3: Common Flags
- [ ] `--json` produces valid JSON
- [ ] `--yes` allows mutations without prompt
- [ ] `--human-time` shows relative times
- [ ] `--fields LIST` filters output
- [ ] `--help` shows usage

### Phase 3b: Search Command Coverage
- [ ] `linear search "keyword" --team TEAM_KEY --limit 5` (table output)
- [ ] `linear search "keyword" --team TEAM_KEY --json --limit 2` (JSON + pagination warning when hasNextPage)
- [ ] `linear search IDENTIFIER --fields identifier --team TEAM_KEY` (identifier search resolves numbers)
- [ ] `linear search "Keyword" --case-sensitive --team TEAM_KEY` vs lowercase query (case sensitivity respected)
- [ ] `linear search "keyword" --fields title,description,comments --team TEAM_KEY` (field selection honored)
- [ ] `linear search "keyword" --assignee me --team TEAM_KEY` (assignee resolution works or returns empty set gracefully)

### Phase 4: Common Gotchas Table
Verify each error scenario:
- [ ] No team specified → empty results
- [ ] Missing --yes → mutation exits without action
- [ ] Invalid issue ID → appropriate error message

### Phase 5: Issue Update Command
Test issue update functionality:
- [ ] `linear issue update ID --assignee me --yes` - assigns to current user
- [ ] `linear issue update ID --priority 1 --yes` - sets priority
- [ ] `linear issue update ID --state STATE_ID|NAME --yes` - changes state (state names resolve case-insensitively; UUIDs still work)
- [ ] `linear issue update ID --state "In Progress" --yes` - state name path updates successfully
- [ ] `linear issue update ID --title "New Title" --yes` - updates title
- [ ] `linear issue update ID --description "New description" --yes` - updates description
- [ ] `linear issue update ID --parent PARENT_UUID --yes` - sets parent (**requires UUID**)
- [ ] `linear issue update ID --parent IDENTIFIER --yes` → error "Argument Validation Error" (identifiers not supported)
- [ ] `linear issue update ID --yes` (no fields) → error "at least one field"
- [ ] `linear issue update ID --priority 1` (no --yes) → error "confirmation required"

### Phase 6: Issue Link Command
Test issue linking functionality (accepts TEAM-NUMBER identifiers or UUIDs):
- [ ] `linear issue link ENG-123 --blocks ENG-456 --yes` - creates blocks relation
- [ ] `linear issue link ENG-123 --related ENG-456 --yes` - creates related relation
- [ ] `linear issue link ENG-123 --duplicate ENG-456 --yes` - marks as duplicate
- [ ] `linear issue link ENG-123 --yes` (no relation) → error "exactly one of --blocks"
- [ ] `linear issue link ENG-123 --blocks A --related B --yes` → error "only one of --blocks"
- [ ] `linear issue link UUID --blocks UUID --yes` - UUIDs still work directly

### Phase 6b: Issue Comment Command
Test issue comment functionality:
- [ ] `linear issue comment ENG-123 --body "Test comment" --yes` - creates comment with inline text
- [ ] `echo "Multi-line\ncomment" | linear issue comment ENG-123 --body-file - --yes` - creates comment from stdin
- [ ] `linear issue comment ENG-123 --body "text" --yes --json` - JSON output shows comment id and url
- [ ] `linear issue comment ENG-123 --body "text" --yes --quiet` - only outputs comment id
- [ ] `linear issue comment ENG-123 --yes` (no body) → error "--body or --body-file is required"
- [ ] `linear issue comment ENG-123 --body "x" --body-file y --yes` → error "cannot use both"
- [ ] `linear issue comment ENG-123 --body "text"` (no --yes) → error "confirmation required"

### Phase 7: Hygiene Section
Verify hygiene examples from SKILL.md work:
- [ ] Assignment workflow: `linear issue update ENG-123 --assignee me --yes` (identifiers work for main ID)
- [ ] Sub-issue workflow: `linear issue update ENG-123 --parent PARENT_UUID --yes` (**--parent requires UUID**)
- [ ] Blocking workflow: `linear issue link ENG-123 --blocks ENG-456 --yes` (TEAM-NUMBER identifiers now supported)

### Phase 8: GraphQL Recipes (graphql-recipes.md)
Test at least these recipes:
- [ ] Viewer query: `echo 'query { viewer { id name } }' | linear gql --json`
- [ ] Teams query: `echo 'query { teams { nodes { id key } } }' | linear gql --json`
- [ ] Attach URL (attachmentCreate) - on a test issue

Note: Link issues and set parent are now covered by direct CLI commands in Phases 5-6.
Note: Adding comments is now covered by `linear issue comment` in Phase 6b.

### Phase 8b: File Upload (Critical Path)
This tests the three-step file upload process which agents often get wrong:

1. Create a test file:
   ```bash
   echo "QA test content $(date)" > /tmp/linear-qa-test.txt
   ```

2. Follow the fileUpload recipe in graphql-recipes.md exactly:
   - [ ] Step 1: Call `fileUpload` mutation to get signed upload URL
   - [ ] Step 2: PUT the file to the signed URL with correct headers
   - [ ] Step 3: Use the returned `assetUrl` in an attachment or comment

3. Verify the upload:
   - [ ] Create attachment with the assetUrl on a test issue
   - [ ] View the issue in Linear web UI to confirm file is accessible
   - [ ] Download the file and verify content matches

4. Clean up:
   ```bash
   rm /tmp/linear-qa-test.txt
   ```

Common failure modes to verify against:
- Using wrong Content-Type header in PUT request
- Not waiting for signed URL before uploading
- Using uploadUrl instead of assetUrl in attachments

### Phase 9: Troubleshooting Scenarios
Verify error handling matches documentation:
- [ ] 401 error format (if safe to test)
- [ ] "Issue not found" error message
- [ ] Missing required fields error

### Phase 10: External Links
Verify links are valid:
- [ ] Linear API Docs link
- [ ] Apollo Studio link
- [ ] Project state mapping note: `projects list --state NAME` filters via `statusId` from `projectStatuses` (planned/started/backlog/etc.)

## Reporting

For each test:
1. Run the exact command from the docs
2. Compare output to documented expectation
3. Mark PASS or FAIL

Provide final summary:
- Total: X/Y passed
- Failed tests with actual vs expected
- Suggested documentation fixes

Fix any documentation errors directly in the skill files.

## Cleanup

Delete any test issues created during QA.
~~~
