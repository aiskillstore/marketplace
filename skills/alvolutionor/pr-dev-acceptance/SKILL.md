---
name: pr-dev-acceptance
description: Test already-deployed development environments for human-approved Bitbucket PRs against related Jira requirements, verify the real website through fresh browser logins and independent final visits, and deliver saved screenshots with a local acceptance report. This skill handles testing and acceptance only; it does not coordinate Slack use, deploy, or trigger pipelines. Creating it or checking approval alone does not start testing.
---

# PR Dev Acceptance

Accept the deployed change only when its expected behavior has been exercised through the real dev website and verified during an independent final page visit in a fresh browser login session. Builds, unit tests, API responses, DOM snapshots, and deployment success are supporting evidence; they cannot replace the fresh login, browser visit, and screenshots.

Creating or updating this skill does not execute a live workflow. Invoking this skill for acceptance authorizes scoped browser tests of the existing dev deployment and local evidence delivery. Do not ask again for permission already supplied by that invocation. Approval inspection alone does not start testing.

This skill never deploys to any environment, starts, reruns, or resumes pipelines, uploads deployment artifacts, or changes environment configuration, credentials, or permissions, except for explicitly authorized dedicated dev test accounts as described in "Obtain scoped test accounts". Deployment records and pipeline results may be read as version evidence. If the intended change is not deployed, report a blocker and leave deployment to the user or a separately authorized workflow. Slack notifications, environment-use coordination, merge, commit, and changes to approval status remain outside this workflow.

The user handles Slack notifications and environment-use coordination. Do not send notices, monitor Slack replies, or impose a five-minute wait. Slack access or evidence of a notification is not a prerequisite for testing.

## Establish the target

Resolve the repositories, exact PR URLs, related Jira card and its requirements and acceptance criteria, already-deployed dev application URL, test account or role, and permitted test records from the conversation and repository evidence. Ask for missing facts that prevent the test; never invent requirements, credentials, domains, or deployment state. Do not expand a frontend request into backend changes.

The approval prerequisite is human Bitbucket reviewer Approve. Verify actual human reviewer approvals and honor the repository's applicable approval requirements and outstanding change requests. Record the approver, approval time, decision evidence, and approved source commit for each PR in scope. A clean automated review result, green build, or Slack announcement does not replace human approval. Do not accept unapproved changes as the approved PR.

Read PR metadata, activity, approval decisions and the published diff through the available provider connector or authenticated API. Resolve the repository from its Git remote. Record the approved source commit, and honor the provider's actual approval-reset semantics when commits change. Do not silently test unpublished local edits as though they belonged to the approved PR. If the PR changed after approval, establish approval of the new commit before continuing.

## Verify the existing deployment identity

Before testing, use read-only evidence to confirm that the URL is the intended dev environment and that its deployed frontend and relevant backend contain the approved changes. Use available existing deployment records, pipeline commit IDs, runtime version information, or deployed asset provenance. Record what establishes the link between the approved commit and the served application. A PR head, local Git checkout, page appearance, or successful S3 upload alone is insufficient.

If changes were merged or rebuilt, record the deployed commit and evidence that it contains the approved commits. Include a paired repository only when the acceptance scope depends on it. If deployment identity cannot be established, report the missing evidence and keep acceptance blocked. Do not trigger a deployment to obtain evidence or make the target match.

Read the consuming application's routing and deployment documentation to resolve the actual dev URL. An asset bucket is not necessarily the served application URL. A local development server, component gallery, mocked API or HTML preview does not satisfy deployed-dev acceptance.

If the existing deployment failed, is incomplete or lacks the approved changes, keep acceptance blocked. Do not deploy, choose production, or invoke a privileged cloud role as a fallback.

## Prepare focused cases

Derive a small set of cases primarily from the related Jira card's requirements and acceptance criteria, then cross-check the approved diff and verified review feedback. For each case, record the Jira requirement, route, role, input or action, expected visible outcome, and any persistence check. Cover the changed behavior and directly affected existing behavior. Include validation, role restrictions, or negative cases only when the change or requirements make them relevant.

Use designated dev test data. Record original values before editing existing records; restore them when the test permits. If suitable records or authorization for a consequential operation are missing, block that case rather than using unrelated records. A requested dev acceptance run is not authority to send real notifications, operate hardware, or alter production data.

Keep all evidence under the owning project's existing acceptance-artifact directory. If no convention exists, use `artifacts/dev-acceptance/<issue>/current/`, with `report.md` and `screenshots/`. Move an earlier run intact into the sibling `archive/<run-id>/` before creating the new current run; never overwrite its evidence. Use the project's language conventions and English filenames. Record timestamps with an explicit timezone agreed in the task context.

## Obtain scoped test accounts

Use dedicated accounts and records supplied by the consuming project. If required roles are unavailable, use an existing project-approved provisioning adapter only when the current request authorizes those account writes. No provisioning adapter, role ARN, application model or default account is shipped with this public skill. Do not invent a user-creation API or reset an existing user's credentials. Missing access blocks the affected case. Avoid invitation or notification paths unless explicitly requested. Store temporary credentials privately outside the report and list only nonsecret account identifiers in the handoff.

## Exercise the real page

Use the available browser-control tools and their documented initialization and screenshot APIs. Read the applicable browser skill when required by the active harness. Browser automation that creates a new isolated context per login can satisfy the fresh-session requirement; a tool-runtime reset cannot. Do not assume a personal browser installation path or a tool from another harness. If isolated login or screenshot-saving capability is unavailable, report the blocker instead of substituting HTTP requests, a recreated page or a synthetic screenshot.

Create a dedicated task tab without activating unrelated apps or stealing focus. Use a visible browser window only when the user requests it. Navigate to the dev application's URL normally, authenticate with an authorized session, and exercise the actual controls. Use the real backend. Do not inject data into application state, edit the DOM, patch page scripts, or stub responses to make a case pass. DOM and network inspection can help diagnose a failure but cannot substitute for exercising the page.

Observe the rendered result for each case and capture the relevant state. For a saved change, establish success through the UI and then verify persistence during the final independent visit. A success toast alone is insufficient. Record errors with the route and reproduction steps. Do not change code, deploy, or alter configuration to make a failing case pass. A fix delivered outside this skill changes the target and requires a new run with its approval and existing deployment evidence.

## Independent final visit and screenshots

The mandatory final check is a separate page visit after setup and test actions in a fresh browser login session. Create an isolated browser context, temporary profile, or private session using the browser tool's supported capabilities. It must start without the previous test session's cookies, authentication storage, or application state. A new tab, renamed browser session, page refresh, or tool-runtime reset alone is insufficient. Verify the dev site presents the unauthenticated login flow, then sign in through the real UI with the designated test account. Never copy authentication tokens or storage from the action-phase session.

Keep the user's existing browser sessions intact; do not clear their cookies or log them out to create isolation. If the tools cannot establish a fresh isolated login, or credentials or a required authentication step are unavailable, mark final acceptance blocked and explain the missing capability. Do not weaken this requirement to a same-session tab visit.

After fresh login, navigate directly to the relevant dev routes, repeat cases needed to establish behavior for that role, and inspect saved results from the action phase. Record which cases were repeated and which persisted results were checked. Use separate fresh logins when distinct roles are required. Do not rely on the prior page's unsaved in-memory state. Re-read and inspect the final rendered page before capturing evidence.

For each required case, save an actual browser screenshot of the visible expected result, including a persisted value or role-specific state when relevant. Record the exact dev route separately if the screenshot API omits browser chrome. Capture additional states only when needed to prove the case, such as an error message or a disabled control. An image of a test report or code editor is not page evidence.

Persist the tool's screenshot output as PNG or another supported image format in `screenshots/`, then open the saved file with the available image viewer to verify that it is readable, shows the intended state, and belongs to the recorded URL and case. A tool-returned screenshot without an accessible saved artifact does not complete evidence delivery. Use test records that avoid exposing passwords, tokens, or unnecessary personal information in screenshots.

Record the PR commits and deployment identity again at the end. If the approved source or served deployment changed during testing, identify the affected evidence and repeat those checks against one established version before passing acceptance.

## Decision and handoff

Save `report.md` with:

- Jira card link, requirements and acceptance criteria used, and their corresponding test cases.
- PR links, human approvers and approval evidence, approved source commits, existing deployment record links, deployed commits and provenance, dev URL, run time, browser, and tested roles. State that this run performed no deployment or pipeline execution.
- Fresh-session isolation method, observed unauthenticated login flow, fresh login time and role, and final-visit routes. Never include credentials or authentication tokens.
- One row per case: expected result, observed result, `PASS`, `FAIL`, or `BLOCKED`, exact route, and clickable screenshot links. Distinguish the action-phase evidence from the independent final-visit evidence.
- Reproduction steps for failures, missing prerequisites for blockers, test-data changes and restoration results, and requirements or roles not covered.

Set the overall result to `PASS` only when every required case passes, human approval and the existing dev deployment identity are established, and the independent final visits in fresh login sessions and saved screenshots have been inspected. An observed required-case defect makes the result `FAIL`; missing prerequisites or evidence without an established defect make it `BLOCKED`. Preserve failed and blocked case details even when another failure determines the overall result. Do not label exploratory results as acceptance of an unverified deployment.

Return a concise handoff in the user's language with the outcome, tested Jira scope, report link, representative screenshot links when tests ran, uncovered scope, and the single next action when blocked or failed. Claim only what the recorded cases establish. Do not send Slack messages or require a Slack handoff. Do not alter Jira, approve the PR, merge, or commit unless separately requested; when the user asks to record the acceptance on the card, follow "Record acceptance on the Jira card". Do not open artifacts in an editor or system reader without a user request.

## Record acceptance on the Jira card

Only when the user asks. Scope changes agreed during acceptance (deferred items, requirements found unnecessary, role decisions) go into the card **description**, edited in place, never into the comment. The comment shows only what was verified:

- One row per check, written in plain words saying what was verified (no opaque case IDs), with role, result and the screenshot inline in the same row. Group rows by feature or route.
- A short test-data section: QA users used, records restored.
- No PR, commit, approval or deployment tables; those stay in the local report.

Write the draft as Markdown next to the report (`jira-comment.md`), embedding each screenshot by its real relative path (`![](screenshots/<file>.png)`) so it previews in the editor. Follow `references/jira-comment-example.md`. Prepare a concrete preview first. When posting is already explicitly requested, do not add a second approval gate. Run `scripts/post_jira_acceptance.py` (run `--help`; preview is the default and `--apply` performs the requested writes). It converts the Markdown to Jira markup, uploads the referenced screenshots as `<issuekey-without-hyphen>-<file>.png` attachments, posts the comment, and applies `--transition` only if the user explicitly requested moving the card and that transition is available.


## Optional Jira helper setup

The posting helper needs Python 3.10+, `requests`, `WORKFLOW_CONFIG` pointing to a private JSON file with `jira_url`, and private `JIRA_EMAIL` / `JIRA_API_TOKEN` environment variables. No service credentials are needed for preparing a local report. Keep credentials, screenshots and actual report data outside this public repository.
