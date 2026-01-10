---
name: using-xtool
description: This skill should be used when building iOS apps with xtool (Xcode-free iOS development), creating xtool projects, adding app extensions, or configuring xtool.yml. Triggers on "xtool", "SwiftPM iOS", "iOS on Linux", "iOS on Windows", "Xcode-free", "app extension", "widget extension", "share extension". Covers project setup, app extensions, and deployment.
---

# Using xtool

## Overview

xtool is a **cross-platform Xcode replacement** for building iOS apps with SwiftPM on Linux, Windows, and macOS. It is NOT XcodeGen, Tuist, or Xcode project files.

## Critical: xtool is NOT XcodeGen

| xtool Uses | NOT These |
|------------|-----------|
| `xtool.yml` | `project.yml`, `Project.swift` |
| `Package.swift` (SwiftPM) | Xcode project files |
| `xtool dev` | `xtool build`, `xtool run`, `xtool generate` |
| `Sources/` directory | `Extensions/` directory |

## Project Structure

```
MyApp/
├── Package.swift          # SwiftPM package definition
├── xtool.yml              # xtool configuration
├── Sources/
│   ├── MyApp/             # Main app target
│   │   ├── MyAppApp.swift
│   │   └── ContentView.swift
│   └── MyWidget/          # Extension target (if any)
│       └── Widget.swift
├── MyApp-Info.plist       # Optional custom Info.plist
└── MyWidget-Info.plist    # Required for extensions
```

## Quick Reference: Commands

```bash
# Project lifecycle
xtool new MyApp              # Create new project
xtool new MyApp --skip-setup # Create without running setup
xtool dev                    # Build + run (same as `xtool dev run`)
xtool dev build              # Build only
xtool dev build --ipa        # Build IPA file
xtool dev run -s             # Run on iOS Simulator (--simulator)
xtool dev run -c release     # Release build (--configuration)
xtool dev run -u <udid>      # Target specific device (--udid)
xtool dev generate-xcode-project  # Generate .xcodeproj for debugging

# Device management
xtool devices                # List connected devices
xtool install app.ipa        # Install IPA to device
xtool launch                 # Launch installed app
xtool uninstall              # Uninstall app from device

# Authentication & setup
xtool setup                  # Full setup (auth + SDK)
xtool auth login             # Authenticate with Apple
xtool auth status            # Check auth status
xtool auth logout            # Log out
xtool sdk                    # Manage Darwin Swift SDK

# Developer Services
xtool ds teams               # List development teams
xtool ds certificates        # Manage certificates
xtool ds profiles            # Manage provisioning profiles
```

## xtool.yml Format

Minimal:
```yaml
version: 1
bundleID: com.example.MyApp
```

Full options:
```yaml
version: 1
bundleID: com.example.MyApp
product: MyApp                    # Which SwiftPM product is main app
infoPath: MyApp-Info.plist        # Custom Info.plist (merged)
iconPath: Resources/AppIcon.png   # App icon (1024x1024 PNG)
entitlementsPath: App.entitlements
resources:                        # Files copied to app bundle root
  - Resources/GoogleServices-Info.plist
extensions:                       # App extensions
  - product: MyWidget
    infoPath: MyWidget-Info.plist
```

## Adding App Extensions (Widgets, Share, etc.)

### Step 1: Update Package.swift

Add BOTH a product AND a target. Note: xtool uses `.library` (not `.executable`) - it bundles the library into an iOS app.

```swift
// swift-tools-version: 6.0
import PackageDescription

let package = Package(
    name: "MyApp",
    platforms: [.iOS(.v17)],
    products: [
        .library(name: "MyApp", targets: ["MyApp"]),
        .library(name: "MyWidget", targets: ["MyWidget"]),  // ADD
    ],
    targets: [
        .target(name: "MyApp"),
        .target(name: "MyWidget"),  // ADD
    ]
)
```

### Step 2: Update xtool.yml

```yaml
version: 1
bundleID: com.example.MyApp
product: MyApp
extensions:
  - product: MyWidget
    infoPath: MyWidget-Info.plist
```

### Step 3: Create Extension Info.plist

Minimal required (just the extension type):

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>NSExtension</key>
    <dict>
        <key>NSExtensionPointIdentifier</key>
        <string>com.apple.widgetkit-extension</string>
    </dict>
</dict>
</plist>
```

### Step 4: Create Extension Code

`Sources/MyWidget/Widget.swift`:
```swift
import WidgetKit
import SwiftUI

@main struct MyWidgetBundle: WidgetBundle {
    var body: some Widget { MyWidget() }
}

struct MyWidget: Widget {
    var body: some WidgetConfiguration {
        StaticConfiguration(kind: "MyWidget", provider: Provider()) { entry in
            Text(entry.date, style: .date)
                .containerBackground(.fill.tertiary, for: .widget)
        }
        .configurationDisplayName("My Widget")
    }
}

struct Entry: TimelineEntry { var date = Date() }

struct Provider: TimelineProvider {
    func placeholder(in context: Context) -> Entry { Entry() }
    func getSnapshot(in context: Context, completion: @escaping (Entry) -> Void) {
        completion(Entry())
    }
    func getTimeline(in context: Context, completion: @escaping (Entry) -> Void) {
        completion(Timeline(entries: [Entry()], policy: .after(.now + 3600)))
    }
}
```

### Step 5: Build and Run

```bash
xtool dev
```

## Common Extension Types

| Extension | NSExtensionPointIdentifier |
|-----------|---------------------------|
| Widget (WidgetKit) | `com.apple.widgetkit-extension` |
| Share | `com.apple.share-services` |
| Action | `com.apple.ui-services` |
| Safari | `com.apple.Safari.web-extension` |
| Keyboard | `com.apple.keyboard-service` |
| Today (deprecated) | `com.apple.widget-extension` |

## Troubleshooting

| Error | Solution |
|-------|----------|
| "Untrusted Developer" | Settings > General > VPN & Device Management > Trust |
| Device not found | Connect USB, run `xtool devices`, enable Developer Mode |
| Auth failed | Run `xtool auth login` |
| Build fails on first run | Normal - SDK modules building. Wait for completion. |

## Resources Configuration

SwiftPM resources (in bundle subdirectory):
```swift
.target(name: "MyApp", resources: [.copy("Blob.png")])
// Access: Image("Blob", bundle: Bundle.module)
```

Top-level resources (in app bundle root):
```yaml
# xtool.yml
resources:
  - Resources/GoogleServices-Info.plist
```

## Entitlements

```yaml
# xtool.yml
entitlementsPath: App.entitlements
```

```xml
<!-- App.entitlements -->
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>com.apple.developer.homekit</key>
    <true/>
</dict>
</plist>
```

## Common Mistakes

| Mistake | Fix |
|---------|-----|
| Using `xtool build` | Use `xtool dev build` |
| Using `project.yml` | Use `xtool.yml` |
| Using `Extensions/` dir | Use `Sources/` (standard SwiftPM) |
| Forgetting Package.swift | Extensions need product + target in Package.swift |
| Complex extension Info.plist | Only NSExtension/NSExtensionPointIdentifier required |
