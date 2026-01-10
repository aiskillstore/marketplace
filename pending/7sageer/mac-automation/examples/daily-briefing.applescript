#!/usr/bin/env osascript
-- Daily Briefing: Get today's calendar events and unread emails

-- Get today's calendar events
tell application "Calendar"
    set todayStart to current date
    set hours of todayStart to 0
    set minutes of todayStart to 0
    set seconds of todayStart to 0
    set todayEnd to todayStart + 1 * days

    set eventList to ""
    repeat with cal in calendars
        set todayEvents to (events of cal whose start date ≥ todayStart and start date < todayEnd)
        repeat with evt in todayEvents
            set eventTime to time string of (start date of evt)
            set eventList to eventList & "  • " & eventTime & " - " & (summary of evt) & linefeed
        end repeat
    end repeat

    if eventList is "" then
        set eventList to "  今天没有日程安排" & linefeed
    end if
end tell

-- Get unread email count and subjects
tell application "Mail"
    set unreadCount to unread count of inbox
    set emailList to ""

    if unreadCount > 0 then
        set unreadMsgs to (messages of inbox whose read status is false)
        set maxShow to 5
        set showCount to 0
        repeat with msg in unreadMsgs
            if showCount < maxShow then
                set emailList to emailList & "  • " & (sender of msg) & ": " & (subject of msg) & linefeed
                set showCount to showCount + 1
            end if
        end repeat
        if unreadCount > maxShow then
            set emailList to emailList & "  ... 还有 " & (unreadCount - maxShow) & " 封未读邮件" & linefeed
        end if
    else
        set emailList to "  没有未读邮件" & linefeed
    end if
end tell

-- Format output
set output to "📅 今日日程:" & linefeed & eventList & linefeed
set output to output & "📧 未读邮件 (" & unreadCount & "):" & linefeed & emailList

return output
