# Scanlume API Contract / Contrato da API do Scanlume

This reference covers the current public image OCR API exposed behind [https://www.scanlume.com/](https://www.scanlume.com/).

Esta referencia cobre a API publica atual de OCR de imagem exposta por [https://www.scanlume.com/](https://www.scanlume.com/).

## English

### Public base URL

- Default base URL: `https://api.scanlume.com`

### Public image OCR endpoint

- Method: `POST`
- Path: `/v1/api/ocr`
- Auth header: `Authorization: Bearer <SCANLUME_API_KEY>`
- Content type: `application/json`

### Request body

```json
{
  "mode": "formatted",
  "base64": "data:image/png;base64,..."
}
```

### Important constraints

- `base64` must be a full data URL.
- Current public v1 does **not** support:
  - multipart upload
  - remote file URL input
  - public PDF OCR jobs

### Mode rules

- `simple`
  - raw plain text
  - 1 credit per image

- `formatted`
  - text blocks plus table-aware structured output
  - Markdown and HTML friendly
  - 2 credits per image

### Public PDF route status

- Route: `POST /v1/api/pdf/jobs`
- Current public behavior: beta waitlist / not generally available yet

Do not present this route as publicly available until the product team opens it.

### Typical success response

```json
{
  "request_id": "uuid",
  "status": "success",
  "plan": "starter",
  "mode": "formatted",
  "result": {
    "txt": "...",
    "md": "...",
    "html": "...",
    "preview": "...",
    "blocks": [],
    "tableSummary": {
      "tableCount": 1,
      "rowGroupCount": 2,
      "recordCount": 7
    }
  },
  "credits_charged": 2,
  "remaining_credits": 9998
}
```

### Common error codes

- `api_invalid_payload`
- `api_ocr_failed`
- `api_account_rate_limit`
- `pdf_api_beta_waitlist`

## Portugues (Brasil)

### Base URL publica

- Base URL padrao: `https://api.scanlume.com`

### Endpoint publico de OCR de imagem

- Metodo: `POST`
- Path: `/v1/api/ocr`
- Header de auth: `Authorization: Bearer <SCANLUME_API_KEY>`
- Tipo de conteudo: `application/json`

### Corpo da requisicao

```json
{
  "mode": "formatted",
  "base64": "data:image/png;base64,..."
}
```

### Restricoes importantes

- `base64` precisa ser uma data URL completa.
- A v1 publica atual **nao** suporta:
  - multipart upload
  - URL remota de arquivo
  - jobs publicos de OCR para PDF

### Regras de modo

- `simple`
  - texto puro
  - 1 credito por imagem

- `formatted`
  - blocos de texto mais saida estruturada com suporte a tabelas
  - amigavel para Markdown e HTML
  - 2 creditos por imagem

### Status da rota publica de PDF

- Rota: `POST /v1/api/pdf/jobs`
- Comportamento publico atual: beta waitlist / ainda nao disponivel de forma geral

Nao apresente essa rota como publica enquanto o time de produto nao liberar o acesso.

### Resposta tipica de sucesso

```json
{
  "request_id": "uuid",
  "status": "success",
  "plan": "starter",
  "mode": "formatted",
  "result": {
    "txt": "...",
    "md": "...",
    "html": "...",
    "preview": "...",
    "blocks": [],
    "tableSummary": {
      "tableCount": 1,
      "rowGroupCount": 2,
      "recordCount": 7
    }
  },
  "credits_charged": 2,
  "remaining_credits": 9998
}
```

### Codigos de erro comuns

- `api_invalid_payload`
- `api_ocr_failed`
- `api_account_rate_limit`
- `pdf_api_beta_waitlist`
