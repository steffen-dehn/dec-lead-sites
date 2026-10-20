#!/usr/bin/env python3
"""Baut eine Lead-Seite: template/index.html + leads/<slug>/lead.json -> docs/<slug>-<token>/index.html

Aufruf: python3 scripts/build.py <slug>     (oder --all)
"""
import html
import json
import secrets
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TEMPLATE = ROOT / "template" / "index.html"


def build(slug: str) -> Path:
    lead_path = ROOT / "leads" / slug / "lead.json"
    data = json.loads(lead_path.read_text(encoding="utf-8"))

    # Token einmalig erzeugen und im Datensatz festhalten (stabile URL)
    if not data.get("token"):
        data["token"] = secrets.token_hex(3)
        lead_path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    # "</" im JSON entschärfen, damit kein Inhalt den <script>-Block beenden kann
    payload = json.dumps(data, ensure_ascii=False, indent=2).replace("</", "<\\/")
    page = (
        TEMPLATE.read_text(encoding="utf-8")
        .replace("{{LEAD_JSON}}", payload)
        .replace("{{TITLE}}", html.escape(f"{data['firma']} - Was wird sein"))
    )

    out = ROOT / "docs" / f"{slug}-{data['token']}" / "index.html"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(page, encoding="utf-8")
    return out


def main() -> None:
    if len(sys.argv) != 2:
        sys.exit("Aufruf: python3 scripts/build.py <slug> | --all")
    slugs = (
        [p.name for p in (ROOT / "leads").iterdir() if (p / "lead.json").exists()]
        if sys.argv[1] == "--all"
        else [sys.argv[1]]
    )
    for slug in sorted(slugs):
        print(f"gebaut: {build(slug).relative_to(ROOT)}")


if __name__ == "__main__":
    main()
