# Task Visibility

## Module Description

Change the visibility of one of my tasks.

Resolve exactly one Buyer-owned `jobId` from the current request or a fresh
task list. If no candidate or multiple candidates remain, ask the Buyer to
provide or select one; never infer the most recent task from conversation
history.


## Flow
### Command

```bash
onchainos agent task-visibility-update --job-id <jobId> --visibility public|private
```
