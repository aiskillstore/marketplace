# Doctoral TI News + CvLAC (Colombia)

Skill 04 — vigilancia científica en TI con **enfoque colombiano**: vincula noticias con papers, enriquece autores con **CvLAC/GrupLAC** y revistas con **Publindex**.

Evolución de la skill 01 optimizada para publicación en [Skillstore](https://skillstore.io/) con arquitectura de prompt, patrones de herramientas, casos límite y ejemplos concretos.

## Propósito

Para investigadores doctorales y equipos de vigilancia tecnológica en Colombia que necesitan:

- Noticias TI recientes con respaldo científico verificable
- Metadatos completos (DOI, cuartil, h-index, abstracts simplificados)
- **Perfiles CvLAC** de autores colombianos y cruce con la publicación encontrada
- Categoría **Publindex** en revistas nacionales
- Salida dual **JSON + texto** trazable

## Archivos

| Archivo | Uso |
|---------|-----|
| `SKILL.md` | Instrucciones principales (Skillstore-ready) |
| `output-schema.json` | Contrato JSON con bloques CvLAC y Publindex |
| `business-prompt-template.md` | Plantilla de prompt para el usuario |
| `examples.md` | 5 ejemplos entrada/salida |
| `assets/sample-output.md` | Salida de muestra realista |
| `references/cvlac-guide.md` | Búsqueda y desambiguación CvLAC |
| `references/sources-colombia.md` | Publindex, GrupLAC, medios CO |
| `references/tool-patterns.md` | Patrones WebSearch/WebFetch/API |
| `references/validation-checklist.md` | Checklist pre-entrega |

## Mejoras vs skill 01 (Skillstore)

| Dimensión | Mejora |
|-----------|--------|
| Arquitectura | Secciones `When to Use`, `Guidelines`, Hard Gates, Tool Patterns |
| CvLAC | Bloque por autor colombiano + cruce publicación |
| Colombia | Publindex, GrupLAC, región default Colombia |
| Ejemplos | 5 casos + sample-output en assets |
| Seguridad | Sin scraping masivo, sin datos personales, dominios oficiales |
| Especificación | Frontmatter YAML, name kebab-case, version semver |

## Uso rápido

1. Cargar `SKILL.md` como instrucción del agente.
2. Completar `business-prompt-template.md`.
3. Validar JSON contra `output-schema.json`.
4. Verificar manualmente URLs CvLAC en hallazgos críticos.

## Publicación en Skillstore

Para enviar a [skillstore.io/submit](https://skillstore.io/submit):

1. Copiar carpeta `doctoral-ti-news-cvlac/` (subcarpeta de publicación) a un repo GitHub.
2. Asegurar que el directorio se llame `doctoral-ti-news-cvlac` (coincide con `name` en frontmatter).
3. Incluir `LICENSE` (MIT).
4. Enviar URL del repositorio.

## Fuentes

OpenAlex, Crossref, SCImago, DOAJ, **scienti.minciencias.gov.co** (CvLAC, GrupLAC, Publindex).

## Autor

Jhusef Alfonso López Parra — MIT License

## Versión

`1.0.0` — 2026-06-29
