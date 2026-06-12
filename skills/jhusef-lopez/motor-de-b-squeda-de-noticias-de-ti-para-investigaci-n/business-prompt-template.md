# Plantilla de prompt — Noticias TI doctorales

Complete y entregue esta plantilla al skill:

## Contexto de búsqueda

1. **Tema / área TI:**
   _(ej. seguridad en LLMs, edge AI, computación cuántica aplicada)_

2. **Ventana temporal:**
   _(ej. últimos 30 / 60 / 90 días, 6 meses)_

3. **Profundidad:**
   - [ ] breve (3-5 hallazgos)
   - [ ] media (5-8 hallazgos)
   - [ ] profunda (8-12 hallazgos)

4. **Región / idioma de fuentes:**
   _(ej. global, LATAM, solo inglés, español+inglés)_

5. **Formato de salida:**
   - [ ] json
   - [ ] texto
   - [x] ambos _(recomendado)_

6. **Idioma de la respuesta:**
   - [x] español
   - [ ] inglés

## Filtros opcionales

7. **Tipo de publicación preferido:**
   _(ej. solo artículos de revista, incluir preprints, revisiones sistemáticas)_

8. **Cuartil mínimo deseado:**
   _(ej. Q1-Q2 preferido; incluir Q3-Q4 si no hay alternativa)_

9. **Excluir:**
   _(ej. preprints sin peer review, noticias sin DOI, papers retractados)_

10. **Autores o instituciones de interés:**
    _(opcional)_

## Salida solicitada (checklist)

Por cada hallazgo, incluir obligatoriamente:

- [ ] Noticia: título, fuente, fecha, URL
- [ ] Publicación: DOI, tipo, **estado**, **fecha** (con precisión)
- [ ] Venue: revista/lugar, ISSN, indexación
- [ ] Métricas: **cuartil Q** y/o **percentil**, fuente de la métrica
- [ ] **Abstract original** + **abstract simplificado** (lenguaje claro)
- [ ] **Puntos importantes** (3-7)
- [ ] **Impactos**: científico, técnico, social, doctoral
- [ ] **Autores** con ORCID, afiliación, **índice h** y créditos
- [ ] Relevancia doctoral, nivel de confianza, riesgos de sesgo

Cierre obligatorio:

- [ ] Preguntas doctorales sugeridas
- [ ] Riesgos metodológicos
- [ ] Vacíos de investigación

## Ejemplo mínimo listo para pegar

```
Tema: seguridad adversarial en modelos fundacionales.
Ventana temporal: últimos 90 días.
Profundidad: profunda.
Región: global.
Formato salida: ambos.
Idioma: español.

Entregar metadatos completos según output-schema.json:
tipo y estado de publicación, fechas, venue, cuartil/percentil,
abstract simplificado, puntos importantes, impactos,
autores con h-index y créditos CRediT cuando existan.
No inventar datos no verificados.
```
