# AI SEO Analyzer (Chrome Extension Skill)

Eine Manifest-V3-Extension, die On-Page-SEO-Signale analysiert und optional einen OpenAI-gestützten Kurzbericht liefert. Die Struktur folgt dem Blueprint "Professional Senior Chrome Extension Architect & Developer" und zeigt typische Patterns für Service Worker, Content Script, Offscreen-Dokument und Popup-UI.

## Features
- Content Script sammelt Meta-Daten, Überschriften, Bilder und Links pro Seite.
- Service Worker berechnet einen heuristischen SEO-Score und kann optional die OpenAI API nutzen (API-Key wird in `chrome.storage.session` gehalten).
- Popup ermöglicht API-Key-Verwaltung und startet die Analyse des aktiven Tabs.
- Offscreen-Dokument demonstriert DOM-PARSING fernab des sichtbaren Kontextes.
- Typisierte Messaging-Contracts und Utility-Funktionen (`src/shared`).

## Projektstruktur
```
manifest.json
assets/
  icons.base64.json  # Textbasierte Icon-Definitionen
src/
  background/
    index.ts          # Service Worker: Messaging, Analyse, Offscreen-Delegation
    offscreen.ts      # Offscreen-Listener (DOMParser)
    offscreen.html    # Offscreen-Dokument
  content/
    index.ts          # Content Script: Snapshot-Erfassung + Floating Button
  shared/
    contracts.ts      # Typisierte Message-Contracts
    utils.ts          # Scoring, OpenAI-Fetch, Offscreen-Hilfen
  ui/
    popup.html        # Popup-Oberfläche
    popup.ts          # Popup-Logik
scripts/
  generate-icons.js  # erzeugt PNG-Icons aus Base64 (keine Binärdateien im Repo)
  copy-static.js      # Kopiert Manifest/Assets/HTML nach dist
tests/
  unit/, e2e/         # Test-Skelette
```

## Setup
```bash
npm install
npm run build
```

- `npm run build` kompiliert TypeScript nach `dist/`, erzeugt PNG-Icons aus den Base64-Definitionen und kopiert statische Assets sowie das Manifest.
- Falls du die Icons separat erzeugen möchtest (z. B. nach einem Clean), kannst du `npm run generate:icons` ausführen.
- `npm test` führt Unit-Tests (Vitest) aus.

## Laden der Extension in Chrome
1. `npm run build` ausführen.
2. Chrome öffnen → `chrome://extensions` → Entwicklermodus aktivieren.
3. "Entpackte Erweiterung laden" wählen und den `dist/`-Ordner auswählen.

## Sicherheit & Datenschutz
- Keine Remote-Eval oder externen Skriptquellen.
- API-Key wird nur in `chrome.storage.session` gespeichert (tab-scope, nicht persistent über Browser-Restarts).
- Minimale Permissions: `activeTab`, `storage`, `offscreen`, `tabs`, `scripting`; Host-Permission für http/https zur Analyse.

## Tests & Qualitätssicherung
- Unit-Tests prüfen die Scoring-Logik in `src/shared/utils.ts`.
- GitHub Actions Workflow (`.github/workflows/release.yml`) baut das Projekt und führt Tests aus.

## Hinweise zur OpenAI-Nutzung
- Trage einen gültigen Schlüssel im Popup ein. Fehler beim API-Aufruf werden im Ergebnis als Fallback-Nachricht angezeigt.
- Für Datenschutz-restriktive Umgebungen kann der AI-Teil ausgelassen werden: Die heuristische Auswertung läuft offline.

## Lizenz
MIT
