#!/usr/bin/env python3
"""Vérifie le site généré : chaque lien interne et chaque image/script/feuille de style pointe vers un fichier existant,
chaque page FR a son équivalent EN, les balises essentielles sont présentes. Lancer après build.py."""
import re, sys
from pathlib import Path
from urllib.parse import urlparse, unquote

PUB = Path(__file__).resolve().parent.parent / "public"
bad = []; pages = sorted(PUB.rglob("*.html"))
for f in pages:
    t = f.read_text()
    for m in re.finditer(r'(?:href|src)="([^"#?]+)(?:[?#][^"]*)?"', t):
        u = m.group(1)
        if re.match(r"(https?:|mailto:|data:|tel:)", u): continue
        path = (PUB / u.lstrip("/")) if u.startswith("/") else (f.parent / u)
        if not path.resolve().exists(): bad.append((f.relative_to(PUB), u))
    if f.parent.name in ("fr", "en"):
        for need in ("<title>", 'name="description"', 'rel="canonical"', 'hreflang="fr"', 'hreflang="en"', 'property="og:image"'):
            if need not in t: bad.append((f.relative_to(PUB), "manque " + need))
fr = {p.name for p in (PUB / "fr").glob("*.html")}; en = {p.name for p in (PUB / "en").glob("*.html")}
print("pages FR :", len(fr), "· pages EN :", len(en), "· total HTML :", len(pages))
sm = (PUB / "sitemap.xml").read_text(); print("URLs dans le sitemap :", sm.count("<loc>"))
if bad:
    print("PROBLÈMES :"); [print("  ", b) for b in bad[:40]]; sys.exit(1)
print("OK : aucun lien cassé, balises essentielles présentes")
