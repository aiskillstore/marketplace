# Reminders AppleScript Reference

## Create Reminders

### Basic Reminder
```bash
osascript <<'EOF'
tell application "Reminders"
    set defaultList to default list
    make new reminder in defaultList with properties {name:"买牛奶"}
end tell
EOF
```

### Reminder with Due Date
```bash
osascript <<'EOF'
tell application "Reminders"
    set dueDate to (current date) + 1 * days
    make new reminder in default list with properties {name:"明天的任务", due date:dueDate}
end tell
EOF
```

### Reminder with Specific Date and Time
```bash
osascript <<'EOF'
tell application "Reminders"
    set dueDate to current date
    set day of dueDate to 25
    set month of dueDate to 12
    set year of dueDate to 2024
    set hours of dueDate to 9
    set minutes of dueDate to 0
    set seconds of dueDate to 0
    make new reminder in default list with properties {name:"圣诞节提醒", due date:dueDate}
end tell
EOF
```

### Reminder with Notes
```bash
osascript <<'EOF'
tell application "Reminders"
    make new reminder in default list with properties {name:"开会", body:"会议室A，带笔记本"}
end tell
EOF
```

### Reminder with Priority
```bash
osascript <<'EOF'
tell application "Reminders"
    -- priority: 0=none, 1=high, 5=medium, 9=low
    make new reminder in default list with properties {name:"紧急任务", priority:1}
end tell
EOF
```

### Reminder in Specific List
```bash
osascript <<'EOF'
tell application "Reminders"
    set targetList to list "工作"
    make new reminder in targetList with properties {name:"完成报告"}
end tell
EOF
```

### Reminder with All Properties
```bash
osascript <<'EOF'
tell application "Reminders"
    set dueDate to (current date) + 2 * days
    set hrs to 14
    set mins to 30
    set hours of dueDate to hrs
    set minutes of dueDate to mins
    make new reminder in default list with properties {name:"完整提醒", body:"详细说明", due date:dueDate, priority:5}
end tell
EOF
```

## List Reminders

### List All Reminder Lists
```bash
osascript -e 'tell application "Reminders" to return name of every list'
```

### List Incomplete Reminders
```bash
osascript <<'EOF'
tell application "Reminders"
    set output to ""
    set incompleteReminders to (reminders in default list whose completed is false)
    repeat with r in incompleteReminders
        set output to output & (name of r) & linefeed
    end repeat
    return output
end tell
EOF
```

### List Reminders with Due Dates
```bash
osascript <<'EOF'
tell application "Reminders"
    set output to ""
    set remindersWithDue to (reminders in default list whose due date is not missing value and completed is false)
    repeat with r in remindersWithDue
        set output to output & (name of r) & " - " & (due date of r) & linefeed
    end repeat
    return output
end tell
EOF
```

### List Today's Reminders
```bash
osascript <<'EOF'
tell application "Reminders"
    set todayStart to current date
    set hours of todayStart to 0
    set minutes of todayStart to 0
    set seconds of todayStart to 0
    set todayEnd to todayStart + 1 * days

    set output to ""
    set todayReminders to (reminders in default list whose due date ≥ todayStart and due date < todayEnd and completed is false)
    repeat with r in todayReminders
        set output to output & (name of r) & linefeed
    end repeat
    return output
end tell
EOF
```

### List Overdue Reminders
```bash
osascript <<'EOF'
tell application "Reminders"
    set now to current date
    set output to ""
    set overdueReminders to (reminders in default list whose due date < now and completed is false)
    repeat with r in overdueReminders
        set output to output & (name of r) & " (逾期: " & (due date of r) & ")" & linefeed
    end repeat
    return output
end tell
EOF
```

### List Reminders from Specific List
```bash
osascript <<'EOF'
tell application "Reminders"
    set targetList to list "购物清单"
    set output to ""
    set items to (reminders in targetList whose completed is false)
    repeat with r in items
        set output to output & (name of r) & linefeed
    end repeat
    return output
end tell
EOF
```

### Count Incomplete Reminders
```bash
osascript -e 'tell application "Reminders" to return count of (reminders in default list whose completed is false)'
```

## Manage Reminders

### Complete a Reminder
```bash
osascript <<'EOF'
tell application "Reminders"
    set targetReminder to (first reminder in default list whose name is "买牛奶")
    set completed of targetReminder to true
end tell
EOF
```

### Delete a Reminder
```bash
osascript <<'EOF'
tell application "Reminders"
    set targetReminder to (first reminder in default list whose name is "旧任务")
    delete targetReminder
end tell
EOF
```

### Update Reminder
```bash
osascript <<'EOF'
tell application "Reminders"
    set targetReminder to (first reminder in default list whose name is "任务名")
    set name of targetReminder to "新任务名"
    set body of targetReminder to "更新的备注"
end tell
EOF
```

### Complete All Reminders in List
```bash
osascript <<'EOF'
tell application "Reminders"
    set allReminders to (reminders in default list whose completed is false)
    repeat with r in allReminders
        set completed of r to true
    end repeat
end tell
EOF
```

## Manage Lists

### Create New List
```bash
osascript -e 'tell application "Reminders" to make new list with properties {name:"新列表"}'
```

### Delete List
```bash
osascript <<'EOF'
tell application "Reminders"
    set targetList to list "要删除的列表"
    delete targetList
end tell
EOF
```

### Get Default List Name
```bash
osascript -e 'tell application "Reminders" to return name of default list'
```

## Time Calculations

### Due in N Hours
```bash
osascript <<'EOF'
tell application "Reminders"
    set dueDate to (current date) + 3 * hours
    make new reminder in default list with properties {name:"3小时后", due date:dueDate}
end tell
EOF
```

### Due in N Days
```bash
osascript <<'EOF'
tell application "Reminders"
    set dueDate to (current date) + 7 * days
    make new reminder in default list with properties {name:"一周后", due date:dueDate}
end tell
EOF
```

### Due Next Monday at 9 AM
```bash
osascript <<'EOF'
tell application "Reminders"
    set targetDate to current date
    set hours of targetDate to 9
    set minutes of targetDate to 0
    set seconds of targetDate to 0
    -- Find next Monday (weekday 2)
    repeat until (weekday of targetDate) is Monday
        set targetDate to targetDate + 1 * days
    end repeat
    make new reminder in default list with properties {name:"周一任务", due date:targetDate}
end tell
EOF
```

## Tips

1. **App Sync**: Reminders syncs with iCloud, changes appear on all devices
2. **Default List**: Use `default list` for quick operations
3. **Date Handling**: Use `+ N * days/hours/minutes` for relative dates
4. **Missing Value**: Due date can be `missing value` if not set
5. **Priority Values**: 0=none, 1=high, 5=medium, 9=low
6. **Permissions**: Requires Automation permission for Reminders
