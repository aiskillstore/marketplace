# Swift Development Best Practices

Essential guidelines for building robust, maintainable Swift applications.

## DO

- Use SwiftUI + Observable/ObservableObject for UI
- Use async/await for all async operations
- Store secrets in Keychain, not UserDefaults
- Use `@MainActor` for UI-related code
- Test on real devices before release
- Enable strict concurrency checking

## DON'T

- Force unwrap without safety checks
- Block main thread with sync operations
- Store API keys in source code
- Ignore Swift 6 concurrency warnings
- Skip error handling
