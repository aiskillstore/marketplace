---
name: DevOps & Quality
description: Code quality standards, linting rules, and CI/CD principles.
---

# DevOps & Code Quality

## Linting & Formatting
- **Tool**: ESLint (`npm run lint`).
- **Config**: `eslint.config.mjs` / `next.config.ts`.
- **Rule**: strict type checking is enabled in `tsconfig.json`.

## Version Control
- **Branching**: Feature branch workflow (main <- feature/xyz).
- **Commit Messages**: Semantic commits preferred (e.g., `feat: add chatbot`, `fix: header overflow`).

## Continuous Integration (CI)
(Future Implementation)
- **GitHub Actions**: Recommended for running `npm run lint` and `npm run build` on every PR.
- **Testing**:
  - Unit: Jest (for utility logic).
  - E2E: Playwright (for auth flows).

## Secrets Management
- **Local**: `.env` file (never committed).
- **Production**: Vercel Environment Variables.
