# Mail AppleScript Reference

## Send Email

### Basic Send
```bash
osascript <<'EOF'
tell application "Mail"
    set newMessage to make new outgoing message with properties {subject:"主题", content:"邮件内容", visible:true}
    tell newMessage
        make new to recipient at end of to recipients with properties {address:"recipient@example.com"}
    end tell
    send newMessage
end tell
EOF
```

### Send with CC and BCC
```bash
osascript <<'EOF'
tell application "Mail"
    set newMessage to make new outgoing message with properties {subject:"主题", content:"内容"}
    tell newMessage
        make new to recipient at end of to recipients with properties {address:"to@example.com"}
        make new cc recipient at end of cc recipients with properties {address:"cc@example.com"}
        make new bcc recipient at end of bcc recipients with properties {address:"bcc@example.com"}
    end tell
    send newMessage
end tell
EOF
```

### Send with Attachment
```bash
osascript <<'EOF'
tell application "Mail"
    set newMessage to make new outgoing message with properties {subject:"带附件", content:"请查收附件"}
    tell newMessage
        make new to recipient at end of to recipients with properties {address:"to@example.com"}
        make new attachment with properties {file name:POSIX file "/path/to/file.pdf"} at after last paragraph
    end tell
    send newMessage
end tell
EOF
```

### Create Draft (不发送)
```bash
osascript <<'EOF'
tell application "Mail"
    set newMessage to make new outgoing message with properties {subject:"草稿", content:"内容", visible:true}
    tell newMessage
        make new to recipient at end of to recipients with properties {address:"to@example.com"}
    end tell
    -- 不调用 send，保存为草稿
end tell
EOF
```

## Read Emails

### Get Unread Count
```bash
osascript -e 'tell application "Mail" to return unread count of inbox'
```

### List Unread Emails
```bash
osascript <<'EOF'
tell application "Mail"
    set unreadMessages to (messages of inbox whose read status is false)
    set output to ""
    repeat with msg in unreadMessages
        set output to output & "From: " & (sender of msg) & linefeed
        set output to output & "Subject: " & (subject of msg) & linefeed
        set output to output & "Date: " & (date received of msg) & linefeed
        set output to output & "---" & linefeed
    end repeat
    return output
end tell
EOF
```

### Read Specific Email Content
```bash
osascript <<'EOF'
tell application "Mail"
    set msgs to (messages of inbox whose read status is false)
    if (count of msgs) > 0 then
        set firstMsg to item 1 of msgs
        set msgContent to content of firstMsg
        return msgContent
    end if
end tell
EOF
```

### Get Recent Emails (last N)
```bash
osascript <<'EOF'
tell application "Mail"
    set recentMsgs to messages 1 thru 5 of inbox
    set output to ""
    repeat with msg in recentMsgs
        set output to output & (subject of msg) & " - " & (sender of msg) & linefeed
    end repeat
    return output
end tell
EOF
```

## Search Emails

### Search by Subject
```bash
osascript <<'EOF'
tell application "Mail"
    set foundMsgs to (messages of inbox whose subject contains "关键词")
    set output to ""
    repeat with msg in foundMsgs
        set output to output & (subject of msg) & linefeed
    end repeat
    return output
end tell
EOF
```

### Search by Sender
```bash
osascript <<'EOF'
tell application "Mail"
    set foundMsgs to (messages of inbox whose sender contains "someone@example.com")
    return count of foundMsgs
end tell
EOF
```

### Search by Date Range
```bash
osascript <<'EOF'
tell application "Mail"
    set startDate to date "2024-01-01"
    set foundMsgs to (messages of inbox whose date received > startDate)
    return count of foundMsgs
end tell
EOF
```

## Manage Emails

### Mark as Read
```bash
osascript <<'EOF'
tell application "Mail"
    set unreadMsgs to (messages of inbox whose read status is false)
    repeat with msg in unreadMsgs
        set read status of msg to true
    end repeat
end tell
EOF
```

### Delete Email
```bash
osascript <<'EOF'
tell application "Mail"
    set msgsToDelete to (messages of inbox whose subject contains "spam")
    repeat with msg in msgsToDelete
        delete msg
    end repeat
end tell
EOF
```

### Move to Folder
```bash
osascript <<'EOF'
tell application "Mail"
    set targetMailbox to mailbox "Archive" of account "iCloud"
    set msgsToMove to (messages of inbox whose subject contains "存档")
    repeat with msg in msgsToMove
        move msg to targetMailbox
    end repeat
end tell
EOF
```

## Account & Mailbox Info

### List Accounts
```bash
osascript -e 'tell application "Mail" to return name of every account'
```

### List Mailboxes
```bash
osascript -e 'tell application "Mail" to return name of every mailbox'
```

### Get Account Email
```bash
osascript <<'EOF'
tell application "Mail"
    set accts to every account
    set output to ""
    repeat with acct in accts
        set output to output & (name of acct) & ": " & (email addresses of acct) & linefeed
    end repeat
    return output
end tell
EOF
```

## Tips

1. **App Must Be Running**: Mail app should be running for most operations
2. **Large Inboxes**: Use `messages 1 thru N` to limit results
3. **POSIX Paths**: Use `POSIX file "/path"` for attachment paths
4. **Unicode Support**: Chinese characters work natively
5. **Permissions**: First run requires granting automation permission
