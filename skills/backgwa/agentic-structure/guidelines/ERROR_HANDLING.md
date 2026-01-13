# Error Handling Guidelines

## Purpose and Mindset
Error handling is not primarily about catching exceptions; it is about designing and implementing code so exceptions are less likely to occur. Assume all code can be deployed to production and exposed to real users and real traffic. Failures should be predictable, safe, and maintainable.

## Core Principles
- Exceptions are not a normal control-flow tool. When possible, express failure as an explicit error result.
- Handle exceptions only when necessary. Use the Meaningful Error Handling Test below to decide.
- Every failure must have a clear "owner" for where it is handled. Convert/map failures consistently at boundaries.
- Do not leak sensitive information through error messages or logs.

## Application Philosophy
These guidelines are designed to be applied thoughtfully, not rigidly:

- **Strive to follow** - Aim to apply these principles consistently, but use judgment when exceptions are warranted
- **Apply incrementally** - Build good habits gradually; it's acceptable to apply these imperfectly at first and improve over time
- **Context matters** - Adapt guidelines to project size, team structure, and specific requirements
- **Progress over perfection** - Moving in the right direction is better than perfect adherence that delays delivery
- **Question and clarify** - When unsure, err on the side of asking or documenting your reasoning

## Decision Point: When to Add Try-Catch

### Meaningful Error Handling Test
**Prefer to add try-catch when it meets at least one of these criteria** (use judgment for edge cases):

#### Signal High - Prefer try-catch when these apply
- [ ] Can recover from error (retry with backoff, fallback to alternate path, use cached value)
- [ ] Can add contextual information not in original error (what operation was being performed, which resource)
- [ ] Can transform error into domain-specific error type (DatabaseError → UserNotFoundError)
- [ ] Can clean up resources (close files, release connections, unlock resources)
- [ ] Can apply different handling based on error type (transient vs permanent, auth vs validation)

#### Signal Low - Generally avoid unless there's a compelling reason
- [ ] Catch only to log and rethrow unchanged
- [ ] Catch only to wrap in generic error with no added context
- [ ] Catch broad exception type (Error, Exception) and treat all cases identically
- [ ] Catch to return undefined/null without signaling failure to caller
- [ ] Catch to hide errors from caller who needs to know about failure

### Decision Template - Use this as a mental model
**Before adding try-catch, ask yourself:**
"What specific error am I catching, and what meaningful action am I taking?"
"If you cannot identify both, prefer to let the error propagate instead."

### Examples

#### Meaningful Try-Catch

Pattern 1: Wrap an operation in a try block, catch any error that occurs, and throw a new error that includes what operation was being performed and the original error message. This adds context about what failed.

Pattern 2: Attempt to retrieve data from a primary API. If it fails, log a warning and retrieve the data from a cache instead. This provides a fallback to maintain availability when the primary source is unavailable.

Pattern 3: Wrap an operation in a try block. In the catch block, check the error type. If it is a transient or temporary error, retry the operation later. If it is a business rule error like fraud, block the request and notify. For any other error type, let the error propagate upward.

Pattern 4: Open a resource like a file, then in a try block process the resource. In the finally block, which always executes regardless of success or failure, close the resource to prevent leaks.

#### Patterns to Avoid

Pattern 1: Wrap an operation in a try block, catch any error, log it to the console, and then immediately rethrow the error. This adds no value and only introduces noise.

Pattern 2: Wrap a data-fetching operation in a try block. If an error occurs, catch it and return null or undefined. The caller cannot distinguish between a successful fetch that returned no data and a failed fetch.

Pattern 3: Wrap an operation in a try block. If an error occurs, catch it and throw a generic error like "Something went wrong". This discards all the useful information from the original error, making debugging impossible.

Pattern 4: Wrap multiple operations in a try block. Catch all errors regardless of type and return a simple success or failure flag. This loses error details and prevents the caller from handling different types of errors appropriately.

## Where to Handle Errors (Layer Responsibilities)
Separate responsibilities by layer:
- Input boundary (UI/HTTP/CLI): validate inputs, normalize parameters, and return/apply a clear error response format.
- Domain/business logic: represent rule violations explicitly and keep behavior predictable.
- Integration/infra (external APIs/DB/files): deal with dependency failures (timeouts, retries, circuit breakers) and translate them into meaningful errors for higher layers.
- Top-level boundary (controller/handler): map internal failures into client-friendly responses and apply consistent logging/tracing policies.

## Do / Don't
### Do
- Validate inputs early so invalid states do not flow inward.
- Recover only when recovery is meaningful (retry, fallback, alternate path).
- When rethrowing, add context about what you were trying to do when it failed.
- If returning errors, keep types/codes/messages consistent so callers can handle them reliably.

### Don't
- Don't wrap broad areas with `try/catch` to “handle everything”.
- Don't swallow exceptions or hide failures behind meaningless defaults.
- Don't use exceptions as routine branching for normal logic.
- Don't expose internal details or sensitive data (tokens, passwords, personal data) in errors.

## Recovery vs Fail Fast
Do not try to recover from every failure. Decide based on recoverability and cost:
- Recoverable failures: transient network issues, transient 5xx, limited timeouts
  - Retries should include backoff/jitter and have clear attempt/time limits.
- Non-recoverable failures: invalid input, domain rule violations, authorization failures
  - Fail fast and let the caller decide the next action.

## User-Facing Error Messages
- Provide understandable messages to users (or API clients), but do not expose internal causes, stack traces, or infrastructure details.
- When needed, separate user-facing messages from developer/operator context.
- Be careful not to leak unnecessary information in authentication-related failures (e.g., account existence).

## Security Considerations
- Never reveal internal implementation details (queries, stacks, paths, configuration) in error responses.
- Control failure patterns for authentication and critical endpoints with abuse prevention in mind.
- Do not over-explain security-related failures.

## Maintainability Considerations
- Error handling policy should be consistent across the project.
- If a new failure pattern becomes common, refine how and where it is handled to keep behavior predictable.
