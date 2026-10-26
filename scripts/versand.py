#!/usr/bin/env python3
"""Briefversand über die LetterXpress-API (v3).

Zugangsdaten nur per Umgebungsvariable, nie im Repo:
    LXP_USER  = API-Benutzername (LXPApi..., NICHT E-Mail oder Kundennummer)
    LXP_KEY   = API-Key

Aufrufe:
    python3 scripts/versand.py guthaben
    python3 scripts/versand.py preis
    python3 scripts/versand.py test  <pdf> [<pdf> ...]   # Entwurf in die Postbox, nichts wird gedruckt/abgebucht
    python3 scripts/versand.py live  <pdf> [<pdf> ...]   # druckt und verschickt - nur nach Steffens Freigabe
    python3 scripts/versand.py liste [test|live]
    python3 scripts/versand.py loeschen <job-id> [test|live]   # nur solange Status "queue"/"draft"

Standard: Farbe, einseitig, national (ca. 1,09 EUR brutto pro einseitigem Brief).
Die Ausgabe zeigt die von LetterXpress erkannte Anschrift - immer gegen die Soll-Anschrift prüfen.
"""
import base64
import hashlib
import json
import os
import sys
from pathlib import Path

import requests

API = "https://api.letterxpress.de/v3"
SPEC = {"color": "4", "mode": "simplex", "shipping": "national"}


def auth(mode: str) -> dict:
    return {"username": os.environ["LXP_USER"], "apikey": os.environ["LXP_KEY"], "mode": mode}


def call(method: str, path: str, mode: str = "test", body: dict | None = None) -> dict:
    payload = {"auth": auth(mode), **(body or {})}
    r = requests.request(method, API + path, json=payload, timeout=60)
    try:
        return {"http": r.status_code, **r.json()}
    except ValueError:
        return {"http": r.status_code, "text": r.text[:500]}


def senden(mode: str, pdfs: list[str]) -> None:
    for f in pdfs:
        p = Path(f)
        data = base64.b64encode(p.read_bytes()).decode()
        letter = {
            "base64_file": data,
            "base64_file_checksum": hashlib.md5(data.encode()).hexdigest(),
            "filename_original": p.name,
            "notice": f"DEC Kaltakquise - {p.stem}"[:255],
            "specification": SPEC,
        }
        res = call("POST", "/printjobs", mode, {"letter": letter})
        d = res.get("data") or {}
        item = (d.get("items") or [{}])[0]
        print(json.dumps({"datei": p.name, "http": res["http"], "job": d.get("id"), "status": d.get("status"),
                          "anschrift_erkannt": item.get("address"), "netto": item.get("amount"),
                          "mwst": item.get("vat"), "meldung": res.get("message")}, ensure_ascii=False))


def main() -> None:
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    cmd, args = sys.argv[1], sys.argv[2:]
    if cmd == "guthaben":
        print(call("GET", "/balance"))
    elif cmd == "preis":
        print(call("GET", "/price", body={"letter": {"specification": {"pages": 1, **SPEC}}}))
    elif cmd in ("test", "live"):
        senden(cmd, args)
    elif cmd == "liste":
        res = call("GET", "/printjobs", args[0] if args else "live")
        for j in (res.get("data") or {}).get("printjobs", []):
            print(j["id"], j["status"], j.get("created_at"), (j.get("items") or [{}])[0].get("address"))
    elif cmd == "loeschen":
        print(call("DELETE", f"/printjobs/{args[0]}", args[1] if len(args) > 1 else "test"))
    else:
        sys.exit(__doc__)


if __name__ == "__main__":
    main()
