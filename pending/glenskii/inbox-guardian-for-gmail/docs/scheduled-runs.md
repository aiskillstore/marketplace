# Scheduled Audit Runs

Schedule only the standard audit command. It writes a local review file and does not label, archive, move, or delete mail.

Complete `python guardian.py --setup` manually before creating a schedule. A schedule cannot complete the browser consent step for you.

## Windows Task Scheduler

Create a basic task that runs at a time you choose. Set **Program/script** to the full path of the virtual-environment Python executable. Set **Add arguments** to:

```text
guardian.py --max 50
```

Set **Start in** to the folder that contains `guardian.py`. Run the task once manually and confirm that it creates a review file before relying on the schedule.

## macOS and Linux

Use your preferred user-level scheduler, such as `launchd` on macOS or cron on Linux. Run the virtual-environment Python executable with the full path to `guardian.py --max 50`. Set the working directory to the skill folder so review files remain local to the installation.

## Review Requirement

Open each generated review file before applying quarantine or Trash. Do not schedule `--execute`, `--trash`, or `--hard-delete`.
