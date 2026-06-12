# Claude academic TI news searcher

## Propósito

Encontrar noticias recientes de TI, vincularlas con evidencia científica verificable y entregar **metadatos enriquecidos** listos para investigación doctoral: tipo y estado de publicación, fechas, venue, cuartil/percentil, abstracts en lenguaje claro, impactos, autores con índice h y créditos.

## Archivos de la skill


| Archivo                       | Uso                                                     |
| ----------------------------- | ------------------------------------------------------- |
| `SKILL.md`                    | Instrucciones principales para el agente                |
| `output-schema.json`          | Esquema JSON de salida (validación y contrato de datos) |
| `business-prompt-template.md` | Plantilla de prompt para el usuario                     |
| `examples.md`                 | Ejemplos de entrada/salida en texto y JSON              |


## Qué debe entregar

### Por cada hallazgo


| Campo                 | Descripción                                           |
| --------------------- | ----------------------------------------------------- |
| Noticia               | Título, fuente, fecha, URL, tipo                      |
| Tipo de publicación   | Artículo, preprint, congreso, revisión, etc.          |
| Estado                | Publicado, preprint, en revisión, retractado…         |
| Fecha                 | ISO 8601 + precisión (día/mes/año)                    |
| Venue                 | Revista o lugar, ISSN, editorial, indexación          |
| Cuartil / percentil   | Q1-Q4 o percentil SJR; fuente de la métrica           |
| Abstract original     | Texto tal como en la fuente                           |
| Abstract simplificado | Reescritura en lenguaje claro (~120 palabras)         |
| Puntos importantes    | 3-7 bullets con hallazgos y limitaciones              |
| Impactos              | Científico, técnico, social, doctoral                 |
| Autores               | Nombre, ORCID, afiliación, rol, **h-index**, créditos |
| Créditos              | CRediT del paper cuando exista                        |


### Cierre de la respuesta

- Resumen ejecutivo
- Ranking priorizado
- Preguntas doctorales sugeridas
- Riesgos metodológicos
- Vacíos de investigación

## Formatos de salida


| Valor   | Comportamiento                                            |
| ------- | --------------------------------------------------------- |
| `json`  | Solo JSON válido según `output-schema.json`               |
| `texto` | Solo bloque de texto plano estructurado                   |
| `ambos` | Texto plano + separador `--- JSON ---` + JSON *(default)* |


## Entradas esperadas

- **Tema** TI (obligatorio)
- **Ventana temporal** (default: 90 días)
- **Profundidad**: breve / media / profunda
- **Región** e idioma (opcional)
- **Formato salida**: json / texto / ambos

## Fuentes gratuitas

OpenAlex, Crossref, DOAJ, arXiv, PubMed, Semantic Scholar, SCImago JR (consulta web para cuartil).

## Calidad mínima

- Diferenciar **noticia** vs **evidencia científica**.
- No inventar DOI, cuartil, h-index ni fechas.
- Marcar `no_confirmado` / `null` cuando falte verificación.
- Papers retractados: marcar y no usar como evidencia principal.

## Uso rápido

1. Cargar `SKILL.md` como instrucción del agente.
2. Completar `business-prompt-template.md` o usar el ejemplo mínimo.
3. Validar JSON contra `output-schema.json` si aplica.
4. Verificar DOI y cuartil manualmente en hallazgos críticos.

