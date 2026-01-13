---
name: css-colors
description: Instructions on how to add new colors for CSS rules
---
When adding new colors for CSS rules, follow these guidelines to ensure consistency and maintainability:
- If possible use Material UI color palette which is derived from MUI theme in frontend/src/theme/theme.ts
- Do not use direct color codes in component code but instead refer to the theme colors
- If a new color is needed, add it to the theme file's customColors section
