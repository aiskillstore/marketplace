# Fuentes Colombia — Publindex, GrupLAC y medios TI

## Índices y registros nacionales

| Fuente | Uso | Acceso |
|--------|-----|--------|
| **Publindex** | Categoría A1/A2/B/C de revistas colombianas | Consulta en portal MinCiencias / buscador de revistas indexadas |
| **GrupLAC** | Grupos de investigación reconocidos | `scienti.minciencias.gov.co/gruplac` |
| **CvLAC** | Hoja de vida investigadores | Ver [cvlac-guide.md](cvlac-guide.md) |
| **Colciencias/MinCiencias** | Comunicados oficiales de ciencia y TI | WebSearch en `minciencias.gov.co` |

### Publindex — categorías

| Cat. | Interpretación para salida |
|------|---------------------------|
| A1 | Revista de mayor reconocimiento nacional |
| A2 | Alto reconocimiento |
| B | Reconocimiento intermedio |
| C | Reconocimiento básico |
| no_indexada | Revista extranjera o colombiana sin indexación Publindex verificada |

Registrar en `revista_o_venue.publindex`:

```json
{
  "categoria": "A1",
  "fuente": "publindex_minciencias",
  "notas": "Verificado por ISSN 0123-4567 en consulta 2026-06."
}
```

Si no se puede verificar: `"categoria": null`, `"notas": "No verificado en Publindex"`.

## Fuentes internacionales (complemento)

Mismo orden que skill 01:

1. OpenAlex — works, autores CO, h-index
2. Crossref — DOI, retractación
3. SCImago JR — cuartil SJR internacional
4. DOAJ — acceso abierto
5. arXiv / PubMed — según subdominio TI

## Medios y fuentes de noticias — Colombia / LATAM

Priorizar cuando `region: Colombia`:

| Tipo | Ejemplos |
|------|----------|
| Prensa económica/TI | Portafolio, La República tecnología |
| General con sección tech | El Tiempo, El Espectador |
| Institucional | Comunicados UNAL, Uniandes, EAFIT, MinTIC, MinCiencias |
| LATAM | TecMundo LATAM, Xataka Colombia, MIT Tech Review en español |
| Global (complemento) | IEEE Spectrum, Ars Technica, The Register |

## Instituciones colombianas frecuentes en TI

Para desambiguación CvLAC:

- Universidad Nacional de Colombia (UNAL)
- Universidad de los Andes
- Universidad EAFIT
- Universidad del Valle
- Universidad Industrial de Santander (UIS)
- Universidad Tecnológica de Pereira (UTP)
- Pontificia Universidad Javeriana
- Universidad de Antioquia
- ICESI, Universidad Icesi
- MinTIC, MinCiencias

Usar nombre institucional **exacto** del paper al buscar CvLAC.

## Política de costo

- Todas las fuentes listadas son consultables sin API premium.
- Scopus/JCR: mencionar solo con alternativa SCImago/OpenAlex.
- No bloquear entrega por falta de suscripción.

## Vacíos típicos Colombia/LATAM

Incluir en `vacios_investigacion` cuando aplique:

- Pocos datasets locales en español para el subdominio TI.
- Subrepresentación de autores CO en papers Q1 del tema.
- Desfase entre noticia mediática nacional y publicación indexada.
- Registro tardío en CvLAC de productos recién publicados.
