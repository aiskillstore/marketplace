# Saleor Storefront Skill

Universal agent skill for building storefronts on the [Saleor](https://saleor.io) e-commerce platform. Framework-agnostic — applies to Next.js, Remix, Nuxt, or any custom setup.

## Installation

```shell
npx skills add saleor/agent-skills --skill saleor-storefront
```

## What's Included

7 rules across 4 categories covering Saleor's storefront API:

| Category | Rules | Topics |
| --- | --- | --- |
| API | `api-data-model`, `api-permissions`, `api-graphql-patterns`, `api-investigation` | Nullable fields, pricing, permissions, codegen, source investigation |
| Products | `products-variants` | Variant model, selection attributes, pricing, UX patterns |
| Checkout | `checkout-lifecycle` | Session lifecycle, payment errors, debugging |
| Channels | `channels-purchasability` | Fulfillment triangle, multi-currency, purchasability checklist |

## Structure

```
saleor-storefront/
├── SKILL.md              # Overview and quick reference (agents read this first)
├── AGENTS.md             # Full compiled document (all rules expanded)
├── README.md             # This file (for humans)
├── rules/                # Individual rule files
│   ├── api-data-model.md
│   ├── api-permissions.md
│   ├── api-graphql-patterns.md
│   ├── api-investigation.md
│   ├── products-variants.md
│   ├── checkout-lifecycle.md
│   └── channels-purchasability.md
└── references/           # Supporting deep-dive documentation
    └── saleor-key-directories.md
```

## Who Is This For?

- **Any Saleor storefront** — framework-agnostic API patterns
- **AI agents** building or maintaining Saleor-powered stores
- **Developers** looking for a quick reference on Saleor's data model

For framework-specific patterns (caching, component architecture, file locations), see project-level skills like `saleor-paper-storefront`.

## License

MIT
