# Framework Recognition Guide

Quick reference for identifying frameworks and their conventions.

## JavaScript/TypeScript Frameworks

### React
**Files:** `package.json` with `react` dependency, `.jsx/.tsx` files
**Patterns:** `useState`, `useEffect`, JSX syntax, component functions
**Structure:** `components/`, `hooks/`, `context/`
**Key Files:** `App.tsx`, `index.tsx`

### Next.js
**Files:** `next.config.js`, `pages/` or `app/` directory
**Patterns:** `getServerSideProps`, `getStaticProps`, App Router, Server Components
**Structure:** `pages/` (old) or `app/` (new), `public/`, `api/`
**Key Files:** `_app.tsx`, `layout.tsx`, `page.tsx`

### Vue.js
**Files:** `package.json` with `vue`, `.vue` files
**Patterns:** `<template>`, `<script>`, `<style>`, Options API or Composition API
**Structure:** `components/`, `views/`, `router/`, `store/`
**Key Files:** `App.vue`, `main.js`

### Express.js
**Files:** `package.json` with `express`
**Patterns:** `app.get()`, `app.post()`, middleware functions
**Structure:** `routes/`, `middleware/`, `controllers/`
**Key Files:** `server.js`, `app.js`

## Python Frameworks

### Django
**Files:** `manage.py`, `settings.py`, `urls.py`
**Patterns:** Models, Views, Templates, ORM
**Structure:** `app/models.py`, `app/views.py`, `templates/`
**Key Files:** `settings.py`, `urls.py`, `wsgi.py`

### Flask
**Files:** `app.py`, `requirements.txt` with `flask`
**Patterns:** `@app.route()` decorators
**Structure:** `templates/`, `static/`, blueprints
**Key Files:** `app.py`, `config.py`

### FastAPI
**Files:** `main.py`, `requirements.txt` with `fastapi`
**Patterns:** Type hints, async/await, `@app.get()` decorators
**Structure:** `routers/`, `models/`, `schemas/`
**Key Files:** `main.py`, `dependencies.py`

## Other Languages

### Ruby on Rails
**Files:** `Gemfile`, `config/application.rb`
**Structure:** `app/models/`, `app/views/`, `app/controllers/`
**Conventions:** CoC (Convention over Configuration), ActiveRecord

### Go (Various)
**Gin:** `gin.Default()`, `router.GET()`
**Echo:** `e := echo.New()`
**Chi:** `chi.NewRouter()`

---

*Part of research-agent/investigating-codebases skill*
