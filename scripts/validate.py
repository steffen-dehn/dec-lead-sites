#!/usr/bin/env python3
"""Prüft leads/<slug>/lead.json gegen die Regeln aus SPEC.md (Abschnitt 6).

Aufruf: python3 scripts/validate.py <slug> [--check-urls]
Exit-Code 1 bei Fehlern.
"""
import json
import re
import sys
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
GRAVES = {"PURPUR", "ROT", "BLAU", "ORANGE", "GRUEN", "GELB", "TUERKIS"}
# Graves-Farbnamen dürfen im sichtbaren Text nicht vorkommen
GRAVES_WORDS = re.compile(r"\b(purpur|türkis|tuerkis|graves|spiral dynamics)\b", re.I)
# typische Umlaut-Ersatzschreibungen (Stichprobe, keine Vollprüfung)
UMLAUT_FAKES = re.compile(r"\b\w*(fuer|ueber|koennen|moeglich|aussen|groesse|haeufig|zusaetzlich|naechste)\w*\b", re.I)
# Webadressen/Pfade (z. B. futurium.de/de/ueber-uns) nicht als Umlaut-Ersatz werten
URLISH = re.compile(r"\S*[a-z0-9-]+\.[a-z]{2,}(/\S*)?", re.I)
REQUIRED = ["slug", "firma", "hero", "muster", "handlungsfelder", "cta", "hinweis", "disclaimer", "quellen"]
FIELD_KEYS = ["id", "titel", "graves", "heute", "beleg", "erster_schritt", "ergebnis_6m"]
VISIBLE_SKIP = {"graves", "farbe", "slug", "id", "url", "mailto", "token", "ci"}


def visible_strings(obj, key=None):
    """Alle Texte, die auf der Seite sichtbar werden."""
    if key in VISIBLE_SKIP:
        return
    if isinstance(obj, str):
        yield key, obj
    elif isinstance(obj, list):
        for v in obj:
            yield from visible_strings(v, key)
    elif isinstance(obj, dict):
        for k, v in obj.items():
            yield from visible_strings(v, k)


def validate(slug: str, check_urls: bool) -> list[str]:
    d = json.loads((ROOT / "leads" / slug / "lead.json").read_text(encoding="utf-8"))
    err = []

    for k in REQUIRED:
        if not d.get(k):
            err.append(f"Pflichtfeld fehlt oder leer: {k}")

    hf = d.get("handlungsfelder", [])
    if not 3 <= len(hf) <= 4:
        err.append(f"3-4 Handlungsfelder erwartet, gefunden: {len(hf)}")
    for i, f in enumerate(hf, 1):
        for k in FIELD_KEYS:
            if not f.get(k):
                err.append(f"Handlungsfeld {i}: '{k}' fehlt")
        if re.search(r"\b\d+\s*(halbe[rn]?\s+)?(Tag|Tage|Stunde|Stunden)\b|\bhalber Tag\b", f.get("erster_schritt", "")):
            err.append(f"Handlungsfeld {i}: Dauerangabe im ersten Schritt")
        g = f.get("graves", {})
        if g and not {g.get("von"), g.get("zu")} <= GRAVES:
            err.append(f"Handlungsfeld {i}: ungültige Graves-Farbe {g}")

    for t in d.get("muster", {}).get("treppe", []):
        if t.get("farbe") not in GRAVES:
            err.append(f"Treppe: ungültige Farbe {t.get('farbe')}")

    for key, s in visible_strings(d):
        if "—" in s or "–" in s:
            err.append(f"Gedankenstrich in '{key}': {s[:60]}...")
        if GRAVES_WORDS.search(s):
            err.append(f"Graves-Begriff im sichtbaren Text '{key}': {s[:60]}...")
        m = UMLAUT_FAKES.search(URLISH.sub(" ", s))
        if m:
            err.append(f"Umlaut-Ersatz in '{key}': {m.group(0)}")

    if check_urls:
        for q in d.get("quellen", []):
            try:
                req = urllib.request.Request(q["url"], method="HEAD", headers={"User-Agent": "Mozilla/5.0"})
                urllib.request.urlopen(req, timeout=10)
            except urllib.error.HTTPError as e:
                # 404/410 = Link tot; 403/429/503 = Bot-Sperre, Link meist ok
                if e.code in (404, 410):
                    err.append(f"Quelle nicht gefunden: {q['url']} ({e.code})")
                else:
                    print(f"Warnung: {q['url']} antwortet {e.code} (manuell prüfen)")
            except Exception as e:  # noqa: BLE001
                print(f"Warnung: {q['url']} nicht prüfbar ({e})")
    return err


def main() -> None:
    if len(sys.argv) < 2:
        sys.exit("Aufruf: python3 scripts/validate.py <slug> [--check-urls]")
    errors = validate(sys.argv[1], "--check-urls" in sys.argv)
    if errors:
        print("FEHLER:\n- " + "\n- ".join(errors))
        sys.exit(1)
    print(f"ok: {sys.argv[1]}")


if __name__ == "__main__":
    main()
