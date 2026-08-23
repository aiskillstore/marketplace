# Fallback: collapse the chain by hand

Use this only when a native stack is unavailable: exit 9, a fork PR in the
work set, or a rewrite the user declined.

Do not merge the chain bottom-up into the default branch. Merging the bottom
PR with `--delete-branch` removes the branch the next PR is based on, and
GitHub then retargets or closes that child. Under a strict checks policy each
retargeted child also waits through a fresh CI cycle.

Collapse top-down into the lowest work-set PR, then merge that one PR into the
default branch. Check protection on every parent branch; internal chain
branches may also be gated.

```sh
# chain: main <- A <- B <- C   (A bottom, C top)
gh pr merge C <verified-method-flag> --match-head-commit <verified-C-sha>
gh pr merge B <verified-method-flag> --match-head-commit <verified-B-sha>
gh pr merge A <verified-method-flag> --delete-branch --match-head-commit <verified-A-sha>
```

When squash is allowed, give the final squash one combined commit message that
references every folded PR number. Re-read each head and the default-branch
tip immediately before each merge. If the default branch moved, re-prepare the
remaining chain. A post-snapshot PR is still ignored.

If a child was auto-closed after its base disappeared: recreate the base
branch at the parent's old head (`git push origin <sha>:refs/heads/<baseRefName>`),
`gh pr reopen <child>`, retarget with `gh pr edit <child> --base <default>`,
then delete the temporary branch.
