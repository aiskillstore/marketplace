# Shadcn Aesthetic - Quick Reference

## Color Usage
```scss
// Always use HSL variables
background-color: hsl(var(--primary));
color: hsl(var(--primary-foreground));

// With opacity
border: 1px solid hsl(var(--border) / 0.5);
```

## Spacing Scale (4px base)
```scss
--spacing-1: 0.25rem;   // 4px
--spacing-2: 0.5rem;    // 8px
--spacing-4: 1rem;      // 16px
--spacing-6: 1.5rem;    // 24px
--spacing-8: 2rem;      // 32px
```

## Shadows (Subtle & Layered)
```scss
--shadow-sm: 0 1px 2px 0 rgb(0 0 0 / 0.05);
--shadow-md: 0 4px 6px -1px rgb(0 0 0 / 0.1);
--shadow-lg: 0 10px 15px -3px rgb(0 0 0 / 0.1);
```

## Transitions (Quick & Smooth)
```scss
transition: all 150ms cubic-bezier(0.4, 0, 0.2, 1);
```

## Focus States
```scss
&:focus-visible {
  outline: 2px solid hsl(var(--ring));
  outline-offset: 2px;
}
```

## Modern Layouts
```scss
// Grid with gap
display: grid;
grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
gap: var(--spacing-6);

// Flex with gap
display: flex;
gap: var(--spacing-2);
```

## Typography Scale
```scss
--text-sm: 0.875rem;    // 14px
--text-base: 1rem;      // 16px
--text-lg: 1.125rem;    // 18px
--text-xl: 1.25rem;     // 20px
```

## Button Pattern
```scss
.button {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: var(--spacing-2);
  padding: var(--spacing-2) var(--spacing-4);
  font-size: var(--text-sm);
  font-weight: var(--font-medium);
  border-radius: var(--radius);
  background-color: hsl(var(--primary));
  color: hsl(var(--primary-foreground));
  box-shadow: var(--shadow-sm);
  transition: all var(--duration-150) var(--ease-in-out);
  
  &:hover {
    background-color: hsl(var(--primary) / 0.9);
  }
  
  &:focus-visible {
    outline: 2px solid hsl(var(--ring));
    outline-offset: 2px;
  }
}
```

## Card Pattern
```scss
.card {
  padding: var(--spacing-6);
  border-radius: calc(var(--radius) + 2px);
  border: 1px solid hsl(var(--border));
  background-color: hsl(var(--card));
  box-shadow: var(--shadow-sm);
  
  &:hover {
    box-shadow: var(--shadow-md);
  }
}
```

## Input Pattern
```scss
.input {
  padding: var(--spacing-2) var(--spacing-3);
  font-size: var(--text-sm);
  border-radius: var(--radius);
  border: 1px solid hsl(var(--input));
  background-color: hsl(var(--background));
  box-shadow: var(--shadow-sm);
  
  &:focus {
    outline: none;
    border-color: hsl(var(--ring));
    box-shadow: 0 0 0 2px hsl(var(--ring) / 0.2);
  }
}
```

## Dark Mode
```scss
// Define in :root
:root {
  --background: 0 0% 100%;
  --foreground: 222.2 84% 4.9%;
}

// Override with .dark class
.dark {
  --background: 222.2 84% 4.9%;
  --foreground: 210 40% 98%;
}

// Components automatically adapt
.card {
  background-color: hsl(var(--background));
  color: hsl(var(--foreground));
}
```

## Anti-Patterns to Avoid

❌ Hard-coded hex colors
❌ Random pixel values (13px, 22px)
❌ Heavy shadows (0 5px 15px rgba(0,0,0,0.3))
❌ Slow transitions (0.3s)
❌ Margins instead of gap
❌ Removing outline without focus-visible
❌ RGB colors without variables

## Quality Checklist

✅ CSS variables for all colors
✅ HSL format with opacity support
✅ 4px spacing scale
✅ Subtle shadows
✅ 150ms transitions
✅ focus-visible states
✅ Grid/Flex with gap
✅ Dark mode support
✅ Reduced motion support
✅ Semantic class names
