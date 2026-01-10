# Finder AppleScript Reference

## Open Folders

### Open Folder by Path
```bash
osascript <<'EOF'
tell application "Finder"
    activate
    open folder POSIX file "/Users/seven/Documents"
end tell
EOF
```

### Open Home Folder
```bash
osascript -e 'tell application "Finder" to open home'
```

### Open Desktop
```bash
osascript -e 'tell application "Finder" to open desktop'
```

### Open Downloads
```bash
osascript <<'EOF'
tell application "Finder"
    activate
    open folder "Downloads" of home
end tell
EOF
```

### Open Applications Folder
```bash
osascript <<'EOF'
tell application "Finder"
    activate
    open folder "Applications" of startup disk
end tell
EOF
```

### Reveal File in Finder
```bash
osascript <<'EOF'
tell application "Finder"
    activate
    reveal POSIX file "/Users/seven/Documents/file.txt"
end tell
EOF
```

## File Operations

### Create New Folder
```bash
osascript <<'EOF'
tell application "Finder"
    make new folder at POSIX file "/Users/seven/Documents" with properties {name:"新文件夹"}
end tell
EOF
```

### Copy File
```bash
osascript <<'EOF'
tell application "Finder"
    set sourceFile to POSIX file "/Users/seven/Documents/source.txt" as alias
    set destFolder to POSIX file "/Users/seven/Desktop" as alias
    duplicate sourceFile to destFolder
end tell
EOF
```

### Move File
```bash
osascript <<'EOF'
tell application "Finder"
    set sourceFile to POSIX file "/Users/seven/Documents/file.txt" as alias
    set destFolder to POSIX file "/Users/seven/Desktop" as alias
    move sourceFile to destFolder
end tell
EOF
```

### Rename File
```bash
osascript <<'EOF'
tell application "Finder"
    set targetFile to POSIX file "/Users/seven/Documents/old.txt" as alias
    set name of targetFile to "new.txt"
end tell
EOF
```

### Delete File (Move to Trash)
```bash
osascript <<'EOF'
tell application "Finder"
    set targetFile to POSIX file "/Users/seven/Documents/delete.txt" as alias
    move targetFile to trash
end tell
EOF
```

### Empty Trash
```bash
osascript -e 'tell application "Finder" to empty trash'
```

### Empty Trash with Confirmation
```bash
osascript <<'EOF'
tell application "Finder"
    empty trash with security
end tell
EOF
```

## File Information

### Get File Info
```bash
osascript <<'EOF'
tell application "Finder"
    set targetFile to POSIX file "/Users/seven/Documents/file.txt" as alias
    set fileName to name of targetFile
    set fileSize to size of targetFile
    set modDate to modification date of targetFile
    return "Name: " & fileName & ", Size: " & fileSize & " bytes, Modified: " & modDate
end tell
EOF
```

### Check If File Exists
```bash
osascript <<'EOF'
tell application "Finder"
    set filePath to POSIX file "/Users/seven/Documents/test.txt"
    if exists filePath then
        return "File exists"
    else
        return "File does not exist"
    end if
end tell
EOF
```

### Get File Kind
```bash
osascript <<'EOF'
tell application "Finder"
    set targetFile to POSIX file "/Users/seven/Documents/file.pdf" as alias
    return kind of targetFile
end tell
EOF
```

### Get File Extension
```bash
osascript <<'EOF'
tell application "Finder"
    set targetFile to POSIX file "/Users/seven/Documents/file.txt" as alias
    return name extension of targetFile
end tell
EOF
```

## List Files

### List Files in Folder
```bash
osascript <<'EOF'
tell application "Finder"
    set targetFolder to POSIX file "/Users/seven/Documents" as alias
    set fileList to name of every file of targetFolder
    set output to ""
    repeat with f in fileList
        set output to output & f & linefeed
    end repeat
    return output
end tell
EOF
```

### List Folders in Directory
```bash
osascript <<'EOF'
tell application "Finder"
    set targetFolder to POSIX file "/Users/seven/Documents" as alias
    set folderList to name of every folder of targetFolder
    set output to ""
    repeat with f in folderList
        set output to output & f & linefeed
    end repeat
    return output
end tell
EOF
```

### List All Items
```bash
osascript <<'EOF'
tell application "Finder"
    set targetFolder to POSIX file "/Users/seven/Documents" as alias
    set itemList to name of every item of targetFolder
    set output to ""
    repeat with i in itemList
        set output to output & i & linefeed
    end repeat
    return output
end tell
EOF
```

### List Files by Extension
```bash
osascript <<'EOF'
tell application "Finder"
    set targetFolder to POSIX file "/Users/seven/Documents" as alias
    set pdfFiles to name of every file of targetFolder whose name extension is "pdf"
    set output to ""
    repeat with f in pdfFiles
        set output to output & f & linefeed
    end repeat
    return output
end tell
EOF
```

### Get Desktop Items
```bash
osascript <<'EOF'
tell application "Finder"
    set desktopItems to name of every item of desktop
    set output to ""
    repeat with i in desktopItems
        set output to output & i & linefeed
    end repeat
    return output
end tell
EOF
```

## Selection

### Get Selected Files
```bash
osascript <<'EOF'
tell application "Finder"
    set selectedItems to selection
    set output to ""
    repeat with i in selectedItems
        set output to output & (POSIX path of (i as alias)) & linefeed
    end repeat
    return output
end tell
EOF
```

### Select File
```bash
osascript <<'EOF'
tell application "Finder"
    activate
    select POSIX file "/Users/seven/Documents/file.txt"
end tell
EOF
```

### Select Multiple Files
```bash
osascript <<'EOF'
tell application "Finder"
    activate
    set file1 to POSIX file "/Users/seven/Documents/file1.txt" as alias
    set file2 to POSIX file "/Users/seven/Documents/file2.txt" as alias
    select {file1, file2}
end tell
EOF
```

## Window Management

### Get Frontmost Folder Path
```bash
osascript <<'EOF'
tell application "Finder"
    if (count of windows) > 0 then
        return POSIX path of (target of window 1 as alias)
    else
        return "No Finder window open"
    end if
end tell
EOF
```

### Open New Finder Window
```bash
osascript <<'EOF'
tell application "Finder"
    activate
    make new Finder window
end tell
EOF
```

### Close All Finder Windows
```bash
osascript -e 'tell application "Finder" to close every window'
```

### Set Window Bounds
```bash
osascript <<'EOF'
tell application "Finder"
    set bounds of window 1 to {100, 100, 800, 600}
end tell
EOF
```

### Set View Mode
```bash
osascript <<'EOF'
tell application "Finder"
    -- icon view, list view, column view, flow view (gallery)
    set current view of window 1 to list view
end tell
EOF
```

## Disk Information

### Get Startup Disk Name
```bash
osascript -e 'tell application "Finder" to return name of startup disk'
```

### Get Disk Free Space
```bash
osascript <<'EOF'
tell application "Finder"
    set diskInfo to startup disk
    return free space of diskInfo
end tell
EOF
```

### List Mounted Volumes
```bash
osascript <<'EOF'
tell application "Finder"
    set output to ""
    repeat with d in disks
        set output to output & (name of d) & linefeed
    end repeat
    return output
end tell
EOF
```

### Eject Volume
```bash
osascript <<'EOF'
tell application "Finder"
    eject disk "USB Drive"
end tell
EOF
```

## Labels and Tags

### Set File Label (Color)
```bash
osascript <<'EOF'
tell application "Finder"
    set targetFile to POSIX file "/Users/seven/Documents/important.txt" as alias
    -- label index: 0=none, 1=orange, 2=red, 3=yellow, 4=blue, 5=purple, 6=green, 7=gray
    set label index of targetFile to 2
end tell
EOF
```

### Get File Label
```bash
osascript <<'EOF'
tell application "Finder"
    set targetFile to POSIX file "/Users/seven/Documents/file.txt" as alias
    return label index of targetFile
end tell
EOF
```

## Tips

1. **POSIX Paths**: Use `POSIX file "/path"` for Unix-style paths
2. **Alias Conversion**: Convert to alias with `as alias` for operations
3. **Permissions**: Some operations require Full Disk Access
4. **Special Folders**: Use `home`, `desktop`, `startup disk` keywords
5. **Trash**: Items in Trash can be recovered until emptied
6. **Labels**: Labels are 0-7, correspond to Finder colors
7. **View Modes**: icon view, list view, column view, flow view
