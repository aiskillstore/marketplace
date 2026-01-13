# Calendar AppleScript Reference

## Create Events

### Basic Event
```bash
osascript <<'EOF'
tell application "Calendar"
    tell calendar "Home"
        set startDate to (current date) + 1 * days
        set hours of startDate to 14
        set minutes of startDate to 0
        set endDate to startDate + 1 * hours
        make new event with properties {summary:"会议", start date:startDate, end date:endDate}
    end tell
end tell
EOF
```

### Event with Location and Notes
```bash
osascript <<'EOF'
tell application "Calendar"
    tell calendar "Work"
        set startDate to date "2024-12-20 10:00:00"
        set endDate to date "2024-12-20 11:30:00"
        make new event with properties {summary:"客户会议", location:"会议室B", description:"讨论Q1计划", start date:startDate, end date:endDate}
    end tell
end tell
EOF
```

### All-Day Event
```bash
osascript <<'EOF'
tell application "Calendar"
    tell calendar "Home"
        set eventDate to date "2024-12-25"
        set endDate to eventDate + 1 * days
        make new event with properties {summary:"圣诞节", start date:eventDate, end date:endDate, allday event:true}
    end tell
end tell
EOF
```

### Event with Alarm
```bash
osascript <<'EOF'
tell application "Calendar"
    tell calendar "Work"
        set startDate to (current date) + 1 * days
        set hours of startDate to 9
        set newEvent to make new event with properties {summary:"重要会议", start date:startDate, end date:startDate + 1 * hours}
        -- Add alarm 30 minutes before
        tell newEvent
            make new display alarm with properties {trigger interval:-30}
        end tell
    end tell
end tell
EOF
```

### Recurring Event (Weekly)
```bash
osascript <<'EOF'
tell application "Calendar"
    tell calendar "Work"
        set startDate to current date
        set hours of startDate to 10
        set minutes of startDate to 0
        set newEvent to make new event with properties {summary:"周会", start date:startDate, end date:startDate + 1 * hours, recurrence:"FREQ=WEEKLY;BYDAY=MO"}
    end tell
end tell
EOF
```

### Event Today at Specific Time
```bash
osascript <<'EOF'
tell application "Calendar"
    tell calendar "Home"
        set startDate to current date
        set hours of startDate to 15
        set minutes of startDate to 30
        set seconds of startDate to 0
        make new event with properties {summary:"下午会议", start date:startDate, end date:startDate + 1 * hours}
    end tell
end tell
EOF
```

## List Events

### List All Calendars
```bash
osascript -e 'tell application "Calendar" to return name of every calendar'
```

### List Today's Events
```bash
osascript <<'EOF'
tell application "Calendar"
    set todayStart to current date
    set hours of todayStart to 0
    set minutes of todayStart to 0
    set seconds of todayStart to 0
    set todayEnd to todayStart + 1 * days

    set output to ""
    repeat with cal in calendars
        set todayEvents to (events of cal whose start date ≥ todayStart and start date < todayEnd)
        repeat with evt in todayEvents
            set output to output & (summary of evt) & " @ " & (start date of evt) & linefeed
        end repeat
    end repeat
    return output
end tell
EOF
```

### List This Week's Events
```bash
osascript <<'EOF'
tell application "Calendar"
    set weekStart to current date
    set hours of weekStart to 0
    set minutes of weekStart to 0
    set weekEnd to weekStart + 7 * days

    set output to ""
    repeat with cal in calendars
        set weekEvents to (events of cal whose start date ≥ weekStart and start date < weekEnd)
        repeat with evt in weekEvents
            set output to output & (summary of evt) & " - " & (start date of evt) & linefeed
        end repeat
    end repeat
    return output
end tell
EOF
```

### List Events from Specific Calendar
```bash
osascript <<'EOF'
tell application "Calendar"
    set output to ""
    set workEvents to events of calendar "Work"
    repeat with evt in workEvents
        set output to output & (summary of evt) & linefeed
    end repeat
    return output
end tell
EOF
```

### Get Next Event
```bash
osascript <<'EOF'
tell application "Calendar"
    set now to current date
    set nextEvent to missing value
    set nextDate to now + 365 * days

    repeat with cal in calendars
        set futureEvents to (events of cal whose start date > now)
        repeat with evt in futureEvents
            if start date of evt < nextDate then
                set nextEvent to evt
                set nextDate to start date of evt
            end if
        end repeat
    end repeat

    if nextEvent is not missing value then
        return (summary of nextEvent) & " at " & (start date of nextEvent)
    else
        return "No upcoming events"
    end if
end tell
EOF
```

### Search Events by Title
```bash
osascript <<'EOF'
tell application "Calendar"
    set searchTerm to "会议"
    set output to ""
    repeat with cal in calendars
        set foundEvents to (events of cal whose summary contains searchTerm)
        repeat with evt in foundEvents
            set output to output & (summary of evt) & " - " & (start date of evt) & linefeed
        end repeat
    end repeat
    return output
end tell
EOF
```

## Manage Events

### Delete Event by Title
```bash
osascript <<'EOF'
tell application "Calendar"
    repeat with cal in calendars
        set eventsToDelete to (events of cal whose summary is "要删除的事件")
        repeat with evt in eventsToDelete
            delete evt
        end repeat
    end repeat
end tell
EOF
```

### Update Event
```bash
osascript <<'EOF'
tell application "Calendar"
    tell calendar "Work"
        set targetEvent to (first event whose summary is "旧标题")
        set summary of targetEvent to "新标题"
        set location of targetEvent to "新地点"
    end tell
end tell
EOF
```

### Move Event to Another Time
```bash
osascript <<'EOF'
tell application "Calendar"
    tell calendar "Work"
        set targetEvent to (first event whose summary is "会议")
        set newStart to (current date) + 2 * days
        set hours of newStart to 14
        set start date of targetEvent to newStart
        set end date of targetEvent to newStart + 1 * hours
    end tell
end tell
EOF
```

## Manage Calendars

### Create New Calendar
```bash
osascript -e 'tell application "Calendar" to make new calendar with properties {name:"新日历"}'
```

### Delete Calendar
```bash
osascript <<'EOF'
tell application "Calendar"
    set targetCal to calendar "要删除的日历"
    delete targetCal
end tell
EOF
```

### Get Calendar Color
```bash
osascript <<'EOF'
tell application "Calendar"
    return color of calendar "Work"
end tell
EOF
```

## Recurrence Patterns

### Daily
```applescript
recurrence:"FREQ=DAILY"
```

### Weekly on Specific Days
```applescript
recurrence:"FREQ=WEEKLY;BYDAY=MO,WE,FR"
```

### Monthly on Date
```applescript
recurrence:"FREQ=MONTHLY;BYMONTHDAY=15"
```

### Yearly
```applescript
recurrence:"FREQ=YEARLY"
```

### With End Date
```applescript
recurrence:"FREQ=WEEKLY;UNTIL=20241231T235959Z"
```

### With Count
```applescript
recurrence:"FREQ=DAILY;COUNT=10"
```

## Alarm Types

### Display Alarm (Minutes Before)
```applescript
make new display alarm with properties {trigger interval:-15}
```

### Sound Alarm
```applescript
make new sound alarm with properties {trigger interval:-30, sound name:"Basso"}
```

### Email Alarm
```applescript
make new mail alarm with properties {trigger interval:-60}
```

## Tips

1. **Calendar Names**: Use exact calendar names, case-sensitive
2. **Date Format**: AppleScript parses "YYYY-MM-DD HH:MM:SS" format
3. **Time Zones**: Events use system time zone by default
4. **Sync Delay**: iCloud calendars may take a moment to sync
5. **Recurrence**: Uses iCalendar RRULE format
6. **All-Day Events**: Set `allday event:true`, only date matters
7. **Permissions**: Requires Calendar access in Privacy settings
