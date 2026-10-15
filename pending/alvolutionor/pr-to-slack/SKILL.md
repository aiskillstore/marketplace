---
name: pr-to-slack
description: Create or reuse Bitbucket Cloud pull requests, assign configured reviewers, request review through connected Slack tools, and announce only after a verified clean review for unchanged commits. Use when the user explicitly asks to publish or send PRs; ordinary code review does not send messages.
---

# Deliver PRs through Slack

The authorized delivery is: prepare the requested PR batch, assign the configured reviewers, request analysis in the configured review channel, and announce the overall change in the configured announcement channel only after a clean result. Settings and identities belong to the consuming team's private configuration. See [setup](references/setup.md) and the [example review protocol](references/review-protocol.md).

A request to send PRs authorizes that delivery for those PRs. Creating or editing this skill authorizes only skill work. Preview requests stop at preview. Do not add commits, merges, deployments, unrelated recipients or retrospective edits to old messages. Match the user's project language and channel conventions.

## Establish scope and access

Resolve repositories and source branches from the conversation and Git remotes. Include paired repositories only when established by the request. Inspect the published diff and matching validation evidence before writing factual PR titles and descriptions. Report only validation that applies to the published commits. Omit attribution trailers.

Confirm the connected Slack tools can read, send and verify messages before creating PRs that require a Slack review request. Without them, prepare the descriptions and report the missing connection. Do not substitute a copied Slack token, background daemon or another identity.

The local worktree must be clean and the intended source commit must exist remotely. Do not silently omit dirty or unpushed work or claim it is published. A send request may authorize a normal push of existing requested commits; commits and force-pushes require their own explicit authorization. Report divergent history before proceeding.

## Prepare and publish the PR batch

Save the request and outputs under the owning task's private artifact directory, using `current/` and a sibling `archive/` for prior runs. Never store real requests in this public skill repository. Use UTF-8 JSON rather than interpolating multiline descriptions into shell commands.

Run `scripts/prepare_prs.py --request <request.json> --output <plan.json>` to inspect, then add `--apply` with a separate handoff output for authorized writes. The helper creates a missing PR or reuses the matching open source/destination pair. It preserves existing reviewers, adds missing configured reviewers and verifies the returned PR and commits. Do not reuse merged or declined PRs. Exclude an author from reviewing their own PR before creation when required by the provider.

An unknown PR-write outcome requires inspecting the exact branch pair before retrying. Save the applied, verified handoff, including canonical PR URLs and source/destination commits.

## Request review exactly once

Read recent review-channel messages. Reuse an existing thread for the identical PR URLs and source commits rather than duplicating an analysis request. A fresh review of the same commits needs the user's request.

Post one top-level message for the whole batch, with each canonical PR URL on its own line. Capture the returned channel ID and exact parent timestamp. Save the intended text. Read the thread back to verify its URLs and formatting. If a send times out, inspect the channel before retrying; never blindly repost.

When a connector adds an unwanted footer, use its documented edit operation on that newly sent message, then read it back. Preserve the original timestamp, replies and exact URL targets. If Markdown conversion collapses URL lines, use explicit `[URL](URL)` links and hard line breaks when supported. Do not delete/repost as a formatting workaround. Claim delivery only after verification.

## Wait for the correlated result

Keep following the same review thread during the active run. Poll about every two minutes for at most an hour, using short interruptible waits when the harness requires progress updates. Save each fresh thread snapshot and run `scripts/check_review.py --handoff <handoff.json> --thread <thread.txt>`.

The included parser supports only its documented example protocol. It must be adapted to the consuming bot's actual contract before automatic announcements. Only the configured trusted bot, the current job and exact PR set can supply the result. A status of `completed`, zero published comments, or a human saying "looks good" does not establish zero outstanding findings. Unknown or incomplete formats require inspection.

- `waiting`: continue bounded polling. Report persistent access failure or timeout with the thread link.
- `findings` or `needs_attention`: stop and report the reason. Do not announce, suppress findings or automatically repair code.
- `clean`: re-read PR metadata to verify that both source and destination commits still match the reviewed handoff. The helper blocks stale results.

Before the announcement, check the announcement channel for the same PR URL set at those source commits and the saved delivery record. If already announced, reuse its message link. Otherwise send the helper's escaped overall summary and plain canonical URL lines once. Verify the new message with the same send/read or send/edit/read sequence. Read before retrying any timed-out write.

Return the PR links, reviewer assignments, review-thread link, verdict and announcement link when sent. A clean bot result does not replace human reviewer approval for downstream acceptance.
