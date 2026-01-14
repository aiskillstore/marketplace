# Swift 6 Concurrency Patterns

## Enabling Swift 6 Mode

### Package.swift
```swift
// swift-tools-version: 6.0
let package = Package(name: "MyPackage", ...)
```

### Xcode Build Settings
```
SWIFT_VERSION = 6.0
SWIFT_STRICT_CONCURRENCY = complete
```

## Sendable Protocol

### Value Types (implicitly Sendable)
```swift
struct User: Sendable {
    let id: UUID
    let name: String
}
```

### Classes (must be final with immutable properties)
```swift
final class Configuration: Sendable {
    let apiKey: String
    let timeout: TimeInterval

    init(apiKey: String, timeout: TimeInterval) {
        self.apiKey = apiKey
        self.timeout = timeout
    }
}
```

### @unchecked Sendable (manual thread safety)
```swift
final class Cache: @unchecked Sendable {
    private let lock = NSLock()
    private var storage: [String: Data] = [:]

    func get(_ key: String) -> Data? {
        lock.lock()
        defer { lock.unlock() }
        return storage[key]
    }

    func set(_ key: String, _ value: Data) {
        lock.lock()
        defer { lock.unlock() }
        storage[key] = value
    }
}
```

## Actors

```swift
actor DataStore {
    private var items: [Item] = []

    func add(_ item: Item) {
        items.append(item)
    }

    func getAll() -> [Item] {
        items
    }

    // nonisolated for synchronous access to immutable data
    nonisolated var storeIdentifier: String {
        "main-store"
    }
}

// Usage
let store = DataStore()
await store.add(newItem)
let items = await store.getAll()
```

## @MainActor

### Class-level
```swift
@MainActor
class ViewModel: ObservableObject {
    @Published var items: [Item] = []

    func loadItems() async {
        let fetched = await dataService.fetchItems()
        items = fetched  // Safe - runs on main actor
    }
}
```

### Method-level
```swift
class Service {
    @MainActor
    func updateUI() {
        // Guaranteed main thread
    }
}
```

## async/await

### Basic
```swift
func fetchUser(id: String) async throws -> User {
    let url = URL(string: "https://api.example.com/users/\(id)")!
    let (data, _) = try await URLSession.shared.data(from: url)
    return try JSONDecoder().decode(User.self, from: data)
}
```

### Concurrent with async let
```swift
func fetchDashboard() async throws -> Dashboard {
    async let user = fetchUser(id: currentUserId)
    async let posts = fetchPosts()
    async let notifications = fetchNotifications()

    return try await Dashboard(
        user: user,
        posts: posts,
        notifications: notifications
    )
}
```

### Task Groups
```swift
func processItems(_ items: [Item]) async throws -> [Result] {
    try await withThrowingTaskGroup(of: Result.self) { group in
        for item in items {
            group.addTask {
                try await process(item)
            }
        }

        var results: [Result] = []
        for try await result in group {
            results.append(result)
        }
        return results
    }
}
```

## Swift 6.2 Features

### @concurrent
```swift
// Explicitly runs on global executor (off caller's actor)
@concurrent
func heavyComputation() async -> Result {
    // Background execution
}
```

### Default Behavior Change
In Swift 6.2, `nonisolated async` functions run on caller's actor by default. Use `@concurrent` when background execution is needed.

## Common Patterns

### Converting completion handlers
```swift
// Before
func fetchData(completion: @escaping (Result<Data, Error>) -> Void)

// After
func fetchData() async throws -> Data {
    try await withCheckedThrowingContinuation { continuation in
        fetchData { result in
            continuation.resume(with: result)
        }
    }
}
```

### Cancellation
```swift
func downloadFile() async throws -> Data {
    try Task.checkCancellation()  // Throws if cancelled

    // Or check without throwing
    if Task.isCancelled {
        return Data()
    }

    return try await performDownload()
}
```

### Task Priority
```swift
Task(priority: .high) {
    await importantWork()
}

Task.detached(priority: .background) {
    await lowPriorityWork()
}
```
