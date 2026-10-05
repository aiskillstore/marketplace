# Security policy

task-observer is a skill: instruction text plus a few shell snippets and
Python scripts that an agent runs inside your workspace. It has no server,
no network service and no credentials of its own. The security questions
that matter are therefore about what the skill tells an agent to do on
your machine.

## What counts as a security issue here

- A snippet or script that can write, move or delete files outside the
  workspace it was pointed at, or that fails in a way that silently
  destroys observation data.
- Instruction text that an agent could reasonably follow into an unsafe
  action — running fetched content, widening its own permissions,
  sending workspace content somewhere.
- A way for content from outside the user's control (a fetched page, a
  third-party skill, a pull request) to be carried into the observation
  log or a staged skill and acted on as an instruction.
- Anything in the released `.skill` bundle that differs from the tagged
  source.

A snippet that is merely wrong — reports the wrong count, breaks on an
unusual shell — is a bug, not a vulnerability: open a normal issue.

## Supported versions

Only the latest release on `main` receives fixes. Older tags are not
patched; update to the latest release.

## How to report

Please do **not** open a public issue for a vulnerability. Email
**eoghan@rebelytics.com** with:

- what the problem is and which file or snippet it is in;
- how to reproduce it (the environment, the harness and its permission
  mode matter);
- what an attacker or a mistaken agent could achieve with it.

You will get an acknowledgement within a week. Once a fix is released the
report is credited in the commit and the release notes, unless you ask
not to be named.
