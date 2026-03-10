---
name: codebase-search
description: Search and navigate large codebases efficiently. Use when finding specific code patterns, tracing function calls, understanding code structure, or locating bugs. Handles semantic search, grep patterns, AST analysis.
allowed-tools: Read Grep Glob Bash
metadata:
  tags: codebase-search, grep, code-navigation, pattern-matching
  platforms: Claude, ChatGPT, Gemini
---


# Codebase Search

## When to use this skill
- Finding specific functions or classes
- Tracing function calls and dependencies
- Understanding code structure and architecture
- Finding usage examples
- Identifying code patterns
- Locating bugs or issues
- Code archaeology (understanding legacy code)
- Impact analysis before changes

## Instructions

### Step 1: Understand what you're looking for

**Feature implementation**:
- Where is feature X implemented?
- How does feature Y work?
- What files are involved in feature Z?

**Bug location**:
- Where is this error coming from?
- What code handles this case?
- Where is this data being modified?

**API usage**:
- How is this API used?
- Where is this function called?
- What are examples of using this?

**Configuration**:
- Where are settings defined?
- How is this configured?
- What are the config options?

### Step 2: Choose search strategy

**Semantic search** (for conceptual questions):
```
Use when: You understand what you're looking for conceptually
Examples:
- "How do we handle user authentication?"
- "Where is email validation implemented?"
- "How do we connect to the database?"

Benefits:
- Finds relevant code by meaning
- Works with unfamiliar codebases
- Good for exploratory searches
```

**Grep** (for exact text/patterns):
```
Use when: You know exact text or patterns
Examples:
- Function names: "def authenticate"
- Class names: "class UserManager"
- Error messages: "Invalid credentials"
- Specific strings: "API_KEY"

Benefits:
- Fast and precise
- Works with regex patterns
- Good for known terms
```

**Glob** (for file discovery):
```
Use when: You need to find files by pattern
Examples:
- "**/*.test.js" (all test files)
- "**/config*.yaml" (config files)
- "src/**/*Controller.py" (controllers)

Benefits:
- Quickly find files by type
- Discover file structure
- Locate related files
```

### Step 3: Search workflow

**1. Start broad, then narrow**:
```
Step 1: Semantic search "How does authentication work?"
Result: Points to auth/ directory

Step 2: Grep in auth/ for specific function
Pattern: "def verify_token"
Result: Found in auth/jwt.py

Step 3: Read the file
File: auth/jwt.py
Result: Understand implementation
```

**2. Use directory targeting**:
```
# Start without target (search everywhere)
Query: "Where is user login implemented?"
Target: []

# Refine with specific directory
Query: "Where is login validated?"
Target: ["backend/auth/"]
```

**3. Combine searches**:
```
# Find where feature is implemented
Semantic: "user registration flow"

# Find all files involved
Grep: "def register_user"

# Find test files
Glob: "**/*register*test*.py"

# Understand the implementation
Read: registration.py, test_registration.py
```

### Step 4: Common search patterns

**Find function definition**:
```bash
# Python
grep -n "def function_name" --type py

# JavaScript
grep -n "function functionName" --type js
grep -n "const functionName = " --type js

# TypeScript
grep -n "function functionName" --type ts
grep -n "export const functionName" --type ts

# Go
grep -n "func functionName" --type go

# Java
grep -n "public.*functionName" --type java
```

**Find class definition**:
```bash
# Python
grep -n "class ClassName" --type py

# JavaScript/TypeScript
grep -n "class ClassName" --type js,ts

# Java
grep -n "public class ClassName" --type java

# C++
grep -n "class ClassName" --type cpp
```

**Find class/function usage**:
```bash
# Python
grep -n "ClassName(" --type py
grep -n "function_name(" --type py

# JavaScript
grep -n "new ClassName" --type js
grep -n "functionName(" --type js
```

**Find imports/requires**:
```bash
# Python
grep -n "from.*import.*ModuleName" --type py
grep -n "import.*ModuleName" --type py

# JavaScript
grep -n "import.*from.*module-name" --type js
grep -n "require.*module-name" --type js

# Go
grep -n "import.*package-name" --type go
```

**Find configuration**:
```bash
# Config files
glob "**/*config*.{json,yaml,yml,toml,ini}"

# Environment variables
grep -n "process\\.env\\." --type js
grep -n "os\\.environ" --type py

# Constants
grep -n "^[A-Z_]+\\s*=" --type py
grep -n "const [A-Z_]+" --type js
```

**Find TODO/FIXME**:
```bash
grep -n "TODO|FIXME|HACK|XXX" -i
```

**Find error handling**:
```bash
# Python
grep -n "try:|except|raise" --type py

# JavaScript
grep -n "try|catch|throw" --type js

# Go
grep -n "if err != nil" --type go
```

### Step 5: Advanced techniques

**Trace data flow**:
```
1. Find where data is created
   Semantic: "Where is user object created?"

2. Search for variable usage
   Grep: "user\\." with context lines

3. Follow transformations
   Read: Files that modify user

4. Find where it's consumed
   Grep: "user\\." in relevant files
```

**Find all callsites of a function**:
```
1. Find function definition
   Grep: "def process_payment"
   Result: payments/processor.py:45

2. Find all imports of that module
   Grep: "from payments.processor import"
   Result: Multiple files

3. Find all calls to the function
   Grep: "process_payment\\("
   Result: All callsites

4. Read each callsite for context
   Read: Each file with context
```

**Understand a feature end-to-end**:
```
1. Find API endpoint
   Semantic: "Where is user registration endpoint?"
   Result: routes/auth.py

2. Trace to controller
   Read: routes/auth.py
   Find: Calls to AuthController.register

3. Trace to service
   Read: controllers/auth.py
   Find: Calls to UserService.create_user

4. Trace to database
   Read: services/user.py
   Find: Database operations

5. Find tests
   Glob: "**/*auth*test*.py"
   Read: Test files for examples
```

**Find related files**:
```
1. Start with known file
   Example: models/user.py

2. Find imports of this file
   Grep: "from models.user import"

3. Find files this imports
   Read: models/user.py
   Note: Import statements

4. Build dependency graph
   Map: All related files
```

**Impact analysis**:
```
Before changing function X:

1. Find all callsites
   Grep: "function_name\\("

2. Find all tests
   Grep: "test.*function_name" -i

3. Check related functionality
   Semantic: "What depends on X?"

4. Review each usage
   Read: Each file using function

5. Plan changes
   Document: Impact and required updates
```

### Step 6: Search optimization

**Use appropriate context**:
```bash
# See surrounding context
grep -n "pattern" -C 5  # 5 lines before and after
grep -n "pattern" -B 3  # 3 lines before
grep -n "pattern" -A 3  # 3 lines after
```

**Case sensitivity**:
```bash
# Case insensitive
grep -n "pattern" -i

# Case sensitive (default)
grep -n "Pattern"
```

**File type filtering**:
```bash
# Specific type
grep -n "pattern" --type py

# Multiple types
grep -n "pattern" --type py,js,ts

# Exclude types
grep -n "pattern" --glob "!*.test.js"
```

**Regex patterns**:
```bash
# Any character: .
grep -n "function.*Name"

# Start of line: ^
grep -n "^class"

# End of line: $
grep -n "TODO$"

# Optional: ?
grep -n "function_name_?()"

# One or more: +
grep -n "[A-Z_]+"

# Zero or more: *
grep -n "import.*"

# Alternatives: |
grep -n "TODO|FIXME"

# Groups: ()
grep -n "(get|set)_user"

# Escape special chars: \
grep -n "function\(\)"
```

## Best practices

1. **Start with semantic search**: For unfamiliar code or conceptual questions
2. **Use grep for precision**: When you know exact terms
3. **Combine multiple searches**: Build understanding incrementally
4. **Read surrounding context**: Don't just look at matching lines
5. **Check file history**: Use `git blame` for context
6. **Document findings**: Note important discoveries
7. **Verify assumptions**: Read actual code, don't assume
8. **Use directory targeting**: Narrow scope when possible
9. **Follow the data**: Trace data flow through the system
10. **Check tests**: Tests often show usage examples

## Common search scenarios

### Scenario 1: Understanding a bug
```
1. Find error message
   Grep: "exact error message"

2. Find where it's thrown
   Read: File with error

3. Find what triggers it
   Semantic: "What causes X error?"

4. Find related code
   Grep: Related function names

5. Check tests
   Glob: "**/*test*.py"
   Look: For related test cases
```

### Scenario 2: Learning a new codebase
```
1. Find entry point
   Semantic: "Where does the application start?"
   Common files: main.py, index.js, app.py

2. Find main routes/endpoints
   Grep: "route|endpoint|@app\\."

3. Find data models
   Semantic: "Where are data models defined?"
   Common: models/, entities/

4. Find configuration
   Glob: "**/*config*"

5. Read README and docs
   Read: README.md, docs/
```

### Scenario 3: Refactoring preparation
```
1. Find all usages
   Grep: "function_to_change"

2. Find tests
   Grep: "test.*function_to_change"

3. Find dependencies
   Semantic: "What does X depend on?"

4. Check imports
   Grep: "from.*import.*X"

5. Document scope
   List: All affected files
```

### Scenario 4: Adding a feature
```
1. Find similar features
   Semantic: "How is similar feature implemented?"

2. Find where to add code
   Semantic: "Where should new feature go?"

3. Check patterns
   Read: Similar implementations

4. Find tests to emulate
   Glob: Test files for similar features

5. Check documentation
   Grep: "TODO.*new feature" -i
```

## Tools integration

**Git integration**:
```bash
# Who changed this line?
git blame filename

# History of a file
git log -p filename

# Find when function was added
git log -S "function_name" --source --all

# Find commits mentioning X
git log --grep="feature name"
```

**IDE integration**:
- Use "Go to Definition" for quick navigation
- Use "Find References" for usage
- Use "Find in Files" for broad search
- Use symbol search for classes/functions

**Documentation**:
- Check inline comments
- Look for docstrings
- Read README files
- Check architecture docs

## Troubleshooting

**No results found**:
- Check spelling and case sensitivity
- Try semantic search instead of grep
- Broaden search scope (remove directory target)
- Try different search terms
- Check if files are in .gitignore

**Too many results**:
- Add directory targeting
- Use more specific patterns
- Filter by file type
- Use exact phrases (quotes)

**Wrong results**:
- Be more specific in query
- Use grep instead of semantic for exact terms
- Add context to semantic queries
- Check file types

## References

- [Ripgrep User Guide](https://github.com/BurntSushi/ripgrep/blob/master/GUIDE.md)
- [Regular Expressions Tutorial](https://regexone.com/)
- [Git Blame Guide](https://git-scm.com/docs/git-blame)

## Examples

### Example 1: Basic usage
<!-- Add example content here -->

### Example 2: Advanced usage
<!-- Add advanced example content here -->
