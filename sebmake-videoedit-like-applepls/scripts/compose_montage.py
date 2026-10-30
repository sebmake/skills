#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""compose_montage.py: a composed edit (plan.json) -> montage.json, ready for FilmCraft, the XML and the review.

A composed edit assembles pre-made elements. It does not pick from footage:
  chapitres   videos already composed (rendered scenes, chapters of a demo), end to end on V1;
  voix        one sentence per file, each at its time in the film (A1);
  sous-titres an SRT file, or "auto": one subtitle per sentence, taken from the voice-over text;
  musique     on A2, at its level, with a fade-out and ducking under the voice-over;
  sons        one-off sound effects (gestures, clicks), each at its time (A3).

  python3 compose_montage.py plan.json [-o montage.json]

plan.json (paths relative to its folder; times in seconds, in the film):
  {"titre": "TEST-demo", "famille": "bande_annonce", "format": {"largeur": 1920, "hauteur": 1080, "fps": 30},
   "chapitres": [{"fichier": "chapitres/1.mp4", "nom": "Opening"}, ...],
   "voix": [{"t": 3.0, "fichier": "voix/v1.mp3", "texte": "The spoken sentence."}, ...],
   "sous_titres": "auto" | "sous-titres.srt",
   "musique": {"fichier": "musique.wav", "niveau_db": -8, "attenuation_db": 12, "fondu_sortie_s": 2, "decalage_s": 0},
   "sons": [{"t": 7.0, "fichier": "clic.wav", "nom": "clic"}]}

The resulting edit follows montage-spec.md § 2: one shot per chapter (type image, hard cut), one speech item per
sentence, one marker per chapter. The fields specific to a composed edit (`sous_titres`, `sons`,
`musique.attenuation_db`) are read by filmcraft_build.py; export_xml.py and the review ignore them.
Exit codes: 0 written; 1 unreadable plan or missing file. Python 3.9, no dependencies; ffprobe.
"""
import json
import os
import subprocess
import sys


def duree(chemin):
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", chemin],
                       capture_output=True, text=True)
    try:
        return float(r.stdout.strip())
    except ValueError:
        return None


def srt_temps(s):
    h, r = divmod(int(round(s * 1000)), 3600000)
    m, r = divmod(r, 60000)
    sec, ms = divmod(r, 1000)
    return "%02d:%02d:%02d,%03d" % (h, m, sec, ms)


def main(argv):
    if not argv or argv[0] in ("-h", "--help"):
        print(__doc__)
        return 0
    src = os.path.abspath(argv[0])
    sortie = os.path.abspath(argv[argv.index("-o") + 1]) if "-o" in argv else os.path.join(os.path.dirname(src), "montage.json")
    base = os.path.dirname(src)
    ab = lambda f: f if os.path.isabs(f) else os.path.normpath(os.path.join(base, f))
    try:
        P = json.load(open(src, encoding="utf-8"))
    except (OSError, ValueError) as ex:
        print("unreadable plan: %s" % ex)
        return 1
    fmt = dict({"largeur": 1920, "hauteur": 1080, "fps": 30, "tc_debut": "00:00:00:00"}, **(P.get("format") or {}))
    fps = float(fmt["fps"])
    img = lambda s: int(round(s * fps))
    journal, fautes = [], []

    plans, marqueurs, t = [], [], 0
    for i, c in enumerate(P.get("chapitres", []), 1):
        ch = ab(c["fichier"])
        d = duree(ch)
        if d is None:
            fautes.append("chapter %d missing or unreadable: %s" % (i, ch))
            continue
        n_img = int(d * fps + 1e-6)          # never past the last frame of the file
        plans.append({"n": i, "type": "image", "temps": "chapitre", "debut_img": t, "duree_img": n_img,
                      "debut_s": round(t / fps, 3), "duree_s": round(n_img / fps, 3), "source": "c%02d" % i, "chemin": ch,
                      "entree_img": 0, "sortie_img": n_img, "entree_s": 0.0, "sortie_s": round(n_img / fps, 3),
                      "transition": {"type": "coupe"}, "carton": None, "son_image": bool(c.get("son_image")),
                      "notes": "pre-made chapter: %s" % c.get("nom", "")})
        marqueurs.append({"debut_img": t, "duree_img": 0, "nom": "%d · %s" % (i, c.get("nom", "chapter")), "texte": ""})
        t += n_img
    total = t
    if not plans:
        fautes.append("no chapters")

    paroles = []
    for i, v in enumerate(P.get("voix", []), 1):
        ch = ab(v["fichier"])
        d = duree(ch)
        if d is None:
            fautes.append("voice-over %d missing: %s" % (i, ch))
            continue
        a, n_img = img(float(v["t"])), int(d * fps + 1e-6)
        if a + n_img > total:
            journal.append("voice-over %d runs %.2f s past the end of the film: trimmed" % (i, (a + n_img - total) / fps))
            n_img = max(1, total - a)
        if paroles and a < paroles[-1]["debut_img"] + paroles[-1]["duree_img"]:
            journal.append("voice-over %d starts before voice-over %d ends (%.2f s overlap)" % (
                i, i - 1, (paroles[-1]["debut_img"] + paroles[-1]["duree_img"] - a) / fps))
        paroles.append({"n": i, "source": "v%02d" % i, "chemin": ch, "debut_img": a, "duree_img": n_img,
                        "entree_img": 0, "sortie_img": n_img, "texte": v.get("texte", ""), "piste": "A1"})

    sous_titres = None
    st = P.get("sous_titres")
    if st == "auto":
        blocs = [(q["debut_img"] / fps, (q["debut_img"] + q["duree_img"]) / fps, q["texte"]) for q in paroles if q["texte"]]
        if blocs:
            sous_titres = os.path.splitext(sortie)[0] + ".srt"
            with open(sous_titres, "w", encoding="utf-8") as f:
                for k, (a, b, x) in enumerate(blocs, 1):
                    f.write("%d\n%s --> %s\n%s\n\n" % (k, srt_temps(a + 0.05), srt_temps(b + 0.3), x))
            journal.append("subtitles taken from the voice-over text: %s (%d)" % (os.path.basename(sous_titres), len(blocs)))
        else:
            journal.append("subtitles \"auto\": no voice-over has text, no subtitles")
    elif st:
        sous_titres = ab(st)
        if not os.path.exists(sous_titres):
            fautes.append("subtitles missing: %s" % sous_titres)

    musique = None
    mu = P.get("musique")
    if mu:
        ch = ab(mu["fichier"])
        d = duree(ch)
        if d is None:
            fautes.append("music missing: %s" % ch)
        else:
            dec = img(float(mu.get("decalage_s", 0)))
            dispo = int(d * fps + 1e-6) - dec
            n_img = min(total, dispo)
            if dispo < total:
                journal.append("the music stops %.2f s before the end of the film: loop it with a cross dissolve "
                               "(ffmpeg -i m -i m -filter_complex acrossfade=d=3 m2.wav) or use a longer track" % ((total - dispo) / fps))
            musique = {"chemin": ch, "debut_img": 0, "entree_img": dec, "duree_img": n_img, "piste": "A2",
                       "fondu_sortie_img": img(float(mu.get("fondu_sortie_s", 2)))}
            if mu.get("niveau_db") is not None:
                musique["niveau_db"] = float(mu["niveau_db"])
            if mu.get("attenuation_db"):
                musique["attenuation_db"] = abs(float(mu["attenuation_db"]))

    sons = []
    for i, x in enumerate(P.get("sons", []), 1):
        ch = ab(x["fichier"])
        d = duree(ch)
        if d is None:
            fautes.append("sound %d missing: %s" % (i, ch))
            continue
        sons.append({"n": i, "nom": x.get("nom", "sound"), "chemin": ch, "debut_img": img(float(x["t"])),
                     "entree_img": 0, "duree_img": max(1, int(d * fps + 1e-6)), "piste": "A3"})

    if fautes:
        print("incomplete plan:\n  " + "\n  ".join(fautes))
        return 1
    m = {"version": 1, "titre": P.get("titre", "edit"), "famille": P.get("famille", "bande_annonce"),
         "schema": "compose", "duree_cible_s": round(total / fps, 3), "duree_s": round(total / fps, 3), "duree_img": total,
         "format": fmt, "police": P.get("police") or {"famille": "Inter", "fichier": None},
         "couleurs": P.get("couleurs") or {"fond": "#000000", "texte": "#FFFFFF"},
         "musique": musique, "plans": plans, "paroles": paroles, "sons": sons, "sous_titres": sous_titres,
         "marqueurs": marqueurs, "controle": [], "journal": journal}
    with open(sortie, "w", encoding="utf-8") as f:
        json.dump(m, f, ensure_ascii=False, indent=1)
    print("composed edit: %s — %d chapters, %.2f s, %d voice-overs, %s, %d sounds, subtitles %s" % (
        sortie, len(plans), total / fps, len(paroles), "music" + (" ducked by %.0f dB" % musique["attenuation_db"]
                                                                     if musique and musique.get("attenuation_db") else "") if musique else "no music",
        len(sons), os.path.basename(sous_titres) if sous_titres else "none"))
    for x in journal:
        print("  " + x)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
