# Patrones de herramientas — vigilancia TI + CvLAC

Guía operativa para maximizar trazabilidad y cumplir Hard Gates del workflow.

## Patrón 1 — Descubrimiento de noticias

```
INPUT: tema, ventana_temporal, region
TOOL: WebSearch
QUERY: "{tema}" noticias {ventana} {region opcional}
FOLLOW-UP: WebFetch de 3-5 URLs más prometedoras
OUTPUT: lista noticias { titulo, fuente, url, fecha, tipo }
GATE: url + fecha presentes
```

**Ejemplo:**

```
WebSearch: "inteligencia artificial salud" noticias Colombia últimos 90 días
WebFetch: https://www.eltiempo.com/... (verificar fecha en página)
```

## Patrón 2 — Resolver paper desde noticia

```
INPUT: titulo_noticia, keywords del titular
TOOL: WebSearch → OpenAlex
QUERY OpenAlex: https://api.openalex.org/works?search={keywords}&sort=publication_date:desc
TOOL: Crossref si hay DOI parcial en noticia
OUTPUT: work seleccionado con doi, autores, venue
GATE: doi o match unívoco
```

## Patrón 3 — Autores colombianos desde OpenAlex

```
INPUT: openalex work id o doi
TOOL: fetch work JSON
FILTER: authorships[].institutions[].country_code == "CO"
OUTPUT: lista autores CO con display_name, institution, orcid
GATE: al menos un autor CO para enriquecer CvLAC (si enriquecer_cvlac != no)
```

## Patrón 4 — Búsqueda CvLAC

```
INPUT: nombre_completo, afiliacion
TOOL: WebSearch
QUERY: "{nombre}" "{afiliacion}" site:scienti.minciencias.gov.co cvlac
IF result URL contains cod_rh:
  TOOL: WebFetch perfil
  EXTRACT: categoria, gruplac links, productos bibliográficos
  MATCH: titulo paper en sección artículos
OUTPUT: bloque cvlac completo
GATE: coincidencia_confianza documentada
```

**Ejemplo entrada/salida:**

| Input | Output esperado |
|-------|-----------------|
| `"María García López"`, `"Universidad Nacional de Colombia"` | URL perfil + cod_rh + categoría si único match |
| `"Carlos Rodríguez"`, `"UIS"` | 3 candidatos → confianza baja, notas con URLs |

## Patrón 5 — Cuartil + Publindex

```
INPUT: issn, nombre_revista, pais_revista
IF pais == CO or revista colombiana:
  TOOL: WebSearch publindex "{nombre_revista}" ISSN
  OUTPUT: publindex.categoria
ALWAYS:
  TOOL: WebSearch scimago "{nombre_revista}" ISSN
  OUTPUT: metricas_venue.cuartil, sjr
GATE: fuente_metrica en cada métrica
```

## Patrón 6 — h-index con desambiguación

```
INPUT: autor { nombre, orcid?, afiliacion }
IF orcid present:
  OpenAlex: /authors?filter=orcid:{orcid}
ELSE:
  OpenAlex: /authors?search={nombre}&filter=last_known_institutions.country_code:CO
IF count(authors) > 1:
  h_index: null, h_index_fuente: no_disponible, nota homónimo
ELSE:
  h_index from summary_stats.h_index
```

## Patrón 7 — Validación pre-entrega

```
CHECKLIST: references/validation-checklist.md
IF any Hard Gate fail:
  corregir o marcar nivel_confianza baja antes de entregar
FORMAT: texto + --- JSON --- + json según formato_solicitado
```

## Manejo de errores de herramientas

| Error | Acción |
|-------|--------|
| WebFetch timeout CvLAC | 1 reintento; luego `cvlac.notas: "timeout"` |
| OpenAlex 429 | Reducir paralelismo; usar Crossref |
| Noticia paywall | Usar titular + fuente alternativa (comunicado institucional) |
| DOI no resuelve | Buscar por título en OpenAlex; si falla → evidencia null |

## Eficiencia de tokens

- No pegar HTML completo de CvLAC en la respuesta.
- Abstract simplificado: máx. 120 palabras.
- Resumen ejecutivo: 5-8 líneas.
- Máx. 7 puntos importantes por hallazgo.

## Seguridad en uso de herramientas

- Fetch solo HTTPS.
- Dominios permitidos para CvLAC/Publindex: `*.minciencias.gov.co`, APIs públicas documentadas.
- No pasar credenciales ni cookies en requests.
- No invocar scripts locales de scraping del usuario sin revisión de seguridad.
