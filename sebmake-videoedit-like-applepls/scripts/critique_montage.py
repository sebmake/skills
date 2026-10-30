#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
critique_montage.py: measures an edit and compares it with the keynote films of its family.
Python 3.9 + numpy + Pillow; ffmpeg and ffprobe on the PATH.

    python3 critique_montage.py MONTAGE --famille produit|ouverture|documentaire|bandeannonce
            [--sous-famille X] [--debut S --fin S] [--sous-titres F.srt|F.vtt]
            [--annotations A.json] [--son FILE] [--fps N] [--mesurer-medias]
            [--cibles FOLDER] [--sortie report.md] [--json report.json] [--planche image.jpg]

MONTAGE: a video file (render), an FCP7 XML (xmeml, exported from Premiere Pro or DaVinci Resolve)
or a CMX3600 EDL. The report says what matches, what deviates (alerts), the notes (possible
but rare), what to check by eye, and fixes with timecodes.

Measurement sources:
  - calculation: the video is split into shots (same thresholds as the corpus); fades (cross dissolves,
    to black, to white) found by calculation are CANDIDATES (in the corpus, 54 real out of 225): they stay "to check"
    until an annotation confirms them;
  - declared: transitions, text and blacks read from the XML or the EDL;
  - eye: annotations (shot sizes, text, reveal, name...) written after looking at the contact sheet;
  - subtitles: speech (upper bounds); sound: level, onsets, tempo (voice and music mixed).
Verdict: "on target" = no alert. Exit code: 0 on target, 1 deviates, 2 error.
"""
import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import mesure_video as mv  # noqa: E402  (before numpy: says what to do if it is missing)
import numpy as np  # noqa: E402
import lire_timeline as lt  # noqa: E402

ICI = os.path.dirname(os.path.abspath(__file__))
CIBLES = os.path.join(os.path.dirname(ICI), "references", "cibles")

FAMILLES = {"produit": "product and reveal", "ouverture": "opening and mood",
            "documentaire": "documentary and testimonial", "bandeannonce": "trailer and usage"}
ALIAS = {"produit_revelation": "produit", "revelation": "produit", "ouverture_ambiance": "ouverture",
         "ambiance": "ouverture", "documentaire_temoignage": "documentaire", "temoignage": "documentaire",
         "bande_annonce_usage": "bandeannonce", "bande-annonce": "bandeannonce", "bande_annonce": "bandeannonce",
         "usage": "bandeannonce", "trailer": "bandeannonce"}
SOUS = {"produit": ["revelation_objet", "logiciel", "materiaux_voix_off", "usage_gamme"],
        "ouverture": ["ouverture", "sketch", "cloture", "hommage", "transition_decor", "clip"],
        "documentaire": ["pose", "choral"],
        "bandeannonce": ["oeuvre", "catalogue_par_blocs", "catalogue_mele", "usage"]}

# shot sizes (annotations): shared vocabulary and the codes of the analyses
VALEURS = ["detail", "tres_gros", "gros", "serre", "rapproche", "moyen", "ensemble", "entier", "large", "abstrait"]
CODES = {
    "produit": {"1": "detail", "2": "serre", "3": "entier", "4": "large", "A": "abstrait", "N": "noir", "T": "texte"},
    "documentaire": {"D": "detail", "TG": "tres_gros", "G": "gros", "R": "rapproche", "M": "moyen", "L": "large"},
    "bandeannonce": {"S": "serre", "R": "rapproche", "M": "moyen", "L": "large", "T": "texte", "N": "noir", "A": "abstrait", "X": "hors"},
    "ouverture": {"S": "serre", "M": "moyen", "E": "ensemble", "L": "large", "T": "texte", "N": "noir"},
}
SERRE = {"detail", "tres_gros", "gros", "serre"}
PROCHE = SERRE | {"rapproche"}
ENTIER_LARGE = {"entier", "large", "ensemble", "moyen"}

# English labels for the stored values, in the report only (the values themselves stay as they are)
VAL_EN = {"detail": "detail", "tres_gros": "extreme close-up", "gros": "close-up", "serre": "tight",
          "rapproche": "medium close-up", "moyen": "medium", "ensemble": "group", "entier": "whole object",
          "large": "wide", "abstrait": "abstract", "texte": "text", "noir": "black", "hors": "excluded"}
KIND_EN = {"image": "picture", "noir": "black", "blanc": "white", "uni": "solid", "carton": "title card"}
TIN_EN = {"debut": "start", "coupe": "cut", "fondu_enchaine": "cross dissolve", "fondu_au_noir": "fade to black",
          "fondu_depuis_noir": "fade from black", "passage_par_le_noir": "dip to black", "volet": "wipe",
          "autre_transition": "other transition", "autre": "other"}


# ---------------------------------------------------------------- tools

def charger_cibles(famille, dossier):
    p = os.path.join(dossier, famille + ".json")
    if not os.path.exists(p):
        raise SystemExit("targets not found: %s" % p)
    return json.load(open(p, encoding="utf-8"))


def g(d, chemin, defaut=None):
    x = d
    for k in chemin.split("."):
        if isinstance(x, dict) and k in x:
            x = x[k]
        elif isinstance(x, list):
            try:
                x = x[int(k)]
            except (ValueError, IndexError):
                return defaut
        else:
            return defaut
    return x


F = mv.fmt_n


def S_(t):
    return mv.fmt_s(t)


def P_(x):
    return ("%d %%" % round(100 * x)) if x is not None else "—"


class Rapport(object):
    def __init__(self, fps, depart):
        self.c = []
        self.fps = fps
        self.depart = depart

    def tc(self, t):
        return mv.tc(t, self.fps, self.depart)

    def at(self, t):
        return "%s (%s)" % (self.tc(t), S_(t))

    def add(self, id_, titre, statut, mesure, cible, base, correctif=None, source="calcul"):
        self.c.append({"id": id_, "titre": titre, "statut": statut, "mesure": mesure, "cible": cible,
                       "base": base, "correctif": correctif, "source": source})

    def n(self, statut):
        return sum(1 for x in self.c if x["statut"] == statut)


# ---------------------------------------------------------------- reading the edit

def depuis_video(path, a):
    info = mv.probe(path)
    S = mv.lire_series(path, a.debut, a.fin, critique=True,
                       journal=None if a.silencieux else (lambda m: sys.stderr.write(m + "\n")))
    dec, ajouts = None, None
    ann = a._ann
    if ann.get("transitions"):
        dec = {str(k): v for k, v in ann["transitions"].items()}
    if ann.get("ajouts"):
        ajouts = [(float(x["t"]), x["type"]) for x in ann["ajouts"]]
    P = mv.segmenter(S, dec, ajouts)
    t0 = S["t0"]
    plans = []
    for p in P:
        kind = "noir" if p["noir"] else ("blanc" if p["blanc"] else "image")
        # a shot of at least 1 s whose first and last frames no longer have anything in common:
        # maybe a missed fade or wipe (fade detection is a lower bound)
        suspect = False
        s_, e_ = p["_s"], p["_e"]
        if kind == "image" and (e_ - s_) / mv.FPS >= 1.0:
            ia, ib = s_ + (e_ - s_) // 7, e_ - 1 - (e_ - s_) // 7
            va, vb = S["vig"][ia].astype(np.float32), S["vig"][ib].astype(np.float32)
            za, zb = (va - va.mean()) / (va.std() + 4), (vb - vb.mean()) / (vb.std() + 4)
            suspect = bool(float(np.abs(za - zb).mean()) >= 0.75) and p["transition_entree"] != "fondu_enchaine"
        plans.append(dict(debut=p["debut"], fin=p["fin"], duree=p["duree"], kind=kind,
                          tin=p["transition_entree"], tl=p["duree_transition_entree"], verif=p["verif_transition"],
                          mouvement=p["mouvement"], fixe=p["fixe"], nb=p["nb"], lum=p["lum"], sat=p["sat"],
                          letterbox=p["letterbox"], derive=p["derive"], suspect=suspect, textes=[], carton_src=None, ann={}))
    # likely title cards: middle frame of each non-black shot
    cand = [i for i, p in enumerate(plans) if p["kind"] == "image" and p["duree"] >= 0.4]
    imgs = mv.extraire_images(path, [t0 + (plans[i]["debut"] + plans[i]["fin"]) / 2 for i in cand], 480, 270, gris=True)
    for i, im in zip(cand, imgs):
        ok, det = mv.score_carton(im)
        if ok:
            plans[i]["kind"] = "carton"
            plans[i]["carton_src"] = "calcul"
            plans[i]["carton_det"] = det
    fps = (info["video"] or {}).get("fps") or 25.0
    meta = {"source": "video", "fichier": os.path.abspath(path), "fps": fps, "depart": 0.0, "t0": t0,
            "duree": S["n"] / mv.FPS, "info": info, "textes": []}
    return plans, meta


def depuis_timeline(path, a):
    t = lt.lire(path, a.fps)
    plans = []
    for p in t["plans"]:
        kind = {"image": "image", "noir": "noir", "uni": "uni", "carton": "carton"}.get(p["type"], "image")
        plans.append(dict(debut=p["debut"], fin=p["fin"], duree=p["duree"], kind=kind, tin=p["transition_entree"],
                          tl=p["duree_transition_entree"], verif=p["verif_transition"], mouvement=None, fixe=None,
                          nb=None, lum=None, sat=None, letterbox=None, derive=None, textes=list(p["textes"]),
                          carton_src="declare" if kind == "carton" else None, ann={}, nom=p["nom"],
                          fichier=p["fichier"], source_in=p["source_in"], source_out=p["source_out"]))
    hors, durees = [], {}
    if a.mesurer_medias:
        for p in plans:
            f = p.get("fichier")
            if p["kind"] != "image" or not f or not os.path.exists(f) or p.get("source_in") is None:
                continue
            # EDL: the source timecode starts at the timecode written in the file; subtract it
            e = lt.entree_dans_fichier(p, t)
            if f not in durees:
                try:
                    durees[f] = mv.probe(f).get("duree")
                except Exception:
                    durees[f] = None
            if e < 0 or (durees[f] is not None and e >= durees[f]):
                hors.append(p)
                continue
            try:
                S = mv.lire_series(f, e, e + p["duree"], critique=True)
                q = mv._mesures_plan(S, {"s": 0, "e": S["n"], "tin": "debut", "tout": "fin", "vf": None, "tl": None,
                                         "noir": False, "blanc": False})
                p.update(mouvement=q["mouvement"], fixe=q["fixe"], nb=q["nb"], lum=q["lum"], sat=q["sat"], derive=q["derive"])
            except Exception as ex:
                sys.stderr.write("media not measured (%s): %s\n" % (f, ex))
    meta = {"source": t["source"], "fichier": os.path.abspath(path), "fps": t["fps"], "depart": t["depart"], "t0": 0.0,
            "duree": t["duree"], "textes": t["textes"], "audio": t["audio"], "avertissements": t["avertissements"],
            "hors_fichier": len(hors)}
    if hors:
        sys.stderr.write("source timecode outside the file, shot(s) not measured: %s\n" % ", ".join(
            "%s at %.2f s" % (os.path.basename(p["fichier"]), p["debut"]) for p in hors))
    return plans, meta


def valider_annotations(ann):
    """Format errors in a hand-written annotations file (critique.md § 5), one per place."""
    def num(v):
        return isinstance(v, (int, float)) and not isinstance(v, bool)

    def lu(v):
        return json.dumps(v, ensure_ascii=False)[:40]

    if not isinstance(ann, dict):
        return ["expected a JSON object {...}"]
    F = []
    for k in ("revelation", "fermeture"):
        if ann.get(k) is not None and not num(ann[k]):
            F.append("%s: expected a number of seconds (decimal point), read %s" % (k, lu(ann[k])))
    for k in ("codes", "sous_famille", "schema"):
        if ann.get(k) is not None and not isinstance(ann[k], str):
            F.append("%s: expected a string, read %s" % (k, lu(ann[k])))
    nom = ann.get("nom")
    if nom is not None:
        if isinstance(nom, list):
            if len(nom) != 2 or not all(num(x) for x in nom):
                F.append("nom: expected [start, end] in seconds, read %s" % lu(nom))
        elif isinstance(nom, dict):
            if ("debut" in nom or "fin" in nom) and not (num(nom.get("debut")) and num(nom.get("fin"))):
                F.append("nom: expected \"debut\" and \"fin\" in seconds, read %s" % lu(nom))
            elif "debut" not in nom and not isinstance(nom.get("type"), str):
                F.append("nom: expected [start, end] or {\"type\": \"dit_par_orateur\"}, read %s" % lu(nom))
        else:
            F.append("nom: expected [start, end] or {\"type\": \"dit_par_orateur\"}, read %s" % lu(nom))
    plans = ann.get("plans")
    if plans is not None:
        if not isinstance(plans, dict):
            F.append("plans: expected an object {\"shot number\": {\"valeur\", \"type\"}}")
        else:
            for k, v in plans.items():
                if not isinstance(v, dict):
                    F.append("plans[%s]: expected an object {\"valeur\", \"type\"}, read %s" % (k, lu(v)))
    for cle, champs in (("plans_par_temps", ("t",)), ("textes", ("debut", "fin")), ("ajouts", ("t",))):
        L = ann.get(cle)
        if L is None:
            continue
        if not isinstance(L, list):
            F.append("%s: expected a list" % cle)
            continue
        for i, x in enumerate(L):
            if not isinstance(x, dict):
                F.append("%s[%d]: expected an object, read %s" % (cle, i, lu(x)))
                continue
            for c in champs:
                if c not in x:
                    F.append("%s[%d] has no \"%s\"" % (cle, i, c))
                elif not num(x[c]):
                    F.append("%s[%d].%s: expected a number of seconds (decimal point), read %s" % (cle, i, c, lu(x[c])))
            if x.get("mots") is not None and not num(x["mots"]):
                F.append("%s[%d].mots: expected a number, read %s" % (cle, i, lu(x["mots"])))
            if cle == "ajouts" and not isinstance(x.get("type"), str):
                F.append("ajouts[%d] has no \"type\" (fondu_enchaine, volet, fondu_au_noir...)" % i)
    tr = ann.get("transitions")
    if tr is not None:
        if not isinstance(tr, dict):
            F.append("transitions: expected an object {\"time in s\": \"T|F|C|U|B\"}")
        else:
            for k, v in tr.items():
                try:
                    float(k)
                except ValueError:
                    F.append("transitions: key \"%s\": expected a time in seconds (decimal point)" % k)
                if not isinstance(v, str):
                    F.append("transitions[%s]: expected T, F, C, U or B, read %s" % (k, lu(v)))
    return F


def appliquer_annotations(plans, ann, famille, D):
    """Annotations by eye: by shot number, by time, or as a string of codes."""
    def norm_val(v):
        if v is None:
            return None
        v = str(v).strip()
        if v.lower() in VALEURS:
            return v.lower()
        for fam in (famille, "produit", "documentaire", "bandeannonce", "ouverture"):
            if v in CODES.get(fam, {}):
                return CODES[fam][v]
        return v.lower()

    def poser(p, d):
        d = dict(d)
        if "valeur" in d:
            d["valeur"] = norm_val(d["valeur"])
            # two readings in the same shot: the picture wins, the text is part of the picture
            if d["valeur"] == "texte" and p["ann"].get("valeur") in VALEURS:
                p["ann"]["texte_integre"] = True
                p["textes"] = p.get("textes") or []
                return
            if d["valeur"] in VALEURS and p["ann"].get("valeur") == "texte":
                d["texte_integre"] = True
        if d.get("valeur") in VALEURS and p["kind"] in ("carton", "noir", "blanc"):
            p["kind"] = "image"          # the eye wins over the calculation
            p["carton_src"] = None
        if d.get("valeur") in ("noir",):
            p["kind"] = "noir"
        if d.get("valeur") == "texte" or d.get("type") in ("carton", "titre", "nom", "logo"):
            p["kind"] = "carton"
            p["carton_src"] = "oeil"
        if d.get("type") in ("image", "entretien", "personne", "illustration", "objet") and p["kind"] == "carton":
            p["kind"] = "image"
            p["carton_src"] = None
        if d.get("type") == "noir":
            p["kind"] = "noir"
        p["ann"].update(d)
    codes = ann.get("codes")
    if codes:
        toks = codes.split() if " " in codes.strip() else list(codes)
        if len(toks) != len(plans):
            sys.stderr.write("annotations: %d codes for %d shots, applied in order to the first ones\n" % (len(toks), len(plans)))
        for p, c in zip(plans, toks):
            poser(p, {"valeur": c})
    for k, d in (ann.get("plans") or {}).items():
        try:
            i = int(k) - 1
        except ValueError:
            continue
        if 0 <= i < len(plans):
            poser(plans[i], d)
    for d in ann.get("plans_par_temps") or []:
        t = float(d["t"])
        for p in plans:
            if p["debut"] <= t < p["fin"]:
                poser(p, {k: v for k, v in d.items() if k != "t"})
                break


# ---------------------------------------------------------------- measurements

def mesurer(plans, D, ann, subs, son):
    M = {"duree": D}
    for i, p in enumerate(plans):
        p["n"] = i + 1
        p["rel"] = ((p["debut"] + p["fin"]) / 2) / D if D else 0
        p["rel0"] = p["debut"] / D if D else 0
    img = [p for p in plans if p["kind"] == "image"]
    M["img"] = img
    d = [p["duree"] for p in img]
    M["n_img"] = len(img)
    M["med"], M["p10"], M["p90"] = mv.med(d), mv.pct(d, 10), mv.pct(d, 90)
    tiers = [[], [], []]
    for p in img:
        tiers[min(2, int(p["rel"] * 3))].append(p["duree"])
    M["tiers"] = [mv.med(x) for x in tiers]
    M["tiers_n"] = [len(x) for x in tiers]
    M["img_min"] = len(img) / D * 60 if D else None
    M["chg_min"] = (len(plans) - 1) / D * 60 if D else None
    M["premier"] = img[0] if img else None
    M["dernier"] = img[-1] if img else None
    M["plus_long"] = max(img, key=lambda p: p["duree"]) if img else None
    i = 0
    lead = 0.0
    while i < len(plans) and plans[i]["kind"] == "noir":
        lead += plans[i]["duree"]
        i += 1
    j = len(plans)
    trail = 0.0
    while j > i and plans[j - 1]["kind"] == "noir":
        trail += plans[j - 1]["duree"]
        j -= 1
    M["noir_ouverture"] = lead
    M["noir_fin"] = trail
    # internal black: a black with a picture shot before and after it (not the opening, not the end, not before a final title card)
    idx_img = [k for k, p in enumerate(plans) if p["kind"] == "image"]
    M["noirs_internes"] = [p for k, p in enumerate(plans) if p["kind"] == "noir" and idx_img and idx_img[0] < k < idx_img[-1]]
    M["seuil_carton"] = bool(i < len(plans) and plans[i]["kind"] == "carton" and (not img or plans[i]["debut"] < img[0]["debut"]))
    M["premiere_image_t"] = img[0]["debut"] if img else None
    tr = {}
    cand, conf = [], []
    for p in plans[1:]:
        t = p["tin"]
        if t == "fondu_enchaine" and p["verif"] == "candidat":
            cand.append(p)
            t = "fondu_enchaine_candidat"
        elif t == "fondu_enchaine":
            conf.append(p)
        tr[t] = tr.get(t, 0) + 1
    M["transitions"] = tr
    M["n_transitions"] = max(1, len(plans) - 1)
    M["fondus_candidats"] = cand
    M["fondus_enchaines"] = conf
    M["coupes_part"] = tr.get("coupe", 0) / M["n_transitions"]
    M["cartons"] = [p for p in plans if p["kind"] == "carton"]
    M["textes"] = list(ann.get("textes") or [])
    mvts = [p["mouvement"] for p in img if p["mouvement"] is not None]
    M["mouvement_mesure"] = bool(mvts)
    M["part_fixes"] = (sum(1 for x in mvts if x < mv.FIXE) / len(mvts)) if mvts else None
    nbs = [p["nb"] for p in img if p["nb"] is not None]
    M["part_nb"] = (sum(nbs) / len(nbs)) if nbs else None
    # fastest passage: 5 consecutive picture shots
    M["pic5"] = None
    if len(img) >= 5:
        best = None
        for k in range(len(img) - 4):
            w = img[k:k + 5]
            m = float(np.median([x["duree"] for x in w]))
            tot = sum(x["duree"] for x in w)
            # for an equal median, the shortest window: otherwise a long shot (the first shot) enters the peak
            if best is None or (m, tot) < (best[0], best[2]):
                best = (m, w, tot)
        m, w, _ = best
        M["pic5"] = {"mediane": m, "debut": w[0]["debut"], "fin": w[-1]["fin"], "debut_rel": w[0]["debut"] / D,
                     "milieu_rel": ((w[0]["debut"] + w[-1]["fin"]) / 2) / D, "plans": [x["n"] for x in w]}
    # fastest 10 s (the trailer definition)
    M["pic10"] = None
    if img:
        last_end = max(p["fin"] for p in img)
        fen = []
        for w0 in np.arange(0, max(0.01, last_end - 10), 0.5):
            ds = [p["duree"] for p in img if w0 <= p["debut"] < w0 + 10 and p.get("ann", {}).get("valeur") != "abstrait"]
            if len(ds) >= 5:
                fen.append((float(np.median(ds)), float(w0), len(ds)))
        best = None
        if fen:
            # lowest median; within one frame (1/29.97 s), the window with the most shots
            mmin = min(f[0] for f in fen)
            proches = [f for f in fen if f[0] <= mmin + 1.0 / mv.FPS + 1e-6]
            best = max(proches, key=lambda f: (f[2], -f[0]))
        if best:
            M["pic10"] = {"mediane": best[0], "debut": best[1], "fin": best[1] + 10, "position": (best[1] + 5) / D, "plans": best[2]}
    raf, run = [], []
    for p in img + [None]:
        if p is not None and p["duree"] < 0.8 and (not run or run[-1]["n"] == p["n"] - 1):
            run.append(p)
        else:
            if len(run) >= 3:
                raf.append(run)
            run = [p] if (p is not None and p["duree"] < 0.8) else []
    M["rafales"] = raf
    # speech
    M["parole"] = None
    if subs is not None:
        iv = mv.union([(x[0], x[1]) for x in subs])
        tot = sum(b - a for a, b in iv)
        resp = []
        for (a1, b1), (a2, b2) in zip(iv[:-1], iv[1:]):
            if a2 - b1 >= 3.0:
                resp.append((b1, a2))
        M["parole"] = {"n": len(subs), "part": tot / D if D else 0, "intervalles": iv,
                       "premiere": subs[0][0] if subs else None, "derniere_fin": subs[-1][1] if subs else None,
                       "fin_avant_bout": (D - max(x[1] for x in subs)) if subs else None,
                       "plus_longue": max(subs, key=lambda x: x[1] - x[0]) if subs else None,
                       "plus_de_mots": max(subs, key=lambda x: x[3]) if subs else None,
                       "respirations": resp}

        def parole_dans(a, b):
            return sum(max(0.0, min(b, y) - max(a, x)) for x, y in iv)
        M["parole_dans"] = parole_dans
    M["son"] = son
    M["coupes_t"] = [p["debut"] for p in plans[1:] if p["tin"] == "coupe"]
    if son and son.get("attaques"):
        M["sur_son"] = mv.coupes_sur_son(M["coupes_t"], son["attaques"], D, 0.07,
                                         son.get("tempo_bpm") if (son.get("tempo_confiance") or 0) >= 0.3 else None,
                                         son.get("tempo_phase"))
    else:
        M["sur_son"] = None
    return M


def liste_tc(R, plans, n=6):
    s = ", ".join("#%d at %s" % (p["n"], R.at(p["debut"])) for p in plans[:n])
    return s + (" (and %d more)" % (len(plans) - n) if len(plans) > n else "")


def plage(R, D, a, b):
    return "between %s and %s" % (R.at(a * D), R.at(b * D))


# ---------------------------------------------------------------- shared checks

def ctl_fondus(R, M, id_, max_n, max_part, base, permis="", sur_texte_permis=False):
    conf, cand = M["fondus_enchaines"], M["fondus_candidats"]
    if sur_texte_permis:
        idx = {p["n"]: p for p in R._plans}

        def texte(p):
            return p is not None and (p["kind"] == "carton" or bool(p.get("textes")))
        conf = [p for p in conf if not (texte(p) or texte(idx.get(p["n"] - 1)))]
        cand = [p for p in cand if not (texte(p) or texte(idx.get(p["n"] - 1)))]
    n = len(conf)
    part = n / M["n_transitions"]
    if n > max_n or (n >= 2 and part > max_part):
        R.add(id_, "Cross dissolves", "alerte", "%d cross dissolves (%s of transitions)" % (n, P_(part)),
              "at most %s, %s of transitions" % (max_n, P_(max_part)), base,
              "replace with hard cuts: %s%s" % (liste_tc(R, conf), permis),
              "declare" if any(p["verif"] == "declare" for p in conf) else "oeil")
    elif cand:
        R.add(id_, "Cross dissolves", "a_verifier", "%d candidate cross dissolves found by calculation" % len(cand),
              "at most %s" % max_n, base + "; by calculation, 54 real dissolves out of 225 candidates in the corpus",
              "look at %s; confirm (T) or reject (F) in annotations.transitions" % liste_tc(R, cand))
    else:
        R.add(id_, "Cross dissolves", "ok", "%d cross dissolve" % n if n == 1 else "%d cross dissolves" % n,
              "at most %s" % max_n, base)


def ctl_parole_absente(R, id_, titre, besoin):
    R.add(id_, titre, "non_mesure", "—", "—", "—", besoin, "—")


# ---------------------------------------------------------------- product family

def controles_produit(R, M, C, a, ann):
    D = M["duree"]
    img = M["img"]
    sf = a.sous_famille or ann.get("sous_famille") or "revelation_objet"
    schema = a.schema or ann.get("schema")
    if not schema:
        schema = "tardif" if sf in ("revelation_objet", "materiaux_voix_off") else ("des_le_debut" if sf == "usage_gamme" else None)
    R.contexte = "subfamily %s; pattern %s" % (sf, {"tardif": "late reveal", "des_le_debut": "object from the start", None: "not specified"}[schema])
    plan_seq = len(img) <= 5 and D >= 30
    voix = M["parole"] is not None and M["parole"]["part"] >= 0.2
    # C2 duration
    if voix:
        lo, hi = g(C, "corpus.duree_s.materiaux_voix_off.min", 53.57), g(C, "corpus.duree_s.materiaux_voix_off.max", 127.55)
    else:
        lo, hi = g(C, "corpus.duree_s.sans_voix_off.min", 24.09), g(C, "corpus.duree_s.sans_voix_off.max", 51.0)
    R.add("C2", "Film duration", "ok" if lo - 1 <= D <= hi + 1 else "note", S_(D),
          "%s to %s %s" % (S_(lo), S_(hi), "(voice-over)" if voix else "(no voice)"),
          "13 films without voice from 24 to 51 s; 3 voice-over films from 54 to 128 s",
          None if lo - 1 <= D <= hi + 1 else ("cut to about %s (median of the corpus without voice)" % S_(g(C, "corpus.duree_s.sans_voix_off.mediane", 31.9)) if D > hi else "the film is short: check that it has its five beats"))
    # C3 open on black
    nb_o = M["noir_ouverture"]
    if nb_o == 0:
        R.add("C3", "Open on black", "note", "the film starts on a picture", "black for 0.3 to 1.6 s, then the picture appears",
              "observed 13 out of 16 (black), 8 out of 16 (appears through light or a fade)",
              "add 0.3 to 1.6 s of black before %s, then a fade from black of 0.7 to 1.3 s" % R.at(M["premiere_image_t"] or 0))
    elif nb_o > 1.6:
        R.add("C3", "Open on black", "note", "opening black of %s" % S_(nb_o), "0.3 to 1.6 s (9 out of 13)",
              "long blacks: 4 out of 13, 3 of them from the same keynote in a hall", "shorten the opening black to about 1 s")
    else:
        R.add("C3", "Open on black", "ok", "black of %s" % S_(nb_o), "0.3 to 1.6 s", "observed 13 out of 16")
    # K1 reveal
    rev = ann.get("revelation")
    if schema == "tardif":
        if rev is not None:
            r = float(rev) / D
            lo, hi = g(C, "structure.3.position.min", 0.69), g(C, "structure.3.position.max", 0.82)
            if r < 0.60:
                R.add("K1", "Reveal position", "alerte", "whole object at %s of the duration (%s)" % (P_(r), R.at(float(rev))),
                      "%s to %s (median 77 %%)" % (P_(lo), P_(hi)), "10 films out of 10 after 69 %",
                      "push the reveal back %s: lengthen the build-up with details" % plage(R, D, lo, hi), "oeil")
            else:
                R.add("K1", "Reveal position", "ok" if lo - 0.03 <= r <= hi + 0.05 else "note", "at %s of the duration" % P_(r),
                      "%s to %s" % (P_(lo), P_(hi)), "10 films out of 10 between 69 and 82 %", None, "oeil")
        else:
            cands = [p for p in img if p["rel0"] >= 0.6]
            c = max(cands, key=lambda p: p["duree"]) if cands else None
            R.add("K1", "Reveal position", "a_verifier", "not annotated" + ("; candidate: shot #%d at %s (%s, the longest after 60 %%)" % (c["n"], R.at(c["debut"]), S_(c["duree"])) if c else ""),
                  "69 to 82 % of the duration", "10 films out of 10", "give \"revelation\" (in s) in the annotations")
    else:
        R.add("K1", "Reveal position", "sans_objet", "pattern \"object from the start\"", "whole object between 1 and 18 %", "5 films out of 16")
    # K2 first shot
    if M["premier"] is not None:
        v = M["premier"]["ann"].get("valeur")
        if schema == "tardif":
            if v is None:
                R.add("K2", "First picture shot", "a_verifier", "size not annotated (shot #%d)" % M["premier"]["n"],
                      "a world (setting, landscape) or a material; never the whole object", "0 out of 10 whole object", None)
            elif v == "entier":
                R.add("K2", "First picture shot", "alerte", "the whole object from the first shot (%s)" % R.at(M["premier"]["debut"]),
                      "a setting, a landscape or a material", "0 out of 10 with a late reveal",
                      "open on a setting or a material (a detail in raking light) and keep the whole object for the reveal", "oeil")
            else:
                R.add("K2", "First picture shot", "ok", "first shot: %s" % VAL_EN.get(v, v), "setting, landscape or material", "10 out of 10", None, "oeil")
        q1 = g(C, "durees.premier_plan_image.quartiles.0", 2.32)
        R.add("C4", "First picture shot duration", "ok" if M["premier"]["duree"] >= q1 else "note", S_(M["premier"]["duree"]),
              "median 3.3 s (quartiles 2.3 and 7.9 s)", "16 films; shorter than %s s in 1 film out of 4" % F(q1, 1),
              None if M["premier"]["duree"] >= q1 else "hold the first shot 2.5 to 4 s: it sets up the world")
    # K3 median shot
    if M["med"] is not None:
        lo, hi = g(C, "durees.mediane_par_film.films_qui_coupent.min", 1.0), g(C, "durees.mediane_par_film.films_qui_coupent.max", 3.6)
        if lo - 1.0 / mv.FPS <= M["med"] <= hi + 1.0 / mv.FPS:
            R.add("K3", "Median picture shot", "ok", "%s s" % F(M["med"]),
                  "%s to %s s" % (F(lo, 1), F(hi, 1)), "14 films that cut: 1.0 to 3.6 s")
        else:
            st = "note" if plan_seq else "alerte"
            courts = sorted([p for p in img if p["duree"] < 0.8], key=lambda p: p["debut"])
            longs = sorted([p for p in img if p["duree"] > 5], key=lambda p: p["debut"])
            cor = ("too choppy: lengthen or group the short shots (%s); aim for 2 to 2.5 s in the build-up" % liste_tc(R, courts)) if M["med"] < lo \
                else ("too slow: cut the long picture shots, except the reveal and the final shot (%s)" % liste_tc(R, longs))
            R.add("K3", "Median picture shot", st, "%s s" % F(M["med"]), "%s to %s s" % (F(lo, 1), F(hi, 1)),
                  "14 films that cut: 1.0 to 3.6 s" + ("; single take: 2 films out of 16" if plan_seq else ""), cor)
    # K4 pace
    if M["img_min"] is not None:
        lo, hi = g(C, "durees.plans_image_par_minute.films_qui_coupent.min", 13.17), g(C, "durees.plans_image_par_minute.films_qui_coupent.max", 32.42)
        tol = 60.0 / D          # one shot more or less
        ok = lo - tol <= M["img_min"] <= hi + tol
        R.add("K4", "Picture shots per minute", "ok" if ok else ("note" if plan_seq else "alerte"), F(M["img_min"], 1),
              "%s to %s" % (F(lo, 1), F(hi, 1)), "14 films that cut",
              None if ok else ("fewer shots: remove or merge %d shots" % max(1, round(M["n_img"] - hi * D / 60)) if M["img_min"] > hi
                               else "more shots: break the build-up into details of 1.2 to 3.5 s"))
    # K5 longest shot
    pl = M["plus_long"]
    if pl is not None:
        if pl["duree"] >= 5:
            R.add("K5", "One shot of at least 5 s", "ok", "shot #%d: %s" % (pl["n"], S_(pl["duree"])), "at least 5 s (median 8.1 s)", "14 out of 16")
        else:
            R.add("K5", "One shot of at least 5 s", "note", "the longest lasts %s (shot #%d at %s)" % (S_(pl["duree"]), pl["n"], R.at(pl["debut"])),
                  "at least 5 s; the longest is 8.1 s at the median", "14 films out of 16; 2 fast-cut software films have none",
                  "hold the reveal or the last shot 5 to 9 s (take it longer from the clip); candidate: shot #%d at %s" % (M["dernier"]["n"], R.at(M["dernier"]["debut"])))
    # K6 last picture shot
    der = M["dernier"]
    if der is not None:
        # only a name written after the last picture shot counts (not a name shown earlier, nor spoken by the presenter)
        nom_a = ann.get("nom")
        t_nom = (float(nom_a[0]) if isinstance(nom_a, (list, tuple)) and len(nom_a) == 2 else
                 float(nom_a["debut"]) if isinstance(nom_a, dict) and "debut" in nom_a else None)
        nom_ann = t_nom is not None and t_nom >= der["fin"] - 0.05
        if M["textes"]:
            nom_apres = nom_ann or any(x.get("type") == "nom" and float(x.get("debut", 0)) >= der["fin"] - 0.05 for x in M["textes"])
        else:
            nom_apres = nom_ann or any(p["debut"] >= der["fin"] - 0.05 for p in M["cartons"])
        if der["duree"] >= 4:
            R.add("K6", "Last picture shot held", "ok", S_(der["duree"]), "at least 4 s (median 7.4 s)", "13 out of 16")
        elif nom_apres and (M["textes"] or nom_ann):
            R.add("K6", "Last picture shot held", "ok", "%s, then the name" % S_(der["duree"]), "at least 4 s, or end on the name", "3 out of 16 end this way", None, "oeil")
        elif nom_apres:
            R.add("K6", "Last picture shot held", "a_verifier", "%s, then a title card: is it the name?" % S_(der["duree"]), "at least 4 s, or end on the name",
                  "13 out of 16 at least 4 s; the other 3 end on the name",
                  "if the title card is not the name: hold the last shot (#%d) 6 to 8.5 s; give the text types in the annotations" % der["n"])
        else:
            R.add("K6", "Last picture shot held", "alerte", "%s (shot #%d at %s)" % (S_(der["duree"]), der["n"], R.at(der["debut"])),
                  "at least 4 s (6 to 8.5 s between quartiles), or end on the name", "13 out of 16 at least 4 s; the other 3 end on the name",
                  "hold the last shot (#%d, at %s) 6 to 8.5 s instead of %s, on the whole object; or end on the name" % (der["n"], R.at(der["debut"]), S_(der["duree"])))
    # K7 cross dissolves
    ctl_fondus(R, M, "K7", 1, 0.10, "3 % of transitions; never 2 seen by eye in one film",
               "; keep at most one dissolve, to enter a key shot (the name)")
    # K8 fade from black in the last third
    fdn = [p for p in R._plans if p["tin"] == "fondu_depuis_noir" and p["rel0"] >= 2 / 3]
    R.add("K8", "Fade from black in the last third", "note" if fdn else "ok", "%d" % len(fdn), "none", "0 out of 10",
          ("a black that opens belongs to the start: hard cut at %s" % liste_tc(R, fdn)) if fdn else None)
    # K9 tighten
    vals = [p for p in img if p["rel"] < 2 / 3 and p["ann"].get("valeur") in VALEURS]
    if schema == "tardif":
        if len(vals) >= 3:
            part = sum(1 for p in vals if p["ann"]["valeur"] in PROCHE) / len(vals)
            R.add("K9", "Details and tight shots (first two thirds)", "ok" if part >= 0.5 else "note", P_(part),
                  "65 to 70 %; at least 50 %", "70 % then 65 % over 141 shots; 7 late-reveal films out of 10 above 50 %",
                  None if part >= 0.5 else "replace wide shots in the build-up with details of the object (material, parts)", "oeil")
        else:
            R.add("K9", "Details and tight shots (first two thirds)", "a_verifier", "sizes not annotated", "65 to 70 %", "observed", None)
    # K10 widen at the end
    if der is not None:
        v = der["ann"].get("valeur")
        if v is None:
            R.add("K10", "Last shot: the whole object", "a_verifier", "size not annotated (shot #%d)" % der["n"], "whole object or wide", "14 out of 16", None)
        else:
            ok = v in ENTIER_LARGE
            R.add("K10", "Last shot: the whole object", "ok" if ok else "note", VAL_EN.get(v, v), "whole object or wide", "14 out of 16; 2 end tight or abstract",
                  None if ok else "end on the whole object, held (pull back or slow turn)", "oeil")
    # K11 name
    nom = ann.get("nom")
    if isinstance(nom, dict) and nom.get("type") in ("dit_par_orateur", "orateur", "aucun_orateur_le_dit"):
        R.add("K11", "The name", "sans_objet", "spoken by the presenter after the film", "—", "8 out of 16 in the keynotes")
    else:
        if isinstance(nom, (list, tuple)) and len(nom) == 2:
            t0n, t1n, src = float(nom[0]), float(nom[1]), "oeil"
        elif isinstance(nom, dict) and "debut" in nom:
            t0n, t1n, src = float(nom["debut"]), float(nom["fin"]), "oeil"
        elif M["textes"]:
            # text noted by eye: only a text of type "nom" counts
            nt = [x for x in M["textes"] if x.get("type") == "nom"]
            if nt:
                t0n, t1n, src = float(nt[-1]["debut"]), float(nt[-1]["fin"]), "oeil"
            else:
                t0n = None
        else:
            c = [p for p in M["cartons"] if p["rel0"] >= 0.5]
            if c:
                t0n, t1n, src = c[-1]["debut"], c[-1]["fin"], c[-1]["carton_src"] or "calcul"
            else:
                t0n = None
        if t0n is None:
            R.add("C16", "Write the name (no presenter)", "note", "no written name found", "the name alone, centered, at 83-96 %, 1.3 to 4.5 s",
                  "convention (in the keynotes, the presenter says it: 8 out of 8)",
                  "add the name %s, for about 2.4 s" % plage(R, D, 0.83, 0.96))
        else:
            r, dn = t0n / D, t1n - t0n
            lo, hi = g(C, "cartons.nom.position.min", 0.83), g(C, "cartons.nom.position.max", 0.96)
            bad = r < lo - 0.02 or dn < 1.25
            st = ("alerte" if bad else "ok") if src == "oeil" else "a_verifier"
            R.add("K11", "Name position and duration", st, "at %s, %s%s" % (P_(r), S_(dn), "" if src != "calcul" else " (title card found by calculation)"),
                  "%s to %s; 1.3 to 4.5 s" % (P_(lo), P_(hi)), "7 out of 7 written names",
                  ("place the name %s and hold it for about 2.4 s" % plage(R, D, lo, hi)) if bad else
                  (None if src == "oeil" else "say in the annotations whether this last title card is the name (textes, type \"nom\")"), src)
    # K12 too much text
    types = [x.get("type") for x in M["textes"]]
    n_txt = len(M["cartons"]) + sum(1 for x in M["textes"] if x.get("type") not in ("nom",) and not x.get("sur_carton"))
    interdits = [x for x in M["textes"] if x.get("type") in ("chiffre", "explicatif", "slogan", "date")]
    phrases = [x for x in M["textes"] if x.get("type") == "phrase"]
    src = "oeil" if M["textes"] else ("declare" if any(p["carton_src"] == "declare" for p in M["cartons"]) else "calcul")
    if interdits or len(phrases) > 1:
        R.add("K12", "Too much text", "alerte", "%d forbidden text(s) (%s), %d sentence(s)" % (len(interdits), ", ".join(sorted(set(x["type"] for x in interdits))) or "—", len(phrases)),
              "no title card with figures or explanations; at most one 5-word sentence", "0 out of 16; one sentence in 1 film out of 16",
              "remove: " + ", ".join("%s at %s" % (x.get("type"), R.at(float(x.get("debut", 0)))) for x in interdits + phrases[1:]), "oeil")
    elif len(M["cartons"]) > 2:
        st = "alerte" if src in ("declare", "oeil") else "a_verifier"
        R.add("K12", "Too much text", st, "%d title cards" % len(M["cartons"]), "at most 2 texts (the name, one sentence or a lower third)",
              "no film has more than 2 texts (16 films)",
              "keep the name at the end; remove %s" % liste_tc(R, M["cartons"][:-1]), src)
    else:
        R.add("K12", "Too much text", "ok", "%d title card(s)" % len(M["cartons"]), "at most 2 texts", "16 films", None, src)
    # K13 logo, date, slogan at the end
    fin_t = [x for x in M["textes"] if x.get("type") in ("logo", "slogan", "date") and float(x.get("debut", 0)) >= 0.8 * D]
    if fin_t:
        R.add("K13", "Logo, date or slogan at the end", "alerte", ", ".join(x["type"] for x in fin_t), "end on the object, or the name then a black",
              "0 out of 16", "replace with the name alone, then a short black (0.1 to 2.8 s)", "oeil")
    elif M["cartons"] and M["cartons"][-1]["rel0"] >= 0.8 and not ann.get("nom") and not M["textes"]:
        R.add("K13", "Logo, date or slogan at the end", "a_verifier", "a title card closes the film (%s): the name, or a logo?" % R.at(M["cartons"][-1]["debut"]),
              "the name; never a logo alone", "0 out of 16 logo alone", None)
    # K14 internal blacks
    ni = M["noirs_internes"]
    R.add("K14", "Internal blacks", "note" if len(ni) > 2 else "ok", "%d" % len(ni), "at most 2, from 0.3 to 0.9 s", "4 films out of 16 have some; 1 has 6 (chapters)",
          ("remove the blacks %s, unless they split chapters" % liste_tc(R, ni)) if len(ni) > 2 else None)
    # K15 still pictures
    if M["part_fixes"] is not None:
        R.add("K15", "Still pictures", "note" if M["part_fixes"] > 0.25 else "ok", P_(M["part_fixes"]), "7 % (at most 25 %)", "197 shots",
              "make the picture move: slow turn, push in or pull back on the static shots" if M["part_fixes"] > 0.25 else None)
    # K16 voice-over
    pa = M["parole"]
    if pa is not None and pa["n"]:
        bad = []
        if pa["part"] > 0.75:
            bad.append("voice over %s of the time (target 61 to 69 %%)" % P_(pa["part"]))
        if pa["premiere"] < 3.0:
            bad.append("the voice starts at %s (target 3.9 to 4.6 s)" % S_(pa["premiere"]))
        if pa["fin_avant_bout"] < 2.0:
            bad.append("the voice ends %s before the end (target 2.3 to 3.6 s)" % S_(pa["fin_avant_bout"]))
        R.add("K16", "Voice-over", "alerte" if bad else "ok", "; ".join(bad) or "%s of the time, from %s to %s before the end" % (P_(pa["part"]), S_(pa["premiere"]), S_(pa["fin_avant_bout"])),
              "61 to 69 %; silent for 3.9 to 4.6 s at the start and 2.3 to 3.6 s at the end", "3 voice-over films out of 3",
              "leave the start and the end silent, cut sentences" if bad else None, "sous-titres")
    # K18 duration without voice
    if D > 60 and not voix:
        R.add("K18", "Film without voice longer than 60 s", "note", S_(D), "24 to 51 s, or chapters", "13 out of 13 films without voice",
              "split into chapters of 15 to 30 s (convention) or shorten")
    # K19 black and white
    if M["part_nb"] is not None:
        R.add("K19", "Black and white", "note" if M["part_nb"] > 0.5 else "ok", "%s of shots desaturated" % P_(M["part_nb"]), "color",
              "0 out of 16 in desaturated black and white", "keep color in a product film" if M["part_nb"] > 0.5 else None)
    ctl_musique(R, M, "K20", "note")


def ctl_musique(R, M, id_, niveau, permis=False):
    ss = M.get("sur_son")
    if ss is None:
        R.add(id_, "Cuts locked to every beat", "non_mesure", "—", "the big changes on the music, not every cut",
              "convention (locking not shown in the corpus)", "provide the sound (the render's track, or --son)", "—")
        return
    n = ss["coupes"]
    st_t = ss.get("sur_temps")
    grille = st_t is not None and n >= 6 and st_t >= 0.6 * n and st_t >= 2 * ss.get("attendu_temps", 0)
    att = n >= 6 and ss["sur_attaque"] >= 0.6 * n and ss["sur_attaque"] >= 2 * ss["attendu_hasard"]
    mes = "%d cuts out of %d within ± 70 ms of an onset (chance %s)" % (ss["sur_attaque"], n, F(ss["attendu_hasard"], 1))
    if st_t is not None:
        mes += "; %d on the tempo grid (chance %s)" % (st_t, F(ss["attendu_temps"], 1))
    if (grille or att) and not permis:
        R.add(id_, "Cuts locked to every beat", niveau, mes, "lock the exit from black, the reveal, the peak, the name; not every cut",
              "locking not shown in the corpus (16 out of 62 against 16.4 by chance); clear in 1 film out of 11 (photos)",
              "move every other cut off the beat; keep the strong beats for the big changes", "son")
    else:
        R.add(id_, "Cuts locked to every beat", "ok", mes, "no mechanical locking", "convention", None, "son")


# ---------------------------------------------------------------- documentary family

def controles_documentaire(R, M, C, a, ann):
    D = M["duree"]
    img = M["img"]
    sf = a.sous_famille or ann.get("sous_famille")
    deduit = False
    if sf not in ("pose", "choral"):
        sf = "choral" if (M["med"] or 2) < 1.5 else "pose"
        deduit = True
    R.contexte = "mode %s%s" % (sf, " (inferred from the median shot)" if deduit else "")
    ctl = {c["id"]: c for c in C.get("controles", [])}
    pa = M["parole"]
    # D1
    if M["med"] is not None:
        if sf == "pose":
            bad = M["med"] < 1.5 or M["med"] > 2.8
            cib = "1.8 to 2.2 s"
        else:
            bad = M["med"] > 1.8
            cib = "1.0 to 1.5 s"
        R.add("D1", "Median shot", "alerte" if bad else "ok", "%s s" % F(M["med"]), cib, g(ctl, "D1.statut", "observed"),
              None if not bad else ("shorten the illustrations; cut the interviews under the voice" if M["med"] > 2 else "let the shots run: fewer cuts in the interviews"))
    # D2
    cpm = M["chg_min"]
    bad = cpm < 18 or cpm > 48
    R.add("D2", "Cuts per minute", "alerte" if bad else ("ok" if (20 <= cpm <= 27 if sf == "pose" else 33 <= cpm <= 45) else "note"),
          F(cpm, 1), "calm 20 to 27; choral 33 to 45; alert outside 18 to 48", "observed 8 out of 8; threshold: convention",
          None if not bad else ("cut more often: illustrate the voice" if cpm < 18 else "too many cuts: group them"))
    # D3
    t = M["tiers"]
    if all(x is not None for x in t):
        if sf == "pose":
            r_ = t[2] / t[1] if t[1] else 1.0
            st = "ok" if r_ >= 0.85 else ("note" if r_ >= 0.80 else "alerte")
            R.add("D3", "Shape of the pace", st, "thirds: %s / %s / %s s (end %s vs. the middle)" % (F(t[0]), F(t[1]), F(t[2]), ("%+d %%" % round(100 * (r_ - 1)))),
                  "the end is not faster than the middle (no more than 15 % faster); alert beyond 20 % (measurement margin: convention)",
                  "0 out of 5 calm films speed up by more than 15 %; the fastest: 14 %",
                  "lengthen the shots in the last third; end on a held shot" if st != "ok" else None)
        else:
            bad = t[2] >= t[0]
            R.add("D3", "Shape of the pace", "alerte" if bad else "ok", "thirds: %s / %s / %s s" % (F(t[0]), F(t[1]), F(t[2])),
                  "the end is faster than the start", "3 out of 3 choral films", "speed up the last third: a burst of works before the logo" if bad else None)
    # D4
    if sf == "pose":
        lf = [p for p in img if p["duree"] >= 5 and p["rel"] >= 0.8]
        R.add("D4", "Shot of at least 5 s in the last fifth", "ok" if lf else "alerte",
              ("shot #%d (%s)" % (lf[0]["n"], S_(lf[0]["duree"]))) if lf else "none", "at least one", "5 out of 5 calm films",
              None if lf else "hold the last shot 5.7 to 8.1 s (preferably wide) from %s" % R.at(M["dernier"]["debut"] if M["dernier"] else D - 6))
    # D5
    non_coupe = M["n_transitions"] - M["transitions"].get("coupe", 0) - M["transitions"].get("fondu_enchaine_candidat", 0)
    ni = [p for p in M["noirs_internes"] if 0.1 <= p["rel"] <= 0.9]     # chapter zone
    bad = len(ni) > 1 or (non_coupe / M["n_transitions"]) > 0.05
    R.add("D5", "Transitions other than the cut", "alerte" if bad else "ok", "%s; %d internal black(s)" % (P_(non_coupe / M["n_transitions"]), len(ni)),
          "at most 2 %; a single dip to black, to change chapter", "12 out of 606; at most 1 internal black (3 films)",
          ("keep a single chapter black; remove %s" % liste_tc(R, ni[1:])) if len(ni) > 1 else ("hard cut everywhere" if bad else None))
    if M["fondus_enchaines"]:
        idx = {p["n"]: p for p in R._plans}
        PERS = ("entretien", "personne")
        par = [p for p in M["fondus_enchaines"] if p["ann"].get("type") in PERS and idx.get(p["n"] - 1, {}).get("ann", {}).get("type") in PERS]
        if par:
            R.add("D5b", "Cross dissolve under speech", "alerte", liste_tc(R, par), "never between two speech shots", "0 out of 606",
                  "replace with hard cuts", "declare")
    ctl_fondus(R, M, "D5c", 1, 0.02, "1 cross dissolve out of 606 transitions")
    # D6, D7 speech
    if pa is None:
        for id_, ti in (("D6", "Share of speech"), ("D7", "Breathing spaces"), ("D17", "First speech"), ("D18", "Last speech")):
            ctl_parole_absente(R, id_, ti, "provide the subtitles (--sous-titres .srt or .vtt)")
    else:
        p_ = pa["part"]
        bad = p_ < 0.45 or p_ > 0.92
        R.add("D6", "Share of speech", "alerte" if bad else ("ok" if 0.51 <= p_ <= 0.88 else "note"), P_(p_), "51 to 88 %; alert under 45 % or above 92 %",
              "observed 8 out of 8; threshold: convention",
              None if not bad else ("let it breathe: remove sentences" if p_ > 0.92 else "too little speech for a testimonial"), "sous-titres")
        resp = [(x, y) for x, y in pa["respirations"]]
        if sf == "pose" and D > 90:
            R.add("D7", "Breathing spaces (3 s without speech)", "ok" if resp else "note", "%d" % len(resp), "at least one (0.6 per minute)", "6 films out of 8; 2 films with almost continuous speech have none",
                  None if resp else "leave 3 to 9 s of music alone over pictures, around the middle", "sous-titres")
        else:
            R.add("D7", "Breathing spaces (3 s without speech)", "ok", "%d" % len(resp), "at least one if a calm film is longer than 90 s", "6 out of 8", None, "sous-titres")
        pr = pa["premiere"]
        st = "alerte" if pr < 1.0 else ("ok" if 2.9 <= pr <= 16.5 else "note")
        R.add("D17", "First speech", st, "at %s" % S_(pr), "between 3 and 17 s (median 6 s), after the black and the calm", "8 out of 8",
              "open with 3 to 6 s of black, calm sound or pictures before the first sentence" if st != "ok" else None, "sous-titres")
        fb = pa["fin_avant_bout"]
        fmin = g(C, "parole.derniere_parole_avant_fin.min", 0.89)
        st = "alerte" if fb < fmin - 0.05 else ("ok" if fb <= 10 else "note")
        R.add("D18", "Last speech before the end", st, "%s before the end" % S_(fb), "1 to 10 s (median 4.2 s)", "7 out of 7, from %s to 9.5 s" % F(fmin),
              "do not cut on a sentence: leave 2 to 5 s of picture and music after the last sentence" if st == "alerte" else None, "sous-titres")
    # D8 speech over the face
    vis = [p for p in img if p["ann"].get("type") in ("entretien", "personne")]
    if pa is not None and vis:
        tot = sum(b - a_ for a_, b in pa["intervalles"])
        sur = sum(M["parole_dans"](p["debut"], p["fin"]) for p in vis)
        r = sur / tot if tot else 0
        R.add("D8", "Speech heard over the face", "alerte" if (r > 0.60 and sf == "pose") else "ok", P_(r), "25 to 55 % (median 33 %)", "6 films out of 8 under 55 %",
              "put two thirds of the speech over illustrations (places, hands, works)" if (r > 0.60 and sf == "pose") else None, "oeil")
    else:
        R.add("D8", "Speech heard over the face", "non_mesure", "—", "25 to 55 %", "6 out of 8", "annotate the shot types (entretien, personne, illustration) and provide the subtitles", "—")
    # D9 enter through the voice
    pers = {}
    for p in img:
        pid = p["ann"].get("personne")
        if pid and p["ann"].get("type") in ("entretien", "personne") and pid not in pers:
            pers[pid] = p
    if pa is not None and pers:
        voix_avant = [pid for pid, p in pers.items() if M["parole_dans"](max(0, p["debut"] - 1.5), p["debut"]) > 0.5]
        R.add("D9", "Enter through the voice", "ok" if voix_avant else "note", "%d person(s) out of %d heard before being seen (approximate)" % (len(voix_avant), len(pers)),
              "at least the first person, face 1.5 to 4.7 s after the voice", "13 out of 20",
              None if voix_avant else "let the first voice be heard over an illustration, show the face 3 s later", "oeil")
    # D10, D11, D12, D13 interviews
    ent = [p for p in img if p["ann"].get("type") == "entretien"]
    if ent:
        longs = [p for p in ent if p["duree"] > 5 and p["rel"] < 0.8]
        R.add("D10", "Long interview shot before the end", "alerte" if longs else "ok", "%d shot(s) > 5 s before the last fifth" % len(longs),
              "at most 3.2 s (p90); more than 5 s only at the end", "162 shots", ("cut under the voice: %s" % liste_tc(R, longs)) if longs else None, "oeil")
        lar = [p for p in ent if p["ann"].get("valeur") == "large"]
        R.add("D11", "Interview in a wide shot", "alerte" if lar else "ok", "%d" % len(lar), "medium close-up, medium, close-up", "0 out of 162",
              ("reframe tighter: %s" % liste_tc(R, lar)) if lar else None, "oeil")
        saute = []
        for p1, p2 in zip(img[:-1], img[1:]):
            if p1["ann"].get("personne") and p1["ann"].get("personne") == p2["ann"].get("personne") \
                    and p1["ann"].get("valeur") and p1["ann"].get("valeur") == p2["ann"].get("valeur") and p2["ann"].get("type") == "entretien":
                saute.append(p2)
        R.add("D12", "Same person, two shots in a row", "note" if saute else "ok", "%d jump cut(s)" % len(saute), "the second one tighter", "9 out of 10",
              ("use the other camera, tighter: %s" % liste_tc(R, saute)) if saute else None, "oeil")
        bouge = [p for p in ent if p.get("derive")]
        if bouge:
            R.add("D13", "Camera on the interview", "a_verifier", "%d interview(s) where the picture changes between start and end" % len(bouge), "static", "18 out of 20 static",
                  "look at %s" % liste_tc(R, bouge))
    # D15 lower thirds
    band = [x for x in M["textes"] if x.get("type") == "bandeau"]
    if band:
        bad = [x for x in band if (float(x["fin"]) - float(x["debut"])) > 5 or x.get("boite") or x.get("place") in ("centre", "visage")]
        R.add("D15", "Name lower thirds", "alerte" if bad else "ok", "%d lower third(s), %d breaking the rule" % (len(band), len(bad)),
              "2 to 3.5 s, bottom left or right, away from the face, no box", "27 lower thirds, 8 people",
              "small, at the bottom, on the empty side, no box, 2 to 3.5 s" if bad else None, "oeil")
    # D16 message title cards
    cm = [x for x in M["textes"] if x.get("type") in ("phrase", "question", "these", "carton")]
    nb_c = len(cm) if M["textes"] else len(M["cartons"])
    trop_mots = [x for x in cm if int(x.get("mots", 0)) > 12]
    src = "oeil" if M["textes"] else ("declare" if any(p["carton_src"] == "declare" for p in M["cartons"]) else "calcul")
    bad = nb_c > 3 or trop_mots or any(x.get("boite") for x in cm)
    R.add("D16", "Message title cards", ("alerte" if src != "calcul" else "a_verifier") if bad else "ok", "%d title card(s)%s" % (nb_c, (", %d with more than 12 words" % len(trop_mots)) if trop_mots else ""),
          "0 to 3, small, centered, 12 words at most", "observed 8 out of 8", "keep one question or thesis at the opening, or 1 to 3 closing title cards" if bad else None, src)
    # D17 calm sound at the opening
    if M["noir_ouverture"] == 0 and not M["seuil_carton"]:
        R.add("D17b", "Opening through black", "note", "the film starts on a picture", "black first", "6 out of 8", "add 1 to 4 s of black at the start")
    son = M["son"]
    if son:
        calme = son["ecart_debut_db"] >= 6
        R.add("D17c", "Calm sound at the start", "ok" if calme else "note", "first 3 s %s dB under the median level" % F(son["ecart_debut_db"], 1),
              "lower than the rest (9.7 to 47.8 dB lower)", "8 out of 8", None if calme else "bring the music in gently; start in calm", "son")
        if pa is not None:
            sil = []
            ivs = pa["intervalles"]
            pas_parole = []
            prev = 1.0
            for x, y in ivs:
                if x > prev:
                    pas_parole.append((prev, x))
                prev = y
            if D - 1 > prev:
                pas_parole.append((prev, D - 1))
            courbe = son.get("courbe_db_par_0_5s") or []
            tot = n_sil = 0
            for x, y in pas_parole:
                for k in range(int(x * 2), int(y * 2)):
                    if k < len(courbe):
                        tot += 1
                        n_sil += courbe[k] < -50
            if tot:
                r = n_sil / tot
                R.add("D20", "Sound between sentences", "alerte" if r > 0.2 else "ok", "%s of the time without speech under -50 dB" % P_(r),
                      "a continuous bed (at most 20 % under -50 dB)", "8 out of 8", "lay continuous music under the voices" if r > 0.2 else None, "son")
    # D19 final burst of faces
    raf = [r for r in M["rafales"] if r[0]["rel"] >= 0.85]
    if raf:
        vis = [p for p in raf[-1] if p["ann"].get("visage") or p["ann"].get("type") in ("entretien", "personne")]
        if any(p["ann"] for p in raf[-1]):
            R.add("D19", "Final burst", "alerte" if vis else "ok", "%d face shot(s) in the final burst" % len(vis), "the works or the product, not the faces",
                  "4 out of 4", "replace the faces with works" if vis else None, "oeil")
        else:
            R.add("D19", "Final burst", "a_verifier", "final burst of %d shots at %s" % (len(raf[-1]), R.at(raf[-1][0]["debut"])), "works or product, no faces", "4 out of 4", None)
    # D21 black and white
    if M["part_nb"] is not None and 0.1 < M["part_nb"] < 0.9:
        R.add("D21", "Black and white", "a_verifier", "%s of shots desaturated" % P_(M["part_nb"]), "the whole film, or people in B&W and screens in color",
              "4 out of 4 portraits; 2 out of 2 mixed", "check that the mix follows a rule (people in B&W, screens in color)")
    elif M["part_nb"] is not None:
        R.add("D21", "Black and white", "ok", "%s of shots desaturated" % P_(M["part_nb"]), "a single choice, or a rule", "observed")
    if M["dernier"] is not None and sf == "pose":
        d = M["dernier"]["duree"]
        R.add("D18b", "Held shot at the end", "ok" if d >= 5 else "note", S_(d), "5.7 to 8.1 s", "5 out of 5 calm films",
              None if d >= 5 else "hold the last shot 6 to 8 s, preferably wide")


# ---------------------------------------------------------------- trailer family

def controles_bandeannonce(R, M, C, a, ann):
    D = M["duree"]
    img = M["img"]
    sf = a.sous_famille or ann.get("sous_famille") or "catalogue_mele"
    R.contexte = "subfamily %s" % sf
    sc = C.get("seuils_critique", {})
    usage = sf == "usage"
    # B1 median shot
    if M["med"] is not None:
        if usage:
            lo, hi, alo, ahi = 1.0, 1.7, 0.5, 1.9
            base = "2 usage films: 1.03 and 1.67 s; alert above 1.9 s: convention"
        else:
            lo, hi = g(sc, "plan_image_median_s.cible.0", 0.75), g(sc, "plan_image_median_s.cible.1", 1.2)
            alo, ahi = g(sc, "plan_image_median_s.alerte_en_dessous", 0.5), g(sc, "plan_image_median_s.alerte_au_dessus", 1.65)
            base = "6 trailers: 0.73 to 1.65 s"
        m = M["med"]
        e1 = 1.0 / mv.FPS          # one frame of tolerance
        st = "alerte" if (m > ahi + e1 or m < alo - e1) else ("ok" if lo - e1 <= m <= hi + e1 else "note")
        R.add("B1", "Median picture shot", st, "%s s" % F(m), "%s to %s s; alert above %s s or under %s s" % (F(lo), F(hi), F(ahi), F(alo)), base,
              None if st != "alerte" else ("cut shorter: the body around 0.9 s, the peak around 0.6 s" if m > ahi else "unreadable: hold shots at least 0.5 s"))
    # B2 acceleration
    t = M["tiers"]
    if t[0] is not None and t[2] is not None:
        ok = t[2] < t[0]
        R.add("B2", "Last third faster than the first", "ok" if ok else "alerte", "thirds: %s / %s / %s s" % (F(t[0]), F(t[1]) if t[1] else "—", F(t[2])),
              "shorter in the last third (1.20 → 0.90 → 0.77 s)", "6 out of 6",
              None if ok else "shorten the shots in the last third, up to the peak")
    # B3, B4 peak
    pk = M["pic10"]
    if pk:
        p0, p1 = g(sc, "pic_position.0", 0.78), g(sc, "pic_position.1", 0.88)
        if usage:
            R.add("B3", "Peak position (fastest 10 s)", "note" if not (0.7 <= pk["position"] <= 0.9) else "ok", P_(pk["position"]), "78 % in 1 usage film out of 2", "2 usage films",
                  None)
        else:
            st = "alerte" if pk["position"] < 0.70 else ("ok" if p0 - 0.02 <= pk["position"] <= p1 + 0.02 else "note")
            R.add("B3", "Peak position (fastest 10 s)", st, "%s (%s → %s)" % (P_(pk["position"]), R.at(pk["debut"]), R.at(pk["fin"])),
                  "%s to %s; alert before 70 %%" % (P_(p0), P_(p1)), "6 out of 6",
                  "move the fastest passage %s, just before the closing" % plage(R, D, p0, p1) if st == "alerte" else None)
        q0, q1 = g(sc, "pic_plan_median_s.0", 0.5), g(sc, "pic_plan_median_s.1", 0.85)
        st = "alerte" if pk["mediane"] > 1.0 else ("ok" if pk["mediane"] <= q1 + 0.05 else "note")
        parle = M["parole"] is not None and M["parole"]["n"] > 0
        if (usage or not parle) and st == "alerte":
            st = "note"          # basis: 5 films with speech; usage: peaks of 1.17 and 0.37 s (2 films)
        R.add("B4", "Peak shots", st, "%s s" % F(pk["mediane"]), "%s to %s s; alert above 1 s" % (F(q0), F(q1)), "5 films with speech",
              "cut the peak to 0.5-0.6 s per shot" if st == "alerte" else None)
    else:
        R.add("B3", "Peak position", "alerte", "no 10 s window with 5 shots", "78 to 88 %", "6 out of 6", "cut a 10 s peak at 0.6 s per shot around 80 %")
    # B5 closing: from the first black or title card after the peak to the end
    fstart, src = None, "calcul"
    if ann.get("fermeture") is not None:
        fstart, src = float(ann["fermeture"]), "oeil"
    elif pk:
        apres = [p for p in R._plans if p["debut"] >= pk["fin"] - 1 and p["kind"] in ("noir", "carton")]
        if apres:
            fstart = apres[0]["debut"]
            src = "declare" if R.meta["source"] != "video" else "calcul"
    if fstart is not None:
        part = (D - fstart) / D
        lo, hi = g(sc, "fermeture_part.0", 0.06), g(sc, "fermeture_part.1", 0.17)
        st = "alerte" if (part > 0.20 or part < 0.05) else ("ok" if lo <= part <= hi else "note")
        if st == "alerte" and src == "calcul":
            st = "a_verifier"
        R.add("B5", "Closing duration", st, "%s (%s, from %s)" % (P_(part), S_(D - fstart), R.at(fstart)), "%s to %s; alert beyond 20 %% or under 5 %%" % (P_(lo), P_(hi)),
              "8 films (median 8 s)", ("bring the closing back to 6-17 %%: black, closing line, black, title, from about %s" % R.at(D * 0.9)) if st in ("alerte", "a_verifier") else None, src)
    else:
        R.add("B5", "Closing duration", "a_verifier", "start of the closing not found", "6 to 17 % of the duration", "8 films",
              "give \"fermeture\" (in s) in the annotations")
    # B6 last element
    vis = [p for p in R._plans if p["kind"] != "noir"]
    last = vis[-1] if vis else None
    if last is not None:
        lo, hi = g(sc, "titre_final_s.0", 2.5), g(sc, "titre_final_s.1", 4.8)
        if last["kind"] == "carton":
            ok = lo - 0.1 <= last["duree"] <= hi + 0.3 or last["duree"] <= 7.7
            st = "ok" if lo - 0.1 <= last["duree"] <= hi + 0.3 else ("note" if last["duree"] <= 7.7 else "alerte")
            R.add("B6", "Last element: title or logo", st, "title card of %s%s" % (S_(last["duree"]), " (found by calculation)" if last["carton_src"] == "calcul" else ""),
                  "%s to %s s" % (F(lo, 1), F(hi, 1)), "8 out of 8; 7.7 s for an animated title (1 case)",
                  None if st == "ok" else "hold the title for about 3.5 s", last["carton_src"] or "calcul")
        else:
            st = "alerte" if R.meta["source"] != "video" or last["ann"] else "a_verifier"
            R.add("B6", "Last element: title or logo", st, "the film ends on a picture (%s)" % R.at(last["debut"]), "title or logo, 2.5 to 4.8 s",
                  "8 out of 8", "end with a black, then the title or the logo coming out of the black, 3.5 s", "oeil" if last["ann"] else "calcul")
    # B7, B8 transitions
    fondus = len(M["fondus_enchaines"])
    autres = M["n_transitions"] - M["transitions"].get("coupe", 0) - M["transitions"].get("fondu_enchaine_candidat", 0)
    part = 1 - autres / M["n_transitions"]
    st = "alerte" if part < 0.85 else ("ok" if part >= 0.9 else "note")
    R.add("B7", "Hard cuts", st, P_(part), "at least 90 %; alert under 85 %", "92 % (423 out of 459)", "replace the effects with cuts" if st == "alerte" else None)
    ctl_fondus(R, M, "B8", max(1, int(0.03 * M["n_transitions"])), g(sc, "fondus_enchaines_max", 0.03), "1.7 %; 6 out of 8 go from a title to the picture",
               "; keep the dissolve for going from a title to the picture", sur_texte_permis=True)
    # B9 wide shots in the first third
    v1 = [p for p in img if p["rel"] < 1 / 3 and p["ann"].get("valeur") in VALEURS]
    if len(v1) >= 3 and not usage:
        r = sum(1 for p in v1 if p["ann"]["valeur"] == "large") / len(v1)
        st = "alerte" if r < 0.25 else ("ok" if r >= g(sc, "part_plans_larges_debut_min", 0.35) else "note")
        R.add("B9", "Wide shots in the first third", st, P_(r), "at least 35 %; alert under 25 %", "39 to 56 % (6 films)",
              "open wide: place the locations before getting closer" if st == "alerte" else None, "oeil")
    elif not usage:
        R.add("B9", "Wide shots in the first third", "a_verifier", "sizes not annotated", "at least 35 %", "6 out of 6", None)
    # B10 static shots
    if M["part_fixes"] is not None:
        f_ = M["part_fixes"]
        st = "alerte" if f_ > 0.25 else ("ok" if f_ <= g(sc, "plans_fixes_max", 0.15) else "note")
        R.add("B10", "Static shots", st, P_(f_), "at most 15 %; alert beyond 25 %", "7.6 % (29 out of 384)", "make the picture move" if st == "alerte" else None)
    # B11, B12 speech
    pa = M["parole"]
    if pa is not None and pa["n"]:
        smax, wmax = g(sc, "replique_max_s", 3.1), g(sc, "replique_max_mots", 10)
        subs = R._subs or []
        longues = [x for x in subs if (x[1] - x[0]) > smax or x[3] > wmax]
        part = len(longues) / len(subs) if subs else 0
        st = "alerte" if part > 0.25 else ("ok" if part <= 0.15 else "note")
        R.add("B11", "Long lines", st, "%d out of %d beyond %s s or %d words (%s)" % (len(longues), len(subs), F(smax, 1), wmax, P_(part)),
              "1 line out of 10 beyond (90th percentile: %s s, %d words); alert beyond one out of 4 (convention)" % (F(smax, 1), wmax),
              "108 lines: median 1.7 s and 6 words",
              ("cut, or split over two shots: %s" % ", ".join(R.at(x[0]) for x in longues[:6])) if st != "ok" else None, "sous-titres")
        if pk:
            r = M["parole_dans"](pk["debut"], pk["fin"]) / 10.0
            st = "alerte" if r > 0.5 else ("ok" if r <= 1 / 3 + 0.02 else "note")
            R.add("B12", "Speech in the peak", st, P_(r), "a third at most; alert beyond half", "16 to 38 %; less than over the whole film in 4 out of 5",
                  "leave the music alone during the peak" if st == "alerte" else None, "sous-titres")
    else:
        ctl_parole_absente(R, "B11", "Longest line", "provide the subtitles if the film has speech")
    # B13 opening
    nb_o = M["noir_ouverture"]
    lo, hi = g(sc, "ouverture_noir_s.0", 0.1), g(sc, "ouverture_noir_s.1", 4.2)
    st = "alerte" if nb_o == 0 else ("ok" if lo <= nb_o <= hi else "note")
    R.add("B13", "Opening in black", st, ("black of %s" % S_(nb_o)) if nb_o else "picture from the first frame", "%s to %s s (median 0.6 s)" % (F(lo, 1), F(hi, 1)),
          "7 out of 7", "add 0.5 s of black before the first picture" if st == "alerte" else None)
    # B14 block titles
    tb = [x for x in M["textes"] if x.get("type") == "titre_bloc"]
    if sf == "catalogue_par_blocs" and tb:
        bad = [x for x in tb if (float(x["fin"]) - float(x["debut"])) > 3.0 or x.get("place") == "fin_de_bloc"]
        R.add("B14", "Block titles", "alerte" if bad else "ok", "%d title(s), %d breaking the rule" % (len(tb), len(bad)), "at the head of the block, 0.8 to 2.3 s", "20 out of 21",
              "title at the head of the block, about 1 s" if bad else None, "oeil")
    # B15, B16 usage
    if usage:
        tx = [p for p in M["cartons"] if p["rel0"] < 0.9] + [x for x in M["textes"] if float(x.get("debut", 0)) < 0.9 * D]
        src = "oeil" if M["textes"] else ("declare" if any(p["carton_src"] == "declare" for p in M["cartons"]) else "calcul")
        st = ("alerte" if src != "calcul" else "a_verifier") if tx else "ok"
        R.add("B15", "Text in a usage film", st, "%d text(s) before the last 10 %%" % len(tx), "only in the last 10 %", "2 out of 2",
              "move the text to the end: one sentence of 3 to 9 words, then the name" if tx else None, src)
        ob = [p for p in img if "objet" in p["ann"]]
        if len(ob) >= 5:
            r = sum(1 for p in ob if p["ann"]["objet"]) / len(ob)
            st = "alerte" if (r < 1 / 6 or r > 0.5) else ("ok" if 0.25 <= r <= 0.36 else "note")
            R.add("B16", "Object in the picture (usage film)", st, P_(r), "one shot in 4 to one shot in 3", "2 films: 32 and 34 %",
                  ("show the object more often: person, object, person" if r < 1 / 6 else "too much object: that is a product film; show the people and what they do") if st == "alerte" else None, "oeil")
        else:
            R.add("B16", "Object in the picture (usage film)", "a_verifier", "shots not annotated (field \"objet\")", "one shot in 4 to one in 3", "2 films", None)
    ctl_musique(R, M, "B17", "note", permis=False)


# ---------------------------------------------------------------- opening family

def controles_ouverture(R, M, C, a, ann):
    """Levels: alert = no film in the corpus does it; note = a minority does it."""
    D = M["duree"]
    img = M["img"]
    sf = a.sous_famille or ann.get("sous_famille") or "ouverture"
    R.contexte = "subfamily %s" % sf
    med_film = M["med"]
    corps = img[1:-1]
    cmed = mv.med([p["duree"] for p in corps]) if corps else None
    plan_seq = len(img) <= 3
    froid = bool(ann.get("ouverture_a_froid"))
    if sf in ("ouverture", "sketch"):
        lo, hi = g(C, "durees.film.cible_conseil.0", 60), g(C, "durees.film.cible_conseil.1", 120)
        R.add("O0", "Film duration", "ok" if lo <= D <= hi else "note", S_(D), "60 to 120 s (convention)", "8 openings from 65 to 143 s", None)
        if plan_seq:
            R.add("O2", "Median shot of the body", "sans_objet", "single take (%d picture shots)" % len(img), "—", "1 opening out of 8 is a single take")
        # O1 entry
        if M["premier"] is not None and not plan_seq:
            seuil = M["noir_ouverture"] > 0 or M["seuil_carton"]
            d1 = M["premier"]["duree"]
            ok = d1 >= 5 or froid or (seuil and d1 >= 3)
            R.add("O1", "Entry", "ok" if ok else "note", "%s; first shot of %s" % ("threshold" if seuil else "no threshold", S_(d1)),
                  "a threshold (black 0.5 to 1.5 s, or title card then black), then a first shot of 5 to 10 s",
                  "5 out of 8 at least 5 s; 6 out of 8 with a threshold; 1 cold open",
                  None if ok else "%shold the first shot 5 to 10 s (shot #%d at %s)" % ("" if seuil else "add 0.5 to 1.5 s of black, then ", M["premier"]["n"], R.at(M["premier"]["debut"])))
        # O2 body: corpus quartiles, slowest observed 3.17 s (1 film out of 7)
        if cmed is not None and not plan_seq:
            q1, q3 = g(C, "durees.p25", 0.90), g(C, "durees.p75", 2.13)
            vmax = g(C, "durees.mediane_des_medianes_par_film.max", 3.17)
            if q1 <= cmed <= q3:
                st = "ok"
            elif q3 < cmed <= vmax + 1.0 / mv.FPS:
                st = "note"
            else:
                st = "alerte"
            R.add("O2", "Median shot of the body", st, "%s s" % F(cmed), "1.33 s (quartiles %s to %s s)" % (F(q1), F(q3)),
                  "337 shots, 7 films; median per film from 1.20 to %s s" % F(vmax),
                  None if st == "ok" else ("too slow: cut the body shots to about 1.3 s" if cmed > q3 else "too choppy: hold the shots around 1.3 s"))
            tc_ = [[], [], []]
            for p in corps:
                tc_[min(2, int(p["rel"] * 3))].append(p["duree"])
            tm = [mv.med(x) for x in tc_]
            if all(x is not None for x in tm):
                bad = tm[2] > 1.15 * tm[1] + 1.0 / mv.FPS
                R.add("O3", "The body keeps its pace", "note" if bad else "ok", "thirds of the body: %s / %s / %s s" % (F(tm[0]), F(tm[1]), F(tm[2])),
                      "1.60 → 1.30 → 1.24 s", "7 films", "keep the pace up to the peak; only the landing slows down" if bad else None)
        # O4 peak
        p5 = M["pic5"]
        if p5 is not None and not plan_seq:
            pos = p5["milieu_rel"]
            ok = 0.58 <= pos <= 0.82 and p5["mediane"] <= 0.8
            R.add("O4", "Speed peak", "ok" if ok else "note",
                  "at %s (%s → %s), shots of %s s" % (P_(pos), R.at(p5["debut"]), R.at(p5["fin"]), F(p5["mediane"])),
                  "5 shots of 0.4 to 0.7 s between 60 and 80 %", "5 openings out of 7",
                  None if ok else "place 5 short shots (0.4 to 0.7 s) %s, on the strongest moment of the music" % plage(R, D, 0.6, 0.8))
    # O5 landing
    der = M["dernier"]
    if der is not None and sf not in ("transition_decor",):
        if sf in ("cloture", "hommage", "clip"):
            R.add("O5", "Ending", "ok", "last picture shot of %s" % S_(der["duree"]), "signature shot or logo (1.5 to 3.5 s)", "closings: 3 out of 4 end on a logo", None)
        elif not plan_seq:
            apres = [p for p in R._plans if p["debut"] >= der["fin"] - 0.05 and p["kind"] == "carton"]
            fin_carton = max((p["duree"] for p in apres), default=0.0)
            ratio = der["duree"] / med_film if med_film else None
            dmin = g(C, "durees.fin.dernier_plan_image.min", 4.34)
            if (ratio is not None and ratio >= 3.5 and der["duree"] >= 5) or fin_carton >= 5:
                st = "ok"
            elif der["duree"] < dmin - 1.0 / mv.FPS and (ratio is None or ratio < 3.5):
                st = "alerte"      # shorter than any last shot in the corpus
            else:
                st = "note"
            R.add("O5", "Landing", st, "last picture shot of %s (%s times the median shot)%s" % (S_(der["duree"]), F(ratio, 1), ("; final title card of %s" % S_(fin_carton)) if fin_carton else ""),
                  "5 to 11 s, at least 3.5 times the median shot; or a final title card", "6 out of 8 at least 5 s; 7 out of 7 at least 3.5 times the median shot; 2 end on a title card",
                  None if st == "ok" else "hold the last shot (#%d, %s) up to about 7 s, wide, on the place or the person who will speak; lengthen the 3 to 5 shots before it" % (der["n"], R.at(der["debut"])))
        v = der["ann"].get("valeur")
        if v:
            R.add("O6", "Wide ending", "alerte" if v in SERRE else "ok", VAL_EN.get(v, v), "the place or the person, wide", "0 out of 7 end tight; 5 out of 7 wide",
                  "end on the place or the person, wide" if v in SERRE else None, "oeil")
    # O7 dissolves
    if sf != "clip":
        ctl_fondus(R, M, "O7", max(1, int(0.05 * M["n_transitions"])), 0.05, "2 out of 367 changes",
                   "; a dissolve of 1 to 1.5 s only to go from animation to live action")
    # O8 black in the middle (the transition between settings hides its cuts in the dark: not concerned)
    if sf in ("ouverture", "sketch"):
        mil = [p for p in M["noirs_internes"] if 0.15 <= p["rel"] <= 0.85 and p["duree"] >= 0.2]
        R.add("O8", "Black in the middle of the film", "note" if (mil and not froid) else "ok", "%d" % len(mil), "black is for entering or ending",
              "15 blacks out of 17 at the entry; in the middle: one cold open, one flame between blacks",
              ("remove the blacks %s: hard cut" % liste_tc(R, mil)) if (mil and not froid) else None)
    # O9 text in the middle
    tx = list(M["cartons"])
    src = "oeil" if M["textes"] else ("declare" if any(p["carton_src"] == "declare" for p in tx) else "calcul")
    txt_t = [(float(x.get("debut", 0)), x) for x in M["textes"] if x.get("type") not in ("bandeau",)] if M["textes"] else [(p["debut"], p) for p in tx]
    mil_t = [t for t, _ in txt_t if 0.15 * D <= t <= 0.85 * D]
    if sf in ("ouverture", "sketch", "transition_decor"):
        bad = bool(mil_t) or len(txt_t) > 2 or (sf == "transition_decor" and txt_t)
        st = ("alerte" if src != "calcul" else "a_verifier") if bad else "ok"
        R.add("O9", "Text in the middle, or more than 2 texts", st, "%d text(s), %d of them in the middle" % (len(txt_t), len(mil_t)),
              "0 to 2 texts, at the threshold or at the end" if sf != "transition_decor" else "no text", "0 out of 7 in the middle; 0 out of 6 transitions with text",
              ("move to the threshold or the end, or remove: %s" % ", ".join(R.at(t) for t in mil_t[:6])) if bad else None, src)
    # O10 reading the title cards
    lents = [x for x in M["textes"] if x.get("mots") and (float(x["fin"]) - float(x["debut"])) / float(x["mots"]) < 0.3]
    if lents:
        R.add("O10", "Title card too short", "alerte", ", ".join("%d words in %s" % (int(x["mots"]), S_(float(x["fin"]) - float(x["debut"]))) for x in lents),
              "at least 0.3 s per word (median 0.5 s)", "7 title cards: 0.32 to 2.09 s per word", "hold the title card 0.5 s per word", "oeil")
    # O11 music: clear locking in 1 film out of 11 (photos)
    ctl_musique(R, M, "O11", "note", permis=(sf in ("hommage", "clip")))
    # O12 sound climax (openings and closings)
    son = M["son"]
    if sf in ("ouverture", "sketch", "cloture"):
        if son and son.get("sommet_10s"):
            pos = son["sommet_10s"]["position"]
            st = "ok" if pos >= 0.6 else "note"
            R.add("O12", "Sound climax", st, "at %s" % P_(pos), "after 60 %", "7 out of 8",
                  "build the music toward the end; the climax on the peak" if st != "ok" else None, "son")
        elif son is None:
            R.add("O12", "Sound climax", "non_mesure", "—", "after 60 %", "7 out of 8", "provide the sound (the render's track, or --son)", "—")
    # O13 speech up to the end
    pa = M["parole"]
    if pa is not None and pa["n"] and sf in ("ouverture", "sketch") and not ann.get("fiction_narree"):
        fb = pa["fin_avant_bout"]
        fmin = g(C, "parole.ouverture.fin_sans_parole_s.valeurs.0", 15.0)
        st = "ok" if fb >= fmin else ("alerte" if fb < 10 else "note")
        R.add("O13", "Ending without speech", st, "%s without speech at the end" % S_(fb), "15 to 33 s of music alone",
              "3 out of 3 films with speech (narrated fiction excluded)", "stop the speech 15 to 30 s before the end" if st != "ok" else None, "sous-titres")
        R.add("O13b", "Share of speech", "note" if pa["part"] > 0.30 else "ok", P_(pa["part"]), "30 % at most (narrated fiction excluded)", "7 out of 8", None, "sous-titres")
    # O15 lower thirds
    band = [x for x in M["textes"] if x.get("type") == "bandeau"]
    if band:
        tot = [x for x in band if float(x["debut"]) < D / 3]
        R.add("O15", "Name lower thirds", "alerte" if tot else "ok", "%d lower third(s) in the first third" % len(tot), "after the first third: show, then name", "7 out of 7",
              "name at the second appearance" if tot else None, "oeil")
    # O16, O17 transition between settings
    if sf == "transition_decor":
        lo, hi = g(C, "sous_familles.transition_decor.duree_s.cible.0", 15), g(C, "sous_familles.transition_decor.duree_s.cible.1", 30)
        R.add("O16a", "Transition duration", "ok" if lo <= D <= hi else "note", S_(D), "%d to %d s" % (lo, hi), "6 transitions from 11 to 31 s", None)
        if M["part_fixes"] is not None:
            fx = [p for p in img if p["fixe"] and p["duree"] >= 0.2]
            R.add("O16", "Static shots in the transition", "alerte" if fx else "ok", "%d" % len(fx), "none: one continuous forward move", "0 out of 33",
                  ("replace with moving shots: %s" % liste_tc(R, fx)) if fx else None)
        if der is not None:
            amin = g(C, "sous_familles.transition_decor.arrivee_tenue_avant_parole_s.min", 6.7)
            R.add("O17", "Held arrival", "alerte" if der["duree"] < 6 else ("ok" if der["duree"] >= amin else "note"), S_(der["duree"]),
                  "7 to 11.5 s before the speech (median 9.3 s)", "%s to 11.5 s (5 transitions)" % F(amin, 1),
                  "hold the arrival shot 7 to 11 s, then on under the first words" if der["duree"] < amin else None)
    if sf in ("ouverture", "sketch") and M["noir_ouverture"] == 0 and not M["seuil_carton"] and not froid:
        R.add("O1b", "Threshold", "note", "no black or title card before the first picture", "black 0.5 to 1.5 s, or title card then black", "6 out of 8 have a threshold",
              "add 0.5 to 1.5 s of black and silence at the start")


# ---------------------------------------------------------------- report

ORDRE = [("alerte", "What deviates"), ("note", "Notes (possible, but rare in the corpus)"),
         ("a_verifier", "To check by eye"), ("ok", "What matches"), ("non_mesure", "Not measured"), ("sans_objet", "Not applicable")]
SRC = {"calcul": "calculation", "declare": "declared in the timeline", "oeil": "annotation by eye", "sous-titres": "subtitles", "son": "sound", "—": "—"}


def rendu(R, M, meta, a, famille):
    D = M["duree"]
    al = R.n("alerte")
    verdict = "on target" if al == 0 else "deviates (%d alert%s)" % (al, "s" if al > 1 else "")
    L = []
    L.append("# Edit review: %s" % os.path.basename(meta["fichier"]))
    L.append("")
    L.append("Family: %s (%s). Source: %s. Verdict: **%s**." % (FAMILLES[famille], R.contexte,
             {"video": "rendered video", "xml": "FCP7 XML", "edl": "CMX3600 EDL"}[meta["source"]], verdict))
    L.append("")
    tr = M["transitions"]
    def pl(n, mot, mots=None):
        return "%d %s" % (n, mot if n == 1 else (mots or mot + "s"))
    L.append("Measured: duration %s; %s, %s, %s; median picture shot %s s (p10 %s, p90 %s); "
             "%s picture shots per minute; hard cuts %s; opening black %s." % (
                 S_(D), pl(M["n_img"], "picture shot", "picture shots"), pl(sum(1 for p in R._plans if p["kind"] == "noir"), "black"),
                 pl(len(M["cartons"]), "title card"), F(M["med"]), F(M["p10"]), F(M["p90"]), F(M["img_min"], 1), P_(M["coupes_part"]), S_(M["noir_ouverture"])))
    L.append("")
    L.append("Checks: %d that match, %s, %s, %d to check, %d not measured." % (
        R.n("ok"), pl(al, "alert"), pl(R.n("note"), "note"), R.n("a_verifier"), R.n("non_mesure")))
    for st, titre in ORDRE:
        xs = [c for c in R.c if c["statut"] == st]
        if not xs:
            continue
        L.append("")
        L.append("## %s (%d)" % (titre, len(xs)))
        L.append("")
        for c in xs:
            if st in ("ok", "sans_objet"):
                L.append("- **%s %s**: %s. Target: %s. Corpus: %s." % (c["id"], c["titre"], c["mesure"], c["cible"], c["base"]))
            elif st == "non_mesure":
                L.append("- **%s %s**: %s" % (c["id"], c["titre"], c["correctif"] or "—"))
            else:
                L.append("- **%s %s**: %s. Target: %s. Corpus: %s. Source: %s." % (c["id"], c["titre"], c["mesure"], c["cible"], c["base"], SRC.get(c["source"], c["source"])))
                if c["correctif"]:
                    L.append("  - Fix: %s." % c["correctif"].rstrip("."))
    L.append("")
    L.append("## Measured timeline")
    L.append("")
    L.append("| # | In | Duration | What | Incoming transition | Movement | Annotation |")
    L.append("|---|---|---|---|---|---|---|")
    for p in R._plans:
        tin = TIN_EN.get(p["tin"], p["tin"]) + (" (candidate)" if p["verif"] == "candidat" else "")
        an = ", ".join("%s=%s" % (k, v) for k, v in p["ann"].items()) if p["ann"] else ""
        if p["kind"] == "carton" and p.get("carton_src") == "calcul":
            an = (an + "; " if an else "") + "title card found by calculation"
        if p.get("textes"):
            an = (an + "; " if an else "") + "text: " + " / ".join(p["textes"])
        L.append("| %d | %s | %s | %s | %s | %s | %s |" % (p["n"], R.tc(p["debut"]), F(p["duree"]), KIND_EN.get(p["kind"], p["kind"]), tin,
                                                        "—" if p["mouvement"] is None else "%d" % p["mouvement"], an))
    L.append("")
    L.append("How to read: timecodes at %s fps from %s. \"candidate\" = dissolve found by calculation, to be confirmed. "
             "Thresholds and counts come from references/cibles/%s.json (N out of M = observed in N cases out of the M of the stated basis: films, shots, cuts...; convention = a choice of the skill)." % (
                 F(R.fps, 3).rstrip("0").rstrip(",."), mv.tc(0, R.fps, R.depart), famille))
    for w in meta.get("avertissements") or []:
        L.append("")
        L.append("Warning: %s." % w)
    return "\n".join(L) + "\n", verdict


def main(argv):
    ap = argparse.ArgumentParser(description="Reviews an edit against the keynote films of its family.")
    ap.add_argument("montage", help="rendered video, FCP7 XML or CMX3600 EDL")
    ap.add_argument("--famille", required=True)
    ap.add_argument("--sous-famille", default=None)
    ap.add_argument("--schema", choices=["tardif", "des_le_debut"], default=None, help="produit: late reveal (tardif) or object from the start (des_le_debut)")
    ap.add_argument("--debut", type=float, default=None, help="video: start of the film in the file (s)")
    ap.add_argument("--fin", type=float, default=None, help="video: end of the film in the file (s)")
    ap.add_argument("--sous-titres", default=None, help=".srt or .vtt (video file times; shifted by --debut)")
    ap.add_argument("--annotations", default=None, help="JSON of annotations made by eye")
    ap.add_argument("--son", default=None, help="sound file to measure (otherwise the render's track)")
    ap.add_argument("--son-debut", type=float, default=None, help="--son: position (s) in the sound file of the film's first frame (default 0)")
    ap.add_argument("--fps", type=float, default=None, help="EDL: timeline frame rate")
    ap.add_argument("--mesurer-medias", action="store_true", help="XML/EDL: measure movement and color in the source files")
    ap.add_argument("--cibles", default=CIBLES)
    ap.add_argument("--sortie", default=None, help="Markdown report (default: on screen)")
    ap.add_argument("--json", default=None, help="JSON report")
    ap.add_argument("--planche", default=None, help="video: contact sheet of the shots (JPEG)")
    ap.add_argument("--silencieux", action="store_true")
    a = ap.parse_args(argv)
    fam = ALIAS.get(a.famille.lower(), a.famille.lower())
    if fam not in FAMILLES:
        sys.stderr.write("unknown family: %s (produit, ouverture, documentaire, bandeannonce)\n" % a.famille)
        return 2
    if a.sous_famille and a.sous_famille not in SOUS[fam]:
        sys.stderr.write("unknown subfamily for %s: %s (%s)\n" % (fam, a.sous_famille, ", ".join(SOUS[fam])))
        return 2
    C = charger_cibles(fam, a.cibles)
    a._ann = {}
    if a.annotations:
        try:
            with open(a.annotations, encoding="utf-8") as fh:
                a._ann = json.load(fh)
        except OSError as ex:
            sys.stderr.write("unreadable annotations: %s: %s\n" % (a.annotations, ex.strerror or ex))
            return 2
        except ValueError as ex:
            sys.stderr.write("unreadable annotations: %s: invalid JSON (%s)\n" % (a.annotations, ex))
            return 2
        fautes = valider_annotations(a._ann)
        if fautes:
            sys.stderr.write("unreadable annotations: %s: %s\n" % (a.annotations, "; ".join(fautes)))
            return 2
    for opt, f in (("--sous-titres", a.sous_titres), ("--son", a.son)):
        if f and not os.path.isfile(f):
            sys.stderr.write("%s %s not found\n" % (opt, f))
            return 2
    ext = os.path.splitext(a.montage.rstrip("/"))[1].lower()
    try:
        if ext in (".xml", ".edl", ".xmeml", ".fcpxml", ".fcpxmld"):
            plans, meta = depuis_timeline(a.montage, a)
        else:
            plans, meta = depuis_video(a.montage, a)
    except Exception as ex:
        sys.stderr.write("cannot read: %s\n" % ex)
        return 2
    D = meta["duree"]
    appliquer_annotations(plans, a._ann, fam, D)
    subs = None
    if a.sous_titres:
        try:
            subs = mv.lire_sous_titres(a.sous_titres, a.debut or 0.0, (a.debut or 0.0) + D)
        except (OSError, ValueError, IndexError) as ex:
            sys.stderr.write("unreadable subtitles: %s: %s\n" % (a.sous_titres, ex))
            return 2
    son = None
    src_son = a.son or (a.montage if meta["source"] == "video" and (meta.get("info") or {}).get("audio") else None)
    if src_son:
        s0 = (a.debut or 0.0) if src_son == a.montage else (a.son_debut or 0.0)
        x = mv.lire_audio(src_son, s0, s0 + D)
        son = mv.analyse_son(x)
        if son is not None and son["part_silence_numerique"] >= 0.98:
            # silent track (a render without music often carries one): nothing to measure, not a random climax
            son = None
            if not a.silencieux:
                sys.stderr.write("silent sound track: the sound checks stay not measured\n")
    M = mesurer(plans, D, a._ann, subs, son)
    R = Rapport(meta["fps"], meta["depart"])
    R._plans = plans
    R._subs = subs
    R.meta = meta
    R.contexte = ""
    {"produit": controles_produit, "documentaire": controles_documentaire,
     "bandeannonce": controles_bandeannonce, "ouverture": controles_ouverture}[fam](R, M, C, a, a._ann)
    sus = [p for p in plans if p.get("suspect") and p["kind"] == "image"]
    if sus:
        R.add("V1", "Possibly missed transitions", "a_verifier",
              "%d shot(s) whose start and end no longer look alike" % len(sus), "—",
              "fade detection is a lower bound (corpus: 54 real out of 225 candidates, others missed)",
              "look at %s; a dissolve or a wipe seen by eye goes into annotations.ajouts" % liste_tc(R, sus))
    if not M["mouvement_mesure"]:
        if a.mesurer_medias and meta.get("hors_fichier"):
            pourquoi = ("source timecode outside the file for %d shot(s): the in-point read in the timeline is past the "
                        "file's duration, after subtracting the timecode written in it; check that the timeline points to the right files, "
                        "or review the rendered video" % meta["hors_fichier"])
        elif a.mesurer_medias:
            pourquoi = "source files not found or unreadable: review the rendered video"
        else:
            pourquoi = "timeline without pictures: run again with --mesurer-medias (source files present) or review the rendered video"
        R.add("MV", "Movement, still pictures, black and white", "non_mesure", "—", "—", "—", pourquoi, "—")
    txt, verdict = rendu(R, M, meta, a, fam)
    if a.planche and meta["source"] == "video":
        t0 = meta["t0"]
        imgs = mv.extraire_images(a.montage, [t0 + (p["debut"] + p["fin"]) / 2 for p in plans], 320, 180)
        leg = ["%d %s %s\n%s%s" % (p["n"], R.tc(p["debut"]), F(p["duree"]), KIND_EN.get(p["kind"], p["kind"]), " ?" if p["verif"] == "candidat" else "") for p in plans]
        cand = M["fondus_candidats"]
        for p in cand:
            for dt in (-0.4, -0.15, 0.0, 0.15, 0.4):
                imgs += mv.extraire_images(a.montage, [t0 + p["debut"] + dt], 320, 180)
                leg.append("dissolve? #%d %+.2f s" % (p["n"], dt))
        mv.planche(imgs, leg, a.planche, colonnes=6)
        txt += "\nContact sheet: %s\n" % os.path.abspath(a.planche)
    if a.sortie:
        with open(a.sortie, "w", encoding="utf-8") as fh:
            fh.write(txt)
    else:
        sys.stdout.write(txt)
    if a.json:
        out = {"fichier": meta["fichier"], "famille": fam, "contexte": R.contexte, "source": meta["source"],
               "verdict": verdict, "duree": round(D, 3), "fps": meta["fps"],
               "comptes": {k: R.n(k) for k in ("ok", "alerte", "note", "a_verifier", "non_mesure", "sans_objet")},
               "controles": R.c,
               "mesures": {"plans_image": M["n_img"], "plan_median": M["med"], "p10": M["p10"], "p90": M["p90"],
                           "tiers": M["tiers"], "plans_image_par_minute": M["img_min"], "changements_par_minute": M["chg_min"],
                           "noir_ouverture": M["noir_ouverture"], "noir_fin": M["noir_fin"],
                           "noirs_internes": [[p["debut"], p["duree"]] for p in M["noirs_internes"]],
                           "transitions": M["transitions"], "part_coupes": M["coupes_part"],
                           "part_fixes": M["part_fixes"], "part_nb": M["part_nb"], "pic_5_plans": M["pic5"], "pic_10s": M["pic10"],
                           "parole": {k: v for k, v in (M["parole"] or {}).items() if k != "intervalles"} or None,
                           "son": {k: v for k, v in (M["son"] or {}).items() if k not in ("attaques", "courbe_db_par_0_5s")} or None,
                           "coupes_sur_son": M["sur_son"]},
               "plans": [{k: v for k, v in p.items() if not k.startswith("_")} for p in plans]}
        with open(a.json, "w", encoding="utf-8") as fh:
            json.dump(out, fh, ensure_ascii=False, indent=1, default=lambda o: o if not isinstance(o, (np.floating, np.integer)) else o.item())
    return 0 if R.n("alerte") == 0 else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
