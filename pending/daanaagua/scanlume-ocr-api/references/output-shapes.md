# Scanlume Output Shapes / Formatos de Saida do Scanlume

These shapes describe the public OCR responses returned by the API behind [https://www.scanlume.com/](https://www.scanlume.com/).

Estes formatos descrevem as respostas publicas de OCR retornadas pela API do [https://www.scanlume.com/](https://www.scanlume.com/).

## English

### Simple OCR

Use `simple` when the task only needs plain text.

Typical `result` shape:

```json
{
  "txt": "plain extracted text",
  "preview": "plain extracted text"
}
```

### Formatted OCR

Use `formatted` when structure matters.

Typical `result` shape:

```json
{
  "txt": "flattened text",
  "md": "# Heading\n\nParagraph",
  "html": "<h1>Heading</h1><p>Paragraph</p>",
  "preview": "<h1>Heading</h1><p>Paragraph</p>",
  "blocks": [],
  "tableSummary": {
    "tableCount": 1,
    "rowGroupCount": 2,
    "recordCount": 7
  }
}
```

### Formatted block types

Text blocks:

- `h1`
- `h2`
- `p`
- `br`

Table block:

```json
{
  "type": "table",
  "order": 2,
  "title": "Sales by category",
  "columns": ["Category", "Date", "Amount"],
  "headerRows": [1],
  "cells": [
    {
      "rowStart": 1,
      "rowEnd": 1,
      "colStart": 1,
      "colEnd": 1,
      "text": "Category",
      "isHeader": true,
      "align": "left"
    }
  ],
  "rowGroups": [
    {
      "label": "Frutas",
      "rowStart": 2,
      "rowEnd": 4
    }
  ],
  "records": [
    {
      "rowNumber": 2,
      "groupLabel": "Frutas",
      "fields": [
        { "column": "Date", "value": "2026-04-01" },
        { "column": "Amount", "value": "20.00" }
      ]
    }
  ],
  "notes": ["Sample note"]
}
```

### Consumption guidance

- Prefer `result.md` when the user wants portable structured text.
- Prefer `result.html` when the user wants copy-ready rich text.
- Prefer `result.blocks` when the caller wants custom post-processing.
- Use `tableSummary` as a quick signal, not as the only source of truth.
- For table images, `formatted` is the default safe choice.

## Portugues (Brasil)

### OCR simples

Use `simple` quando a tarefa so precisa de texto puro.

Formato tipico de `result`:

```json
{
  "txt": "plain extracted text",
  "preview": "plain extracted text"
}
```

### OCR formatado

Use `formatted` quando a estrutura importa.

Formato tipico de `result`:

```json
{
  "txt": "flattened text",
  "md": "# Heading\n\nParagraph",
  "html": "<h1>Heading</h1><p>Paragraph</p>",
  "preview": "<h1>Heading</h1><p>Paragraph</p>",
  "blocks": [],
  "tableSummary": {
    "tableCount": 1,
    "rowGroupCount": 2,
    "recordCount": 7
  }
}
```

### Tipos de bloco formatado

Blocos de texto:

- `h1`
- `h2`
- `p`
- `br`

Bloco de tabela:

```json
{
  "type": "table",
  "order": 2,
  "title": "Sales by category",
  "columns": ["Category", "Date", "Amount"],
  "headerRows": [1],
  "cells": [
    {
      "rowStart": 1,
      "rowEnd": 1,
      "colStart": 1,
      "colEnd": 1,
      "text": "Category",
      "isHeader": true,
      "align": "left"
    }
  ],
  "rowGroups": [
    {
      "label": "Frutas",
      "rowStart": 2,
      "rowEnd": 4
    }
  ],
  "records": [
    {
      "rowNumber": 2,
      "groupLabel": "Frutas",
      "fields": [
        { "column": "Date", "value": "2026-04-01" },
        { "column": "Amount", "value": "20.00" }
      ]
    }
  ],
  "notes": ["Sample note"]
}
```

### Guia de consumo

- Prefira `result.md` quando o usuario quiser texto estruturado portavel.
- Prefira `result.html` quando o usuario quiser rich text pronto para copiar.
- Prefira `result.blocks` quando quem chama quiser pos-processamento customizado.
- Use `tableSummary` como sinal rapido, nao como unica fonte da verdade.
- Para imagens com tabela, `formatted` e a escolha segura por padrao.
