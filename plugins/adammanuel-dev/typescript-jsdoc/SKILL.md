---
name: typescript-jsdoc
description: Write effective JSDoc comments for TypeScript code. Provides guidance on documentation format, strategic placement, best practices, and when to document versus when to keep code self-documenting. Helps maintain code clarity and IDE support.
---

# TypeScript JSDoc Documentation

Write effective JSDoc comments that enhance code maintainability and provide valuable context to developers and IDEs.

## Core Format

JSDoc comments begin with `/**` and end with `*/`, with lines inside typically starting with an asterisk. Tags start with `@` followed by a keyword. Essential tags include `@param`, `@returns`, `@throws`, `@example`, and `@deprecated`.

Since TypeScript code already contains type information, JSDoc should focus on the "why" and "how" rather than repeating types:

```typescript
/**
 * Calculates the total price including tax
 * @param basePrice - The price before tax
 * @param taxRate - The tax rate as a decimal (0.08 for 8%)
 * @returns The total price after applying tax
 */
function calculateTotal(basePrice: number, taxRate: number): number {
    return basePrice * (1 + taxRate);
}
```

## Strategic Documentation Levels

Treat JSDoc usage as having three distinct levels, each serving different purposes:

**Essential Documentation** appears on all public APIs, exported functions, classes, and interfaces. This is non-negotiable for library code or shared modules. Document what the entity does, important behaviors, potential errors, and provide a usage example when the interface isn't immediately obvious.

**Clarifying Documentation** becomes valuable when code has non-obvious behavior, implements complex algorithms, or has important side effects. Explain critical behaviors that aren't apparent from the signature, warn about unusual performance characteristics, or document retry logic, caching behavior, or state management. This documentation adds genuine value beyond the type system.

**Minimal Documentation** applies to internal helper functions, private methods, and straightforward utility functions where the code is genuinely self-documenting. Even here, a brief one-liner explaining intent helps future developers quickly understand purpose. Skip documentation only when the function name and implementation are immediately transparent.

## Documentation Structure for Complex APIs

For classes and services, document the class at a high level, then provide detailed documentation on public methods:

```typescript
/**
 * Manages user authentication and session handling.
 * 
 * This service maintains a singleton instance that handles all
 * authentication flows including login, logout, and token refresh.
 * It automatically manages token expiration and renewal.
 */
export class AuthenticationService {
    /**
     * Attempts to authenticate a user with provided credentials
     * @param credentials - User login information
     * @throws {AuthenticationError} When credentials are invalid
     * @throws {NetworkError} When the authentication server is unreachable
     * @example
     * ```typescript
     * const auth = new AuthenticationService();
     * try {
     *   const session = await auth.login({ 
     *     username: 'user@example.com',
     *     password: 'securepass' 
     *   });
     * } catch (error) {
     *   console.error('Login failed:', error.message);
     * }
     * ```
     */
    async login(credentials: LoginCredentials): Promise<Session> {
        // Implementation details
    }
}
```

## Advanced Patterns

For **generic functions**, JSDoc shines in providing context that type signatures alone cannot convey. Use `@template` tags to explain type parameters and document how they interact:

```typescript
/**
 * Transforms an array of items using a mapping function with memoization.
 * 
 * This function caches results based on item identity, making it efficient
 * for repeated transformations of the same data. The cache is cleared
 * when the array reference changes.
 * 
 * @template T - The type of items in the input array
 * @template R - The type of items in the output array
 * @param items - Source array to transform
 * @param mapper - Function to transform each item
 * @param keyExtractor - Optional function to generate cache keys
 * @returns Transformed array with results potentially served from cache
 */
function memoizedMap<T, R>(
    items: T[],
    mapper: (item: T) => R,
    keyExtractor?: (item: T) => string
): R[] {
    // Implementation with caching logic
}
```

For **complex object parameters**, use nested parameter documentation to keep organization clear:

```typescript
/**
 * Configures the application database connection
 * @param config - Database configuration options
 * @param config.host - Database server hostname
 * @param config.port - Port number (defaults to 5432)
 * @param config.ssl - SSL connection settings
 * @param config.ssl.required - Whether SSL is mandatory
 * @param config.ssl.certificatePath - Path to SSL certificate file
 * @param config.poolSize - Maximum connection pool size (1-100)
 */
function configureDatabase(config: DatabaseConfig): void {
    // Configuration logic
}
```

## When Documentation Becomes Redundant

Understanding when JSDoc becomes redundant is equally important. Avoid documenting when TypeScript's type system already tells the complete story and the function name is genuinely self-explanatory. A utility like `function isEven(n: number): boolean` probably doesn't need JSDoc unless it has unexpected edge cases.

Similarly, avoid documenting implementation details that might change. Focus on the contract—what the function promises to do, not how it currently does it. This keeps documentation stable even as implementation evolves.

## The Golden Rule

Write JSDoc when it adds meaningful information that helps developers use or maintain your code correctly. Good documentation explains intentions, warns about gotchas, provides context for decisions, and illustrates usage patterns. It should feel like having an experienced colleague explaining the important parts of the code, not like reading a redundant transcript of what's already visible in the type signatures.

See [references/patterns.md](references/patterns.md) for detailed examples of common patterns and anti-patterns.