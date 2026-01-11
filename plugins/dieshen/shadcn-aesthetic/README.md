# shadcn-aesthetic

Modern CSS/SCSS architecture skill based on shadcn/ui design principles.

## What This Does

Teaches Claude Code to generate refined, professional CSS that matches the shadcn/ui aesthetic - clean, minimal, accessible, and beautifully crafted.

Instead of generating old-school, clunky CSS with hard-coded colors and random pixel values, Claude will output modern CSS with:

- **CSS variables** for complete theming
- **HSL color system** for easy manipulation and opacity
- **Consistent spacing scale** (4px base)
- **Subtle, layered shadows**
- **Quick, smooth transitions** (150ms)
- **Proper focus states** (focus-visible)
- **Modern layout primitives** (Grid/Flex with gap)
- **Dark mode support** built-in
- **Accessibility** by default

## Installation

```bash
# Add marketplace
/plugin marketplace add https://github.com/Dieshen/claude_marketplace.git

# Install plugin
/plugin install shadcn-aesthetic@dieshen-plugins

# Restart Claude Code
```

## Usage

This skill activates automatically when:
- Writing CSS, SCSS, or styling code
- Creating component styles from scratch
- Refactoring existing styles
- Building design systems or theme systems
- Working on any web UI (Blazor, React, Vue, etc.)

Just ask Claude to create styled components and it will use these modern patterns!

## Examples

### Before
```scss
.button {
  padding: 10px 20px;
  background: #007bff;
  border-radius: 4px;
  transition: all 0.3s ease;
}
```

### After
```scss
.button {
  display: inline-flex;
  align-items: center;
  padding: var(--spacing-2) var(--spacing-4);
  background-color: hsl(var(--primary));
  color: hsl(var(--primary-foreground));
  border-radius: var(--radius);
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

## What's Included

- **SKILL.md** - Complete comprehensive guide (50+ patterns)
- **QUICK_REFERENCE.md** - Fast lookup for common patterns
- **BEFORE_AFTER.md** - Visual examples of improvements

## Perfect For

- **Vibe.UI development** - Building components that match shadcn aesthetic
- **Blazor projects** - Modern styling for Blazor components
- **React/Vue projects** - shadcn-style components
- **Design systems** - Building consistent, themeable systems
- **Any web project** - Upgrading from old-school CSS

## Key Features

### Color System
```scss
// HSL-based for easy theming
:root {
  --primary: 222.2 47.4% 11.2%;
  --primary-foreground: 210 40% 98%;
}

// Use with opacity
background: hsl(var(--primary) / 0.9);
```

### Spacing Scale
```scss
// Consistent 4px-based scale
--spacing-2: 0.5rem;   // 8px
--spacing-4: 1rem;     // 16px
--spacing-6: 1.5rem;   // 24px
```

### Shadow System
```scss
// Subtle, layered shadows
--shadow-sm: 0 1px 2px 0 rgb(0 0 0 / 0.05);
--shadow-md: 0 4px 6px -1px rgb(0 0 0 / 0.1);
```

### Dark Mode
```scss
// Automatic dark mode support
.dark {
  --background: 222.2 84% 4.9%;
  --foreground: 210 40% 98%;
}
```

## Documentation

- [Complete Skill Documentation](./SKILL.md)
- [Quick Reference](./QUICK_REFERENCE.md)
- [Before & After Examples](./BEFORE_AFTER.md)

## Why This Matters

Modern UIs demand modern CSS. This skill ensures Claude generates:
- ✅ Professional-looking components
- ✅ Accessible interfaces by default
- ✅ Complete theming support
- ✅ Perfect dark mode
- ✅ Consistent design language
- ✅ Maintainable code

No more clunky, old-school CSS!

## Vibe.UI Integration

This skill was created specifically to help with [Vibe.UI](https://github.com/Dieshen/Vibe.UI) development - bringing shadcn aesthetics to Blazor. Perfect for:

- Creating new Vibe.UI components
- Refining existing component styles
- Building custom themes
- Ensuring consistency across the library

## License

MIT License - see repository LICENSE for details

## Author

Brock / Narcoleptic Fox LLC
- **Email**: contact@narcolepticfox.com
- **Company**: [Narcoleptic Fox](https://narcolepticfox.com)

## Contributing

Found ways to improve these patterns? Contributions welcome! This skill evolves with modern CSS best practices.

---

**Remember:** Subtle beats flashy. Consistent beats clever. Accessible beats everything.
