---
name: hora-exacta
description: >-
  Use whenever the date, time, day of the week or year matters: "¿qué hora es?", "¿qué día es hoy?", "hoy", "mañana", "esta semana", "el lunes", schedules, deadlines, publishing times, "hace cuánto", time zones (CDMX, Lima, Costa Rica, Caracas, Florida), or before writing any date in a file, report or message. Never guess the date from memory or from the conversation: run the script and use what it prints. Also install the hook so every message already carries the real date and time.
license: MIT
---

# Hora exacta

Claude no tiene reloj. Si adivina la fecha, se equivoca de día, de semana o de año, y eso sale caro: una publicación programada el día que no era, un reporte con la fecha mal o un "mañana" que ya pasó.

Esta skill da la fecha y la hora REALES de la computadora, en las zonas donde trabajamos.

## Cómo se usa

1. Antes de decir o escribir una fecha u hora, corre:
   ```bash
   python scripts/hora.py
   ```
   Imprime el día, la fecha y la hora de CDMX, Lima, Costa Rica, Caracas y Florida, y la hora UTC.
2. Usa esa salida tal cual. No la corrijas con lo que "debería" ser.
3. Para calcular días ("el lunes que viene", "en 3 días"), parte de la fecha que imprimió el script, no de la memoria.
4. Al programar algo, di siempre la zona ("7:00 CDMX = 8:00 Lima").

## Que todos los chats la sepan siempre (hook)

Agrega este hook en `~/.claude/settings.json`, dentro de `hooks.UserPromptSubmit`. Así cada mensaje llega con la fecha y la hora reales, en todos los chats y sin pedirlo:

```json
{ "type": "command", "command": "python \"~/.claude/skills/hora-exacta/scripts/hora.py\" --corto", "timeout": 5 }
```

Cambia la ruta por la ruta completa de tu equipo. `--corto` imprime una sola línea con la hora, la semana en curso y dónde estás (ciudad por IP, reloj de la computadora y tu nota de `~/.claude/hora-exacta-lugar.txt`). `--sin-ip` no consulta la IP.

## Detalles

- No necesita internet ni paquetes. Usa `zoneinfo` si está; si no (en Windows sin `tzdata`), usa los desfases fijos: México, Perú, Costa Rica y Venezuela no cambian de hora. El horario de verano de Florida se calcula aparte.
- Para agregar una zona, edita la lista `ZONAS` en `scripts/hora.py`.
