# Swift Package Manager Reference

## Creating Packages

```bash
# Library package
swift package init --type library --name MyLibrary

# Executable package
swift package init --type executable --name MyTool

# Empty package
swift package init --type empty
```

## Package.swift Structure

```swift
// swift-tools-version: 5.10
import PackageDescription

let package = Package(
    name: "MyPackage",
    platforms: [
        .iOS(.v15),
        .macOS(.v13)
    ],
    products: [
        .library(name: "MyLibrary", targets: ["MyLibrary"]),
        .executable(name: "MyTool", targets: ["MyTool"])
    ],
    dependencies: [
        .package(url: "https://github.com/example/dependency.git", from: "1.0.0"),
        .package(url: "https://github.com/example/other.git", branch: "main"),
        .package(path: "../LocalPackage")
    ],
    targets: [
        .target(
            name: "MyLibrary",
            dependencies: ["dependency"],
            resources: [.process("Resources/")]
        ),
        .executableTarget(
            name: "MyTool",
            dependencies: ["MyLibrary"]
        ),
        .testTarget(
            name: "MyLibraryTests",
            dependencies: ["MyLibrary"]
        )
    ]
)
```

## Swift 6 Package.swift

```swift
// swift-tools-version: 6.0
import PackageDescription

let package = Package(
    name: "MyPackage",
    platforms: [.iOS(.v17), .macOS(.v14)],
    products: [
        .library(name: "MyLibrary", targets: ["MyLibrary"])
    ],
    targets: [
        .target(name: "MyLibrary")
        // Swift 6 has strict concurrency by default - no swiftSettings needed
    ]
)
```

## Build Commands

| Command | Description |
|---------|-------------|
| `swift build` | Debug build |
| `swift build -c release` | Release build |
| `swift build --target MyLib` | Build specific target |
| `swift build -v` | Verbose output |
| `swift build --show-bin-path` | Show output directory |

## Dependency Management

```bash
# Update all dependencies
swift package update

# Resolve without updating
swift package resolve

# Show dependency graph
swift package show-dependencies
swift package show-dependencies --format json

# Clean build artifacts
swift package clean
rm -rf .build
```

## Testing with SPM

```bash
# Run all tests
swift test

# Verbose output
swift test -v

# Run specific test
swift test --filter MyLibraryTests.MyTestCase

# Run tests in parallel
swift test --parallel

# Generate code coverage
swift test --enable-code-coverage
```

## iOS Builds with SPM

SPM packages for iOS require xcodebuild:

```bash
# Build for iOS Simulator
xcodebuild -scheme MyScheme \
    -destination 'platform=iOS Simulator,name=iPhone 15' \
    build

# Build for iOS device
xcodebuild -scheme MyScheme \
    -destination 'generic/platform=iOS' \
    build
```
