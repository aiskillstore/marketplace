# Safari AppleScript Reference

## Open URLs

### Open URL in New Tab
```bash
osascript <<'EOF'
tell application "Safari"
    activate
    tell window 1
        set current tab to (make new tab with properties {URL:"https://www.google.com"})
    end tell
end tell
EOF
```

### Open URL in New Window
```bash
osascript <<'EOF'
tell application "Safari"
    activate
    make new document with properties {URL:"https://www.apple.com"}
end tell
EOF
```

### Open URL in Current Tab
```bash
osascript <<'EOF'
tell application "Safari"
    activate
    set URL of current tab of window 1 to "https://www.github.com"
end tell
EOF
```

### Open Multiple URLs
```bash
osascript <<'EOF'
tell application "Safari"
    activate
    set urlList to {"https://google.com", "https://github.com", "https://apple.com"}
    repeat with theURL in urlList
        tell window 1
            make new tab with properties {URL:theURL}
        end tell
    end repeat
end tell
EOF
```

## Get Page Information

### Get Current URL
```bash
osascript -e 'tell application "Safari" to return URL of current tab of window 1'
```

### Get Page Title
```bash
osascript -e 'tell application "Safari" to return name of current tab of window 1'
```

### Get Page Source (HTML)
```bash
osascript -e 'tell application "Safari" to return source of current tab of window 1'
```

### Get Selected Text
```bash
osascript <<'EOF'
tell application "Safari"
    do JavaScript "window.getSelection().toString()" in current tab of window 1
end tell
EOF
```

### Get All Tab URLs
```bash
osascript <<'EOF'
tell application "Safari"
    set output to ""
    repeat with t in tabs of window 1
        set output to output & (URL of t) & linefeed
    end repeat
    return output
end tell
EOF
```

### Get All Tab Titles
```bash
osascript <<'EOF'
tell application "Safari"
    set output to ""
    repeat with t in tabs of window 1
        set output to output & (name of t) & linefeed
    end repeat
    return output
end tell
EOF
```

## Tab Management

### Close Current Tab
```bash
osascript -e 'tell application "Safari" to close current tab of window 1'
```

### Close All Tabs Except Current
```bash
osascript <<'EOF'
tell application "Safari"
    tell window 1
        set currentIndex to index of current tab
        repeat with i from (count of tabs) to 1 by -1
            if i ≠ currentIndex then
                close tab i
            end if
        end repeat
    end tell
end tell
EOF
```

### Switch to Tab by Index
```bash
osascript -e 'tell application "Safari" to set current tab of window 1 to tab 2 of window 1'
```

### Get Tab Count
```bash
osascript -e 'tell application "Safari" to return count of tabs of window 1'
```

### Create New Tab
```bash
osascript <<'EOF'
tell application "Safari"
    activate
    tell window 1
        make new tab
    end tell
end tell
EOF
```

## JavaScript Execution

### Execute JavaScript
```bash
osascript <<'EOF'
tell application "Safari"
    do JavaScript "document.title" in current tab of window 1
end tell
EOF
```

### Click Element by ID
```bash
osascript <<'EOF'
tell application "Safari"
    do JavaScript "document.getElementById('submit-button').click()" in current tab of window 1
end tell
EOF
```

### Fill Form Field
```bash
osascript <<'EOF'
tell application "Safari"
    do JavaScript "document.getElementById('username').value = 'myuser'" in current tab of window 1
end tell
EOF
```

### Scroll Page
```bash
osascript <<'EOF'
tell application "Safari"
    do JavaScript "window.scrollTo(0, document.body.scrollHeight)" in current tab of window 1
end tell
EOF
```

### Get Element Text
```bash
osascript <<'EOF'
tell application "Safari"
    do JavaScript "document.querySelector('h1').innerText" in current tab of window 1
end tell
EOF
```

### Get All Links
```bash
osascript <<'EOF'
tell application "Safari"
    do JavaScript "Array.from(document.querySelectorAll('a')).map(a => a.href).join('\\n')" in current tab of window 1
end tell
EOF
```

## Window Management

### Get Window Count
```bash
osascript -e 'tell application "Safari" to return count of windows'
```

### Minimize Window
```bash
osascript -e 'tell application "Safari" to set miniaturized of window 1 to true'
```

### Maximize Window
```bash
osascript <<'EOF'
tell application "Safari"
    activate
    set bounds of window 1 to {0, 0, 1920, 1080}
end tell
EOF
```

### Close Window
```bash
osascript -e 'tell application "Safari" to close window 1'
```

### Create New Window
```bash
osascript <<'EOF'
tell application "Safari"
    activate
    make new document
end tell
EOF
```

## Navigation

### Go Back
```bash
osascript -e 'tell application "Safari" to do JavaScript "history.back()" in current tab of window 1'
```

### Go Forward
```bash
osascript -e 'tell application "Safari" to do JavaScript "history.forward()" in current tab of window 1'
```

### Reload Page
```bash
osascript -e 'tell application "Safari" to do JavaScript "location.reload()" in current tab of window 1'
```

### Stop Loading
```bash
osascript -e 'tell application "Safari" to do JavaScript "window.stop()" in current tab of window 1'
```

## Reading List

### Add Current Page to Reading List
```bash
osascript <<'EOF'
tell application "Safari"
    add reading list item (URL of current tab of window 1)
end tell
EOF
```

### Add URL to Reading List
```bash
osascript -e 'tell application "Safari" to add reading list item "https://example.com"'
```

## Bookmarks

### Get Bookmark Folders
```bash
osascript <<'EOF'
tell application "Safari"
    set output to ""
    repeat with f in bookmark folders
        set output to output & (name of f) & linefeed
    end repeat
    return output
end tell
EOF
```

## Search

### Google Search
```bash
osascript <<'EOF'
tell application "Safari"
    activate
    set searchQuery to "AppleScript tutorial"
    set searchURL to "https://www.google.com/search?q=" & (do shell script "python3 -c \"import urllib.parse; print(urllib.parse.quote('" & searchQuery & "'))\"")
    tell window 1
        set current tab to (make new tab with properties {URL:searchURL})
    end tell
end tell
EOF
```

## Tips

1. **Activation**: Use `activate` to bring Safari to front
2. **Window 1**: `window 1` refers to the frontmost window
3. **JavaScript Permissions**: May require "Allow JavaScript from Apple Events" in Safari Developer menu
4. **Tab Indexing**: Tabs are 1-indexed
5. **URL Encoding**: Encode special characters for URLs
6. **Private Windows**: Private windows have limited AppleScript access
7. **Synchronous Loading**: Scripts don't wait for pages to load; add delays if needed
