#!/usr/bin/env python3
"""Rendert die gebaute Seite (Desktop 1280 / Mobil 390), prüft JS-Fehler,
horizontalen Scroll und Sichtbarkeit des Daten-Hinweises.

Aufruf: python3 scripts/screenshot.py <slug> [ausgabeordner]
Benötigt: pip install playwright && playwright install chromium
"""
import json
import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parent.parent


def main() -> None:
    if len(sys.argv) < 2:
        sys.exit("Aufruf: python3 scripts/screenshot.py <slug> [ausgabeordner]")
    slug = sys.argv[1]
    out_dir = Path(sys.argv[2]) if len(sys.argv) > 2 else ROOT / ".screenshots"
    out_dir.mkdir(parents=True, exist_ok=True)

    token = json.loads((ROOT / "leads" / slug / "lead.json").read_text(encoding="utf-8"))["token"]
    page_file = ROOT / "docs" / f"{slug}-{token}" / "index.html"
    if not page_file.exists():
        sys.exit(f"Nicht gebaut: {page_file} - zuerst scripts/build.py {slug}")

    problems = []
    with sync_playwright() as p:
        browser = p.chromium.launch()
        for width, name in [(1280, "desktop"), (390, "mobil")]:
            page = browser.new_page(viewport={"width": width, "height": 900})
            errors = []
            page.on("pageerror", lambda e, errors=errors: errors.append(str(e)))
            page.goto(page_file.as_uri())
            page.wait_for_timeout(800)
            if errors:
                problems.append(f"{name}: JS-Fehler {errors}")
            if page.evaluate("document.documentElement.scrollWidth") > width:
                problems.append(f"{name}: horizontaler Scroll")
            if not page.is_visible("#note") or not page.inner_text("#note").strip():
                problems.append(f"{name}: Daten-Hinweis nicht sichtbar")
            shot = out_dir / f"{slug}-{name}.png"
            page.screenshot(path=str(shot), full_page=True)
            print(f"Screenshot: {shot}")
        browser.close()

    if problems:
        print("FEHLER:\n- " + "\n- ".join(problems))
        sys.exit(1)
    print("ok: Rendering")


if __name__ == "__main__":
    main()
