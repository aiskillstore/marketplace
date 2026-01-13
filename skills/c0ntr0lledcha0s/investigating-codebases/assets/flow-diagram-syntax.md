# Execution Flow Diagram Syntax

Guide for creating clear execution flow diagrams in investigations.

## Simple Linear Flow

```
[Start] → [Step 1] → [Step 2] → [Step 3] → [End]
```

Example:
```
User Login Request
  → Validate Credentials (auth.ts:25)
  → Generate JWT Token (jwt.ts:42)
  → Set Cookie (auth.ts:67)
  → Redirect to Dashboard
```

## Flow with Branches

```
[Start] → [Decision]
            ├─ [Yes Path] → [Action A]
            └─ [No Path] → [Action B]
```

Example:
```
Authentication Check
  ├─ Valid Token → Continue to Protected Route
  └─ Invalid Token → Redirect to Login
```

## Data Flow

```
[Input Data]
  → [Transform 1]
  → [Transform 2]
  → [Storage/Output]
```

Example:
```
User Form Data
  → Validation (validators/user.ts:15)
  → Sanitization (sanitize.ts:42)
  → Hash Password (crypto.ts:88)
  → Save to DB (userRepo.ts:120)
```

## Multi-Layer Flow

```
Presentation Layer
  ↓
Business Logic Layer
  ↓
Data Access Layer
  ↓
Database
```

Example:
```
UserController (controllers/user.ts:25)
  ↓
UserService (services/userService.ts:42)
  ↓
UserRepository (repositories/userRepo.ts:78)
  ↓
PostgreSQL Database
```

---

*Part of research-agent/investigating-codebases skill*
