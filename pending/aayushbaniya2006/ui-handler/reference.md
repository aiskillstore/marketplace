# UI Architecture Reference

## 1. Component Strategy

| Component Type | Source | MCP Tool | Path |
| :--- | :--- | :--- | :--- |
| **Atoms** (Button, Input) | Shadcn UI | `shadcn` | `src/components/ui/` |
| **Blocks** (Hero, Footer) | 21st.dev | `21st-dev` | `src/components/sections/` |
| **Page Specific** | Custom | - | `src/app/.../_components/` |

## 2. Theming (`src/app/globals.css`)
-   **Format**: CSS Variables with Tailwind v4 `@theme`.
-   **Colors**: OKLCH color space is preferred for dynamic range.
-   **Updates**: Use the Shadcn MCP to update the base color palette or typography variables safely.

## 3. Best Practices
1.  **Don't Reinvent**: Always check Shadcn or 21st.dev before coding from scratch.
2.  **Tailwind Native**: Use utility classes (`flex gap-4`) over custom CSS.
3.  **Responsiveness**: Design Mobile-First (`w-full md:w-1/2`).
4.  **Dark Mode**: Ensure all colors use semantic variables (`bg-background` not `bg-white`) to support dark mode automatically.

## 4. 21st.dev Usage
When generating components with 21st.dev:
-   Be specific about the **vibe** (e.g., "minimalist", "brutalist", "corporate").
-   Mention required **interactivity** (e.g., "with a framer motion reveal").
-   Ask for **responsive** designs.
