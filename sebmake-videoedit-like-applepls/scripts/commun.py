#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""commun.py: helpers shared by assemble.py, export_xml.py, export_edl.py and filmcraft_build.py.

Python 3.9, standard library only. Nothing here touches editing software.
"""
import json
import os
import subprocess
from fractions import Fraction

TICKS_PAR_S = 254016000000  # time unit of Premiere Pro and FilmCraft

# NTSC frame rates: the displayed value and the true fraction
NTSC = {23.976: Fraction(24000, 1001), 23.98: Fraction(24000, 1001), 29.97: Fraction(30000, 1001),
        59.94: Fraction(60000, 1001), 47.952: Fraction(48000, 1001), 119.88: Fraction(120000, 1001)}


def fps_fraction(v):
    """23.976 → 24000/1001 ; 25 → 25 ; "30000/1001" → 30000/1001."""
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
    """Readable number for the JSON: 23.976, 25, 29.97."""
    f = fps_fraction(f)
    if f.denominator == 1:
        return int(f)
    return round(float(f), 3)


def timebase(f):
    """(integer timebase, ntsc) as FCP7 XML and EDL mean it: 24000/1001 → (24, True)."""
    f = fps_fraction(f)
    if f.denominator == 1001:
        return int(round(f.numerator / 1000)), True
    return int(round(float(f))), False


def s2i(sec, fps):
    """Seconds → frames (rounded to the nearest frame)."""
    return int(round(float(sec) * float(fps_fraction(fps))))


def i2s(n, fps):
    return float(Fraction(int(n)) / fps_fraction(fps))


def i2ticks(n, fps):
    return int(Fraction(int(n)) / fps_fraction(fps) * TICKS_PAR_S)


def tc(n, fps, debut=0):
    """Frames → non-drop-frame timecode HH:MM:SS:FF (frames counted at the integer rate). Never negative."""
    base, _ = timebase(fps)
    n = int(n) + int(debut)
    if n < 0:
        raise ValueError("negative timecode (%d frames): an in point falls outside its clip" % n)
    ff = n % base
    s = n // base
    return "%02d:%02d:%02d:%02d" % (s // 3600, (s // 60) % 60, s % 60, ff)


def tc_vers_images(chaine, fps):
    base, _ = timebase(fps)
    h, m, s, f = [int(x) for x in chaine.replace(";", ":").split(":")]
    return ((h * 60 + m) * 60 + s) * base + f


_TC_FICHIERS = {}


def tc_fichier(chemin, fps=None):
    """Timecode written in the file (cameras), "HH:MM:SS:FF", else 00:00:00:00 (ffprobe)."""
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
    """ffprobe: duration, frame rate, size, whether there is sound and picture. A still image has duration None."""
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
    """Reads montage.json and checks that it holds together (contiguous shots, out = in + duration).

    A missing file or broken JSON (a hand edit) becomes a one-line error, not a traceback."""
    nom = os.path.basename(chemin)
    try:
        m = lire_json(chemin)
    except OSError as ex:
        return None, ["%s unreadable: %s" % (nom, ex.strerror or ex)]
    except ValueError as ex:  # json.JSONDecodeError: the message gives the line and column
        return None, ["%s unreadable: %s" % (nom, ex)]
    if not isinstance(m, dict) or not isinstance(m.get("plans"), list) or not isinstance(m.get("format"), dict) \
            or not m["format"].get("fps"):
        return None, ["%s: not an edit (\"plans\", \"format\" and \"format.fps\" expected, montage-spec.md § 2)" % nom]
    try:
        fautes = verifier_montage(m)
    except (TypeError, AttributeError, ValueError) as ex:
        return None, ["%s: a field does not have the expected type (montage-spec.md § 2): %s" % (nom, ex)]
    return m, fautes


def verifier_sources(m):
    """Shots and speech that run past their source file (duration read by ffprobe when the file exists).

    Returns (errors, missing): a shot that points past the end of its clip is an error; a file
    that cannot be found is only a warning (it will be offline on import)."""
    fps = float(fps_fraction(m["format"]["fps"]))
    fautes, absents, vus = [], [], {}

    def info_de(ch):
        if ch not in vus:
            vus[ch] = sonder(ch)
        return vus[ch]

    def dispo_de(ch):
        """Frames available in the file, or None (still image, unknown duration, missing file)."""
        info = info_de(ch)
        if info.get("absent") or info.get("fixe") or not info.get("duree_s"):
            return None
        return int(round(info["duree_s"] * fps))

    elements = [("shot", p) for p in m.get("plans", []) if p.get("type") == "image" and p.get("chemin")]
    elements += [("speech", q) for q in m.get("paroles", []) if q.get("chemin")]
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
            fautes.append("%s %s: out point at frame %s, past the end of the clip (%s frames, %.2f s): %s"
                          % (quoi, p.get("n"), sortie, dispo, info["duree_s"], os.path.basename(ch)))
    # a dissolve between two picture shots shows frames outside the shots on both sides of the cut:
    # the exports center it (d // 2 frames before the cut, the rest after), so the footage must have those frames
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
            fautes.append("shot %s: %d-frame dissolve without handles (%d frame(s) before the in point of %s, %d needed)"
                          % (p.get("n"), d, p.get("entree_img", 0), p.get("source") or os.path.basename(p["chemin"]), avant))
        dispo = dispo_de(prev["chemin"])
        if dispo is not None and prev.get("sortie_img", 0) + apres > dispo:
            fautes.append("shot %s: %d-frame dissolve without handles (%d frame(s) after the out point of %s, %d needed)"
                          % (p.get("n"), d, max(0, dispo - prev.get("sortie_img", 0)),
                             prev.get("source") or os.path.basename(prev["chemin"]), apres))
    return fautes, absents


def verifier_montage(m):
    fautes = []
    t = 0
    for p in m.get("plans", []):
        if p.get("debut_img") != t:
            fautes.append("shot %s: start %s, expected %s (shots must follow each other with no gap)" % (p.get("n"), p.get("debut_img"), t))
        if p.get("duree_img", 0) <= 0:
            fautes.append("shot %s: zero duration" % p.get("n"))
        if p.get("type") == "image":
            if p.get("sortie_img", 0) - p.get("entree_img", 0) != p.get("duree_img"):
                fautes.append("shot %s: out − in ≠ duration" % p.get("n"))
            if p.get("entree_img", 0) < 0:
                fautes.append("shot %s: negative in point" % p.get("n"))
        t = p.get("debut_img", 0) + p.get("duree_img", 0)
    if m.get("plans") and t != m.get("duree_img"):
        fautes.append("edit duration %s ≠ end of last shot %s" % (m.get("duree_img"), t))
    for q in m.get("paroles", []):
        if q.get("sortie_img", 0) - q.get("entree_img", 0) != q.get("duree_img"):
            fautes.append("speech %s: out − in ≠ duration" % q.get("n"))
        if q.get("debut_img", 0) + q.get("duree_img", 0) > m.get("duree_img", 0):
            fautes.append("speech %s: runs past the end of the edit" % q.get("n"))
    return fautes
