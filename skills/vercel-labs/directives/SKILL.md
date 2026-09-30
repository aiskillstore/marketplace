---
name: directives
description: Pre-built custom directives for json-render — formatting, math, string manipulation, and i18n. Use when working with @json-render/directives, defining custom directives with defineDirective, or adding $format, $math, $concat, $count, $truncate, $pluralize, $join, or $t to specs.
---

# @json-render/directives

Pre-built custom directives for `@json-render/core`. Drop them into your catalog and renderer to add formatting, math, string manipulation, and i18n.

## Quick Start

```typescript
import { standardDirectives } from '@json-render/directives';

// Wire into prompt generation
const prompt = catalog.prompt({ directives: standardDirectives });

// Wire into the renderer (React example)
import { JSONUIProvider, Renderer } from '@json-render/react';

<JSONUIProvider registry={registry} directives={standardDirectives}>
  <Renderer spec={spec} registry={registry} />
</JSONUIProvider>
```

To add factory directives like `createI18nDirective`, spread the array:

```typescript
import { standardDirectives, createI18nDirective } from '@json-render/directives';

const directives = [...standardDirectives, createI18nDirective(config)];
```

## Defining Custom Directives

Use `defineDirective` from `@json-render/core`:

```typescript
import { defineDirective, resolvePropValue } from '@json-render/core';
import { z } from 'zod';

const doubleDirective = defineDirective({
  name: '$double',
  description: 'Double a numeric value.',
  schema: z.object({
    $double: z.unknown(),
  }),
  resolve(value, ctx) {
    const resolved = resolvePropValue(value.$double, ctx);
    return (resolved as number) * 2;
  },
});
```

Rules:
- Name must start with `$`
- Name must not conflict with built-in keys (`$state`, `$cond`, `$computed`, `$template`, `$item`, `$index`, `$bindState`, `$bindItem`)
- Resolvers should call `resolvePropValue` on sub-values to support composition

## Built-in Directives

### `$format` — Locale-aware value formatting

Formats values using `Intl` formatters. Supports `date`, `currency`, `number`, and `percent`.

```json
{ "$format": "currency", "value": { "$state": "/cart/total" }, "currency": "USD" }
{ "$format": "date", "value": { "$state": "/user/createdAt" } }
{ "$format": "number", "value": 1234567, "notation": "compact" }
{ "$format": "percent", "value": 0.75 }
{ "$format": "date", "value": { "$state": "/post/createdAt" }, "style": "relative" }
```

Fields: `$format` (date | currency | number | percent), `value` (any expression), `locale?` (string), `currency?` (string, default "USD"), `notation?` (string), `style?` ("relative" for relative dates), `options?` (extra Intl options).

### `$math` — Arithmetic operations

```json
{ "$math": "add", "a": { "$state": "/subtotal" }, "b": { "$state": "/tax" } }
{ "$math": "round", "a": 3.7 }
```

Operations: `add`, `subtract`, `multiply`, `divide`, `mod`, `min`, `max`, `round`, `floor`, `ceil`, `abs`. Unary ops (`round`, `floor`, `ceil`, `abs`) only use `a`. Division by zero returns `0`.

Fields: `$math` (operation enum), `a?` (first operand, default 0), `b?` (second operand, default 0).

### `$concat` — String concatenation

```json
{ "$concat": [{ "$state": "/user/firstName" }, " ", { "$state": "/user/lastName" }] }
```

Fields: `$concat` (array of values to resolve and join into a string).

### `$count` — Array/string length

```json
{ "$count": { "$state": "/cart/items" } }
```

Returns `.length` of arrays or strings, `0` for other types.

Fields: `$count` (value to count).

### `$truncate` — Text truncation

```json
{ "$truncate": { "$state": "/post/body" }, "length": 140, "suffix": "..." }
```

Fields: `$truncate` (value to truncate), `length?` (max chars, default 100), `suffix?` (string, default "...").

### `$pluralize` — Singular/plural forms

```json
{ "$pluralize": { "$state": "/cart/itemCount" }, "one": "item", "other": "items", "zero": "no items" }
```

Output: `"3 items"`, `"1 item"`, or `"no items"`.

Fields: `$pluralize` (count value), `one` (singular label), `other` (plural label), `zero?` (zero label).

### `$join` — Join array elements

```json
{ "$join": { "$state": "/tags" }, "separator": ", " }
```

Fields: `$join` (array to join), `separator?` (string, default ", ").

### `createI18nDirective` — Internationalization factory

```typescript
import { createI18nDirective } from '@json-render/directives';

const tDirective = createI18nDirective({
  locale: 'en',
  messages: {
    en: { "greeting": "Hello, {{name}}!", "checkout.submit": "Place Order" },
    es: { "greeting": "Hola, {{name}}!", "checkout.submit": "Realizar Pedido" },
  },
  fallbackLocale: 'en',
});
```

Usage in specs:

```json
{ "$t": "checkout.submit" }
{ "$t": "greeting", "params": { "name": { "$state": "/user/name" } } }
```

Fields: `$t` (translation key), `params?` (interpolation parameters, values accept expressions).

Config: `locale` (current locale), `messages` (Record<locale, Record<key, string>>), `fallbackLocale?` (fallback when key missing).

## Composition

Directives compose naturally — each resolver calls `resolvePropValue` on its inputs, so directives can wrap other directives or built-in expressions:

```json
{
  "$format": "currency",
  "value": { "$math": "multiply", "a": { "$state": "/price" }, "b": { "$state": "/qty" } },
  "currency": "USD"
}
```

Resolves inside-out: `$state` reads from state, `$math` multiplies, `$format` formats as currency.

## Wiring into Renderers

All four renderers (React, Vue, Svelte, Solid) accept `directives` on their provider and `createRenderer` output:

```tsx
// Provider pattern
<JSONUIProvider registry={registry} directives={directives}>
  <Renderer spec={spec} registry={registry} />
</JSONUIProvider>

// createRenderer pattern
const MyRenderer = createRenderer(catalog, components);
<MyRenderer spec={spec} directives={directives} />
```

For prompt generation, pass the same array:

```typescript
const prompt = catalog.prompt({ directives });
```

## Key Exports

| Export | Purpose |
|--------|---------|
| `formatDirective` | `$format` directive definition |
| `mathDirective` | `$math` directive definition |
| `concatDirective` | `$concat` directive definition |
| `countDirective` | `$count` directive definition |
| `truncateDirective` | `$truncate` directive definition |
| `pluralizeDirective` | `$pluralize` directive definition |
| `joinDirective` | `$join` directive definition |
| `createI18nDirective` | Factory for `$t` i18n directive |
| `standardDirectives` | Array of all 7 non-factory directives |
| `I18nConfig` | Type for i18n configuration |
