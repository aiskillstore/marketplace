# Examples

## Add a meeting

```
python scripts/schedule_tool.py --operation add --data-dir "D:\Schedules" --title "Weekly Sync" --start "2026-02-10 09:00" --end "2026-02-10 09:30" --remind 15 --tags "team,weekly"
```

## Import from CSV

```
python scripts/schedule_tool.py --operation import --data-dir "D:\Schedules" --input "events.csv"
```

CSV headers:
- title,start,end,type,location,notes,tags,remind_minutes

## Detect conflicts

```
python scripts/schedule_tool.py --operation conflicts --data-dir "D:\Schedules"
```

## Export reminders

```
python scripts/schedule_tool.py --operation reminders --data-dir "D:\Schedules"
```

## Popup reminders (Windows)

1) Generate reminders:

```
python scripts/schedule_tool.py --operation reminders --data-dir "D:\Schedules"
```

2) Run the notifier:

```
powershell -ExecutionPolicy Bypass -File "scripts\notify.ps1" -DataDir "D:\Schedules" -WindowMinutes 10
```

3) Optional Task Scheduler (every 5 minutes):

```
schtasks /Create /SC MINUTE /MO 5 /TN "ScheduleReminders" /TR "powershell -ExecutionPolicy Bypass -File D:\skill_delivery\small_skill\schedule_management\scripts\notify.ps1 -DataDir D:\Schedules -WindowMinutes 10" /F
```