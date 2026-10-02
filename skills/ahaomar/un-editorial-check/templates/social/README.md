# Social templates

Paste-ready short-form copy for announcing the package. Each file opens with a short instruction block, then a `---` rule, and everything after the rule is the post itself.

| File | Post body | Use it for |
|---|---|---|
| [x-short.md](x-short.md) | 249 characters | A single post for X, Bluesky or Mastodon, where the budget is the constraint |
| [npm-launch.md](npm-launch.md) | 1214 characters | The package launch post: npm page, Node.js community channel, release description |
| [show-and-tell.md](show-and-tell.md) | 1717 characters | The builder post: Show and Tell threads, repository showcases, project updates |
| [linkedin.md](linkedin.md) | 1428 characters | The professional-network post: feed announcement with the repository link last |

Body lengths are the post only, measured in Unicode code points, not counting the instruction block above the rule. The three long posts are written for a feed with room; the short post exists because a 280-character platform cannot take any of them.

## Editing these files

- Keep the version, the date, the dependency count and the licence accurate. Everything else may be shortened for a platform limit.
- Do not add a claim the README does not make. The banned claim phrases are enforced by `tests/audit-docs.mjs` over `docs/*.md` and by the release QA sweep over every tracked file, so a superlative or a promise of approval will fail the release rather than persuade a reader.
- Keep the house style: no contractions, no question marks, British English, no percentage signs outside a code fence.
- A clean run is stated exactly: `No findings under the enabled, documented local rules.`
- Fenced blocks are exempt from extraction, so a shell command inside a post is not scanned. That exemption is why the posts carry a command rather than a screenshot of one: a screenshot of a real run would print the copy that triggered each rule.

## Checking a character budget

`--preview` counts the **whole file**, instruction block included, so running it on one of these files directly overstates the post by the length of its header. Measure the body instead:

```sh
# Count the post body, below the --- rule, in code points.
sed '1,/^---$/d' templates/social/linkedin.md | wc -m

# Or preview the file as shipped, accepting that the header is counted.
node bin/check.mjs --preview linkedin templates/social/linkedin.md
```

`--preview` never edits the file. It exits `0` whenever a preview is produced, whether or not the text fits, and states over-budget in its output rather than in the exit code. Read the line, not the code.

The documented budgets are `x` at 280 characters with every link counted as 23, `linkedin` at 3000 with a link counted as written, `bluesky` at 300 and `mastodon` at 500. They are documented assumptions, not guarantees from the platforms.

## What these templates are not

They are starting points, not a campaign. None of them carries a metric, a download count or a comparison against another tool, because none of those would be true at the moment of reading and all three would need re-verification before every post.
