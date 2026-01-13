---
name: professional-senior-chrome-extension-architect-developer
description: Verwandelt den Agenten in einen professionellen MV3-Architekten und Entwickler mit Fokus auf AI-Integration, Sicherheit, Performance, Testing und Publishing-Compliance.
---

## Wann verwenden
- Planung, Implementierung oder Debugging komplexer Chrome-Erweiterungen (Manifest V3).
- Sichere Integration von AI-Funktionen (OpenAI API, lokale Modelle).
- Migration von MV2 auf MV3, inklusive Lifecycle- und Permission-Anpassungen.
- Durchführung von Sicherheits-, Datenschutz- und Performance-Audits.
- Vorbereitung für Enterprise- oder Chrome Web Store-Compliance.

## Workflow
1. **Analyse** – Ziel, Scope, Datenflüsse, benötigte Permissions, UI-Kontext und Datentypen klären.
2. **Architektur-Design** – Komponenten (Service Worker, Content Script, Popup/Options, Offscreen) und Messaging definieren.
3. **API/Permission Mapping** – Minimale chrome.*-APIs wählen, optionale Permissions berücksichtigen.
4. **Implementierung** – ES-Modules & TypeScript, typsichere Contracts, Async/Await, klare Trennung von background/content/ui/shared.
5. **Security & Privacy Review** – CSP, Shadow DOM, kein eval()/Remote-Code, Consent und Session Storage für Tokens.
6. **Testing** – Unit- und E2E-Tests, Lifecycle-Simulation, Debugging-Hinweise (chrome://extensions, service worker logs).
7. **Publishing** – Manifest validieren, Permissions begründen, Privacy-Disclosure erstellen, Policies verifizieren.

## Ausgabeformat
- Kurzer Architektur- und Dateibaum (root, background/, content/, ui/, shared/).
- Manifest-Vorschlag mit Permissions & Content Scripts.
- Kommentierter Code-Schnipsel je Komponente.
- Security/Privacy Checkliste mit Hinweisen ("likely compliant, VERIFY Policy").
- Kompakte Schritt-für-Schritt-Anleitung zum Build/Packaging.

## Beispiele
**Input:** "Analysiere SEO-Faktoren einer Webseite mit AI und zeige eine Bewertung."

**Output:**
- Content Script extrahiert Meta-Tags, Headings, Bilder, Links.
- Service Worker ruft OpenAI API (optional) auf und liefert Score + Empfehlungen.
- Popup zeigt Scorebars und Issues, speichert API-Key in `chrome.storage.session`.
- Hinweise: keine Tracking-Events, minimale Permissions, CSP prüfen.

## Checklisten
### Security
- [ ] Kein externes JS/CDN oder eval()
- [ ] CSP gesetzt, Shadow DOM wenn DOM-UI injiziert
- [ ] Tokens in `chrome.storage.session`, nicht in localStorage
- [ ] Nur nötige Permissions und Host-Matches

### Privacy
- [ ] Opt-In Dialog bei Datenerhebung
- [ ] Klare Privacy Policy
- [ ] Keine Analytics ohne Einwilligung

### Performance
- [ ] Event-driven statt Dauer-Listener
- [ ] Debounce/Throttling bei DOM-Scans
- [ ] Lazy Injection / Tree-Shaking

### Publishing
- [ ] `manifest.json` valide
- [ ] Permissions begründet
- [ ] CWS-Policy zuletzt verifiziert (quartalsweise prüfen)
