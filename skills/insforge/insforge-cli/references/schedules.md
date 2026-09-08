# InsForge CLI Schedules

Use `npx -y @insforge/cli schedules` to create and manage cron-style backend jobs.

## Commands

- `npx -y @insforge/cli schedules list` - list all scheduled tasks, including ID, name, cron, URL, method, active state, and next run.
- `npx -y @insforge/cli schedules get <id>` - get schedule details.
- `npx -y @insforge/cli schedules create --name --cron --url --method [--headers <json>] [--body <json>]` - create a scheduled job.
- `npx -y @insforge/cli schedules update <id> [--name] [--cron] [--url] [--method] [--headers] [--body] [--active]` - update a scheduled job.
- `npx -y @insforge/cli schedules delete <id>` - delete a scheduled job.
- `npx -y @insforge/cli schedules logs <id> [--limit] [--offset]` - view execution logs.

Confirm destructive intent before deleting schedules.

## Create Examples

```bash
# Wall-clock cadence: every 5 minutes (5-field cron)
npx -y @insforge/cli schedules create \
  --name "Cleanup Expired" \
  --cron "*/5 * * * *" \
  --url "https://my-app.us-east.insforge.app/functions/cleanup" \
  --method POST \
  --headers '{"Authorization": "Bearer ${{secrets.API_TOKEN}}"}'

# Sub-minute cadence: every 30 seconds (pg_cron interval syntax)
npx -y @insforge/cli schedules create \
  --name "Health Probe" \
  --cron "30 seconds" \
  --url "https://my-app.us-east.insforge.app/functions/probe" \
  --method GET

# Check execution history
npx -y @insforge/cli schedules logs <id>
```

## Cron Expression Format

InsForge accepts two cron formats:

- Standard 5-field cron expressions.
- pg_cron interval syntax for sub-minute cadence, such as `30 seconds`.

Six-field cron expressions with seconds, such as Quartz/Spring `*/2 * * * * *`, are not supported. Use interval syntax for sub-minute schedules.

5-field cron format:

```text
minute hour day-of-month month day-of-week
*      *    *            *     *

minute      0-59
hour        0-23
day-of-month 1-31
month       1-12
day-of-week 0-6, Sunday=0
```

| Expression      | Description                          |
| --------------- | ------------------------------------ |
| `* * * * *`     | Every minute                         |
| `*/5 * * * *`   | Every 5 minutes                      |
| `0 * * * *`     | Every hour, at minute 0              |
| `0 9 * * *`     | Daily at 9:00 AM                     |
| `0 9 * * 1`     | Every Monday at 9:00 AM              |
| `0 0 1 * *`     | First day of every month at midnight |
| `30 14 * * 1-5` | Weekdays at 2:30 PM                  |

Use 5-field cron for wall-clock cadence, such as daily, hourly, weekly, or every 5 minutes on the clock. Use interval syntax when the user needs sub-minute cadence or simple "every N seconds" semantics. At very high cadence, such as `1 second`, watch schedule log volume because every fire writes a log row.

## Secret References in Headers

Headers can reference InsForge secrets with `${{secrets.KEY_NAME}}`.

```json
{
  "headers": {
    "Authorization": "Bearer ${{secrets.API_TOKEN}}",
    "X-API-Key": "${{secrets.EXTERNAL_API_KEY}}"
  }
}
```

Secrets are resolved at schedule creation/update time. If a referenced secret does not exist, the operation fails.

## Recommended Workflow

1. Create secrets if needed with `npx -y @insforge/cli secrets add KEY VALUE`.
2. Create or verify the target function with `npx -y @insforge/cli functions list`.
3. Create the schedule with `npx -y @insforge/cli schedules create`.
4. Verify the schedule is active with `npx -y @insforge/cli schedules get <id>`.
5. Monitor execution logs with `npx -y @insforge/cli schedules logs <id>`.

## Best Practices

- Pick the right cron format for the cadence: 5-field cron for wall-clock cadence; interval syntax for sub-minute cadence.
- Store sensitive values as InsForge secrets and reference them from headers.
- Target InsForge functions for serverless scheduled tasks using `https://your-project.region.insforge.app/functions/{slug}`.
- Verify the target function exists and is active before scheduling it.
- Monitor execution logs for failed runs and non-2xx responses.

## Common Mistakes

| Mistake                                                 | Solution                                                                                              |
| ------------------------------------------------------- | ----------------------------------------------------------------------------------------------------- |
| Using 6-field cron such as `*/2 * * * * *`              | Use pg_cron interval form such as `2 seconds` for sub-minute cadence, or 5-field cron for everything. |
| Referencing a non-existent secret                       | Create the secret first with `npx -y @insforge/cli secrets add`.                                         |
| Targeting a non-existent function                       | Verify the function exists and is active before scheduling.                                           |
| Assuming a schedule is running after create/update only | Check `isActive`, next run, and execution logs with `schedules get` and `schedules logs`.             |
| Embedding raw secret values in schedule headers         | Store the value as an InsForge secret and use `${{secrets.KEY_NAME}}` in the schedule header JSON.    |
