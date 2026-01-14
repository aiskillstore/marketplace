# xcodebuild Reference

## Basic Commands

```bash
# Build project
xcodebuild -project MyApp.xcodeproj -scheme MyApp build

# Build workspace
xcodebuild -workspace MyApp.xcworkspace -scheme MyApp build

# Clean and build
xcodebuild -project MyApp.xcodeproj -scheme MyApp clean build

# Build with configuration
xcodebuild -project MyApp.xcodeproj -scheme MyApp -configuration Release build
```

## Destinations

### iOS Simulator
```bash
-destination 'platform=iOS Simulator,name=iPhone 15'
-destination 'platform=iOS Simulator,name=iPhone 15 Pro,OS=17.2'
```

### iOS Device
```bash
-destination 'platform=iOS,id=DEVICE_UDID'
-destination 'generic/platform=iOS'
```

### macOS
```bash
-destination 'platform=macOS'
-destination 'platform=macOS,arch=arm64'
```

### Mac Catalyst
```bash
-destination 'platform=macOS,variant=Mac Catalyst'
```

### List Available
```bash
xcodebuild -scheme MyApp -showdestinations
```

## Archive and Export

```bash
# Create archive
xcodebuild -workspace MyApp.xcworkspace \
    -scheme MyApp \
    -configuration Release \
    -archivePath ./build/MyApp.xcarchive \
    archive

# Export IPA
xcodebuild -exportArchive \
    -archivePath ./build/MyApp.xcarchive \
    -exportPath ./build/export \
    -exportOptionsPlist ExportOptions.plist
```

## Package Dependencies

```bash
# Resolve SPM packages
xcodebuild -resolvePackageDependencies \
    -workspace MyApp.xcworkspace \
    -scheme MyApp

# Custom package cache
xcodebuild -workspace MyApp.xcworkspace \
    -scheme MyApp \
    -clonedSourcePackagesDirPath ./SourcePackages \
    build
```

## Testing

```bash
# Run all tests
xcodebuild test \
    -workspace MyApp.xcworkspace \
    -scheme MyApp \
    -destination 'platform=iOS Simulator,name=iPhone 15'

# Specific test class
xcodebuild test \
    -only-testing:MyAppTests/MyTestClass

# Specific test method
xcodebuild test \
    -only-testing:MyAppTests/MyTestClass/testMethod

# Skip tests
xcodebuild test \
    -skip-testing:MyAppTests/SlowTests

# Build for testing only
xcodebuild build-for-testing \
    -workspace MyApp.xcworkspace \
    -scheme MyApp

# Test without building
xcodebuild test-without-building \
    -workspace MyApp.xcworkspace \
    -scheme MyApp

# Code coverage
xcodebuild test \
    -enableCodeCoverage YES \
    -resultBundlePath ./TestResults.xcresult
```

## Xcode Selection

```bash
# Show active Xcode
xcode-select -p

# Switch Xcode version
sudo xcode-select -s /Applications/Xcode.app/Contents/Developer

# List SDKs
xcodebuild -showsdks

# List schemes
xcodebuild -list -project MyApp.xcodeproj
xcodebuild -list -workspace MyApp.xcworkspace
```

## xcrun

Route to correct developer tools:

```bash
xcrun swift --version
xcrun swiftc MyFile.swift -o MyExecutable
xcrun simctl list
xcrun notarytool --help
xcrun altool --help
```

## Useful Flags

| Flag | Description |
|------|-------------|
| `-v` | Verbose output |
| `-configuration Debug/Release` | Build configuration |
| `-allowProvisioningUpdates` | Auto-manage signing |
| `-resultBundlePath` | Save test results |
| `-derivedDataPath` | Custom derived data |
