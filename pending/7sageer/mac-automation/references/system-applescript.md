# System AppleScript Reference

## Notifications

### Display Notification
```bash
osascript -e 'display notification "消息内容" with title "标题"'
```

### Notification with Subtitle
```bash
osascript -e 'display notification "消息内容" with title "标题" subtitle "副标题"'
```

### Notification with Sound
```bash
osascript -e 'display notification "任务完成" with title "提醒" sound name "Glass"'
```

### Available Sounds
Common system sounds: Basso, Blow, Bottle, Frog, Funk, Glass, Hero, Morse, Ping, Pop, Purr, Sosumi, Submarine, Tink

## Volume Control

### Get Current Volume
```bash
osascript -e 'output volume of (get volume settings)'
```

### Set Volume (0-100)
```bash
osascript -e 'set volume output volume 50'
```

### Mute
```bash
osascript -e 'set volume output muted true'
```

### Unmute
```bash
osascript -e 'set volume output muted false'
```

### Toggle Mute
```bash
osascript <<'EOF'
set currentMute to output muted of (get volume settings)
if currentMute then
    set volume output muted false
else
    set volume output muted true
end if
EOF
```

### Check If Muted
```bash
osascript -e 'output muted of (get volume settings)'
```

### Set Volume with Alert Volume
```bash
osascript -e 'set volume output volume 50 alert volume 50'
```

### Volume Up/Down
```bash
# Volume up by 10
osascript <<'EOF'
set currentVol to output volume of (get volume settings)
set newVol to currentVol + 10
if newVol > 100 then set newVol to 100
set volume output volume newVol
EOF

# Volume down by 10
osascript <<'EOF'
set currentVol to output volume of (get volume settings)
set newVol to currentVol - 10
if newVol < 0 then set newVol to 0
set volume output volume newVol
EOF
```

## Clipboard

### Get Clipboard Content
```bash
osascript -e 'the clipboard'
```

### Set Clipboard Text
```bash
osascript -e 'set the clipboard to "要复制的文本"'
```

### Get Clipboard as Specific Type
```bash
osascript -e 'the clipboard as text'
```

### Clear Clipboard
```bash
osascript -e 'set the clipboard to ""'
```

## Application Control

### Launch Application
```bash
osascript -e 'tell application "App Name" to activate'
```

### Quit Application
```bash
osascript -e 'tell application "App Name" to quit'
```

### Quit Application (Force)
```bash
osascript -e 'tell application "App Name" to quit saving no'
```

### Hide Application
```bash
osascript -e 'tell application "System Events" to set visible of process "App Name" to false'
```

### Check If App Is Running
```bash
osascript <<'EOF'
tell application "System Events"
    if exists process "Safari" then
        return "Running"
    else
        return "Not running"
    end if
end tell
EOF
```

### Get Running Applications
```bash
osascript -e 'tell application "System Events" to return name of every process whose background only is false'
```

### Get Frontmost Application
```bash
osascript -e 'tell application "System Events" to return name of first process whose frontmost is true'
```

### Switch to Application
```bash
osascript <<'EOF'
tell application "Safari"
    activate
    delay 0.5
end tell
EOF
```

## Dialogs

### Display Alert
```bash
osascript -e 'display alert "警告标题" message "详细信息"'
```

### Display Dialog with Input
```bash
osascript -e 'display dialog "请输入:" default answer ""'
```

### Display Dialog with Buttons
```bash
osascript -e 'display dialog "确认操作?" buttons {"取消", "确定"} default button "确定"'
```

### Choose File
```bash
osascript -e 'POSIX path of (choose file with prompt "选择文件")'
```

### Choose Folder
```bash
osascript -e 'POSIX path of (choose folder with prompt "选择文件夹")'
```

### Choose from List
```bash
osascript -e 'choose from list {"选项1", "选项2", "选项3"} with prompt "请选择:"'
```

## System Information

### Get Computer Name
```bash
osascript -e 'computer name of (system info)'
```

### Get User Name
```bash
osascript -e 'short user name of (system info)'
```

### Get System Version
```bash
osascript -e 'system version of (system info)'
```

### Get Current Date and Time
```bash
osascript -e 'current date'
```

### Get Free Memory
```bash
osascript -e 'do shell script "vm_stat | grep free | awk '\''{print $3}'\'' | sed '\''s/\\.//g'\''"'
```

## Screen & Display

### Get Screen Resolution
```bash
osascript -e 'tell application "Finder" to get bounds of window of desktop'
```

### Take Screenshot
```bash
osascript -e 'do shell script "screencapture ~/Desktop/screenshot.png"'
```

### Take Screenshot of Selection
```bash
osascript -e 'do shell script "screencapture -i ~/Desktop/screenshot.png"'
```

## Power Management

### Sleep Display
```bash
osascript -e 'tell application "System Events" to sleep'
```

### Prevent Sleep (Caffeinate)
```bash
osascript -e 'do shell script "caffeinate -d -t 3600 &"'
```

### Check Battery (MacBook)
```bash
osascript -e 'do shell script "pmset -g batt | grep -o '[0-9]*%'"'
```

## System Events (Danger Zone)

### Lock Screen
```bash
osascript -e 'tell application "System Events" to keystroke "q" using {control down, command down}'
```

### Sleep Computer
```bash
osascript -e 'tell application "System Events" to sleep'
```

### Restart (requires confirmation)
```bash
osascript -e 'tell application "System Events" to restart'
```

### Shutdown (requires confirmation)
```bash
osascript -e 'tell application "System Events" to shut down'
```

### Log Out
```bash
osascript -e 'tell application "System Events" to log out'
```

## Keyboard Simulation

### Keystroke
```bash
osascript -e 'tell application "System Events" to keystroke "hello"'
```

### Key with Modifiers
```bash
# Command+S (Save)
osascript -e 'tell application "System Events" to keystroke "s" using command down'

# Command+Shift+N
osascript -e 'tell application "System Events" to keystroke "n" using {command down, shift down}'
```

### Key Codes
```bash
# Press Enter (key code 36)
osascript -e 'tell application "System Events" to key code 36'

# Press Escape (key code 53)
osascript -e 'tell application "System Events" to key code 53'

# Press Tab (key code 48)
osascript -e 'tell application "System Events" to key code 48'
```

### Common Key Codes
- Return: 36
- Tab: 48
- Space: 49
- Delete: 51
- Escape: 53
- Arrow Up: 126
- Arrow Down: 125
- Arrow Left: 123
- Arrow Right: 124
- F1-F12: 122-111

## Dark Mode

### Check Dark Mode
```bash
osascript -e 'tell application "System Events" to tell appearance preferences to return dark mode'
```

### Toggle Dark Mode
```bash
osascript -e 'tell application "System Events" to tell appearance preferences to set dark mode to not dark mode'
```

### Set Dark Mode On
```bash
osascript -e 'tell application "System Events" to tell appearance preferences to set dark mode to true'
```

### Set Dark Mode Off
```bash
osascript -e 'tell application "System Events" to tell appearance preferences to set dark mode to false'
```

## Do Not Disturb

### Enable DND (macOS Monterey+)
```bash
osascript <<'EOF'
tell application "System Events"
    tell application process "Control Center"
        -- Click on Control Center menu bar item
        click menu bar item "Control Center" of menu bar 1
        delay 0.5
        -- Click Focus/DND
        click button "Focus" of window "Control Center"
    end tell
end tell
EOF
```

## Wi-Fi

### Get Wi-Fi Status
```bash
osascript -e 'do shell script "networksetup -getairportpower en0"'
```

### Turn Wi-Fi On
```bash
osascript -e 'do shell script "networksetup -setairportpower en0 on"'
```

### Turn Wi-Fi Off
```bash
osascript -e 'do shell script "networksetup -setairportpower en0 off"'
```

### Get Current Wi-Fi Network
```bash
osascript -e 'do shell script "networksetup -getairportnetwork en0"'
```

## Bluetooth

### Get Bluetooth Status
```bash
osascript -e 'do shell script "defaults read /Library/Preferences/com.apple.Bluetooth ControllerPowerState"'
```

## Tips

1. **Permissions**: System Events requires Accessibility permissions
2. **Danger Commands**: sleep/restart/shutdown may show confirmation dialogs
3. **Key Codes**: Search "Mac key codes" for complete list
4. **Delays**: Use `delay 0.5` between operations when needed
5. **Background Apps**: Some system operations need app in foreground
6. **Security**: Some operations blocked by SIP (System Integrity Protection)
7. **Version Differences**: Some commands vary by macOS version
