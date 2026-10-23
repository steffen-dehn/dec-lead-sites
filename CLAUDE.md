# DEC Lead-Microsites

Personalisierte Akquise-Seiten von Dehn Consulting (DEC) für einzelne Leads. Vollständige Spezifikation: `SPEC.md`.

## Wichtig: Dieser Repo ist öffentlich

Alles, was committet wird, ist für jede*n einsehbar - auch für die Leads selbst.

- **Nie committen:** CRM-Zeilen, interne Lead-Bewertungen ("perfekter ICP", Abschlusswahrscheinlichkeit), Analyse-Notizen, Kontaktdaten außer Firmenadressen. Dafür sind `leads/_input/` und `leads/*/analyse.md` per `.gitignore` ausgeschlossen. Interne Analyse gehört zusätzlich ins Second Brain.
- **Committen:** `lead.json` (enthält nur, was auch auf der Seite steht), Template, Skripte, gebaute Seiten in `docs/`.
- Seite erst committen, wenn Steffen sie freigegeben hat.

## Regeln für Inhalte

- Außenperspektive, keine Diagnose: Beobachtung + Hypothese, jede Aussage unter "Was ist heute" mit `beleg`.
- Handlungsfelder frei aus der Analyse abgeleitet, 3-4 pro Lead.
- Struktur je Feld: **Was ist heute** / **Was wird sein** (erster Schritt als Format ohne Dauer- oder Tagesangabe + Ergebnis nach 6 Monaten).
- Graves nur dezent: Farbverlauf je Feld und kleine Treppe. Keine Farbnamen oder Graves-Begriffe im sichtbaren Text.
- Pflicht: `hinweis` (sichtbar unter dem Einstieg: Inhalte aus öffentlich zugänglichen Daten abgeleitet) und `disclaimer` mit Quellen im Footer.
- Sprache: "ihr/euch", gegenderte Formen (Mitarbeiter*innen), Bindestrich statt Gedankenstrich, echte Umlaute.
- Absender: im Abschnitt "Wer wir sind" einmal "Dehn Consulting // DEC", danach auf der ganzen Seite nur "DEC".
- CI des Leads (Farben, Schrift) ja, Logo des Leads nein. DEC als Absender immer sichtbar. `noindex`.
- CI immer per direktem Download ziehen (`curl` der Startseite + verlinkte CSS-Dateien, Hex- und rgb-Werte sowie `font-family` auszählen) - nicht über WebFetch, das verwirft CSS. Lizenzpflichtige Schriften durch eine ähnliche Google-Font ersetzen und das Original in `ci.font_original` vermerken.
- Entwürfe auf Branch `draft/<slug>` pushen (nicht live). Erst nach Freigabe durch Steffen nach `main` mergen.

## Ablauf pro Lead

1. Input (CRM-Zeile) nach `leads/_input/<slug>.md` - wird nicht committet.
2. Recherche + Graves-Analyse nach `leads/<slug>/analyse.md` - wird nicht committet.
3. `leads/<slug>/lead.json` nach Schema in `SPEC.md` befüllen.
4. `python3 scripts/validate.py <slug> --check-urls`
5. `python3 scripts/build.py <slug>` → `docs/<slug>-<token>/index.html`
6. `python3 scripts/screenshot.py <slug>` und Screenshots ansehen.
7. Freigabe durch Steffen, dann commit + push. Live unter `https://steffen-dehn.github.io/dec-lead-sites/<slug>-<token>/`.

## Kontakt-CTA

Standard: `info@dehn-consulting.com`. Mails von Steffen enden mit "Beste Grüße".
