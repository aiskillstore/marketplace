# Complete Module Example

This directory demonstrates a properly structured module following DevPrep AI standards.

## Structure

```
example/
├── components/
│   ├── ExampleCard.tsx    # Component with proper patterns
│   └── index.ts           # Barrel exports
├── hooks/
│   ├── useExample.ts      # Hook with return type
│   └── index.ts
├── utils/
│   ├── helpers.ts         # Utility functions
│   └── index.ts
├── types.ts               # Module-specific types
└── README.md
```

## Key Patterns Demonstrated

### 1. Interfaces with I Prefix
See `types.ts` and `ExampleCard.tsx`

### 2. Path Aliases
All imports use `@shared`, `@/types`, etc. No relative paths except within-module.

### 3. Proper Component Structure
- Props interface with I prefix
- Named function export
- React.ReactElement return type
- JSDoc comments

### 4. Hook Pattern
- Return type interface
- Proper hook naming (use prefix)
- State management

### 5. Barrel Exports
All `index.ts` files properly re-export

### 6. Quality Standards
- All files < 180 lines
- No `any` types
- Complexity < 15
- Proper error handling

## Usage in Real Project

This structure can be copied to `frontend/src/modules/<your-module-name>/` and renamed.

**Or use the scaffolder:**
```bash
./.claude/skills/module-scaffolder/scripts/create-module.sh your-module-name
```
