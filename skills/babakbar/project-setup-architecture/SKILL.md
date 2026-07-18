---
name: Project Setup & Architecture
description: Set up project infrastructure including TypeScript, database, state management, navigation, and testing. Use when initializing new features or configuring development environment.
allowed-tools: Bash, Read, Write, Edit, Glob
---

# Project Setup & Architecture

Guide for setting up React Native/Expo project infrastructure.

## When to Use

- Initializing TypeScript configuration
- Setting up database layer
- Configuring state management
- Installing and configuring testing
- Creating directory structure
- Adding linting and formatting

## Setup Workflows

### TypeScript Setup

```bash
# Install TypeScript
npm install --save-dev typescript @types/react @types/react-native

# Create tsconfig.json
npx tsc --init
```

```json
{
  "extends": "expo/tsconfig.base",
  "compilerOptions": {
    "strict": true,
    "skipLibCheck": true,
    "jsx": "react-native"
  }
}
```

### Directory Structure

```bash
# Create feature-sliced architecture
mkdir -p src/{app,features,shared,db,theme}
mkdir -p src/shared/{components,hooks,utils,types}
```

### Database Setup (SQLite + Drizzle)

```bash
# Install dependencies
npx expo install expo-sqlite
npm install drizzle-orm
npm install --save-dev drizzle-kit

# Create structure
mkdir -p src/db/{schema,migrations}
```

```typescript
// src/db/client.ts
import * as SQLite from 'expo-sqlite';
import { drizzle } from 'drizzle-orm/expo-sqlite';

const db = SQLite.openDatabaseSync('app.db');
export const drizzle = drizzle(db);
```

### State Management (Zustand)

```bash
npm install zustand
```

```typescript
// src/shared/stores/useAppStore.ts
import { create } from 'zustand';

interface AppState {
  count: number;
  increment: () => void;
}

export const useAppStore = create<AppState>((set) => ({
  count: 0,
  increment: () => set((state) => ({ count: state.count + 1 })),
}));
```

### Testing Setup

```bash
npm install --save-dev jest @testing-library/react-native
```

```json
// package.json
{
  "scripts": {
    "test": "jest"
  }
}
```

### Linting & Formatting

```bash
npm install --save-dev eslint prettier
npx eslint --init
```

## Configuration Files

### app.json (Expo Configuration)
```json
{
  "expo": {
    "name": "MyApp",
    "slug": "my-app",
    "version": "1.0.0",
    "platforms": ["ios", "android"],
    "ios": {
      "bundleIdentifier": "com.company.myapp"
    },
    "android": {
      "package": "com.company.myapp"
    }
  }
}
```

### package.json Scripts
```json
{
  "scripts": {
    "start": "expo start",
    "android": "expo start --android",
    "ios": "expo start --ios",
    "test": "jest",
    "lint": "eslint src/",
    "type-check": "tsc --noEmit"
  }
}
```

## Best Practices

1. **Incremental Setup**: Install and configure one system at a time
2. **Verify Installation**: Test each setup before moving to next
3. **Check Dependencies**: Ensure compatibility with Expo SDK
4. **Use Expo Install**: For Expo packages, use `npx expo install`
5. **Version Control**: Commit after each successful setup step

## Common Tasks

### Add New Dependency
```bash
# Check if it's an Expo SDK package
npx expo install package-name

# Otherwise use npm
npm install package-name
```

### Create New Feature Module
```bash
mkdir -p src/features/my-feature/{components,hooks,services,types}
touch src/features/my-feature/index.ts
```

### Generate Database Migration
```bash
npx drizzle-kit generate:sqlite
npx drizzle-kit push:sqlite
```

## Verification Checklist

After setup, verify:
- [ ] TypeScript compiles without errors (`npx tsc --noEmit`)
- [ ] App runs on both iOS and Android
- [ ] Tests run successfully (`npm test`)
- [ ] Linting passes (`npm run lint`)
- [ ] Database connects and queries work
- [ ] State management functions correctly

## Resources

- [Expo Configuration](https://docs.expo.dev/workflow/configuration/)
- [TypeScript with Expo](https://docs.expo.dev/guides/typescript/)
