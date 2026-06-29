# Checklist de validación pre-entrega

Ejecutar antes de entregar la respuesta final (Hard Gate 4).

## Meta

- [ ] `meta.tema` coincide con solicitud del usuario
- [ ] `meta.fecha_generacion` en ISO 8601
- [ ] `meta.fuentes_utilizadas` lista URLs reales consultadas
- [ ] `meta.enfoque_colombiano` coherente con `region`
- [ ] `meta.cvlac_consultado` refleja si se intentó Fase 3

## Por cada hallazgo

- [ ] Noticia con título, fuente, URL, fecha
- [ ] `evidencia_cientifica` null solo si no hay paper verificable
- [ ] DOI verificado o explícitamente null con nota
- [ ] `estado_publicacion` no es `publicado` sin venue/DOI
- [ ] Cuartil = `no_confirmado` si no hay ISSN/fuente SCImago
- [ ] Abstract simplificado ≠ abstract original y ≤ ~120 palabras
- [ ] 3-7 `puntos_importantes`
- [ ] Cuatro `impactos` completos

## Autores colombianos (si aplica)

- [ ] `pais_afiliacion: "CO"` cuando afiliación es colombiana
- [ ] Bloque `cvlac` presente o null (autor no CO)
- [ ] `cvlac.url` solo si `perfil_encontrado: true`
- [ ] `cod_rh` extraído de URL verificada, no inventado
- [ ] `publicacion_en_cvlac` justificado en `cvlac.notas`
- [ ] Homónimos → `coincidencia_confianza: baja`

## Revistas colombianas

- [ ] `revista_o_venue.publindex` completado
- [ ] Categoría Publindex con `fuente` o null con nota

## Calidad doctoral

- [ ] `relevancia_doctoral` distingue hechos vs inferencias
- [ ] `nivel_confianza` coherente con verificaciones
- [ ] `riesgos_sesgo` incluye sesgo mediático si hay noticia
- [ ] Papers retractados no usados como evidencia principal

## Formato

- [ ] Respeta `formato_solicitado` (json / texto / ambos)
- [ ] JSON parseable y alineado con `output-schema.json`
- [ ] Separador `--- JSON ---` solo en modo `ambos`
- [ ] Idioma de salida según `idioma_salida`

## Cierre obligatorio

- [ ] `preguntas_doctorales_sugeridas` ≥ 1
- [ ] `riesgos_metodologicos` no vacío
- [ ] `vacios_investigacion` menciona brecha Colombia/LATAM si region lo indica

## Seguridad

- [ ] Sin números de cédula/documento en salida
- [ ] Sin credenciales ni tokens en URLs
- [ ] Solo dominios oficiales en fuentes CvLAC
