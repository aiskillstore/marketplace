# CI/CD for Swift Projects

## GitHub Actions

### Basic Build and Test

```yaml
name: Build and Test

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  build:
    runs-on: macos-14

    steps:
      - uses: actions/checkout@v4

      - name: Select Xcode
        run: sudo xcode-select -s /Applications/Xcode_15.4.app

      - name: Show versions
        run: |
          xcodebuild -version
          swift --version

      - name: Resolve packages
        run: |
          xcodebuild -resolvePackageDependencies \
            -workspace MyApp.xcworkspace \
            -scheme MyApp

      - name: Build
        run: |
          xcodebuild build \
            -workspace MyApp.xcworkspace \
            -scheme MyApp \
            -destination 'platform=iOS Simulator,name=iPhone 15' \
            | xcpretty

      - name: Test
        run: |
          xcodebuild test \
            -workspace MyApp.xcworkspace \
            -scheme MyApp \
            -destination 'platform=iOS Simulator,name=iPhone 15' \
            -resultBundlePath TestResults.xcresult \
            | xcpretty

      - name: Upload test results
        uses: actions/upload-artifact@v4
        if: failure()
        with:
          name: test-results
          path: TestResults.xcresult
```

### Swift Package Only

```yaml
name: Swift Package CI

on: [push, pull_request]

jobs:
  test:
    runs-on: macos-14

    steps:
      - uses: actions/checkout@v4

      - name: Build
        run: swift build -v

      - name: Test
        run: swift test -v
```

### Matrix Build (Multiple Xcode Versions)

```yaml
jobs:
  build:
    runs-on: macos-14
    strategy:
      matrix:
        xcode: ['15.2', '15.4', '16.0']

    steps:
      - uses: actions/checkout@v4

      - name: Select Xcode ${{ matrix.xcode }}
        run: sudo xcode-select -s /Applications/Xcode_${{ matrix.xcode }}.app

      - name: Build and Test
        run: swift test
```

## Build Scripts

### Generic Build Script

```bash
#!/bin/bash
set -e

WORKSPACE="MyApp.xcworkspace"
SCHEME="MyApp"
CONFIGURATION="Release"
ARCHIVE_PATH="./build/MyApp.xcarchive"
EXPORT_PATH="./build/export"

echo "Cleaning..."
xcodebuild clean -workspace "$WORKSPACE" -scheme "$SCHEME"

echo "Archiving..."
xcodebuild archive \
    -workspace "$WORKSPACE" \
    -scheme "$SCHEME" \
    -configuration "$CONFIGURATION" \
    -archivePath "$ARCHIVE_PATH" \
    -allowProvisioningUpdates

echo "Exporting..."
xcodebuild -exportArchive \
    -archivePath "$ARCHIVE_PATH" \
    -exportPath "$EXPORT_PATH" \
    -exportOptionsPlist ExportOptions.plist

echo "Build complete: $EXPORT_PATH"
```

### SPM Build Script

```bash
#!/bin/bash
set -e

echo "Resolving dependencies..."
swift package resolve

echo "Building..."
swift build -c release

echo "Testing..."
swift test --parallel

echo "Build complete!"
```

## Code Coverage

### Generate Coverage

```bash
xcodebuild test \
    -workspace MyApp.xcworkspace \
    -scheme MyApp \
    -destination 'platform=iOS Simulator,name=iPhone 15' \
    -enableCodeCoverage YES \
    -resultBundlePath TestResults.xcresult
```

### Extract Coverage Report

```bash
xcrun xccov view --report TestResults.xcresult
xcrun xccov view --report --json TestResults.xcresult > coverage.json
```

## Fastlane (Optional)

### Fastfile Example

```ruby
default_platform(:ios)

platform :ios do
  desc "Run tests"
  lane :test do
    run_tests(
      workspace: "MyApp.xcworkspace",
      scheme: "MyApp",
      devices: ["iPhone 15"]
    )
  end

  desc "Build and upload to TestFlight"
  lane :beta do
    build_app(
      workspace: "MyApp.xcworkspace",
      scheme: "MyApp"
    )
    upload_to_testflight
  end
end
```

## Pre-commit Hooks

### SwiftFormat + SwiftLint Hook

```bash
#!/bin/sh
# .git/hooks/pre-commit

STAGED_FILES=$(git diff --cached --name-only --diff-filter=d | grep '\.swift$')

if [ -z "$STAGED_FILES" ]; then
    exit 0
fi

# Format
if command -v swiftformat &> /dev/null; then
    echo "Running SwiftFormat..."
    echo "$STAGED_FILES" | xargs swiftformat
    echo "$STAGED_FILES" | xargs git add
fi

# Lint
if command -v swiftlint &> /dev/null; then
    echo "Running SwiftLint..."
    echo "$STAGED_FILES" | xargs swiftlint --strict
    if [ $? -ne 0 ]; then
        echo "SwiftLint violations found. Fix before committing."
        exit 1
    fi
fi

exit 0
```

Make executable:
```bash
chmod +x .git/hooks/pre-commit
```
