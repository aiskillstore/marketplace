# Editorial review for Cursor

Paste this section into a rule file under `.cursor/rules/`, so every session
starts with the law.

You run the un-editorial-check CLI over user-visible copy, report what its
documented rules find, and correct that copy only when the user tells you to.
The checker reports rule violations; it does not decide whether a claim is
true, and you do not decide it either.

## 1. The law

Never modify a file before the user has explicitly approved the corrections.

Reading, scanning and asking questions are always allowed; writing, applying
fixes and inserting `ue:ignore` suppressions are not, until the approval gate
in step 3 has been passed.

## 2. Scan

Run the checker over the paths the user gave you, writing the report the user
will read:

```text
npx un-editorial-check <paths> --report un-editorial-review.pdf
```

Exit codes: `0` no error-severity findings, `1` error-severity findings
present, `2` usage, configuration, scan or write failure.

## 3. Approval gate

Ask the user one question: Apply these corrections?

Proceed only on an explicit go-ahead, such as yes or go ahead. Any other
answer means stop: write nothing, and say plainly that you are waiting for
approval.

## 4. Apply

After an explicit go-ahead only, run the mechanical fixes with `--fix --apply`
and review every diff it prints. Rewrite the remaining findings by hand,
taking wording only from the `Should be` line of the report.

If `proposed` is null, do not improvise — ask the user what should be written instead.

Never invent wording for a finding, and never insert a `ue:ignore`
suppression without telling the user.

## 5. Baseline and verification

Record the findings the project has accepted:

```text
npx un-editorial-check <paths> --baseline .ue-baseline.json
```

The first run writes the snapshot and exits 0; later runs fail only on new
error-severity findings. Verify the installation with
`npx un-editorial-check --self-test`.

Never claim the copy is clean unless the exit code is 0.
