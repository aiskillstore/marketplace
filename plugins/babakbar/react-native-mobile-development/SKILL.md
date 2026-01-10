---
name: React Native Mobile Development
description: Build and manage React Native/Expo mobile apps including project setup, development workflows, and platform-specific guidance. Use when working on mobile app development, configuration, or running apps.
allowed-tools: Bash, Read, Write, Edit, Grep, Glob
---

# React Native Mobile Development

Guide for building mobile apps with React Native and Expo.

## When to Use

- Setting up React Native/Expo projects
- Running dev servers or builds
- Creating mobile components
- Handling platform-specific code (iOS/Android)
- Configuring app.json or native modules
- Troubleshooting mobile-specific issues

## Core Commands

```bash
# Development
npm start               # Start Metro bundler
npm run ios            # Run on iOS Simulator
npm run android        # Run on Android Emulator

# Expo specific
npx expo start         # Start with Expo CLI
npx expo install PKG   # Install compatible packages
npx expo prebuild      # Generate native code
```

## Component Structure

```typescript
// Mobile component template
import { View, Text, TouchableOpacity, StyleSheet } from 'react-native';

interface Props {
  title: string;
  onPress: () => void;
}

export function MyComponent({ title, onPress }: Props) {
  return (
    <TouchableOpacity onPress={onPress} style={styles.container}>
      <Text style={styles.text}>{title}</Text>
    </TouchableOpacity>
  );
}

const styles = StyleSheet.create({
  container: {
    padding: 16,
    backgroundColor: '#007AFF',
    borderRadius: 8,
  },
  text: {
    color: '#FFFFFF',
    fontSize: 16,
    fontWeight: '600',
  },
});
```

## Platform-Specific Code

```typescript
import { Platform } from 'react-native';

// Conditional rendering
{Platform.OS === 'ios' && <IOSComponent />}
{Platform.OS === 'android' && <AndroidComponent />}

// Platform-specific values
const height = Platform.select({
  ios: 44,
  android: 56,
  default: 50,
});

// Platform-specific styles
const styles = StyleSheet.create({
  container: {
    ...Platform.select({
      ios: { shadowColor: '#000', shadowOpacity: 0.3 },
      android: { elevation: 4 },
    }),
  },
});
```

## Best Practices

1. **Performance**: Use `StyleSheet.create()`, avoid inline styles, optimize images
2. **Accessibility**: Add `accessibilityLabel` and `accessibilityRole`
3. **Responsive**: Test on different screen sizes
4. **Navigation**: Use React Navigation or Expo Router
5. **State**: Keep component state minimal, use context/store for shared state

## Common Patterns

### Lists
```typescript
import { FlatList } from 'react-native';

<FlatList
  data={items}
  keyExtractor={(item) => item.id}
  renderItem={({ item }) => <ItemComponent item={item} />}
/>
```

### Forms
```typescript
import { TextInput } from 'react-native';
const [value, setValue] = useState('');

<TextInput
  value={value}
  onChangeText={setValue}
  placeholder="Enter text"
  style={styles.input}
/>
```

### Loading States
```typescript
import { ActivityIndicator } from 'react-native';

{loading ? <ActivityIndicator /> : <Content />}
```

## Troubleshooting

- **Metro won't start**: Clear cache with `npx expo start --clear`
- **Native module error**: Run `npx expo prebuild --clean`
- **Build fails**: Check `app.json` configuration
- **Simulator issues**: Reset simulator or emulator

## Resources

- [React Native Docs](https://reactnative.dev)
- [Expo Docs](https://docs.expo.dev)
