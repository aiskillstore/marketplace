# JSDoc Patterns and Best Practices

This reference provides detailed examples of common JSDoc patterns and anti-patterns for TypeScript.

## Table of Contents

- [Complete Examples](#complete-examples)
- [Advanced Tags](#advanced-tags)
- [Anti-Patterns](#anti-patterns)
- [Documentation Timing](#documentation-timing)

## Complete Examples

### Basic Function with All Tag Types

This example demonstrates proper use of common tags together:

```typescript
/**
 * Fetches user data from the API with automatic retry and timeout handling.
 * 
 * Requests will automatically retry up to 3 times if they fail with
 * transient network errors. The function will timeout after 30 seconds
 * if no response is received.
 * 
 * @param userId - The numeric ID of the user to fetch
 * @param options - Optional configuration for the request
 * @param options.timeout - Request timeout in milliseconds (default: 30000)
 * @param options.retries - Maximum number of retry attempts (default: 3)
 * @returns Promise resolving to the user object with id, name, and email fields
 * @throws {NotFoundError} When the user ID does not exist
 * @throws {TimeoutError} When the request exceeds the timeout duration
 * @throws {NetworkError} After exhausting all retry attempts
 * @example
 * ```typescript
 * const user = await fetchUser(123);
 * const userWithTimeout = await fetchUser(456, { timeout: 5000 });
 * ```
 * @deprecated Use {@link fetchUserV2} instead - this function will be removed in v3.0
 * @see fetchUserV2
 */
async function fetchUser(
    userId: number,
    options?: { timeout?: number; retries?: number }
): Promise<User> {
    // Implementation
}
```

### React Component Documentation

Document component props thoroughly to help other developers understand usage:

```typescript
/**
 * Displays a user profile card with optional edit capabilities.
 * 
 * This component renders user information in a visually appealing card format.
 * When the `editable` prop is true, users can modify the displayed information.
 * Changes are emitted through the `onUserChange` callback but not persisted
 * automatically—parent components must handle persistence.
 * 
 * @param user - The user object containing id, name, email, and avatar
 * @param editable - Whether the user information can be edited (default: false)
 * @param onUserChange - Callback fired when user edits any field
 * @param showLastSeen - Display when the user was last active (default: true)
 * @returns React component element
 * 
 * @example
 * ```typescript
 * // Read-only card
 * <UserProfileCard user={userData} />
 * 
 * // Editable with change handler
 * <UserProfileCard
 *   user={userData}
 *   editable={true}
 *   onUserChange={(updatedUser) => saveUser(updatedUser)}
 * />
 * ```
 */
export function UserProfileCard({
    user,
    editable = false,
    onUserChange,
    showLastSeen = true
}: UserProfileCardProps): JSX.Element {
    // Implementation
}
```

### Async Function with Complex Behavior

When async functions have non-obvious timing characteristics, document them explicitly:

```typescript
/**
 * Processes a payment transaction with automatic retry and exponential backoff.
 * 
 * IMPORTANT: This method implements exponential backoff for failed transactions.
 * It will attempt up to 3 retries with delays of 1s, 2s, and 4s respectively.
 * The entire process may take up to 7 seconds to complete in worst-case scenarios.
 * 
 * Do not assume the function completes instantly—callers must be prepared to wait.
 * Consider implementing their own timeout if 7 seconds is unacceptable.
 * 
 * @param payment - The payment details to process
 * @param payment.amount - Transaction amount in cents (e.g., 2999 for $29.99)
 * @param payment.currency - ISO 4217 currency code (e.g., 'USD')
 * @param payment.cardToken - Tokenized card from the payment provider
 * @returns Transaction ID if successful, unique per payment attempt
 * @throws {PaymentDeclinedError} After all retry attempts fail
 * @throws {InvalidPaymentError} When payment details are malformed
 * 
 * @example
 * ```typescript
 * try {
 *   const txId = await processPayment({
 *     amount: 2999,
 *     currency: 'USD',
 *     cardToken: 'tok_visa'
 *   });
 *   console.log('Payment successful:', txId);
 * } catch (error) {
 *   if (error instanceof PaymentDeclinedError) {
 *     console.log('Card was declined');
 *   }
 * }
 * ```
 */
async function processPayment(payment: PaymentRequest): Promise<string> {
    // Complex retry logic here
}
```

## Advanced Tags

### Using @template for Generics

Template tags help document type parameters in generic functions:

```typescript
/**
 * Creates a new array with duplicates removed, preserving original order.
 * 
 * Uses identity comparison (===) to determine uniqueness. For objects,
 * pass a custom `getId` function to define what makes two items unique.
 * 
 * @template T - The type of items in the array
 * @param items - Array that may contain duplicates
 * @param getId - Optional function to extract unique identifier for each item
 * @returns New array with duplicates removed
 * 
 * @example
 * ```typescript
 * unique([1, 2, 2, 3, 1]) // [1, 2, 3]
 * unique(users, u => u.id) // removes users with duplicate IDs
 * ```
 */
function unique<T>(items: T[], getId?: (item: T) => unknown): T[] {
    // Implementation
}
```

### Using @deprecated

Mark functions that are being phased out with clear migration guidance:

```typescript
/**
 * @deprecated This function performs slowly for large arrays.
 * Use {@link efficientSort} instead, which is 10x faster.
 * Migration: Replace calls to `legacySort(arr)` with `efficientSort(arr)`.
 * This function will be removed in version 3.0.
 */
function legacySort(array: number[]): number[] {
    // Old implementation
}
```

### Using @see for Related Functions

Cross-reference related functionality:

```typescript
/**
 * Fetches data from the API with caching.
 * 
 * @param url - The endpoint to fetch from
 * @returns Cached response data
 * @see fetchWithRetry - For requests that may timeout
 * @see fetchBatch - For fetching multiple endpoints efficiently
 */
async function fetch(url: string): Promise<unknown> {
    // Implementation
}
```

## Anti-Patterns

### Redundant Documentation

Don't repeat information the type system already provides:

```typescript
// ❌ AVOID - Type information is redundant
/**
 * @param name - A string representing the user's name
 * @param age - A number representing the user's age
 * @returns A string with the formatted message
 */
function formatUserInfo(name: string, age: number): string {
    return `${name} (${age} years old)`;
}

// ✅ GOOD - Focus on intent and usage
/**
 * Formats user information for display in the UI
 * @example
 * formatUserInfo('Alice', 30) // "Alice (30 years old)"
 */
function formatUserInfo(name: string, age: number): string {
    return `${name} (${age} years old)`;
}
```

### Over-Documentation of Obvious Code

Don't document implementation details that are immediately apparent:

```typescript
// ❌ AVOID - Obvious from code alone
/**
 * Increments the counter by 1
 * @param counter - The counter to increment
 * @returns The incremented counter
 */
function incrementCounter(counter: number): number {
    return counter + 1;
}

// ✅ GOOD - Skip it if it's self-evident
function incrementCounter(counter: number): number {
    return counter + 1;
}
```

### Outdated Documentation

Don't include implementation-dependent documentation that becomes false as code changes:

```typescript
// ❌ AVOID - Implementation detail that might change
/**
 * Fetches users from the database via SQL query and caches results
 * in memory for 5 minutes before refreshing
 */
async function getUsers(): Promise<User[]> {
    // Implementation might change—could switch to Redis, different TTL, etc.
}

// ✅ GOOD - Document the contract, not the implementation
/**
 * Fetches the current list of all users, with results cached for performance
 * @returns Promise resolving to array of all users
 */
async function getUsers(): Promise<User[]> {
    // Implementation is free to change
}
```

### Unnecessarily Complex Parameter Documentation

Keep parameter documentation proportional to complexity:

```typescript
// ❌ AVOID - Over-documented for simple parameters
/**
 * @param x - A parameter of type number that represents a numeric value
 * @param y - Another parameter of type number that also represents a numeric value
 * @returns A result of type number representing the sum
 */
function add(x: number, y: number): number {
    return x + y;
}

// ✅ GOOD - Brief or skip if self-evident
/**
 * Adds two numbers together
 */
function add(x: number, y: number): number {
    return x + y;
}
```

## Documentation Timing

### When to Write Documentation First

Document public APIs before implementation when the API contract is critical and stable. This helps validate the interface design with others and serves as a specification.

### When to Write Documentation After

Internal helper functions can be documented after implementation once their purpose and behavior are clear. This avoids writing documentation that becomes immediately outdated.

### When to Update Documentation

Update documentation when changing behavior, when new side effects are introduced, when performance characteristics change significantly, or when error conditions are added. Before refactoring, use documentation as a test—if the documented contract still holds, the refactoring is safe.