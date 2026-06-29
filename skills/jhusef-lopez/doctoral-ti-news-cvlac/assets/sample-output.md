# Sample output — doctoral-ti-news-cvlac

Salida ilustrativa completa (extracto de un hallazgo). Datos ficticios para validación de formato.

## Texto plano (extracto)

```
=== RESUMEN EJECUTIVO ===
Tres noticias recientes conectan LLMs con sector público colombiano. La evidencia
peer-reviewed más sólida es un artículo Q2 con coautor UIS registrado en CvLAC
como Investigador Junior; la publicación aún no figura en su perfil (preprint reciente).
Una revista colombiana del mismo eje temático tiene Publindex B. Brecha: pocos
benchmarks en español para evaluación de alucinaciones en contexto gubernamental.

=== HALLAZGO #1 — Chatbot institucional MinTIC ===
Noticia: MinTIC prueba asistente IA para trámites | Fuente: Portafolio
| Fecha: 2026-06-10 | URL: https://example.com/noticia

Publicación científica
  Título: Evaluating Hallucination Rates in Spanish-Language Government Chatbots
  DOI: 10.1234/example.2026.001 | URL: https://doi.org/10.1234/example.2026.001
  Tipo: Artículo de revista | Estado: publicado
  Fecha publicación: 2026-03-01 (precisión: mes)
  Venue: Revista Ingeniería UIS | ISSN: 0123-9999 | Publindex: B

Autores y créditos (Colombia)
  1. Laura Méndez Castillo — Universidad Industrial de Santander — h-index: 8 (openalex)
     CvLAC: https://scienti.minciencias.gov.co/cvlac/visualizador/generarCurriculoCv.do?cod_rh=0000999888
     Categoría: Investigador Junior
     GrupLAC: GIMEL (B)
     Publicación en CvLAC: no (paper muy reciente)
     Publindex revista: B

Relevancia doctoral: Alta — evaluación LLM en español institucional.
Nivel de confianza: media
Riesgos de sesgo: Noticia ministerial sin métricas; paper sí reporta tasas.

=== FIN HALLAZGO #1 ===
```

## JSON (hallazgo completo)

```json
{
  "meta": {
    "tema": "LLMs en sector público colombiano",
    "ventana_temporal": "últimos 90 días",
    "profundidad": "media",
    "region": "Colombia",
    "enriquecer_cvlac": "solo_colombianos",
    "idioma_salida": "es",
    "fecha_generacion": "2026-06-29T15:00:00Z",
    "formato_solicitado": "ambos",
    "total_hallazgos": 5,
    "enfoque_colombiano": true,
    "cvlac_consultado": true,
    "fuentes_utilizadas": [
      "https://api.openalex.org",
      "https://api.crossref.org",
      "https://scienti.minciencias.gov.co/cvlac",
      "https://www.scimagojr.com"
    ]
  },
  "resumen_ejecutivo": "Tres noticias recientes conectan LLMs con sector público colombiano...",
  "hallazgos": [
    {
      "ranking": 1,
      "tema": "Chatbot institucional MinTIC",
      "noticia": {
        "titulo": "MinTIC prueba asistente IA para trámites",
        "fuente": "Portafolio",
        "url": "https://example.com/noticia",
        "fecha": "2026-06-10",
        "tipo": "noticia"
      },
      "evidencia_cientifica": {
        "titulo": "Evaluating Hallucination Rates in Spanish-Language Government Chatbots",
        "doi": "10.1234/example.2026.001",
        "url": "https://doi.org/10.1234/example.2026.001",
        "tipo_publicacion": "journal-article",
        "tipo_publicacion_etiqueta": "Artículo de revista",
        "estado_publicacion": "publicado",
        "fecha_publicacion": "2026-03-01",
        "fecha_precision": "mes",
        "revista_o_venue": {
          "nombre": "Revista Ingeniería UIS",
          "issn": "0123-9999",
          "editorial": "UIS",
          "pais": "CO",
          "indexacion": ["Publindex", "DOAJ"],
          "publindex": {
            "categoria": "B",
            "fuente": "publindex_minciencias",
            "notas": "ISSN verificado en índice nacional."
          }
        },
        "metricas_venue": {
          "cuartil": "Q2",
          "percentil": 78,
          "fuente_metrica": "scimago",
          "sjr": 0.45,
          "impact_factor": null,
          "notas": "SJR 2024 por ISSN."
        },
        "abstract_original": "We evaluate hallucination rates...",
        "abstract_simplificado": "Los autores midieron con qué frecuencia un chatbot en español inventa respuestas en escenarios de trámites gubernamentales simulados. Probaron tres modelos comerciales y reportan tasas del 12-28%. Proponen un protocolo de evaluación reproducible.",
        "puntos_importantes": [
          "Evaluación en español para contexto gubernamental.",
          "Tres LLMs comerciales comparados.",
          "Protocolo reproducible publicado como anexo.",
          "Limitación: datos simulados, no producción real."
        ],
        "impactos": {
          "cientifico": "Primer benchmark reportado en español para alucinaciones gubernamentales.",
          "tecnico": "Guía práctica para despliegue de chatbots institucionales.",
          "social": "Impacto en confianza ciudadana en trámites digitales.",
          "doctoral": "Línea de tesis en evaluación LLM + regulación CO."
        },
        "autores": [
          {
            "nombre": "Laura Méndez Castillo",
            "orcid": "0000-0002-1111-2222",
            "afiliacion": "Universidad Industrial de Santander",
            "pais_afiliacion": "CO",
            "rol": "primer_autor",
            "h_index": 8,
            "h_index_fuente": "openalex",
            "creditos": "Conceptualización, Metodología, Escritura",
            "cvlac": {
              "perfil_encontrado": true,
              "url": "https://scienti.minciencias.gov.co/cvlac/visualizador/generarCurriculoCv.do?cod_rh=0000999888",
              "cod_rh": "0000999888",
              "categoria": "Investigador Junior",
              "afiliacion_principal": "Universidad Industrial de Santander",
              "gruplac": [
                {
                  "nombre": "GIMEL",
                  "url": "https://scienti.minciencias.gov.co/gruplac/jsp/visualiza/visualizagr.jsp?nro=0000111222",
                  "categoria_grupo": "B"
                }
              ],
              "publicacion_en_cvlac": false,
              "publindex_categoria": "B",
              "coincidencia_confianza": "alta",
              "notas": "Perfil verificado; paper de 2026 aún no registrado en productos."
            }
          }
        ],
        "creditos_contribucion": "CRediT disponible en paper.",
        "open_access": true,
        "notas": ""
      },
      "relevancia_doctoral": "Alta — gap en evaluación LLM institucional CO.",
      "nivel_confianza": "media",
      "riesgos_sesgo": ["Noticia sin métricas técnicas; paper reciente."]
    }
  ],
  "preguntas_doctorales_sugeridas": [
    "¿Cómo adaptar benchmarks de alucinación a normativa Ley 1581 en Colombia?"
  ],
  "riesgos_metodologicos": [
    "Generalizar tasas de prensa sin paper vinculado."
  ],
  "vacios_investigacion": [
    "Escasez de datasets abiertos de diálogos gubernamentales en español colombiano."
  ]
}
```
