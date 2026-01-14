# Code Signing Reference

## Understanding Certificates and Profiles

```bash
# List code signing identities
security find-identity -v -p codesigning

# List provisioning profiles
ls ~/Library/MobileDevice/Provisioning\ Profiles/

# Decode provisioning profile
security cms -D -i ~/Library/MobileDevice/Provisioning\ Profiles/PROFILE_UUID.mobileprovision
```

## Manual Code Signing

```bash
# Sign app bundle
codesign -s "Apple Development: Your Name (TEAM_ID)" \
    --entitlements MyApp.entitlements \
    MyApp.app

# Sign with specific identity
codesign -f -s "iPhone Distribution: Company Name" MyApp.app

# Verify signature
codesign -v --verbose MyApp.app
codesign -d --verbose=4 MyApp.app

# Display entitlements
codesign -d --entitlements :- MyApp.app

# Re-sign with different identity
codesign -f -s "New Identity" MyApp.app
```

## xcodebuild Signing Options

### Automatic Signing
```bash
xcodebuild -project MyApp.xcodeproj \
    -scheme MyApp \
    -allowProvisioningUpdates \
    build
```

### Manual Signing
```bash
xcodebuild -project MyApp.xcodeproj \
    -scheme MyApp \
    CODE_SIGN_IDENTITY="iPhone Distribution: Company" \
    PROVISIONING_PROFILE_SPECIFIER="MyApp Distribution" \
    build
```

### Disable Signing (CI builds)
```bash
xcodebuild build \
    CODE_SIGN_IDENTITY="" \
    CODE_SIGNING_REQUIRED=NO \
    CODE_SIGNING_ALLOWED=NO
```

## CI/CD Keychain Setup

```bash
# Create temporary keychain
security create-keychain -p "$KEYCHAIN_PASSWORD" build.keychain
security default-keychain -s build.keychain
security unlock-keychain -p "$KEYCHAIN_PASSWORD" build.keychain

# Import certificate
security import certificate.p12 -k build.keychain \
    -P "$CERT_PASSWORD" -T /usr/bin/codesign

# Allow codesign access
security set-key-partition-list -S apple-tool:,apple:,codesign: \
    -s -k "$KEYCHAIN_PASSWORD" build.keychain
```

## ExportOptions.plist

See `assets/ExportOptions/` for templates:
- `app-store.plist` - App Store distribution
- `ad-hoc.plist` - Ad-hoc distribution
- `development.plist` - Development/testing

## Troubleshooting

### "No signing certificate" error
```bash
# Check certificates
security find-identity -v -p codesigning

# Clear derived data
rm -rf ~/Library/Developer/Xcode/DerivedData

# Reset package caches
rm -rf ~/Library/Caches/org.swift.swiftpm
```

### Provisioning profile issues
```bash
# Download fresh profiles
xcodebuild -downloadAllPlatforms

# List profile details
security cms -D -i profile.mobileprovision | grep -A1 "ExpirationDate"
```
