#!/usr/bin/env python3
"""
Project scaffolding script - IDE-grade project creation comparable to WebStorm/PyCharm.
Supports comprehensive configuration options for modern development workflows.
"""

import os
import sys
import json
import shutil
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from enum import Enum


class Language(Enum):
    TYPESCRIPT = "typescript"
    JAVASCRIPT = "javascript"
    PYTHON = "python"


class PackageManager(Enum):
    NPM = "npm"
    YARN = "yarn"
    PNPM = "pnpm"
    BUN = "bun"
    PIP = "pip"
    POETRY = "poetry"
    PIPENV = "pipenv"
    CONDA = "conda"


class CSSFramework(Enum):
    TAILWIND = "tailwind"
    CSS_MODULES = "css-modules"
    STYLED_COMPONENTS = "styled-components"
    EMOTION = "emotion"
    SCSS = "scss"
    NONE = "none"


class Database(Enum):
    NONE = "none"
    SQLITE = "sqlite"
    POSTGRESQL = "postgresql"
    MYSQL = "mysql"
    MONGODB = "mongodb"


class ORM(Enum):
    NONE = "none"
    PRISMA = "prisma"
    DRIZZLE = "drizzle"
    TYPEORM = "typeorm"
    SEQUELIZE = "sequelize"
    SQLALCHEMY = "sqlalchemy"
    SQLMODEL = "sqlmodel"
    TORTOISE = "tortoise"
    MONGOOSE = "mongoose"


@dataclass
class ProjectConfig:
    """Configuration for a new project."""
    name: str
    project_type: str
    language: Language = Language.TYPESCRIPT
    description: str = ""
    author: str = ""
    license: str = "MIT"
    version: str = "0.1.0"

    # SDK/Runtime
    node_version: str = "22"
    python_version: str = "3.12"
    package_manager: PackageManager = PackageManager.NPM

    # Framework options
    css_framework: CSSFramework = CSSFramework.TAILWIND
    database: Database = Database.NONE
    orm: ORM = ORM.NONE

    # Features
    typescript_strict: bool = True
    eslint: bool = True
    prettier: bool = True
    testing: bool = True
    docker: bool = False
    github_actions: bool = False

    # Python-specific
    type_hints: bool = True
    ruff: bool = True
    mypy: bool = True
    pytest: bool = True

    # Additional features
    features: List[str] = field(default_factory=list)


class ProjectScaffolder:
    """Main scaffolding engine for creating projects with IDE-grade configuration."""

    def __init__(self, base_path: Path = Path.cwd()):
        self.base_path = base_path

    def create_project(self, config: ProjectConfig) -> Path:
        """Create a new project from configuration."""
        project_path = self.base_path / config.name

        if project_path.exists():
            raise FileExistsError(f"Project {config.name} already exists")

        # Map project types to creation methods
        creators = {
            # Static Sites
            "html": self._create_html,
            # Frontend
            "react": self._create_react,
            "nextjs": self._create_nextjs,
            "vue": self._create_vue,
            "nuxt": self._create_nuxt,
            "svelte": self._create_svelte,
            "angular": self._create_angular,
            # Backend
            "express": self._create_express,
            "nestjs": self._create_nestjs,
            "fastapi": self._create_fastapi,
            "django": self._create_django,
            "flask": self._create_flask,
            # Libraries
            "python": self._create_python,
            "typescript": self._create_typescript_lib,
            "cli": self._create_cli,
            "electron": self._create_electron,
            "monorepo": self._create_monorepo,
        }

        if config.project_type not in creators:
            raise ValueError(f"Unknown project type: {config.project_type}")

        project_path.mkdir(parents=True)
        creators[config.project_type](project_path, config)

        return project_path

    # =========================================================================
    # Frontend Projects
    # =========================================================================

    def _create_react(self, path: Path, config: ProjectConfig):
        """Create a React project with Vite."""
        # Create directory structure
        self._create_dirs(path, [
            "src/components/ui",
            "src/components/features",
            "src/hooks",
            "src/lib",
            "src/types",
            "src/styles",
            "public",
            "tests/unit",
            "tests/e2e",
        ])

        # Package.json
        ext = "tsx" if config.language == Language.TYPESCRIPT else "jsx"
        deps = {
            "react": "^18.2.0",
            "react-dom": "^18.2.0",
        }
        dev_deps = {
            "@vitejs/plugin-react": "^4.2.0",
            "vite": "^5.0.0",
        }

        if config.language == Language.TYPESCRIPT:
            dev_deps.update({
                "typescript": "^5.3.0",
                "@types/react": "^18.2.0",
                "@types/react-dom": "^18.2.0",
            })

        if config.css_framework == CSSFramework.TAILWIND:
            dev_deps.update({
                "tailwindcss": "^3.4.0",
                "postcss": "^8.4.0",
                "autoprefixer": "^10.4.0",
            })

        if config.eslint:
            dev_deps.update({
                "eslint": "^8.56.0",
                "eslint-plugin-react": "^7.33.0",
                "eslint-plugin-react-hooks": "^4.6.0",
            })
            if config.language == Language.TYPESCRIPT:
                dev_deps["@typescript-eslint/eslint-plugin"] = "^6.0.0"
                dev_deps["@typescript-eslint/parser"] = "^6.0.0"

        if config.prettier:
            dev_deps["prettier"] = "^3.1.0"

        if config.testing:
            dev_deps.update({
                "vitest": "^1.0.0",
                "@testing-library/react": "^14.0.0",
                "@testing-library/jest-dom": "^6.0.0",
            })

        # State management based on features
        if "zustand" in config.features:
            deps["zustand"] = "^4.4.0"
        if "redux" in config.features:
            deps["@reduxjs/toolkit"] = "^2.0.0"
            deps["react-redux"] = "^9.0.0"

        # Data fetching
        if "tanstack-query" in config.features:
            deps["@tanstack/react-query"] = "^5.0.0"

        # Routing
        if "react-router" in config.features:
            deps["react-router-dom"] = "^6.20.0"

        package_json = self._create_package_json(config, deps, dev_deps, {
            "dev": "vite",
            "build": "vite build",
            "preview": "vite preview",
            "lint": "eslint src --ext .ts,.tsx" if config.eslint else None,
            "format": "prettier --write src" if config.prettier else None,
            "test": "vitest" if config.testing else None,
            "test:coverage": "vitest --coverage" if config.testing else None,
        })
        self._write_json(path / "package.json", package_json)

        # Vite config
        vite_config = self._generate_vite_config(config)
        self._write_file(path / "vite.config.ts", vite_config)

        # TypeScript config
        if config.language == Language.TYPESCRIPT:
            self._write_json(path / "tsconfig.json", self._create_tsconfig(config, "react"))

        # Tailwind config
        if config.css_framework == CSSFramework.TAILWIND:
            self._create_tailwind_config(path, config)

        # ESLint config
        if config.eslint:
            self._create_eslint_config(path, config, "react")

        # Prettier config
        if config.prettier:
            self._create_prettier_config(path)

        # Source files
        self._write_file(path / f"src/main.{ext}", self._react_main(config))
        self._write_file(path / f"src/App.{ext}", self._react_app(config))
        self._write_file(path / "src/styles/globals.css", self._css_globals(config))
        self._write_file(path / "index.html", self._react_index_html(config))

        # Vitest config
        if config.testing:
            self._write_file(path / "vitest.config.ts", self._vitest_config())
            self._write_file(path / "tests/setup.ts", self._vitest_setup())

        # Common files
        self._create_common_files(path, config)

    def _create_nextjs(self, path: Path, config: ProjectConfig):
        """Create a Next.js project with App Router."""
        # Directory structure
        self._create_dirs(path, [
            "src/app/(auth)/login",
            "src/app/(auth)/register",
            "src/app/api",
            "src/components/ui",
            "src/components/features",
            "src/lib",
            "src/hooks",
            "src/types",
            "public",
            "tests/unit",
            "tests/e2e",
        ])

        if config.orm == ORM.PRISMA:
            self._create_dirs(path, ["prisma"])

        deps = {
            "next": "^14.0.0",
            "react": "^18.2.0",
            "react-dom": "^18.2.0",
        }
        dev_deps = {}

        if config.language == Language.TYPESCRIPT:
            dev_deps.update({
                "typescript": "^5.3.0",
                "@types/node": "^22.0.0",
                "@types/react": "^18.2.0",
                "@types/react-dom": "^18.2.0",
            })

        if config.css_framework == CSSFramework.TAILWIND:
            dev_deps.update({
                "tailwindcss": "^3.4.0",
                "postcss": "^8.4.0",
                "autoprefixer": "^10.4.0",
            })

        if config.eslint:
            dev_deps.update({
                "eslint": "^8.56.0",
                "eslint-config-next": "^14.0.0",
            })

        if config.prettier:
            dev_deps["prettier"] = "^3.1.0"
            dev_deps["prettier-plugin-tailwindcss"] = "^0.5.0"

        if config.testing:
            dev_deps.update({
                "vitest": "^1.0.0",
                "@testing-library/react": "^14.0.0",
                "@vitejs/plugin-react": "^4.2.0",
            })

        # ORM
        if config.orm == ORM.PRISMA:
            deps["@prisma/client"] = "^5.7.0"
            dev_deps["prisma"] = "^5.7.0"

        # Auth
        if "nextauth" in config.features:
            deps["next-auth"] = "^4.24.0"

        package_json = self._create_package_json(config, deps, dev_deps, {
            "dev": "next dev",
            "build": "next build",
            "start": "next start",
            "lint": "next lint" if config.eslint else None,
            "format": "prettier --write ." if config.prettier else None,
            "test": "vitest" if config.testing else None,
            "db:generate": "prisma generate" if config.orm == ORM.PRISMA else None,
            "db:push": "prisma db push" if config.orm == ORM.PRISMA else None,
            "db:migrate": "prisma migrate dev" if config.orm == ORM.PRISMA else None,
        })
        self._write_json(path / "package.json", package_json)

        # Next.js config
        self._write_file(path / "next.config.js", self._nextjs_config(config))

        # TypeScript config
        if config.language == Language.TYPESCRIPT:
            self._write_json(path / "tsconfig.json", self._create_tsconfig(config, "nextjs"))

        # Tailwind config
        if config.css_framework == CSSFramework.TAILWIND:
            self._create_tailwind_config(path, config, framework="nextjs")

        # ESLint config
        if config.eslint:
            self._write_json(path / ".eslintrc.json", {
                "extends": ["next/core-web-vitals"],
                "rules": {}
            })

        # Prettier config
        if config.prettier:
            self._create_prettier_config(path, plugins=["prettier-plugin-tailwindcss"])

        # App files
        ext = "tsx" if config.language == Language.TYPESCRIPT else "jsx"
        self._write_file(path / f"src/app/layout.{ext}", self._nextjs_layout(config))
        self._write_file(path / f"src/app/page.{ext}", self._nextjs_page(config))
        self._write_file(path / "src/app/globals.css", self._css_globals(config))

        # Prisma schema
        if config.orm == ORM.PRISMA:
            self._write_file(path / "prisma/schema.prisma", self._prisma_schema(config))
            self._write_file(path / "src/lib/db.ts", self._prisma_client())

        # Lib utilities
        self._write_file(path / "src/lib/utils.ts", self._utils_file())

        # Common files
        self._create_common_files(path, config)

    def _create_vue(self, path: Path, config: ProjectConfig):
        """Create a Vue 3 project with Vite."""
        self._create_dirs(path, [
            "src/components",
            "src/composables",
            "src/views",
            "src/stores",
            "src/assets",
            "src/router",
            "public",
            "tests",
        ])

        deps = {"vue": "^3.4.0"}
        dev_deps = {
            "@vitejs/plugin-vue": "^4.5.0",
            "vite": "^5.0.0",
        }

        if config.language == Language.TYPESCRIPT:
            dev_deps.update({
                "typescript": "^5.3.0",
                "vue-tsc": "^1.8.0",
            })

        if "pinia" in config.features:
            deps["pinia"] = "^2.1.0"

        if "vue-router" in config.features:
            deps["vue-router"] = "^4.2.0"

        if config.css_framework == CSSFramework.TAILWIND:
            dev_deps.update({
                "tailwindcss": "^3.4.0",
                "postcss": "^8.4.0",
                "autoprefixer": "^10.4.0",
            })

        package_json = self._create_package_json(config, deps, dev_deps, {
            "dev": "vite",
            "build": "vite build",
            "preview": "vite preview",
            "type-check": "vue-tsc --noEmit" if config.language == Language.TYPESCRIPT else None,
        })
        self._write_json(path / "package.json", package_json)

        # Vite config
        self._write_file(path / "vite.config.ts", self._vue_vite_config(config))

        # TypeScript config
        if config.language == Language.TYPESCRIPT:
            self._write_json(path / "tsconfig.json", self._create_tsconfig(config, "vue"))

        # Source files
        ext = "ts" if config.language == Language.TYPESCRIPT else "js"
        self._write_file(path / f"src/main.{ext}", self._vue_main(config))
        self._write_file(path / "src/App.vue", self._vue_app(config))
        self._write_file(path / "index.html", self._vue_index_html(config))

        if config.css_framework == CSSFramework.TAILWIND:
            self._create_tailwind_config(path, config)
            self._write_file(path / "src/assets/main.css", self._css_globals(config))

        self._create_common_files(path, config)

    def _create_nuxt(self, path: Path, config: ProjectConfig):
        """Create a Nuxt 3 project."""
        self._create_dirs(path, [
            "components",
            "composables",
            "layouts",
            "pages",
            "public",
            "server/api",
            "stores",
        ])

        deps = {}
        dev_deps = {"nuxt": "^3.9.0"}

        if config.css_framework == CSSFramework.TAILWIND:
            dev_deps["@nuxtjs/tailwindcss"] = "^6.10.0"

        if "pinia" in config.features:
            deps["@pinia/nuxt"] = "^0.5.0"
            deps["pinia"] = "^2.1.0"

        package_json = self._create_package_json(config, deps, dev_deps, {
            "dev": "nuxt dev",
            "build": "nuxt build",
            "generate": "nuxt generate",
            "preview": "nuxt preview",
        })
        self._write_json(path / "package.json", package_json)

        # Nuxt config
        self._write_file(path / "nuxt.config.ts", self._nuxt_config(config))

        # Pages
        self._write_file(path / "pages/index.vue", self._nuxt_index_page(config))
        self._write_file(path / "app.vue", self._nuxt_app(config))

        self._create_common_files(path, config)

    def _create_svelte(self, path: Path, config: ProjectConfig):
        """Create a SvelteKit project."""
        self._create_dirs(path, [
            "src/lib",
            "src/lib/components",
            "src/routes",
            "static",
            "tests",
        ])

        deps = {}
        dev_deps = {
            "@sveltejs/adapter-auto": "^3.0.0",
            "@sveltejs/kit": "^2.0.0",
            "svelte": "^4.2.0",
            "vite": "^5.0.0",
        }

        if config.language == Language.TYPESCRIPT:
            dev_deps.update({
                "typescript": "^5.3.0",
                "svelte-check": "^3.6.0",
                "tslib": "^2.6.0",
            })

        if config.css_framework == CSSFramework.TAILWIND:
            dev_deps.update({
                "tailwindcss": "^3.4.0",
                "postcss": "^8.4.0",
                "autoprefixer": "^10.4.0",
            })

        package_json = self._create_package_json(config, deps, dev_deps, {
            "dev": "vite dev",
            "build": "vite build",
            "preview": "vite preview",
            "check": "svelte-kit sync && svelte-check --tsconfig ./tsconfig.json",
        })
        self._write_json(path / "package.json", package_json)

        # SvelteKit config
        self._write_file(path / "svelte.config.js", self._svelte_config(config))
        self._write_file(path / "vite.config.ts", self._svelte_vite_config(config))

        # Routes
        ext = "ts" if config.language == Language.TYPESCRIPT else "js"
        self._write_file(path / f"src/routes/+page.svelte", self._svelte_page(config))
        self._write_file(path / f"src/routes/+layout.svelte", self._svelte_layout(config))

        if config.css_framework == CSSFramework.TAILWIND:
            self._create_tailwind_config(path, config)
            self._write_file(path / "src/app.css", self._css_globals(config))

        self._write_file(path / "src/app.html", self._svelte_app_html(config))

        self._create_common_files(path, config)

    def _create_angular(self, path: Path, config: ProjectConfig):
        """Create an Angular project structure (recommend using ng new)."""
        # For Angular, we primarily recommend using the CLI
        self._create_dirs(path, [
            "src/app/components",
            "src/app/services",
            "src/app/models",
            "src/app/pages",
            "src/assets",
            "src/environments",
        ])

        deps = {
            "@angular/core": "^17.0.0",
            "@angular/common": "^17.0.0",
            "@angular/compiler": "^17.0.0",
            "@angular/platform-browser": "^17.0.0",
            "@angular/platform-browser-dynamic": "^17.0.0",
            "@angular/router": "^17.0.0",
            "rxjs": "^7.8.0",
            "zone.js": "^0.14.0",
        }
        dev_deps = {
            "@angular/cli": "^17.0.0",
            "@angular/compiler-cli": "^17.0.0",
            "typescript": "^5.2.0",
        }

        package_json = self._create_package_json(config, deps, dev_deps, {
            "ng": "ng",
            "start": "ng serve",
            "build": "ng build",
            "test": "ng test",
        })
        self._write_json(path / "package.json", package_json)

        # Angular config
        self._write_json(path / "angular.json", self._angular_config(config))
        self._write_json(path / "tsconfig.json", self._create_tsconfig(config, "angular"))

        self._create_common_files(path, config)

    # =========================================================================
    # Static Websites
    # =========================================================================

    def _create_html(self, path: Path, config: ProjectConfig):
        """Create a static HTML/CSS website."""
        # Create directory structure
        self._create_dirs(path, [
            "css",
            "js",
            "images",
        ])

        # Main HTML file
        self._write_file(path / "index.html", self._html_index(config))

        # Additional pages
        self._write_file(path / "about.html", self._html_about(config))
        self._write_file(path / "contact.html", self._html_contact(config))

        # CSS files
        self._write_file(path / "css/reset.css", self._css_reset())
        self._write_file(path / "css/style.css", self._css_main(config))

        # JavaScript
        self._write_file(path / "js/main.js", self._js_main())

        # Favicon and robots.txt
        self._write_file(path / "robots.txt", "User-agent: *\nDisallow:\n")

        # Package.json for dev server (optional)
        if config.css_framework == CSSFramework.TAILWIND:
            package_json = {
                "name": config.name,
                "version": config.version,
                "description": config.description or "",
                "scripts": {
                    "dev": "npx tailwindcss -i ./css/style.css -o ./css/output.css --watch",
                    "build": "npx tailwindcss -i ./css/style.css -o ./css/output.css --minify",
                },
                "devDependencies": {
                    "tailwindcss": "^3.4.0"
                }
            }
            self._write_json(path / "package.json", package_json)

            # Create Tailwind config (no PostCSS needed for CLI usage)
            tailwind_config = """/** @type {import('tailwindcss').Config} */
export default {
  content: ['./**/*.html'],
  theme: {
    extend: {},
  },
  plugins: [],
}
"""
            self._write_file(path / "tailwind.config.js", tailwind_config)
        else:
            # Simple package.json for live server
            package_json = {
                "name": config.name,
                "version": config.version,
                "description": config.description or "",
                "scripts": {
                    "dev": "npx live-server",
                },
                "devDependencies": {
                    "live-server": "^1.2.2"
                }
            }
            self._write_json(path / "package.json", package_json)

        # Create basic README
        readme = f"""# {config.name}

{config.description or 'A static HTML/CSS website'}

## Development

Start the development server:

```bash
npm install
npm run dev
```

The site will be available at http://localhost:8080

## Project Structure

```
{config.name}/
├── index.html          # Home page
├── about.html          # About page
├── contact.html        # Contact page
├── css/
│   ├── reset.css       # CSS reset
│   └── style.css       # Main styles
├── js/
│   └── main.js         # Main JavaScript
├── images/             # Image assets
└── robots.txt          # SEO
```

## Features

- Mobile-first responsive design
- BEM naming convention for CSS
- Semantic HTML5
- SEO-ready
{'- Tailwind CSS' if config.css_framework == CSSFramework.TAILWIND else '- Pure CSS'}

## Browser Support

- Chrome (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)

## License

{config.license}
"""
        self._write_file(path / "README.md", readme)

        # .gitignore for HTML projects
        gitignore = """# Dependencies
node_modules/

# Tailwind output
css/output.css

# OS files
.DS_Store
Thumbs.db

# Editor
.vscode/
.idea/
*.sublime-*

# Logs
*.log
"""
        self._write_file(path / ".gitignore", gitignore)

    # =========================================================================
    # Backend Projects
    # =========================================================================

    def _create_express(self, path: Path, config: ProjectConfig):
        """Create an Express.js project."""
        self._create_dirs(path, [
            "src/routes",
            "src/controllers",
            "src/middleware",
            "src/models",
            "src/services",
            "src/utils",
            "src/config",
            "tests",
        ])

        deps = {
            "express": "^4.18.0",
            "cors": "^2.8.0",
            "helmet": "^7.1.0",
            "morgan": "^1.10.0",
            "dotenv": "^16.3.0",
        }
        dev_deps = {}

        if config.language == Language.TYPESCRIPT:
            dev_deps.update({
                "typescript": "^5.3.0",
                "@types/node": "^22.0.0",
                "@types/express": "^4.17.0",
                "@types/cors": "^2.8.0",
                "@types/morgan": "^1.9.0",
                "ts-node": "^10.9.0",
                "tsx": "^4.6.0",
                "nodemon": "^3.0.0",
            })

        if config.orm == ORM.PRISMA:
            deps["@prisma/client"] = "^5.7.0"
            dev_deps["prisma"] = "^5.7.0"
        elif config.orm == ORM.TYPEORM:
            deps["typeorm"] = "^0.3.0"
            deps["reflect-metadata"] = "^0.1.0"
        elif config.orm == ORM.SEQUELIZE:
            deps["sequelize"] = "^6.35.0"

        if config.database == Database.POSTGRESQL:
            deps["pg"] = "^8.11.0"
        elif config.database == Database.MYSQL:
            deps["mysql2"] = "^3.6.0"
        elif config.database == Database.MONGODB:
            deps["mongoose"] = "^8.0.0"

        if "zod" in config.features:
            deps["zod"] = "^3.22.0"

        if "swagger" in config.features:
            deps["swagger-ui-express"] = "^5.0.0"
            deps["swagger-jsdoc"] = "^6.2.0"

        if config.testing:
            dev_deps.update({
                "vitest": "^1.0.0",
                "supertest": "^6.3.0",
                "@types/supertest": "^2.0.0",
            })

        package_json = self._create_package_json(config, deps, dev_deps, {
            "dev": "tsx watch src/index.ts" if config.language == Language.TYPESCRIPT else "nodemon src/index.js",
            "build": "tsc" if config.language == Language.TYPESCRIPT else None,
            "start": "node dist/index.js" if config.language == Language.TYPESCRIPT else "node src/index.js",
            "lint": "eslint src" if config.eslint else None,
            "test": "vitest" if config.testing else None,
        })
        self._write_json(path / "package.json", package_json)

        # TypeScript config
        if config.language == Language.TYPESCRIPT:
            self._write_json(path / "tsconfig.json", self._create_tsconfig(config, "node"))

        # Source files
        ext = "ts" if config.language == Language.TYPESCRIPT else "js"
        self._write_file(path / f"src/index.{ext}", self._express_index(config))
        self._write_file(path / f"src/app.{ext}", self._express_app(config))
        self._write_file(path / f"src/config/index.{ext}", self._express_config(config))
        self._write_file(path / f"src/routes/index.{ext}", self._express_routes(config))
        self._write_file(path / f"src/middleware/errorHandler.{ext}", self._express_error_handler(config))

        self._create_common_files(path, config)

    def _create_nestjs(self, path: Path, config: ProjectConfig):
        """Create a NestJS project structure."""
        self._create_dirs(path, [
            "src/modules",
            "src/common/decorators",
            "src/common/filters",
            "src/common/guards",
            "src/common/interceptors",
            "src/config",
            "test",
        ])

        deps = {
            "@nestjs/common": "^10.0.0",
            "@nestjs/core": "^10.0.0",
            "@nestjs/platform-express": "^10.0.0",
            "reflect-metadata": "^0.1.0",
            "rxjs": "^7.8.0",
        }
        dev_deps = {
            "@nestjs/cli": "^10.0.0",
            "@nestjs/schematics": "^10.0.0",
            "@types/node": "^22.0.0",
            "@types/express": "^4.17.0",
            "typescript": "^5.3.0",
            "ts-node": "^10.9.0",
        }

        if config.testing:
            dev_deps.update({
                "@nestjs/testing": "^10.0.0",
                "jest": "^29.7.0",
                "@types/jest": "^29.5.0",
                "ts-jest": "^29.1.0",
            })

        package_json = self._create_package_json(config, deps, dev_deps, {
            "start": "nest start",
            "start:dev": "nest start --watch",
            "start:debug": "nest start --debug --watch",
            "build": "nest build",
            "test": "jest" if config.testing else None,
            "test:watch": "jest --watch" if config.testing else None,
        })
        self._write_json(path / "package.json", package_json)

        # Nest CLI config
        self._write_json(path / "nest-cli.json", {
            "$schema": "https://json.schemastore.org/nest-cli",
            "collection": "@nestjs/schematics",
            "sourceRoot": "src"
        })

        # TypeScript config
        self._write_json(path / "tsconfig.json", self._create_tsconfig(config, "nestjs"))

        # Source files
        self._write_file(path / "src/main.ts", self._nestjs_main(config))
        self._write_file(path / "src/app.module.ts", self._nestjs_app_module(config))
        self._write_file(path / "src/app.controller.ts", self._nestjs_controller(config))
        self._write_file(path / "src/app.service.ts", self._nestjs_service(config))

        self._create_common_files(path, config)

    def _create_fastapi(self, path: Path, config: ProjectConfig):
        """Create a FastAPI project."""
        # Determine structure based on features
        if "large-scale" in config.features:
            self._create_dirs(path, [
                "app/api/v1/endpoints",
                "app/core",
                "app/models",
                "app/schemas",
                "app/services",
                "app/db",
                "tests/unit",
                "tests/integration",
                "alembic/versions",
            ])
        else:
            self._create_dirs(path, [
                "app/api",
                "app/models",
                "app/schemas",
                "app/core",
                "tests",
            ])

        # Requirements
        requirements = [
            "fastapi>=0.109.0",
            "uvicorn[standard]>=0.25.0",
            "pydantic>=2.5.0",
            "pydantic-settings>=2.1.0",
            "python-dotenv>=1.0.0",
        ]

        dev_requirements = []

        if config.orm == ORM.SQLALCHEMY:
            requirements.extend([
                "sqlalchemy>=2.0.0",
                "alembic>=1.13.0",
            ])
            if config.database == Database.POSTGRESQL:
                requirements.append("asyncpg>=0.29.0")
                requirements.append("psycopg2-binary>=2.9.0")
            elif config.database == Database.MYSQL:
                requirements.append("aiomysql>=0.2.0")
            elif config.database == Database.SQLITE:
                requirements.append("aiosqlite>=0.19.0")
        elif config.orm == ORM.SQLMODEL:
            requirements.append("sqlmodel>=0.0.14")

        if "jwt" in config.features:
            requirements.extend([
                "python-jose[cryptography]>=3.3.0",
                "passlib[bcrypt]>=1.7.0",
            ])

        if "celery" in config.features:
            requirements.extend([
                "celery>=5.3.0",
                "redis>=5.0.0",
            ])

        if config.pytest:
            dev_requirements.extend([
                "pytest>=7.4.0",
                "pytest-asyncio>=0.23.0",
                "pytest-cov>=4.1.0",
                "httpx>=0.26.0",
            ])

        if config.ruff:
            dev_requirements.append("ruff>=0.1.0")

        if config.mypy:
            dev_requirements.append("mypy>=1.8.0")

        # Write requirements
        self._write_file(path / "requirements.txt", "\n".join(requirements))
        if dev_requirements:
            self._write_file(path / "requirements-dev.txt", "\n".join(dev_requirements))

        # pyproject.toml
        self._write_file(path / "pyproject.toml", self._fastapi_pyproject(config))

        # Source files
        self._write_file(path / "app/__init__.py", "")
        self._write_file(path / "app/main.py", self._fastapi_main(config))
        self._write_file(path / "app/core/__init__.py", "")
        self._write_file(path / "app/core/config.py", self._fastapi_config(config))
        self._write_file(path / "app/api/__init__.py", "")

        if config.orm == ORM.SQLALCHEMY:
            self._write_file(path / "app/db/__init__.py", "")
            self._write_file(path / "app/db/session.py", self._fastapi_db_session(config))
            self._write_file(path / "app/db/base.py", self._fastapi_db_base())
            self._write_file(path / "alembic.ini", self._alembic_ini(config))
            self._write_file(path / "alembic/env.py", self._alembic_env(config))

        # Ruff config
        if config.ruff:
            self._write_file(path / "ruff.toml", self._ruff_config())

        # Docker
        if config.docker:
            self._write_file(path / "Dockerfile", self._fastapi_dockerfile(config))
            self._write_file(path / "docker-compose.yml", self._fastapi_docker_compose(config))

        self._create_common_files(path, config, python=True)

    def _create_django(self, path: Path, config: ProjectConfig):
        """Create a Django project."""
        project_name = config.name.replace("-", "_")

        self._create_dirs(path, [
            f"{project_name}/settings",
            "apps/core",
            "apps/users",
            "static",
            "media",
            "templates",
            "tests",
        ])

        requirements = [
            "django>=5.0.0",
            "python-dotenv>=1.0.0",
            "django-environ>=0.11.0",
        ]

        if "drf" in config.features:
            requirements.append("djangorestframework>=3.14.0")

        if config.database == Database.POSTGRESQL:
            requirements.append("psycopg2-binary>=2.9.0")

        if "celery" in config.features:
            requirements.extend([
                "celery>=5.3.0",
                "django-celery-beat>=2.5.0",
                "redis>=5.0.0",
            ])

        self._write_file(path / "requirements.txt", "\n".join(requirements))

        # Django settings
        self._write_file(path / f"{project_name}/__init__.py", "")
        self._write_file(path / f"{project_name}/settings/__init__.py", "from .base import *")
        self._write_file(path / f"{project_name}/settings/base.py", self._django_settings_base(config, project_name))
        self._write_file(path / f"{project_name}/settings/dev.py", self._django_settings_dev(config))
        self._write_file(path / f"{project_name}/settings/prod.py", self._django_settings_prod(config))
        self._write_file(path / f"{project_name}/urls.py", self._django_urls(config))
        self._write_file(path / f"{project_name}/wsgi.py", self._django_wsgi(config, project_name))
        self._write_file(path / f"{project_name}/asgi.py", self._django_asgi(config, project_name))

        # manage.py
        self._write_file(path / "manage.py", self._django_manage(config, project_name))

        # Apps
        self._write_file(path / "apps/__init__.py", "")
        self._write_file(path / "apps/core/__init__.py", "")
        self._write_file(path / "apps/users/__init__.py", "")

        self._create_common_files(path, config, python=True)

    def _create_flask(self, path: Path, config: ProjectConfig):
        """Create a Flask project."""
        self._create_dirs(path, [
            "app/api",
            "app/models",
            "app/services",
            "app/templates",
            "app/static",
            "tests",
        ])

        requirements = [
            "flask>=3.0.0",
            "python-dotenv>=1.0.0",
        ]

        if config.orm == ORM.SQLALCHEMY:
            requirements.append("flask-sqlalchemy>=3.1.0")

        self._write_file(path / "requirements.txt", "\n".join(requirements))

        self._write_file(path / "app/__init__.py", self._flask_init(config))
        self._write_file(path / "app/config.py", self._flask_config(config))
        self._write_file(path / "run.py", self._flask_run(config))

        self._create_common_files(path, config, python=True)

    # =========================================================================
    # Library/Tool Projects
    # =========================================================================

    def _create_python(self, path: Path, config: ProjectConfig):
        """Create a Python package/library."""
        package_name = config.name.replace("-", "_")

        self._create_dirs(path, [
            f"src/{package_name}",
            "tests",
            "docs",
        ])

        # pyproject.toml
        self._write_file(path / "pyproject.toml", self._python_pyproject(config, package_name))

        # Package files
        self._write_file(path / f"src/{package_name}/__init__.py", f'"""{ config.description or config.name }"""\n\n__version__ = "{config.version}"\n')
        self._write_file(path / f"src/{package_name}/main.py", self._python_main(config))

        # Tests
        self._write_file(path / "tests/__init__.py", "")
        self._write_file(path / "tests/test_main.py", self._python_test(config, package_name))

        if config.ruff:
            self._write_file(path / "ruff.toml", self._ruff_config())

        self._create_common_files(path, config, python=True)

    def _create_typescript_lib(self, path: Path, config: ProjectConfig):
        """Create a TypeScript library/package."""
        self._create_dirs(path, [
            "src",
            "tests",
            "dist",
        ])

        deps = {}
        dev_deps = {
            "typescript": "^5.3.0",
            "tsup": "^8.0.0",
        }

        if config.testing:
            dev_deps["vitest"] = "^1.0.0"

        if config.eslint:
            dev_deps.update({
                "eslint": "^8.56.0",
                "@typescript-eslint/eslint-plugin": "^6.0.0",
                "@typescript-eslint/parser": "^6.0.0",
            })

        package_json = self._create_package_json(config, deps, dev_deps, {
            "build": "tsup",
            "dev": "tsup --watch",
            "test": "vitest" if config.testing else None,
            "lint": "eslint src" if config.eslint else None,
            "prepublishOnly": "npm run build",
        })
        package_json["main"] = "./dist/index.js"
        package_json["module"] = "./dist/index.mjs"
        package_json["types"] = "./dist/index.d.ts"
        package_json["exports"] = {
            ".": {
                "require": "./dist/index.js",
                "import": "./dist/index.mjs",
                "types": "./dist/index.d.ts"
            }
        }
        package_json["files"] = ["dist"]

        self._write_json(path / "package.json", package_json)

        # tsconfig
        self._write_json(path / "tsconfig.json", self._create_tsconfig(config, "library"))

        # tsup config
        self._write_file(path / "tsup.config.ts", self._tsup_config())

        # Source files
        self._write_file(path / "src/index.ts", f'export const hello = (name: string): string => `Hello, ${{name}}!`;\n')

        if config.testing:
            self._write_file(path / "tests/index.test.ts", "import { describe, it, expect } from 'vitest';\nimport { hello } from '../src';\n\ndescribe('hello', () => {\n  it('should greet', () => {\n    expect(hello('World')).toBe('Hello, World!');\n  });\n});\n")

        self._create_common_files(path, config)

    def _create_cli(self, path: Path, config: ProjectConfig):
        """Create a CLI tool project."""
        if config.language == Language.PYTHON:
            self._create_python_cli(path, config)
        else:
            self._create_node_cli(path, config)

    def _create_python_cli(self, path: Path, config: ProjectConfig):
        """Create a Python CLI with Click or Typer."""
        package_name = config.name.replace("-", "_")

        self._create_dirs(path, [
            f"src/{package_name}/commands",
            "tests",
        ])

        requirements = [
            "typer[all]>=0.9.0",
            "rich>=13.7.0",
        ]

        self._write_file(path / "requirements.txt", "\n".join(requirements))
        self._write_file(path / "pyproject.toml", self._python_cli_pyproject(config, package_name))

        self._write_file(path / f"src/{package_name}/__init__.py", f'__version__ = "{config.version}"\n')
        self._write_file(path / f"src/{package_name}/__main__.py", f"from {package_name}.cli import app\n\nif __name__ == '__main__':\n    app()\n")
        self._write_file(path / f"src/{package_name}/cli.py", self._python_cli_main(config, package_name))

        self._create_common_files(path, config, python=True)

    def _create_node_cli(self, path: Path, config: ProjectConfig):
        """Create a Node.js CLI tool."""
        self._create_dirs(path, [
            "src/commands",
            "tests",
        ])

        deps = {
            "commander": "^11.1.0",
            "chalk": "^5.3.0",
            "ora": "^8.0.0",
        }
        dev_deps = {}

        if config.language == Language.TYPESCRIPT:
            dev_deps.update({
                "typescript": "^5.3.0",
                "@types/node": "^22.0.0",
                "tsup": "^8.0.0",
            })

        package_json = self._create_package_json(config, deps, dev_deps, {
            "build": "tsup",
            "dev": "tsup --watch",
            "start": "node dist/cli.js",
        })
        package_json["bin"] = {config.name: "./dist/cli.js"}
        package_json["type"] = "module"

        self._write_json(path / "package.json", package_json)

        if config.language == Language.TYPESCRIPT:
            self._write_json(path / "tsconfig.json", self._create_tsconfig(config, "node"))
            self._write_file(path / "tsup.config.ts", self._cli_tsup_config(config))

        ext = "ts" if config.language == Language.TYPESCRIPT else "js"
        self._write_file(path / f"src/cli.{ext}", self._node_cli_main(config))

        self._create_common_files(path, config)

    def _create_electron(self, path: Path, config: ProjectConfig):
        """Create an Electron desktop application."""
        self._create_dirs(path, [
            "src/main",
            "src/renderer",
            "src/preload",
            "resources",
        ])

        deps = {}
        dev_deps = {
            "electron": "^28.0.0",
            "electron-builder": "^24.9.0",
        }

        if config.language == Language.TYPESCRIPT:
            dev_deps.update({
                "typescript": "^5.3.0",
                "@types/node": "^22.0.0",
            })

        package_json = self._create_package_json(config, deps, dev_deps, {
            "start": "electron .",
            "build": "electron-builder",
        })
        package_json["main"] = "src/main/index.js"

        self._write_json(path / "package.json", package_json)

        ext = "ts" if config.language == Language.TYPESCRIPT else "js"
        self._write_file(path / f"src/main/index.{ext}", self._electron_main(config))
        self._write_file(path / f"src/preload/preload.{ext}", self._electron_preload(config))
        self._write_file(path / "src/renderer/index.html", self._electron_html(config))

        self._create_common_files(path, config)

    def _create_monorepo(self, path: Path, config: ProjectConfig):
        """Create a monorepo structure."""
        self._create_dirs(path, [
            "packages",
            "apps",
            ".github/workflows",
        ])

        # Root package.json for pnpm/npm workspaces
        package_json = {
            "name": config.name,
            "private": True,
            "workspaces": ["packages/*", "apps/*"],
            "scripts": {
                "build": "turbo build",
                "dev": "turbo dev",
                "lint": "turbo lint",
                "test": "turbo test",
            },
            "devDependencies": {
                "turbo": "^1.11.0",
            }
        }
        self._write_json(path / "package.json", package_json)

        # Turbo config
        self._write_json(path / "turbo.json", {
            "$schema": "https://turbo.build/schema.json",
            "globalDependencies": ["**/.env.*local"],
            "pipeline": {
                "build": {
                    "dependsOn": ["^build"],
                    "outputs": ["dist/**", ".next/**"]
                },
                "dev": {
                    "cache": False,
                    "persistent": True
                },
                "lint": {},
                "test": {}
            }
        })

        # pnpm workspace
        self._write_file(path / "pnpm-workspace.yaml", "packages:\n  - 'packages/*'\n  - 'apps/*'\n")

        self._create_common_files(path, config)

    # =========================================================================
    # Helper Methods
    # =========================================================================

    def _create_dirs(self, path: Path, dirs: List[str]):
        """Create directory structure."""
        for d in dirs:
            (path / d).mkdir(parents=True, exist_ok=True)

    def _write_file(self, path: Path, content: str):
        """Write content to a file."""
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content)

    def _write_json(self, path: Path, data: dict):
        """Write JSON to a file."""
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w") as f:
            json.dump(data, f, indent=2)

    def _create_package_json(self, config: ProjectConfig, deps: dict, dev_deps: dict, scripts: dict) -> dict:
        """Create a package.json structure."""
        return {
            "name": config.name,
            "version": config.version,
            "description": config.description or f"{config.name} project",
            "author": config.author,
            "license": config.license,
            "scripts": {k: v for k, v in scripts.items() if v is not None},
            "dependencies": deps,
            "devDependencies": dev_deps,
        }

    def _create_tsconfig(self, config: ProjectConfig, framework: str) -> dict:
        """Create TypeScript configuration."""
        base = {
            "compilerOptions": {
                "target": "ES2022",
                "module": "ESNext",
                "moduleResolution": "bundler",
                "esModuleInterop": True,
                "skipLibCheck": True,
                "forceConsistentCasingInFileNames": True,
                "strict": config.typescript_strict,
            }
        }

        if framework == "react":
            base["compilerOptions"].update({
                "lib": ["DOM", "DOM.Iterable", "ES2022"],
                "jsx": "react-jsx",
                "baseUrl": ".",
                "paths": {"@/*": ["./src/*"]},
            })
            base["include"] = ["src"]
        elif framework == "nextjs":
            base["compilerOptions"].update({
                "lib": ["DOM", "DOM.Iterable", "ES2022"],
                "jsx": "preserve",
                "incremental": True,
                "plugins": [{"name": "next"}],
                "baseUrl": ".",
                "paths": {"@/*": ["./src/*"]},
            })
            base["include"] = ["next-env.d.ts", "**/*.ts", "**/*.tsx", ".next/types/**/*.ts"]
            base["exclude"] = ["node_modules"]
        elif framework == "vue":
            base["compilerOptions"].update({
                "lib": ["DOM", "ES2022"],
                "jsx": "preserve",
                "baseUrl": ".",
                "paths": {"@/*": ["./src/*"]},
            })
            base["include"] = ["src/**/*.ts", "src/**/*.tsx", "src/**/*.vue"]
        elif framework == "node":
            base["compilerOptions"].update({
                "module": "CommonJS",
                "moduleResolution": "node",
                "outDir": "./dist",
                "rootDir": "./src",
                "declaration": True,
            })
            base["include"] = ["src"]
            base["exclude"] = ["node_modules", "dist"]
        elif framework == "library":
            base["compilerOptions"].update({
                "declaration": True,
                "declarationMap": True,
                "sourceMap": True,
                "outDir": "./dist",
            })
            base["include"] = ["src"]
        elif framework == "nestjs":
            base["compilerOptions"].update({
                "module": "CommonJS",
                "declaration": True,
                "removeComments": True,
                "emitDecoratorMetadata": True,
                "experimentalDecorators": True,
                "allowSyntheticDefaultImports": True,
                "sourceMap": True,
                "outDir": "./dist",
                "baseUrl": "./",
                "incremental": True,
            })
        elif framework == "angular":
            base["compilerOptions"].update({
                "outDir": "./dist/out-tsc",
                "sourceMap": True,
                "declaration": False,
                "downlevelIteration": True,
                "experimentalDecorators": True,
                "moduleResolution": "node",
                "importHelpers": True,
                "lib": ["ES2022", "dom"],
            })

        return base

    def _create_common_files(self, path: Path, config: ProjectConfig, python: bool = False):
        """Create common project files."""
        # .gitignore
        if python:
            gitignore = """# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
.venv/
ENV/
.env
build/
dist/
*.egg-info/
.pytest_cache/
.coverage
htmlcov/
.mypy_cache/
.ruff_cache/

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Project
*.log
"""
        else:
            gitignore = """# Dependencies
node_modules/

# Build
dist/
build/
.next/
out/

# Environment
.env
.env.local
.env.*.local

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Testing
coverage/

# Logs
*.log
npm-debug.log*
yarn-debug.log*
yarn-error.log*
"""
        self._write_file(path / ".gitignore", gitignore)

        # .env.example
        if python:
            env_example = """# Environment
DEBUG=true
LOG_LEVEL=debug

# Database
DATABASE_URL=postgresql://user:password@localhost:5432/dbname

# Security
SECRET_KEY=your-secret-key-here
"""
        else:
            env_example = """# Environment
NODE_ENV=development

# Database
DATABASE_URL=postgresql://user:password@localhost:5432/dbname

# API
API_URL=http://localhost:3000

# Auth
NEXTAUTH_SECRET=your-secret-key
NEXTAUTH_URL=http://localhost:3000
"""
        self._write_file(path / ".env.example", env_example)

        # README.md
        readme = f"""# {config.name}

{config.description or 'Project description'}

## Getting Started

### Prerequisites

"""
        if python:
            readme += f"""- Python {config.python_version}+

### Installation

```bash
# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # Unix
# .venv\\Scripts\\activate  # Windows

# Install dependencies
pip install -r requirements.txt

# Copy environment file
cp .env.example .env
```

### Development

```bash
# Run development server
uvicorn app.main:app --reload  # FastAPI
# python manage.py runserver  # Django
```

### Testing

```bash
pytest
```
"""
        else:
            readme += f"""- Node.js {config.node_version}+
- {config.package_manager.value}

### Installation

```bash
# Install dependencies
{config.package_manager.value} install

# Copy environment file
cp .env.example .env.local
```

### Development

```bash
{config.package_manager.value} run dev
```

### Building

```bash
{config.package_manager.value} run build
```

### Testing

```bash
{config.package_manager.value} run test
```
"""
        readme += f"""
## License

{config.license}
"""
        self._write_file(path / "README.md", readme)

        # VS Code settings
        if config.eslint or config.prettier or config.ruff:
            vscode_settings = {}
            if config.eslint:
                vscode_settings["editor.codeActionsOnSave"] = {"source.fixAll.eslint": "explicit"}
            if config.prettier:
                vscode_settings["editor.defaultFormatter"] = "esbenp.prettier-vscode"
                vscode_settings["editor.formatOnSave"] = True
            if config.ruff:
                vscode_settings["[python]"] = {
                    "editor.defaultFormatter": "charliermarsh.ruff",
                    "editor.formatOnSave": True,
                    "editor.codeActionsOnSave": {"source.fixAll.ruff": "explicit"}
                }

            (path / ".vscode").mkdir(exist_ok=True)
            self._write_json(path / ".vscode/settings.json", vscode_settings)

        # GitHub Actions
        if config.github_actions:
            self._create_github_actions(path, config, python)

        # Docker
        if config.docker and not python:
            self._create_node_docker(path, config)

    def _create_tailwind_config(self, path: Path, config: ProjectConfig, framework: str = "react"):
        """Create Tailwind CSS configuration."""
        content_paths = {
            "html": "'./**/*.html'",
            "react": "'./index.html', './src/**/*.{js,ts,jsx,tsx}'",
            "nextjs": "'./src/**/*.{js,ts,jsx,tsx,mdx}'",
            "vue": "'./index.html', './src/**/*.{vue,js,ts,jsx,tsx}'",
            "svelte": "'./src/**/*.{html,js,svelte,ts}'",
        }

        config_content = f"""/** @type {{import('tailwindcss').Config}} */
export default {{
  content: [{content_paths.get(framework, content_paths['react'])}],
  theme: {{
    extend: {{}},
  }},
  plugins: [],
}}
"""
        self._write_file(path / "tailwind.config.js", config_content)

        postcss_content = """export default {
  plugins: {
    tailwindcss: {},
    autoprefixer: {},
  },
}
"""
        self._write_file(path / "postcss.config.js", postcss_content)

    def _create_eslint_config(self, path: Path, config: ProjectConfig, framework: str):
        """Create ESLint configuration."""
        eslint_config = {
            "env": {"browser": True, "es2022": True, "node": True},
            "extends": ["eslint:recommended"],
            "parserOptions": {"ecmaVersion": "latest", "sourceType": "module"},
            "rules": {}
        }

        if config.language == Language.TYPESCRIPT:
            eslint_config["extends"].append("plugin:@typescript-eslint/recommended")
            eslint_config["parser"] = "@typescript-eslint/parser"
            eslint_config["plugins"] = ["@typescript-eslint"]

        if framework == "react":
            eslint_config["extends"].extend([
                "plugin:react/recommended",
                "plugin:react-hooks/recommended"
            ])
            eslint_config["plugins"] = eslint_config.get("plugins", []) + ["react", "react-hooks"]
            eslint_config["settings"] = {"react": {"version": "detect"}}
            eslint_config["rules"]["react/react-in-jsx-scope"] = "off"

        self._write_json(path / ".eslintrc.json", eslint_config)

    def _create_prettier_config(self, path: Path, plugins: List[str] = None):
        """Create Prettier configuration."""
        config = {
            "semi": True,
            "singleQuote": True,
            "tabWidth": 2,
            "trailingComma": "es5",
            "printWidth": 100,
        }
        if plugins:
            config["plugins"] = plugins
        self._write_json(path / ".prettierrc", config)

    def _create_github_actions(self, path: Path, config: ProjectConfig, python: bool):
        """Create GitHub Actions workflow."""
        (path / ".github/workflows").mkdir(parents=True, exist_ok=True)

        if python:
            workflow = f"""name: CI

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '{config.python_version}'

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt
          pip install -r requirements-dev.txt

      - name: Lint with ruff
        run: ruff check .

      - name: Type check with mypy
        run: mypy .

      - name: Test with pytest
        run: pytest --cov
"""
        else:
            workflow = f"""name: CI

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  build:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v4

      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '{config.node_version}'

      - name: Install dependencies
        run: npm ci

      - name: Lint
        run: npm run lint

      - name: Type check
        run: npm run type-check

      - name: Test
        run: npm run test

      - name: Build
        run: npm run build
"""
        self._write_file(path / ".github/workflows/ci.yml", workflow)

    def _create_node_docker(self, path: Path, config: ProjectConfig):
        """Create Docker configuration for Node.js projects."""
        dockerfile = f"""FROM node:{config.node_version}-alpine AS base

# Install dependencies only when needed
FROM base AS deps
WORKDIR /app
COPY package*.json ./
RUN npm ci

# Build the application
FROM base AS builder
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY . .
RUN npm run build

# Production image
FROM base AS runner
WORKDIR /app
ENV NODE_ENV=production

COPY --from=builder /app/dist ./dist
COPY --from=builder /app/node_modules ./node_modules
COPY --from=builder /app/package.json ./

EXPOSE 3000
CMD ["node", "dist/index.js"]
"""
        self._write_file(path / "Dockerfile", dockerfile)

        docker_compose = """version: '3.8'

services:
  app:
    build: .
    ports:
      - "3000:3000"
    environment:
      - NODE_ENV=development
    volumes:
      - .:/app
      - /app/node_modules
"""
        self._write_file(path / "docker-compose.yml", docker_compose)

    # =========================================================================
    # Template Content Methods (simplified - full implementation would be longer)
    # =========================================================================

    def _generate_vite_config(self, config: ProjectConfig) -> str:
        return """import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import path from 'path';

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
});
"""

    def _react_main(self, config: ProjectConfig) -> str:
        ext = "tsx" if config.language == Language.TYPESCRIPT else "jsx"
        return f"""import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App';
import './styles/globals.css';

ReactDOM.createRoot(document.getElementById('root'){'!' if config.language == Language.TYPESCRIPT else ''}).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
);
"""

    def _react_app(self, config: ProjectConfig) -> str:
        return """function App() {
  return (
    <div className="min-h-screen bg-gray-100 flex items-center justify-center">
      <div className="text-center">
        <h1 className="text-4xl font-bold text-gray-900">Welcome</h1>
        <p className="mt-2 text-gray-600">Your app is ready!</p>
      </div>
    </div>
  );
}

export default App;
"""

    def _css_globals(self, config: ProjectConfig) -> str:
        if config.css_framework == CSSFramework.TAILWIND:
            return """@tailwind base;
@tailwind components;
@tailwind utilities;
"""
        return """* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: system-ui, -apple-system, sans-serif;
}
"""

    def _react_index_html(self, config: ProjectConfig) -> str:
        return f"""<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <link rel="icon" type="image/svg+xml" href="/vite.svg" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>{config.name}</title>
  </head>
  <body>
    <div id="root"></div>
    <script type="module" src="/src/main.{'tsx' if config.language == Language.TYPESCRIPT else 'jsx'}"></script>
  </body>
</html>
"""

    def _vitest_config(self) -> str:
        return """import { defineConfig } from 'vitest/config';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
  test: {
    environment: 'jsdom',
    globals: true,
    setupFiles: './tests/setup.ts',
  },
});
"""

    def _vitest_setup(self) -> str:
        return """import '@testing-library/jest-dom';
"""

    def _nextjs_config(self, config: ProjectConfig) -> str:
        return """/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
};

module.exports = nextConfig;
"""

    def _nextjs_layout(self, config: ProjectConfig) -> str:
        return f"""import type {{ Metadata }} from 'next';
import './globals.css';

export const metadata: Metadata = {{
  title: '{config.name}',
  description: '{config.description or "Generated by Next.js"}',
}};

export default function RootLayout({{
  children,
}}: {{
  children: React.ReactNode;
}}) {{
  return (
    <html lang="en">
      <body>{{children}}</body>
    </html>
  );
}}
"""

    def _nextjs_page(self, config: ProjectConfig) -> str:
        return """export default function Home() {
  return (
    <main className="min-h-screen flex items-center justify-center">
      <div className="text-center">
        <h1 className="text-4xl font-bold">Welcome</h1>
        <p className="mt-2 text-gray-600">Your Next.js app is ready!</p>
      </div>
    </main>
  );
}
"""

    def _prisma_schema(self, config: ProjectConfig) -> str:
        provider = "postgresql" if config.database == Database.POSTGRESQL else "sqlite"
        return f"""generator client {{
  provider = "prisma-client-js"
}}

datasource db {{
  provider = "{provider}"
  url      = env("DATABASE_URL")
}}

model User {{
  id        String   @id @default(cuid())
  email     String   @unique
  name      String?
  createdAt DateTime @default(now())
  updatedAt DateTime @updatedAt
}}
"""

    def _prisma_client(self) -> str:
        return """import { PrismaClient } from '@prisma/client';

const globalForPrisma = globalThis as unknown as {
  prisma: PrismaClient | undefined;
};

export const prisma = globalForPrisma.prisma ?? new PrismaClient();

if (process.env.NODE_ENV !== 'production') globalForPrisma.prisma = prisma;

export default prisma;
"""

    def _utils_file(self) -> str:
        return """import { type ClassValue, clsx } from 'clsx';
import { twMerge } from 'tailwind-merge';

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}
"""

    def _vue_vite_config(self, config: ProjectConfig) -> str:
        return """import { defineConfig } from 'vite';
import vue from '@vitejs/plugin-vue';
import path from 'path';

export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
});
"""

    def _vue_main(self, config: ProjectConfig) -> str:
        imports = ["import { createApp } from 'vue';", "import App from './App.vue';"]
        setup = ["const app = createApp(App);"]

        if "pinia" in config.features:
            imports.append("import { createPinia } from 'pinia';")
            setup.append("app.use(createPinia());")

        if "vue-router" in config.features:
            imports.append("import router from './router';")
            setup.append("app.use(router);")

        if config.css_framework == CSSFramework.TAILWIND:
            imports.append("import './assets/main.css';")

        setup.append("app.mount('#app');")

        return "\n".join(imports) + "\n\n" + "\n".join(setup) + "\n"

    def _vue_app(self, config: ProjectConfig) -> str:
        return """<script setup lang="ts">
</script>

<template>
  <div class="min-h-screen bg-gray-100 flex items-center justify-center">
    <div class="text-center">
      <h1 class="text-4xl font-bold text-gray-900">Welcome</h1>
      <p class="mt-2 text-gray-600">Your Vue app is ready!</p>
    </div>
  </div>
</template>
"""

    def _vue_index_html(self, config: ProjectConfig) -> str:
        return f"""<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <link rel="icon" href="/favicon.ico" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>{config.name}</title>
  </head>
  <body>
    <div id="app"></div>
    <script type="module" src="/src/main.{'ts' if config.language == Language.TYPESCRIPT else 'js'}"></script>
  </body>
</html>
"""

    def _nuxt_config(self, config: ProjectConfig) -> str:
        modules = []
        if config.css_framework == CSSFramework.TAILWIND:
            modules.append("'@nuxtjs/tailwindcss'")
        if "pinia" in config.features:
            modules.append("'@pinia/nuxt'")

        return f"""export default defineNuxtConfig({{
  devtools: {{ enabled: true }},
  modules: [{', '.join(modules)}],
}});
"""

    def _nuxt_index_page(self, config: ProjectConfig) -> str:
        return """<template>
  <div class="min-h-screen bg-gray-100 flex items-center justify-center">
    <div class="text-center">
      <h1 class="text-4xl font-bold text-gray-900">Welcome</h1>
      <p class="mt-2 text-gray-600">Your Nuxt app is ready!</p>
    </div>
  </div>
</template>
"""

    def _nuxt_app(self, config: ProjectConfig) -> str:
        return """<template>
  <NuxtPage />
</template>
"""

    def _svelte_config(self, config: ProjectConfig) -> str:
        return """import adapter from '@sveltejs/adapter-auto';
import { vitePreprocess } from '@sveltejs/vite-plugin-svelte';

/** @type {import('@sveltejs/kit').Config} */
const config = {
  preprocess: vitePreprocess(),
  kit: {
    adapter: adapter(),
  },
};

export default config;
"""

    def _svelte_vite_config(self, config: ProjectConfig) -> str:
        return """import { sveltekit } from '@sveltejs/kit/vite';
import { defineConfig } from 'vite';

export default defineConfig({
  plugins: [sveltekit()],
});
"""

    def _svelte_page(self, config: ProjectConfig) -> str:
        return """<script lang="ts">
</script>

<div class="min-h-screen bg-gray-100 flex items-center justify-center">
  <div class="text-center">
    <h1 class="text-4xl font-bold text-gray-900">Welcome</h1>
    <p class="mt-2 text-gray-600">Your SvelteKit app is ready!</p>
  </div>
</div>
"""

    def _svelte_layout(self, config: ProjectConfig) -> str:
        css_import = "import '../app.css';" if config.css_framework == CSSFramework.TAILWIND else ""
        return f"""<script>
  {css_import}
</script>

<slot />
"""

    def _svelte_app_html(self, config: ProjectConfig) -> str:
        return f"""<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <link rel="icon" href="%sveltekit.assets%/favicon.png" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    %sveltekit.head%
  </head>
  <body data-sveltekit-preload-data="hover">
    <div style="display: contents">%sveltekit.body%</div>
  </body>
</html>
"""

    def _angular_config(self, config: ProjectConfig) -> dict:
        return {
            "$schema": "./node_modules/@angular/cli/lib/config/schema.json",
            "version": 1,
            "newProjectRoot": "projects",
            "projects": {
                config.name: {
                    "projectType": "application",
                    "root": "",
                    "sourceRoot": "src",
                    "architect": {}
                }
            }
        }

    def _express_index(self, config: ProjectConfig) -> str:
        return """import app from './app';
import { config } from './config';

const PORT = config.port || 3000;

app.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`);
});
"""

    def _express_app(self, config: ProjectConfig) -> str:
        return """import express from 'express';
import cors from 'cors';
import helmet from 'helmet';
import morgan from 'morgan';
import routes from './routes';
import { errorHandler } from './middleware/errorHandler';

const app = express();

// Middleware
app.use(helmet());
app.use(cors());
app.use(morgan('dev'));
app.use(express.json());

// Routes
app.use('/api', routes);

// Error handling
app.use(errorHandler);

export default app;
"""

    def _express_config(self, config: ProjectConfig) -> str:
        return """import dotenv from 'dotenv';

dotenv.config();

export const config = {
  port: process.env.PORT || 3000,
  nodeEnv: process.env.NODE_ENV || 'development',
  databaseUrl: process.env.DATABASE_URL,
};
"""

    def _express_routes(self, config: ProjectConfig) -> str:
        return """import { Router } from 'express';

const router = Router();

router.get('/health', (req, res) => {
  res.json({ status: 'ok' });
});

export default router;
"""

    def _express_error_handler(self, config: ProjectConfig) -> str:
        return """import { Request, Response, NextFunction } from 'express';

export const errorHandler = (
  err: Error,
  req: Request,
  res: Response,
  next: NextFunction
) => {
  console.error(err.stack);
  res.status(500).json({ error: 'Something went wrong!' });
};
"""

    def _nestjs_main(self, config: ProjectConfig) -> str:
        return """import { NestFactory } from '@nestjs/core';
import { AppModule } from './app.module';

async function bootstrap() {
  const app = await NestFactory.create(AppModule);
  await app.listen(3000);
}
bootstrap();
"""

    def _nestjs_app_module(self, config: ProjectConfig) -> str:
        return """import { Module } from '@nestjs/common';
import { AppController } from './app.controller';
import { AppService } from './app.service';

@Module({
  imports: [],
  controllers: [AppController],
  providers: [AppService],
})
export class AppModule {}
"""

    def _nestjs_controller(self, config: ProjectConfig) -> str:
        return """import { Controller, Get } from '@nestjs/common';
import { AppService } from './app.service';

@Controller()
export class AppController {
  constructor(private readonly appService: AppService) {}

  @Get()
  getHello(): string {
    return this.appService.getHello();
  }
}
"""

    def _nestjs_service(self, config: ProjectConfig) -> str:
        return """import { Injectable } from '@nestjs/common';

@Injectable()
export class AppService {
  getHello(): string {
    return 'Hello World!';
  }
}
"""

    def _fastapi_pyproject(self, config: ProjectConfig) -> str:
        return f"""[project]
name = "{config.name}"
version = "{config.version}"
description = "{config.description or ''}"
authors = [{{name = "{config.author}"}}]
readme = "README.md"
requires-python = ">={config.python_version}"

[tool.ruff]
line-length = 100
target-version = "py311"

[tool.ruff.lint]
select = ["E", "F", "I", "N", "W", "UP"]

[tool.mypy]
python_version = "{config.python_version}"
strict = true
"""

    def _fastapi_main(self, config: ProjectConfig) -> str:
        return """from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


@app.get("/")
async def root():
    return {"message": "Welcome to the API"}
"""

    def _fastapi_config(self, config: ProjectConfig) -> str:
        return f"""from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    PROJECT_NAME: str = "{config.name}"
    VERSION: str = "{config.version}"
    API_V1_STR: str = "/api/v1"

    DATABASE_URL: str = "sqlite:///./app.db"

    class Config:
        env_file = ".env"


settings = Settings()
"""

    def _fastapi_db_session(self, config: ProjectConfig) -> str:
        return """from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import settings

engine = create_async_engine(settings.DATABASE_URL, echo=True)

async_session = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)


async def get_db() -> AsyncSession:
    async with async_session() as session:
        yield session
"""

    def _fastapi_db_base(self) -> str:
        return """from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass
"""

    def _alembic_ini(self, config: ProjectConfig) -> str:
        return """[alembic]
script_location = alembic
prepend_sys_path = .
version_path_separator = os

[post_write_hooks]

[loggers]
keys = root,sqlalchemy,alembic

[handlers]
keys = console

[formatters]
keys = generic

[logger_root]
level = WARN
handlers = console
qualname =

[logger_sqlalchemy]
level = WARN
handlers =
qualname = sqlalchemy.engine

[logger_alembic]
level = INFO
handlers =
qualname = alembic

[handler_console]
class = StreamHandler
args = (sys.stderr,)
level = NOTSET
formatter = generic

[formatter_generic]
format = %(levelname)-5.5s [%(name)s] %(message)s
datefmt = %H:%M:%S
"""

    def _alembic_env(self, config: ProjectConfig) -> str:
        return """from logging.config import fileConfig
from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config
from alembic import context

from app.core.config import settings
from app.db.base import Base

config = context.config
config.set_main_option("sqlalchemy.url", settings.DATABASE_URL)

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    context.configure(connection=connection, target_metadata=target_metadata)
    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)
    await connectable.dispose()


def run_migrations_online() -> None:
    import asyncio
    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
"""

    def _ruff_config(self) -> str:
        return """line-length = 100
target-version = "py311"

[lint]
select = [
    "E",   # pycodestyle errors
    "F",   # pyflakes
    "I",   # isort
    "N",   # pep8-naming
    "W",   # pycodestyle warnings
    "UP",  # pyupgrade
    "B",   # flake8-bugbear
    "C4",  # flake8-comprehensions
]
ignore = ["E501"]

[lint.isort]
known-first-party = ["app"]
"""

    def _fastapi_dockerfile(self, config: ProjectConfig) -> str:
        return f"""FROM python:{config.python_version}-slim as builder

WORKDIR /app

RUN pip install --no-cache-dir poetry

COPY pyproject.toml poetry.lock* ./
RUN poetry export -f requirements.txt --output requirements.txt --without-hashes

FROM python:{config.python_version}-slim

WORKDIR /app

COPY --from=builder /app/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
"""

    def _fastapi_docker_compose(self, config: ProjectConfig) -> str:
        services = """version: '3.8'

services:
  app:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://postgres:postgres@db:5432/app
    depends_on:
      - db
    volumes:
      - .:/app

  db:
    image: postgres:15
    environment:
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=postgres
      - POSTGRES_DB=app
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

volumes:
  postgres_data:
"""
        return services

    def _django_settings_base(self, config: ProjectConfig, project_name: str) -> str:
        return f"""from pathlib import Path
import environ

BASE_DIR = Path(__file__).resolve().parent.parent.parent

env = environ.Env()
environ.Env.read_env(BASE_DIR / '.env')

SECRET_KEY = env('SECRET_KEY', default='your-secret-key-change-in-production')

DEBUG = env.bool('DEBUG', default=False)

ALLOWED_HOSTS = env.list('ALLOWED_HOSTS', default=[])

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'apps.core',
    'apps.users',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = '{project_name}.urls'

TEMPLATES = [
    {{
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {{
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        }},
    }},
]

WSGI_APPLICATION = '{project_name}.wsgi.application'

DATABASES = {{
    'default': env.db('DATABASE_URL', default='sqlite:///db.sqlite3')
}}

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
"""

    def _django_settings_dev(self, config: ProjectConfig) -> str:
        return """from .base import *

DEBUG = True
ALLOWED_HOSTS = ['*']
"""

    def _django_settings_prod(self, config: ProjectConfig) -> str:
        return """from .base import *

DEBUG = False
# Add production-specific settings
"""

    def _django_urls(self, config: ProjectConfig) -> str:
        return """from django.contrib import admin
from django.urls import path

urlpatterns = [
    path('admin/', admin.site.urls),
]
"""

    def _django_wsgi(self, config: ProjectConfig, project_name: str) -> str:
        return f"""import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', '{project_name}.settings')
application = get_wsgi_application()
"""

    def _django_asgi(self, config: ProjectConfig, project_name: str) -> str:
        return f"""import os
from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', '{project_name}.settings')
application = get_asgi_application()
"""

    def _django_manage(self, config: ProjectConfig, project_name: str) -> str:
        return f"""#!/usr/bin/env python
import os
import sys

def main():
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', '{project_name}.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django."
        ) from exc
    execute_from_command_line(sys.argv)

if __name__ == '__main__':
    main()
"""

    def _flask_init(self, config: ProjectConfig) -> str:
        return """from flask import Flask

def create_app():
    app = Flask(__name__)
    app.config.from_object('app.config.Config')

    @app.route('/')
    def index():
        return {'message': 'Hello, World!'}

    return app
"""

    def _flask_config(self, config: ProjectConfig) -> str:
        return """import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key')
    DEBUG = os.environ.get('DEBUG', 'true').lower() == 'true'
"""

    def _flask_run(self, config: ProjectConfig) -> str:
        return """from app import create_app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True)
"""

    def _python_pyproject(self, config: ProjectConfig, package_name: str) -> str:
        return f"""[project]
name = "{config.name}"
version = "{config.version}"
description = "{config.description or ''}"
authors = [{{name = "{config.author}"}}]
readme = "README.md"
license = {{text = "{config.license}"}}
requires-python = ">={config.python_version}"
classifiers = [
    "Development Status :: 3 - Alpha",
    "Intended Audience :: Developers",
    "License :: OSI Approved :: MIT License",
    "Programming Language :: Python :: 3",
]
dependencies = []

[project.optional-dependencies]
dev = [
    "pytest>=7.4.0",
    "pytest-cov>=4.1.0",
    "ruff>=0.1.0",
    "mypy>=1.8.0",
]

[build-system]
requires = ["setuptools>=61.0", "wheel"]
build-backend = "setuptools.build_meta"

[tool.setuptools.packages.find]
where = ["src"]

[tool.ruff]
line-length = 100
target-version = "py311"

[tool.mypy]
python_version = "{config.python_version}"
strict = true
"""

    def _python_main(self, config: ProjectConfig) -> str:
        return '''"""Main module."""


def hello(name: str) -> str:
    """Return a greeting."""
    return f"Hello, {name}!"
'''

    def _python_test(self, config: ProjectConfig, package_name: str) -> str:
        return f'''"""Tests for main module."""

from {package_name}.main import hello


def test_hello():
    """Test hello function."""
    assert hello("World") == "Hello, World!"
'''

    def _python_cli_pyproject(self, config: ProjectConfig, package_name: str) -> str:
        return f"""[project]
name = "{config.name}"
version = "{config.version}"
description = "{config.description or ''}"
authors = [{{name = "{config.author}"}}]
readme = "README.md"
requires-python = ">={config.python_version}"
dependencies = [
    "typer[all]>=0.9.0",
    "rich>=13.7.0",
]

[project.scripts]
{config.name} = "{package_name}.cli:app"

[build-system]
requires = ["setuptools>=61.0", "wheel"]
build-backend = "setuptools.build_meta"

[tool.setuptools.packages.find]
where = ["src"]
"""

    def _python_cli_main(self, config: ProjectConfig, package_name: str) -> str:
        return f'''"""CLI application."""

import typer
from rich import print

app = typer.Typer(help="{config.description or config.name}")


@app.command()
def hello(name: str = "World"):
    """Say hello."""
    print(f"[green]Hello, {{name}}![/green]")


@app.command()
def version():
    """Show version."""
    from {package_name} import __version__
    print(f"[blue]{{__version__}}[/blue]")


if __name__ == "__main__":
    app()
'''

    def _tsup_config(self) -> str:
        return """import { defineConfig } from 'tsup';

export default defineConfig({
  entry: ['src/index.ts'],
  format: ['cjs', 'esm'],
  dts: true,
  splitting: false,
  sourcemap: true,
  clean: true,
});
"""

    def _cli_tsup_config(self, config: ProjectConfig) -> str:
        return """import { defineConfig } from 'tsup';

export default defineConfig({
  entry: ['src/cli.ts'],
  format: ['esm'],
  target: 'node18',
  splitting: false,
  sourcemap: true,
  clean: true,
  banner: {
    js: '#!/usr/bin/env node',
  },
});
"""

    def _node_cli_main(self, config: ProjectConfig) -> str:
        return f"""import {{ Command }} from 'commander';
import chalk from 'chalk';

const program = new Command();

program
  .name('{config.name}')
  .description('{config.description or "CLI tool"}')
  .version('0.1.0');

program
  .command('hello')
  .description('Say hello')
  .argument('[name]', 'Name to greet', 'World')
  .action((name) => {{
    console.log(chalk.green(`Hello, ${{name}}!`));
  }});

program.parse();
"""

    def _electron_main(self, config: ProjectConfig) -> str:
        return """const { app, BrowserWindow } = require('electron');
const path = require('path');

function createWindow() {
  const mainWindow = new BrowserWindow({
    width: 800,
    height: 600,
    webPreferences: {
      preload: path.join(__dirname, '../preload/preload.js'),
      contextIsolation: true,
      nodeIntegration: false,
    },
  });

  mainWindow.loadFile('src/renderer/index.html');
}

app.whenReady().then(() => {
  createWindow();

  app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) {
      createWindow();
    }
  });
});

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit();
  }
});
"""

    def _electron_preload(self, config: ProjectConfig) -> str:
        return """const { contextBridge, ipcRenderer } = require('electron');

contextBridge.exposeInMainWorld('electronAPI', {
  // Add your API methods here
});
"""

    def _electron_html(self, config: ProjectConfig) -> str:
        return f"""<!DOCTYPE html>
<html>
  <head>
    <meta charset="UTF-8" />
    <meta http-equiv="Content-Security-Policy" content="default-src 'self'; script-src 'self'" />
    <title>{config.name}</title>
  </head>
  <body>
    <h1>Hello from {config.name}!</h1>
  </body>
</html>
"""

    # =========================================================================
    # HTML/CSS Templates
    # =========================================================================

    def _html_css_links(self, config: ProjectConfig) -> str:
        """Generate CSS link tags based on framework configuration."""
        if config.css_framework == CSSFramework.TAILWIND:
            return '\n    <link rel="stylesheet" href="css/output.css">'
        return '''
    <link rel="stylesheet" href="css/reset.css">
    <link rel="stylesheet" href="css/style.css">'''

    def _html_header(self, config: ProjectConfig, active_page: str = "index") -> str:
        """Generate HTML header with navigation."""
        nav_items = [
            ("index.html", "Home", "index"),
            ("about.html", "About", "about"),
            ("contact.html", "Contact", "contact"),
        ]
        nav_links = "\n".join(
            f'                <li class="nav__item"><a href="{href}" class="nav__link{" nav__link--active" if key == active_page else ""}">{label}</a></li>'
            for href, label, key in nav_items
        )
        return f'''    <header class="header">
        <nav class="nav">
            <div class="nav__logo">
                <a href="index.html">{config.name}</a>
            </div>
            <ul class="nav__menu">
{nav_links}
            </ul>
        </nav>
    </header>'''

    def _html_footer(self, config: ProjectConfig) -> str:
        """Generate HTML footer."""
        return f'''    <footer class="footer">
        <div class="container">
            <p>&copy; 2024 {config.name}. All rights reserved.</p>
        </div>
    </footer>'''

    def _html_index(self, config: ProjectConfig) -> str:
        """Generate index.html for static website."""
        css_links = self._html_css_links(config)
        header = self._html_header(config, "index")
        footer = self._html_footer(config)

        return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="description" content="{config.description or config.name}">
    <meta name="author" content="{config.author or ''}">
    <title>{config.name}</title>{css_links}
</head>
<body>
{header}

    <!-- Main Content -->
    <main class="main">
        <section class="hero">
            <div class="hero__content">
                <h1 class="hero__title">Welcome to {config.name}</h1>
                <p class="hero__subtitle">{config.description or 'A modern, responsive website'}</p>
                <a href="about.html" class="btn btn--primary">Learn More</a>
            </div>
        </section>

        <section class="features">
            <div class="container">
                <h2 class="section__title">Features</h2>
                <div class="features__grid">
                    <div class="feature">
                        <h3 class="feature__title">Responsive Design</h3>
                        <p class="feature__text">Works seamlessly on all devices</p>
                    </div>
                    <div class="feature">
                        <h3 class="feature__title">Modern CSS</h3>
                        <p class="feature__text">Clean and maintainable styles</p>
                    </div>
                    <div class="feature">
                        <h3 class="feature__title">Fast Performance</h3>
                        <p class="feature__text">Optimized for speed</p>
                    </div>
                </div>
            </div>
        </section>
    </main>

{footer}

    <script src="js/main.js"></script>
</body>
</html>
"""

    def _html_about(self, config: ProjectConfig) -> str:
        """Generate about.html page."""
        css_links = self._html_css_links(config)
        header = self._html_header(config, "about")
        footer = self._html_footer(config)

        return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="description" content="About {config.name}">
    <title>About - {config.name}</title>{css_links}
</head>
<body>
{header}

    <main class="main">
        <section class="page-header">
            <div class="container">
                <h1 class="page-header__title">About Us</h1>
                <p class="page-header__subtitle">Learn more about {config.name}</p>
            </div>
        </section>

        <section class="content">
            <div class="container">
                <p>This is the about page. Add your content here.</p>
            </div>
        </section>
    </main>

{footer}

    <script src="js/main.js"></script>
</body>
</html>
"""

    def _html_contact(self, config: ProjectConfig) -> str:
        """Generate contact.html page."""
        css_links = self._html_css_links(config)
        header = self._html_header(config, "contact")
        footer = self._html_footer(config)

        return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="description" content="Contact {config.name}">
    <title>Contact - {config.name}</title>{css_links}
</head>
<body>
{header}

    <main class="main">
        <section class="page-header">
            <div class="container">
                <h1 class="page-header__title">Contact Us</h1>
                <p class="page-header__subtitle">Get in touch</p>
            </div>
        </section>

        <section class="content">
            <div class="container">
                <form class="contact-form" action="#" method="post">
                    <div class="form-group">
                        <label for="name" class="form-label">Name</label>
                        <input type="text" id="name" name="name" class="form-input" required>
                    </div>
                    <div class="form-group">
                        <label for="email" class="form-label">Email</label>
                        <input type="email" id="email" name="email" class="form-input" required>
                    </div>
                    <div class="form-group">
                        <label for="message" class="form-label">Message</label>
                        <textarea id="message" name="message" class="form-textarea" rows="5" required></textarea>
                    </div>
                    <button type="submit" class="btn btn--primary">Send Message</button>
                </form>
            </div>
        </section>
    </main>

{footer}

    <script src="js/main.js"></script>
</body>
</html>
"""

    def _css_reset(self) -> str:
        """Generate CSS reset file."""
        return """/* CSS Reset */
* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

html {
    font-size: 16px;
    -webkit-font-smoothing: antialiased;
    -moz-osx-font-smoothing: grayscale;
}

body {
    line-height: 1.6;
}

img {
    max-width: 100%;
    height: auto;
    display: block;
}

a {
    text-decoration: none;
    color: inherit;
}

button {
    border: none;
    background: none;
    cursor: pointer;
    font: inherit;
}

ul {
    list-style: none;
}
"""

    def _css_main(self, config: ProjectConfig) -> str:
        """Generate main stylesheet with BEM methodology."""
        if config.css_framework == CSSFramework.TAILWIND:
            return """@tailwind base;
@tailwind components;
@tailwind utilities;

/* Custom styles can be added here */
"""

        return """/* Variables */
:root {
    --color-primary: #3b82f6;
    --color-primary-dark: #2563eb;
    --color-secondary: #64748b;
    --color-text: #1e293b;
    --color-text-light: #64748b;
    --color-background: #ffffff;
    --color-background-light: #f8fafc;
    --color-border: #e2e8f0;

    --font-sans: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;

    --spacing-xs: 0.5rem;
    --spacing-sm: 1rem;
    --spacing-md: 1.5rem;
    --spacing-lg: 2rem;
    --spacing-xl: 3rem;

    --border-radius: 0.5rem;
    --box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06);
}

/* Global Styles */
body {
    font-family: var(--font-sans);
    color: var(--color-text);
    background-color: var(--color-background);
}

.container {
    max-width: 1200px;
    margin: 0 auto;
    padding: 0 var(--spacing-md);
}

/* Header & Navigation */
.header {
    background-color: var(--color-background);
    border-bottom: 1px solid var(--color-border);
    position: sticky;
    top: 0;
    z-index: 100;
}

.nav {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: var(--spacing-sm) var(--spacing-md);
    max-width: 1200px;
    margin: 0 auto;
}

.nav__logo a {
    font-size: 1.5rem;
    font-weight: 700;
    color: var(--color-primary);
}

.nav__menu {
    display: flex;
    gap: var(--spacing-md);
}

.nav__link {
    color: var(--color-text-light);
    transition: color 0.2s;
}

.nav__link:hover,
.nav__link--active {
    color: var(--color-primary);
}

/* Hero Section */
.hero {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    padding: var(--spacing-xl) 0;
    text-align: center;
}

.hero__content {
    max-width: 800px;
    margin: 0 auto;
    padding: 0 var(--spacing-md);
}

.hero__title {
    font-size: 3rem;
    font-weight: 800;
    margin-bottom: var(--spacing-sm);
}

.hero__subtitle {
    font-size: 1.25rem;
    margin-bottom: var(--spacing-lg);
    opacity: 0.9;
}

/* Buttons */
.btn {
    display: inline-block;
    padding: var(--spacing-sm) var(--spacing-lg);
    border-radius: var(--border-radius);
    font-weight: 600;
    transition: all 0.2s;
}

.btn--primary {
    background-color: white;
    color: var(--color-primary);
}

.btn--primary:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
}

/* Features Section */
.features {
    padding: var(--spacing-xl) 0;
}

.section__title {
    font-size: 2rem;
    font-weight: 700;
    text-align: center;
    margin-bottom: var(--spacing-lg);
}

.features__grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
    gap: var(--spacing-lg);
    margin-top: var(--spacing-lg);
}

.feature {
    padding: var(--spacing-lg);
    background-color: var(--color-background-light);
    border-radius: var(--border-radius);
    text-align: center;
}

.feature__title {
    font-size: 1.25rem;
    font-weight: 600;
    margin-bottom: var(--spacing-sm);
    color: var(--color-primary);
}

.feature__text {
    color: var(--color-text-light);
}

/* Page Header */
.page-header {
    background-color: var(--color-background-light);
    padding: var(--spacing-xl) 0;
    text-align: center;
}

.page-header__title {
    font-size: 2.5rem;
    font-weight: 700;
    margin-bottom: var(--spacing-sm);
}

.page-header__subtitle {
    font-size: 1.125rem;
    color: var(--color-text-light);
}

/* Content Section */
.content {
    padding: var(--spacing-xl) 0;
}

/* Contact Form */
.contact-form {
    max-width: 600px;
    margin: 0 auto;
}

.form-group {
    margin-bottom: var(--spacing-md);
}

.form-label {
    display: block;
    margin-bottom: var(--spacing-xs);
    font-weight: 600;
}

.form-input,
.form-textarea {
    width: 100%;
    padding: var(--spacing-sm);
    border: 1px solid var(--color-border);
    border-radius: var(--border-radius);
    font-family: inherit;
}

.form-input:focus,
.form-textarea:focus {
    outline: none;
    border-color: var(--color-primary);
}

/* Footer */
.footer {
    background-color: var(--color-background-light);
    border-top: 1px solid var(--color-border);
    padding: var(--spacing-lg) 0;
    text-align: center;
    color: var(--color-text-light);
}

/* Responsive */
@media (max-width: 768px) {
    .hero__title {
        font-size: 2rem;
    }

    .nav__menu {
        gap: var(--spacing-sm);
    }

    .features__grid {
        grid-template-columns: 1fr;
    }
}
"""

    def _js_main(self) -> str:
        """Generate main JavaScript file."""
        return """// Main JavaScript file
console.log('Website loaded successfully');

// Mobile menu toggle (if needed)
document.addEventListener('DOMContentLoaded', () => {
    // Add your JavaScript here

    // Example: Smooth scrolling for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth'
                });
            }
        });
    });
});
"""


def main():
    """Main entry point for CLI usage."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Create a new project with IDE-grade configuration",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s html my-site --tailwind
  %(prog)s react my-app --typescript --tailwind
  %(prog)s nextjs my-app --database postgresql --orm prisma
  %(prog)s fastapi my-api --database postgresql --orm sqlalchemy
  %(prog)s python my-lib --pytest --ruff
        """
    )
    parser.add_argument("type", help="Project type (html, react, nextjs, vue, fastapi, django, etc.)")
    parser.add_argument("name", help="Project name")
    parser.add_argument("--description", help="Project description")
    parser.add_argument("--author", help="Author name")
    parser.add_argument("--license", default="MIT", help="License type")
    parser.add_argument("--version", default="0.1.0", help="Initial version")

    # Language options
    parser.add_argument("--typescript", action="store_true", help="Use TypeScript")
    parser.add_argument("--javascript", action="store_true", help="Use JavaScript")

    # Framework options
    parser.add_argument("--tailwind", action="store_true", help="Include Tailwind CSS")
    parser.add_argument("--database", choices=["sqlite", "postgresql", "mysql", "mongodb"], help="Database type")
    parser.add_argument("--orm", choices=["prisma", "drizzle", "typeorm", "sqlalchemy", "sqlmodel"], help="ORM/ODM")

    # Tooling
    parser.add_argument("--eslint", action="store_true", default=True, help="Include ESLint")
    parser.add_argument("--prettier", action="store_true", default=True, help="Include Prettier")
    parser.add_argument("--testing", action="store_true", default=True, help="Include testing setup")
    parser.add_argument("--docker", action="store_true", help="Include Docker configuration")
    parser.add_argument("--github-actions", action="store_true", help="Include GitHub Actions CI")

    # Python-specific
    parser.add_argument("--ruff", action="store_true", default=True, help="Include Ruff (Python)")
    parser.add_argument("--mypy", action="store_true", default=True, help="Include mypy (Python)")
    parser.add_argument("--pytest", action="store_true", default=True, help="Include pytest (Python)")

    # Additional features (comma-separated)
    parser.add_argument("--features", help="Additional features (comma-separated)")

    args = parser.parse_args()

    # Determine language
    language = Language.TYPESCRIPT if args.typescript else Language.JAVASCRIPT
    if args.type in ["python", "fastapi", "django", "flask"]:
        language = Language.PYTHON

    # Parse features
    features = args.features.split(",") if args.features else []

    # Create config
    config = ProjectConfig(
        name=args.name,
        project_type=args.type,
        language=language,
        description=args.description or "",
        author=args.author or "",
        license=args.license,
        version=args.version,
        css_framework=CSSFramework.TAILWIND if args.tailwind else CSSFramework.NONE,
        database=Database(args.database) if args.database else Database.NONE,
        orm=ORM(args.orm) if args.orm else ORM.NONE,
        eslint=args.eslint,
        prettier=args.prettier,
        testing=args.testing,
        docker=args.docker,
        github_actions=args.github_actions,
        ruff=args.ruff,
        mypy=args.mypy,
        pytest=args.pytest,
        features=features,
    )

    scaffolder = ProjectScaffolder()
    try:
        project_path = scaffolder.create_project(config)
        print(f"✅ Created {args.type} project '{args.name}' at {project_path}")
        print(f"\nNext steps:")
        print(f"  cd {args.name}")
        if language == Language.PYTHON:
            print(f"  python -m venv .venv && source .venv/bin/activate")
            print(f"  pip install -r requirements.txt")
        else:
            print(f"  npm install")
            print(f"  npm run dev")
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
