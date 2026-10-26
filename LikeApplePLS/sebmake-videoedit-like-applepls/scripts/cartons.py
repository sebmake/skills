#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""cartons.py : dessine un carton en PNG (texte, avec ou sans fond) à la taille de la timeline. Demande Pillow.

Utilisé par export_xml.py --cartons png. La police est celle de l'utilisateur (montage.json « police.fichier »),
sinon Inter ou DejaVu Sans (libres), puis Arial si le système l'a. La skill n'embarque aucune police et
n'emploie aucune police Apple.
"""
import glob
import os

from PIL import Image, ImageDraw, ImageFont

REPLIS = ["~/Library/Fonts/Inter*.ttf", "/Library/Fonts/Inter*.ttf", "/usr/share/fonts/**/Inter*.ttf",
          "/usr/share/fonts/**/DejaVuSans.ttf", "/System/Library/Fonts/Supplemental/Arial.ttf", "C:/Windows/Fonts/arial.ttf"]


def police(m):
    return choisir_police(m)[0]


def choisir_police(m):
    """(chemin de la police, avertissement ou None). Le fichier donné d'abord ; sinon un repli, toujours dit."""
    pol = m.get("police") or {}
    f = (pol.get("fichier") or "").strip()
    famille = (pol.get("famille") or "").strip()
    if f and os.path.exists(os.path.expanduser(f)):
        return os.path.expanduser(f), None
    repli = None
    for motif in REPLIS:
        # le romain avant l'italique (Inter-Italic… passerait sinon devant Inter-Variable…)
        trouves = sorted(glob.glob(os.path.expanduser(motif), recursive=True),
                         key=lambda x: ("italic" in os.path.basename(x).lower(), x))
        if trouves:
            repli = trouves[0]
            break
    nom = os.path.basename(repli) if repli else "police par défaut de Pillow"
    if f:
        return repli, "police %s introuvable : repli %s ; donner un police.fichier qui existe" % (f, nom)
    if famille and (not repli or famille.lower().replace(" ", "") not in os.path.basename(repli).lower().replace(" ", "")):
        return repli, "police « %s » sans fichier (police.fichier vide) : repli %s ; donner police.fichier" % (famille, nom)
    return repli, None


def dessiner(chemin, carton, m, fond=None):
    L, H = int(m["format"]["largeur"]), int(m["format"]["hauteur"])
    img = Image.new("RGBA", (L, H), (0, 0, 0, 0) if not fond else fond)
    d = ImageDraw.Draw(img)
    corps = max(8, int(round(float(carton.get("taille_pct") or 4.5) / 100.0 * H / 0.7)))  # capitales ≈ 0,7 × corps
    fp = police(m)
    f1 = ImageFont.truetype(fp, corps) if fp else ImageFont.load_default()
    f2 = ImageFont.truetype(fp, int(corps * 0.75)) if fp else f1
    couleur = (m.get("couleurs") or {}).get("texte", "#FFFFFF")
    if fond and fond.upper() in ("#FFFFFF", "WHITE") and couleur.upper() == "#FFFFFF":
        couleur = "#000000"
    place = carton.get("place", "centre")
    marge_x, marge_y = int(L * 0.08), int(H * 0.1)
    if place == "centre":
        x, y, ancre = L / 2, H / 2, "mm"
    elif place == "bas_droite":
        x, y, ancre = L - marge_x, H - marge_y, "rs"
    elif place == "haut_gauche":
        x, y, ancre = marge_x, marge_y + corps, "ls"
    else:
        x, y, ancre = marge_x, H - marge_y, "ls"
    texte = carton.get("texte") or ""
    if carton.get("deuxieme_ligne") and place != "centre":
        d.text((x, y - int(corps * 1.1)), texte, font=f1, fill=couleur, anchor=ancre)
        d.text((x, y), carton["deuxieme_ligne"], font=f2, fill=couleur, anchor=ancre)
    else:
        d.text((x, y), texte, font=f1, fill=couleur, anchor=ancre)
    img.save(chemin)
    return chemin
