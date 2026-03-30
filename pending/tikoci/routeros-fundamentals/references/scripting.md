# RouterOS Scripting Language

## Overview

RouterOS has its own scripting language (`.rsc` files) used for automation. It is NOT bash,
NOT Lua, NOT any standard language. It runs inside the RouterOS CLI environment.

## Variable Declaration

```routeros
# Local variable (scoped to current script/function)
:local myVar "hello"

# Global variable (persists across scripts until reboot)
:global myVar "hello"

# Variable reference
:put $myVar
```

## Data Types

| Type | Syntax | Example |
|---|---|---|
| String | `"text"` | `"hello world"` |
| Number | `123` | `42`, `0xFF` |
| Boolean | `true` / `false` / `yes` / `no` | `true` |
| IP Address | `1.2.3.4` | `192.168.1.1` |
| IP Prefix | `1.2.3.0/24` | `10.0.0.0/8` |
| Array | `{1; 2; 3}` or `{"a"; "b"}` | `{1; 2; "mixed"}` |
| Time | `1h2m3s` | `30s`, `5m`, `1d` |
| Nil | (no keyword) | absent value |

## String Operations

```routeros
# Concatenation
:local greeting ("Hello " . "World")

# Substring (pick)
:local sub [:pick "Hello" 0 3]     # → "Hel"

# Length
:local len [:len "Hello"]          # → 5

# Find
:local pos [:find "Hello World" "World"]  # → 6

# Convert to/from
:local num [:tonum "42"]
:local str [:tostr 42]
```

## Control Flow

```routeros
# If/else
:if ($x > 10) do={
  :put "big"
} else={
  :put "small"
}

# For loop
:for i from=1 to=10 do={
  :put $i
}

# Foreach
:foreach item in=$myArray do={
  :put $item
}

# While
:while ($count < 10) do={
  :set count ($count + 1)
}
```

**Critical syntax:** `do={...}` and `else={...}` use `=` and curly braces. No colon before `do`.

## Functions

```routeros
# Define a function (stored as a global variable)
:global myFunc do={
  :local arg1 $1
  :return ("Result: " . $arg1)
}

# Call it
:put [$myFunc "test"]
```

## Common Built-in Commands

```routeros
:put "text"                    # Print to console
:log info "message"            # Write to system log
:delay 5s                      # Sleep
:execute script="/path/to/script"  # Run another script
:resolve "example.com"         # DNS lookup
:ping 8.8.8.8 count=3         # Ping
:time { /ip/route/print }     # Measure execution time
:environment print             # Show all variables
```

## Working with Router Config

```routeros
# Add entry and capture its ID
:local newId [/ip/address/add address=10.0.0.1/24 interface=ether1]

# Find entries
:local entries [/ip/address/find where interface=ether1]

# Get property value
:local addr [/ip/address/get $newId address]

# Set property
/ip/address/set $newId disabled=yes

# Remove
/ip/address/remove $newId
```

## Scheduler (Cron Equivalent)

```routeros
/system/scheduler/add name=my-task interval=1h \
  on-event="/system/script/run myScript"
```

## File Operations

```routeros
# Read file content
:local content [/file/get myfile.txt contents]

# Files are stored in RouterOS flash — /file/print lists them
/file/print
```

## Error Handling

```routeros
:do {
  /ip/address/add address=invalid interface=ether1
} on-error={
  :log error "Failed to add address"
}
```

## Important Gotchas

- **No pipes, no redirection** — can't do `cmd | grep` or `cmd > file`
- **`$` is required** to reference variables — `:put myVar` prints literal "myVar"
- **Array indexing** uses `->` not `[]` — `($arr->0)` for first element
- **String comparison** uses `=` not `==` — `(:if ($a = "test") do={...})`
- **Command substitution** uses `[...]` not `$(...)` — `:local result [/system/identity/get name]`
- **Semicolons in arrays** — `{1; 2; 3}` not `{1, 2, 3}`
- **Script line continuation** — use `\` at end of line
- **Property names with hyphens** — use quotes in find: `[find where "mac-address"="AA:BB:CC:DD:EE:FF"]`
