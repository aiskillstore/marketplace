---
name: doctoral-ti-news-cvlac
description: >-
  Vigilancia científica en TI con enfoque colombiano: vincula noticias recientes
  con publicaciones verificables, enriquece autores con perfiles CvLAC/GrupLAC y
  revistas con Publindex. Usar cuando el usuario pida noticias TI doctorales,
  metadatos académicos, CvLAC, investigadores colombianos, Publindex, GrupLAC
  o vigilancia científica LATAM con trazabilidad JSON/texto.
version: 1.0.0
license: MIT
author: Jhusef Alfonso López Parra
---

# Vigilancia científica TI — enfoque Colombia (CvLAC)

Conecta noticias recientes de TI con evidencia científica verificable y enriquece cada hallazgo con metadatos académicos, perfiles **CvLAC** de autores colombianos, categorías **Publindex** y vínculos **GrupLAC** cuando existan.

## When to Use

Activa esta skill cuando el usuario:

1. Pida noticias de TI vinculadas a papers, tesis o investigación doctoral.
2. Mencione **CvLAC**, **MinCiencias**, **Publindex**, **GrupLAC** o investigadores colombianos.
3. Necesite metadatos enriquecidos (DOI, cuartil, h-index, abstract simplificado) con salida JSON y/o texto.
4. Priorice contexto **Colombia** o **LATAM** en vigilancia científica.
5. Quiera cruzar una publicación encontrada con la hoja de vida nacional del autor.

**Anti-triggers** — no uses esta skill si:

- Solo se pide traducción, redacción o corrección de estilo sin búsqueda de evidencia.
- El usuario exige datos de CvLAC sin acceso a internet o sin permitir consulta web.
- Se solicita scraping masivo, extracción de cédulas/IDs personales o automatización fuera de dominios oficiales.
- El tema no es TI/ciencias de la computación y no hay componente de vigilancia científica.

## Capabilities & Limitations

| Capacidad | Límite |
|-----------|--------|
| Noticias + papers con metadatos OpenAlex/Crossref | CvLAC no tiene API pública; consulta web puntual |
| Perfil CvLAC por autor colombiano identificado | Homónimos requieren desambiguación manual |
| Categoría Publindex de revistas colombianas | Solo cuando la revista esté indexada y sea verificable |
| h-index vía OpenAlex/Semantic Scholar | No confundir con métricas internas MinCiencias |
| Salida JSON + texto trazable | No inventar DOI, cuartil, categoría CvLAC ni URLs |

## Core Principles

1. **Iron Law — No inventar:** Si un dato no está verificado, usar `null`, `no_confirmado` o `no_disponible`. Nunca rellenar campos CvLAC/Publindex por inferencia.
2. **Iron Law — Trazabilidad:** Toda métrica lleva `fuente` y URL consultada en `meta.fuentes_utilizadas`.
3. **Iron Law — Separar capas:** Diferenciar **noticia**, **evidencia internacional** (DOI/OpenAlex) y **registro nacional** (CvLAC/Publindex).
4. Priorizar autores con afiliación colombiana (`country_code: CO` en OpenAlex) para enriquecimiento CvLAC.
5. Modo **gratuito por defecto**; alternativa gratuita si se menciona Scopus/JCR.

## Guidelines

- Idioma de salida por defecto: **español**.
- Región por defecto: **Colombia** (expandir a LATAM si el usuario lo pide).
- Respetar rate limits en `scienti.minciencias.gov.co` (máx. 1 perfil CvLAC por autor por hallazgo).
- No almacenar ni solicitar números de cédula, pasaporte ni datos personales sensibles.
- Solo consultar dominios oficiales: `scienti.minciencias.gov.co`, APIs públicas (OpenAlex, Crossref).
- Papers **retractados**: marcar y no usar como evidencia principal.

## Tool Usage Patterns

Usa herramientas en este orden y propósito:

| Herramienta | Cuándo | Patrón |
|-------------|--------|--------|
| **WebSearch** | Descubrir noticias recientes; buscar autor en CvLAC por nombre + institución | Query: `"nombre apellido" site:scienti.minciencias.gov.co cvlac` o `"título paper" DOI` |
| **WebFetch** | Leer perfil CvLAC, página Publindex o noticia concreta | URL must be HTTPS; validar dominio antes de fetch |
| **OpenAlex API** | Works, autores, h-index, afiliaciones CO | `https://api.openalex.org/works?search=...` → autor → `authors?filter=display_name.search:...` |
| **Crossref API** | DOI, tipo, fechas, estado retractación | `https://api.crossref.org/works/{doi}` |
| **Semantic Scholar** | h-index alternativo si OpenAlex ambiguo | Solo si autor identificado unívocamente |

**Patrón CvLAC (sin API):**

```
1. Detectar autores con afiliación CO en OpenAlex/Crossref.
2. WebSearch: "{nombre completo}" "{universidad colombiana}" cvlac minciencias
3. Si hay candidato: WebFetch URL perfil (formato generarCurriculoCv.do?cod_rh=...)
4. Verificar coincidencia: nombre + afiliación + área TI.
5. Buscar en HTML del perfil el título/DOI de la publicación vinculada.
6. Registrar cvlac.publicacion_en_cvlac: true|false|null según evidencia.
```

Detalle extendido: [references/cvlac-guide.md](references/cvlac-guide.md)  
Patrones de herramientas: [references/tool-patterns.md](references/tool-patterns.md)

## Input Parameters

| Parámetro | Valores | Default |
|-----------|---------|---------|
| `tema` | Texto libre TI | obligatorio |
| `ventana_temporal` | 30/60/90 días, 6 meses, 1 año | 90 días |
| `profundidad` | `breve` (3-5) / `media` (5-8) / `profunda` (8-12) | `media` |
| `region` | Colombia, LATAM, Global | **Colombia** |
| `enriquecer_cvlac` | `si` / `no` / `solo_colombianos` | `solo_colombianos` |
| `formato_salida` | `json` / `texto` / `ambos` | `ambos` |
| `idioma_salida` | `es` / `en` | `es` |

Plantilla de entrada: [business-prompt-template.md](business-prompt-template.md)

---

## Workflow

### Fase 1 — Descubrimiento de noticias

1. Identificar 3-12 noticias recientes según `profundidad`.
2. Priorizar fuentes colombianas/LATAM cuando `region` lo indique (El Espectador Tech, Semana, Portafolio, blogs UNAL/Andes, comunicados MinCiencias).
3. Registrar fuente, URL, fecha y tipo.
4. Descartar titulares sin posible respaldo técnico → marcar `solo_noticia`.

**Hard Gate 1:** ¿Cada noticia tiene URL y fecha verificables? Si no → excluir o marcar `nivel_confianza: baja`.

### Fase 2 — Vinculación científica internacional

5. Por noticia, buscar 0-2 publicaciones (DOI preferido).
6. Resolver metadatos vía OpenAlex → Crossref → arXiv/PubMed según tema.
7. Completar tipo, estado, fecha, venue, cuartil SJR, abstract simplificado, impactos.

**Hard Gate 2:** ¿Hay DOI o match unívoco en OpenAlex? Si no → `evidencia_cientifica: null` y explicar en notas.

### Fase 3 — Enriquecimiento Colombia (CvLAC / Publindex / GrupLAC)

8. Por cada autor con afiliación CO (si `enriquecer_cvlac` ≠ `no`):
   - Buscar perfil CvLAC siguiendo patrón de herramientas.
   - Completar bloque `cvlac` del esquema (ver abajo).
   - Si el paper aparece en el perfil: `publicacion_en_cvlac: true`.
9. Si la revista es colombiana o indexada en Publindex:
   - Consultar categoría A1/A2/B/C vía fuentes MinCiencias o [references/sources-colombia.md](references/sources-colombia.md).
   - Registrar en `revista_o_venue.publindex`.
10. Extraer GrupLAC vinculados al investigador cuando consten en CvLAC.

**Hard Gate 3:** ¿Perfil CvLAC con coincidencia nombre + afiliación? Si ambiguo → `perfil_encontrado: false`, `coincidencia_confianza: baja`, nota de homónimo.

### Fase 4 — Síntesis doctoral

11. Ranking por rigor, novedad, relevancia doctoral, calidad venue y presencia en ecosistema nacional.
12. Preguntas doctorales, riesgos metodológicos y vacíos (incluir brecha Colombia/LATAM).
13. Entregar formato solicitado.

**Hard Gate 4:** Validar salida contra checklist de [references/validation-checklist.md](references/validation-checklist.md).

---

## Campos CvLAC por autor

Cada autor colombiano debe incluir:

```
cvlac: {
  perfil_encontrado, url, cod_rh,
  categoria,           // Investigador Senior | Asociado | Junior | null
  afiliacion_principal,
  gruplac[],           // { nombre, url, categoria_grupo }
  publicacion_en_cvlac,
  publindex_categoria, // A1|A2|B|C|null — de la revista del paper
  coincidencia_confianza,  // alta|media|baja
  notas
}
```

Esquema JSON completo: [output-schema.json](output-schema.json)

---

## Output Format

### Texto plano

Seguir plantilla de skill 01 con secciones adicionales por autor:

```
Autores y créditos (Colombia)
  1. Nombre — Afiliación — h-index: N (openalex)
     CvLAC: [url o "no encontrado"]
     Categoría: Senior|Asociado|Junior|no confirmado
     GrupLAC: nombre (categoría) — url
     Publicación en CvLAC: sí|no|no verificado
     Publindex revista: A1|A2|B|C|no aplica
```

Cierre: `--- JSON ---` + JSON completo si `formato_salida: ambos`.

### JSON

- Válido UTF-8, sin comentarios.
- `null` para datos no verificados; no omitir claves de primer nivel.
- Bloque `meta.enfoque_colombiano: true` y `meta.cvlac_consultado: true|false`.

Ejemplo completo: [assets/sample-output.md](assets/sample-output.md)

---

## Edge Cases

| Caso | Acción |
|------|--------|
| Autor colombiano sin CvLAC público | `perfil_encontrado: false`; buscar ORCID/OpenAlex; nota explicativa |
| Homónimo (varios perfiles CvLAC) | No asignar URL; `coincidencia_confianza: baja`; listar candidatos en `notas` |
| Paper en preprint, no aún en CvLAC | `publicacion_en_cvlac: false`; nota "preprint pendiente de registro" |
| Revista extranjera Q1, sin Publindex | `publindex_categoria: null`; cuartil SJR en `metricas_venue` |
| CvLAC no accesible (timeout/403) | Reintentar 1 vez; si falla → `cvlac.notas: "consulta no disponible"` |
| Noticia solo marketing | `evidencia_cientifica: null`; `relevancia_doctoral: Baja` |
| URL CvLAC dominio legacy colciencias.gov.co | Normalizar a `scienti.minciencias.gov.co` si redirige |

## Common Pitfalls

| Error | Consecuencia | Corrección |
|-------|--------------|------------|
| Asumir CvLAC por nombre común | Perfil incorrecto | Exigir afiliación + área; bajar confianza |
| Confundir h-index OpenAlex con índices MinCiencias | Métricas falsas | Etiquetar fuente en `h_index_fuente` |
| Ignorar preprints en noticias de prensa | Sobrevalorar evidencia | Verificar `estado_publicacion` |
| No registrar Publindex en revistas CO | Pierde valor colombiano | Consultar índice para ISSN/nombre |
| Inventar `cod_rh` | Fallo de trazabilidad | Solo extraer de URL verificada |

## Red Flags

- Autor "colombiano" sin afiliación CO verificable en metadatos del paper.
- Categoría CvLAC Senior/Asociado sin URL de perfil.
- Publicación marcada `publicacion_en_cvlac: true` sin coincidencia de título o DOI.
- Cuartil Q1 sin ISSN ni fuente SCImago.
- Más de 3 consultas CvLAC por hallazgo (riesgo de rate limit / mala práctica).

## FAQ

**¿CvLAC tiene API?** No. Consulta web puntual al visualizador MinCiencias.

**¿Debo incluir CvLAC para autores extranjeros?** No, salvo que el usuario lo pida; usar `enriquecer_cvlac: solo_colombianos`.

**¿Publindex reemplaza al cuartil SJR?** No. Son complementarios: SJR para comparación internacional, Publindex para política nacional colombiana.

**¿Qué hacer si no hay noticia pero sí papers recientes?** Informar al usuario; puedes listar papers recientes del tema en Colombia como hallazgos tipo `evidencia_directa`.

## Additional Resources

- [references/cvlac-guide.md](references/cvlac-guide.md) — búsqueda y desambiguación CvLAC
- [references/sources-colombia.md](references/sources-colombia.md) — Publindex, GrupLAC, fuentes nacionales
- [references/tool-patterns.md](references/tool-patterns.md) — patrones detallados de herramientas
- [references/validation-checklist.md](references/validation-checklist.md) — checklist pre-entrega
- [examples.md](examples.md) — 5 ejemplos entrada/salida
- [business-prompt-template.md](business-prompt-template.md) — plantilla lista para pegar
