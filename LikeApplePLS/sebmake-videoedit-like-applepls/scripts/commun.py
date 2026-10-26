#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""commun.py : outils partagés par assemble.py, export_xml.py, export_edl.py et filmcraft_build.py.

Python 3.9, bibliothèque standard seulement. Rien ici ne touche à un logiciel de montage.
"""
import json
import os
import subprocess
from fractions import Fraction

TICKS_PAR_S = 254016000000  # unité de temps de Premiere Pro et de FilmCraft

# cadences NTSC : la valeur affichée et la vraie fraction
NTSC = {23.976: Fraction(24000, 1001), 23.98: Fraction(24000, 1001), 29.97: Fraction(30000, 1001),
        59.94: Fraction(60000, 1001), 47.952: Fraction(48000, 1001), 119.88: Fraction(120000, 1001)}


def fps_fraction(v):
    """23.976 → 24000/1001 ; 25 → 25 ; « 30000/1001 » → 30000/1001."""
    if isinstance(v, Fraction):
        return v
    if isinstance(v, str):
        if "/" in v:
            a, b = v.split("/")
            return Fraction(int(a), int(b))
        v = float(v)
    for k, f in NTSC.items():
        if abs(float(v) - k) < 0.006:
            return f
    return Fraction(v).limit_denominator(1001)


def fps_affiche(f):
    """Nombre lisible pour le JSON : 23.976, 25, 29.97."""
    f = fps_fraction(f)
    if f.denominator == 1:
        return int(f)
    return round(float(f), 3)


def timebase(f):
    """(timebase entière, ntsc) au sens du XML FCP7 et de l'EDL : 24000/1001 → (24, True)."""
    f = fps_fraction(f)
    if f.denominator == 1001:
        return int(round(f.numerator / 1000)), True
    return int(round(float(f))), False


def s2i(sec, fps):
    """Secondes → images (arrondi à l'image la plus proche)."""
    return int(round(float(sec) * float(fps_fraction(fps))))


def i2s(n, fps):
    return float(Fraction(int(n)) / fps_fraction(fps))


def i2ticks(n, fps):
    return int(Fraction(int(n)) / fps_fraction(fps) * TICKS_PAR_S)


def tc(n, fps, debut=0):
    """Images → timecode non drop-frame HH:MM:SS:FF (images comptées à la cadence entière). Jamais négatif."""
    base, _ = timebase(fps)
    n = int(n) + int(debut)
    if n < 0:
        raise ValueError("timecode négatif (%d images) : une entrée sort de son rush" % n)
    ff = n % base
    s = n // base
    return "%02d:%02d:%02d:%02d" % (s // 3600, (s // 60) % 60, s % 60, ff)


def tc_vers_images(chaine, fps):
    base, _ = timebase(fps)
    h, m, s, f = [int(x) for x in chaine.replace(";", ":").split(":")]
    return ((h * 60 + m) * 60 + s) * base + f


_TC_FICHIERS = {}


def tc_fichier(chemin, fps=None):
    """Timecode inscrit dans le fichier (caméras), « HH:MM:SS:FF », sinon 00:00:00:00 (ffprobe)."""
    if chemin in _TC_FICHIERS:
        return _TC_FICHIERS[chemin]
    res = "00:00:00:00"
    try:
        r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format_tags=timecode:stream_tags=timecode",
                            "-of", "default=nw=1:nk=1", chemin], capture_output=True, text=True, timeout=30)
        for ligne in r.stdout.split():
            if ligne.count(":") + ligne.count(";") == 3:
                res = ligne.replace(";", ":")
                break
    except (OSError, subprocess.TimeoutExpired):
        pass
    _TC_FICHIERS[chemin] = res
    return res


def chemin_absolu(chemin, base):
    if not chemin:
        return chemin
    chemin = os.path.expanduser(chemin)
    if os.path.isabs(chemin):
        return os.path.normpath(chemin)
    return os.path.normpath(os.path.join(base, chemin))


def lire_json(chemin):
    with open(chemin, encoding="utf-8") as f:
        return json.load(f)


def ecrire_json(chemin, donnees):
    os.makedirs(os.path.dirname(os.path.abspath(chemin)), exist_ok=True)
    with open(chemin, "w", encoding="utf-8") as f:
        json.dump(donnees, f, ensure_ascii=False, indent=1)
        f.write("\n")


EXT_IMAGES = {".png", ".jpg", ".jpeg", ".tif", ".tiff", ".bmp", ".webp", ".heic", ".psd"}
EXT_AUDIO = {".wav", ".aif", ".aiff", ".mp3", ".m4a", ".aac", ".flac", ".ogg"}


def sonder(chemin):
    """ffprobe : durée, cadence, taille, présence de son et d'image. Une image fixe a une durée None."""
    ext = os.path.splitext(chemin)[1].lower()
    info = {"duree_s": None, "fps": None, "largeur": None, "hauteur": None, "video": False, "audio": False,
            "canaux": 0, "fixe": ext in EXT_IMAGES}
    if not os.path.exists(chemin):
        info["absent"] = True
        return info
    try:
        r = subprocess.run(["ffprobe", "-v", "error", "-show_entries",
                            "format=duration:stream=codec_type,r_frame_rate,avg_frame_rate,width,height,channels,duration",
                            "-of", "json", chemin], capture_output=True, text=True, timeout=60)
        d = json.loads(r.stdout or "{}")
    except (OSError, ValueError, subprocess.TimeoutExpired):
        return info
    try:
        info["duree_s"] = float(d.get("format", {}).get("duration"))
    except (TypeError, ValueError):
        pass
    for s in d.get("streams", []):
        if s.get("codec_type") == "video":
            info["video"] = True
            info["largeur"], info["hauteur"] = s.get("width"), s.get("height")
            taux = s.get("r_frame_rate") or s.get("avg_frame_rate")
            if taux and taux != "0/0":
                a, b = taux.split("/")
                if int(b):
                    info["fps"] = Fraction(int(a), int(b))
        elif s.get("codec_type") == "audio":
            info["audio"] = True
            info["canaux"] = int(s.get("channels") or 0)
    if info["fixe"]:
        info["duree_s"] = None
        info["fps"] = None
    return info


def charger_montage(chemin):
    """Lit montage.json, vérifie qu'il se tient (plans contigus, sorties = entrées + durées).

    Un fichier absent ou un JSON cassé (une retouche à la main) devient une faute d'une ligne, pas une trace."""
    nom = os.path.basename(chemin)
    try:
        m = lire_json(chemin)
    except OSError as ex:
        return None, ["%s illisible : %s" % (nom, ex.strerror or ex)]
    except ValueError as ex:  # json.JSONDecodeError : le message donne la ligne et la colonne
        return None, ["%s illisible : %s" % (nom, ex)]
    if not isinstance(m, dict) or not isinstance(m.get("plans"), list) or not isinstance(m.get("format"), dict) \
            or not m["format"].get("fps"):
        return None, ["%s : pas un montage (« plans », « format » et « format.fps » attendus, montage-spec.md § 2)" % nom]
    try:
        fautes = verifier_montage(m)
    except (TypeError, AttributeError, ValueError) as ex:
        return None, ["%s : un champ n'a pas le type attendu (montage-spec.md § 2) : %s" % (nom, ex)]
    return m, fautes


def verifier_sources(m):
    """Plans et paroles qui sortent de leur fichier source (durée lue par ffprobe quand le fichier existe).

    Renvoie (fautes, absents) : un plan qui pointe au-delà de la fin du rush est une faute ; un fichier
    introuvable n'est qu'un avertissement (il sera hors ligne à l'import)."""
    fps = float(fps_fraction(m["format"]["fps"]))
    fautes, absents, vus = [], [], {}

    def info_de(ch):
        if ch not in vus:
            vus[ch] = sonder(ch)
        return vus[ch]

    def dispo_de(ch):
        """Images disponibles dans le fichier, ou None (image fixe, durée inconnue, fichier absent)."""
        info = info_de(ch)
        if info.get("absent") or info.get("fixe") or not info.get("duree_s"):
            return None
        return int(round(info["duree_s"] * fps))

    elements = [("plan", p) for p in m.get("plans", []) if p.get("type") == "image" and p.get("chemin")]
    elements += [("parole", q) for q in m.get("paroles", []) if q.get("chemin")]
    for quoi, p in elements:
        ch = p["chemin"]
        info = info_de(ch)
        if info.get("absent"):
            if ch not in absents:
                absents.append(ch)
            continue
        dispo = dispo_de(ch)
        if dispo is None:
            continue
        sortie = p.get("sortie_img", p.get("entree_img", 0) + p.get("duree_img", 0))
        if sortie > dispo:
            fautes.append("%s %s : sortie à l'image %s, au-delà de la fin du rush (%s images, %.2f s) : %s"
                          % (quoi, p.get("n"), sortie, dispo, info["duree_s"], os.path.basename(ch)))
    # un fondu entre deux images montre, de part et d'autre de la coupe, des images hors des plans :
    # les exports le centrent (d // 2 images avant la coupe, le reste après), il faut ces images dans les rushes
    P = m.get("plans", [])
    for i in range(1, len(P)):
        p, prev = P[i], P[i - 1]
        t = p.get("transition") or {}
        d = int(t.get("duree_img") or 0)
        if t.get("type") not in ("fondu", "blanc", "poussee") or d <= 0:
            continue
        if p.get("type") != "image" or prev.get("type") != "image" or not p.get("chemin") or not prev.get("chemin"):
            continue
        avant, apres = d // 2, d - d // 2
        if p.get("entree_img", 0) < avant:
            fautes.append("plan %s : fondu de %d images sans marge (%d image(s) avant l'entrée de %s, %d demandées)"
                          % (p.get("n"), d, p.get("entree_img", 0), p.get("source") or os.path.basename(p["chemin"]), avant))
        dispo = dispo_de(prev["chemin"])
        if dispo is not None and prev.get("sortie_img", 0) + apres > dispo:
            fautes.append("plan %s : fondu de %d images sans marge (%d image(s) après la sortie de %s, %d demandées)"
                          % (p.get("n"), d, max(0, dispo - prev.get("sortie_img", 0)),
                             prev.get("source") or os.path.basename(prev["chemin"]), apres))
    return fautes, absents


def verifier_montage(m):
    fautes = []
    t = 0
    for p in m.get("plans", []):
        if p.get("debut_img") != t:
            fautes.append("plan %s : début %s, attendu %s (les plans doivent se suivre sans trou)" % (p.get("n"), p.get("debut_img"), t))
        if p.get("duree_img", 0) <= 0:
            fautes.append("plan %s : durée nulle" % p.get("n"))
        if p.get("type") == "image":
            if p.get("sortie_img", 0) - p.get("entree_img", 0) != p.get("duree_img"):
                fautes.append("plan %s : sortie − entrée ≠ durée" % p.get("n"))
            if p.get("entree_img", 0) < 0:
                fautes.append("plan %s : entrée négative" % p.get("n"))
        t = p.get("debut_img", 0) + p.get("duree_img", 0)
    if m.get("plans") and t != m.get("duree_img"):
        fautes.append("durée du montage %s ≠ fin du dernier plan %s" % (m.get("duree_img"), t))
    for q in m.get("paroles", []):
        if q.get("sortie_img", 0) - q.get("entree_img", 0) != q.get("duree_img"):
            fautes.append("parole %s : sortie − entrée ≠ durée" % q.get("n"))
        if q.get("debut_img", 0) + q.get("duree_img", 0) > m.get("duree_img", 0):
            fautes.append("parole %s : dépasse la fin du montage" % q.get("n"))
    return fautes
