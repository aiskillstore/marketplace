# Guía CvLAC — búsqueda y desambiguación

Referencia para la Fase 3 del workflow. CvLAC (Currículo Lattes de Colombia) es el sistema de hoja de vida de investigadores administrado por **MinCiencias**.

## URLs oficiales (solo estos dominios)

| Recurso | URL base |
|---------|----------|
| Búsqueda investigadores | `https://scienti.minciencias.gov.co/cvlac/EnBusquedaInvestigadores.jsp` |
| Perfil individual | `https://scienti.minciencias.gov.co/cvlac/visualizador/generarCurriculoCv.do?cod_rh={COD_RH}` |
| GrupLAC | `https://scienti.minciencias.gov.co/gruplac/` |

**No usar** URLs legacy `colciencias.gov.co:8080` salvo redirección verificada.

## Extracción de cod_rh

El identificador `cod_rh` aparece en la URL del perfil:

```
generarCurriculoCv.do?cod_rh=0000123456
                         ^^^^^^^^^^^
```

Solo registrar `cod_rh` si se obtuvo de una URL fetch verificada.

## Procedimiento de búsqueda

### Paso 1 — Identificar candidatos colombianos

Desde OpenAlex/Crossref del paper:

- Filtrar autores con `institutions.country_code = CO`.
- Anotar nombre completo y afiliación tal como aparece en el paper.

### Paso 2 — Búsqueda web

Queries recomendadas (una por autor):

```
"{Nombre Apellido}" "{Universidad}" site:scienti.minciencias.gov.co
"{Nombre Apellido}" cvlac investigador
```

### Paso 3 — Validación de coincidencia

| Señal | Peso |
|-------|------|
| Nombre completo coincide | Alta |
| Afiliación coincide con paper | Alta |
| Área de conocimiento TI/similar | Media |
| Misma ciudad/región | Media |
| Solo apellido común | Insuficiente → no asignar |

**Regla:** Si hay 2+ perfiles plausibles → `coincidencia_confianza: baja`, listar URLs candidatas en `notas`, no elegir uno al azar.

### Paso 4 — Verificar publicación en perfil

En el HTML del perfil CvLAC, buscar:

- Título exacto o muy similar al paper.
- Año de publicación coherente.
- Nombre de revista coincidente.
- DOI si está registrado (no siempre presente).

Resultado:

- Coincidencia clara → `publicacion_en_cvlac: true`
- Perfil encontrado pero paper no listado → `publicacion_en_cvlac: false`
- No se pudo revisar sección de productos → `publicacion_en_cvlac: null`

## Categorías de investigador CvLAC

| Categoría | Significado breve |
|-----------|-------------------|
| Investigador Senior | Máxima categoría nacional |
| Investigador Asociado | Categoría intermedia |
| Investigador Junior | Categoría inicial |

Registrar solo si aparece explícitamente en el perfil. No inferir por antigüedad.

## GrupLAC

En la sección de grupos del perfil CvLAC:

```json
{
  "nombre": "GRUPO DE INVESTIGACIÓN EN ...",
  "url": "https://scienti.minciencias.gov.co/gruplac/jsp/visualiza/visualizagr.jsp?nro=...",
  "categoria_grupo": "A1|A2|B|C|null"
}
```

## Límites de consulta

- Máximo **1 fetch de perfil** por autor por hallazgo.
- Pausa implícita entre consultas (no paralelizar masivamente).
- Si el sitio no responde: documentar y continuar con metadatos internacionales.

## Seguridad y privacidad

- **No** extraer ni reportar número de documento de identidad.
- **No** almacenar HTML completo del perfil en la salida.
- **No** ejecutar scripts de scraping masivo; solo lectura puntual vía herramientas del agente.
- Reportar únicamente datos académicos públicos del perfil.

## Anti-patrones CvLAC

| Anti-patrón | Por qué evitar |
|-------------|----------------|
| Asignar perfil solo por apellido | Homónimos frecuentes en Colombia |
| Copiar categoría de un paper anterior del autor | La categoría es del investigador, no del paper |
| Marcar publicacion_en_cvlac=true sin revisar productos | Falsa trazabilidad nacional |
| Usar datos de LinkedIn como CvLAC | No es fuente oficial |
