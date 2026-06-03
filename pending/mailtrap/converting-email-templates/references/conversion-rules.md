# Template Conversion Rules

Reference for the template converter skill and script. Each provider section defines the exact patterns to find and replace, plus patterns that cannot be auto-converted and must be flagged.

## Provider: SendGrid

**Compatibility**: High - both use Handlebars. Only helper-specific patterns need conversion.

### Auto-convertible patterns

| # | Find | Replace | Notes |
|---|------|---------|-------|
| SG1 | `{{insert VARNAME "default=FALLBACK"}}` | `{{#if VARNAME}}{{VARNAME}}{{else}}FALLBACK{{/if}}` | Capture VARNAME and FALLBACK from the insert helper |
| SG2 | `{{insert VARNAME}}` (no default) | `{{VARNAME}}` | insert helper with no default = plain variable |

**Regex for SG1:**
```
\{\{insert\s+(\w[\w.]*)\s+"default=([^"]+)"\}\}
```
Replace: `{{#if $1}}{{$1}}{{else}}$2{{/if}}`

**Regex for SG2:**
```
\{\{insert\s+(\w[\w.]*)\}\}
```
Replace: `{{$1}}`

### Flag-only patterns (cannot auto-convert)

| # | Pattern | Reason | Flag message |
|---|---------|--------|-------------|
| SG-F1 | `{{formatDate EXPR "FORMAT"}}` | Requires server-side date formatting | `MANUAL: Replace {{formatDate ...}} with a pre-formatted string variable. Format the date in your application before passing it as a template variable.` |
| SG-F2 | `{{#greaterThan ...}}` | Requires app-layer logic | `MANUAL: Move greaterThan comparison to your application. Pass a boolean template variable instead.` |
| SG-F3 | `{{#lessThan ...}}` | Requires app-layer logic | `MANUAL: Move lessThan comparison to your application. Pass a boolean template variable instead.` |
| SG-F4 | `{{#notEquals ...}}` | Requires app-layer logic | `MANUAL: Move notEquals comparison to your application. Pass a boolean template variable instead.` |
| SG-F5 | `{{#and ...}}` | Requires app-layer logic | `MANUAL: Move AND logic to your application. Pass a single boolean template variable instead.` |
| SG-F6 | `{{#or ...}}` | Requires app-layer logic | `MANUAL: Move OR logic to your application. Pass a single boolean template variable instead.` |
| SG-F7 | `{{#length ...}}` | Requires app-layer logic | `MANUAL: Move length check to your application. Pass a boolean or count as a template variable instead.` |

**Regex to detect all flaggable patterns:**
```
\{\{#?(formatDate|greaterThan|lessThan|notEquals|and|or|length)\s
```

---

## Provider: Mailgun

**Compatibility**: High - both use Handlebars. No syntax conversion needed.

### Auto-convertible patterns

None. Template markup is identical.

### API field changes (informational, not template-level)

| Old field | New field |
|-----------|-----------|
| `template` (name string) | `template_uuid` |
| `t:variables` (JSON string) | `template_variables` (JSON object) |

### Flag-only patterns

| # | Pattern | Reason | Flag message |
|---|---------|--------|-------------|
| MG-F1 | `%recipient.VARNAME%` | Mailgun batch variable syntax, not Handlebars | `MANUAL: Mailgun batch variable %recipient.X% detected. This is not part of the Handlebars template - it is resolved by Mailgun's batch API. In Mailtrap, send separate API calls per recipient with their own template_variables.` |

**Regex:**
```
%recipient\.\w+%
```

---

## Provider: Mandrill (Handlebars mode)

**Compatibility**: High - same Handlebars engine. No syntax changes.

### Auto-convertible patterns

None. Template markup is identical when `merge_language: "handlebars"`.

### Flag-only patterns

| # | Pattern | Reason | Flag message |
|---|---------|--------|-------------|
| MD-F1 | `mc:edit="REGION"` | Mandrill editable content regions | `MANUAL: mc:edit region detected. Mailtrap does not support editable regions. Replace this with a Handlebars variable (e.g., {{REGION}}) and pass the content via template_variables.` |

**Regex:**
```
mc:edit="([^"]+)"
```

---

## Provider: Mandrill (Mailchimp merge tags)

**Compatibility**: Medium - requires full merge tag to Handlebars conversion.

### Auto-convertible patterns

| # | Find | Replace | Notes |
|---|------|---------|-------|
| MC1 | `*\|VARNAME\|*` | `{{varname}}` | Lowercase the variable name (Handlebars convention) |
| MC2 | `*\|IF:VARNAME\|*` | `{{#if varname}}` | Opening conditional |
| MC3 | `*\|ELSE:\|*` | `{{else}}` | Else branch |
| MC4 | `*\|END:IF\|*` | `{{/if}}` | Closing conditional |
| MC5 | `*\|DATE:FORMAT\|*` | Flag | Date formatting - cannot auto-convert |

**Regex for MC1 (general variable):**
```
\*\|([A-Z_][A-Z0-9_]*)\|\*
```
Replace: `{{$1_lowercased}}`

Note: must NOT match IF:, ELSE:, END:IF, DATE: prefixed tags. Apply MC2-MC4 first, then MC1 on remaining.

**Regex for MC2:**
```
\*\|IF:([A-Z_][A-Z0-9_]*)\|\*
```
Replace: `{{#if $1_lowercased}}`

**Regex for MC3:**
```
\*\|ELSE:\|\*
```
Replace: `{{else}}`

**Regex for MC4:**
```
\*\|END:IF\|\*
```
Replace: `{{/if}}`

### Flag-only patterns

| # | Pattern | Reason | Flag message |
|---|---------|--------|-------------|
| MC-F1 | `*\|DATE:FORMAT\|*` | Date formatting | `MANUAL: Mailchimp date merge tag detected. Format the date server-side and pass as a string variable.` |
| MC-F2 | `mc:edit="REGION"` | Same as Mandrill Handlebars mode | See MD-F1 |

---

## Provider: Postmark

**Compatibility**: Medium-High - Mustachio is close to Handlebars but conditionals differ.

### Auto-convertible patterns

| # | Find | Replace | Notes |
|---|------|---------|-------|
| PM1 | `{{#VARNAME}}...{{/VARNAME}}` | `{{#if VARNAME}}...{{/if VARNAME}}` | Truthy conditional. The tricky part: must distinguish from `{{#each}}`, `{{#if}}`, `{{#unless}}`, `{{#with}}` which are already valid Handlebars. Only convert when VARNAME is NOT a Handlebars keyword. |
| PM2 | `{{^VARNAME}}...{{/VARNAME}}` | `{{#unless VARNAME}}...{{/unless}}` | Falsy/inverted conditional |
| PM3 | `{{&VARNAME}}` | `{{{VARNAME}}}` | Alternate unescaped HTML syntax |

**Regex for PM1:**
Match `{{#` followed by a name that is NOT `if`, `unless`, `each`, `with`, `else`:
```
\{\{#(?!if\b|unless\b|each\b|with\b)(\w[\w.]*)\}\}
```
Replace: `{{#if $1}}`

Corresponding closing tag:
```
\{\{/(?!if\b|unless\b|each\b|with\b)(\w[\w.]*)\}\}
```
Replace: `{{/if}}` (but only when this tag was opened by a PM1-matched opening tag, not a legitimate `{{#each items}}...{{/items}}` - this is the hard part)

**Strategy for PM1 closing tags**: Track which opening tags were converted. For each `{{/VARNAME}}`, check if a corresponding `{{#VARNAME}}` was converted to `{{#if VARNAME}}`. If yes, replace with `{{/if}}`. This requires stateful processing, not pure regex.

**Regex for PM2:**
```
\{\{\^(\w[\w.]*)\}\}
```
Replace: `{{#unless $1}}`

Closing tag for PM2: same `{{/VARNAME}}` pattern, replace with `{{/unless}}`.

**Regex for PM3:**
```
\{\{&(\w[\w.]*)\}\}
```
Replace: `{{{$1}}}`

### Flag-only patterns

| # | Pattern | Reason | Flag message |
|---|---------|--------|-------------|
| PM-F1 | Ambiguous `{{/VARNAME}}` closing tags | Could close a truthy or falsy block | `WARNING: Closing tag {{/VARNAME}} detected. Verify it matches the correct opening block ({{#if}} or {{#unless}}).` |

---

## Provider: Brevo

**Compatibility**: Low - completely different template language. Full rewrite needed.

### Auto-convertible patterns

| # | Find | Replace | Notes |
|---|------|---------|-------|
| BR1 | `{{ params.VARNAME }}` | `{{VARNAME}}` | Remove params. prefix. Handle nested: `params.order.item` → `order.item` |
| BR2 | `{% if params.CONDITION %}` | `{{#if CONDITION}}` | Convert Django conditional opener |
| BR3 | `{% else %}` | `{{else}}` | Else branch |
| BR4 | `{% endif %}` | `{{/if}}` | Close conditional |
| BR5 | `{% for ITEM in params.LIST %}` | `{{#each LIST}}` | Convert loop. Note: loop variable changes from ITEM to `this` |
| BR6 | `{% endfor %}` | `{{/each}}` | Close loop |
| BR7 | `{{ ITEM.PROPERTY }}` (inside a for loop) | `{{this.PROPERTY}}` | Replace loop variable with `this` |

**Regex for BR1:**
```
\{\{\s*params\.(\w[\w.]*)\s*\}\}
```
Replace: `{{$1}}`

**Regex for BR2:**
```
\{%\s*if\s+params\.(\w[\w.]*)\s*%\}
```
Replace: `{{#if $1}}`

**Regex for BR3:**
```
\{%\s*else\s*%\}
```
Replace: `{{else}}`

**Regex for BR4:**
```
\{%\s*endif\s*%\}
```
Replace: `{{/if}}`

**Regex for BR5:**
```
\{%\s*for\s+(\w+)\s+in\s+params\.(\w[\w.]*)\s*%\}
```
Capture: ITEM=$1, LIST=$2. Replace: `{{#each $2}}`
Then track ITEM name for BR7 replacements within this loop scope.

**Regex for BR6:**
```
\{%\s*endfor\s*%\}
```
Replace: `{{/each}}`

### Flag-only patterns

| # | Pattern | Reason | Flag message |
|---|---------|--------|-------------|
| BR-F1 | `{{ params.VAR \| default:"VALUE" }}` | Filter-based default | `MANUAL: Brevo default filter detected. Replace with {{#if VAR}}{{VAR}}{{else}}VALUE{{/if}}. The script attempts this conversion but verify the result.` |
| BR-F2 | `{{ params.VAR \| date:"FORMAT" }}` | Filter-based date formatting | `MANUAL: Brevo date filter detected. Format the date server-side and pass as a string variable.` |
| BR-F3 | Any `\|` filter not covered above | Unknown filter | `MANUAL: Brevo filter detected. Mailtrap Handlebars does not support filters. Move this logic to your application.` |
| BR-F4 | Nested `{% for %}` loops | Loop variable scoping gets complex | `WARNING: Nested loop detected. Verify that {{this}} references resolve correctly in Handlebars context.` |

**Regex for BR-F1 (attempt auto-convert):**
```
\{\{\s*params\.(\w[\w.]*)\s*\|\s*default:"([^"]+)"\s*\}\}
```
Replace: `{{#if $1}}{{$1}}{{else}}$2{{/if}}`

**Regex for BR-F2:**
```
\{\{\s*params\.(\w[\w.]*)\s*\|\s*date:"[^"]+"\s*\}\}
```
Flag only.

---

## Provider: Amazon SES

**Compatibility**: High - both use Handlebars. No syntax conversion needed.

### Auto-convertible patterns

None. Template markup is identical.

### Flag-only patterns

None for template syntax. API field changes only:

| Old field | New field |
|-----------|-----------|
| `TemplateName` or `TemplateArn` | `template_uuid` |
| `TemplateData` (escaped JSON string) | `template_variables` (JSON object) |

---

## Conversion priority order

When applying conversions, process in this order to avoid conflicts:

1. **Flag-only patterns first** (detect and collect, do not modify)
2. **Brevo filter patterns** (BR-F1 auto-convert attempt, BR-F2/F3 flag)
3. **Brevo structural patterns** (BR2-BR6, then BR1, then BR7)
4. **Mandrill merge tag patterns** (MC2-MC4 first, then MC1)
5. **SendGrid helper patterns** (SG1, SG2)
6. **Postmark conditional patterns** (PM1, PM2, PM3)
