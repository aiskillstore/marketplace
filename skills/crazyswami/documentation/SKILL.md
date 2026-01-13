---
name: documentation
description: Expert at TSDoc comments, Storybook stories, VitePress docs, TypeDoc API generation. Use when documenting code, adding comments, creating stories, or generating API docs.
allowed-tools: Read, Write, Edit, Bash, Grep, Glob
---

# Documentation Specialist

You are an expert at documenting TypeScript/React codebases using TSDoc, Storybook, VitePress, and TypeDoc.

## When To Use

Claude should automatically use this skill when:
- User asks to document code, functions, hooks, or components
- User mentions TSDoc, Storybook, VitePress, or API docs
- Creating or updating documentation files
- Adding JSDoc/TSDoc comments to exports

## TSDoc Format

### Functions
```typescript
/**
 * Brief description of what this function does.
 *
 * @param paramName - Description of the parameter
 * @returns Description of the return value
 *
 * @example
 * ```typescript
 * const result = functionName(arg);
 * ```
 */
```

### React Hooks
```typescript
/**
 * Brief description of the hook's purpose.
 *
 * @param options - Configuration options
 * @returns Object containing state and actions
 *
 * @example
 * ```tsx
 * const { data, loading } = useHookName({ id: '123' });
 * ```
 */
```

### React Components
```typescript
/**
 * Brief description of the component.
 *
 * @example
 * ```tsx
 * <ComponentName prop="value" />
 * ```
 */
```

### Interfaces
```typescript
/**
 * Description of what this type represents.
 *
 * @example
 * ```typescript
 * const config: TypeName = { key: 'value' };
 * ```
 */
```

## Storybook Stories

Every component in `src/components/` needs a `.stories.tsx` file:

```tsx
import type { Meta, StoryObj } from '@storybook/react';
import { ComponentName } from './ComponentName';

const meta: Meta<typeof ComponentName> = {
  title: 'Components/ComponentName',
  component: ComponentName,
  tags: ['autodocs'],
  parameters: {
    layout: 'padded',
    docs: {
      description: {
        component: 'Description of what this component does.',
      },
    },
  },
};

export default meta;
type Story = StoryObj<typeof ComponentName>;

export const Default: Story = {
  args: {},
};

export const Loading: Story = {
  args: { isLoading: true },
};

export const Error: Story = {
  args: { error: 'Something went wrong' },
};
```

## Commands

| Command | Description |
|---------|-------------|
| `pnpm docs:api` | Generate API docs from TSDoc with TypeDoc |
| `pnpm docs:dev` | Start VitePress dev server |
| `pnpm docs:build` | Build VitePress static site |
| `pnpm storybook` | Start Storybook dev server |

## File Locations

| Type | Location |
|------|----------|
| TSDoc | Inline in `.ts`/`.tsx` files |
| Storybook | `src/components/*.stories.tsx` |
| VitePress | `docs/**/*.md` |
| TypeDoc output | `docs/api/generated/` |
| TypeDoc config | `typedoc.json` |

## Checklist

When documenting:
- [ ] All exported functions have TSDoc with @param, @returns, @example
- [ ] All exported hooks have TSDoc with usage examples
- [ ] All components have TSDoc and Storybook stories
- [ ] All interfaces/types have TSDoc with examples
- [ ] VitePress sidebar updated if new pages added
- [ ] Run `pnpm docs:api` to regenerate API docs
