# Swift Architecture Patterns

## Table of Contents
1. [Observable (iOS 17+)](#observable-ios-17)
2. [ObservableObject (iOS 13+)](#observableobject-ios-13)
3. [MVVM Pattern](#mvvm-pattern)
4. [Navigation Patterns](#navigation-patterns)
5. [Network Service](#network-service)
6. [Keychain Manager](#keychain-manager)
7. [Core Data](#core-data)
8. [SwiftData (iOS 17+)](#swiftdata-ios-17)
9. [Combine Integration](#combine-integration)
10. [Project Structure](#project-structure)

---

## Observable (iOS 17+)

```swift
import SwiftUI

@Observable
class CounterViewModel {
    var count = 0

    func increment() {
        count += 1
    }
}

struct CounterView: View {
    @State private var viewModel = CounterViewModel()

    var body: some View {
        VStack {
            Text("Count: \(viewModel.count)")
            Button("Increment") {
                viewModel.increment()
            }
        }
    }
}
```

---

## ObservableObject (iOS 13+)

```swift
class CounterViewModel: ObservableObject {
    @Published var count = 0

    func increment() {
        count += 1
    }
}

struct CounterView: View {
    @StateObject private var viewModel = CounterViewModel()

    var body: some View {
        VStack {
            Text("Count: \(viewModel.count)")
            Button("Increment") {
                viewModel.increment()
            }
        }
    }
}
```

**Property Wrapper Rules:**
- `@StateObject` - Own the view model (create it)
- `@ObservedObject` - Receive from parent (don't own)
- `@EnvironmentObject` - App-wide shared state

---

## MVVM Pattern

### Model
```swift
struct User: Codable, Identifiable {
    let id: UUID
    var name: String
    var email: String
}
```

### ViewModel
```swift
@MainActor
class UserViewModel: ObservableObject {
    @Published var user: User?
    @Published var isLoading = false
    @Published var errorMessage: String?

    private let networkService: NetworkService

    init(networkService: NetworkService = .shared) {
        self.networkService = networkService
    }

    func fetchUser(id: UUID) async {
        isLoading = true
        errorMessage = nil

        do {
            user = try await networkService.fetch(User.self, from: "/users/\(id)")
        } catch {
            errorMessage = error.localizedDescription
        }

        isLoading = false
    }
}
```

### View
```swift
struct UserView: View {
    @StateObject private var viewModel = UserViewModel()

    var body: some View {
        Group {
            if viewModel.isLoading {
                ProgressView()
            } else if let user = viewModel.user {
                Text(user.name)
            } else if let error = viewModel.errorMessage {
                Text(error).foregroundStyle(.red)
            }
        }
        .task {
            await viewModel.fetchUser(id: UUID())
        }
    }
}
```

---

## Navigation Patterns

### NavigationStack (iOS 16+)

```swift
import SwiftUI

// Type-safe navigation with enum
enum AppRoute: Hashable {
    case itemDetail(Int)
    case settings
    case profile(User)
}

struct AppView: View {
    @State private var navigationPath = NavigationPath()

    var body: some View {
        NavigationStack(path: $navigationPath) {
            HomeView(path: $navigationPath)
                .navigationDestination(for: AppRoute.self) { route in
                    switch route {
                    case .itemDetail(let id):
                        ItemDetailView(id: id)
                    case .settings:
                        SettingsView()
                    case .profile(let user):
                        ProfileView(user: user)
                    }
                }
        }
    }
}

// Programmatic navigation
struct HomeView: View {
    @Binding var path: NavigationPath
    
    var body: some View {
        List {
            Button("Go to Settings") {
                path.append(AppRoute.settings)
            }
            Button("Go to Item 42") {
                path.append(AppRoute.itemDetail(42))
            }
        }
    }
}

// Deep linking
extension AppView {
    func handleDeepLink(_ url: URL) {
        // Parse URL and navigate
        if url.pathComponents.contains("settings") {
            navigationPath.append(AppRoute.settings)
        }
    }
}
```

### Coordinator Pattern

```swift
@MainActor
class NavigationCoordinator: ObservableObject {
    @Published var path = NavigationPath()
    
    func navigate(to route: AppRoute) {
        path.append(route)
    }
    
    func pop() {
        if !path.isEmpty {
            path.removeLast()
        }
    }
    
    func popToRoot() {
        path.removeLast(path.count)
    }
}

// Usage in ViewModel
@Observable
class HomeViewModel {
    private let coordinator: NavigationCoordinator
    
    init(coordinator: NavigationCoordinator) {
        self.coordinator = coordinator
    }
    
    func showDetail(for item: Item) {
        coordinator.navigate(to: .itemDetail(item.id))
    }
}
```

### NavigationView (iOS 13-15)

```swift
struct ContentView: View {
    var body: some View {
        NavigationView {
            List {
                NavigationLink(destination: DetailView()) {
                    Text("Item 1")
                }
            }
            .navigationTitle("Items")
        }
    }
}
```

---

## Network Service

```swift
class NetworkService {
    static let shared = NetworkService()

    private let session: URLSession
    private let baseURL: URL

    init(session: URLSession = .shared, baseURL: URL = URL(string: "https://api.example.com")!) {
        self.session = session
        self.baseURL = baseURL
    }

    func fetch<T: Decodable>(_ type: T.Type, from endpoint: String) async throws -> T {
        let url = baseURL.appendingPathComponent(endpoint)
        var request = URLRequest(url: url)
        request.addAuthHeader()

        let (data, response) = try await session.data(for: request)
        try validateResponse(response)

        let decoder = JSONDecoder()
        decoder.dateDecodingStrategy = .iso8601
        return try decoder.decode(T.self, from: data)
    }

    func post<T: Decodable, Body: Encodable>(_ type: T.Type, to endpoint: String, body: Body) async throws -> T {
        let url = baseURL.appendingPathComponent(endpoint)
        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        request.addAuthHeader()
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        request.httpBody = try JSONEncoder().encode(body)

        let (data, response) = try await session.data(for: request)
        try validateResponse(response)
        return try JSONDecoder().decode(T.self, from: data)
    }

    private func validateResponse(_ response: URLResponse) throws {
        guard let http = response as? HTTPURLResponse else {
            throw NetworkError.invalidResponse
        }

        switch http.statusCode {
        case 200...299: return
        case 401: throw NetworkError.unauthorized
        case 404: throw NetworkError.notFound
        case 500...599: throw NetworkError.serverError
        default: throw NetworkError.unknown(http.statusCode)
        }
    }
}

enum NetworkError: LocalizedError {
    case invalidResponse, unauthorized, notFound, serverError, unknown(Int)

    var errorDescription: String? {
        switch self {
        case .invalidResponse: "Invalid response"
        case .unauthorized: "Unauthorized"
        case .notFound: "Not found"
        case .serverError: "Server error"
        case .unknown(let code): "HTTP \(code)"
        }
    }
}

extension URLRequest {
    mutating func addAuthHeader() {
        if let token = KeychainManager.shared.getToken() {
            setValue("Bearer \(token)", forHTTPHeaderField: "Authorization")
        }
    }
}
```

---

## Keychain Manager

```swift
import Security

class KeychainManager {
    static let shared = KeychainManager()
    private let service = Bundle.main.bundleIdentifier ?? "com.app"

    func saveToken(_ token: String) -> Bool {
        guard let data = token.data(using: .utf8) else { return false }

        let query: [String: Any] = [
            kSecClass as String: kSecClassGenericPassword,
            kSecAttrService as String: service,
            kSecAttrAccount as String: "authToken",
            kSecValueData as String: data
        ]

        SecItemDelete(query as CFDictionary)
        return SecItemAdd(query as CFDictionary, nil) == errSecSuccess
    }

    func getToken() -> String? {
        let query: [String: Any] = [
            kSecClass as String: kSecClassGenericPassword,
            kSecAttrService as String: service,
            kSecAttrAccount as String: "authToken",
            kSecReturnData as String: true,
            kSecMatchLimit as String: kSecMatchLimitOne
        ]

        var result: AnyObject?
        guard SecItemCopyMatching(query as CFDictionary, &result) == errSecSuccess,
              let data = result as? Data else { return nil }
        return String(data: data, encoding: .utf8)
    }

    func deleteToken() {
        let query: [String: Any] = [
            kSecClass as String: kSecClassGenericPassword,
            kSecAttrService as String: service,
            kSecAttrAccount as String: "authToken"
        ]
        SecItemDelete(query as CFDictionary)
    }
}
```

---

## Core Data

```swift
import CoreData

class PersistenceController {
    static let shared = PersistenceController()

    let container: NSPersistentContainer

    var viewContext: NSManagedObjectContext { container.viewContext }

    init(inMemory: Bool = false) {
        container = NSPersistentContainer(name: "Model")

        if inMemory {
            container.persistentStoreDescriptions.first?.url = URL(fileURLWithPath: "/dev/null")
        }

        container.loadPersistentStores { _, error in
            if let error { fatalError("Core Data error: \(error)") }
        }

        container.viewContext.automaticallyMergesChangesFromParent = true
        container.viewContext.mergePolicy = NSMergeByPropertyObjectTrumpMergePolicy
    }

    func save() {
        guard viewContext.hasChanges else { return }
        try? viewContext.save()
    }
}

// SwiftUI Usage
struct ListView: View {
    @Environment(\.managedObjectContext) private var viewContext

    @FetchRequest(sortDescriptors: [NSSortDescriptor(keyPath: \Item.timestamp, ascending: false)])
    private var items: FetchedResults<Item>

    var body: some View {
        List(items) { item in
            Text(item.name ?? "")
        }
    }
}
```

---

## SwiftData (iOS 17+)

```swift
import SwiftData

@Model
class Item {
    var name: String
    var timestamp: Date

    init(name: String, timestamp: Date = .now) {
        self.name = name
        self.timestamp = timestamp
    }
}

// App setup
@main
struct MyApp: App {
    var body: some Scene {
        WindowGroup {
            ContentView()
        }
        .modelContainer(for: Item.self)
    }
}

// View usage
struct ListView: View {
    @Environment(\.modelContext) private var modelContext
    @Query(sort: \Item.timestamp, order: .reverse) private var items: [Item]

    var body: some View {
        List(items) { item in
            Text(item.name)
        }
    }

    func addItem() {
        let item = Item(name: "New")
        modelContext.insert(item)
    }
}
```

---

## Combine Integration

```swift
import Combine

class SearchViewModel: ObservableObject {
    @Published var searchText = ""
    @Published var results: [SearchResult] = []
    @Published var isSearching = false

    private var cancellables = Set<AnyCancellable>()

    init() {
        $searchText
            .debounce(for: .milliseconds(300), scheduler: RunLoop.main)
            .removeDuplicates()
            .filter { !$0.isEmpty }
            .handleEvents(receiveOutput: { [weak self] _ in
                self?.isSearching = true
            })
            .flatMap { query in
                SearchService.shared.search(query: query)
                    .catch { _ in Just([]) }
            }
            .receive(on: DispatchQueue.main)
            .sink { [weak self] results in
                self?.results = results
                self?.isSearching = false
            }
            .store(in: &cancellables)
    }
}
```

---

## Project Structure

### Swift Package

```
MyPackage/
├── Package.swift
├── Sources/MyPackage/
│   ├── Models/
│   ├── Services/
│   └── Utilities/
└── Tests/MyPackageTests/
```

### iOS App

```
MyApp/
├── MyApp.xcodeproj/
├── MyApp/
│   ├── App/
│   │   └── MyAppApp.swift
│   ├── Features/
│   │   ├── Home/
│   │   └── Settings/
│   ├── Core/
│   │   ├── Models/
│   │   └── Services/
│   └── Resources/
├── MyAppTests/
└── MyAppUITests/
```
