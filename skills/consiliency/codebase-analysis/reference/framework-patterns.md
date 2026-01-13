# Framework Entry Points Reference

Complete reference for entry points and patterns by framework/stack.

## JavaScript / TypeScript

### Node.js (Vanilla)

| Entry Point | Purpose |
|-------------|---------|
| `index.js` / `index.ts` | Main module |
| `server.js` / `server.ts` | HTTP server |
| `app.js` / `app.ts` | Application setup |
| `bin/*` | CLI executables |

Config: `package.json` (main, bin, module, exports)

### Express.js

| Entry Point | Purpose |
|-------------|---------|
| `app.js` | Express app setup |
| `server.js` | HTTP server with app |
| `routes/*.js` | Route definitions |
| `middleware/*.js` | Middleware functions |

Pattern: Middleware pipeline

### NestJS

| Entry Point | Purpose |
|-------------|---------|
| `src/main.ts` | Bootstrap |
| `src/app.module.ts` | Root module |
| `src/*/*.controller.ts` | Request handlers |
| `src/*/*.service.ts` | Business logic |

Pattern: Modular + DI

### React (CRA)

| Entry Point | Purpose |
|-------------|---------|
| `src/index.tsx` | ReactDOM render |
| `src/App.tsx` | Root component |
| `src/components/` | UI components |

Pattern: Component-based

### Next.js (Pages Router)

| Entry Point | Purpose |
|-------------|---------|
| `pages/_app.tsx` | App wrapper |
| `pages/_document.tsx` | HTML document |
| `pages/*.tsx` | Page routes |
| `pages/api/*.ts` | API routes |

Pattern: File-based routing

### Next.js (App Router)

| Entry Point | Purpose |
|-------------|---------|
| `app/layout.tsx` | Root layout |
| `app/page.tsx` | Home page |
| `app/*/page.tsx` | Page routes |
| `app/api/*/route.ts` | API routes |

Pattern: File-based routing + RSC

## Python

### FastAPI

| Entry Point | Purpose |
|-------------|---------|
| `main.py` / `app.py` | FastAPI instance |
| `routers/*.py` | Route definitions |
| `models/*.py` | Pydantic models |
| `services/*.py` | Business logic |

Pattern: Router-based

### Django

| Entry Point | Purpose |
|-------------|---------|
| `manage.py` | CLI entry |
| `project/settings.py` | Configuration |
| `project/urls.py` | URL routing |
| `app/views.py` | Request handlers |
| `app/models.py` | ORM models |

Pattern: MTV (Model-Template-View)

### Flask

| Entry Point | Purpose |
|-------------|---------|
| `app.py` | Flask instance |
| `wsgi.py` | WSGI entry |
| `blueprints/*.py` | Route groups |

Pattern: Blueprint-based

## Go

### Standard Library

| Entry Point | Purpose |
|-------------|---------|
| `main.go` | Main package |
| `cmd/app/main.go` | Multiple binaries |
| `internal/` | Private packages |
| `pkg/` | Public packages |

Pattern: Flat or cmd/ structure

### Gin

| Entry Point | Purpose |
|-------------|---------|
| `main.go` | Gin engine setup |
| `handlers/*.go` | Route handlers |
| `middleware/*.go` | Middleware |

Pattern: Handler-based

## Java

### Spring Boot

| Entry Point | Purpose |
|-------------|---------|
| `*Application.java` | @SpringBootApplication |
| `controller/*.java` | @RestController |
| `service/*.java` | @Service |
| `repository/*.java` | @Repository |

Pattern: Layered + DI

## Rust

### Binary

| Entry Point | Purpose |
|-------------|---------|
| `src/main.rs` | Binary entry |
| `src/lib.rs` | Library entry |

Config: `Cargo.toml`

### Actix Web

| Entry Point | Purpose |
|-------------|---------|
| `src/main.rs` | HttpServer setup |
| `src/handlers/` | Route handlers |
| `src/models/` | Data structures |

Pattern: Handler-based

## Dart / Flutter

### Flutter App

| Entry Point | Purpose |
|-------------|---------|
| `lib/main.dart` | App entry |
| `lib/*` | Widgets and app logic |
| `pubspec.yaml` | Dependencies and assets |

Pattern: Widget tree + declarative UI

### Dart CLI

| Entry Point | Purpose |
|-------------|---------|
| `bin/*.dart` | CLI entry |
| `lib/` | Shared libraries |

Pattern: Package + bin/ entry

## C / C++

### CMake-based

| Entry Point | Purpose |
|-------------|---------|
| `main.c` / `main.cpp` | Application entry |
| `src/main.cpp` | Project entry |
| `CMakeLists.txt` | Build targets |

Pattern: Target-based build graph

### Meson/Bazel

| Entry Point | Purpose |
|-------------|---------|
| `meson.build` | Meson project definition |
| `WORKSPACE` | Bazel workspace |

Pattern: Build definition driven

## Ruby

### Rails

| Entry Point | Purpose |
|-------------|---------|
| `config.ru` | Rack entry |
| `config/routes.rb` | URL routing |
| `app/controllers/` | Request handlers |
| `app/models/` | ActiveRecord models |
| `app/views/` | Templates |

Pattern: MVC + Convention over Configuration

### Sinatra

| Entry Point | Purpose |
|-------------|---------|
| `app.rb` | Sinatra app |
| `config.ru` | Rack entry |

Pattern: DSL-based routing
