#!/usr/bin/env python3
"""Lit le catalogue directement dans le code de l'app (Engine/SiteData/*.swift) et écrit data/sites.json.
Le site affiche ainsi toujours les vrais chiffres. À relancer après chaque ajout de sites dans l'app."""
import json, re
from pathlib import Path

APP = Path.home() / "FortChateau-Projet-Complet/01-Application-Xcode/FortChateau/FortChateau"
DATA = APP / "Sources/Engine/SiteData"
OUT = Path(__file__).resolve().parent.parent / "data" / "sites.json"
S = r'"((?:[^"\\]|\\.)*)"'

def un(s): return s.replace('\\"', '"').replace("\\\\", "\\").replace("\\n", " ")

# ---- continents, types
cont = {}
for m in re.finditer(r'case \.(\w+): return LocalizedText\(fr: ' + S + r', en: ' + S + r'\)', (APP / "Sources/Models/Continent.swift").read_text()):
    cont[m.group(1)] = {"fr": un(m.group(2)), "en": un(m.group(3))}
types = {}
for m in re.finditer(r'case \.(\w+):\s*return LocalizedText\(fr: ' + S + r', en: ' + S + r'\)', (APP / "Sources/Models/SiteType.swift").read_text()):
    types[m.group(1)] = {"fr": un(m.group(2)), "en": un(m.group(3))}

# ---- pays
countries = {}
for m in re.finditer(r'static let (\w+) = Country\(\s*id: ' + S + r',\s*name: LocalizedText\(fr: ' + S + r', en: ' + S + r'\),\s*continent: \.(\w+),\s*flagEmoji: ' + S, (DATA / "Countries.swift").read_text()):
    countries[m.group(1)] = dict(id=un(m.group(2)), fr=un(m.group(3)), en=un(m.group(4)), continent=m.group(5), flag=un(m.group(6)))

# ---- sites
sites = []
for f in sorted(DATA.glob("*Sites.swift")):
    for b in re.split(r'\n        Site\(\n', f.read_text())[1:]:
        g = lambda pat: re.search(pat, b, re.S)
        sid = g(r'id: ' + S).group(1)
        desc = g(r'description: LocalizedText\(\s*fr: ' + S + r',\s*en: ' + S + r'\s*\)')
        high = g(r'highlight: LocalizedText\(\s*fr: ' + S + r',\s*en: ' + S + r'\s*\)')
        addr = g(r'address: LocalizedText\(fr: ' + S + r', en: ' + S + r'\)')
        ph = g(r'SitePhoto\(assetName: ' + S + r', credit: PhotoCredit\(author: ' + S + r', license: ' + S + r', sourceURL: ' + S + r'\)')
        sites.append(dict(
            id=sid, name=un(g(r'name: ' + S).group(1)), country=g(r'country: Countries\.(\w+)').group(1),
            city=un(g(r'city: ' + S).group(1)), type=g(r'type: \.(\w+)').group(1),
            desc=dict(fr=un(desc.group(1)), en=un(desc.group(2))), highlight=dict(fr=un(high.group(1)), en=un(high.group(2))),
            address=dict(fr=un(addr.group(1)), en=un(addr.group(2))),
            lat=float(g(r'latitude: (-?[\d.]+)').group(1)), lon=float(g(r'longitude: (-?[\d.]+)').group(1)),
            photo=un(ph.group(1)), credit=dict(author=un(ph.group(2)), license=un(ph.group(3)), url=un(ph.group(4))),
            narrated=bool(re.search(r'narrationAssetNameFR: "', b)),
        ))

# ---- sites gratuits (FreeCatalog.swift)
free_src = (APP / "Sources/Engine/FreeCatalog.swift").read_text().split("freeSiteIds")[1].split("]")[0]
free = re.findall(r'^\s*"([a-z0-9-]+)"', free_src, re.M)
for s in sites: s["free"] = s["id"] in free
assert len(sites) == len({s["id"] for s in sites}), "ids en double"
assert all(s["country"] in countries for s in sites), "pays inconnu"
OUT.parent.mkdir(exist_ok=True)
OUT.write_text(json.dumps(dict(continents=cont, types=types, countries=countries, sites=sites), ensure_ascii=False, indent=1))
print(f"{len(sites)} sites, {len({s['country'] for s in sites})} pays, {sum(s['free'] for s in sites)} gratuits, {sum(s['narrated'] for s in sites)} narrés → {OUT}")
