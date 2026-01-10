---
name: shadcn-ui-patterns
description: Use when building UI components. Enforces ShadCN UI patterns, accessibility standards (Radix UI), and TailwindCSS best practices for November 2025.
allowed-tools: Read, Grep, Glob
---

# ShadCN UI Patterns - November 2025 Standards

## When to Use
- Building new UI components
- Refactoring existing components to use ShadCN
- Implementing forms with validation
- Creating modals, dialogs, and overlays
- Ensuring accessibility compliance

## Why ShadCN UI?
- **Copy-paste, not npm** - Full ownership of component code
- **Radix UI primitives** - Accessibility built-in (WCAG 2.1 AA compliant)
- **TailwindCSS-first** - Full customization, no CSS-in-JS
- **TypeScript-native** - Type-safe props and variants
- **Server Component compatible** - Works with Next.js 15 App Router

## Core Principles

### 1. Component Installation Pattern
```bash
# Install individual components as needed
npx shadcn@latest add button
npx shadcn@latest add dialog
npx shadcn@latest add form
npx shadcn@latest add input
npx shadcn@latest add label
```

Components are copied to `src/components/ui/` directory - you own the code.

### 2. Component Usage Patterns

#### Button Component
```typescript
import { Button } from "@/components/ui/button"

// ✅ DO: Use semantic variants
<Button variant="default">Save</Button>
<Button variant="destructive">Delete</Button>
<Button variant="outline">Cancel</Button>
<Button variant="ghost">Skip</Button>
<Button variant="link">Learn More</Button>

// ✅ DO: Use size variants
<Button size="default">Medium</Button>
<Button size="sm">Small</Button>
<Button size="lg">Large</Button>
<Button size="icon"><Icon /></Button>

// ❌ DON'T: Create custom buttons without using Button component
<button className="px-4 py-2 bg-blue-500">Bad</button>
```

#### Dialog/Modal Component
```typescript
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog"

// ✅ DO: Use proper dialog structure (accessibility)
<Dialog>
  <DialogTrigger asChild>
    <Button>Open Settings</Button>
  </DialogTrigger>
  <DialogContent>
    <DialogHeader>
      <DialogTitle>Settings</DialogTitle>
      <DialogDescription>
        Configure your application settings here.
      </DialogDescription>
    </DialogHeader>
    {/* Dialog content */}
  </DialogContent>
</Dialog>

// ❌ DON'T: Skip DialogHeader or DialogTitle (breaks screen readers)
<DialogContent>
  <h2>Settings</h2> {/* Wrong - use DialogTitle */}
</DialogContent>
```

#### Form Component (with React Hook Form + Zod)
```typescript
import { useForm } from "react-hook-form"
import { zodResolver } from "@hookform/resolvers/zod"
import * as z from "zod"
import {
  Form,
  FormControl,
  FormDescription,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "@/components/ui/form"
import { Input } from "@/components/ui/input"
import { Button } from "@/components/ui/button"

// ✅ DO: Define Zod schema first (validation)
const formSchema = z.object({
  email: z.string().email("Invalid email address"),
  password: z.string().min(8, "Password must be at least 8 characters"),
})

function LoginForm() {
  const form = useForm<z.infer<typeof formSchema>>({
    resolver: zodResolver(formSchema),
    defaultValues: {
      email: "",
      password: "",
    },
  })

  async function onSubmit(values: z.infer<typeof formSchema>) {
    // Type-safe validated data
    console.log(values)
  }

  return (
    <Form {...form}>
      <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
        <FormField
          control={form.control}
          name="email"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Email</FormLabel>
              <FormControl>
                <Input placeholder="you@example.com" {...field} />
              </FormControl>
              <FormDescription>
                We'll never share your email.
              </FormDescription>
              <FormMessage />
            </FormItem>
          )}
        />

        <FormField
          control={form.control}
          name="password"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Password</FormLabel>
              <FormControl>
                <Input type="password" {...field} />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />

        <Button type="submit">Sign In</Button>
      </form>
    </Form>
  )
}

// ❌ DON'T: Use uncontrolled forms without validation
<form>
  <input name="email" /> {/* No validation */}
</form>
```

### 3. Server vs Client Components

```typescript
// ✅ DO: Use Server Component for static dialogs
import { Dialog, DialogContent } from "@/components/ui/dialog"

export default function ServerDialog() {
  // No 'use client' needed
  return <Dialog>...</Dialog>
}

// ✅ DO: Use Client Component when state is needed
'use client'

import { useState } from 'react'
import { Dialog, DialogContent } from "@/components/ui/dialog"

export function ClientDialog() {
  const [open, setOpen] = useState(false)

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogContent>...</DialogContent>
    </Dialog>
  )
}
```

### 4. Accessibility Requirements

#### Focus Management
```typescript
// ✅ DO: Use DialogTrigger with asChild for proper focus
<DialogTrigger asChild>
  <Button>Open</Button>
</DialogTrigger>

// ❌ DON'T: Manually trigger without proper focus handling
<Button onClick={() => setOpen(true)}>Open</Button>
```

#### Keyboard Navigation
```typescript
// ✅ ShadCN handles this automatically:
// - ESC closes dialogs
// - Tab navigates focusable elements
// - Enter/Space activates buttons
// - Arrow keys navigate menus

// ❌ DON'T: Override default keyboard behavior without good reason
```

#### Screen Reader Support
```typescript
// ✅ DO: Always include DialogTitle (required for ARIA)
<DialogHeader>
  <DialogTitle>Delete Project</DialogTitle>
  <DialogDescription>
    This action cannot be undone.
  </DialogDescription>
</DialogHeader>

// ❌ DON'T: Use visually hidden titles incorrectly
<DialogTitle className="sr-only">Delete</DialogTitle>
// Only hide if there's a clear visual alternative
```

### 5. Common Components to Use

| Component | Use Case | Key Props |
|-----------|----------|-----------|
| `Button` | All clickable actions | `variant`, `size`, `asChild` |
| `Dialog` | Modals, confirmations | `open`, `onOpenChange` |
| `Sheet` | Side panels, drawers | `side`, `open`, `onOpenChange` |
| `Popover` | Tooltips, menus | `open`, `onOpenChange` |
| `Form` | All forms | `form` (from useForm) |
| `Input` | Text input | `type`, `placeholder` |
| `Select` | Dropdowns | `value`, `onValueChange` |
| `Checkbox` | Boolean input | `checked`, `onCheckedChange` |
| `RadioGroup` | Single choice | `value`, `onValueChange` |
| `Table` | Data tables | `table` (from TanStack Table) |
| `Card` | Content containers | `CardHeader`, `CardContent`, `CardFooter` |
| `Toast` | Notifications | `title`, `description`, `variant` |
| `Command` | Command palette | `onSelect` |
| `Tabs` | Tab navigation | `value`, `onValueChange` |

### 6. TailwindCSS Best Practices

```typescript
// ✅ DO: Use Tailwind utility classes
<Button className="w-full mt-4">Submit</Button>

// ✅ DO: Use cn() helper for conditional classes
import { cn } from "@/lib/utils"

<Button className={cn(
  "w-full",
  isLoading && "opacity-50 cursor-not-allowed"
)}>
  Submit
</Button>

// ❌ DON'T: Use inline styles
<Button style={{ width: '100%', marginTop: '16px' }}>Submit</Button>

// ❌ DON'T: Create custom CSS files for components
// styles.css
.my-button { width: 100%; }
```

### 7. Dark Mode Support

```typescript
// ✅ DO: Use Tailwind dark mode classes
<div className="bg-white dark:bg-gray-900 text-black dark:text-white">
  Content
</div>

// ✅ ShadCN components have dark mode built-in
<Button variant="default">
  {/* Automatically styled for dark mode */}
</Button>
```

## Common Mistakes to Catch

### ❌ Missing DialogTitle (Accessibility Violation)
```typescript
// BAD
<DialogContent>
  <h2>Settings</h2>
  <p>Content</p>
</DialogContent>

// GOOD
<DialogContent>
  <DialogHeader>
    <DialogTitle>Settings</DialogTitle>
  </DialogHeader>
  <p>Content</p>
</DialogContent>
```

### ❌ Not Using Form Component for Forms
```typescript
// BAD - No validation, poor UX
<form>
  <input name="email" />
  <button type="submit">Submit</button>
</form>

// GOOD - Validation, error messages, accessibility
<Form {...form}>
  <form onSubmit={form.handleSubmit(onSubmit)}>
    <FormField name="email" ... />
  </form>
</Form>
```

### ❌ Hardcoding Colors Instead of Using Variants
```typescript
// BAD
<Button className="bg-red-500 hover:bg-red-600">Delete</Button>

// GOOD
<Button variant="destructive">Delete</Button>
```

### ❌ Not Using asChild for Triggers
```typescript
// BAD - Creates unnecessary nested buttons
<DialogTrigger>
  <Button>Open</Button>
</DialogTrigger>
// Renders: <button><button>Open</button></button> (invalid HTML)

// GOOD - Merges props into single button
<DialogTrigger asChild>
  <Button>Open</Button>
</DialogTrigger>
// Renders: <button>Open</button>
```

## Testing ShadCN Components

```typescript
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { Dialog, DialogTrigger, DialogContent } from '@/components/ui/dialog'

describe('Dialog', () => {
  it('should open when trigger is clicked', async () => {
    const user = userEvent.setup()

    render(
      <Dialog>
        <DialogTrigger asChild>
          <button>Open</button>
        </DialogTrigger>
        <DialogContent>
          <div>Dialog content</div>
        </DialogContent>
      </Dialog>
    )

    // Dialog content should not be visible initially
    expect(screen.queryByText('Dialog content')).not.toBeInTheDocument()

    // Click trigger
    await user.click(screen.getByText('Open'))

    // Dialog content should now be visible
    expect(screen.getByText('Dialog content')).toBeInTheDocument()
  })

  it('should close on ESC key', async () => {
    const user = userEvent.setup()

    render(
      <Dialog defaultOpen>
        <DialogContent>Dialog content</DialogContent>
      </Dialog>
    )

    expect(screen.getByText('Dialog content')).toBeInTheDocument()

    await user.keyboard('{Escape}')

    expect(screen.queryByText('Dialog content')).not.toBeInTheDocument()
  })
})
```

## Resources

- **Official Docs**: https://ui.shadcn.com
- **Radix UI**: https://www.radix-ui.com
- **Examples**: https://ui.shadcn.com/examples
- **Themes**: https://ui.shadcn.com/themes

## November 2025 Note

ShadCN UI is the industry standard for React component libraries as of November 2025. All new Quetrex applications must use ShadCN UI for consistency, accessibility, and maintainability.
