# Coding Agent Review Checklist

Use this after an agent finishes implementation.

## Scope

- [ ] Changed files match the assignment
- [ ] No unrelated refactors
- [ ] No reverted user work
- [ ] No generated clutter or unnecessary metadata changes

## Behavior

- [ ] Acceptance criteria are met
- [ ] Edge cases are handled or named as risks
- [ ] User-facing text is clear and consistent
- [ ] Error states are handled deliberately

## Code Quality

- [ ] Existing patterns were followed
- [ ] New abstraction is justified by real complexity
- [ ] No ad hoc parsing where structured APIs exist
- [ ] Comments explain non-obvious logic only

## Verification

- [ ] Relevant tests were run
- [ ] Manual checks were run when tests are insufficient
- [ ] Failed checks are reported honestly
- [ ] Final response includes changed files and validation result

## Security / Privacy

- [ ] No secrets committed or printed
- [ ] No private data leaked into logs, docs, or screenshots
- [ ] No destructive command used without explicit approval
- [ ] Auth/session assumptions are stated clearly
