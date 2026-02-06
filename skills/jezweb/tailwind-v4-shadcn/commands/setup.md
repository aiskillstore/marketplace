# Setup Tailwind v4 + shadcn/ui

Add Tailwind CSS v4 and shadcn/ui to an existing React/Vite project.

---

## Your Task

Follow these steps to configure Tailwind v4 and shadcn/ui.

### 1. Check Prerequisites

Verify the project has:
- Vite + React configured
- TypeScript (recommended)

If not a Vite project, inform user of requirements.

### 2. Install Tailwind v4

```bash
npm install tailwindcss @tailwindcss/vite
```

### 3. Configure Vite

Update `vite.config.ts`:

```typescript
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import tailwindcss from '@tailwindcss/vite';

export default defineConfig({
  plugins: [react(), tailwindcss()],
});
```

**Important**: Use `@tailwindcss/vite` plugin, NOT PostCSS.

### 4. Create CSS Entry

Create or update `src/index.css`:

```css
@import "tailwindcss";
```

### 5. Initialize shadcn/ui

```bash
npx shadcn@latest init
```

When prompted:
- Style: Default
- Base color: Neutral (or user preference)
- CSS variables: Yes
- Tailwind config: Leave empty for v4
- Components path: `src/components`
- Utils path: `src/lib/utils`

### 6. Configure components.json

Ensure `components.json` has:

```json
{
  "tailwind": {
    "config": ""
  }
}
```

**Important**: Empty string for `config` is required for Tailwind v4.

### 7. Add Theme Provider

Create `src/components/theme-provider.tsx`:

```typescript
import { createContext, useContext, useEffect, useState } from 'react';

type Theme = 'dark' | 'light' | 'system';

type ThemeProviderProps = {
  children: React.ReactNode;
  defaultTheme?: Theme;
  storageKey?: string;
};

type ThemeProviderState = {
  theme: Theme;
  setTheme: (theme: Theme) => void;
};

const ThemeProviderContext = createContext<ThemeProviderState | undefined>(undefined);

export function ThemeProvider({
  children,
  defaultTheme = 'system',
  storageKey = 'ui-theme',
}: ThemeProviderProps) {
  const [theme, setTheme] = useState<Theme>(
    () => (localStorage.getItem(storageKey) as Theme) || defaultTheme
  );

  useEffect(() => {
    const root = window.document.documentElement;
    root.classList.remove('light', 'dark');

    if (theme === 'system') {
      const systemTheme = window.matchMedia('(prefers-color-scheme: dark)').matches
        ? 'dark'
        : 'light';
      root.classList.add(systemTheme);
    } else {
      root.classList.add(theme);
    }
  }, [theme]);

  return (
    <ThemeProviderContext.Provider
      value={{
        theme,
        setTheme: (theme: Theme) => {
          localStorage.setItem(storageKey, theme);
          setTheme(theme);
        },
      }}
    >
      {children}
    </ThemeProviderContext.Provider>
  );
}

export const useTheme = () => {
  const context = useContext(ThemeProviderContext);
  if (!context) throw new Error('useTheme must be used within ThemeProvider');
  return context;
};
```

### 8. Wrap App with Theme Provider

Update main entry (e.g., `src/main.tsx`):

```typescript
import { ThemeProvider } from '@/components/theme-provider';

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <ThemeProvider defaultTheme="system">
      <App />
    </ThemeProvider>
  </React.StrictMode>
);
```

### 9. Add First Components

```bash
npx shadcn@latest add button
npx shadcn@latest add card
```

### 10. Provide Next Steps

```
✅ Tailwind v4 + shadcn/ui configured!

📁 Added:
   - @tailwindcss/vite plugin
   - src/components/ui/     (shadcn components)
   - src/lib/utils.ts       (cn utility)
   - Theme provider         (dark/light/system)

🎨 Add components:
   npx shadcn@latest add <component>
   npx shadcn@latest add button card input

⚠️ Critical Rules:
   - Use semantic colors: bg-primary, text-foreground
   - Never use raw Tailwind colors: bg-blue-500

📚 Skill loaded: tailwind-v4-shadcn
   - v3→v4 syntax corrections
   - Semantic color system
   - Theme provider included
```

---

## Tailwind v4 Key Differences

| v3 Pattern | v4 Pattern |
|------------|------------|
| `tailwind.config.js` | CSS-based config in `@theme` |
| PostCSS plugin | Vite plugin (`@tailwindcss/vite`) |
| `@apply` everywhere | Prefer utility classes |
