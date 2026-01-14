# iOS Simulator Control (simctl)

## Listing Simulators

```bash
# List all simulators
xcrun simctl list

# Devices only
xcrun simctl list devices

# Available device types
xcrun simctl list devicetypes

# Available runtimes
xcrun simctl list runtimes

# JSON output
xcrun simctl list devices --json
```

## Managing Simulators

```bash
# Boot simulator
xcrun simctl boot "iPhone 15"
xcrun simctl boot DEVICE_UDID

# Open Simulator app with device
open -a Simulator --args -CurrentDeviceUDID DEVICE_UDID

# Shutdown
xcrun simctl shutdown booted
xcrun simctl shutdown "iPhone 15"
xcrun simctl shutdown all

# Erase (factory reset)
xcrun simctl erase booted
xcrun simctl erase all

# Create new simulator
xcrun simctl create "My iPhone" \
    com.apple.CoreSimulator.SimDeviceType.iPhone-15 \
    com.apple.CoreSimulator.SimRuntime.iOS-17-0

# Clone simulator
xcrun simctl clone "iPhone 15" "iPhone 15 Clone"

# Delete simulator
xcrun simctl delete "My iPhone"

# Delete unavailable (cleanup)
xcrun simctl delete unavailable
```

## App Management

```bash
# Install app
xcrun simctl install booted ./MyApp.app

# Uninstall app
xcrun simctl uninstall booted com.mycompany.myapp

# Launch app
xcrun simctl launch booted com.mycompany.myapp

# Launch with arguments
xcrun simctl launch booted com.mycompany.myapp --arg1 value1

# Terminate app
xcrun simctl terminate booted com.mycompany.myapp

# Get app container path
xcrun simctl get_app_container booted com.mycompany.myapp data
xcrun simctl get_app_container booted com.mycompany.myapp app
```

## Media and Screenshots

```bash
# Open URL
xcrun simctl openurl booted "https://example.com"
xcrun simctl openurl booted "myapp://deeplink/path"

# Add photos/videos
xcrun simctl addmedia booted ~/Desktop/photo.jpg
xcrun simctl addmedia booted ~/Desktop/video.mp4

# Screenshot
xcrun simctl io booted screenshot screenshot.png

# Record video (Ctrl+C to stop)
xcrun simctl io booted recordVideo video.mp4
```

## Push Notifications

```bash
# Send push notification
xcrun simctl push booted com.mycompany.myapp notification.apns
```

Example `notification.apns`:
```json
{
    "aps": {
        "alert": {
            "title": "Test",
            "body": "Hello World"
        }
    }
}
```

## Privacy/Permissions

```bash
# Grant permission
xcrun simctl privacy booted grant photos com.mycompany.myapp
xcrun simctl privacy booted grant location com.mycompany.myapp
xcrun simctl privacy booted grant camera com.mycompany.myapp

# Revoke permission
xcrun simctl privacy booted revoke location com.mycompany.myapp

# Reset all permissions
xcrun simctl privacy booted reset all com.mycompany.myapp
```

## Status Bar (Screenshots)

```bash
# Override status bar
xcrun simctl status_bar booted override \
    --time "9:41" \
    --batteryState charged \
    --batteryLevel 100 \
    --wifiBars 3 \
    --cellularBars 4

# Clear overrides
xcrun simctl status_bar booted clear
```

## Appearance

```bash
# Dark mode
xcrun simctl ui booted appearance dark

# Light mode
xcrun simctl ui booted appearance light
```

## Clipboard

```bash
# Paste to simulator
echo "text to paste" | xcrun simctl pbpaste booted

# Copy from simulator
xcrun simctl pbcopy booted
```

## Quick Reference

| Task | Command |
|------|---------|
| List devices | `xcrun simctl list devices` |
| Boot iPhone 15 | `xcrun simctl boot "iPhone 15"` |
| Shutdown all | `xcrun simctl shutdown all` |
| Install app | `xcrun simctl install booted ./App.app` |
| Launch app | `xcrun simctl launch booted com.app.id` |
| Screenshot | `xcrun simctl io booted screenshot shot.png` |
| Dark mode | `xcrun simctl ui booted appearance dark` |
