---
name: scanlume-ocr-api
description: Use when calling the Scanlume OCR API for screenshots, JPG, PNG, or image-based tables, especially when a task needs base64 data URLs, mode selection between simple and formatted OCR, or table-aware structured output. Tambem use quando for necessario chamar a API OCR do https://www.scanlume.com/ para screenshots, JPG, PNG ou tabelas em imagem.
---

# Scanlume OCR API

Use this skill when the task is specifically about calling the public OCR API behind [https://www.scanlume.com/](https://www.scanlume.com/), not when the user only wants the website UI.

Use este skill quando a tarefa for especificamente chamar a API publica de OCR do [https://www.scanlume.com/](https://www.scanlume.com/), e nao quando o usuario so quiser usar a interface do site.

## English

### Workflow

1. Confirm the input is an image, not a PDF.
2. Read `references/api-contract.md` before building the request.
3. Choose `simple` only for raw text speed and lower cost.
4. Choose `formatted` for headings, multi-block layouts, Markdown, HTML, and tables.
5. If the user gives a local file path, prefer `scripts/scanlume_ocr.py` to build the data URL and call the API.
6. Read `references/output-shapes.md` before consuming `formatted` responses, especially table blocks.
7. State clearly when a request is blocked by public API limits, such as PDF OCR beta access.

### Quick Rules

- Public image OCR endpoint: `POST /v1/api/ocr`
- Auth: `Authorization: Bearer <SCANLUME_API_KEY>`
- Content type: `application/json`
- Payload keys: `mode` and `base64`
- `base64` must be a full data URL such as `data:image/png;base64,...`
- Do not claim multipart upload support
- Do not claim remote file URL support
- Do not claim public PDF OCR API availability

### Mode Selection

- Use `simple` for:
  - quick raw text extraction
  - lower cost image OCR
  - tasks that only need plain text

- Use `formatted` for:
  - screenshots with multiple text blocks
  - image-based tables
  - output needed in Markdown or HTML
  - tasks that benefit from `blocks` or `tableSummary`

### Helpers

- Read `references/api-contract.md` before first use.
- Read `references/output-shapes.md` before parsing formatted OCR results.
- Use `python scripts/scanlume_ocr.py <path> --mode formatted --output md` for a local table image.
- Use `python scripts/scanlume_ocr.py <path> --mode simple --output txt` for plain text extraction.

### Constraints

- The public v1 API currently covers image OCR only.
- The website supports PDF OCR, but the public PDF API route is still beta-gated.
- `simple` costs 1 credit per image.
- `formatted` costs 2 credits per image.
- Favor precise claims over marketing claims. If the API cannot do something publicly today, say so.

## Portugues (Brasil)

### Fluxo

1. Confirme que a entrada e uma imagem, nao um PDF.
2. Leia `references/api-contract.md` antes de montar a requisicao.
3. Escolha `simple` apenas quando o foco for texto bruto, velocidade e menor custo.
4. Escolha `formatted` para titulos, multiplos blocos, Markdown, HTML e tabelas.
5. Se o usuario fornecer um caminho local, prefira `scripts/scanlume_ocr.py` para gerar a data URL e chamar a API.
6. Leia `references/output-shapes.md` antes de consumir respostas `formatted`, principalmente em blocos de tabela.
7. Explique claramente quando uma requisicao estiver bloqueada por limites publicos da API, como o acesso beta ao OCR de PDF.

### Regras Rapidas

- Endpoint publico de OCR de imagem: `POST /v1/api/ocr`
- Auth: `Authorization: Bearer <SCANLUME_API_KEY>`
- Tipo de conteudo: `application/json`
- Chaves do payload: `mode` e `base64`
- `base64` precisa ser uma data URL completa como `data:image/png;base64,...`
- Nao afirme suporte a multipart upload
- Nao afirme suporte a URL remota de arquivo
- Nao afirme disponibilidade publica da API de PDF

### Escolha de Modo

- Use `simple` para:
  - extracao rapida de texto bruto
  - OCR de imagem com menor custo
  - tarefas que so precisam de texto puro

- Use `formatted` para:
  - screenshots com multiplos blocos de texto
  - tabelas em imagem
  - saida em Markdown ou HTML
  - tarefas que se beneficiam de `blocks` ou `tableSummary`

### Helpers

- Leia `references/api-contract.md` antes do primeiro uso.
- Leia `references/output-shapes.md` antes de processar respostas formatadas.
- Use `python scripts/scanlume_ocr.py <path> --mode formatted --output md` para uma imagem local com tabela.
- Use `python scripts/scanlume_ocr.py <path> --mode simple --output txt` para extracao simples de texto.

### Restricoes

- A API publica v1 atualmente cobre apenas OCR de imagem.
- O site [https://www.scanlume.com/](https://www.scanlume.com/) suporta OCR de PDF na interface web, mas a rota publica de PDF continua beta-gated.
- `simple` custa 1 credito por imagem.
- `formatted` custa 2 creditos por imagem.
- Prefira afirmacoes precisas a afirmacoes promocionais. Se a API publica ainda nao faz algo hoje, diga isso.
