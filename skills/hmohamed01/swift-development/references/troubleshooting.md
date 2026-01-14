# Swift Development Troubleshooting

## Build Issues

### "No signing certificate" error

```bash
# Check available certificates
security find-identity -v -p codesigning

# Clear derived data
rm -rf ~/Library/Developer/Xcode/DerivedData

# Reset package caches
rm -rf ~/Library/Caches/org.swift.swiftpm
```

### "Module not found" error

```bash
# Clean and rebuild (SPM)
swift package clean
swift build

# For Xcode projects
xcodebuild clean -workspace MyApp.xcworkspace -scheme MyApp
xcodebuild -resolvePackageDependencies -workspace MyApp.xcworkspace -scheme MyApp
```

### Package resolution fails

```bash
# Reset package cache
rm -rf ~/Library/Caches/org.swift.swiftpm
rm -rf .build

# Force re-resolve
swift package reset
swift package resolve
```

### "Command CodeSign failed"

```bash
# Verify certificate is valid
security find-identity -v -p codesigning

# Check certificate expiration
security find-certificate -c "Apple Development" -p | openssl x509 -noout -dates

# Re-download certificates in Xcode
# Xcode > Preferences > Accounts > Manage Certificates
```

## Simulator Issues

### Simulator not booting

```bash
# Reset all simulators
xcrun simctl erase all

# Restart CoreSimulator service
sudo killall -9 com.apple.CoreSimulator.CoreSimulatorService

# Clear simulator caches
rm -rf ~/Library/Developer/CoreSimulator/Caches
```

### "Unable to boot device in current state"

```bash
# Shutdown all simulators first
xcrun simctl shutdown all

# Then boot desired device
xcrun simctl boot "iPhone 15"
```

### App not installing

```bash
# Verify app is built for correct architecture
file MyApp.app/MyApp

# Check simulator compatibility
xcrun simctl list devicetypes

# Reinstall after uninstall
xcrun simctl uninstall booted com.mycompany.myapp
xcrun simctl install booted ./MyApp.app
```

## Xcode Issues

### Xcode indexing stuck

```bash
# Kill Xcode and clear index
killall Xcode
rm -rf ~/Library/Developer/Xcode/DerivedData/*/Index
```

### Package dependencies not updating

```bash
# Clear package cache
rm -rf ~/Library/Caches/org.swift.swiftpm
rm -rf ~/Library/Developer/Xcode/DerivedData/*/SourcePackages

# Re-resolve in Xcode
# File > Packages > Reset Package Caches
```

### Build settings not applying

```bash
# Clear derived data
rm -rf ~/Library/Developer/Xcode/DerivedData

# Rebuild
xcodebuild clean build -workspace MyApp.xcworkspace -scheme MyApp
```

## Swift Concurrency Issues

### "Sendable" warnings

```swift
// For value types, ensure all properties are Sendable
struct MyData: Sendable {
    let id: UUID          // UUID is Sendable
    let name: String      // String is Sendable
}

// For classes, make them final with immutable properties
final class Config: Sendable {
    let value: String
    init(value: String) { self.value = value }
}

// For thread-safe mutable state, use @unchecked Sendable
final class Cache: @unchecked Sendable {
    private let lock = NSLock()
    private var data: [String: Any] = [:]
}
```

### "Main actor-isolated" errors

```swift
// Mark UI-related classes with @MainActor
@MainActor
class ViewModel: ObservableObject {
    @Published var data: [Item] = []
}

// Or mark specific methods
class Service {
    @MainActor
    func updateUI() { }
}
```

### Task cancellation not working

```swift
// Check cancellation explicitly
func fetchData() async throws -> Data {
    try Task.checkCancellation()  // Throws if cancelled

    // Or check without throwing
    guard !Task.isCancelled else {
        return Data()
    }

    return try await download()
}
```

## Performance Issues

### App launch slow

```bash
# Profile with Instruments
xcrun xctrace record --template 'App Launch' --launch MyApp.app

# Check for main thread blocking
# Instruments > Time Profiler
```

### Memory issues

```bash
# Check for leaks
xcrun xctrace record --template 'Leaks' --attach MyApp.app

# Memory graph in Xcode
# Debug > Debug Memory Graph
```

## Common Error Messages

| Error | Solution |
|-------|----------|
| "No provisioning profile" | Add signing capability in Xcode |
| "Code signing is required" | Set CODE_SIGN_IDENTITY in build settings |
| "Embedded binary not signed" | Sign frameworks in "Embed Frameworks" phase |
| "Duplicate symbols" | Check for duplicate file imports |
| "Cannot find type 'X'" | Ensure module is imported, check target membership |
| "Expression too complex" | Break complex expressions into parts |
| "Circular reference" | Restructure dependencies |

## Quick Fixes

### Reset everything

```bash
# Nuclear option - reset all Xcode state
rm -rf ~/Library/Developer/Xcode/DerivedData
rm -rf ~/Library/Caches/org.swift.swiftpm
rm -rf ~/Library/Developer/CoreSimulator/Caches
xcrun simctl erase all
```

### Verify tool versions

```bash
xcode-select -p
xcodebuild -version
swift --version
xcrun simctl list runtimes
```
