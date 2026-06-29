# Ejemplos de uso — Skill 04 (TI + CvLAC Colombia)

## Ejemplo 1 — Entrada completa con CvLAC (formato ambos)

**Entrada:**

```
Tema: aprendizaje federado en salud digital.
Ventana temporal: últimos 90 días.
Profundidad: media.
Región: Colombia.
Enriquecer CvLAC: solo_colombianos.
Formato salida: ambos.
Idioma: español.

Vincular noticias con papers, metadatos completos y perfiles CvLAC de autores
colombianos. Incluir Publindex si la revista es colombiana.
```

**Salida esperada (texto plano — extracto):**

```
=== RESUMEN EJECUTIVO ===
En Colombia y LATAM emergen iniciativos de aprendizaje federado aplicados a
historias clínicas, impulsados por alianzas universidad-hospital. La evidencia
Q1-Q2 proviene principalmente de revistas internacionales; un paper reciente
incluye coautoría de la Universidad Nacional con registro verificable en CvLAC
categoría Asociado. Publindex aplica a una revista colombiana en cat. B.
Prioridad doctoral: privacidad diferencial en entornos clínicos con datos
regulatorios colombianos (Ley 1581).

=== HALLAZGO #1 — Piloto federado UNAL-ESE ===
Noticia: UNAL prueba IA federada sin compartir datos clínicos | Fuente: El Espectador
| Fecha: 2026-05-20 | URL: https://...

Publicación científica
  Título: Federated Learning for Clinical Prediction in Low-Resource Settings
  DOI: 10.1016/j.example.2026.xxxxx | URL: https://doi.org/...
  Tipo: Artículo de revista | Estado: publicado
  Fecha publicación: 2026-04-15 (precisión: dia)
  Venue: Journal of Biomedical Informatics | ISSN: 1532-0464
  Publindex: no_indexada (revista extranjera)

Métricas del venue
  Cuartil: Q1 | Percentil: 92 | Fuente: scimago

Autores y créditos (Colombia)
  1. Ana María Pérez Ríos — Universidad Nacional de Colombia — h-index: 12 (openalex)
     CvLAC: https://scienti.minciencias.gov.co/cvlac/visualizador/generarCurriculoCv.do?cod_rh=0000123456
     Categoría: Investigador Asociado
     GrupLAC: GRUPO IA EN SALUD (B) — url
     Publicación en CvLAC: sí
     Publindex revista: no aplica

Relevancia doctoral: Alta para tesis en IA + salud con enfoque regulatorio CO.
Nivel de confianza: alta
```

**Salida esperada (JSON — extracto autor con CvLAC):**

```json
{
  "nombre": "Ana María Pérez Ríos",
  "orcid": "0000-0001-2345-6789",
  "afiliacion": "Universidad Nacional de Colombia",
  "pais_afiliacion": "CO",
  "rol": "primer_autor",
  "h_index": 12,
  "h_index_fuente": "openalex",
  "creditos": "Conceptualización, Metodología",
  "cvlac": {
    "perfil_encontrado": true,
    "url": "https://scienti.minciencias.gov.co/cvlac/visualizador/generarCurriculoCv.do?cod_rh=0000123456",
    "cod_rh": "0000123456",
    "categoria": "Investigador Asociado",
    "afiliacion_principal": "Universidad Nacional de Colombia",
    "gruplac": [
      {
        "nombre": "GRUPO IA EN SALUD",
        "url": "https://scienti.minciencias.gov.co/gruplac/jsp/visualiza/visualizagr.jsp?nro=000012345678",
        "categoria_grupo": "B"
      }
    ],
    "publicacion_en_cvlac": true,
    "publindex_categoria": null,
    "coincidencia_confianza": "alta",
    "notas": "Coincidencia nombre + afiliación + título en productos bibliográficos."
  }
}
```

> DOI, URLs y nombres son **ilustrativos**. En uso real deben verificarse.

---

## Ejemplo 2 — Revista colombiana con Publindex

**Entrada:**

```
Tema: ciberseguridad en infraestructura crítica.
Ventana: 60 días.
Profundidad: breve.
Región: Colombia.
Formato: json.
```

**Salida esperada (extracto venue):**

```json
{
  "revista_o_venue": {
    "nombre": "Revista Colombiana de Computación",
    "issn": "0123-4567",
    "editorial": "Universidad X",
    "pais": "CO",
    "indexacion": ["Publindex", "DOAJ"],
    "publindex": {
      "categoria": "B",
      "fuente": "publindex_minciencias",
      "notas": "Verificado por ISSN en consulta MinCiencias."
    }
  },
  "metricas_venue": {
    "cuartil": "no_confirmado",
    "percentil": null,
    "fuente_metrica": "publindex",
    "sjr": null,
    "impact_factor": null,
    "notas": "Revista nacional; Publindex B como métrica principal."
  }
}
```

---

## Ejemplo 3 — Autor colombiano sin CvLAC público

**Entrada:**

```
Tema: blockchain en cadena de suministro.
Profundidad: media.
Enriquecer CvLAC: si.
```

**Salida esperada (autor):**

```json
{
  "nombre": "Pedro Sánchez Vega",
  "afiliacion": "Universidad del Valle",
  "pais_afiliacion": "CO",
  "cvlac": {
    "perfil_encontrado": false,
    "url": null,
    "cod_rh": null,
    "categoria": null,
    "afiliacion_principal": null,
    "gruplac": [],
    "publicacion_en_cvlac": null,
    "publindex_categoria": null,
    "coincidencia_confianza": "baja",
    "notas": "Búsqueda site:minciencias.gov.co sin resultados unívocos. Posible investigador sin registro público CvLAC."
  }
}
```

---

## Ejemplo 4 — Homónimo CvLAC

**Entrada:** Paper con autor "Carlos Rodríguez" afiliado a UIS.

**Salida esperada:**

```json
{
  "cvlac": {
    "perfil_encontrado": false,
    "url": null,
    "cod_rh": null,
    "categoria": null,
    "coincidencia_confianza": "baja",
    "notas": "3 perfiles CvLAC con nombre similar. Candidatos: [url1], [url2], [url3]. No asignado por ambigüedad."
  }
}
```

---

## Ejemplo 5 — Noticia sin paper + enriquecer_cvlac: no

**Entrada:**

```
Tema: anuncio comercial de chip cuántico.
Formato: texto.
Enriquecer CvLAC: no.
```

**Salida:** Bloque texto con `Sin evidencia científica verificable vinculada.` y sin sección CvLAC.

---

## Validación rápida

- [ ] ¿Autores CO tienen bloque `cvlac`?
- [ ] ¿Publindex solo cuando revista es colombiana/indexada?
- [ ] ¿`coincidencia_confianza` documentada?
- [ ] ¿JSON alineado con `output-schema.json`?

Ver también: [assets/sample-output.md](assets/sample-output.md)
