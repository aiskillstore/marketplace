# Framework-Specific Configuration Guide

Comprehensive configuration options for each supported framework, comparable to WebStorm/PyCharm project wizards.

## Frontend Frameworks

### React (with Vite)

#### Recommended Stack
```
Build Tool:     Vite (fast HMR, ESM-native)
Language:       TypeScript (strict mode)
Styling:        Tailwind CSS
State:          Zustand or TanStack Query
Routing:        React Router v6 or TanStack Router
Forms:          React Hook Form + Zod
Testing:        Vitest + React Testing Library
```

#### Project Structure
```
my-react-app/
├── src/
│   ├── components/
│   │   ├── ui/              # Reusable UI (Button, Card, Modal)
│   │   └── features/        # Feature-specific components
│   ├── hooks/               # Custom React hooks
│   ├── lib/                 # Utilities, API clients
│   ├── stores/              # State management
│   ├── types/               # TypeScript types
│   ├── styles/              # Global styles
│   ├── App.tsx
│   └── main.tsx
├── public/
├── tests/
│   ├── unit/
│   └── e2e/
├── .eslintrc.json
├── .prettierrc
├── tailwind.config.js
├── tsconfig.json
├── vite.config.ts
└── package.json
```

#### Key Configuration Files

**vite.config.ts**
```typescript
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import path from 'path';

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
  server: {
    port: 3000,
  },
});
```

**tsconfig.json**
```json
{
  "compilerOptions": {
    "target": "ES2022",
    "lib": ["DOM", "DOM.Iterable", "ES2022"],
    "module": "ESNext",
    "moduleResolution": "bundler",
    "jsx": "react-jsx",
    "strict": true,
    "noUnusedLocals": true,
    "noUnusedParameters": true,
    "noFallthroughCasesInSwitch": true,
    "baseUrl": ".",
    "paths": {
      "@/*": ["./src/*"]
    }
  },
  "include": ["src"]
}
```

#### State Management Options

| Library | Best For | Bundle Size |
|---------|----------|-------------|
| Zustand | Simple global state | ~1KB |
| Jotai | Atomic state | ~2KB |
| Redux Toolkit | Complex apps, time-travel | ~11KB |
| TanStack Query | Server state | ~12KB |

#### Data Fetching Patterns

```typescript
// TanStack Query (recommended)
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';

export function useUsers() {
  return useQuery({
    queryKey: ['users'],
    queryFn: () => fetch('/api/users').then(r => r.json()),
    staleTime: 5 * 60 * 1000, // 5 minutes
  });
}

export function useCreateUser() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (user: User) =>
      fetch('/api/users', { method: 'POST', body: JSON.stringify(user) }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['users'] });
    },
  });
}
```

---

### Next.js

#### Recommended Stack
```
Version:        14+ with App Router
Language:       TypeScript (strict)
Styling:        Tailwind CSS
Database:       Prisma or Drizzle
Auth:           NextAuth.js v5 (Auth.js)
Validation:     Zod
Testing:        Vitest + Playwright
```

#### Project Structure (App Router)
```
my-nextjs-app/
├── src/
│   ├── app/
│   │   ├── (auth)/
│   │   │   ├── login/page.tsx
│   │   │   └── register/page.tsx
│   │   ├── (dashboard)/
│   │   │   └── dashboard/page.tsx
│   │   ├── api/
│   │   │   ├── auth/[...nextauth]/route.ts
│   │   │   └── users/route.ts
│   │   ├── layout.tsx
│   │   ├── page.tsx
│   │   └── globals.css
│   ├── components/
│   │   ├── ui/
│   │   └── features/
│   ├── lib/
│   │   ├── auth.ts
│   │   ├── db.ts
│   │   └── utils.ts
│   ├── hooks/
│   └── types/
├── prisma/
│   ├── schema.prisma
│   └── migrations/
├── public/
├── tests/
├── next.config.js
├── tailwind.config.ts
└── package.json
```

#### Server Components vs Client Components

```typescript
// Server Component (default) - runs on server
// app/users/page.tsx
import { prisma } from '@/lib/db';

export default async function UsersPage() {
  const users = await prisma.user.findMany();
  return <UserList users={users} />;
}

// Client Component - runs on client
// components/features/UserForm.tsx
'use client';

import { useState } from 'react';

export function UserForm() {
  const [name, setName] = useState('');
  // Client-side interactivity
}
```

#### Server Actions (Next.js 14+)

```typescript
// app/actions.ts
'use server';

import { prisma } from '@/lib/db';
import { revalidatePath } from 'next/cache';

export async function createUser(formData: FormData) {
  const name = formData.get('name') as string;

  await prisma.user.create({
    data: { name },
  });

  revalidatePath('/users');
}
```

---

### Vue 3

#### Recommended Stack
```
Build Tool:     Vite
Language:       TypeScript
API Style:      Composition API
State:          Pinia
Routing:        Vue Router 4
Styling:        Tailwind CSS or UnoCSS
Testing:        Vitest + Vue Test Utils
```

#### Project Structure
```
my-vue-app/
├── src/
│   ├── components/
│   │   ├── common/
│   │   └── features/
│   ├── composables/         # Composition API utilities
│   ├── views/               # Page components
│   ├── stores/              # Pinia stores
│   ├── router/
│   ├── types/
│   ├── assets/
│   ├── App.vue
│   └── main.ts
├── public/
├── tests/
├── vite.config.ts
├── tsconfig.json
└── package.json
```

#### Composition API Patterns

```vue
<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import { useUserStore } from '@/stores/user';

// Reactive state
const count = ref(0);
const doubled = computed(() => count.value * 2);

// Store
const userStore = useUserStore();

// Lifecycle
onMounted(() => {
  userStore.fetchUsers();
});
</script>

<template>
  <div>
    <p>Count: {{ count }}</p>
    <p>Doubled: {{ doubled }}</p>
  </div>
</template>
```

#### Pinia Store Pattern

```typescript
// stores/user.ts
import { defineStore } from 'pinia';

interface User {
  id: string;
  name: string;
}

export const useUserStore = defineStore('user', {
  state: () => ({
    users: [] as User[],
    loading: false,
  }),

  getters: {
    userCount: (state) => state.users.length,
  },

  actions: {
    async fetchUsers() {
      this.loading = true;
      try {
        const response = await fetch('/api/users');
        this.users = await response.json();
      } finally {
        this.loading = false;
      }
    },
  },
});
```

---

### Nuxt 3

#### Recommended Stack
```
Version:        3.x
Auto-imports:   Enabled
Styling:        @nuxtjs/tailwindcss
State:          Pinia (@pinia/nuxt)
API:            Nitro server routes
```

#### Project Structure
```
my-nuxt-app/
├── assets/
├── components/
├── composables/
├── layouts/
├── middleware/
├── pages/
├── plugins/
├── public/
├── server/
│   ├── api/
│   └── middleware/
├── stores/
├── app.vue
├── nuxt.config.ts
└── package.json
```

#### Auto-imports

Nuxt auto-imports Vue functions and composables:

```vue
<script setup lang="ts">
// No imports needed!
const count = ref(0);
const route = useRoute();
const { data } = await useFetch('/api/users');
</script>
```

---

### SvelteKit

#### Recommended Stack
```
Version:        2.x
Language:       TypeScript
Styling:        Tailwind CSS
State:          Svelte stores
```

#### Project Structure
```
my-sveltekit-app/
├── src/
│   ├── lib/
│   │   ├── components/
│   │   ├── stores/
│   │   └── utils/
│   ├── routes/
│   │   ├── +layout.svelte
│   │   ├── +page.svelte
│   │   └── api/
│   └── app.html
├── static/
├── tests/
├── svelte.config.js
├── vite.config.ts
└── package.json
```

#### SvelteKit Routing

```
routes/
├── +page.svelte              → /
├── +layout.svelte            → Layout for all pages
├── about/+page.svelte        → /about
├── blog/
│   ├── +page.svelte          → /blog
│   └── [slug]/+page.svelte   → /blog/:slug
└── api/
    └── users/+server.ts      → /api/users
```

---

## Backend Frameworks

### FastAPI

#### Recommended Stack
```
Python:         3.12+
Async:          Full async/await
Database:       PostgreSQL + asyncpg
ORM:            SQLAlchemy 2.0 (async)
Migrations:     Alembic
Validation:     Pydantic v2
Auth:           python-jose (JWT)
Testing:        pytest-asyncio + httpx
```

#### Project Structure (Large-Scale)
```
my-fastapi-app/
├── app/
│   ├── api/
│   │   ├── v1/
│   │   │   ├── endpoints/
│   │   │   │   ├── users.py
│   │   │   │   └── items.py
│   │   │   └── __init__.py
│   │   └── deps.py          # Dependencies
│   ├── core/
│   │   ├── config.py        # Pydantic Settings
│   │   ├── security.py      # JWT, hashing
│   │   └── exceptions.py
│   ├── db/
│   │   ├── session.py       # Database session
│   │   ├── base.py          # SQLAlchemy Base
│   │   └── models/
│   ├── schemas/             # Pydantic models
│   ├── services/            # Business logic
│   ├── crud/                # Database operations
│   └── main.py
├── alembic/
│   ├── versions/
│   └── env.py
├── tests/
│   ├── unit/
│   ├── integration/
│   └── conftest.py
├── alembic.ini
├── pyproject.toml
├── requirements.txt
└── Dockerfile
```

#### Configuration with Pydantic Settings

```python
# app/core/config.py
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
    )

    # App
    PROJECT_NAME: str = "My API"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    DEBUG: bool = False

    # Database
    DATABASE_URL: str

    # Security
    SECRET_KEY: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # CORS
    ALLOWED_ORIGINS: list[str] = ["http://localhost:3000"]


settings = Settings()
```

#### Async SQLAlchemy 2.0

```python
# app/db/session.py
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import settings

engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
    future=True,
)

async_session = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_db() -> AsyncSession:
    async with async_session() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
```

#### Dependency Injection Pattern

```python
# app/api/deps.py
from typing import Annotated
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.core.security import decode_token
from app.crud import user as user_crud

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")

async def get_current_user(
    db: Annotated[AsyncSession, Depends(get_db)],
    token: Annotated[str, Depends(oauth2_scheme)],
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
    )

    payload = decode_token(token)
    if payload is None:
        raise credentials_exception

    user = await user_crud.get_by_id(db, id=payload.sub)
    if user is None:
        raise credentials_exception

    return user
```

---

### Django

#### Recommended Stack
```
Version:        5.x
API:            Django REST Framework
Database:       PostgreSQL
Auth:           Django Allauth (social)
Background:     Celery + Redis
Testing:        pytest-django
```

#### Project Structure
```
my-django-project/
├── config/                  # Project settings
│   ├── settings/
│   │   ├── base.py
│   │   ├── dev.py
│   │   └── prod.py
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
├── apps/
│   ├── core/               # Shared utilities
│   ├── users/
│   │   ├── models.py
│   │   ├── views.py
│   │   ├── serializers.py
│   │   ├── urls.py
│   │   └── tests/
│   └── api/
├── static/
├── media/
├── templates/
├── requirements/
│   ├── base.txt
│   ├── dev.txt
│   └── prod.txt
├── manage.py
└── docker-compose.yml
```

#### Custom User Model (Always Do This)

```python
# apps/users/models.py
from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    email = models.EmailField(unique=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']
```

```python
# config/settings/base.py
AUTH_USER_MODEL = 'users.User'
```

---

### Express.js

#### Recommended Stack
```
Language:       TypeScript
Runtime:        Node.js 22+
ORM:            Prisma or Drizzle
Validation:     Zod
Auth:           Passport.js or custom JWT
Testing:        Vitest + Supertest
```

#### Project Structure
```
my-express-api/
├── src/
│   ├── routes/
│   │   ├── index.ts
│   │   ├── users.ts
│   │   └── auth.ts
│   ├── controllers/
│   ├── middleware/
│   │   ├── auth.ts
│   │   ├── validate.ts
│   │   └── errorHandler.ts
│   ├── services/
│   ├── models/
│   ├── schemas/            # Zod schemas
│   ├── utils/
│   ├── config/
│   ├── app.ts
│   └── index.ts
├── prisma/
├── tests/
├── tsconfig.json
└── package.json
```

#### Middleware Pattern

```typescript
// src/middleware/validate.ts
import { Request, Response, NextFunction } from 'express';
import { ZodSchema } from 'zod';

export const validate = (schema: ZodSchema) => {
  return (req: Request, res: Response, next: NextFunction) => {
    try {
      schema.parse({
        body: req.body,
        query: req.query,
        params: req.params,
      });
      next();
    } catch (error) {
      res.status(400).json({ error: 'Validation failed', details: error });
    }
  };
};
```

---

### NestJS

#### Recommended Stack
```
Language:       TypeScript
ORM:            Prisma or TypeORM
Validation:     class-validator
Auth:           @nestjs/passport
Testing:        Jest
```

#### Project Structure
```
my-nestjs-app/
├── src/
│   ├── modules/
│   │   ├── users/
│   │   │   ├── users.module.ts
│   │   │   ├── users.controller.ts
│   │   │   ├── users.service.ts
│   │   │   ├── dto/
│   │   │   └── entities/
│   │   └── auth/
│   ├── common/
│   │   ├── decorators/
│   │   ├── filters/
│   │   ├── guards/
│   │   └── interceptors/
│   ├── config/
│   ├── app.module.ts
│   └── main.ts
├── test/
├── nest-cli.json
├── tsconfig.json
└── package.json
```

---

## Database & ORM Comparison

### JavaScript/TypeScript ORMs

| ORM | Type Safety | Migrations | Learning Curve | Best For |
|-----|-------------|------------|----------------|----------|
| Prisma | Excellent | Built-in | Low | Most projects |
| Drizzle | Excellent | Built-in | Medium | Performance-critical |
| TypeORM | Good | Built-in | High | NestJS, complex queries |
| Sequelize | Fair | Built-in | Medium | Legacy projects |

### Python ORMs

| ORM | Async Support | Type Hints | Learning Curve | Best For |
|-----|---------------|------------|----------------|----------|
| SQLAlchemy 2.0 | Full | Excellent | Medium | Most projects |
| SQLModel | Full | Excellent | Low | FastAPI |
| Tortoise | Full | Good | Low | Simple async apps |
| Django ORM | Limited | Good | Low | Django projects |

---

## Testing Strategies

### Frontend Testing Pyramid
```
E2E Tests (Playwright/Cypress)     [10%]
Integration Tests                   [20%]
Unit Tests (Vitest/Jest)           [70%]
```

### Backend Testing Pyramid
```
E2E/API Tests                      [10%]
Integration Tests                   [30%]
Unit Tests                         [60%]
```

### Example Test Setup (Vitest + React)

```typescript
// vitest.config.ts
import { defineConfig } from 'vitest/config';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
  test: {
    environment: 'jsdom',
    globals: true,
    setupFiles: './tests/setup.ts',
    coverage: {
      provider: 'v8',
      reporter: ['text', 'html'],
      exclude: ['node_modules/', 'tests/'],
    },
  },
});
```

```typescript
// tests/setup.ts
import '@testing-library/jest-dom';
import { cleanup } from '@testing-library/react';
import { afterEach } from 'vitest';

afterEach(() => {
  cleanup();
});
```
