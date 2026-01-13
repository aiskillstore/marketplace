#!/usr/bin/env osascript
-- Quick Note: Create a reminder from clipboard content

-- Get clipboard content
set clipContent to the clipboard as text

-- Check if clipboard has content
if clipContent is "" then
    display notification "剪贴板为空" with title "Quick Note"
    return "Error: Clipboard is empty"
end if

-- Truncate if too long for display
if length of clipContent > 50 then
    set displayText to (text 1 thru 50 of clipContent) & "..."
else
    set displayText to clipContent
end if

-- Create reminder with clipboard content
tell application "Reminders"
    set dueDate to (current date) + 1 * days
    set hours of dueDate to 9
    set minutes of dueDate to 0
    make new reminder in default list with properties {name:clipContent, due date:dueDate}
end tell

-- Show notification
display notification displayText with title "已创建提醒" subtitle "明天 9:00 提醒"

return "Created reminder: " & displayText
