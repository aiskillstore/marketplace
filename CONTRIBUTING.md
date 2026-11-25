# Contributing

Pull requests from contributor forks are not accepted in this repository. This
applies to skills, CLI packages (including `packages/skillstore`), scripts, and
other tooling. To preserve security review and publication provenance,
maintainers implement reviewed changes on branches in the official repository.

## Submit a skill

Use [skillstore.io/submit](https://skillstore.io/submit). The platform discovers
the skill, runs its security analysis, and creates the review submission. Do not
add or update skill files with a pull request.

## Report a CLI or tooling issue

Open an [issue](https://github.com/aiskillstore/marketplace/issues/new) with:

- The CLI version, operating system, and relevant installation scope.
- The command and minimal steps needed to reproduce the problem.
- Expected and actual behavior, with secrets and private data removed.
- A link to any prepared patch or pull request as reference material.

Maintainers review the report and, when accepted, implement and test the fix on
an official branch. A closed contributor pull request does not mean its bug
report or proposed behavior has been rejected.
