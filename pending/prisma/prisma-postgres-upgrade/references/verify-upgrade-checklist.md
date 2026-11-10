# verify-upgrade-checklist

Prove the upgrade with the repository's own checks, run the same way before and after.

## Priority

CRITICAL

## Why It Matters

A query rewrite can compile and still return different data, or fail only at runtime. The only
evidence the user can trust is the project's existing checks passing on both sides of the
change. Checks the agent writes for itself prove only what the agent expected.

## Rules

- **Use what the repo has.** Find the type check, build, lint and test scripts in `package.json`
  and CI config, and run exactly those.
- **Same commands before and after.** Record each command and its result before step 1. Run
  the identical commands after step 5. A check that was already failing before is reported as
  such, not fixed silently.
- **Do not invent checks.** Do not write or commit new tests or smoke scripts to stand in for
  missing ones, and do not change existing tests to make them pass.
- **Comparing pages by hand is fine, and it is not a test.** Requesting a few read-only pages
  before and after, against the same database, catches templates `tsc` never checks. Report it
  as a manual comparison, never as test coverage.
- **No tests? Say so.** If the repository has no tests, tell the user plainly that the upgrade
  is verified only by type check, build and the app starting, and leave the change for them to
  review before it ships.

## Checklist

1. **Baseline:** run the type check (`tsc --noEmit` or the repo's script), the build, and the
   test script, then start the app with its own start command and confirm it boots and connects.
   Record `SHOW timezone` on the database.
2. **After step 4:** same commands, against the same local database. No file imports
   `@prisma/client` or the generated client.
3. **After step 5:** a fresh install, then the same commands as the baseline, plus
   `npx prisma db verify` against the signed database. Start the app with its own start command
   again.
4. **Report:** each command, before and after, pass or fail. List what was not verified,
   including any behavior the tests do not cover, including the rc.20
   `DateTime` and `now()` notes in `client-api-mapping.md`. If the database's time zone is not
   UTC, say so first: new rows store a different time than before.

## Bad

```text
"Added tests/upgrade.test.ts that hits every route; all pass."
```

## Good

```text
Before: tsc ok, build ok, npm test 42 passed. After: tsc ok, build ok, npm test 42 passed,
app starts. Not verified: behavior the tests do not cover.
```

## References

- [Guide, step 5.3](https://www.prisma.io/docs/guides/upgrade-prisma-orm/postgresql#53-run-the-app-locally)
