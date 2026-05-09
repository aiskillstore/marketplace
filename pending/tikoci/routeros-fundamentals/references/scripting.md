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

## Comments

```routeros
# This is a comment (single-line only)
:put "hello"  # Inline comment after command
```

No multi-line comment syntax exists. Each line needs its own `#`.

## `:execute` vs `:do`

```routeros
# :do — runs inline, blocks until complete
:do { /ip/address/print } on-error={ :put "failed" }

# :execute — runs in BACKGROUND, returns immediately
# Result can be captured to file or as-string
:local jobId [:execute script="/interface/print"]

# :execute with as-string — BLOCKS (not background)
:local result [:execute script=":put hello" as-string]

# :execute with file — runs in background, writes output to file
:execute script="/export" file="backup"
```

**Key difference:** `:execute` without `as-string` runs asynchronously — the script continues immediately. With `as-string`, it blocks and returns the output. Executed scripts are limited to 64KB.

## `:parse` — Dynamic Code

```routeros
# Parse a string into an executable function
:global myFunc [:parse ":put hello!"]
$myFunc

# Useful for building commands dynamically
:local cmd ":put (1 + 2)"
:local fn [:parse $cmd]
$fn   # → 3
```

`:parse` compiles a string into a callable function. This is the only way to create "functions" in RouterOS — the `do={}` syntax for globals is syntactic sugar for `:parse`.

## Array Operations

```routeros
# Create array
:local arr {1; 2; 3; "four"}

# Named keys
:local dict {name="router1"; ip=192.168.1.1}

# Access by index (uses -> not [])
:put ($arr->0)         # → 1

# Access by key
:put ($dict->"name")   # → "router1"

# Set element value
:set ($dict->"name") "router2"

# Array length
:put [:len $arr]       # → 4

# Append to array (no built-in append — rebuild or use set)
:set arr ($arr, 5)     # append 5

# Loop with keys and values
:foreach k,v in=$dict do={
  :put "$k=$v"
}

# Loop values only
:foreach v in=$arr do={
  :put $v
}
```

**⚠️ Array key sorting:** Elements with named keys are sorted alphabetically. Elements without keys preserve insertion order but are moved before keyed elements.

**⚠️ Key names with uppercase or special chars** must be quoted: `($arr->"myKey")`.

## `:serialize` / `:deserialize` (JSON)

RouterOS 7.x supports JSON serialization:

```routeros
# Serialize array to JSON
:local data {name="test"; value=42}
:put [:serialize to=json value=$data]
# → {"name":"test","value":42}

# Pretty print
:put [:serialize to=json value=$data options=json.pretty]

# Prevent string→number conversion
:put [:serialize to=json value=$data options=json.no-string-conversion]

# Deserialize JSON string to array
:local parsed [:deserialize from=json value="{\"name\":\"test\"}"]
:put ($parsed->"name")   # → test

# Deserialize from file
:deserialize [/file/get config.json contents] from=json

# Also supports DSV (delimiter-separated values)
:put [:serialize to=dsv delimiter=";" value=$data]
```

**DSV options:** `dsv.plain` (no header), `dsv.array` (header as keys), `dsv.wrap-strings`, `dsv.remap` (merge array of dicts).

## `/system/script` — Script Repository

```routeros
# Add stored script
/system/script/add name=my-backup source={
  /export file="daily-backup"
  :log info "Backup complete"
}

# Run stored script
/system/script/run my-backup

# List scripts
/system/script/print

# Edit script source
/system/script/set my-backup source={...new code...}

# Remove
/system/script/remove my-backup
```

**Properties:** `name`, `source`, `policy`, `comment`, `dont-require-permissions`, `owner` (read-only), `run-count` (read-only), `last-started` (read-only).

## Script Permissions (Policies)

Scripts have permission policies that control what they can access:

| Policy | Allows |
|--------|--------|
| `read` | Retrieve configuration |
| `write` | Change configuration |
| `policy` | Manage users and policies |
| `reboot` | Reboot the router |
| `password` | Change passwords |
| `ftp` | FTP access, send/retrieve files |
| `sensitive` | Change "hide sensitive" parameter |
| `sniff` | Run sniffer, torch |
| `test` | Run ping, traceroute, bandwidth-test |
| `romon` | RoMON access |

**Rules:**
- A script can only execute another script with **equal or higher** permissions
- `dont-require-permissions=yes` bypasses the check (useful for Netwatch/scheduler scripts with limited permissions)
- When run from CLI, **user permissions** apply. Use `run use-script-permissions` to use the script's own policy set.

## Important Gotchas

- **No pipes, no redirection** — can't do `cmd | grep` or `cmd > file`
- **`$` is required** to reference variables — `:put myVar` prints literal "myVar"
- **Array indexing** uses `->` not `[]` — `($arr->0)` for first element
- **String comparison** uses `=` not `==` — `(:if ($a = "test") do={...})`
- **Command substitution** uses `[...]` not `$(...)` — `:local result [/system/identity/get name]`
- **Semicolons in arrays** — `{1; 2; 3}` not `{1, 2, 3}`
- **Script line continuation** — use `\` at end of line
- **Property names with hyphens** — use quotes in find: `[find where "mac-address"="AA:BB:CC:DD:EE:FF"]`
- **Variable names are case-sensitive** — `$myVar` ≠ `$myVAR`
- **`:set` without value undefines** — `:global myVar; :set myVar` removes it from environment
- **`:execute` script size limit** — 64KB max for executed scripts
- **Global variables survive across script runs** but NOT across reboots

> **Source:**
> - Rosetta: page 47579229 (Scripting) — comprehensive language reference
> - Reference: `rest-api-patterns.md` — REST vs scripting interface differences
> - Note: `:serialize`/`:deserialize` are RouterOS 7.x features (from docs, not lab-verified)
> - Note: Script permissions table from official docs, verified against page 47579229
