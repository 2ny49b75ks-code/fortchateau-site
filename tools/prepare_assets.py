#!/usr/bin/env python3
"""Prépare les images du site à partir de l'app et des captures App Store :
logos, favicon, captures (WebP), visuel d'accueil (2 téléphones), images de partage, vignettes des 156 sites, extraits audio du Barde.
Lancer une fois, ou après de nouvelles captures / de nouveaux sites :  python3 tools/prepare_assets.py   (nécessite Pillow)"""
import json, shutil
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageOps

ROOT = Path(__file__).resolve().parent.parent
IMG = ROOT / "public/assets/img"
APP = Path.home() / "FortChateau-Projet-Complet/01-Application-Xcode/FortChateau/FortChateau/Resources"
ASSETS = APP / "Assets.xcassets"
DESK = Path.home() / "Desktop/Forts et Châteaux"
SHOTS = {
    "s12": {"fr": DESK / "FortChateau-Screenshots-v1.2/iphone-6.5po", "en": DESK / "FortChateau-Screenshots-v1.2/iphone-6.5po-EN",
            "files": {"fr": dict(menu="01-menu", fiche="02-fiche-barde", globe="03-globe", duel="04-duel", rank="05-classement", badges="06-passeport-badges", carnet="07-carnet"),
                      "en": dict(menu="01-menu", fiche="02-bard-castle-page", globe="03-globe", duel="04-duel", rank="05-ranking", badges="06-passport-badges", carnet="07-sketchbook")}},
    "s13": {"fr": DESK / "FortChateau-App-Store-1.3/Captures-iPhone-6.5-FR", "en": DESK / "FortChateau-App-Store-1.3/Captures-iPhone-6.5-EN",
            "files": {"fr": dict(menu="01-menu", fiche="02-fiche-barde", barde="03-recits-du-barde", globe="04-globe", duel="05-duel", rank="06-classement", badges="07-passeport-badges", carnet="08-carnet"),
                      "en": dict(menu="01-menu", fiche="02-castle-page-bard", barde="03-bard-tales", globe="04-globe", duel="05-duel", rank="06-ranking", badges="07-passport-badges", carnet="08-sketchbook")}},
}
GOLD, GOLDB, PARCH, DARK = (212, 175, 55), (232, 205, 120), (245, 242, 232), (14, 11, 9)
PAL = ("/System/Library/Fonts/Palatino.ttc", 2)
HERO_PHOTOS = ["chateau-de-chambord", "chateau-d-himeji", "chateau-de-neuschwanstein", "alhambra", "cite-interdite", "cite-de-carcassonne"]
AUDIO = ["chateau-de-chambord-fr", "chateau-de-chambord-en", "chateau-d-himeji-fr", "chateau-d-himeji-en"]


def save_webp(im, path, w=None, q=80):
    im = im.convert("RGBA") if im.mode in ("RGBA", "LA", "P") else im.convert("RGB")
    if w and im.width > w: im = im.resize((w, round(im.height * w / im.width)), Image.LANCZOS)
    im.save(path, "WEBP", quality=q, method=6)


def fix_band(im):
    """Efface la bande claire connue au bas de l'écran du menu (défaut d'affichage des captures 1.2) en la remplaçant par le fond sombre."""
    im = im.convert("RGB"); a = np.asarray(im).astype(float).mean(axis=(1, 2)); h = im.height
    y = next((yy for yy in range(int(h * 0.9), h) if (a[yy:] > 150).mean() > 0.75), None)
    if y is None: return im
    src = np.asarray(im).astype(float)[max(0, y - 40):y - 6].mean(axis=0)   # lignes sombres juste au-dessus
    out = np.asarray(im).copy()
    for yy in range(y - 4, h):
        out[yy] = np.clip(src * 0.9, 0, 255)
    return Image.fromarray(out.astype("uint8"))


def rounded(img, r, border=None, bw=0):
    m = Image.new("L", img.size, 0); ImageDraw.Draw(m).rounded_rectangle((0, 0, img.width - 1, img.height - 1), r, fill=255)
    o = img.convert("RGBA"); o.putalpha(m)
    if border: ImageDraw.Draw(o).rounded_rectangle((0, 0, img.width - 1, img.height - 1), r, outline=border + (255,), width=bw)
    return o


def glow(lay, color, radius, k=0.6):
    pad = radius * 3; big = Image.new("RGBA", (lay.width + 2 * pad, lay.height + 2 * pad), (0, 0, 0, 0)); big.paste(lay, (pad, pad))
    a = big.getchannel("A").filter(ImageFilter.GaussianBlur(radius)).point(lambda v: min(255, int(v * k * 2)))
    g = Image.new("RGBA", big.size, color + (0,)); g.putalpha(a); return Image.alpha_composite(g, big)


def phone(shot, h, angle=0):
    sc = Image.open(shot).convert("RGB"); w = round(sc.width * h / sc.height)
    sc = sc.resize((w, h), Image.LANCZOS); bz = round(h * 0.014); r = round(h * 0.07)
    body = Image.new("RGBA", (w + 2 * bz, h + 2 * bz), (0, 0, 0, 0))
    ImageDraw.Draw(body).rounded_rectangle((0, 0, body.width - 1, body.height - 1), r + bz, fill=(8, 7, 6, 255), outline=GOLDB + (255,), width=max(3, round(h * 0.004)))
    body.alpha_composite(rounded(sc, r), (bz, bz))
    body = glow(body, GOLD, round(h * 0.02), 0.45)
    return body.rotate(angle, expand=True, resample=Image.BICUBIC) if angle else body


def bg_img(W, H, zoom=1.25, dark=0.55):
    bg = Image.open(ASSETS / "MenuBackground.imageset/MenuBackground.jpg").convert("RGB")
    sc = max(W / bg.width, H / bg.height) * zoom
    bg = bg.resize((round(bg.width * sc), round(bg.height * sc)), Image.LANCZOS)
    x, y = (bg.width - W) // 2, (bg.height - H) // 2
    a = np.asarray(bg.crop((x, y, x + W, y + H))).astype(np.float32) * dark
    yy, xx = np.mgrid[0:H, 0:W]; r = np.hypot((xx - W / 2) / (W / 2), (yy - H / 2) / (H / 2))
    a *= (1.08 - 0.5 * np.clip(r, 0, 1.3) ** 2)[..., None]
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)).convert("RGBA")


def font(spec, size): return ImageFont.truetype(spec[0], int(size), index=spec[1])


def main():
    IMG.mkdir(parents=True, exist_ok=True)
    (IMG / "t").mkdir(exist_ok=True); (IMG / "p").mkdir(exist_ok=True); (ROOT / "public/assets/audio").mkdir(exist_ok=True)
    # ---- logos et favicon
    mark = Image.open(ASSETS / "LogoMark.imageset/LogoMark.png").convert("RGB")
    mark.resize((256, 256), Image.LANCZOS).save(IMG / "logo-mark.png", optimize=True)
    mark.resize((512, 512), Image.LANCZOS).save(IMG / "logo-large.png", optimize=True)
    mark.resize((48, 48), Image.LANCZOS).save(ROOT / "public/assets/favicon-48.png")
    mark.resize((180, 180), Image.LANCZOS).save(ROOT / "public/assets/apple-touch-icon.png")
    for lang, name in (("fr", "TitleLogoFR"), ("en", "TitleLogoEN")):
        save_webp(Image.open(ASSETS / f"{name}.imageset/{name}.png"), IMG / f"title-{lang}.webp", 1000, 84)
    save_webp(Image.open(ASSETS / "BardeIcon.imageset/BardeIcon.png"), IMG / "barde.webp", 420, 88)
    # ---- captures
    for ver, cfg in SHOTS.items():
        for lang in ("fr", "en"):
            for key, fn in cfg["files"][lang].items():
                src = cfg[lang] / f"{fn}.png"
                if src.exists(): save_webp(fix_band(Image.open(src)), IMG / f"{ver}-{lang}-{key}.webp", 560, 80)
                else: print("manquant :", src)
    # ---- visuel d'accueil (2 téléphones, fond transparent)
    for lang in ("fr", "en"):
        cfg = SHOTS["s12"]; f = cfg["files"][lang]
        L = phone(cfg[lang] / f"{f['fiche']}.png", 1000, 6); R = phone(cfg[lang] / f"{f['duel']}.png", 940, -5)
        hero = Image.new("RGBA", (1180, 1120), (0, 0, 0, 0))
        hero.alpha_composite(L, (0, 80)); hero.alpha_composite(R, (hero.width - R.width, 130 - 0))
        # R passe devant L pour un effet de profondeur
        save_webp(hero, IMG / f"hero-{lang}.webp", 1000, 86)
    # ---- fond de l'en-tête (texture de carte ancienne de l'app, assombrie)
    save_webp(bg_img(1920, 1080, 1.0, 0.40).convert('RGB'), IMG / 'hero-bg.webp', None, 58)
    # ---- images de partage 1200×630
    for lang, (head, sub) in {"fr": (["À la découverte des", "forteresses du monde"], "Globe 3D · Duel · Barde · Passeport"),
                              "en": (["Discover the", "world's fortresses"], "3D Globe · Duel · Bard · Passport")}.items():
        W, H = 2400, 1260; s = H / 630
        img = bg_img(W, H, 1.4, 0.5)
        cfg = SHOTS["s12"]; f = cfg["files"][lang]
        ph = phone(cfg[lang] / f"{f['duel']}.png", 1010, -5); px = W - ph.width - 10
        ph2 = phone(cfg[lang] / f"{f['fiche']}.png", 960, 5)
        img.alpha_composite(ph2, (px - ph2.width + 150, 250)); img.alpha_composite(ph, (px, 120))
        logo = Image.open(ASSETS / f"TitleLogo{lang.upper()}.imageset/TitleLogo{lang.upper()}.png").convert("RGB")
        lw = 880; logo = logo.resize((lw, round(logo.height * lw / logo.width)), Image.LANCZOS)
        card = glow(rounded(logo, 36, GOLDB, 6), GOLD, 20, 0.55); img.alpha_composite(card, (120, 190))
        d = ImageDraw.Draw(img); y = 190 + logo.height + 120
        for i, line in enumerate(head):
            d.text((150, y), line, font=font(PAL, 118), fill=(PARCH if i == 0 else GOLDB) + (255,)); y += 140
        d.text((150, y + 30), sub, font=font(PAL, 54), fill=(200, 192, 170, 255))
        img.convert("RGB").resize((1200, 630), Image.LANCZOS).save(IMG / f"og-image-{lang}.png", optimize=True)
    # ---- vignettes des sites + grandes photos d'accueil
    data = json.load(open(ROOT / "data/sites.json"))
    for s in data["sites"]:
        src = ASSETS / f"Photos/{s['photo']}.imageset/{s['photo']}.jpg"
        im = Image.open(src).convert("RGB")
        save_webp(ImageOps.fit(im, (480, 320), Image.LANCZOS, centering=(0.5, 0.45)), IMG / f"t/{s['id']}.webp", None, 72)
        if s["id"] in HERO_PHOTOS:
            save_webp(ImageOps.fit(im, (960, 640), Image.LANCZOS, centering=(0.5, 0.45)), IMG / f"p/{s['id']}.webp", None, 78)
    # ---- extraits audio du Barde
    for a in AUDIO:
        shutil.copy(APP / f"Audio/{a}.mp3", ROOT / f"public/assets/audio/{a}.mp3")
    print("images prêtes :", len(list(IMG.rglob('*.webp'))), "WebP,", len(list((ROOT / 'public/assets/audio').glob('*.mp3'))), "audios")


if __name__ == "__main__":
    main()
