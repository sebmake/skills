#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
analyse_rushes.py : mesure les rushes (et la musique) avant de construire une timeline.
Python 3.9 + numpy + Pillow ; ffmpeg et ffprobe dans le PATH.

    python3 analyse_rushes.py RUSH_OU_DOSSIER [...] [-o rushes.json] [--planches DOSSIER]
                              [--musique FICHIER ...] [--debut S] [--fin S] [--silencieux]

Pour chaque fichier vidéo :
  - découpage en prises (même détecteur de coupes et de fondus que le corpus) ;
  - par prise : durée, mouvement (même mesure que le corpus), netteté, luminance, saturation,
    noir et blanc, caméra (fixe, lente, rapide, à la main ; tremblement), zones à éviter
    (noir, flou, tremblement, surexposition) et moments forts candidats ;
  - son de la prise s'il existe (niveau, passages actifs, attaques fortes ; voix et bruit non séparés) ;
  - une planche contact par fichier (3 vignettes par prise) pour relever à l'œil la valeur
    de plan et le sujet (champs « valeur » et « sujet » laissés à null).
Pour chaque image fixe (photo, archive : .png, .jpg, .tif…) : une seule prise, fixe, sans mesure de mouvement,
de durée libre ; « valeur » et « sujet » à remplir comme pour une vidéo.
Pour chaque fichier son (ou --musique) : tempo, temps, attaques fortes, courbe de niveau,
sommet, changements de niveau, fin (résolution ou coupure).

Tous les seuils de lecture (fixe, flou, tremblement, sombre) sont des conventions de la skill :
ils ne viennent pas du corpus, sauf « fixe » (mouvement < 10, convention de lecture du corpus).

Une sortie qui existe déjà et porte des champs remplis à l'œil (valeur, sujet, rôle, paroles, nom…) n'est jamais
écrasée : -o autre.json, ou --fusionner pour reprendre ces champs dans la nouvelle analyse (prise retrouvée = même
fichier, début et fin à ± 0,1 s ; champs de la racine repris tels quels).
Code de sortie : 0 = au moins un fichier lu ; 1 = sortie annotée existante, sans --fusionner (rien n'est écrit) ;
2 = rien de lisible.
"""
import argparse
import datetime
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import mesure_video as mv  # noqa: E402  (avant numpy : dit quoi faire s'il manque)
import numpy as np  # noqa: E402

VIDEO = {".mov", ".mp4", ".m4v", ".mxf", ".avi", ".mkv", ".mts", ".m2ts", ".webm", ".mpg", ".mpeg", ".3gp"}
AUDIO = {".wav", ".mp3", ".aif", ".aiff", ".m4a", ".flac", ".ogg", ".opus", ".aac", ".caf"}
IMAGES = {".png", ".jpg", ".jpeg", ".tif", ".tiff", ".bmp", ".webp", ".heic"}  # images fixes (photo, archive)

# Seuils de lecture des rushes : conventions de la skill (non mesurées sur le corpus)
CONV = {
    "fixe_mouvement": mv.FIXE,          # convention de lecture du corpus
    "camera_fixe_pct_s": 0.5,           # vitesse de l'image < 0,5 % de la largeur par seconde
    "camera_rapide_pct_s": 8.0,         # ≥ 8 % de la largeur par seconde
    "tremblement_main_pct": 0.12,       # écart type du tremblement ≥ 0,12 % de la largeur
    "flou_rel": 0.45,                   # netteté < 45 % du 90e centile de la prise
    "sombre_lum": 0.12,
    "surexpose_lum_p95": 0.97,
    "plan_tenu_min_s": 4.0,
    "naissance_lum_noir": 0.06,
    "naissance_montee_s": 4.0,
    "naissance_contraste": 15.0,        # ou l'écart type de la luminance (0-255) monte à 15 : un liseré de lumière dans le noir
}


def log(msg, silencieux=False):
    if not silencieux:
        sys.stderr.write(msg + "\n")
        sys.stderr.flush()


def lister(chemins):
    fichiers = []
    for c in chemins:
        if os.path.isdir(c):
            for racine, dossiers, noms in os.walk(c):
                dossiers[:] = sorted(x for x in dossiers if x != "planches_rushes" and not x.startswith("."))
                for n in sorted(noms):
                    if n.startswith("."):
                        continue
                    ext = os.path.splitext(n)[1].lower()
                    if ext in VIDEO or ext in AUDIO or ext in IMAGES:
                        fichiers.append(os.path.join(racine, n))
                    elif ext not in (".json", ".txt", ".md", ".srt", ".vtt", ".xml", ".edl", ".pdf"):
                        log("ignoré (ni vidéo, ni son, ni image) : %s" % os.path.join(racine, n))
        elif os.path.isfile(c):
            fichiers.append(c)
        else:
            log("introuvable : %s" % c)
    return fichiers


def lisse(x, k):
    if len(x) == 0 or k <= 1:
        return np.asarray(x, np.float64)
    k = min(k, len(x))
    pad = k // 2
    xp = np.concatenate([np.repeat(x[:1], pad), x, np.repeat(x[-1:], k - 1 - pad)])
    return np.convolve(xp, np.ones(k) / k, mode="valid")


def fenetres(mask, min_len):
    """Plages [a, b) où mask est vrai, d'au moins min_len éléments."""
    out, i, n = [], 0, len(mask)
    while i < n:
        if mask[i]:
            j = i
            while j < n and mask[j]:
                j += 1
            if j - i >= min_len:
                out.append((i, j))
            i = j
        else:
            i += 1
    return out


def r2(t):
    return round(float(t), 2)


def camera(S, s, e):
    """Déplacement global de l'image dans la prise, en % de la largeur."""
    dx = S["dx"][s:e].astype(np.float64)
    dy = S["dy"][s:e].astype(np.float64)
    pk = S["pk"][s:e]
    dx[pk < 0.03] = 0.0
    dy[pk < 0.03] = 0.0
    if len(dx) < 8:
        return {"etat": "trop_court"}, np.zeros(len(dx)), np.zeros(len(dx))
    tx, ty = np.cumsum(dx), np.cumsum(dy)
    k = int(mv.FPS * 0.5)
    sx, sy = lisse(tx, k), lisse(ty, k)
    jit = float(np.sqrt(((tx - sx) ** 2 + (ty - sy) ** 2).mean())) / mv.WS * 100
    vx = np.gradient(sx) * mv.FPS / mv.WS * 100
    vy = np.gradient(sy) * mv.FPS / mv.WS * 100
    vit = np.hypot(vx, vy)
    v_med = float(np.median(vit))
    if v_med < CONV["camera_fixe_pct_s"] and jit < CONV["tremblement_main_pct"]:
        etat = "fixe"
    elif jit >= CONV["tremblement_main_pct"] and v_med < CONV["camera_rapide_pct_s"]:
        etat = "a_la_main"
    elif v_med >= CONV["camera_rapide_pct_s"]:
        etat = "rapide"
    else:
        etat = "lente"
    mx, my = float(np.mean(vx)), float(np.mean(vy))
    sens = None
    if max(abs(mx), abs(my)) >= CONV["camera_fixe_pct_s"]:
        if abs(mx) >= abs(my):
            sens = "l'image glisse vers la gauche (caméra vers la droite)" if mx < 0 else "l'image glisse vers la droite (caméra vers la gauche)"
        else:
            sens = "l'image monte (caméra vers le bas)" if my < 0 else "l'image descend (caméra vers le haut)"
    res = (tx - sx) ** 2 + (ty - sy) ** 2
    return {"etat": etat, "vitesse_pct_s": round(v_med, 2), "tremblement_pct": round(jit, 3), "sens": sens}, vit, np.sqrt(res) / mv.WS * 100


def moments_prise(S, s, e, net_ref, vit, trem, t_off):
    """Moments forts candidats dans une prise (indices d'images s..e)."""
    F = mv.FPS
    out, eviter = [], []
    lum = S["lum"][s:e] / 255.0
    m1 = S["m1"][s:e]
    net = S["net"][s:e]
    n = e - s
    if n < 4:
        return out, eviter
    black = lum <= 0.04
    # zones à éviter
    p90 = float(np.percentile(net, 90)) if n else 0.0
    flou = (net < CONV["flou_rel"] * p90) & ~black
    for a, b in fenetres(lisse(flou.astype(float), 5) > 0.5, int(F * 0.5)):
        eviter.append({"debut": r2(t_off + a / F), "fin": r2(t_off + b / F), "raison": "flou (netteté relative basse)"})
    for a, b in fenetres(black, int(F * 0.3)):
        if not (a == 0 and b == n):
            eviter.append({"debut": r2(t_off + a / F), "fin": r2(t_off + b / F), "raison": "noir"})
    if len(trem):
        tl = lisse(trem, int(F * 0.5))
        for a, b in fenetres(tl > 2.5 * CONV["tremblement_main_pct"], int(F * 0.5)):
            eviter.append({"debut": r2(t_off + a / F), "fin": r2(t_off + b / F), "raison": "tremblement fort"})
    sur = lum > CONV["surexpose_lum_p95"]
    for a, b in fenetres(sur, int(F * 0.5)):
        eviter.append({"debut": r2(t_off + a / F), "fin": r2(t_off + b / F), "raison": "image brûlée (presque blanche)"})
    # 1. naissance de la lumière : voir naissances_fichier() (sur tout le fichier : elle peut chevaucher deux prises)
    # 2. plan tenu : la plus longue plage nette et stable, hors noir
    ok = ~black & ~flou
    if len(trem):
        ok &= lisse(trem, int(F * 0.5)) < 2.0 * CONV["tremblement_main_pct"]
    w = fenetres(ok, int(F * CONV["plan_tenu_min_s"]))
    for a, b in sorted(w, key=lambda z: -(z[1] - z[0]))[:2]:
        out.append({"type": "plan_tenu", "debut": r2(t_off + a / F), "fin": r2(t_off + b / F),
                    "score": r2((b - a) / F),
                    "usage": "plan tenu de 5 à 9 s : révélation, dernier plan, atterrissage, entretien"})
    # 3. pics de mouvement (geste, action)
    k = int(F)
    if n > k + 2:
        mot = np.convolve(m1, np.ones(k), mode="valid")
        mot[black[:len(mot)]] = 0
        pris = []
        for idx in np.argsort(-mot):
            if mot[idx] < 60:
                break
            if all(abs(idx - p) > 2 * F for p in pris):
                pris.append(int(idx))
            if len(pris) >= 3:
                break
        for p in pris:
            out.append({"type": "pic_mouvement", "debut": r2(t_off + p / F), "fin": r2(t_off + (p + k) / F),
                        "score": round(float(mot[p]), 1),
                        "usage": "geste ou action : montée, pic, raccord sur le mouvement (couper pendant le geste)"})
    # 4. mouvement de caméra continu (raccord sur le mouvement possible)
    if len(vit):
        cont = (lisse(vit, int(F * 0.5)) >= CONV["camera_fixe_pct_s"] * 2) & ~black
        for a, b in sorted(fenetres(cont, int(F * 2.0)), key=lambda z: -(z[1] - z[0]))[:2]:
            out.append({"type": "mouvement_continu", "debut": r2(t_off + a / F), "fin": r2(t_off + b / F),
                        "score": round(float(np.median(vit[a:b])), 2),
                        "usage": "mouvement de caméra régulier : lier deux plans par le mouvement"})
    # 5. changement de lumière sans coupe (lumière qui s'allume ou s'éteint)
    if n > F:
        L = lisse(lum, 5)
        dl = L[int(F):] - L[:-int(F)]
        for idx in np.argsort(-np.abs(dl))[:1]:
            if abs(dl[idx]) >= 0.15:
                out.append({"type": "changement_lumiere", "debut": r2(t_off + idx / F), "fin": r2(t_off + (idx + F) / F),
                            "score": round(float(dl[idx]), 3),
                            "usage": "la lumière change dans le plan : transition par la lumière, révélation"})
    # 6. image la plus nette (vignette, image fixe)
    cand = np.where(ok)[0]
    if len(cand):
        j = int(cand[np.argmax(net[cand])])
        out.append({"type": "image_nette", "debut": r2(t_off + j / F), "fin": r2(t_off + (j + 1) / F),
                    "score": round(float(net[j] / (net_ref or 1.0)), 2), "usage": "meilleure image fixe de la prise"})
    return out, eviter


def naissances_fichier(S, t_off):
    """Du noir vers une image en moins de 4 s, sur tout le fichier (la sortie du noir peut chevaucher deux prises)."""
    F = mv.FPS
    lum = S["lum"] / 255.0
    sd = S["sd"]
    n = len(lum)
    out = []
    i = 0
    while i < n:
        if lum[i] <= CONV["naissance_lum_noir"]:
            j = i
            lim = min(n, i + int(F * CONV["naissance_montee_s"]))
            # la lumière naît : l'image s'éclaire, ou un trait de lumière apparaît (contraste) sans éclairer l'image
            while j < lim and lum[j] < max(0.15, 3 * lum[i] + 0.05) \
                    and sd[j] < max(CONV["naissance_contraste"], 3 * sd[i] + 5):
                j += 1
            if j < lim and j - i >= 3:
                d0 = i
                # dernière image encore noire et unie (un trait de lumière garde l'image sombre : le contraste dit quand il naît)
                while d0 + 1 < j and lum[d0 + 1] <= CONV["naissance_lum_noir"] and sd[d0 + 1] <= sd[i] + 2.0:
                    d0 += 1
                out.append({"type": "naissance_lumiere", "debut": r2(t_off + d0 / F), "fin": r2(t_off + j / F),
                            "score": round(float(max(lum[j] - lum[d0], (sd[j] - sd[d0]) / 255.0)), 3),
                            "usage": "ouvrir : le noir, puis une lueur (film produit, ouverture)", "_j": j})
                i = j
                continue
        i += 1
    return out


def son_rush(path, t0, t1, info):
    if not info.get("audio"):
        return None
    x = mv.lire_audio(path, t0, t1)
    if x is None:
        return None
    db = mv.niveau_db(x, mv.SR, 0.1)
    if len(db) == 0:
        return None
    plancher = float(np.percentile(db, 10))
    actif = db > max(-55.0, plancher + 10)
    seg = []
    for a, b in fenetres(lisse(actif.astype(float), 5) > 0.5, 3):
        seg.append([r2(a * 0.1), r2(b * 0.1)])
    env, rate = mv.enveloppe_attaques(x)
    att = mv.affiner_attaques(x, mv.attaques(env, rate, k=2.5))
    fortes = sorted(att, key=lambda z: -z[1])[:8]
    return {"niveau_median_db": round(float(np.median(db)), 1), "plancher_db": round(plancher, 1),
            "passages_actifs": seg[:200], "part_active": round(float(actif.mean()), 3),
            "attaques_fortes": sorted(r2(a) for a, _ in fortes),
            "lecture": "son actif = au moins 10 dB au-dessus du plancher ; voix, musique et bruit ne sont pas séparés"}


def analyser_video(path, t0, t1, dossier_planches, silencieux):
    info = mv.probe(path)
    log("vidéo : %s" % os.path.basename(path), silencieux)
    S = mv.lire_series(path, t0, t1, rushes=True,
                       journal=(None if silencieux else (lambda m: log(m, False))))
    plans = mv.segmenter(S)
    off = S["t0"]
    prises = []
    for k, p in enumerate(plans):
        s, e = p["_s"], p["_e"]
        lum = S["lum"][s:e] / 255.0
        net = S["net"][s:e]
        cam, vit, trem = camera(S, s, e)
        prise = {
            "id": "%s#%d" % (os.path.basename(path), k + 1),
            "numero": k + 1,
            "debut": r2(off + p["debut"]), "fin": r2(off + p["fin"]), "duree": r2(p["duree"]),
            "transition_entree": p["transition_entree"],
            "noir": p["noir"], "blanc": p["blanc"],
            "mouvement": p["mouvement"], "fixe": p["fixe"],
            "courbe_mouvement_par_s": [round(float(v), 0) for v in
                                       np.add.reduceat(S["m1"][s:e], np.arange(0, e - s, int(mv.FPS)))] if e - s >= 2 else [],
            "luminance": {"moyenne": round(float(lum.mean()), 3), "p5": round(float(np.percentile(lum, 5)), 3),
                          "p95": round(float(np.percentile(lum, 95)), 3)},
            "saturation": p["sat"], "noir_et_blanc": p["nb"],
            "nettete": round(float(np.median(net)), 1), "nettete_rel": None,
            "camera": cam,
            "exposition": ("sombre" if lum.mean() < CONV["sombre_lum"] else
                           "brulee" if np.percentile(lum, 95) > CONV["surexpose_lum_p95"] and lum.mean() > 0.75 else "normale"),
            "moments": [], "a_eviter": [],
            "valeur": None, "sujet": None, "note": None, "notes": None,
            "_s": s, "_e": e, "_vit": vit, "_trem": trem,
        }
        prises.append(prise)
    son = son_rush(path, t0, t1, info)
    planche = None
    if dossier_planches and prises:
        temps, leg = [], []
        for pr in prises:
            d = pr["duree"]
            for fr, nom in ((0.1, "début"), (0.5, "milieu"), (0.9, "fin")):
                temps.append(pr["debut"] + d * fr)
                leg.append("P%d %s %s\n%s mv %d %s" % (pr["numero"], nom, mv.fmt_s(pr["debut"] + d * fr),
                                                         mv.fmt_s(d), pr["mouvement"], pr["camera"].get("etat", "")))
        imgs = mv.extraire_images(path, temps, 320, int(320 / max(0.3, (info["video"]["rapport"] or 16 / 9))))
        nom = os.path.splitext(os.path.basename(path))[0]
        planche = mv.planche(imgs, leg, os.path.join(dossier_planches, nom + ".jpg"), colonnes=6)
    v = info["video"]
    return {
        "fichier": os.path.abspath(path), "nom": os.path.basename(path), "type": "video",
        "duree": r2(S["n"] / mv.FPS), "duree_fichier": info["duree"],
        "video": {"largeur": v["largeur"], "hauteur": v["hauteur"], "fps": v["fps"],
                  "format": mv.format_nom(v["rapport"]), "rapport": v["rapport"], "codec": v["codec"]},
        "audio": bool(info.get("audio")),
        "prises": prises, "son": son, "planche": planche,
    }, S


def analyser_image(path, silencieux):
    """Une image fixe : une prise, fixe, sans mouvement ni durée (le montage lui donne la sienne)."""
    log("image : %s" % os.path.basename(path), silencieux)
    info = mv.probe(path)
    v = info.get("video") or {}
    if not v.get("largeur"):
        raise RuntimeError("image illisible : %s" % path)
    prise = {"id": "%s#1" % os.path.basename(path), "numero": 1, "debut": 0.0, "fin": 0.0, "duree": None,
             "transition_entree": None, "noir": False, "blanc": False, "mouvement": 0.0, "fixe": True,
             "courbe_mouvement_par_s": [], "camera": {"etat": "image_fixe"}, "exposition": None,
             "moments": [], "a_eviter": [], "valeur": None, "sujet": None, "note": None, "notes": None}
    return {"fichier": os.path.abspath(path), "nom": os.path.basename(path), "type": "image", "duree": None,
            "duree_fichier": None,
            "video": {"largeur": v["largeur"], "hauteur": v["hauteur"], "fps": None,
                      "format": mv.format_nom(v["rapport"]), "rapport": v["rapport"], "codec": v.get("codec")},
            "audio": False, "prises": [prise], "son": None,
            "planche": os.path.abspath(path),
            "lecture": "image fixe : pas de mesure de mouvement ; la planche est l'image elle-même"}


def analyser_musique(path, t0, t1, silencieux):
    log("son : %s" % os.path.basename(path), silencieux)
    info = mv.probe(path)
    x = mv.lire_audio(path, t0, t1)
    a = mv.analyse_son(x)
    if a is None:
        return None
    if a["part_silence_numerique"] >= 0.98:
        # fichier muet : ni tempo, ni sommet, ni attaques (sinon des valeurs au hasard)
        return {"fichier": os.path.abspath(path), "nom": os.path.basename(path), "type": "musique", "duree": a["duree"],
                "duree_fichier": info["duree"], "muette": True, "lecture": "fichier muet : rien à mesurer"}
    D = a["duree"]
    temps, mesures = [], []
    if a["tempo_bpm"] and a["tempo_confiance"] >= 0.2:
        per = 60.0 / a["tempo_bpm"]
        t = a["tempo_phase"] or 0.0
        while t < D:
            temps.append(r2(t))
            t += per
        mesures = temps[::4]
    courbe = a["courbe_db_par_0_5s"]
    chg = []
    c = np.array(courbe)
    for i in range(8, len(c) - 8):
        avant, apres = float(np.mean(c[i - 8:i])), float(np.mean(c[i:i + 8]))
        if abs(apres - avant) >= 4.0 and (not chg or i * 0.5 - chg[-1]["t"] >= 4.0):
            chg.append({"t": r2(i * 0.5), "ecart_db": round(apres - avant, 1),
                        "sens": "monte" if apres > avant else "descend"})
    fin = None
    if len(c) >= 10:
        d4 = float(np.mean(c[-2:]) - np.mean(c[-10:-6]))
        fin = {"ecart_4_dernieres_s_db": round(d4, 1),
               "lecture": "fondu ou résolution" if d4 <= -10 else "fin franche (le son s'arrête net)" if d4 > -3 else "décroît"}
    return {
        "fichier": os.path.abspath(path), "nom": os.path.basename(path), "type": "musique",
        "duree": D, "duree_fichier": info["duree"],
        "tempo_bpm": a["tempo_bpm"], "tempo_confiance": a["tempo_confiance"],
        "temps": temps, "mesures_4_temps": mesures,
        "attaques_fortes": sorted(a["attaques_fortes"]),
        "niveau_median_db": a["niveau_median_db"], "debut_3s_db": a["debut_3s_db"],
        "ecart_debut_db": a["ecart_debut_db"], "sommet_10s": a["sommet_10s"],
        "changements": chg, "fin": fin, "courbe_db_par_0_5s": courbe,
        "lecture": ("tempo par autocorrélation du flux spectral ; « temps » = grille régulière tirée du tempo "
                    "(confiance < 0,2 : pas de grille) ; mesures de 4 temps = convention ; "
                    "changements = écart d'au moins 4 dB entre les 4 s d'avant et les 4 s d'après (convention)"),
    }


# champs qu'analyse_rushes.py n'écrit pas : remplis à l'œil (montage-spec.md § 1.2 et 1.3), à ne jamais perdre
CHAMPS_OEIL = ("valeur", "sujet", "role", "note", "notes", "prises", "meilleur_s", "personne", "fonction", "paroles",
               "bloc", "titre_bloc", "scene", "synchro", "direction", "son_image", "description")
CLES_ANALYSE = ("version", "outil", "date", "lecture", "fichiers", "musiques", "erreurs", "resume")
TOLERANCE_PRISE_S = 0.1


def _rempli(v):
    return v not in (None, "", [], {})


def lire_annotations(chemin):
    """Ce qui a été rempli à l'œil dans un rushes.json existant : (racine, prises), ou None si le fichier
    ne se lit pas comme du JSON. prises = [(fichier, nom, début, fin, champs, id)]."""
    try:
        with open(chemin, encoding="utf-8") as fh:
            ancien = json.load(fh)
    except ValueError:
        return None
    if isinstance(ancien, list):
        return {"rushes": ancien}, []
    if not isinstance(ancien, dict):
        return None
    racine = {k: v for k, v in ancien.items() if k not in CLES_ANALYSE and _rempli(v)}
    prises = []
    for f in ancien.get("fichiers") or []:
        if not isinstance(f, dict):
            continue
        for p in f.get("prises") or []:
            if not isinstance(p, dict):
                continue
            champs = {k: p[k] for k in CHAMPS_OEIL if _rempli(p.get(k))}
            if champs:
                prises.append((f.get("fichier"), f.get("nom"), p.get("debut"), p.get("fin"), champs, p.get("id")))
    return racine, prises


def fusionner(res, racine, prises):
    """Reprend les annotations dans la nouvelle analyse. Renvoie les prises annotées qui n'ont pas été retrouvées."""
    for k, v in racine.items():
        res[k] = v
    perdues = []
    for fichier, nom, a, b, champs, ident in prises:
        trouve = False
        for f in res["fichiers"]:
            if not (fichier and f.get("fichier") == fichier) and not (nom and f.get("nom") == nom):
                continue
            for p in f["prises"]:
                try:
                    if abs(float(p["debut"]) - float(a)) <= TOLERANCE_PRISE_S and abs(float(p["fin"]) - float(b)) <= TOLERANCE_PRISE_S:
                        p.update(champs)
                        trouve = True
                        break
                except (TypeError, ValueError):
                    continue
            if trouve:
                break
        if not trouve:
            perdues.append({"id": ident, "fichier": fichier, "debut": a, "fin": b, "champs": champs})
    if perdues:
        res["annotations_non_retrouvees"] = perdues
    return perdues


def main(argv):
    ap = argparse.ArgumentParser(description="Mesure les rushes et la musique avant le montage.")
    ap.add_argument("chemins", nargs="+", help="fichiers ou dossiers de rushes")
    ap.add_argument("-o", "--sortie", default="rushes.json")
    ap.add_argument("--planches", default=None, help="dossier des planches contact (défaut : planches_rushes/ à côté de la sortie)")
    ap.add_argument("--sans-planches", action="store_true")
    ap.add_argument("--musique", nargs="*", default=[], help="fichiers son à lire comme musique")
    ap.add_argument("--debut", type=float, default=None, help="ne lire qu'à partir de S secondes (tous les fichiers)")
    ap.add_argument("--fin", type=float, default=None, help="ne lire que jusqu'à S secondes")
    ap.add_argument("--silencieux", action="store_true")
    ap.add_argument("--fusionner", action="store_true",
                    help="la sortie existe et a été complétée à l'œil : reprendre ses annotations dans la nouvelle analyse")
    a = ap.parse_args(argv)
    sortie = os.path.abspath(a.sortie)
    annot = None
    if os.path.exists(sortie) and os.path.getsize(sortie) > 0:
        try:
            annot = lire_annotations(sortie)
        except OSError as ex:
            sys.stderr.write("%s illisible (%s) : rien n'est écrit ; -o autre.json\n" % (a.sortie, ex))
            return 1
        if annot is None:
            sys.stderr.write("%s existe et ne se lit pas comme un rushes.json : rien n'est écrit ; -o autre.json\n" % a.sortie)
            return 1
        if (annot[0] or annot[1]) and not a.fusionner:
            sys.stderr.write("%s contient des annotations (%d prises remplies à l'œil%s) : rien n'est écrit ; "
                             "-o autre.json, ou --fusionner pour les reprendre dans la nouvelle analyse\n"
                             % (a.sortie, len(annot[1]), (", et à la racine : " + ", ".join(sorted(annot[0]))) if annot[0] else ""))
            return 1
    dossier_planches = None if a.sans_planches else (a.planches or os.path.join(os.path.dirname(sortie), "planches_rushes"))
    fichiers = lister(a.chemins)
    musiques = lister(a.musique)
    res = {"version": 1, "outil": "analyse_rushes.py", "date": datetime.datetime.now().isoformat(timespec="seconds"),
           "lecture": {"base": "vidéo lue à 29,97 i/s, 288 x 162 puis 96 x 54 (même base que le corpus)",
                       "mouvement": "somme par seconde des écarts moyens de gris (0-255) entre images successives ; < 10 = fixe (convention du corpus)",
                       "nettete": "variance du laplacien sur 288 x 162, divisée par la variance de l'image (une image sombre n'est pas floue) ; nettete_rel = rapport à la prise la plus nette du même fichier",
                       "camera": "déplacement global par corrélation de phase (144 x 81), en % de la largeur ; zoom et rotation non mesurés",
                       "seuils": dict(CONV, statut="convention de la skill, sauf fixe_mouvement (convention de lecture du corpus)"),
                       "a_remplir_a_l_oeil": "valeur (detail, serre, rapproche, moyen, entier, large, abstrait...) et sujet de chaque prise, en regardant la planche"},
           "fichiers": [], "musiques": [], "erreurs": []}
    series = []
    for f in fichiers:
        ext = os.path.splitext(f)[1].lower()
        try:
            if ext in AUDIO:
                m = analyser_musique(f, a.debut, a.fin, a.silencieux)
                if m:
                    res["musiques"].append(m)
                continue
            if ext in IMAGES:
                res["fichiers"].append(analyser_image(f, a.silencieux))
                continue
            info = mv.probe(f)
            if info["video"] is None:
                m = analyser_musique(f, a.debut, a.fin, a.silencieux)
                if m:
                    res["musiques"].append(m)
                continue
            r, S = analyser_video(f, a.debut, a.fin, dossier_planches, a.silencieux)
            res["fichiers"].append(r)
            series.append((r, S))
        except Exception as ex:  # un fichier illisible n'arrête pas le lot
            res["erreurs"].append({"fichier": os.path.abspath(f), "erreur": str(ex)[:300]})
            log("  erreur : %s" % ex, a.silencieux)
    for f in musiques:
        try:
            m = analyser_musique(f, a.debut, a.fin, a.silencieux)
            if m:
                res["musiques"].append(m)
        except Exception as ex:
            res["erreurs"].append({"fichier": os.path.abspath(f), "erreur": str(ex)[:300]})
    # netteté relative dans le fichier (même scène, même caméra), moments forts
    for r, S in series:
        off = S["t0"]
        ref = [p["nettete"] for p in r["prises"] if not p["noir"]]
        net_ref = max(ref) if ref else 1.0
        nais = naissances_fichier(S, off)
        for p in r["prises"]:
            p["nettete_rel"] = round(p["nettete"] / net_ref, 3) if net_ref else None
            mo, ev = moments_prise(S, p["_s"], p["_e"], net_ref, p["_vit"], p["_trem"], off + p["_s"] / mv.FPS)
            for m in nais:
                if p["_s"] < m["_j"] <= p["_e"]:
                    mo.insert(0, {k: v for k, v in m.items() if k != "_j"})
            p["moments"], p["a_eviter"] = mo, ev
            for k in ("_s", "_e", "_vit", "_trem"):
                p.pop(k, None)
    # résumé : les meilleurs candidats du lot, par type
    resume = {"fichiers_video": sum(1 for r in res["fichiers"] if r.get("type") != "image"), "fichiers_son": len(res["musiques"]),
              "prises": sum(len(r["prises"]) for r in res["fichiers"]),
              "images_fixes": sum(1 for r in res["fichiers"] if r.get("type") == "image"),
              "duree_totale": r2(sum(r["duree"] or 0 for r in res["fichiers"])), "meilleurs": {}}
    for typ in ("naissance_lumiere", "plan_tenu", "pic_mouvement", "mouvement_continu", "changement_lumiere"):
        c = [dict(m, fichier=r["nom"], prise=p["numero"]) for r in res["fichiers"] for p in r["prises"]
             for m in p["moments"] if m["type"] == typ]
        resume["meilleurs"][typ] = sorted(c, key=lambda z: -abs(z["score"]))[:6]
    etats = {}
    for r in res["fichiers"]:
        for p in r["prises"]:
            e = p["camera"].get("etat")
            etats[e] = etats.get(e, 0) + 1
    resume["camera"] = etats
    resume["prises_fixes"] = sum(1 for r in res["fichiers"] for p in r["prises"] if p["fixe"] and not p["noir"])
    res["resume"] = resume
    if annot and a.fusionner:
        perdues = fusionner(res, annot[0], annot[1])
        log("fusion : %d prises annotées reprises, %d non retrouvées%s" % (
            len(annot[1]) - len(perdues), len(perdues),
            (" (gardées dans « annotations_non_retrouvees » : %s)" % ", ".join(str(x["id"] or x["fichier"]) for x in perdues))
            if perdues else ""), a.silencieux)
    os.makedirs(os.path.dirname(sortie), exist_ok=True)
    with open(sortie, "w", encoding="utf-8") as fh:
        json.dump(res, fh, ensure_ascii=False, indent=1)
    log("écrit : %s (%d vidéos, %d images fixes, %d prises, %d sons%s)" % (
        sortie, resume["fichiers_video"], resume["images_fixes"], resume["prises"], resume["fichiers_son"],
        (", %d erreurs" % len(res["erreurs"])) if res["erreurs"] else ""), a.silencieux)
    return 0 if (res["fichiers"] or res["musiques"]) else 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
