# Site Fort et Château

Site statique (FR + EN) de l'app Fort et Château, publié sur Netlify : https://fortchateau.netlify.app

- `public/` : le site tel que publié (généré, mais versionné pour que Netlify n'ait rien à compiler)
- `data/sites.json` : le catalogue, lu dans le code de l'app par `tools/extract_data.py`
- `tools/extract_data.py` : lit `Engine/SiteData/*.swift` de l'app → `data/sites.json` (relancer quand l'app gagne des sites)
- `tools/prepare_assets.py` : captures, logos, vignettes, images de partage, extraits du Barde → `public/assets/` (Pillow)
- `tools/build.py` : génère toutes les pages HTML (FR/EN), le sitemap, robots.txt, 404
- `tools/check_site.py` : vérifie les liens et les balises essentielles
- `netlify.toml` : indique à Netlify de publier `public/`

## Interrupteur LIVE13 (en haut de `tools/build.py`)

- `LIVE13 = False` : l'app en ligne est la 1.2 (payante, 131 sites). Le site ne dit ni « gratuit », ni « achat unique », ne montre pas les 25 nouveaux châteaux et utilise les captures 1.2.
- `LIVE13 = True` : la 1.3 est en ligne (gratuite + achat unique, 156 sites, récits du Barde regroupés).

**Le jour de la sortie de la 1.3 :** mettre `LIVE13 = True`, lancer `python3 tools/build.py`, `python3 tools/check_site.py`, puis commit + push (Netlify republie seul).
Aperçu de l'état « 1.3 » sans toucher au site : `python3 tools/build.py --live13 --out public_preview13` (dossier ignoré par git).

## Mettre à jour

Modifier `tools/build.py` (textes FR/EN, pages), lancer `python3 tools/build.py`, puis commit + push.
Pour changer la palette : variables au début de `public/assets/css/style.css`.
Après un changement de contenu important : ping IndexNow (`python3 ~/CaMordTu-Projet-Complet/03-Partenaires/source/indexnow.py fortchateau.netlify.app`).
