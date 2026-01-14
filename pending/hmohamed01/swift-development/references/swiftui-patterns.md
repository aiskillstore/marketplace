# SwiftUI Patterns

Quick reference for common SwiftUI patterns and architectures.

## Observable ViewModel (iOS 17+)

```swift
import SwiftUI

@Observable
class ItemsViewModel {
    var items: [Item] = []
    var isLoading = false
    var error: String?

    func load() async {
        isLoading = true
        defer { isLoading = false }

        do {
            items = try await api.fetchItems()
        } catch {
            self.error = error.localizedDescription
        }
    }
}

struct ItemsView: View {
    @State private var viewModel = ItemsViewModel()

    var body: some View {
        List(viewModel.items) { item in
            Text(item.name)
        }
        .overlay { if viewModel.isLoading { ProgressView() } }
        .task { await viewModel.load() }
    }
}
```

## ObservableObject (iOS 13+)

```swift
class ViewModel: ObservableObject {
    @Published var data: [Item] = []
}

struct MyView: View {
    @StateObject private var viewModel = ViewModel()  // Own it
    // or
    @ObservedObject var viewModel: ViewModel          // Passed in
}
```

## Navigation (iOS 16+)

```swift
// NavigationStack with programmatic navigation
struct ContentView: View {
    @State private var path = NavigationPath()

    var body: some View {
        NavigationStack(path: $path) {
            List {
                NavigationLink("Item 1", value: 1)
                NavigationLink("Item 2", value: 2)
            }
            .navigationDestination(for: Int.self) { id in
                DetailView(id: id)
            }
        }
    }
}

// Navigation with typed paths
enum Route: Hashable {
    case detail(Int)
    case settings
}

struct AppView: View {
    @State private var path = NavigationPath()

    var body: some View {
        NavigationStack(path: $path) {
            HomeView()
                .navigationDestination(for: Route.self) { route in
                    switch route {
                    case .detail(let id):
                        DetailView(id: id)
                    case .settings:
                        SettingsView()
                    }
                }
        }
    }
}

// Programmatic navigation
Button("Go to Detail") {
    path.append(Route.detail(42))
}
```

## Navigation (iOS 13-15)

```swift
// NavigationView with NavigationLink
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
