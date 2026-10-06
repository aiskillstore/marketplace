# Public Reply Mode (GitHub issue / PR)

Loaded from `write` when the deliverable is a maintainer reply on a public issue or PR thread.

Activate when: "回复 issue", "reply to PR", "comment on #N", "回 issue", or the user asks for the text of a GitHub issue / PR comment.

Hard rules for the reply body:

1. **Default to one paragraph and one or two sentences.** Open with `@<reporter>` and at most one short thanks. Match the reporter's language unless the user or project names another. No exclamation mark or stacked courtesy ending (`再次感谢`, `Thanks again`).
2. **State the factual boundary and the reporter's next step.** Name exactly one ship state: already shipped in v<X.Y.Z>, fixed on `main` and going out in the next release, available in nightly/beta/preview, planned for v<X.Y.Z>, duplicate, not planned with one-line reason and an alternative path, or still needs specific evidence. The next step is concrete: the release to install, the nightly upgrade command, a cache path to clear once, or exactly what info is still needed. The step must remain usable with the reported failure or accessibility constraint present; do not ask the reporter to disable an assistive capability they need to follow it. Include root cause only when it changes what the reporter should do. Internal symbols, files, CI approval, and maintainer process stay out.
3. **Every sentence must be currently true.** No "already shipped" without release evidence in the current turn, no "landed on main" while the change sits uncommitted, and no implied build or artifact verification that did not happen.
4. **Two short paragraphs are the exception**, used only when a one-line command or necessary ambiguity cannot fit cleanly. No bullet lists, section headers, or code blocks except that one-line command.
5. **A batch of replies is N replies, not one skeleton filled N times.** When closing or answering several threads in one pass, read the drafts side by side before posting: same opening clause, same paragraph order, and same closing move across three or more of them reads as template voice no matter how correct each one is. Only the facts are shared. The opening sentence in particular should come from that thread's own report.
6. **Sensitive diagnostics stay off the thread.** For logs, crash dumps, screenshots, or local-state archives, ask for the minimum public facts, and point to the project's private support channel only when public project context provides one.

The reply is the final user-facing text, not an agent log. Do not write "刚才我判断错了", "前面回复有误", "I re-read it and changed the comment", or any meta narration about your own process. Edit your own comment in place only while nobody has replied after it, replacing it with clean final wording as if it were the only comment the user will read; once the reporter or anyone else has replied, post a new comment instead of rewriting history.

Before posting, re-read the live issue / PR with `gh issue view <num>` or `gh pr view <num>`. Do not reply from memory; titles, states, and author languages change between sessions.

After posting or editing, re-read the comment body, author, target item, and issue/PR state. Until that readback matches the intended final text, the public action is not done.

For paid / subscribed users, acknowledge the purchase relationship and the inconvenience in one phrase, then state the boundary. Do not over-explain. When the current product cannot support their setup, suggest the safest practical path (upgrade macOS, wait for the next release, provide logs, refund route) without arguing.

For private support channels (DM, in-app reply, support email), drop the report register entirely: short colloquial sentences in the maintainer's own voice, lead with what the user gets rather than how it works, and fewer full stops than documentation would carry.

Closing rule: the closing comment is the reporter's answer, not the investigation; root cause, file names, and reasoning belong in the commit, and a reply that needs scrolling is over-length. When closing as `completed`, the comment must independently explain what was fixed, the channel it arrives on, and the expected release. When closing as `not planned`, it must independently explain the current boundary and an alternative path. Do not rely on prior thread context as the explanation.
