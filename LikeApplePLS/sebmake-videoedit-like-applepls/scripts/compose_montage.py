#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""compose_montage.py : un montage composé (plan.json) → montage.json, prêt pour FilmCraft, le XML et la critique.

Un montage composé assemble des éléments déjà faits, sans choisir dans des rushes :
  chapitres   des vidéos déjà composées (scènes rendues, chapitres d'une démonstration), bout à bout sur V1 ;
  voix        une phrase par fichier, chacune à son instant dans le film (A1) ;
  sous-titres un fichier SRT, ou « auto » : un sous-titre par phrase, tiré du texte des voix ;
  musique     sur A2, à son niveau, avec un fondu de sortie et son atténuation sous les voix ;
  sons        des sons ponctuels (gestes, clics), chacun à son instant (A3).

  python3 compose_montage.py plan.json [-o montage.json]

plan.json (chemins relatifs à son dossier ; temps en secondes, dans le film) :
  {"titre": "TEST-demo", "famille": "bande_annonce", "format": {"largeur": 1920, "hauteur": 1080, "fps": 30},
   "chapitres": [{"fichier": "chapitres/1.mp4", "nom": "Ouverture"}, ...],
   "voix": [{"t": 3.0, "fichier": "voix/v1.mp3", "texte": "La phrase dite."}, ...],
   "sous_titres": "auto" | "sous-titres.srt",
   "musique": {"fichier": "musique.wav", "niveau_db": -8, "attenuation_db": 12, "fondu_sortie_s": 2, "decalage_s": 0},
   "sons": [{"t": 7.0, "fichier": "clic.wav", "nom": "clic"}]}

Le montage obtenu suit montage-spec.md § 2 : un plan par chapitre (type image, coupe franche), une parole par
phrase, un marqueur par chapitre. Les champs propres au montage composé (`sous_titres`, `sons`,
`musique.attenuation_db`) sont lus par filmcraft_build.py ; export_xml.py et la critique les ignorent.
Codes : 0 écrit ; 1 plan illisible ou fichier introuvable. Python 3.9, sans dépendance ; ffprobe.
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
        print("plan illisible : %s" % ex)
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
            fautes.append("chapitre %d introuvable ou illisible : %s" % (i, ch))
            continue
        n_img = int(d * fps + 1e-6)          # jamais au-delà de la dernière image du fichier
        plans.append({"n": i, "type": "image", "temps": "chapitre", "debut_img": t, "duree_img": n_img,
                      "debut_s": round(t / fps, 3), "duree_s": round(n_img / fps, 3), "source": "c%02d" % i, "chemin": ch,
                      "entree_img": 0, "sortie_img": n_img, "entree_s": 0.0, "sortie_s": round(n_img / fps, 3),
                      "transition": {"type": "coupe"}, "carton": None, "son_image": bool(c.get("son_image")),
                      "notes": "chapitre déjà composé : %s" % c.get("nom", "")})
        marqueurs.append({"debut_img": t, "duree_img": 0, "nom": "%d · %s" % (i, c.get("nom", "chapitre")), "texte": ""})
        t += n_img
    total = t
    if not plans:
        fautes.append("aucun chapitre")

    paroles = []
    for i, v in enumerate(P.get("voix", []), 1):
        ch = ab(v["fichier"])
        d = duree(ch)
        if d is None:
            fautes.append("voix %d introuvable : %s" % (i, ch))
            continue
        a, n_img = img(float(v["t"])), int(d * fps + 1e-6)
        if a + n_img > total:
            journal.append("voix %d dépasse la fin du film de %.2f s : coupée" % (i, (a + n_img - total) / fps))
            n_img = max(1, total - a)
        if paroles and a < paroles[-1]["debut_img"] + paroles[-1]["duree_img"]:
            journal.append("voix %d commence avant la fin de la voix %d (chevauchement de %.2f s)" % (
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
            journal.append("sous-titres tirés du texte des voix : %s (%d)" % (os.path.basename(sous_titres), len(blocs)))
        else:
            journal.append("sous-titres « auto » : aucune voix n'a de texte, aucun sous-titre")
    elif st:
        sous_titres = ab(st)
        if not os.path.exists(sous_titres):
            fautes.append("sous-titres introuvables : %s" % sous_titres)

    musique = None
    mu = P.get("musique")
    if mu:
        ch = ab(mu["fichier"])
        d = duree(ch)
        if d is None:
            fautes.append("musique introuvable : %s" % ch)
        else:
            dec = img(float(mu.get("decalage_s", 0)))
            dispo = int(d * fps + 1e-6) - dec
            n_img = min(total, dispo)
            if dispo < total:
                journal.append("la musique s'arrête %.2f s avant la fin du film : bouclez-la avec un fondu enchaîné "
                               "(ffmpeg -i m -i m -filter_complex acrossfade=d=3 m2.wav) ou prenez-en une plus longue" % ((total - dispo) / fps))
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
            fautes.append("son %d introuvable : %s" % (i, ch))
            continue
        sons.append({"n": i, "nom": x.get("nom", "son"), "chemin": ch, "debut_img": img(float(x["t"])),
                     "entree_img": 0, "duree_img": max(1, int(d * fps + 1e-6)), "piste": "A3"})

    if fautes:
        print("plan incomplet :\n  " + "\n  ".join(fautes))
        return 1
    m = {"version": 1, "titre": P.get("titre", "montage"), "famille": P.get("famille", "bande_annonce"),
         "schema": "compose", "duree_cible_s": round(total / fps, 3), "duree_s": round(total / fps, 3), "duree_img": total,
         "format": fmt, "police": P.get("police") or {"famille": "Inter", "fichier": None},
         "couleurs": P.get("couleurs") or {"fond": "#000000", "texte": "#FFFFFF"},
         "musique": musique, "plans": plans, "paroles": paroles, "sons": sons, "sous_titres": sous_titres,
         "marqueurs": marqueurs, "controle": [], "journal": journal}
    with open(sortie, "w", encoding="utf-8") as f:
        json.dump(m, f, ensure_ascii=False, indent=1)
    print("montage composé : %s — %d chapitres, %.2f s, %d voix, %s, %d sons, sous-titres %s" % (
        sortie, len(plans), total / fps, len(paroles), "musique" + (" atténuée de %.0f dB" % musique["attenuation_db"]
                                                                     if musique and musique.get("attenuation_db") else "") if musique else "sans musique",
        len(sons), os.path.basename(sous_titres) if sous_titres else "aucun"))
    for x in journal:
        print("  " + x)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
