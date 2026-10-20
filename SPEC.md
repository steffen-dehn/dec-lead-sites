# DEC Lead-Microsites - Spezifikation für Claude Code (v1)

Personalisierte Akquise-Seiten pro Lead: Außenanalyse auf Graves-Basis, 3-4 Handlungsfelder als *Was ist heute* vs. *Was wird sein* (erster Schritt + Ergebnis nach 6 Monaten), CI-angelehnt, ausgespielt über GitHub Pages.

Pilot: `leads/fuchs-eule/` (fertige Referenz, siehe `index.html`).

---

## 1. Prinzipien

| Prinzip | Bedeutung für die Umsetzung |
|---|---|
| Außenperspektive, keine Diagnose | Alles als Beobachtung + Hypothese formulieren. Nie "eure Kultur ist X". Jede "Was ist heute"-Aussage hat einen `beleg` (Quelle). |
| Graves dezent | Graves steuert die Analyse, erscheint auf der Seite nur als Farbverlauf je Handlungsfeld und als kleine "Treppe" unter dem Muster. Keine Farbnamen, keine Stufen-Erklärung im Text. |
| Handlungsfelder frei abgeleitet | Kein fester Katalog. 3-4 Felder pro Lead (harte Obergrenze), aus Spannungen der Analyse. |
| Zwei Spalten | *Was ist heute* (Lage + Beleg) / *Was wird sein* (erster Schritt mit Format und Dauer + Ergebnis nach 6 Monaten). |
| Positiv, konkret, kein Pitch | Zukunftsbild als Anknüpfungspunkt fürs Gespräch, keine Leistungsliste. |
| DEC-Sprache | "ihr/euch", gegenderte Formen (Mitarbeiter*innen), Bindestrich statt Gedankenstrich, echte Umlaute. |
| Herkunft transparent | Pflicht: kleiner Hinweis direkt unter dem Einstieg ("Alle Inhalte sind aus öffentlich zugänglichen Daten abgeleitet ...") plus ausführlicher Disclaimer mit Quellen im Footer. |
| Kein Impersonieren | Farben/Schrift des Leads ja, Logo des Leads nein. DEC-Absender und Disclaimer immer sichtbar. `noindex`. |

---

## 2. Repo-Struktur

```
dec-lead-sites/
├── CLAUDE.md                  # Kurzfassung dieser Spec + Regeln aus Abschnitt 1
├── template/
│   └── index.html             # Template = Pilot ohne Lead-Daten (JSON-Block leer)
├── leads/
│   ├── _input/                # CRM-Zeilen als .tsv/.md (Rohinput)
│   └── <slug>/
│       ├── lead.json          # alle Inhalte (Schema Abschnitt 3)
│       ├── analyse.md         # interne Graves-Analyse + Rechercheprotokoll, NICHT veröffentlicht
│       └── index.html         # generiert: template + lead.json
├── scripts/
│   ├── build.py               # injiziert lead.json in template, schreibt docs/<slug>/index.html
│   ├── validate.py            # Schema-, Sprach- und Belegprüfung (Abschnitt 6)
│   └── screenshot.py          # Playwright: Desktop 1280 + Mobile 390
└── docs/                      # GitHub-Pages-Root (nur gebaute Seiten)
    ├── index.html             # leer / Weiterleitung auf dehn-consulting.com
    └── <slug-mit-token>/index.html
```

**URL-Schema:** `docs/<slug>-<6 Zeichen Token>/` (z. B. `fuchs-eule-052870`), damit Seiten nicht erratbar sind. Live: `https://steffen-dehn.github.io/dec-lead-sites/<slug>-<token>/`.

**Hosting:** GitHub Pages aus `/docs` im Branch `main`, Repo `steffen-dehn/dec-lead-sites` (öffentlich). Weil der Repo öffentlich ist, sind `leads/_input/` und `leads/*/analyse.md` per `.gitignore` ausgeschlossen; interne Analysen liegen lokal und im Second Brain. `docs/robots.txt` sperrt Crawler, jede Seite hat `noindex`. Optional später Custom Domain (z. B. `einblick.dehn-consulting.com`).

---

## 3. Datenschema `lead.json`

```jsonc
{
  "slug": "fuchs-eule",
  "firma": "Fuchs & Eule",
  "stand": "Oktober 2026",
  "empfaenger": ["Robin Behlau", "Dr. Tobias Frese"],
  "ci": { "brand": "#hex", "accent": "#hex", "font": "Google-Font-Name", "verified": true },
  "hero": { "kicker": "...", "title": "max. 8 Wörter", "intro": "2-3 Sätze, Trigger + Versprechen" },
  "muster": {
    "title": "Was wir von außen sehen",
    "sub": "1 Satz",
    "karten": [ { "titel": "...", "quelle": "domain/pfad", "werte": ["3-5 Begriffe, wörtlich vom Lead"] } ],
    "lesart": "3-4 Sätze: Spannung benennen, wertschätzend, nicht wertend",
    "treppe": [ { "farbe": "ROT|BLAU|...", "label": "Alltagssprache" } ]   // 3-4 Stufen
  },
  "handlungsfelder": [            // 3-4 Einträge
    {
      "id": "kebab-case",
      "titel": "max. 5 Wörter",
      "graves": { "von": "FARBE", "zu": "FARBE" },   // nur für Farbverlauf
      "heute": "3-4 Sätze, beobachtbar",
      "beleg": "konkrete Quelle der Beobachtung",
      "erster_schritt": "Format (Dauer): Leitfrage",
      "ergebnis_6m": "2-3 Sätze, sichtbares Ergebnis"
    }
  ],
  "cta": { "title": "...", "text": "...", "button": "...", "mailto": "info@dehn-consulting.com", "betreff": "..." },
  "hinweis": "Alle Inhalte sind aus öffentlich zugänglichen Daten abgeleitet (...).",   // Pflicht, sichtbar unter dem Hero
  "disclaimer": "Außenperspektive ... Hypothesen für ein Gespräch.",
  "quellen": [ { "titel": "...", "url": "https://..." } ]
}
```

Graves-Farbwerte: `PURPUR, ROT, BLAU, ORANGE, GRUEN, GELB, TUERKIS`.

---

## 4. Workflow pro Lead

1. **Input lesen** - CRM-Zeile aus `leads/_input/` (Firma, Größe, Trigger, Kontakte, Begründung). CRM-Angaben sind Hypothesen, nicht Fakten.
2. **Recherche** (Quellen in `analyse.md` protokollieren):
   - Website: Startseite, Über uns/Unternehmen, Karriere, Werte/Mission, Team-Seite
   - Stellenanzeigen (Personio, LinkedIn): Führungsrollen, neue Funktionen = Strukturaufbau
   - Presse/Funding der letzten 12 Monate, Interviews der Geschäftsführung
   - Übernahmen, neue Standorte, Wechsel in der Führung
3. **CI extrahieren** - CSS der Lead-Website laden (`curl` + CSS-Datei aus `<link rel=stylesheet>`), häufigste Marken- und Akzentfarbe und Schrift bestimmen. Bei Unsicherheit `verified: false` und neutrale Palette.
4. **Graves-Analyse Außenbild** in `analyse.md`:
   - Wertebegriffe sammeln und Farben zuordnen, getrennt nach Adressat (Kund*innen / Bewerber*innen / Investor*innen)
   - Analogie zur IND/IST/SOLL-Logik: *kommunizierte Werte* (SOLL-Signal) vs. *Wachstumssituation* (IST-Hypothese)
   - Spannungen und Übersteuerungen benennen, aktive Treppe bestimmen (Mapping: Ausgangslage-Dokument im Projekt "Graves Werte")
5. **Handlungsfelder ableiten** - 3-4 Felder, je Feld eine Spannung, eine Graves-Richtung (`von` → `zu`), ein DEC-Format als erster Schritt (Führungs-Nugget, Werte Check-up, Zielbild-Workshop, Schnittstellen-Workshop, Leadership-Klausur, Learning Journey, Transformationsfähigkeit-Check).
6. **Texten** - `lead.json` befüllen. Regeln aus Abschnitt 1.
7. **Bauen** - `python scripts/build.py <slug>` → `docs/<slug>-<token>/index.html`.
8. **Prüfen** - `validate.py` + `screenshot.py`, Screenshots ansehen.
9. **Freigabe** - Steffen prüft Seite + `analyse.md`. Erst nach Freigabe committen und pushen.
10. **Übergabe** - Link + Vorschlag für Erstansprache (3-4 Sätze, "du", endet mit "Beste Grüße") ausgeben.

---

## 5. Analyse-Prompt (pro Lead)

```
Du analysierst die Außendarstellung von <FIRMA> für eine personalisierte Akquise-Seite von Dehn Consulting.
Input: CRM-Zeile <...> und die recherchierten Quellen.

1. Sammle wörtliche Wertebegriffe und Kulturversprechen, getrennt nach Adressat (Kund*innen, Bewerber*innen, Investor*innen). Quelle je Begriff.
2. Ordne sie Graves-Stufen zu (PURPUR, ROT, BLAU, ORANGE, GRUEN, GELB, TUERKIS).
3. Leite aus der Wachstumssituation (Funding, Teamgröße, Übernahmen, offene Führungsrollen) eine IST-Hypothese ab.
4. Benenne 3-4 Spannungen zwischen kommunizierten Werten und Wachstumsanforderungen. Keine Stufe ist besser; Übersteuerung ist genauso relevant wie Unterdeckung.
5. Je Spannung ein Handlungsfeld: was ist heute (beobachtbar + Beleg), erster Schritt (DEC-Format, Dauer, Leitfrage), Ergebnis nach 6 Monaten (sichtbar, konkret).
6. Trenne strikt: Was steht in Quellen / was ist Interpretation. Widersprüche zwischen CRM und Quellen explizit auflisten.
Ton: klar, wertschätzend, keine Floskeln, keine Diagnose, "ihr/euch", gegendert, Bindestrich statt Gedankenstrich.
```

---

## 6. Prüfregeln (`validate.py`)

- Schema vollständig, 3-4 Handlungsfelder, jedes mit `beleg`
- `hinweis` und `disclaimer` vorhanden und nicht leer; Hinweis ist im gerenderten Hero sichtbar
- Keine Gedankenstriche (—, –), keine ue/oe/ae-Ersatzschreibung in deutschen Wörtern
- Keine Graves-Farbnamen im sichtbaren Text (nur in `graves`/`treppe.farbe`)
- Jede URL in `quellen` erreichbar (HTTP 200)
- Keine Zahl im Text ohne Quelle in `analyse.md`
- Kein horizontaler Scroll bei 390 px, keine JS-Fehler (Playwright)

---

## 7. Aufgaben für Claude Code

| # | Aufgabe | Ergebnis |
|---|---|---|
| 1 | ~~Repo anlegen, Struktur, `CLAUDE.md`~~ erledigt 21.10.2026 | Repo-Skelett |
| 2 | ~~erledigt~~ Pilot `index.html` in `template/index.html` überführen (JSON-Block durch Platzhalter `{{LEAD_JSON}}` ersetzen) und `leads/fuchs-eule/lead.json` extrahieren | Template + erster Datensatz |
| 3 | ~~erledigt~~ `build.py`: Template + lead.json → `docs/<slug>-<token>/index.html`; Token einmalig erzeugen und in `lead.json` (`token`) speichern | reproduzierbarer Build |
| 4 | ~~erledigt~~ `validate.py` + `screenshot.py` nach Abschnitt 6 | Qualitätsschranke |
| 5 | GitHub Pages aus `/docs` aktivieren, `docs/index.html` leitet auf dehn-consulting.com | Live-Hosting |
| 6 | CI-Extraktion für Fuchs & Eule nachholen (CSS der Website), `ci.verified = true` | echte Lead-Farben |
| 7 | Leads Limetax und Buena nach Workflow Abschnitt 4 durchlaufen | 2 weitere Seiten zur Freigabe |
| 8 | Optional: Klick-Tracking (Plausible o. Ä., cookiefrei) für "welches Feld wurde geöffnet" | Gesprächseinstieg im Follow-up |
| 9 | Optional: Asana-Anbindung - Status der Karte im Board "DEC Akquise CRM" auf "Seite verschickt" setzen, Link als Kommentar | geschlossener Akquise-Kreislauf |

---

## 8. Offene Punkte (Steffen)

- **CTA/Einstiegsformat:** aktuell 45-Minuten-Gespräch. Alternativ Transformationsfähigkeit-Check (1 Tag, Festpreis) als Angebotsanker?
- **Domain:** github.io-Adresse oder Subdomain von dehn-consulting.com?
