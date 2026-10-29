#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Génère le site Fort et Château (FR + EN) dans public/, sur le modèle du site Acoustic Detector :
fr/ et en/ (accueil, fonctionnalités, catalogue, téléchargement, contact, confidentialité, crédits photo),
assets/, sitemap.xml, robots.txt, 404, redirection de langue à la racine.

Le catalogue vient de data/sites.json (lu dans le code de l'app par tools/extract_data.py).

INTERRUPTEUR LIVE13 :
  False (état actuel) = l'app en ligne est la 1.2 (payante, 131 sites) : le site ne parle ni de « gratuit », ni
                        d'achat unique, ni des 25 nouveaux châteaux, et utilise les captures 1.2.
  True                = la 1.3 est en ligne (gratuite + achat unique, 156 sites, récits du Barde regroupés).
Le jour de la sortie de la 1.3 : passer LIVE13 à True, lancer ce script, commit + push.

Lancer :  python3 tools/extract_data.py ; python3 tools/prepare_assets.py   (une fois, ou après de nouveaux sites/captures)
          python3 tools/build.py                                          (après toute modification), puis commit + push."""
import html
import json
import sys
import unicodedata
from datetime import date
from pathlib import Path

LIVE13 = False
if "--live13" in sys.argv:        # aperçu : python3 tools/build.py --live13 --out public_preview13
    LIVE13 = True

ROOT = Path(__file__).resolve().parent.parent
PUB = ROOT / sys.argv[sys.argv.index("--out") + 1] if "--out" in sys.argv else ROOT / "public"
SITE = "https://fortchateau.netlify.app"
EMAIL = "j_david@live.ca"
APPSTORE_BASE = "https://apps.apple.com/ca/app/fort-et-ch%C3%A2teau/id6811432420"
APPSTORE = {"fr": APPSTORE_BASE + "?l=fr-CA", "en": APPSTORE_BASE + "?l=en-CA"}
TODAY = date.today().isoformat()
VER_ASSETS = date.today().strftime("%Y%m%d") + "a"   # change à chaque génération : force les navigateurs à recharger le CSS et le JS
UPDATED = {"fr": "29 octobre 2026", "en": "October 29, 2026"}

NEW13 = {"alcazar-de-tolede", "castillo-san-felipe-de-barajas", "chateau-d-angers", "chateau-d-eilean-donan", "chateau-de-blarney", "chateau-de-bunratty",
         "chateau-de-cape-coast", "chateau-de-chapultepec", "chateau-de-kumamoto", "chateau-de-lichtenstein", "chateau-de-miramare", "chateau-de-pierrefonds",
         "chateau-de-predjama", "chateau-de-schwerin", "chateau-de-vaux-le-vicomte", "chateau-de-warwick", "chateau-des-comtes-de-flandre",
         "chateau-scaliger-de-sirmione", "citadelle-de-qaitbay", "fort-de-galle", "fort-rouge-de-delhi", "fort-york", "forteresse-d-akershus",
         "forteresse-de-hohensalzburg", "forteresse-de-louisbourg"}

# ------------------------------------------------------------------ données
DATA = json.loads((ROOT / "data/sites.json").read_text())
SITES = [s for s in DATA["sites"] if LIVE13 or s["id"] not in NEW13]
BYID = {s["id"]: s for s in SITES}
COUNTRIES = DATA["countries"]
N = len(SITES)
C = len({s["country"] for s in SITES})
B = sum(s["narrated"] for s in SITES)
FREE = sum(s["free"] for s in SITES) if LIVE13 else 0
LOCKED = N - FREE
FREE_NARR = sum(s["free"] and s["narrated"] for s in SITES) if LIVE13 else 0
CONT_ORDER = ["europe", "northAmerica", "southAmerica", "asia", "africa", "oceania"]
CONT_COUNT = len({COUNTRIES[s["country"]]["continent"] for s in SITES})


def esc(s): return html.escape(s, quote=True)
def norm(s): return "".join(c for c in unicodedata.normalize("NFD", s.lower()) if unicodedata.category(c) != "Mn")


JDG_APPS = {
    "fr": '<div class="jdg-apps" style="margin-top:18px;padding-top:14px;border-top:1px solid rgba(127,127,127,.3);font-size:.88em;line-height:1.8;text-align:center"><strong>Les autres apps de JDG inc., Québec :</strong> <a href="https://camordtu.netlify.app/">CaMordTu</a> <span style="opacity:.75">(guide de pêche au Québec)</span> · <a href="https://sitedim.netlify.app/fr/index.html">SITE DIM</a> <span style="opacity:.75">(relevé de chantier en réalité augmentée)</span> · <a href="https://appmycreation.com/">MY CREATION</a> <span style="opacity:.75">(vos œuvres en relief 3D et en réalité augmentée)</span> · <a href="https://tricolab.netlify.app/fr/index.html">Tricolab</a> <span style="opacity:.75">(tricot, crochet et scrapbook)</span> · <a href="https://apps.apple.com/ca/app/acoustic-detector/id6810440422?l=fr-CA">Acoustic Detector</a> <span style="opacity:.75">(sonomètre et traitement acoustique)</span></div>',
    "en": '<div class="jdg-apps" style="margin-top:18px;padding-top:14px;border-top:1px solid rgba(127,127,127,.3);font-size:.88em;line-height:1.8;text-align:center"><strong>More apps by JDG inc., Quebec:</strong> <a href="https://camordtu.netlify.app/en.html">CaMordTu</a> <span style="opacity:.75">(Quebec fishing guide)</span> · <a href="https://sitedim.netlify.app/en/index.html">SITE DIM</a> <span style="opacity:.75">(AR construction measuring)</span> · <a href="https://appmycreation.com/index-en.html">MY CREATION</a> <span style="opacity:.75">(your artwork in 3D relief and AR)</span> · <a href="https://tricolab.netlify.app/en/index.html">Tricolab</a> <span style="opacity:.75">(knitting, crochet and scrapbooking)</span> · <a href="https://apps.apple.com/ca/app/acoustic-detector/id6810440422?l=en-CA">Acoustic Detector</a> <span style="opacity:.75">(sound meter and room acoustics)</span></div>',
}

FILES = {
    "home": {"fr": "index.html", "en": "index.html"},
    "features": {"fr": "fonctionnalites.html", "en": "features.html"},
    "catalog": {"fr": "catalogue.html", "en": "catalog.html"},
    "download": {"fr": "telechargement.html", "en": "download.html"},
    "contact": {"fr": "contact.html", "en": "contact.html"},
    "privacy": {"fr": "confidentialite.html", "en": "privacy.html"},
    "credits": {"fr": "credits-photos.html", "en": "photo-credits.html"},
}
NAV_ORDER = ["home", "features", "catalog", "download", "contact"]
FOOT_ORDER = ["home", "features", "catalog", "download", "contact", "privacy", "credits"]
LABEL = {
    "fr": {"home": "Accueil", "features": "Fonctionnalités", "catalog": "Catalogue", "download": "Téléchargement", "contact": "Contact", "privacy": "Confidentialité", "credits": "Crédits photo"},
    "en": {"home": "Home", "features": "Features", "catalog": "Catalog", "download": "Download", "contact": "Contact", "privacy": "Privacy", "credits": "Photo credits"},
}
UI = {
    "fr": dict(cta="Télécharger", store="Télécharger sur l'App Store", more="Voir les fonctionnalités", locale="fr_CA", alt="en_CA", menu="Menu",
               foot="© 2026 JDG inc. — Québec, Canada. Fort et Château est une marque de JDG inc."),
    "en": dict(cta="Download", store="Download on the App Store", more="See all features", locale="en_CA", alt="fr_CA", menu="Menu",
               foot="© 2026 JDG inc. — Quebec, Canada. Fort et Château is a trademark of JDG inc."),
}

# ------------------------------------------------------------------ captures
VER = "s13" if LIVE13 else "s12"
SHOT_KEYS = (["menu", "fiche", "barde", "globe", "duel", "rank", "badges", "carnet"] if LIVE13 else ["menu", "fiche", "globe", "duel", "rank", "badges", "carnet"])
CAP = {
    "fr": dict(menu="Menu", fiche="Fiche et Barde", barde="Récits du Barde", globe="Globe 3D", duel="Duel", rank="Classement", badges="Passeport", carnet="Carnet"),
    "en": dict(menu="Menu", fiche="Page and Bard", barde="Bard's Tales", globe="3D Globe", duel="Duel", rank="Ranking", badges="Passport", carnet="Sketchbook"),
}
ALT = {
    "fr": dict(menu="Menu principal de Fort et Château", fiche="Fiche du château de Chambord avec le médaillon du Barde", barde="Liste des sites racontés par le Barde, par pays",
               globe="Globe 3D et liste des pays d'un continent", duel="Duel entre deux châteaux", rank="Classement personnel des châteaux", badges="Passeport de l'Explorateur et badges",
               carnet="Carnet de croquis d'un site visité"),
    "en": dict(menu="Fort et Château main menu", fiche="Château de Chambord page with the Bard's medallion", barde="List of the sites narrated by the Bard, by country",
               globe="3D globe and the list of a continent's countries", duel="Duel between two castles", rank="Personal castle ranking", badges="Explorer's Passport and badges",
               carnet="Sketchbook entry for a visited site"),
}


def shot(lang, key, cls="", w=280, h=606, lazy=True):
    ld = ' loading="lazy"' if lazy else ""
    return f'<img src="../assets/img/{VER}-{lang}-{key}.webp" alt="{esc(ALT[lang][key])}" width="{w}" height="{h}"{ld} class="{cls}">'


# ------------------------------------------------------------------ gabarit
def page(lang, key, title, desc, body, extra_head="", jsonld=None):
    f = FILES[key][lang]; url = f"{SITE}/{lang}/{f}"; other = "en" if lang == "fr" else "fr"
    cur = ' aria-current="page"'
    nav = "".join('<li><a href="' + FILES[k][lang] + '"' + (cur if k == key else "") + ">" + LABEL[lang][k] + "</a></li>" for k in NAV_ORDER)
    sw = "".join('<a href="' + ("" if l == lang else "../" + l + "/") + FILES[key][l] + '" hreflang="' + l + '" lang="' + l + '"' + (' class="active"' if l == lang else "") + ">" + l.upper() + "</a>" for l in ("fr", "en"))
    foot = "".join(f'<li><a href="{FILES[k][lang]}">{LABEL[lang][k]}</a></li>' for k in FOOT_ORDER)
    ld = f'<script type="application/ld+json">\n{json.dumps(jsonld, ensure_ascii=False, indent=2)}\n</script>\n' if jsonld else ""
    return f"""<!DOCTYPE html>
<html lang="{lang}">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)}</title>
<meta name="description" content="{esc(desc)}">
<link rel="canonical" href="{url}">
<link rel="alternate" hreflang="fr" href="{SITE}/fr/{FILES[key]['fr']}">
<link rel="alternate" hreflang="en" href="{SITE}/en/{FILES[key]['en']}">
<link rel="alternate" hreflang="x-default" href="{SITE}/fr/{FILES[key]['fr']}">
<meta property="og:type" content="website">
<meta property="og:site_name" content="Fort et Château">
<meta property="og:title" content="{esc(title)}">
<meta property="og:description" content="{esc(desc)}">
<meta property="og:url" content="{url}">
<meta property="og:image" content="{SITE}/assets/img/og-image-{lang}.png">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:locale" content="{UI[lang]['locale']}">
<meta property="og:locale:alternate" content="{UI[lang]['alt']}">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{esc(title)}">
<meta name="twitter:description" content="{esc(desc)}">
<meta name="twitter:image" content="{SITE}/assets/img/og-image-{lang}.png">
<meta name="theme-color" content="#14100D">
<meta name="author" content="JDG inc.">
<meta name="apple-itunes-app" content="app-id=6811432420">
{ld}<link rel="icon" type="image/png" sizes="48x48" href="../assets/favicon-48.png">
<link rel="apple-touch-icon" href="../assets/apple-touch-icon.png">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Cinzel:wght@500;600;700;800&family=Lora:ital,wght@0,400;0,500;0,600;1,400&display=swap" rel="stylesheet">
<link rel="stylesheet" href="../assets/css/style.css?v={VER_ASSETS}">
{extra_head}</head>
<body>

<header class="site-header">
  <div class="container site-header__row">
    <a href="index.html" class="brand"><img src="../assets/img/logo-mark.png" alt="" class="brand-mark" width="40" height="40">Fort et Château</a>
    <nav class="main-nav" id="main-nav" aria-label="{UI[lang]['menu']}">
      <ul class="main-nav__links">{nav}</ul>
    </nav>
    <div class="header-actions">
      <div class="lang-switch">{sw}</div>
      <a href="{FILES['download'][lang]}" class="btn btn--primary btn--sm">{UI[lang]['cta']}</a>
      <button class="nav-toggle" aria-label="{UI[lang]['menu']}" aria-expanded="false" aria-controls="main-nav"><span></span><span></span><span></span></button>
    </div>
  </div>
</header>

<main>
{body}
</main>

<footer class="site-footer">
  <div class="container">
    <div class="site-footer__row">
      <div class="site-footer__brand"><img src="../assets/img/logo-mark.png" alt="" class="brand-mark" width="32" height="32">Fort et Château</div>
      <nav aria-label="Pied de page"><ul>{foot}</ul></nav>
    </div>
    <p class="site-footer__meta">{UI[lang]['foot']}</p>
    {JDG_APPS[lang]}
  </div>
</footer>
<script src="../assets/js/main.js?v={VER_ASSETS}" defer></script>
</body>
</html>
"""


def store_btn(lang, cls="btn btn--primary"):
    return f'<a href="{APPSTORE[lang]}" class="{cls}" target="_blank" rel="noopener">{UI[lang]["store"]}</a>'


def cta_band(lang):
    t = {"fr": ("Prêt à explorer ?", "Téléchargez Fort et Château sur l'App Store et partez à la découverte des forteresses du monde."),
         "en": ("Ready to explore?", "Download Fort et Château on the App Store and set off to discover the world's fortresses.")}[lang]
    return f'<section><div class="container"><div class="cta-band"><h2>{t[0]}</h2><p>{t[1]}</p>{store_btn(lang)}</div></div></section>'


ORN = '<div class="ornament" aria-hidden="true"><i></i></div>'

# ------------------------------------------------------------------ textes
def fmt_n(n): return str(n)


def site_name(sid): return BYID[sid]["name"]


def ctry(s, lang): return COUNTRIES[s["country"]][lang]


MOSAIC_IDS = ["chateau-de-chambord", "chateau-d-himeji", "chateau-de-neuschwanstein", "alhambra", "cite-interdite", "cite-de-carcassonne"]


def mosaic(lang):
    figs = "".join(f'<figure><img src="../assets/img/p/{i}.webp" alt="{esc(BYID[i]["name"])}, {esc(ctry(BYID[i], lang))}" width="960" height="640" loading="lazy"><figcaption>{esc(BYID[i]["name"])}<small>{esc(ctry(BYID[i], lang))}</small></figcaption></figure>' for i in MOSAIC_IDS)
    cr = {"fr": f'Photos : Wikimedia Commons (licences libres). <a href="{FILES["credits"]["fr"]}">Crédits détaillés</a>.',
          "en": f'Photos: Wikimedia Commons (free licenses). <a href="{FILES["credits"]["en"]}">Full credits</a>.'}[lang]
    return f'<div class="mosaic">{figs}</div><p class="note">{cr}</p>'


def audio_cards(lang):
    out = ""
    for sid, label in (("chateau-de-chambord", ""), ("chateau-d-himeji", "")):
        s = BYID[sid]
        out += (f'<div class="player"><h4>{esc(s["name"])} <span class="gold">· {esc(ctry(s, lang))}</span></h4>'
                f'<audio controls preload="none" src="../assets/audio/{sid}-{lang}.mp3"></audio><p>{esc(s["desc"][lang])}</p></div>')
    return out


def plans(lang):
    if not LIVE13: return ""
    fr = lang == "fr"
    free = [f"{FREE} forts et châteaux emblématiques, un par pays" if fr else f"{FREE} emblematic forts and castles, one per country",
            "Globe 3D, recherche et « Autour de moi »" if fr else "3D globe, search and “Near me”",
            "Duel et classement sur ces sites" if fr else "Duel and ranking on these sites",
            "Passeport, badges et Carnet de croquis" if fr else "Passport, badges and Sketchbook",
            f"Récits du Barde sur {FREE_NARR} sites" if fr else f"Bard's tales on {FREE_NARR} sites"]
    full = [f"Les {LOCKED} autres forts et châteaux" if fr else f"The other {LOCKED} forts and castles",
            "Le Duel sur tout le catalogue" if fr else "The Duel across the whole catalog",
            f"Les {B} récits du Barde" if fr else f"All {B} Bard's tales",
            "Un seul achat, sans abonnement" if fr else "One purchase, no subscription",
            "Pour toujours, à restaurer sur vos appareils" if fr else "Forever, restorable on your devices"]
    li = lambda xs: "".join(f"<li>{x}</li>" for x in xs)
    return (f'<div class="plans"><div class="plan"><h3>{"Gratuit" if fr else "Free"}</h3><p class="price">{"Au téléchargement" if fr else "On download"}</p><ul>{li(free)}</ul></div>'
            f'<div class="plan plan--full"><h3>{"Tous les châteaux" if fr else "All Castles"}</h3><p class="price">{"2,99 $ CA · achat unique" if fr else "$2.99 CAD · one-time purchase"}</p><ul>{li(full)}</ul></div></div>')


def home(lang):
    fr = lang == "fr"
    if fr:
        title = f"Fort et Château — {N} forts et châteaux du monde sur iPhone et iPad"
        desc = f"{N} forts et châteaux dans {C} pays : globe 3D, Duel, récits du Barde, Passeport d'Explorateur. iPhone et iPad, FR/EN, sans compte ni pub."
        eyebrow = "L'index des forteresses du monde"
        h1 = 'À la découverte des <span class="gold">forteresses du monde.</span>'
        lead = (f"Fort et Château réunit {N} forts, châteaux et palais dans {C} pays. Faites tourner le globe 3D, écoutez le Barde raconter l'histoire des lieux, "
                "défiez vos châteaux préférés en duel et remplissez votre Passeport d'Explorateur. Percez leurs secrets.")
        meta = [("iOS 17+", "requis"), ("iPhone et iPad", ""), ("FR · EN", ""), ("Gratuite", "achat unique facultatif") if LIVE13 else ("Sans compte", "ni publicité")]
    else:
        title = f"Fort et Château — {N} forts and castles of the world for iPhone and iPad"
        desc = f"{N} forts and castles in {C} countries: 3D globe, Castle Duel, the Bard's tales and an Explorer's Passport. iPhone and iPad, FR/EN, no account, no ads."
        eyebrow = "The index of the world's fortresses"
        h1 = 'Discover the <span class="gold">world\'s fortresses.</span>'
        lead = (f"Fort et Château (Fort and Castle in English) gathers {N} forts, castles and palaces across {C} countries. Spin the 3D globe, listen to the Bard tell the story of each place, "
                "duel your favorite castles and fill your Explorer's Passport. Unlock their secrets.")
        meta = [("iOS 17+", "required"), ("iPhone & iPad", ""), ("FR · EN", ""), ("Free", "optional one-time purchase") if LIVE13 else ("No account", "no ads")]
    metas = "".join(f"<span><strong>{a}</strong> {b}</span>" if b else f"<span><strong>{a}</strong></span>" for a, b in meta)

    hero = f"""<section class="hero">
  <div class="container hero__grid">
    <div>
      <p class="eyebrow">{eyebrow}</p>
      <h1>{h1}</h1>
      <p class="lead">{lead}</p>
      <div class="hero__actions">{store_btn(lang)}<a href="{FILES['features'][lang]}" class="btn btn--outline">{UI[lang]['more']}</a></div>
      <div class="hero__meta">{metas}</div>
    </div>
    <div class="hero__visual"><img src="../assets/img/hero-{lang}.webp" alt="{esc('Fiche du château de Chambord et Duel entre deux châteaux dans l’app' if fr else 'Château de Chambord page and a duel between two castles in the app')}" width="1000" height="949"></div>
  </div>
</section>
{ORN}"""

    st = [(N, "forts, châteaux et palais" if fr else "forts, castles and palaces"), (C, "pays" if fr else "countries"),
          (B, "récits du Barde" if fr else "Bard's tales"), (10, "badges à gagner" if fr else "badges to earn")]
    stats = '<section class="section--tight"><div class="container"><div class="stats">' + "".join(f'<div class="stat"><b>{a}</b><span>{b}</span></div>' for a, b in st) + "</div></div></section>"

    news = ""
    if LIVE13:
        if fr:
            items = [f"Fort et Château est maintenant gratuit à télécharger : un site par pays est offert ({FREE} forts et châteaux emblématiques), un achat unique débloque tout le reste",
                     "25 nouveaux forts et châteaux, dont 6 nouveaux pays : Autriche, Belgique, Slovénie, Norvège, Mexique et Colombie",
                     "Nouvelle section « Les récits du Barde » : tous les sites racontés, réunis par pays",
                     f"Au total : {N} sites dans {C} pays"]
            news = ('<section class="section--tight"><div class="container"><div class="card card--new"><span class="badge-new">Nouveauté</span>'
                    '<h2 style="margin-top:16px">Version 1.3 : gratuite, plus de châteaux</h2>'
                    '<p class="lead" style="margin-bottom:0">Le voyage s\'agrandit : plus de pays, plus de récits, et un point de départ gratuit.</p>'
                    '<ul class="changelog-list">' + "".join(f"<li>{i}</li>" for i in items) + "</ul></div></div></section>")
        else:
            items = [f"Fort et Château is now free to download: one site per country is included ({FREE} emblematic forts and castles), and a one-time purchase unlocks the rest",
                     "25 new forts and castles, including 6 new countries: Austria, Belgium, Slovenia, Norway, Mexico and Colombia",
                     "New “The Bard's Tales” section: every narrated site, grouped by country",
                     f"In total: {N} sites in {C} countries"]
            news = ('<section class="section--tight"><div class="container"><div class="card card--new"><span class="badge-new">New</span>'
                    '<h2 style="margin-top:16px">Version 1.3: free, and more castles</h2>'
                    '<p class="lead" style="margin-bottom:0">The journey keeps growing: more countries, more tales, and a free starting point.</p>'
                    '<ul class="changelog-list">' + "".join(f"<li>{i}</li>" for i in items) + "</ul></div></div></section>")

    if fr:
        cards = [("Globe 3D", f"Faites tourner le globe, touchez un continent et découvrez ses pays : {C} pays sur {CONT_COUNT} continents."),
                 ("Fiches illustrées", "Photo, histoire du lieu, carte pour tracer la route et un « Secret du Château » à révéler en grattant l'écran."),
                 ("Le Barde", f"Touchez son médaillon : une voix raconte l'histoire du lieu, en français ou en anglais. {B} sites racontés."),
                 ("Duel de châteaux", "Deux châteaux, un seul choix. Votre classement personnel se construit duel après duel, avec un Top 3 à partager."),
                 ("Passeport de l'Explorateur", "Sur place, validez votre visite : votre sceau de cire est apposé (position vérifiée à moins de 300 m). 10 badges à gagner."),
                 ("Carnet de croquis", "Notes privées, photos de votre visite, note de beauté et d'accessibilité, pour garder la mémoire de chaque lieu.")]
        h_feat, e_feat = "Un seul voyage, six façons d'explorer", "Ce que fait Fort et Château"
    else:
        cards = [("3D Globe", f"Spin the globe, touch a continent and discover its countries: {C} countries across {CONT_COUNT} continents."),
                 ("Illustrated pages", "Photo, the place's history, a map to get directions and a “Castle Secret” you reveal by scratching the screen."),
                 ("The Bard", f"Touch the medallion: a voice tells the story of the place, in French or English. {B} narrated sites."),
                 ("Castle Duel", "Two castles, one choice. Your personal ranking builds up duel after duel, with a Top 3 to share."),
                 ("Explorer's Passport", "On site, validate your visit: your wax seal is stamped (position checked within 300 m). 10 badges to earn."),
                 ("Sketchbook", "Private notes, photos from your visit, beauty and accessibility ratings, to keep the memory of every place.")]
        h_feat, e_feat = "One journey, six ways to explore", "What Fort et Château does"
    feats = f'<section class="section--alt"><div class="container"><div class="section-head"><p class="eyebrow">{e_feat}</p><h2>{h_feat}</h2></div><div class="grid-3">' + "".join(f'<div class="card"><h3>{a}</h3><p>{b}</p></div>' for a, b in cards) + "</div></div></section>"

    mos = (f'<section><div class="container"><div class="section-head"><p class="eyebrow">{"Le catalogue" if fr else "The catalog"}</p>'
           f'<h2>{"De Chambord à Himeji" if fr else "From Chambord to Himeji"}</h2>'
           f'<p class="lead">{f"Châteaux de conte de fées, citadelles, forts côtiers, palais fortifiés : {N} lieux à découvrir, de l’Europe à l’Océanie." if fr else f"Fairy-tale castles, citadels, coastal forts, fortified palaces: {N} places to discover, from Europe to Oceania."}</p></div>'
           f'{mosaic(lang)}<p style="margin-top:22px"><a class="btn btn--outline" href="{FILES["catalog"][lang]}">{"Parcourir le catalogue" if fr else "Browse the catalog"}</a></p></div></section>')

    bard = (f'<section class="section--alt"><div class="container"><div class="bard"><div class="bard__medal"><img src="../assets/img/barde.webp" alt="{"Médaillon du Barde" if fr else "The Bard’s medallion"}" width="210" height="210" loading="lazy"></div>'
            f'<div><p class="eyebrow">{"Le Barde" if fr else "The Bard"}</p><h2>{"Écoutez l’histoire des lieux" if fr else "Listen to the story of each place"}</h2>'
            f'<p class="lead">{"Sur les sites phares, le Barde raconte le lieu en une vingtaine de secondes. Essayez avec deux extraits :" if fr else "On flagship sites, the Bard tells the story of the place in about twenty seconds. Try two samples:"}</p>'
            f'{audio_cards(lang)}</div></div></div></section>')

    shots = "".join(f'<figure>{shot(lang, k)}<figcaption>{CAP[lang][k]}</figcaption></figure>' for k in SHOT_KEYS)
    gal = (f'<section><div class="container"><div class="section-head"><p class="eyebrow">{"Aperçu" if fr else "Preview"}</p>'
           f'<h2>{"L’app, de l’intérieur" if fr else "Inside the app"}</h2></div><div class="shots">{shots}</div></div></section>')

    pl = ""
    if LIVE13:
        pl = (f'<section class="section--alt"><div class="container"><div class="section-head"><p class="eyebrow">{"Gratuit pour commencer" if fr else "Free to start"}</p>'
              f'<h2>{"Un site par pays, tout le reste en un seul achat" if fr else "One site per country, everything else in one purchase"}</h2></div>{plans(lang)}</div></section>')

    priv = (f'<section class="section--tight"><div class="container"><div class="callout"><p><strong>{"Aucun compte, aucune publicité, aucun suivi." if fr else "No account, no ads, no tracking."}</strong> '
            f'{"Tout le contenu (fiches, photos, récits du Barde) est dans l’app, qui fonctionne hors ligne. Votre position et vos carnets restent sur votre appareil." if fr else "All the content (pages, photos, Bard’s tales) is inside the app, which works offline. Your location and sketchbooks stay on your device."} '
            f'<a href="{FILES["privacy"][lang]}">{"Politique de confidentialité" if fr else "Privacy policy"}</a></p></div></div></section>')

    ld = {"@context": "https://schema.org", "@type": "MobileApplication", "name": "Fort et Château", "alternateName": "Fort and Castle",
          "operatingSystem": "iOS 17+", "applicationCategory": "TravelApplication", "url": f"{SITE}/{lang}/", "description": desc,
          "inLanguage": ["fr", "en"], "image": f"{SITE}/assets/img/logo-large.png", "installUrl": APPSTORE[lang], "sameAs": [APPSTORE_BASE],
          "offers": {"@type": "Offer", "price": "0" if LIVE13 else "2.99", "priceCurrency": "CAD"},
          "publisher": {"@type": "Organization", "name": "JDG inc.", "address": {"@type": "PostalAddress", "addressRegion": "QC", "addressCountry": "CA"}}}
    body = hero + stats + news + feats + mos + bard + gal + pl + priv + cta_band(lang)
    return page(lang, "home", title, desc, body, jsonld=ld)


def features(lang):
    fr = lang == "fr"
    title = "Fonctionnalités — Fort et Château" if fr else "Features — Fort et Château"
    desc = ("Globe 3D, fiches avec secret à gratter, récits du Barde, Duel de châteaux, Passeport d'Explorateur et Carnet de croquis : tout ce que fait Fort et Château."
            if fr else "3D globe, pages with a scratch-to-reveal secret, the Bard's tales, Castle Duel, Explorer's Passport and Sketchbook: everything Fort et Château does.")

    def row(k, h, paras, bullets, img):
        bl = "<ul>" + "".join(f"<li>{b}</li>" for b in bullets) + "</ul>" if bullets else ""
        if img == "medal":   # avant la 1.3, pas de capture de la liste du Barde : on montre son médaillon
            media = ('<div class="feature__img feature__img--medal"><img src="../assets/img/barde.webp" alt="' + ("Médaillon du Barde" if lang == "fr" else "The Bard’s medallion") + '" width="420" height="420" loading="lazy"></div>')
        else:
            media = f'<div class="feature__img">{shot(lang, img, w=340, h=736)}</div>'
        return (f'<div class="feature"><div><h2>{h}</h2>' + "".join(f"<p>{p}</p>" for p in paras) + bl + "</div>" + media + "</div>")
    if fr:
        rows = [
            row("globe", "Un globe 3D à faire tourner", [f"Faites tourner le globe du bout du doigt, touchez un continent et découvrez les pays qu'il compte. {C} pays répartis sur {CONT_COUNT} continents, de la France au Japon, du Pérou à la Nouvelle-Zélande."],
                ["Recherche par nom de château, ville ou pays", "« Autour de moi » : les sites les plus proches de votre position", "Classement par pays, avec le nombre de sites"], "globe"),
            row("fiche", "Une fiche pour chaque lieu", ["Photo, type de site, histoire du lieu et carte pour tracer la route avec Plans. Sur chaque fiche, un « Secret du Château » se cache sous une couche à gratter : une anecdote à révéler du bout du doigt."],
                ["Photos libres de droits, avec leur crédit sous l'image", "Itinéraire en un geste", "Contenu intégré à l'app : tout fonctionne hors ligne"], "fiche"),
            row("barde", "Le Barde raconte les lieux", [f"Touchez le médaillon du Barde : une voix chaleureuse raconte l'histoire du château, en français ou en anglais. {B} sites sont racontés" + (", réunis dans la section « Les récits du Barde »." if LIVE13 else ".")],
                ["Une vingtaine de secondes par récit", "Lecture et pause d'un geste"] + ([f"Récits du Barde regroupés par pays dans une liste dédiée"] if LIVE13 else []), "barde" if LIVE13 else "medal"),
            row("duel", "Le Duel de châteaux", ["Deux châteaux s'affrontent : glissez ou touchez pour désigner votre préféré. Votre classement personnel se construit duel après duel, et vous pouvez partager votre Top 3 en une image."],
                ["Classement par nombre de victoires", "Carte « Mon Top 3 » à partager", "Remise à zéro quand vous voulez"], "duel"),
            row("badges", "Le Passeport de l'Explorateur", ["Sur place, validez votre visite : votre sceau de cire est apposé (position vérifiée à moins de 300 m) et vous pouvez partager votre carte « Explorateur Confirmé »."],
                ["Liste de Conquêtes : les sites que vous voulez visiter", "10 badges : Premier Sceau, Cosmopolite, Tour du Monde…", "Position utilisée uniquement sur l'appareil"], "badges"),
            row("carnet", "Le Carnet de croquis", ["Pour chaque site visité, gardez vos notes, vos photos, une note de beauté et une note d'accessibilité. Tout reste privé, sur votre appareil."],
                ["Notes libres", "Jusqu'à 6 photos par site", "Rien n'est partagé sans votre geste"], "carnet"),
        ]
        also_h, also = "Et aussi", ["Interface entièrement bilingue français / anglais, au choix en haut du menu", "iPhone et iPad", "Aucun compte, aucune publicité, aucun suivi", "Fonctionne hors ligne", "Cartes à partager : Explorateur Confirmé et Top 3"]
        if LIVE13: also.append("Gratuit à télécharger, un achat unique débloque tout le catalogue")
        head_p = "Tout ce que fait Fort et Château, du globe 3D au Carnet de croquis."
    else:
        rows = [
            row("globe", "A 3D globe to spin", [f"Spin the globe with your fingertip, touch a continent and discover its countries. {C} countries across {CONT_COUNT} continents, from France to Japan, from Peru to New Zealand."],
                ["Search by castle name, city or country", "“Near me”: the sites closest to your location", "Browse by country, with the number of sites"], "globe"),
            row("fiche", "A page for every place", ["Photo, type of site, the place's history and a map to get directions with Maps. Every page hides a “Castle Secret” under a scratch layer: an anecdote to reveal with your fingertip."],
                ["Free-licensed photos, credited under each image", "Directions in one tap", "Content built into the app: everything works offline"], "fiche"),
            row("barde", "The Bard tells the places", [f"Touch the Bard's medallion: a warm voice tells the story of the castle, in French or English. {B} sites are narrated" + (", gathered in the “Bard's Tales” section." if LIVE13 else ".")],
                ["About twenty seconds per tale", "Play and pause with a tap"] + (["Bard's tales grouped by country in a dedicated list"] if LIVE13 else []), "barde" if LIVE13 else "medal"),
            row("duel", "The Castle Duel", ["Two castles face off: swipe or tap to pick your favorite. Your personal ranking builds up duel after duel, and you can share your Top 3 as an image."],
                ["Ranking by number of wins", "Shareable “My Top 3” card", "Reset whenever you like"], "duel"),
            row("badges", "The Explorer's Passport", ["On site, validate your visit: your wax seal is stamped (position checked within 300 m) and you can share your “Confirmed Explorer” card."],
                ["Conquest List: the sites you want to visit", "10 badges: First Seal, Cosmopolitan, World Tour…", "Location used on the device only"], "badges"),
            row("carnet", "The Sketchbook", ["For every visited site, keep your notes, your photos, a beauty rating and an accessibility rating. Everything stays private, on your device."],
                ["Free-form notes", "Up to 6 photos per site", "Nothing is shared without your tap"], "carnet"),
        ]
        also_h, also = "And also", ["Fully bilingual French / English interface, switchable at the top of the menu", "iPhone and iPad", "No account, no ads, no tracking", "Works offline", "Shareable cards: Confirmed Explorer and Top 3"]
        if LIVE13: also.append("Free to download, one purchase unlocks the whole catalog")
        head_p = "Everything Fort et Château does, from the 3D globe to the Sketchbook."
    body = (f'<section class="page-head"><div class="container"><p class="eyebrow">{LABEL[lang]["features"]}</p><h1>{"Explorer, écouter, collectionner" if fr else "Explore, listen, collect"}</h1><p class="lead">{head_p}</p></div></section>'
            f'<section><div class="container">{"".join(rows)}</div></section>'
            f'<section class="section--alt"><div class="container"><div class="section-head"><h2>{also_h}</h2></div><ul class="tick-list">' + "".join(f"<li>{a}</li>" for a in also) + "</ul></div></section>" + cta_band(lang))
    return page(lang, "features", title, desc, body)


def catalog(lang):
    fr = lang == "fr"
    title = f"Catalogue — {N} forts et châteaux du monde" if fr else f"Catalog — {N} forts and castles of the world"
    desc = (f"Les {N} forts, châteaux et palais de Fort et Château, classés par continent et par pays : de Chambord à la Cité interdite, de l'Alhambra à Himeji."
            if fr else f"The {N} forts, castles and palaces of Fort et Château, by continent and country: from Chambord to the Forbidden City, from the Alhambra to Himeji.")
    chips = f'<button class="chip on" data-c="all">{"Tous" if fr else "All"}</button>' + "".join(
        f'<button class="chip" data-c="{c}">{DATA["continents"][c][lang]}</button>' for c in CONT_ORDER if any(COUNTRIES[s["country"]]["continent"] == c for s in SITES))
    blocks = ""
    for c in CONT_ORDER:
        cs = sorted({s["country"] for s in SITES if COUNTRIES[s["country"]]["continent"] == c}, key=lambda k: norm(COUNTRIES[k][lang]))
        if not cs: continue
        n_c = sum(1 for s in SITES if COUNTRIES[s["country"]]["continent"] == c)
        blocks += f'<div class="continent" id="{c}"><h2>{DATA["continents"][c][lang]} <small class="gold" style="font-size:.5em">· {n_c}</small></h2>'
        for k in cs:
            co = COUNTRIES[k]; ss = sorted([s for s in SITES if s["country"] == k], key=lambda s: norm(s["name"]))
            blocks += f'<div class="country"><h3>{co["flag"]} {esc(co[lang])} <small>· {len(ss)}</small></h3><div class="sites">'
            for s in ss:
                tags = ""
                if s["narrated"]: tags += f'<span class="tag">{"Barde" if fr else "Bard"}</span>'
                if LIVE13 and s["free"]: tags += f'<span class="tag tag--free">{"Gratuit" if fr else "Free"}</span>'
                search = norm(" ".join([s["name"], s["city"], co["fr"], co["en"], DATA["types"][s["type"]]["fr"], DATA["types"][s["type"]]["en"]]))
                blocks += (f'<article class="site" data-c="{c}" data-s="{esc(search)}"><img src="../assets/img/t/{s["id"]}.webp" alt="{esc(s["name"])}, {esc(s["city"])}" width="480" height="320" loading="lazy">'
                           f'<div class="site__b"><h4>{esc(s["name"])}</h4><p>{esc(s["city"])} · {esc(DATA["types"][s["type"]][lang])}</p>{tags}</div></article>')
            blocks += "</div></div>"
        blocks += "</div>"
    tpl = "{n} sites affichés" if fr else "{n} sites shown"
    tpl1 = "{n} site affiché" if fr else "{n} site shown"
    intro = (f"{N} forts, châteaux et palais dans {C} pays. Cherchez par nom, ville ou pays, ou filtrez par continent." if fr
             else f"{N} forts, castles and palaces in {C} countries. Search by name, city or country, or filter by continent.")
    free_note = ""
    if LIVE13:
        free_note = (f'<p class="note">{"Les sites marqués « Gratuit » sont offerts dans l’app ; un achat unique débloque tous les autres." if fr else "Sites marked “Free” are included in the app; a one-time purchase unlocks all the others."}</p>')
    ph = "Rechercher un château, une ville, un pays…" if fr else "Search a castle, a city, a country…"
    body = (f'<section class="page-head"><div class="container"><p class="eyebrow">{LABEL[lang]["catalog"]}</p><h1>{"Tous les forts et châteaux" if fr else "Every fort and castle"}</h1><p class="lead">{intro}</p></div></section>'
            f'<section style="padding-top:30px"><div class="container"><div class="toolbar"><div class="search"><input id="q" type="search" placeholder="{ph}" aria-label="{ph}" autocomplete="off"></div><div class="chips">{chips}</div></div>'
            f'<p class="count" id="count" data-tpl="{tpl}" data-tpl1="{tpl1}"></p>{blocks}{free_note}'
            f'<p class="note">{"Photos : Wikimedia Commons (licences libres), " if fr else "Photos: Wikimedia Commons (free licenses), "}<a href="{FILES["credits"][lang]}">{"crédits détaillés" if fr else "full credits"}</a>.</p></div></section>' + cta_band(lang))
    return page(lang, "catalog", title, desc, body)


def download(lang):
    fr = lang == "fr"
    title = "Télécharger Fort et Château sur l'App Store" if fr else "Download Fort et Château on the App Store"
    desc = ("Téléchargez Fort et Château sur l'App Store pour iPhone et iPad (iOS 17 ou plus) : globe 3D, Duel, récits du Barde et Passeport d'Explorateur."
            if fr else "Download Fort et Château on the App Store for iPhone and iPad (iOS 17 or later): 3D globe, Duel, the Bard's tales and an Explorer's Passport.")
    req = ([("Appareils", "iPhone et iPad"), ("Système", "iOS 17.0 ou plus récent"), ("Langues", "Français et anglais"), ("Connexion", "Non requise pour le contenu de l'app"), ("Compte", "Aucun compte à créer")]
           if fr else [("Devices", "iPhone and iPad"), ("System", "iOS 17.0 or later"), ("Languages", "French and English"), ("Connection", "Not required for the app's content"), ("Account", "No account to create")])
    rows = "".join(f'<div class="card"><h3>{a}</h3><p>{b}</p></div>' for a, b in req)
    pl = ""
    if LIVE13:
        pl = (f'<section class="section--alt"><div class="container"><div class="section-head"><p class="eyebrow">{"Gratuit, puis un seul achat" if fr else "Free, then one purchase"}</p><h2>{"Comment ça marche" if fr else "How it works"}</h2>'
              f'<p class="lead">{"Téléchargez l’app gratuitement : un site par pays est offert. Pour tout débloquer, touchez « Débloquer » dans l’app : un seul achat, sans abonnement, valable pour toujours. Vous changez d’appareil ? Touchez « Restaurer mon achat »." if fr else "Download the app for free: one site per country is included. To unlock everything, tap “Unlock” in the app: a single purchase, no subscription, yours forever. New device? Tap “Restore my purchase”."}</p></div>{plans(lang)}</div></section>')
    body = (f'<section class="page-head"><div class="container"><p class="eyebrow">{LABEL[lang]["download"]}</p><h1>{"Partez à la découverte" if fr else "Set off to discover"}</h1>'
            f'<p class="lead">{"Fort et Château est disponible sur l’App Store." if fr else "Fort et Château is available on the App Store."}</p><div class="hero__actions">{store_btn(lang)}</div></div></section>'
            f'<section><div class="container"><div class="section-head"><h2>{"Configuration requise" if fr else "Requirements"}</h2></div><div class="grid-3">{rows}</div></div></section>{pl}' + cta_band(lang))
    return page(lang, "download", title, desc, body)


def faq_items(lang):
    fr = lang == "fr"
    q = []
    if fr:
        q += [("Faut-il créer un compte ?", "Non. Fort et Château n'a ni compte, ni serveur, ni publicité. Vos données restent sur votre appareil."),
              ("L'app fonctionne-t-elle hors ligne ?", "Oui. Les fiches, les photos et les récits du Barde sont intégrés à l'app. Seule la carte d'une fiche (Plans d'Apple) a besoin d'une connexion pour s'afficher."),
              ("Pourquoi l'app demande-t-elle ma position ?", "Pour afficher la distance jusqu'aux sites, proposer ceux qui sont près de vous et activer « Valider ma visite » à moins de 300 m d'un site. Elle est traitée sur l'appareil et jamais envoyée. Vous pouvez la refuser : le reste de l'app fonctionne."),
              ("Comment changer de langue ?", "Touchez FR / EN en haut du menu principal : toute l'interface passe en français ou en anglais."),
              ("Y a-t-il une version iPad ?", "Oui, l'app est conçue pour l'iPhone et l'iPad.")]
        if LIVE13:
            q += [("Comment débloquer tous les châteaux ?", "Touchez la rangée dorée « Débloquer les autres châteaux » en haut du menu, ou le bouton « Tout débloquer » sur la fiche d'un site verrouillé. L'achat est unique, sans abonnement."),
                  ("J'ai changé d'iPhone : comment retrouver mon achat ?", "Ouvrez l'écran de déblocage et touchez « Restaurer mon achat », avec le même identifiant Apple.")]
        q += [("Un château manque ou une information est erronée.", f"Écrivez-nous à {EMAIL} : nous ajoutons des sites et corrigeons les fiches régulièrement."),
              ("D'où viennent les photos ?", "De Wikimedia Commons, sous licences libres. Le crédit de chaque photo est affiché sous l'image dans l'app et listé sur la page des crédits photo.")]
    else:
        q += [("Do I need an account?", "No. Fort et Château has no account, no server and no ads. Your data stays on your device."),
              ("Does it work offline?", "Yes. Pages, photos and the Bard's tales are built into the app. Only a page's map (Apple Maps) needs a connection to display."),
              ("Why does the app ask for my location?", "To show the distance to sites, suggest the ones near you and enable “Validate my visit” within 300 m of a site. It is processed on the device and never sent anywhere. You can decline: the rest of the app works."),
              ("How do I switch language?", "Tap FR / EN at the top of the main menu: the whole interface switches to French or English."),
              ("Is there an iPad version?", "Yes, the app is designed for iPhone and iPad.")]
        if LIVE13:
            q += [("How do I unlock every castle?", "Tap the gold row “Unlock the other castles” at the top of the menu, or the “Unlock everything” button on a locked site's page. It is a one-time purchase, no subscription."),
                  ("I got a new iPhone: how do I get my purchase back?", "Open the unlock screen and tap “Restore my purchase”, with the same Apple ID.")]
        q += [("A castle is missing or a detail is wrong.", f"Write to us at {EMAIL}: we add sites and fix pages regularly."),
              ("Where do the photos come from?", "From Wikimedia Commons, under free licenses. Each photo's credit is shown under the image in the app and listed on the photo credits page.")]
    return q


def contact(lang):
    fr = lang == "fr"
    title = "Contact et assistance — Fort et Château" if fr else "Contact and support — Fort et Château"
    desc = ("Contactez l'équipe de Fort et Château et consultez les questions fréquentes : compte, hors ligne, position, langues, photos."
            if fr else "Contact the Fort et Château team and read the frequently asked questions: account, offline use, location, languages, photos.")
    items = faq_items(lang)
    faq = "".join(f'<details class="faq"><summary>{esc(a)}</summary><p>{esc(b)}</p></details>' for a, b in items)
    blocks = ([("Nous écrire", f'<a href="mailto:{EMAIL}">{EMAIL}</a>', "Question, bogue, idée de château à ajouter : écrivez-nous, nous répondons dès que possible."),
               ("Éditeur", "JDG inc.", "Québec, Canada")] if fr else
              [("Write to us", f'<a href="mailto:{EMAIL}">{EMAIL}</a>', "Question, bug, a castle you'd like to see added: write to us and we'll reply as soon as we can."),
               ("Publisher", "JDG inc.", "Quebec, Canada")])
    cb = "".join(f'<div class="contact-block"><h3>{a}</h3><p class="value">{b}</p><p>{c}</p></div>' for a, b, c in blocks)
    ld = {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": a, "acceptedAnswer": {"@type": "Answer", "text": b}} for a, b in items]}
    body = (f'<section class="page-head"><div class="container"><p class="eyebrow">{LABEL[lang]["contact"]}</p><h1>{"Une question ?" if fr else "A question?"}</h1></div></section>'
            f'<section><div class="container"><div class="contact-grid">{cb}</div></div></section>'
            f'<section class="section--alt"><div class="container doc"><div class="section-head"><h2>{"Questions fréquentes" if fr else "Frequently asked questions"}</h2></div>{faq}</div></section>')
    return page(lang, "contact", title, desc, body, jsonld=ld)


def privacy(lang):
    fr = lang == "fr"
    title = "Politique de confidentialité — Fort et Château" if fr else "Privacy policy — Fort et Château"
    desc = ("Fort et Château ne collecte aucune donnée personnelle : pas de compte, pas de serveur, pas de publicité ni d'outil d'analyse tiers."
            if fr else "Fort et Château collects no personal data: no account, no server, no ads and no third-party analytics.")
    if fr:
        doc = f"""<h2>Résumé</h2>
<p>Fort et Château ne collecte, ne transmet ni ne vend aucune donnée personnelle. L'application n'a pas de compte utilisateur, pas de serveur, et n'intègre aucun outil d'analyse, de mesure d'audience ou de publicité tiers. Tout le contenu (fiches, photos, récits du Barde) est intégré à l'application ; toutes les données que vous générez restent sur votre appareil.</p>
<h2>Localisation</h2>
<p>Avec votre autorisation, l'application utilise la position de votre appareil pour afficher la distance jusqu'aux sites et les sites à proximité, et pour savoir si vous êtes physiquement près d'un site (moins de 300 m) afin d'activer « Valider ma visite ». Cette position est traitée entièrement sur votre appareil, n'est jamais transmise à un serveur et n'est pas conservée au-delà de la session. Vous pouvez la refuser ou la révoquer à tout moment dans les Réglages iOS : le reste de l'application continue de fonctionner.</p>
<h2>Données enregistrées sur votre appareil</h2>
<ul><li>Les sites que vous avez conquis (Passeport) et votre liste de souhaits.</li><li>Votre classement du Duel de châteaux.</li><li>Vos notes de Carnet de croquis et les photos que vous y ajoutez depuis votre photothèque.</li></ul>
<p>Ces données sont stockées localement dans l'espace de l'application et ne sont jamais envoyées vers un serveur ni partagées avec nous. Si vous utilisez une fonction de partage (carte « Explorateur Confirmé », « Mon Top 3 »), seule l'image générée que vous choisissez d'envoyer quitte votre appareil, par le mécanisme de partage natif d'iOS. Supprimer l'application supprime ces données.</p>
<h2>Achats</h2>
<p>Le téléchargement de l'application et, le cas échéant, l'achat intégré qui débloque tous les sites sont traités par Apple. Nous ne recevons ni vos informations de paiement ni votre identité : l'application vérifie seulement auprès de l'App Store que l'achat existe.</p>
<h2>Aucun compte, aucun suivi</h2>
<p>L'application ne requiert aucune création de compte, n'utilise aucun identifiant publicitaire et n'intègre aucun outil d'analyse, de mesure d'audience ou de publicité tiers. Ce site web n'utilise ni témoin (cookie) de suivi ni outil de mesure d'audience ; il charge ses polices depuis Google Fonts.</p>
<h2>Enfants</h2>
<p>L'application ne collecte aucune donnée, y compris auprès des enfants.</p>
<h2>Modifications</h2>
<p>Si cette politique change, la date ci-dessous sera mise à jour. Dernière mise à jour : {UPDATED['fr']}.</p>
<h2>Contact</h2>
<p>Pour toute question : <a href="mailto:{EMAIL}">{EMAIL}</a> — JDG inc., Québec, Canada.</p>"""
    else:
        doc = f"""<h2>Summary</h2>
<p>Fort et Château does not collect, transmit or sell any personal data. The app has no user account, no server, and includes no third-party analytics, audience measurement or advertising tools. All content (pages, photos, Bard's tales) is built into the app; all the data you generate stays on your device.</p>
<h2>Location</h2>
<p>With your permission, the app uses your device's location to show the distance to sites and the sites nearby, and to know whether you are physically near a site (within 300 m) in order to enable “Validate my visit”. This location is processed entirely on your device, is never sent to a server and is not kept beyond the current session. You can decline it or revoke it at any time in iOS Settings: the rest of the app keeps working.</p>
<h2>Data stored on your device</h2>
<ul><li>The sites you have conquered (Passport) and your wish list.</li><li>Your Castle Duel ranking.</li><li>Your Sketchbook notes and the photos you add to it from your photo library.</li></ul>
<p>This data is stored locally in the app's space and is never sent to a server or shared with us. If you use a sharing feature (“Confirmed Explorer” card, “My Top 3”), only the generated image you choose to send leaves your device, through iOS's native sharing mechanism. Deleting the app deletes this data.</p>
<h2>Purchases</h2>
<p>Downloading the app and, where applicable, the in-app purchase that unlocks every site are handled by Apple. We receive neither your payment details nor your identity: the app only checks with the App Store that the purchase exists.</p>
<h2>No account, no tracking</h2>
<p>The app requires no account, uses no advertising identifier and includes no third-party analytics, audience measurement or advertising tools. This website uses no tracking cookie or analytics tool; it loads its fonts from Google Fonts.</p>
<h2>Children</h2>
<p>The app collects no data, including from children.</p>
<h2>Changes</h2>
<p>If this policy changes, the date below will be updated. Last updated: {UPDATED['en']}.</p>
<h2>Contact</h2>
<p>For any question: <a href="mailto:{EMAIL}">{EMAIL}</a> — JDG inc., Quebec, Canada.</p>"""
    body = (f'<section class="page-head"><div class="container"><p class="eyebrow">{LABEL[lang]["privacy"]}</p><h1>{"Politique de confidentialité" if fr else "Privacy policy"}</h1></div></section>'
            f'<section><div class="container doc">{doc}</div></section>')
    return page(lang, "privacy", title, desc, body)


def credits(lang):
    fr = lang == "fr"
    title = "Crédits photo — Fort et Château" if fr else "Photo credits — Fort et Château"
    desc = (f"Auteurs, licences et sources des {N} photos de Fort et Château, issues de Wikimedia Commons." if fr
            else f"Authors, licenses and sources of the {N} photos in Fort et Château, from Wikimedia Commons.")
    rows = "".join(f'<tr><td>{esc(s["name"])}</td><td>{esc(ctry(s, lang))}</td><td>{esc(s["credit"]["author"])}</td><td>{esc(s["credit"]["license"])}</td><td><a href="{esc(s["credit"]["url"])}" target="_blank" rel="noopener">Wikimedia Commons</a></td></tr>'
                   for s in sorted(SITES, key=lambda s: norm(s["name"])))
    th = ("Site", "Pays", "Auteur", "Licence", "Source") if fr else ("Site", "Country", "Author", "License", "Source")
    body = (f'<section class="page-head"><div class="container"><p class="eyebrow">{LABEL[lang]["credits"]}</p><h1>{"Crédits photo" if fr else "Photo credits"}</h1>'
            f'<p class="lead">{"Toutes les photos proviennent de Wikimedia Commons, sous licence libre. Merci à leurs auteurs. Le crédit de chaque photo est aussi affiché sous l’image dans l’app." if fr else "All photos come from Wikimedia Commons under free licenses. Thanks to their authors. Each photo’s credit is also shown under the image in the app."}</p></div></section>'
            f'<section><div class="container"><div style="overflow-x:auto"><table class="credits"><thead><tr>' + "".join(f"<th>{t}</th>" for t in th) + f'</tr></thead><tbody>{rows}</tbody></table></div></div></section>')
    return page(lang, "credits", title, desc, body)


# ------------------------------------------------------------------ fichiers racine
def root_files():
    (PUB / "index.html").write_text(f"""<!DOCTYPE html>
<html lang="fr"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Fort et Château — Forts et châteaux du monde / Forts and castles of the world</title>
<meta name="description" content="Fort et Château : forts et châteaux du monde sur iPhone et iPad. / Forts and castles of the world on iPhone and iPad.">
<link rel="canonical" href="{SITE}/fr/">
<link rel="alternate" hreflang="fr" href="{SITE}/fr/"><link rel="alternate" hreflang="en" href="{SITE}/en/"><link rel="alternate" hreflang="x-default" href="{SITE}/fr/">
<meta http-equiv="refresh" content="1;url=fr/index.html">
<script>var l=(navigator.language||'fr').slice(0,2);location.replace((l==='en'?'en':'fr')+'/index.html');</script>
<link rel="icon" type="image/png" href="assets/favicon-48.png"><meta name="theme-color" content="#14100D">
<style>body{{background:#14100D;color:#F5F2E8;font-family:Georgia,serif;text-align:center;padding:80px 20px}}a{{color:#E8CD78}}</style></head>
<body><p><a href="fr/index.html">Français</a> · <a href="en/index.html">English</a></p></body></html>
""")
    (PUB / "404.html").write_text("""<!DOCTYPE html>
<html lang="fr"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1"><meta name="robots" content="noindex">
<title>404 — Fort et Château</title><link rel="stylesheet" href="/assets/css/style.css"></head>
<body><main><section><div class="container" style="text-align:center;padding:80px 0"><p class="eyebrow">404</p>
<h1>Page introuvable / Page not found</h1>
<p class="lead" style="margin:0 auto 28px"><a href="/fr/index.html">Retour à l'accueil</a> · <a href="/en/index.html">Back to home</a></p></div></section></main></body></html>
""")
    urls = ""
    for key in FOOT_ORDER:
        for lang in ("fr", "en"):
            pr = "1.0" if key == "home" else ("0.9" if key in ("features", "catalog", "download") else "0.5")
            urls += (f'  <url>\n    <loc>{SITE}/{lang}/{FILES[key][lang]}</loc>\n'
                     f'    <xhtml:link rel="alternate" hreflang="fr" href="{SITE}/fr/{FILES[key]["fr"]}"/>\n'
                     f'    <xhtml:link rel="alternate" hreflang="en" href="{SITE}/en/{FILES[key]["en"]}"/>\n'
                     f'    <xhtml:link rel="alternate" hreflang="x-default" href="{SITE}/fr/{FILES[key]["fr"]}"/>\n'
                     f'    <lastmod>{TODAY}</lastmod>\n    <changefreq>monthly</changefreq>\n    <priority>{pr}</priority>\n  </url>\n')
    (PUB / "sitemap.xml").write_text(f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"\n        xmlns:xhtml="http://www.w3.org/1999/xhtml">\n{urls}</urlset>\n')
    (PUB / "robots.txt").write_text(f"User-agent: *\nAllow: /\n\nSitemap: {SITE}/sitemap.xml\n")
    (PUB / "_headers").write_text("/*\n  X-Content-Type-Options: nosniff\n  Referrer-Policy: strict-origin-when-cross-origin\n\n/assets/*\n  Cache-Control: public, max-age=3600\n")
    (PUB / "8037ed04e2a33a44c0c6bf1523c7e159.txt").write_text("8037ed04e2a33a44c0c6bf1523c7e159")
    (PUB / "googlece2393743df5c567.html").write_text("google-site-verification: googlece2393743df5c567.html")


def main():
    if PUB.name != "public":      # dossier d'aperçu : réutilise les images du vrai site
        PUB.mkdir(parents=True, exist_ok=True)
        link = PUB / "assets"
        if not link.exists(): link.symlink_to(ROOT / "public/assets")
    for lang in ("fr", "en"):
        (PUB / lang).mkdir(parents=True, exist_ok=True)
        for key, fn in (("home", home), ("features", features), ("catalog", catalog), ("download", download), ("contact", contact), ("privacy", privacy), ("credits", credits)):
            (PUB / lang / FILES[key][lang]).write_text(fn(lang))
    root_files()
    print(f"Site généré ({'1.3 EN LIGNE' if LIVE13 else 'avant la 1.3'}) : {N} sites, {C} pays, {B} récits du Barde, {FREE} gratuits → {PUB}")


if __name__ == "__main__":
    main()
