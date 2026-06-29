# Plantilla de prompt — TI doctoral + CvLAC Colombia

Complete y entregue al skill:

## Contexto de búsqueda

1. **Tema / área TI:**
   _(ej. IA en salud, ciberseguridad, edge computing, datos abiertos)_

2. **Ventana temporal:**
   _(ej. últimos 30 / 60 / 90 días, 6 meses)_

3. **Profundidad:**
   - [ ] breve (3-5 hallazgos)
   - [x] media (5-8 hallazgos)
   - [ ] profunda (8-12 hallazgos)

4. **Región:**
   - [x] Colombia _(default skill 04)_
   - [ ] LATAM
   - [ ] Global

5. **Enriquecimiento CvLAC:**
   - [ ] si (todos los autores posibles)
   - [x] solo_colombianos _(recomendado)_
   - [ ] no

6. **Formato de salida:**
   - [ ] json
   - [ ] texto
   - [x] ambos _(recomendado)_

7. **Idioma de la respuesta:**
   - [x] español
   - [ ] inglés

## Filtros opcionales

8. **Tipo de publicación preferido:**
   _(ej. artículos de revista, incluir preprints)_

9. **Cuartil / Publindex mínimo:**
   _(ej. Q1-Q2 internacional; Publindex A1-B para revistas CO)_

10. **Instituciones o autores de interés:**
    _(ej. UNAL, Uniandes, autor con URL CvLAC conocida)_

11. **Excluir:**
    _(ej. papers retractados, noticias sin respaldo técnico)_

## Salida solicitada (checklist)

Por cada hallazgo:

- [ ] Noticia: título, fuente, fecha, URL
- [ ] Publicación: DOI, tipo, estado, fecha, venue
- [ ] Métricas: cuartil SJR y/o **Publindex** (revistas CO)
- [ ] Abstract original + simplificado
- [ ] Puntos importantes, impactos (científico, técnico, social, doctoral)
- [ ] Autores con h-index, ORCID, afiliación, **país CO**
- [ ] **CvLAC**: URL, cod_rh, categoría, GrupLAC, publicación en perfil
- [ ] Relevancia doctoral, confianza, riesgos de sesgo

Cierre:

- [ ] Preguntas doctorales sugeridas
- [ ] Riesgos metodológicos
- [ ] Vacíos de investigación (brecha Colombia/LATAM)

## Ejemplo mínimo listo para pegar

```
Tema: inteligencia artificial generativa en educación superior.
Ventana temporal: últimos 90 días.
Profundidad: media.
Región: Colombia.
Enriquecer CvLAC: solo_colombianos.
Formato salida: ambos.
Idioma: español.

Entregar según output-schema.json: metadatos completos, autores colombianos
con bloque CvLAC verificado, Publindex para revistas nacionales, cuartil SJR
internacional. No inventar datos. Marcar null o no_confirmado si no hay verificación.
```

## Plantillas adicionales

### Solo verificar CvLAC de paper conocido

```
Tengo el DOI: 10.xxxx/xxxxx.
Buscar autores colombianos, enriquecer con CvLAC y Publindex si aplica.
Formato: json.
No buscar noticias adicionales.
```

### Vigilancia LATAM ampliada

```
Tema: 5G y IoT industrial.
Región: LATAM (priorizar Colombia, México, Brasil).
Enriquecer CvLAC: solo_colombianos.
Profundidad: profunda.
Formato: ambos.
```
