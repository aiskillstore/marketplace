---
name: Project Architecture
description: Overview of the project's tech stack, directory structure, and architectural patterns.
---

# Project Architecture & Tech Stack

## Tech Stack
- **Framework**: Next.js 15 (App Router)
- **Language**: TypeScript
- **Styling**: Tailwind CSS v4, CSS Modules (for specific components)
- **Docs/Content**: Docusaurus (in `textbook/` directory)
- **Auth**: Better Auth (`better-auth`)
- **Database**: PostgreSQL (NeonDB)
- **ORM**: Drizzle ORM
- **UI Components**: Lucide React icons, Custom components

## Directory Structure
- `/app`: Next.js App Router pages and layouts.
- `/components`: Reusable UI components.
  - `/auth`: Authentication related components (forms, etc.).
- `/lib`: Utility functions and shared logic.
  - `auth-client.ts`: Better Auth client configuration.
  - `auth.ts`: Better Auth server configuration.
- `/db`: Database schema and connection logic.
- `/drizzle`: Migrations.
- `/textbook`: Docusaurus instance for documentation/content.
  - `/src`: Docusaurus source files.

## Key Patterns
- **Hybrid App**: Combines a Next.js web app (marketing, auth, dashboard) with a Docusaurus documentation site.
- **Auth Integration**: Shared authentication state between Next.js and Docusaurus via cookies/sessions (handled by `AuthBar`).
- **Styling**: Global Tailwind styles in `app/globals.css`. Docusaurus has its own theme in `textbook/src/css/custom.css`.

## Development
- Run root app: `npm run dev:root`
- Run docs app: `npm run dev:docs`
- Run both: `npm run dev`
