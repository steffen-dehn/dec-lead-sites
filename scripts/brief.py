#!/usr/bin/env python3
"""Erzeugt den Akquise-Brief (A4, DIN-Fensterkuvert) zu einer Lead-Seite.

Aufruf:  python3 scripts/brief.py <slug> [--datum 2026-10-26] [--an-mich]

Eingaben:
- leads/<slug>/lead.json                -> Handlungsfelder (Titel) für die Aufzählung
- leads/_input/<slug>.brief.json        -> Anschrift, Vorname, Anlass (NICHT committen, liegt im gitignore)
    {
      "anschrift": ["Firma GmbH", "z. Hd. Vorname Nachname", "Straße 1", "12345 Ort"],
      "vorname": "Vorname",
      "anlass": "im Juli habt ihr ... (1-2 Sätze, klein beginnend, endet mit Punkt)"
    }
Ausgabe: leads/_input/briefe/Brief_<slug>.pdf (+ .png zum Ansehen), ebenfalls nicht committet.

--an-mich ersetzt die Anschrift durch Steffens eigene (Testkopie), Inhalt bleibt gleich.
Kurzlink im Brief: dehn-consulting.com/analyse/<slug> (301-Weiterleitung auf der Wix-Website anlegen!).
Benötigt: pip install qrcode[pil]; Playwright/Chromium.
"""
import argparse
import base64
import datetime as dt
import io
import json
from pathlib import Path

import qrcode
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parent.parent
ASSETS = Path(__file__).resolve().parent / "assets"
LOGO = ROOT / "docs" / "assets" / "dec-logo.png"
OUT = ROOT / "leads" / "_input" / "briefe"

ABSENDER = "Dehn Consulting // DEC · Bundesratufer 12 · 10555 Berlin"
AN_MICH = ["Dehn Consulting // DEC", "z. Hd. Steffen Dehn", "Bundesratufer 12", "10555 Berlin"]
MONATE = ["Januar", "Februar", "März", "April", "Mai", "Juni", "Juli", "August",
          "September", "Oktober", "November", "Dezember"]
ZAHL = {3: "drei", 4: "vier"}


def b64(p: Path) -> str:
    return base64.b64encode(p.read_bytes()).decode()


def qr_png(url: str) -> str:
    img = qrcode.make(url, box_size=10, border=0)
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return base64.b64encode(buf.getvalue()).decode()


CSS = f"""
@font-face {{ font-family:P; font-weight:300; src:url(data:font/woff2;base64,{b64(ASSETS / 'poppins-300.woff2')}) }}
@font-face {{ font-family:P; font-weight:600; src:url(data:font/woff2;base64,{b64(ASSETS / 'poppins-600.woff2')}) }}
@page {{ size:A4; margin:0 }}
body {{ margin:0; font-family:P; font-weight:300; color:#1A1A1A; font-size:10.5pt; line-height:1.5 }}
.page {{ position:relative; width:210mm; height:297mm; box-sizing:border-box }}
.ruecksende {{ position:absolute; left:25mm; top:45mm; width:85mm; font-size:7pt; color:#6E6E6E; border-bottom:.3pt solid #6E6E6E; padding-bottom:1mm }}
.anschrift {{ position:absolute; left:25mm; top:62.7mm; width:85mm; font-size:10pt; line-height:1.4 }}
.datum {{ position:absolute; right:20mm; top:92mm; color:#6E6E6E; font-size:9pt }}
.text {{ position:absolute; left:25mm; right:20mm; top:103mm }}
p {{ margin:0 0 4mm }}
ul {{ margin:0 0 4mm; padding-left:5mm }} li {{ margin:0 0 1mm }} li::marker {{ color:#A8B300 }}
.link {{ display:flex; gap:6mm; align-items:center; margin:2mm 0 6mm }}
.link img {{ width:26mm; height:26mm }}
.link span {{ font-size:10pt; color:#1A1A1A }}
.link a {{ color:#1A1A1A; text-decoration:none; border-bottom:1.5px solid #A8B300 }}
.link b {{ display:block; font-weight:600; color:#1A1A1A; font-size:10pt; margin-bottom:1mm }}
.name {{ font-weight:600 }}
.fuss {{ position:absolute; left:25mm; bottom:9mm; font-size:7.5pt; color:#6E6E6E; line-height:1.5 }}
.logo {{ position:absolute; right:20mm; bottom:9mm; width:38mm }}
.akzent {{ position:absolute; left:0; top:0; width:6mm; height:297mm; background:#A8B300 }}
"""


def render(slug: str, inp: dict, felder: list, datum: dt.date) -> str:
    url = f"https://www.dehn-consulting.com/analyse/{slug}"
    kurz = f"dehn-consulting.com/analyse/{slug}"
    adr = "<br>".join(inp["anschrift"])
    li = "".join(f"<li>{f}</li>" for f in felder)
    datum_txt = f"Berlin, {datum.day}. {MONATE[datum.month - 1]} {datum.year}"
    return f"""<!doctype html><html lang="de"><head><meta charset="utf-8"><style>{CSS}</style></head><body><div class="page">
<div class="akzent"></div>
<div class="ruecksende">{ABSENDER}</div>
<div class="anschrift">{adr}</div>
<div class="datum">{datum_txt}</div>
<div class="text">
<p>Hallo {inp['vorname']},</p>
<p>{inp['anlass']}</p>
<p>Dehn Consulting // DEC begleitet Organisationen in solchen Phasen. Wir haben uns deshalb angesehen, was ihr öffentlich über euch zeigt, und daraus {ZAHL.get(len(felder), str(len(felder)))} Handlungsfelder abgeleitet:</p>
<ul>{li}</ul>
<p>Wie wir die Ausgangslage einschätzen und wie sie in sechs Monaten aussehen könnte, haben wir auf einer Seite für euch zusammengefasst:</p>
<div class="link"><img src="data:image/png;base64,{qr_png(url)}"><span><b>Eure Potenzial-Analyse</b><a href="{url}">{kurz}</a></span></div>
<p>Die Analyse beruht ausschließlich auf öffentlichen Informationen und ist bewusst eine Außenperspektive. In einem 30-minütigen Gespräch würden wir gern mit dir abgleichen, was davon zutrifft und wo ihr gerade steht. Einen unverbindlichen Termin kannst du direkt über die Seite buchen.</p>
<p>Beste Grüße</p>
<p class="name">Steffen Dehn</p>
</div>
<div class="fuss">{ABSENDER}<br>info@dehn-consulting.com · www.dehn-consulting.com</div>
<img class="logo" src="data:image/png;base64,{b64(LOGO)}">
</div></body></html>"""


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("slug")
    ap.add_argument("--datum", help="Briefdatum YYYY-MM-DD (Standard: heute)")
    ap.add_argument("--an-mich", action="store_true", help="Testkopie an Steffen")
    a = ap.parse_args()

    lead = json.loads((ROOT / "leads" / a.slug / "lead.json").read_text(encoding="utf-8"))
    inp = json.loads((ROOT / "leads" / "_input" / f"{a.slug}.brief.json").read_text(encoding="utf-8"))
    if a.an_mich:
        inp = dict(inp, anschrift=AN_MICH)
    felder = [h["titel"] for h in lead["handlungsfelder"]]
    datum = dt.date.fromisoformat(a.datum) if a.datum else dt.date.today()

    OUT.mkdir(parents=True, exist_ok=True)
    name = f"Brief_{a.slug}{'_an-mich' if a.an_mich else ''}"
    with sync_playwright() as p:
        b = p.chromium.launch()
        pg = b.new_page(viewport={"width": 794, "height": 1123})
        pg.set_content(render(a.slug, inp, felder, datum))
        pg.wait_for_timeout(300)
        pg.pdf(path=str(OUT / f"{name}.pdf"), format="A4", print_background=True)
        pg.screenshot(path=str(OUT / f"{name}.png"), full_page=True)
        b.close()
    print(OUT / f"{name}.pdf")


if __name__ == "__main__":
    main()
