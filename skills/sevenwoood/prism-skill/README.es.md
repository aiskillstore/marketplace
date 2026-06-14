<!--
Navegación de idiomas (enlaces ancla en la página)
-->

<div align="center">
  <a href="#introducción">Introducción</a> | <a href="#características-principales">Características</a> | <a href="#instalación">Instalación</a> | <a href="#inicio-rápido">Inicio rápido</a> | <a href="#estructura-de-archivos">Estructura</a> | <a href="#licencia">Licencia</a>
</div>

<div align="center">
  <a href="README.md">中文</a> | <a href="README.en.md">English</a> | <a href="README.ja.md">日本語</a> | <a href="README.ko.md">한국어</a> | <a href="README.es.md">Español</a>
</div>

<br>

<div align="center">
  <img src="assets/prism-skill.svg" alt="Banner de Prism Skill" width="600">
</div>

# 🔮 Prism Skill · Prisma

**Motor de análisis multidisciplinario de adaptación dinámica** — Analiza profesionalmente cualquier evento, opinión o fragmento, produciendo informes estructurados, veraces y legibles. Soporta verificación de hechos, complemento de fragmentos, tablas/diagramas de flujo/listas, y exportación a HTML interactivo.

---

## <a id="introducción"></a>📖 Introducción

Prism Skill es una habilidad analítica que sigue el protocolo Agent Skills. Puede:

- Seleccionar dinámicamente **disciplinas** (ciencias naturales, sociales, humanidades, etc.) y **perspectivas** (individual, nacional, corporativa, etc.) para analizar problemas;
- **Priorizar la veracidad**, realizar verificación de hechos cuando se solicite, y citar fuentes autorizadas;
- **Completar automáticamente descripciones fragmentadas** de eventos, con hasta 3 rondas de preguntas inteligentes para entradas vagas;
- Generar **contenido estructurado suave y legible** (tablas, diagramas de flujo de texto, listas) – sin plantillas rígidas como “En una frase”;
- Exportar a **Markdown** o a un **informe HTML interactivo** (secciones plegables, modo oscuro, copia con un clic).

---

## <a id="características-principales"></a>✨ Características principales

| Característica             | Descripción                                                  |
| -------------------------- | ------------------------------------------------------------ |
| 🌍 Multilingüe              | Responde automáticamente en el idioma del usuario (mejor en ZH/EN, aceptable en JA/KO/ES) |
| 🔍 Veracidad primero        | Activa verificación estricta con palabras clave como “caso real”, nunca inventa |
| 🧩 Disciplinas adaptativas  | Elige 1-3 campos más relevantes de forma dinámica            |
| 👥 Perspectivas multiescala | Desde micro (individual) hasta macro (internacional)         |
| 💬 Interacción suave        | Usa encabezados naturales como “En pocas palabras”, “Desglosemos” |
| 📊 Salida rica              | Tablas, listas, diagramas de flujo de texto, Markdown, HTML interactivo |
| ⚙️ Degradación CLI          | En entornos de solo texto, se convierte a texto plano/listas simples |
| 🛡️ Límites éticos           | Sin asesoramiento profesional, sin incitación a la violencia, respeta privacidad, antidiscriminación |

---

## <a id="instalación"></a>📦 Instalación

**Opción 1: GitHub CLI (recomendado)**
```bash
gh skill install sevenwoood/prism-skill prism-skill
```

**Opción 2: CLI universal de Skills**

```bash
npx skills add sevenwoood/prism-skill --skill prism-skill
```



**Opción 3: Manual**

```bash
git clone https://github.com/sevenwoood/prism-skill.git
# Copie la carpeta prism-skill a una de las siguientes ubicaciones:
# - ~/.cursor/skills/
# - ~/.claude/skills/
# - ~/.codex/skills/
```



------

## <a id="inicio-rápido"></a>🚀 Inicio rápido

**Ejemplo de entrada**:

> “La Reserva Federal acaba de subir las tasas de interés. ¿Cómo afecta a la gente común? Quiero hechos reales.”

**Ejemplo de salida (estilo suave)**:

```text
En pocas palabras: una subida de tasas aumenta directamente los pagos mensuales de préstamos a tasa variable, y puede frenar el aumento de precios.

Desglosemos:
| Área | Impacto |
|------|---------|
| Hipoteca | +~140 ¥ por mes por cada 1M ¥ de préstamo |
| Ahorros | Los intereses suben ligeramente |
| Empleo | Sectores orientados a la exportación pueden debilitarse |

En resumen: el efecto más directo es en el costo de los préstamos; otros aspectos son menores.

Si quieres profundizar, podemos hablar de tu situación particular de préstamo, o cómo afecta a otros países.
```



**Generar un informe HTML**: Después de cualquier análisis, escribe “output html” para obtener una página web interactiva.

------

## <a id="estructura-de-archivos"></a>📁 Estructura de archivos

```text
prism-skill/
├── SKILL.md                  # Definición principal de la habilidad
├── README.md                 # Documentación en chino
├── README.en.md              # Documentación en inglés
├── README.ja.md              # Documentación en japonés
├── README.ko.md              # Documentación en coreano
├── README.es.md              # Documentación en español
├── references/               # Metodología y restricciones
│   ├── analysis-framework.md
│   ├── source-priority.md
│   └── ethics-boundaries.md
├── examples/                 # Ejemplos de diálogos
│   ├── economic-example.md
│   ├── health-example.md
│   └── social-example.md
└── assets/                   # Recursos estáticos
    └── prism-skill.svg       # Imagen de banner
```



------

## <a id="licencia"></a>📄 Licencia

MIT © 2026 Prism Skill Contributors

------

## ⚠️ Notas de compatibilidad de idiomas

- **Mejor soporte**: chino, inglés (verificación de hechos más precisa, salida más fluida).
- **Otros idiomas**: japonés, coreano, español funcionan, pero el análisis profundo en contextos complejos puede ser ligeramente más débil.
- **Recomendación**: Para análisis críticos, pida a la habilidad que “primero analice en inglés/chino, luego traduzca a su idioma”.
- **Verificación de hechos**: Cada idioma priorizará fuentes autorizadas en ese idioma; para eventos transfronterizos, puede especificar una región (ej. “prioriza datos oficiales chinos”).