---
name: Mobile Debugging
description: Debug React Native apps including metro bundler issues, native errors, performance problems, and crash analysis. Use when troubleshooting errors or investigating issues.
allowed-tools: Bash, Read, Grep
---

# Mobile Debugging

Debugging guide for React Native and Expo applications.

## When to Use

- App crashes or freezes
- Metro bundler errors
- Native module issues
- Performance problems
- Build failures
- Network request debugging

## Common Issues & Fixes

### Metro Bundler Problems

```bash
# Clear all caches
npx expo start --clear
watchman watch-del-all
rm -rf node_modules && npm install

# Reset packager cache
rm -rf /tmp/metro-*
rm -rf /tmp/haste-*
```

### Native Module Errors

```bash
# iOS: Reset pods
cd ios && pod deintegrate && pod install && cd ..

# Android: Clean build
cd android && ./gradlew clean && cd ..

# Expo: Prebuild clean
npx expo prebuild --clean
```

### Simulator/Emulator Issues

```bash
# iOS: Reset simulator
xcrun simctl erase all

# Android: Wipe emulator data
adb devices  # Find device ID
adb -s DEVICE_ID emu kill
```

## Debugging Tools

### React DevTools

```bash
# Install
npm install -g react-devtools

# Start
react-devtools

# In app: Shake device -> "Debug Remote JS"
```

### Metro Logs

```bash
# View detailed logs
npx expo start --verbose

# iOS device logs
npx react-native log-ios

# Android device logs
npx react-native log-android
adb logcat
```

### Network Debugging

```typescript
// Enable network inspector
import { Platform } from 'react-native';

if (__DEV__ && Platform.OS === 'ios') {
  require('react-native').NativeModules.DevSettings.setIsDebuggingRemotely(true);
}

// Or use Flipper for advanced network inspection
```

## Performance Debugging

### Identify Slow Renders

```typescript
// Add performance logging
import { useEffect, useRef } from 'react';

function useRenderTime(componentName: string) {
  const start = useRef(performance.now());

  useEffect(() => {
    const duration = performance.now() - start.current;
    if (duration > 16) {
      console.warn(`Slow render: ${componentName} took ${duration.toFixed(2)}ms`);
    }
  });
}

// Use in components
function MyComponent() {
  useRenderTime('MyComponent');
  return <View>...</View>;
}
```

### Memory Leaks

```typescript
// Check for missing cleanup
useEffect(() => {
  const subscription = someObservable.subscribe();
  const timer = setInterval(() => {}, 1000);

  // MUST clean up!
  return () => {
    subscription.unsubscribe();
    clearInterval(timer);
  };
}, []);
```

## Error Investigation

### JavaScript Errors

```bash
# Look for error in stack trace
# Check recent file changes
# Verify imports and dependencies
# Check for typos in variable names
```

### Native Errors

```bash
# iOS: Check Xcode console
# Android: Check Android Studio Logcat
# Look for Java/Swift exceptions
# Check native module compatibility
```

### Build Errors

```bash
# Check package versions
npx expo-doctor

# Verify node/npm versions
node --version
npm --version

# Check for conflicting dependencies
npm ls PACKAGE_NAME
```

## Debugging Commands

```bash
# Check what's using a port
lsof -ti:8081  # Metro bundler port
lsof -ti:19000 # Expo DevTools

# Kill process on port
kill -9 $(lsof -ti:8081)

# Check device connectivity
# iOS
xcrun simctl list devices

# Android
adb devices

# Restart adb
adb kill-server
adb start-server
```

## Debugging Checklist

When investigating issues:

1. **Reproduce**: Can you consistently trigger the issue?
2. **Recent Changes**: What was changed before it broke?
3. **Error Message**: Read the full error, including stack trace
4. **Dependencies**: Check if packages are compatible
5. **Platform**: Does it happen on iOS, Android, or both?
6. **Environment**: Dev only or production builds too?
7. **Logs**: Check Metro, Xcode, and Logcat for details

## Common Error Patterns

- **"Unable to resolve module"**: Check import path and file exists
- **"Invariant Violation"**: React error, check component lifecycle
- **"Network request failed"**: Check API URL and network connection
- **"Undefined is not an object"**: Check for null/undefined before accessing properties
- **"Maximum call stack size exceeded"**: Infinite loop or recursion

## Resources

- [React Native Debugging](https://reactnative.dev/docs/debugging)
- [Expo Debugging](https://docs.expo.dev/debugging/runtime-issues/)
- [Flipper Debugger](https://fbflipper.com/)
