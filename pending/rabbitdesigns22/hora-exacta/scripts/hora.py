"""Fecha y hora reales, ahora mismo, en las zonas donde trabaja Rabbit Designs.

Uso: python hora.py            -> todas las zonas
     python hora.py --corto    -> una sola línea (para hooks)
No necesita internet. Usa zoneinfo; si falta la base de zonas (Windows sin tzdata),
usa los desfases fijos, que valen para estas zonas (México, Perú, Costa Rica y Venezuela
no cambian de hora; Florida sí y se calcula aparte).
"""
import sys
from datetime import datetime, timedelta, timezone

DIAS = ["lunes", "martes", "miércoles", "jueves", "viernes", "sábado", "domingo"]
MESES = ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto",
         "septiembre", "octubre", "noviembre", "diciembre"]
ZONAS = [  # (nombre, zona IANA, desfase fijo de respaldo en horas o None si cambia de horario)
    ("CDMX", "America/Mexico_City", -6),
    ("Lima", "America/Lima", -5),
    ("Costa Rica", "America/Costa_Rica", -6),
    ("Caracas", "America/Caracas", -4),
    ("Florida", "America/New_York", None),
]


def _florida(utc):
    """Horario de verano de EE. UU.: 2.º domingo de marzo 2:00 a 1.er domingo de noviembre 2:00."""
    def domingo(año, mes, n):
        d = datetime(año, mes, 1, tzinfo=timezone.utc)
        d += timedelta(days=(6 - d.weekday()) % 7)
        return d + timedelta(weeks=n - 1)
    inicio = domingo(utc.year, 3, 2) + timedelta(hours=7)   # 2:00 EST = 7:00 UTC
    fin = domingo(utc.year, 11, 1) + timedelta(hours=6)     # 2:00 EDT = 6:00 UTC
    return -4 if inicio <= utc < fin else -5


def hora_en(utc, iana, fijo):
    try:
        from zoneinfo import ZoneInfo
        return utc.astimezone(ZoneInfo(iana))
    except Exception:
        h = fijo if fijo is not None else _florida(utc)
        return utc.astimezone(timezone(timedelta(hours=h)))


def texto(d):
    return f"{DIAS[d.weekday()]} {d.day} de {MESES[d.month - 1]} de {d.year}, {d:%H:%M}"


def fecha(d):
    return f"{DIAS[d.weekday()]} {d.day} de {MESES[d.month - 1]}"


def semana(d):
    """Semana en curso (lunes a domingo) según la primera zona de la lista."""
    lunes = d - timedelta(days=d.weekday())
    return (f"Semana en curso: del {fecha(lunes)} al {fecha(lunes + timedelta(days=6))};"
            f" la próxima empieza el {fecha(lunes + timedelta(days=7))}.")


def lugar():
    """Texto libre de ~/.claude/hora-exacta-lugar.txt (dónde está la persona). Opcional."""
    from pathlib import Path
    try:
        return " ".join((Path.home() / ".claude" / "hora-exacta-lugar.txt")
                        .read_text(encoding="utf-8").split())
    except OSError:
        return ""


def por_ip():
    """Ciudad aproximada según la IP pública (ipwho.is, gratis y sin clave).
    Se guarda 6 horas en ~/.claude/hora-exacta-ip.json para no consultar en cada mensaje.
    Sin internet devuelve lo último guardado, o nada."""
    import json, time, urllib.request
    from pathlib import Path
    cache = Path.home() / ".claude" / "hora-exacta-ip.json"
    viejo = {}
    try:
        viejo = json.loads(cache.read_text(encoding="utf-8"))
        if time.time() - viejo.get("t", 0) < 6 * 3600:
            return viejo.get("lugar", "")
    except (OSError, ValueError):
        pass
    try:
        with urllib.request.urlopen("https://ipwho.is/?fields=success,city,region,country,timezone",
                                    timeout=2) as r:
            d = json.load(r)
        if not d.get("success"):
            raise ValueError
        tz = (d.get("timezone") or {}).get("id", "")
        lugar = ", ".join(x for x in (d.get("city"), d.get("region"), d.get("country")) if x)
        lugar += f" (zona {tz})" if tz else ""
        cache.write_text(json.dumps({"t": time.time(), "lugar": lugar}), encoding="utf-8")
        return lugar
    except Exception:
        return viejo.get("lugar", "")


def reloj_local():
    """Desfase del reloj de esta computadora, sin internet (sigue a Windows/macOS si viajas)."""
    off = datetime.now().astimezone().utcoffset()
    h = int(off.total_seconds() // 3600)
    m = int(abs(off.total_seconds()) % 3600 // 60)
    return f"UTC{h:+d}" + (f":{m:02d}" if m else "")


def main(argv):
    sys.stdout.reconfigure(encoding="utf-8")
    utc = datetime.now(timezone.utc)
    partes = [(n, hora_en(utc, z, f)) for n, z, f in ZONAS]
    extra = [semana(partes[0][1])]
    ip = "" if "--sin-ip" in argv else por_ip()
    sitio = lugar()
    donde = f"Reloj de esta computadora: {reloj_local()}."
    if ip:
        donde = f"Ubicación según la IP (aprox.): {ip}. " + donde
    if sitio:
        donde += f" Nota: {sitio}"
    extra.insert(0, "Dónde: " + donde)
    if "--corto" in argv:
        print("FECHA Y HORA REALES AHORA (no las adivines ni uses otra): "
              + " · ".join(f"{n} {texto(d)}" for n, d in partes)
              + f" · UTC {utc:%Y-%m-%d %H:%M}. " + " ".join(extra))
    else:
        for n, d in partes:
            print(f"{n:<11} {texto(d)}")
        print(f"{'UTC':<11} {utc:%Y-%m-%d %H:%M}")
        for e in extra:
            print(e)


if __name__ == "__main__":
    main(sys.argv[1:])
