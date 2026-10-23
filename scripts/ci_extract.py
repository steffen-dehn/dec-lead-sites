#!/usr/bin/env python3
"""Zieht CI-Hinweise (Farben, Schriften) einer Website per Direkt-Download.

Aufruf: python3 scripts/ci_extract.py <url> [arbeitsordner]
Gibt die häufigsten Farben (Hex + rgb) und font-family-Werte aus.
Die Auswahl von brand/accent/bg trifft danach ein Mensch bzw. Claude.
"""
import collections
import re
import subprocess
import sys
import tempfile
from pathlib import Path
from urllib.parse import urljoin

UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_0) AppleWebKit/537.36 Chrome/126 Safari/537.36"
NEUTRAL = {"#000000", "#ffffff", "#fff", "#000"}


def fetch(url: str) -> str:
    r = subprocess.run(["curl", "-sSL", "-m", "25", "-A", UA, url], capture_output=True)
    return r.stdout.decode("utf-8", errors="ignore")


def norm_hex(h: str) -> str:
    h = h.lower()
    if len(h) == 4:
        h = "#" + "".join(c * 2 for c in h[1:])
    return h


def main() -> None:
    if len(sys.argv) < 2:
        sys.exit("Aufruf: python3 scripts/ci_extract.py <url> [arbeitsordner]")
    url = sys.argv[1]
    work = Path(sys.argv[2]) if len(sys.argv) > 2 else Path(tempfile.mkdtemp())
    work.mkdir(parents=True, exist_ok=True)

    html = fetch(url)
    (work / "index.html").write_text(html)
    css = html
    links = re.findall(r'<link[^>]+href="([^"]+\.css[^"]*)"', html) + re.findall(r'<link[^>]+href=\'([^\']+\.css[^\']*)\'', html)
    for i, l in enumerate(links[:8]):
        c = fetch(urljoin(url, l.replace("&amp;", "&")))
        (work / f"style{i}.css").write_text(c)
        css += c

    hexes = collections.Counter(norm_hex(h) for h in re.findall(r"#[0-9a-fA-F]{6}\b|#[0-9a-fA-F]{3}\b(?![0-9a-fA-F])", css))
    rgbs = collections.Counter()
    for m in re.findall(r"rgba?\(\s*(\d+)[,\s]+(\d+)[,\s]+(\d+)", css):
        rgbs["#%02x%02x%02x" % tuple(min(255, int(x)) for x in m)] += 1
    fonts = collections.Counter(f.strip().strip("'\"") for f in re.findall(r"font-family\s*:\s*([^;}\"]+)", css))
    gfonts = re.findall(r"fonts\.googleapis\.com/css2?\?family=([^&\"']+)", css)
    theme = re.findall(r'<meta name="theme-color" content="([^"]+)"', html)

    def colorful(c):
        r, g, b = int(c[1:3], 16), int(c[3:5], 16), int(c[5:7], 16)
        return max(r, g, b) - min(r, g, b) > 40

    allc = hexes + rgbs
    print(f"URL: {url}  ({len(html)} Bytes HTML, {len(links)} CSS-Dateien)")
    print("theme-color:", theme)
    print("bunt:   ", [(c, n) for c, n in allc.most_common(60) if colorful(c)][:10])
    print("neutral:", [(c, n) for c, n in allc.most_common(60) if not colorful(c) and c not in NEUTRAL][:8])
    print("fonts:  ", fonts.most_common(6))
    print("google: ", gfonts[:4])


if __name__ == "__main__":
    main()
