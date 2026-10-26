#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
critique_montage.py : mesure un montage et le compare aux films des keynotes de sa famille.
Python 3.9 + numpy + Pillow ; ffmpeg et ffprobe dans le PATH.

    python3 critique_montage.py MONTAGE --famille produit|ouverture|documentaire|bandeannonce
            [--sous-famille X] [--debut S --fin S] [--sous-titres F.srt|F.vtt]
            [--annotations A.json] [--son FICHIER] [--fps N] [--mesurer-medias]
            [--cibles DOSSIER] [--sortie rapport.md] [--json rapport.json] [--planche image.jpg]

MONTAGE : un fichier vidéo (rendu), un XML FCP7 (xmeml, export Premiere Pro ou DaVinci Resolve)
ou une EDL CMX3600. Le rapport dit ce qui colle, ce qui s'écarte (alertes), les notes (possible
mais rare), ce qu'il faut regarder à l'œil, et des correctifs avec timecodes.

Sources des mesures :
  - calcul : découpage de la vidéo (mêmes seuils que le corpus) ; les fondus (enchaînés, au noir,
    au blanc) trouvés au calcul sont des CANDIDATS (sur le corpus, 54 vrais sur 225) : ils restent « à vérifier »
    tant qu'une annotation ne les confirme pas ;
  - déclaré : transitions, textes et noirs lus dans le XML ou l'EDL ;
  - œil : annotations (valeurs de plan, textes, révélation, nom…) écrites après avoir regardé la planche ;
  - sous-titres : parole (bornes hautes) ; son : niveau, attaques, tempo (voix et musique mêlées).
Verdict : « conforme » = aucune alerte. Code de sortie : 0 conforme, 1 écarts, 2 erreur.
"""
import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import mesure_video as mv  # noqa: E402  (avant numpy : dit quoi faire s'il manque)
import numpy as np  # noqa: E402
import lire_timeline as lt  # noqa: E402

ICI = os.path.dirname(os.path.abspath(__file__))
CIBLES = os.path.join(os.path.dirname(ICI), "references", "cibles")

FAMILLES = {"produit": "produit et révélation", "ouverture": "ouverture et ambiance",
            "documentaire": "documentaire et témoignage", "bandeannonce": "bande-annonce et usage"}
ALIAS = {"produit_revelation": "produit", "revelation": "produit", "ouverture_ambiance": "ouverture",
         "ambiance": "ouverture", "documentaire_temoignage": "documentaire", "temoignage": "documentaire",
         "bande_annonce_usage": "bandeannonce", "bande-annonce": "bandeannonce", "bande_annonce": "bandeannonce",
         "usage": "bandeannonce", "trailer": "bandeannonce"}
SOUS = {"produit": ["revelation_objet", "logiciel", "materiaux_voix_off", "usage_gamme"],
        "ouverture": ["ouverture", "sketch", "cloture", "hommage", "transition_decor", "clip"],
        "documentaire": ["pose", "choral"],
        "bandeannonce": ["oeuvre", "catalogue_par_blocs", "catalogue_mele", "usage"]}

# valeurs de plan (annotations) : vocabulaire commun et codes des analyses
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


# ---------------------------------------------------------------- outils

def charger_cibles(famille, dossier):
    p = os.path.join(dossier, famille + ".json")
    if not os.path.exists(p):
        raise SystemExit("cibles introuvables : %s" % p)
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


# ---------------------------------------------------------------- lecture du montage

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
        # plan d'au moins 1 s dont l'image du début et celle de la fin n'ont plus rien en commun :
        # fondu ou volet peut-être manqué (le calcul des fondus est une borne basse)
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
    # cartons probables : image du milieu de chaque plan non noir
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
            # EDL : le timecode source part du timecode inscrit dans le fichier ; on le retranche
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
                sys.stderr.write("média non mesuré (%s) : %s\n" % (f, ex))
    meta = {"source": t["source"], "fichier": os.path.abspath(path), "fps": t["fps"], "depart": t["depart"], "t0": 0.0,
            "duree": t["duree"], "textes": t["textes"], "audio": t["audio"], "avertissements": t["avertissements"],
            "hors_fichier": len(hors)}
    if hors:
        sys.stderr.write("timecode source hors du fichier, plan(s) non mesuré(s) : %s\n" % ", ".join(
            "%s à %.2f s" % (os.path.basename(p["fichier"]), p["debut"]) for p in hors))
    return plans, meta


def valider_annotations(ann):
    """Les fautes de forme d'un fichier d'annotations écrit à la main (critique.md § 5), une par endroit."""
    def num(v):
        return isinstance(v, (int, float)) and not isinstance(v, bool)

    def lu(v):
        return json.dumps(v, ensure_ascii=False)[:40]

    if not isinstance(ann, dict):
        return ["un objet JSON {…} attendu"]
    F = []
    for k in ("revelation", "fermeture"):
        if ann.get(k) is not None and not num(ann[k]):
            F.append("%s : un nombre de secondes attendu (point décimal), lu %s" % (k, lu(ann[k])))
    for k in ("codes", "sous_famille", "schema"):
        if ann.get(k) is not None and not isinstance(ann[k], str):
            F.append("%s : un texte attendu, lu %s" % (k, lu(ann[k])))
    nom = ann.get("nom")
    if nom is not None:
        if isinstance(nom, list):
            if len(nom) != 2 or not all(num(x) for x in nom):
                F.append("nom : [début, fin] en secondes attendu, lu %s" % lu(nom))
        elif isinstance(nom, dict):
            if ("debut" in nom or "fin" in nom) and not (num(nom.get("debut")) and num(nom.get("fin"))):
                F.append("nom : « debut » et « fin » en secondes attendus, lu %s" % lu(nom))
            elif "debut" not in nom and not isinstance(nom.get("type"), str):
                F.append("nom : [début, fin] ou {\"type\": \"dit_par_orateur\"} attendu, lu %s" % lu(nom))
        else:
            F.append("nom : [début, fin] ou {\"type\": \"dit_par_orateur\"} attendu, lu %s" % lu(nom))
    plans = ann.get("plans")
    if plans is not None:
        if not isinstance(plans, dict):
            F.append("plans : un objet {\"n° de plan\": {\"valeur\", \"type\"}} attendu")
        else:
            for k, v in plans.items():
                if not isinstance(v, dict):
                    F.append("plans[%s] : un objet {\"valeur\", \"type\"} attendu, lu %s" % (k, lu(v)))
    for cle, champs in (("plans_par_temps", ("t",)), ("textes", ("debut", "fin")), ("ajouts", ("t",))):
        L = ann.get(cle)
        if L is None:
            continue
        if not isinstance(L, list):
            F.append("%s : une liste attendue" % cle)
            continue
        for i, x in enumerate(L):
            if not isinstance(x, dict):
                F.append("%s[%d] : un objet attendu, lu %s" % (cle, i, lu(x)))
                continue
            for c in champs:
                if c not in x:
                    F.append("%s[%d] sans « %s »" % (cle, i, c))
                elif not num(x[c]):
                    F.append("%s[%d].%s : un nombre de secondes attendu (point décimal), lu %s" % (cle, i, c, lu(x[c])))
            if x.get("mots") is not None and not num(x["mots"]):
                F.append("%s[%d].mots : un nombre attendu, lu %s" % (cle, i, lu(x["mots"])))
            if cle == "ajouts" and not isinstance(x.get("type"), str):
                F.append("ajouts[%d] sans « type » (fondu_enchaine, volet, fondu_au_noir…)" % i)
    tr = ann.get("transitions")
    if tr is not None:
        if not isinstance(tr, dict):
            F.append("transitions : un objet {\"temps en s\": \"T|F|C|U|B\"} attendu")
        else:
            for k, v in tr.items():
                try:
                    float(k)
                except ValueError:
                    F.append("transitions : clé « %s » : un temps en secondes attendu (point décimal)" % k)
                if not isinstance(v, str):
                    F.append("transitions[%s] : T, F, C, U ou B attendu, lu %s" % (k, lu(v)))
    return F


def appliquer_annotations(plans, ann, famille, D):
    """Annotations à l'œil : par numéro de plan, par temps, ou chaîne de codes."""
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
            # deux relevés dans un même plan : l'image l'emporte, le texte est intégré à l'image
            if d["valeur"] == "texte" and p["ann"].get("valeur") in VALEURS:
                p["ann"]["texte_integre"] = True
                p["textes"] = p.get("textes") or []
                return
            if d["valeur"] in VALEURS and p["ann"].get("valeur") == "texte":
                d["texte_integre"] = True
        if d.get("valeur") in VALEURS and p["kind"] in ("carton", "noir", "blanc"):
            p["kind"] = "image"          # l'œil l'emporte sur le calcul
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
            sys.stderr.write("annotations : %d codes pour %d plans, appliqués dans l'ordre sur les premiers\n" % (len(toks), len(plans)))
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


# ---------------------------------------------------------------- mesures

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
    # noir interne : un noir qui a un plan d'image avant et après lui (ni l'ouverture, ni la fin, ni avant un carton final)
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
    # passage le plus rapide : 5 plans d'image consécutifs
    M["pic5"] = None
    if len(img) >= 5:
        best = None
        for k in range(len(img) - 4):
            w = img[k:k + 5]
            m = float(np.median([x["duree"] for x in w]))
            tot = sum(x["duree"] for x in w)
            # à médiane égale, la fenêtre la plus courte : sinon un plan long (le premier plan) entre dans le pic
            if best is None or (m, tot) < (best[0], best[2]):
                best = (m, w, tot)
        m, w, _ = best
        M["pic5"] = {"mediane": m, "debut": w[0]["debut"], "fin": w[-1]["fin"], "debut_rel": w[0]["debut"] / D,
                     "milieu_rel": ((w[0]["debut"] + w[-1]["fin"]) / 2) / D, "plans": [x["n"] for x in w]}
    # 10 s les plus rapides (définition des bandes-annonces)
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
            # médiane la plus basse ; à une image près (1/29,97 s), la fenêtre qui a le plus de plans
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
    # parole
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
    s = ", ".join("n° %d à %s" % (p["n"], R.at(p["debut"])) for p in plans[:n])
    return s + (" (et %d autres)" % (len(plans) - n) if len(plans) > n else "")


def plage(R, D, a, b):
    return "entre %s et %s" % (R.at(a * D), R.at(b * D))


# ---------------------------------------------------------------- contrôles communs

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
        R.add(id_, "Fondus enchaînés", "alerte", "%d fondus enchaînés (%s des transitions)" % (n, P_(part)),
              "au plus %s, %s des transitions" % (max_n, P_(max_part)), base,
              "remplacer par des coupes franches : %s%s" % (liste_tc(R, conf), permis),
              "declare" if any(p["verif"] == "declare" for p in conf) else "oeil")
    elif cand:
        R.add(id_, "Fondus enchaînés", "a_verifier", "%d fondus enchaînés candidats au calcul" % len(cand),
              "au plus %s" % max_n, base + " ; au calcul, 54 vrais fondus sur 225 candidats dans le corpus",
              "regarder %s ; confirmer (T) ou rejeter (F) dans annotations.transitions" % liste_tc(R, cand))
    else:
        R.add(id_, "Fondus enchaînés", "ok", "%d fondu enchaîné" % n if n <= 1 else "%d fondus" % n,
              "au plus %s" % max_n, base)


def ctl_parole_absente(R, id_, titre, besoin):
    R.add(id_, titre, "non_mesure", "—", "—", "—", besoin, "—")


# ---------------------------------------------------------------- famille produit

def controles_produit(R, M, C, a, ann):
    D = M["duree"]
    img = M["img"]
    sf = a.sous_famille or ann.get("sous_famille") or "revelation_objet"
    schema = a.schema or ann.get("schema")
    if not schema:
        schema = "tardif" if sf in ("revelation_objet", "materiaux_voix_off") else ("des_le_debut" if sf == "usage_gamme" else None)
    R.contexte = "sous-famille %s ; schéma %s" % (sf, {"tardif": "révélation tardive", "des_le_debut": "objet dès le début", None: "non précisé"}[schema])
    plan_seq = len(img) <= 5 and D >= 30
    voix = M["parole"] is not None and M["parole"]["part"] >= 0.2
    # C2 durée
    if voix:
        lo, hi = g(C, "corpus.duree_s.materiaux_voix_off.min", 53.57), g(C, "corpus.duree_s.materiaux_voix_off.max", 127.55)
    else:
        lo, hi = g(C, "corpus.duree_s.sans_voix_off.min", 24.09), g(C, "corpus.duree_s.sans_voix_off.max", 51.0)
    R.add("C2", "Durée du film", "ok" if lo - 1 <= D <= hi + 1 else "note", S_(D),
          "%s à %s %s" % (S_(lo), S_(hi), "(voix off)" if voix else "(sans voix)"),
          "13 films sans voix de 24 à 51 s ; 3 films à voix off de 54 à 128 s",
          None if lo - 1 <= D <= hi + 1 else ("couper vers %s (médiane du corpus sans voix)" % S_(g(C, "corpus.duree_s.sans_voix_off.mediane", 31.9)) if D > hi else "le film est court : vérifier qu'il a ses cinq temps"))
    # C3 ouverture sur le noir
    nb_o = M["noir_ouverture"]
    if nb_o == 0:
        R.add("C3", "Ouvrir sur le noir", "note", "le film commence sur une image", "noir de 0,3 à 1,6 s, puis l'image naît",
              "observé 13 sur 16 (noir), 8 sur 16 (naissance par la lumière ou un fondu)",
              "ajouter 0,3 à 1,6 s de noir avant %s, puis un fondu depuis le noir de 0,7 à 1,3 s" % R.at(M["premiere_image_t"] or 0))
    elif nb_o > 1.6:
        R.add("C3", "Ouvrir sur le noir", "note", "noir d'ouverture de %s" % S_(nb_o), "0,3 à 1,6 s (9 sur 13)",
              "noirs longs : 4 sur 13, dont 3 d'une même keynote en salle", "raccourcir le noir d'ouverture vers 1 s")
    else:
        R.add("C3", "Ouvrir sur le noir", "ok", "noir de %s" % S_(nb_o), "0,3 à 1,6 s", "observé 13 sur 16")
    # K1 révélation
    rev = ann.get("revelation")
    if schema == "tardif":
        if rev is not None:
            r = float(rev) / D
            lo, hi = g(C, "structure.3.position.min", 0.69), g(C, "structure.3.position.max", 0.82)
            if r < 0.60:
                R.add("K1", "Place de la révélation", "alerte", "objet entier à %s de la durée (%s)" % (P_(r), R.at(float(rev))),
                      "%s à %s (médiane 77 %%)" % (P_(lo), P_(hi)), "10 films sur 10 après 69 %",
                      "repousser la révélation %s : allonger la montée par des détails" % plage(R, D, lo, hi), "oeil")
            else:
                R.add("K1", "Place de la révélation", "ok" if lo - 0.03 <= r <= hi + 0.05 else "note", "à %s de la durée" % P_(r),
                      "%s à %s" % (P_(lo), P_(hi)), "10 films sur 10 entre 69 et 82 %", None, "oeil")
        else:
            cands = [p for p in img if p["rel0"] >= 0.6]
            c = max(cands, key=lambda p: p["duree"]) if cands else None
            R.add("K1", "Place de la révélation", "a_verifier", "non annotée" + (" ; candidat : plan n° %d à %s (%s, le plus long après 60 %%)" % (c["n"], R.at(c["debut"]), S_(c["duree"])) if c else ""),
                  "69 à 82 % de la durée", "10 films sur 10", "donner « revelation » (en s) dans les annotations")
    else:
        R.add("K1", "Place de la révélation", "sans_objet", "schéma « objet dès le début »", "objet entier entre 1 et 18 %", "5 films sur 16")
    # K2 premier plan
    if M["premier"] is not None:
        v = M["premier"]["ann"].get("valeur")
        if schema == "tardif":
            if v is None:
                R.add("K2", "Premier plan d'image", "a_verifier", "valeur non annotée (plan n° %d)" % M["premier"]["n"],
                      "un monde (décor, paysage) ou une matière ; jamais l'objet entier", "0 sur 10 objet entier", None)
            elif v == "entier":
                R.add("K2", "Premier plan d'image", "alerte", "l'objet entier dès le premier plan (%s)" % R.at(M["premier"]["debut"]),
                      "un décor, un paysage ou une matière", "0 sur 10 en révélation tardive",
                      "ouvrir sur un décor ou une matière (un détail en lumière rasante) et garder l'objet entier pour la révélation", "oeil")
            else:
                R.add("K2", "Premier plan d'image", "ok", "premier plan : %s" % v, "décor, paysage ou matière", "10 sur 10", None, "oeil")
        q1 = g(C, "durees.premier_plan_image.quartiles.0", 2.32)
        R.add("C4", "Durée du premier plan d'image", "ok" if M["premier"]["duree"] >= q1 else "note", S_(M["premier"]["duree"]),
              "médiane 3,3 s (quartiles 2,3 et 7,9 s)", "16 films ; plus court que %s s dans 1 film sur 4" % F(q1, 1),
              None if M["premier"]["duree"] >= q1 else "tenir le premier plan 2,5 à 4 s : il installe le monde")
    # K3 plan médian
    if M["med"] is not None:
        lo, hi = g(C, "durees.mediane_par_film.films_qui_coupent.min", 1.0), g(C, "durees.mediane_par_film.films_qui_coupent.max", 3.6)
        if lo - 1.0 / mv.FPS <= M["med"] <= hi + 1.0 / mv.FPS:
            R.add("K3", "Plan d'image médian", "ok", "%s s" % F(M["med"]),
                  "%s à %s s" % (F(lo, 1), F(hi, 1)), "14 films qui coupent : 1,0 à 3,6 s")
        else:
            st = "note" if plan_seq else "alerte"
            courts = sorted([p for p in img if p["duree"] < 0.8], key=lambda p: p["debut"])
            longs = sorted([p for p in img if p["duree"] > 5], key=lambda p: p["debut"])
            cor = ("trop haché : allonger ou regrouper les plans courts (%s) ; viser 2 à 2,5 s pour la montée" % liste_tc(R, courts)) if M["med"] < lo \
                else ("trop lent : couper les plans d'image longs hors révélation et plan final (%s)" % liste_tc(R, longs))
            R.add("K3", "Plan d'image médian", st, "%s s" % F(M["med"]), "%s à %s s" % (F(lo, 1), F(hi, 1)),
                  "14 films qui coupent : 1,0 à 3,6 s" + (" ; plan-séquence : 2 films sur 16" if plan_seq else ""), cor)
    # K4 cadence
    if M["img_min"] is not None:
        lo, hi = g(C, "durees.plans_image_par_minute.films_qui_coupent.min", 13.17), g(C, "durees.plans_image_par_minute.films_qui_coupent.max", 32.42)
        tol = 60.0 / D          # un plan de plus ou de moins
        ok = lo - tol <= M["img_min"] <= hi + tol
        R.add("K4", "Plans d'image par minute", "ok" if ok else ("note" if plan_seq else "alerte"), F(M["img_min"], 1),
              "%s à %s" % (F(lo, 1), F(hi, 1)), "14 films qui coupent",
              None if ok else ("moins de plans : supprimer ou fusionner %d plans" % max(1, round(M["n_img"] - hi * D / 60)) if M["img_min"] > hi
                               else "plus de plans : découper la montée en détails de 1,2 à 3,5 s"))
    # K5 plus long plan
    pl = M["plus_long"]
    if pl is not None:
        if pl["duree"] >= 5:
            R.add("K5", "Un plan d'au moins 5 s", "ok", "plan n° %d : %s" % (pl["n"], S_(pl["duree"])), "au moins 5 s (médiane 8,1 s)", "14 sur 16")
        else:
            R.add("K5", "Un plan d'au moins 5 s", "note", "le plus long dure %s (plan n° %d à %s)" % (S_(pl["duree"]), pl["n"], R.at(pl["debut"])),
                  "au moins 5 s ; le plus long 8,1 s en médiane", "14 films sur 16 ; 2 logiciels montés vite n'en ont pas",
                  "tenir la révélation ou le dernier plan 5 à 9 s (le reprendre plus long dans le rush) ; candidat : plan n° %d à %s" % (M["dernier"]["n"], R.at(M["dernier"]["debut"])))
    # K6 dernier plan d'image
    der = M["dernier"]
    if der is not None:
        # seul un nom écrit après le dernier plan d'image compte (pas un nom posé plus tôt, ni dit par l'orateur)
        nom_a = ann.get("nom")
        t_nom = (float(nom_a[0]) if isinstance(nom_a, (list, tuple)) and len(nom_a) == 2 else
                 float(nom_a["debut"]) if isinstance(nom_a, dict) and "debut" in nom_a else None)
        nom_ann = t_nom is not None and t_nom >= der["fin"] - 0.05
        if M["textes"]:
            nom_apres = nom_ann or any(x.get("type") == "nom" and float(x.get("debut", 0)) >= der["fin"] - 0.05 for x in M["textes"])
        else:
            nom_apres = nom_ann or any(p["debut"] >= der["fin"] - 0.05 for p in M["cartons"])
        if der["duree"] >= 4:
            R.add("K6", "Dernier plan d'image tenu", "ok", S_(der["duree"]), "au moins 4 s (médiane 7,4 s)", "13 sur 16")
        elif nom_apres and (M["textes"] or nom_ann):
            R.add("K6", "Dernier plan d'image tenu", "ok", "%s, puis le nom" % S_(der["duree"]), "au moins 4 s, ou finir sur le nom", "3 sur 16 finissent ainsi", None, "oeil")
        elif nom_apres:
            R.add("K6", "Dernier plan d'image tenu", "a_verifier", "%s, puis un carton : est-ce le nom ?" % S_(der["duree"]), "au moins 4 s, ou finir sur le nom",
                  "13 sur 16 au moins 4 s ; les 3 autres finissent sur le nom",
                  "si le carton n'est pas le nom : tenir le dernier plan (n° %d) 6 à 8,5 s ; typer les textes dans les annotations" % der["n"])
        else:
            R.add("K6", "Dernier plan d'image tenu", "alerte", "%s (plan n° %d à %s)" % (S_(der["duree"]), der["n"], R.at(der["debut"])),
                  "au moins 4 s (6 à 8,5 s en quartiles), ou finir sur le nom", "13 sur 16 au moins 4 s ; les 3 autres finissent sur le nom",
                  "tenir le dernier plan (n° %d, à %s) 6 à 8,5 s au lieu de %s, l'objet entier ; ou finir sur le nom" % (der["n"], R.at(der["debut"]), S_(der["duree"])))
    # K7 fondus enchaînés
    ctl_fondus(R, M, "K7", 1, 0.10, "3 % des transitions ; jamais 2 vus à l'œil dans un film",
               " ; garder au plus un fondu, pour entrer dans un plan clé (le nom)")
    # K8 fondu depuis le noir au dernier tiers
    fdn = [p for p in R._plans if p["tin"] == "fondu_depuis_noir" and p["rel0"] >= 2 / 3]
    R.add("K8", "Fondu depuis le noir au dernier tiers", "note" if fdn else "ok", "%d" % len(fdn), "aucun", "0 sur 10",
          ("le noir qui s'ouvre appartient au début : couper franc en %s" % liste_tc(R, fdn)) if fdn else None)
    # K9 serrer
    vals = [p for p in img if p["rel"] < 2 / 3 and p["ann"].get("valeur") in VALEURS]
    if schema == "tardif":
        if len(vals) >= 3:
            part = sum(1 for p in vals if p["ann"]["valeur"] in PROCHE) / len(vals)
            R.add("K9", "Détails et plans serrés (deux premiers tiers)", "ok" if part >= 0.5 else "note", P_(part),
                  "65 à 70 % ; au moins 50 %", "70 % puis 65 % sur 141 plans ; 7 films à révélation tardive sur 10 au-dessus de 50 %",
                  None if part >= 0.5 else "remplacer des plans larges de la montée par des détails de l'objet (matière, pièces)", "oeil")
        else:
            R.add("K9", "Détails et plans serrés (deux premiers tiers)", "a_verifier", "valeurs non annotées", "65 à 70 %", "observé", None)
    # K10 élargir à la fin
    if der is not None:
        v = der["ann"].get("valeur")
        if v is None:
            R.add("K10", "Dernier plan : l'objet entier", "a_verifier", "valeur non annotée (plan n° %d)" % der["n"], "objet entier ou large", "14 sur 16", None)
        else:
            ok = v in ENTIER_LARGE
            R.add("K10", "Dernier plan : l'objet entier", "ok" if ok else "note", v, "objet entier ou large", "14 sur 16 ; 2 finissent serré ou abstrait",
                  None if ok else "finir sur l'objet entier, tenu (recul ou rotation lente)", "oeil")
    # K11 nom
    nom = ann.get("nom")
    if isinstance(nom, dict) and nom.get("type") in ("dit_par_orateur", "orateur", "aucun_orateur_le_dit"):
        R.add("K11", "Le nom", "sans_objet", "dit par l'orateur après le film", "—", "8 sur 16 dans les keynotes")
    else:
        if isinstance(nom, (list, tuple)) and len(nom) == 2:
            t0n, t1n, src = float(nom[0]), float(nom[1]), "oeil"
        elif isinstance(nom, dict) and "debut" in nom:
            t0n, t1n, src = float(nom["debut"]), float(nom["fin"]), "oeil"
        elif M["textes"]:
            # textes relevés à l'œil : seul un texte de type « nom » compte
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
            R.add("C16", "Écrire le nom (sans orateur)", "note", "aucun nom écrit trouvé", "le nom seul, centré, à 83-96 %, 1,3 à 4,5 s",
                  "convention (dans les keynotes, l'orateur le dit : 8 sur 8)",
                  "ajouter le nom %s, pendant 2,4 s environ" % plage(R, D, 0.83, 0.96))
        else:
            r, dn = t0n / D, t1n - t0n
            lo, hi = g(C, "cartons.nom.position.min", 0.83), g(C, "cartons.nom.position.max", 0.96)
            bad = r < lo - 0.02 or dn < 1.25
            st = ("alerte" if bad else "ok") if src == "oeil" else "a_verifier"
            R.add("K11", "Place et durée du nom", st, "à %s, %s%s" % (P_(r), S_(dn), "" if src != "calcul" else " (carton trouvé au calcul)"),
                  "%s à %s ; 1,3 à 4,5 s" % (P_(lo), P_(hi)), "7 sur 7 noms écrits",
                  ("placer le nom %s et le tenir 2,4 s environ" % plage(R, D, lo, hi)) if bad else
                  (None if src == "oeil" else "dire dans les annotations si ce dernier carton est le nom (textes, type « nom »)"), src)
    # K12 texte en trop
    types = [x.get("type") for x in M["textes"]]
    n_txt = len(M["cartons"]) + sum(1 for x in M["textes"] if x.get("type") not in ("nom",) and not x.get("sur_carton"))
    interdits = [x for x in M["textes"] if x.get("type") in ("chiffre", "explicatif", "slogan", "date")]
    phrases = [x for x in M["textes"] if x.get("type") == "phrase"]
    src = "oeil" if M["textes"] else ("declare" if any(p["carton_src"] == "declare" for p in M["cartons"]) else "calcul")
    if interdits or len(phrases) > 1:
        R.add("K12", "Texte en trop", "alerte", "%d texte(s) interdit(s) (%s), %d phrase(s)" % (len(interdits), ", ".join(sorted(set(x["type"] for x in interdits))) or "—", len(phrases)),
              "aucun carton chiffré ou explicatif ; au plus une phrase de 5 mots", "0 sur 16 ; une phrase dans 1 film sur 16",
              "retirer : " + ", ".join("%s à %s" % (x.get("type"), R.at(float(x.get("debut", 0)))) for x in interdits + phrases[1:]), "oeil")
    elif len(M["cartons"]) > 2:
        st = "alerte" if src in ("declare", "oeil") else "a_verifier"
        R.add("K12", "Texte en trop", st, "%d cartons" % len(M["cartons"]), "au plus 2 textes (le nom, une phrase ou un bandeau)",
              "aucun film n'a plus de 2 textes (16 films)",
              "garder le nom à la fin ; retirer %s" % liste_tc(R, M["cartons"][:-1]), src)
    else:
        R.add("K12", "Texte en trop", "ok", "%d carton(s)" % len(M["cartons"]), "au plus 2 textes", "16 films", None, src)
    # K13 logo, date, slogan en fin
    fin_t = [x for x in M["textes"] if x.get("type") in ("logo", "slogan", "date") and float(x.get("debut", 0)) >= 0.8 * D]
    if fin_t:
        R.add("K13", "Logo, date ou slogan en fin", "alerte", ", ".join(x["type"] for x in fin_t), "finir sur l'objet, ou le nom puis un noir",
              "0 sur 16", "remplacer par le nom seul, puis un noir court (0,1 à 2,8 s)", "oeil")
    elif M["cartons"] and M["cartons"][-1]["rel0"] >= 0.8 and not ann.get("nom") and not M["textes"]:
        R.add("K13", "Logo, date ou slogan en fin", "a_verifier", "un carton ferme le film (%s) : le nom, ou un logo ?" % R.at(M["cartons"][-1]["debut"]),
              "le nom ; jamais un logo seul", "0 sur 16 logo seul", None)
    # K14 noirs internes
    ni = M["noirs_internes"]
    R.add("K14", "Noirs internes", "note" if len(ni) > 2 else "ok", "%d" % len(ni), "au plus 2, de 0,3 à 0,9 s", "4 films sur 16 en ont ; 1 en a 6 (chapitres)",
          ("supprimer les noirs %s, sauf s'ils découpent des chapitres" % liste_tc(R, ni)) if len(ni) > 2 else None)
    # K15 images fixes
    if M["part_fixes"] is not None:
        R.add("K15", "Images fixes", "note" if M["part_fixes"] > 0.25 else "ok", P_(M["part_fixes"]), "7 % (au plus 25 %)", "197 plans",
              "faire bouger l'image : rotation lente, avancée ou recul sur les plans fixes" if M["part_fixes"] > 0.25 else None)
    # K16 voix off
    pa = M["parole"]
    if pa is not None and pa["n"]:
        bad = []
        if pa["part"] > 0.75:
            bad.append("voix sur %s du temps (cible 61 à 69 %%)" % P_(pa["part"]))
        if pa["premiere"] < 3.0:
            bad.append("la voix commence à %s (cible 3,9 à 4,6 s)" % S_(pa["premiere"]))
        if pa["fin_avant_bout"] < 2.0:
            bad.append("la voix finit %s avant la fin (cible 2,3 à 3,6 s)" % S_(pa["fin_avant_bout"]))
        R.add("K16", "Voix off", "alerte" if bad else "ok", "; ".join(bad) or "%s du temps, de %s à %s avant la fin" % (P_(pa["part"]), S_(pa["premiere"]), S_(pa["fin_avant_bout"])),
              "61 à 69 % ; muette 3,9 à 4,6 s au début et 2,3 à 3,6 s à la fin", "3 films sur 3 à voix off",
              "laisser le début et la fin muets, couper des phrases" if bad else None, "sous-titres")
    # K18 durée sans voix
    if D > 60 and not voix:
        R.add("K18", "Film sans voix de plus de 60 s", "note", S_(D), "24 à 51 s, ou des chapitres", "13 sur 13 films sans voix",
              "découper en chapitres de 15 à 30 s (convention) ou raccourcir")
    # K19 noir et blanc
    if M["part_nb"] is not None:
        R.add("K19", "Noir et blanc", "note" if M["part_nb"] > 0.5 else "ok", "%s des plans désaturés" % P_(M["part_nb"]), "couleur",
              "0 sur 16 en noir et blanc désaturé", "garder la couleur sur un film produit" if M["part_nb"] > 0.5 else None)
    ctl_musique(R, M, "K20", "note")


def ctl_musique(R, M, id_, niveau, permis=False):
    ss = M.get("sur_son")
    if ss is None:
        R.add(id_, "Coupes calées sur chaque temps", "non_mesure", "—", "les grands changements sur la musique, pas chaque coupe",
              "convention (calage non démontré dans le corpus)", "fournir le son (piste du rendu, ou --son)", "—")
        return
    n = ss["coupes"]
    st_t = ss.get("sur_temps")
    grille = st_t is not None and n >= 6 and st_t >= 0.6 * n and st_t >= 2 * ss.get("attendu_temps", 0)
    att = n >= 6 and ss["sur_attaque"] >= 0.6 * n and ss["sur_attaque"] >= 2 * ss["attendu_hasard"]
    mes = "%d coupes sur %d à ± 70 ms d'une attaque (hasard %s)" % (ss["sur_attaque"], n, F(ss["attendu_hasard"], 1))
    if st_t is not None:
        mes += " ; %d sur la grille du tempo (hasard %s)" % (st_t, F(ss["attendu_temps"], 1))
    if (grille or att) and not permis:
        R.add(id_, "Coupes calées sur chaque temps", niveau, mes, "caler la sortie du noir, la révélation, le pic, le nom ; pas chaque coupe",
              "calage non démontré dans le corpus (16 sur 62 contre 16,4 au hasard) ; net dans 1 film sur 11 (photos)",
              "décaler une coupe sur deux hors du temps ; garder les temps forts pour les grands changements", "son")
    else:
        R.add(id_, "Coupes calées sur chaque temps", "ok", mes, "pas de calage mécanique", "convention", None, "son")


# ---------------------------------------------------------------- famille documentaire

def controles_documentaire(R, M, C, a, ann):
    D = M["duree"]
    img = M["img"]
    sf = a.sous_famille or ann.get("sous_famille")
    deduit = False
    if sf not in ("pose", "choral"):
        sf = "choral" if (M["med"] or 2) < 1.5 else "pose"
        deduit = True
    R.contexte = "régime %s%s" % (sf, " (déduit du plan médian)" if deduit else "")
    ctl = {c["id"]: c for c in C.get("controles", [])}
    pa = M["parole"]
    # D1
    if M["med"] is not None:
        if sf == "pose":
            bad = M["med"] < 1.5 or M["med"] > 2.8
            cib = "1,8 à 2,2 s"
        else:
            bad = M["med"] > 1.8
            cib = "1,0 à 1,5 s"
        R.add("D1", "Plan médian", "alerte" if bad else "ok", "%s s" % F(M["med"]), cib, g(ctl, "D1.statut", "observé"),
              None if not bad else ("raccourcir les illustrations ; couper les entretiens sous la voix" if M["med"] > 2 else "laisser durer les plans : moins de coupes dans les entretiens"))
    # D2
    cpm = M["chg_min"]
    bad = cpm < 18 or cpm > 48
    R.add("D2", "Coupes par minute", "alerte" if bad else ("ok" if (20 <= cpm <= 27 if sf == "pose" else 33 <= cpm <= 45) else "note"),
          F(cpm, 1), "posé 20 à 27 ; choral 33 à 45 ; alerte hors de 18 à 48", "observé 8 sur 8 ; seuil : convention",
          None if not bad else ("couper plus souvent : illustrer la voix" if cpm < 18 else "trop de coupes : regrouper"))
    # D3
    t = M["tiers"]
    if all(x is not None for x in t):
        if sf == "pose":
            r_ = t[2] / t[1] if t[1] else 1.0
            st = "ok" if r_ >= 0.85 else ("note" if r_ >= 0.80 else "alerte")
            R.add("D3", "Forme du rythme", st, "tiers : %s / %s / %s s (fin %s du milieu)" % (F(t[0]), F(t[1]), F(t[2]), ("%+d %%" % round(100 * (r_ - 1)))),
                  "la fin ne va pas plus vite que le milieu (pas plus de 15 % plus vite) ; alerte au-delà de 20 % (marge de mesure : convention)",
                  "0 sur 5 films posés accélèrent de plus de 15 % ; le plus rapide : 14 %",
                  "allonger les plans du dernier tiers ; finir sur un plan tenu" if st != "ok" else None)
        else:
            bad = t[2] >= t[0]
            R.add("D3", "Forme du rythme", "alerte" if bad else "ok", "tiers : %s / %s / %s s" % (F(t[0]), F(t[1]), F(t[2])),
                  "la fin va plus vite que le début", "3 sur 3 films choraux", "accélérer le dernier tiers : une rafale d'œuvres avant le logo" if bad else None)
    # D4
    if sf == "pose":
        lf = [p for p in img if p["duree"] >= 5 and p["rel"] >= 0.8]
        R.add("D4", "Plan d'au moins 5 s dans le dernier cinquième", "ok" if lf else "alerte",
              ("plan n° %d (%s)" % (lf[0]["n"], S_(lf[0]["duree"]))) if lf else "aucun", "au moins un", "5 sur 5 films posés",
              None if lf else "tenir le dernier plan 5,7 à 8,1 s (large de préférence) à partir de %s" % R.at(M["dernier"]["debut"] if M["dernier"] else D - 6))
    # D5
    non_coupe = M["n_transitions"] - M["transitions"].get("coupe", 0) - M["transitions"].get("fondu_enchaine_candidat", 0)
    ni = [p for p in M["noirs_internes"] if 0.1 <= p["rel"] <= 0.9]     # zone des chapitres
    bad = len(ni) > 1 or (non_coupe / M["n_transitions"]) > 0.05
    R.add("D5", "Transitions autres que la coupe", "alerte" if bad else "ok", "%s ; %d noir(s) interne(s)" % (P_(non_coupe / M["n_transitions"]), len(ni)),
          "au plus 2 % ; un seul passage au noir, pour changer de chapitre", "12 sur 606 ; au plus 1 noir interne (3 films)",
          ("garder un seul noir de chapitre ; supprimer %s" % liste_tc(R, ni[1:])) if len(ni) > 1 else ("couper franc partout" if bad else None))
    if M["fondus_enchaines"]:
        idx = {p["n"]: p for p in R._plans}
        PERS = ("entretien", "personne")
        par = [p for p in M["fondus_enchaines"] if p["ann"].get("type") in PERS and idx.get(p["n"] - 1, {}).get("ann", {}).get("type") in PERS]
        if par:
            R.add("D5b", "Fondu enchaîné sous la parole", "alerte", liste_tc(R, par), "jamais entre deux plans de parole", "0 sur 606",
                  "remplacer par des coupes franches", "declare")
    ctl_fondus(R, M, "D5c", 1, 0.02, "1 fondu enchaîné sur 606 transitions")
    # D6, D7 parole
    if pa is None:
        for id_, ti in (("D6", "Part de parole"), ("D7", "Respirations"), ("D17", "Première parole"), ("D18", "Dernière parole")):
            ctl_parole_absente(R, id_, ti, "fournir les sous-titres (--sous-titres .srt ou .vtt)")
    else:
        p_ = pa["part"]
        bad = p_ < 0.45 or p_ > 0.92
        R.add("D6", "Part de parole", "alerte" if bad else ("ok" if 0.51 <= p_ <= 0.88 else "note"), P_(p_), "51 à 88 % ; alerte sous 45 % ou au-dessus de 92 %",
              "observé 8 sur 8 ; seuil : convention",
              None if not bad else ("laisser respirer : retirer des phrases" if p_ > 0.92 else "trop peu de parole pour un témoignage"), "sous-titres")
        resp = [(x, y) for x, y in pa["respirations"]]
        if sf == "pose" and D > 90:
            R.add("D7", "Respirations (3 s sans parole)", "ok" if resp else "note", "%d" % len(resp), "au moins une (0,6 par minute)", "6 films sur 8 ; 2 films à parole presque continue n'en ont pas",
                  None if resp else "ménager 3 à 9 s de musique seule sur des images, vers le milieu", "sous-titres")
        else:
            R.add("D7", "Respirations (3 s sans parole)", "ok", "%d" % len(resp), "au moins une si film posé de plus de 90 s", "6 sur 8", None, "sous-titres")
        pr = pa["premiere"]
        st = "alerte" if pr < 1.0 else ("ok" if 2.9 <= pr <= 16.5 else "note")
        R.add("D17", "Première parole", st, "à %s" % S_(pr), "entre 3 et 17 s (médiane 6 s), après le noir et le calme", "8 sur 8",
              "ouvrir par 3 à 6 s de noir, de son calme ou d'images avant la première phrase" if st != "ok" else None, "sous-titres")
        fb = pa["fin_avant_bout"]
        fmin = g(C, "parole.derniere_parole_avant_fin.min", 0.89)
        st = "alerte" if fb < fmin - 0.05 else ("ok" if fb <= 10 else "note")
        R.add("D18", "Dernière parole avant la fin", st, "%s avant la fin" % S_(fb), "1 à 10 s (médiane 4,2 s)", "7 sur 7, de %s à 9,5 s" % F(fmin),
              "ne pas couper sur une phrase : laisser 2 à 5 s d'image et de musique après la dernière phrase" if st == "alerte" else None, "sous-titres")
    # D8 parole sur le visage
    vis = [p for p in img if p["ann"].get("type") in ("entretien", "personne")]
    if pa is not None and vis:
        tot = sum(b - a_ for a_, b in pa["intervalles"])
        sur = sum(M["parole_dans"](p["debut"], p["fin"]) for p in vis)
        r = sur / tot if tot else 0
        R.add("D8", "Parole entendue sur le visage", "alerte" if (r > 0.60 and sf == "pose") else "ok", P_(r), "25 à 55 % (médiane 33 %)", "6 films sur 8 sous 55 %",
              "passer deux tiers de la parole sur des illustrations (lieux, mains, œuvres)" if (r > 0.60 and sf == "pose") else None, "oeil")
    else:
        R.add("D8", "Parole entendue sur le visage", "non_mesure", "—", "25 à 55 %", "6 sur 8", "annoter le type des plans (entretien, personne, illustration) et fournir les sous-titres", "—")
    # D9 entrée par la voix
    pers = {}
    for p in img:
        pid = p["ann"].get("personne")
        if pid and p["ann"].get("type") in ("entretien", "personne") and pid not in pers:
            pers[pid] = p
    if pa is not None and pers:
        voix_avant = [pid for pid, p in pers.items() if M["parole_dans"](max(0, p["debut"] - 1.5), p["debut"]) > 0.5]
        R.add("D9", "Entrée par la voix", "ok" if voix_avant else "note", "%d personne(s) sur %d entendues avant d'être vues (approché)" % (len(voix_avant), len(pers)),
              "au moins la première personne, visage 1,5 à 4,7 s après la voix", "13 sur 20",
              None if voix_avant else "faire entendre la première voix sur une illustration, montrer le visage 3 s après", "oeil")
    # D10, D11, D12, D13 entretiens
    ent = [p for p in img if p["ann"].get("type") == "entretien"]
    if ent:
        longs = [p for p in ent if p["duree"] > 5 and p["rel"] < 0.8]
        R.add("D10", "Plan d'entretien long avant la fin", "alerte" if longs else "ok", "%d plan(s) > 5 s avant le dernier cinquième" % len(longs),
              "au plus 3,2 s (p90) ; plus de 5 s seulement à la fin", "162 plans", ("couper sous la voix : %s" % liste_tc(R, longs)) if longs else None, "oeil")
        lar = [p for p in ent if p["ann"].get("valeur") == "large"]
        R.add("D11", "Entretien en plan large", "alerte" if lar else "ok", "%d" % len(lar), "rapproché, moyen, gros plan", "0 sur 162",
              ("recadrer serré : %s" % liste_tc(R, lar)) if lar else None, "oeil")
        saute = []
        for p1, p2 in zip(img[:-1], img[1:]):
            if p1["ann"].get("personne") and p1["ann"].get("personne") == p2["ann"].get("personne") \
                    and p1["ann"].get("valeur") and p1["ann"].get("valeur") == p2["ann"].get("valeur") and p2["ann"].get("type") == "entretien":
                saute.append(p2)
        R.add("D12", "Même personne, deux plans de suite", "note" if saute else "ok", "%d saute(s) à l'image" % len(saute), "le second plus serré", "9 sur 10",
              ("prendre l'autre caméra, plus serrée : %s" % liste_tc(R, saute)) if saute else None, "oeil")
        bouge = [p for p in ent if p.get("derive")]
        if bouge:
            R.add("D13", "Caméra sur l'entretien", "a_verifier", "%d entretien(s) où l'image change entre début et fin" % len(bouge), "fixe", "18 sur 20 fixes",
                  "regarder %s" % liste_tc(R, bouge))
    # D15 bandeaux
    band = [x for x in M["textes"] if x.get("type") == "bandeau"]
    if band:
        bad = [x for x in band if (float(x["fin"]) - float(x["debut"])) > 5 or x.get("boite") or x.get("place") in ("centre", "visage")]
        R.add("D15", "Bandeaux de nom", "alerte" if bad else "ok", "%d bandeau(x), %d hors règle" % (len(band), len(bad)),
              "2 à 3,5 s, en bas à gauche ou à droite, hors du visage, sans boîte", "27 bandeaux, 8 personnes",
              "petit, en bas, côté vide, sans boîte, 2 à 3,5 s" if bad else None, "oeil")
    # D16 cartons-message
    cm = [x for x in M["textes"] if x.get("type") in ("phrase", "question", "these", "carton")]
    nb_c = len(cm) if M["textes"] else len(M["cartons"])
    trop_mots = [x for x in cm if int(x.get("mots", 0)) > 12]
    src = "oeil" if M["textes"] else ("declare" if any(p["carton_src"] == "declare" for p in M["cartons"]) else "calcul")
    bad = nb_c > 3 or trop_mots or any(x.get("boite") for x in cm)
    R.add("D16", "Cartons-message", ("alerte" if src != "calcul" else "a_verifier") if bad else "ok", "%d carton(s)%s" % (nb_c, (", %d de plus de 12 mots" % len(trop_mots)) if trop_mots else ""),
          "0 à 3, petits, centrés, 12 mots au plus", "observé 8 sur 8", "garder une question ou une thèse en ouverture, ou 1 à 3 cartons de conclusion" if bad else None, src)
    # D17 son calme à l'ouverture
    if M["noir_ouverture"] == 0 and not M["seuil_carton"]:
        R.add("D17b", "Ouverture par le noir", "note", "le film commence sur une image", "noir d'abord", "6 sur 8", "ajouter 1 à 4 s de noir au début")
    son = M["son"]
    if son:
        calme = son["ecart_debut_db"] >= 6
        R.add("D17c", "Son calme au début", "ok" if calme else "note", "3 premières s %s dB sous le niveau médian" % F(son["ecart_debut_db"], 1),
              "plus bas que le reste (9,7 à 47,8 dB plus bas)", "8 sur 8", None if calme else "faire entrer la musique doucement ; commencer dans le calme", "son")
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
                R.add("D20", "Son entre les phrases", "alerte" if r > 0.2 else "ok", "%s du temps sans parole sous -50 dB" % P_(r),
                      "un fond continu (au plus 20 % sous -50 dB)", "8 sur 8", "poser une musique continue sous les voix" if r > 0.2 else None, "son")
    # D19 rafale finale de visages
    raf = [r for r in M["rafales"] if r[0]["rel"] >= 0.85]
    if raf:
        vis = [p for p in raf[-1] if p["ann"].get("visage") or p["ann"].get("type") in ("entretien", "personne")]
        if any(p["ann"] for p in raf[-1]):
            R.add("D19", "Rafale finale", "alerte" if vis else "ok", "%d plan(s) de visage dans la rafale finale" % len(vis), "les œuvres ou le produit, pas les visages",
                  "4 sur 4", "remplacer les visages par des œuvres" if vis else None, "oeil")
        else:
            R.add("D19", "Rafale finale", "a_verifier", "rafale finale de %d plans à %s" % (len(raf[-1]), R.at(raf[-1][0]["debut"])), "œuvres ou produit, pas de visage", "4 sur 4", None)
    # D21 noir et blanc
    if M["part_nb"] is not None and 0.1 < M["part_nb"] < 0.9:
        R.add("D21", "Noir et blanc", "a_verifier", "%s des plans désaturés" % P_(M["part_nb"]), "tout le film, ou personnes en N&B et écrans en couleur",
              "4 sur 4 portraits ; 2 sur 2 mixtes", "vérifier que le mélange suit une règle (gens en N&B, écrans en couleur)")
    elif M["part_nb"] is not None:
        R.add("D21", "Noir et blanc", "ok", "%s des plans désaturés" % P_(M["part_nb"]), "un seul choix, ou une règle", "observé")
    if M["dernier"] is not None and sf == "pose":
        d = M["dernier"]["duree"]
        R.add("D18b", "Plan tenu à la fin", "ok" if d >= 5 else "note", S_(d), "5,7 à 8,1 s", "5 sur 5 films posés",
              None if d >= 5 else "tenir le dernier plan 6 à 8 s, large de préférence")


# ---------------------------------------------------------------- famille bande-annonce

def controles_bandeannonce(R, M, C, a, ann):
    D = M["duree"]
    img = M["img"]
    sf = a.sous_famille or ann.get("sous_famille") or "catalogue_mele"
    R.contexte = "sous-famille %s" % sf
    sc = C.get("seuils_critique", {})
    usage = sf == "usage"
    # B1 plan médian
    if M["med"] is not None:
        if usage:
            lo, hi, alo, ahi = 1.0, 1.7, 0.5, 1.9
            base = "2 films d'usage : 1,03 et 1,67 s ; alerte au-dessus de 1,9 s : convention"
        else:
            lo, hi = g(sc, "plan_image_median_s.cible.0", 0.75), g(sc, "plan_image_median_s.cible.1", 1.2)
            alo, ahi = g(sc, "plan_image_median_s.alerte_en_dessous", 0.5), g(sc, "plan_image_median_s.alerte_au_dessus", 1.65)
            base = "6 bandes-annonces : 0,73 à 1,65 s"
        m = M["med"]
        e1 = 1.0 / mv.FPS          # une image de tolérance
        st = "alerte" if (m > ahi + e1 or m < alo - e1) else ("ok" if lo - e1 <= m <= hi + e1 else "note")
        R.add("B1", "Plan d'image médian", st, "%s s" % F(m), "%s à %s s ; alerte au-dessus de %s s ou sous %s s" % (F(lo), F(hi), F(ahi), F(alo)), base,
              None if st != "alerte" else ("couper plus court : le corps vers 0,9 s, le pic vers 0,6 s" if m > ahi else "illisible : tenir les plans au moins 0,5 s"))
    # B2 accélération
    t = M["tiers"]
    if t[0] is not None and t[2] is not None:
        ok = t[2] < t[0]
        R.add("B2", "Dernier tiers plus rapide que le premier", "ok" if ok else "alerte", "tiers : %s / %s / %s s" % (F(t[0]), F(t[1]) if t[1] else "—", F(t[2])),
              "plus court au dernier tiers (1,20 → 0,90 → 0,77 s)", "6 sur 6",
              None if ok else "raccourcir les plans du dernier tiers jusqu'au pic")
    # B3, B4 pic
    pk = M["pic10"]
    if pk:
        p0, p1 = g(sc, "pic_position.0", 0.78), g(sc, "pic_position.1", 0.88)
        if usage:
            R.add("B3", "Place du pic (10 s les plus rapides)", "note" if not (0.7 <= pk["position"] <= 0.9) else "ok", P_(pk["position"]), "78 % dans 1 film d'usage sur 2", "2 films d'usage",
                  None)
        else:
            st = "alerte" if pk["position"] < 0.70 else ("ok" if p0 - 0.02 <= pk["position"] <= p1 + 0.02 else "note")
            R.add("B3", "Place du pic (10 s les plus rapides)", st, "%s (%s → %s)" % (P_(pk["position"]), R.at(pk["debut"]), R.at(pk["fin"])),
                  "%s à %s ; alerte avant 70 %%" % (P_(p0), P_(p1)), "6 sur 6",
                  "déplacer le passage le plus rapide %s, juste avant la fermeture" % plage(R, D, p0, p1) if st == "alerte" else None)
        q0, q1 = g(sc, "pic_plan_median_s.0", 0.5), g(sc, "pic_plan_median_s.1", 0.85)
        st = "alerte" if pk["mediane"] > 1.0 else ("ok" if pk["mediane"] <= q1 + 0.05 else "note")
        parle = M["parole"] is not None and M["parole"]["n"] > 0
        if (usage or not parle) and st == "alerte":
            st = "note"          # base : 5 films parlés ; usage : pics de 1,17 et 0,37 s (2 films)
        R.add("B4", "Plans du pic", st, "%s s" % F(pk["mediane"]), "%s à %s s ; alerte au-dessus de 1 s" % (F(q0), F(q1)), "5 films parlés",
              "couper le pic à 0,5-0,6 s par plan" if st == "alerte" else None)
    else:
        R.add("B3", "Place du pic", "alerte", "pas de fenêtre de 10 s avec 5 plans", "78 à 88 %", "6 sur 6", "monter un pic de 10 s à 0,6 s par plan vers 80 %")
    # B5 fermeture : du premier noir ou carton après le pic jusqu'à la fin
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
        R.add("B5", "Durée de la fermeture", st, "%s (%s, depuis %s)" % (P_(part), S_(D - fstart), R.at(fstart)), "%s à %s ; alerte au-delà de 20 %% ou sous 5 %%" % (P_(lo), P_(hi)),
              "8 films (médiane 8 s)", ("ramener la fermeture à 6-17 %% : noir, réplique de fin, noir, titre, à partir de %s environ" % R.at(D * 0.9)) if st in ("alerte", "a_verifier") else None, src)
    else:
        R.add("B5", "Durée de la fermeture", "a_verifier", "début de la fermeture non trouvé", "6 à 17 % de la durée", "8 films",
              "donner « fermeture » (en s) dans les annotations")
    # B6 dernier élément
    vis = [p for p in R._plans if p["kind"] != "noir"]
    last = vis[-1] if vis else None
    if last is not None:
        lo, hi = g(sc, "titre_final_s.0", 2.5), g(sc, "titre_final_s.1", 4.8)
        if last["kind"] == "carton":
            ok = lo - 0.1 <= last["duree"] <= hi + 0.3 or last["duree"] <= 7.7
            st = "ok" if lo - 0.1 <= last["duree"] <= hi + 0.3 else ("note" if last["duree"] <= 7.7 else "alerte")
            R.add("B6", "Dernier élément : titre ou logo", st, "carton de %s%s" % (S_(last["duree"]), " (trouvé au calcul)" if last["carton_src"] == "calcul" else ""),
                  "%s à %s s" % (F(lo, 1), F(hi, 1)), "8 sur 8 ; 7,7 s pour un titre animé (1 cas)",
                  None if st == "ok" else "tenir le titre 3,5 s environ", last["carton_src"] or "calcul")
        else:
            st = "alerte" if R.meta["source"] != "video" or last["ann"] else "a_verifier"
            R.add("B6", "Dernier élément : titre ou logo", st, "le film finit sur une image (%s)" % R.at(last["debut"]), "titre ou logo, 2,5 à 4,8 s",
                  "8 sur 8", "finir par un noir, puis le titre ou le logo qui sort du noir, 3,5 s", "oeil" if last["ann"] else "calcul")
    # B7, B8 transitions
    fondus = len(M["fondus_enchaines"])
    autres = M["n_transitions"] - M["transitions"].get("coupe", 0) - M["transitions"].get("fondu_enchaine_candidat", 0)
    part = 1 - autres / M["n_transitions"]
    st = "alerte" if part < 0.85 else ("ok" if part >= 0.9 else "note")
    R.add("B7", "Coupes franches", st, P_(part), "au moins 90 % ; alerte sous 85 %", "92 % (423 sur 459)", "remplacer les effets par des coupes" if st == "alerte" else None)
    ctl_fondus(R, M, "B8", max(1, int(0.03 * M["n_transitions"])), g(sc, "fondus_enchaines_max", 0.03), "1,7 % ; 6 sur 8 passent d'un titre à l'image",
               " ; garder le fondu pour le passage d'un titre à l'image", sur_texte_permis=True)
    # B9 plans larges au premier tiers
    v1 = [p for p in img if p["rel"] < 1 / 3 and p["ann"].get("valeur") in VALEURS]
    if len(v1) >= 3 and not usage:
        r = sum(1 for p in v1 if p["ann"]["valeur"] == "large") / len(v1)
        st = "alerte" if r < 0.25 else ("ok" if r >= g(sc, "part_plans_larges_debut_min", 0.35) else "note")
        R.add("B9", "Plans larges au premier tiers", st, P_(r), "au moins 35 % ; alerte sous 25 %", "39 à 56 % (6 films)",
              "ouvrir large : situer les lieux avant de se rapprocher" if st == "alerte" else None, "oeil")
    elif not usage:
        R.add("B9", "Plans larges au premier tiers", "a_verifier", "valeurs non annotées", "au moins 35 %", "6 sur 6", None)
    # B10 fixes
    if M["part_fixes"] is not None:
        f_ = M["part_fixes"]
        st = "alerte" if f_ > 0.25 else ("ok" if f_ <= g(sc, "plans_fixes_max", 0.15) else "note")
        R.add("B10", "Plans fixes", st, P_(f_), "au plus 15 % ; alerte au-delà de 25 %", "7,6 % (29 sur 384)", "faire bouger l'image" if st == "alerte" else None)
    # B11, B12 parole
    pa = M["parole"]
    if pa is not None and pa["n"]:
        smax, wmax = g(sc, "replique_max_s", 3.1), g(sc, "replique_max_mots", 10)
        subs = R._subs or []
        longues = [x for x in subs if (x[1] - x[0]) > smax or x[3] > wmax]
        part = len(longues) / len(subs) if subs else 0
        st = "alerte" if part > 0.25 else ("ok" if part <= 0.15 else "note")
        R.add("B11", "Répliques longues", st, "%d sur %d au-delà de %s s ou %d mots (%s)" % (len(longues), len(subs), F(smax, 1), wmax, P_(part)),
              "1 réplique sur 10 au-delà (90e centile : %s s, %d mots) ; alerte au-delà d'une sur 4 (convention)" % (F(smax, 1), wmax),
              "108 répliques : médiane 1,7 s et 6 mots",
              ("couper ou partager sur deux plans : %s" % ", ".join(R.at(x[0]) for x in longues[:6])) if st != "ok" else None, "sous-titres")
        if pk:
            r = M["parole_dans"](pk["debut"], pk["fin"]) / 10.0
            st = "alerte" if r > 0.5 else ("ok" if r <= 1 / 3 + 0.02 else "note")
            R.add("B12", "Parole dans le pic", st, P_(r), "un tiers au plus ; alerte au-delà de la moitié", "16 à 38 % ; moins que sur le film 4 sur 5",
                  "laisser la musique seule pendant le pic" if st == "alerte" else None, "sous-titres")
    else:
        ctl_parole_absente(R, "B11", "Réplique la plus longue", "fournir les sous-titres si le film est parlé")
    # B13 ouverture
    nb_o = M["noir_ouverture"]
    lo, hi = g(sc, "ouverture_noir_s.0", 0.1), g(sc, "ouverture_noir_s.1", 4.2)
    st = "alerte" if nb_o == 0 else ("ok" if lo <= nb_o <= hi else "note")
    R.add("B13", "Ouverture dans le noir", st, ("noir de %s" % S_(nb_o)) if nb_o else "image dès la première image", "%s à %s s (médiane 0,6 s)" % (F(lo, 1), F(hi, 1)),
          "7 sur 7", "ajouter 0,5 s de noir avant la première image" if st == "alerte" else None)
    # B14 titres de bloc
    tb = [x for x in M["textes"] if x.get("type") == "titre_bloc"]
    if sf == "catalogue_par_blocs" and tb:
        bad = [x for x in tb if (float(x["fin"]) - float(x["debut"])) > 3.0 or x.get("place") == "fin_de_bloc"]
        R.add("B14", "Titres de bloc", "alerte" if bad else "ok", "%d titre(s), %d hors règle" % (len(tb), len(bad)), "en tête de bloc, 0,8 à 2,3 s", "20 sur 21",
              "titre en tête de bloc, 1 s environ" if bad else None, "oeil")
    # B15, B16 usage
    if usage:
        tx = [p for p in M["cartons"] if p["rel0"] < 0.9] + [x for x in M["textes"] if float(x.get("debut", 0)) < 0.9 * D]
        src = "oeil" if M["textes"] else ("declare" if any(p["carton_src"] == "declare" for p in M["cartons"]) else "calcul")
        st = ("alerte" if src != "calcul" else "a_verifier") if tx else "ok"
        R.add("B15", "Texte dans un film d'usage", st, "%d texte(s) avant les 10 derniers %%" % len(tx), "seulement dans les 10 derniers %", "2 sur 2",
              "déplacer le texte à la fin : une phrase de 3 à 9 mots, puis le nom" if tx else None, src)
        ob = [p for p in img if "objet" in p["ann"]]
        if len(ob) >= 5:
            r = sum(1 for p in ob if p["ann"]["objet"]) / len(ob)
            st = "alerte" if (r < 1 / 6 or r > 0.5) else ("ok" if 0.25 <= r <= 0.36 else "note")
            R.add("B16", "Objet à l'image (film d'usage)", st, P_(r), "un plan sur 4 à un plan sur 3", "2 films : 32 et 34 %",
                  ("montrer l'objet plus souvent : personne, objet, personne" if r < 1 / 6 else "trop d'objet : c'est un film produit ; montrer les gens et ce qu'ils font") if st == "alerte" else None, "oeil")
        else:
            R.add("B16", "Objet à l'image (film d'usage)", "a_verifier", "plans non annotés (champ « objet »)", "un plan sur 4 à un sur 3", "2 films", None)
    ctl_musique(R, M, "B17", "note", permis=False)


# ---------------------------------------------------------------- famille ouverture

def controles_ouverture(R, M, C, a, ann):
    """Niveaux : alerte = aucun film du corpus ne le fait ; note = une minorité le fait."""
    D = M["duree"]
    img = M["img"]
    sf = a.sous_famille or ann.get("sous_famille") or "ouverture"
    R.contexte = "sous-famille %s" % sf
    med_film = M["med"]
    corps = img[1:-1]
    cmed = mv.med([p["duree"] for p in corps]) if corps else None
    plan_seq = len(img) <= 3
    froid = bool(ann.get("ouverture_a_froid"))
    if sf in ("ouverture", "sketch"):
        lo, hi = g(C, "durees.film.cible_conseil.0", 60), g(C, "durees.film.cible_conseil.1", 120)
        R.add("O0", "Durée du film", "ok" if lo <= D <= hi else "note", S_(D), "60 à 120 s (convention)", "8 ouvertures de 65 à 143 s", None)
        if plan_seq:
            R.add("O2", "Plan médian du corps", "sans_objet", "plan-séquence (%d plans d'image)" % len(img), "—", "1 ouverture sur 8 est un plan-séquence")
        # O1 entrée
        if M["premier"] is not None and not plan_seq:
            seuil = M["noir_ouverture"] > 0 or M["seuil_carton"]
            d1 = M["premier"]["duree"]
            ok = d1 >= 5 or froid or (seuil and d1 >= 3)
            R.add("O1", "Entrée", "ok" if ok else "note", "%s ; premier plan de %s" % ("seuil" if seuil else "sans seuil", S_(d1)),
                  "un seuil (noir 0,5 à 1,5 s, ou carton puis noir), puis un premier plan de 5 à 10 s",
                  "5 sur 8 au moins 5 s ; 6 sur 8 avec un seuil ; 1 ouverture à froid",
                  None if ok else "%stenir le premier plan 5 à 10 s (plan n° %d à %s)" % ("" if seuil else "ajouter 0,5 à 1,5 s de noir, puis ", M["premier"]["n"], R.at(M["premier"]["debut"])))
        # O2 corps : quartiles du corpus, plus lent observé 3,17 s (1 film sur 7)
        if cmed is not None and not plan_seq:
            q1, q3 = g(C, "durees.p25", 0.90), g(C, "durees.p75", 2.13)
            vmax = g(C, "durees.mediane_des_medianes_par_film.max", 3.17)
            if q1 <= cmed <= q3:
                st = "ok"
            elif q3 < cmed <= vmax + 1.0 / mv.FPS:
                st = "note"
            else:
                st = "alerte"
            R.add("O2", "Plan médian du corps", st, "%s s" % F(cmed), "1,33 s (quartiles %s à %s s)" % (F(q1), F(q3)),
                  "337 plans, 7 films ; médiane par film de 1,20 à %s s" % F(vmax),
                  None if st == "ok" else ("trop lent : couper les plans du corps vers 1,3 s" if cmed > q3 else "trop haché : tenir les plans vers 1,3 s"))
            tc_ = [[], [], []]
            for p in corps:
                tc_[min(2, int(p["rel"] * 3))].append(p["duree"])
            tm = [mv.med(x) for x in tc_]
            if all(x is not None for x in tm):
                bad = tm[2] > 1.15 * tm[1] + 1.0 / mv.FPS
                R.add("O3", "Le corps garde son rythme", "note" if bad else "ok", "tiers du corps : %s / %s / %s s" % (F(tm[0]), F(tm[1]), F(tm[2])),
                      "1,60 → 1,30 → 1,24 s", "7 films", "garder le rythme jusqu'au pic ; l'atterrissage seul ralentit" if bad else None)
        # O4 pic
        p5 = M["pic5"]
        if p5 is not None and not plan_seq:
            pos = p5["milieu_rel"]
            ok = 0.58 <= pos <= 0.82 and p5["mediane"] <= 0.8
            R.add("O4", "Pic de vitesse", "ok" if ok else "note",
                  "à %s (%s → %s), plans de %s s" % (P_(pos), R.at(p5["debut"]), R.at(p5["fin"]), F(p5["mediane"])),
                  "5 plans de 0,4 à 0,7 s entre 60 et 80 %", "5 ouvertures sur 7",
                  None if ok else "placer 5 plans courts (0,4 à 0,7 s) %s, sur le moment le plus fort de la musique" % plage(R, D, 0.6, 0.8))
    # O5 atterrissage
    der = M["dernier"]
    if der is not None and sf not in ("transition_decor",):
        if sf in ("cloture", "hommage", "clip"):
            R.add("O5", "Fin", "ok", "dernier plan d'image de %s" % S_(der["duree"]), "plan-signature ou logo (1,5 à 3,5 s)", "clôtures : 3 sur 4 finissent sur un logo", None)
        elif not plan_seq:
            apres = [p for p in R._plans if p["debut"] >= der["fin"] - 0.05 and p["kind"] == "carton"]
            fin_carton = max((p["duree"] for p in apres), default=0.0)
            ratio = der["duree"] / med_film if med_film else None
            dmin = g(C, "durees.fin.dernier_plan_image.min", 4.34)
            if (ratio is not None and ratio >= 3.5 and der["duree"] >= 5) or fin_carton >= 5:
                st = "ok"
            elif der["duree"] < dmin - 1.0 / mv.FPS and (ratio is None or ratio < 3.5):
                st = "alerte"      # plus court que tout dernier plan du corpus
            else:
                st = "note"
            R.add("O5", "Atterrissage", st, "dernier plan d'image de %s (%s fois le plan médian)%s" % (S_(der["duree"]), F(ratio, 1), (" ; carton final de %s" % S_(fin_carton)) if fin_carton else ""),
                  "5 à 11 s, au moins 3,5 fois le plan médian ; ou un carton final", "6 sur 8 au moins 5 s ; 7 sur 7 au moins 3,5 fois le plan médian ; 2 finissent sur un carton",
                  None if st == "ok" else "tenir le dernier plan (n° %d, %s) jusqu'à 7 s environ, large, sur le lieu ou la personne qui va parler ; allonger les 3 à 5 plans d'avant" % (der["n"], R.at(der["debut"])))
        v = der["ann"].get("valeur")
        if v:
            R.add("O6", "Fin large", "alerte" if v in SERRE else "ok", v, "le lieu ou la personne, en large", "0 sur 7 finit serré ; 5 sur 7 large",
                  "finir sur le lieu ou la personne, en large" if v in SERRE else None, "oeil")
    # O7 fondus
    if sf != "clip":
        ctl_fondus(R, M, "O7", max(1, int(0.05 * M["n_transitions"])), 0.05, "2 sur 367 changements",
                   " ; un fondu de 1 à 1,5 s seulement pour passer de l'animation au réel")
    # O8 noir au milieu (la transition entre décors cache ses coupes dans le sombre : non concernée)
    if sf in ("ouverture", "sketch"):
        mil = [p for p in M["noirs_internes"] if 0.15 <= p["rel"] <= 0.85 and p["duree"] >= 0.2]
        R.add("O8", "Noir au milieu du film", "note" if (mil and not froid) else "ok", "%d" % len(mil), "le noir sert à entrer ou à finir",
              "15 noirs sur 17 à l'entrée ; au milieu : une ouverture à froid, une flamme entre des noirs",
              ("supprimer les noirs %s : couper franc" % liste_tc(R, mil)) if (mil and not froid) else None)
    # O9 texte au milieu
    tx = list(M["cartons"])
    src = "oeil" if M["textes"] else ("declare" if any(p["carton_src"] == "declare" for p in tx) else "calcul")
    txt_t = [(float(x.get("debut", 0)), x) for x in M["textes"] if x.get("type") not in ("bandeau",)] if M["textes"] else [(p["debut"], p) for p in tx]
    mil_t = [t for t, _ in txt_t if 0.15 * D <= t <= 0.85 * D]
    if sf in ("ouverture", "sketch", "transition_decor"):
        bad = bool(mil_t) or len(txt_t) > 2 or (sf == "transition_decor" and txt_t)
        st = ("alerte" if src != "calcul" else "a_verifier") if bad else "ok"
        R.add("O9", "Texte au milieu, ou plus de 2 textes", st, "%d texte(s), dont %d au milieu" % (len(txt_t), len(mil_t)),
              "0 à 2 textes, au seuil ou à la fin" if sf != "transition_decor" else "aucun texte", "0 sur 7 au milieu ; 0 sur 6 transitions avec texte",
              ("déplacer au seuil ou à la fin, ou supprimer : %s" % ", ".join(R.at(t) for t in mil_t[:6])) if bad else None, src)
    # O10 lecture des cartons
    lents = [x for x in M["textes"] if x.get("mots") and (float(x["fin"]) - float(x["debut"])) / float(x["mots"]) < 0.3]
    if lents:
        R.add("O10", "Carton trop court", "alerte", ", ".join("%d mots en %s" % (int(x["mots"]), S_(float(x["fin"]) - float(x["debut"]))) for x in lents),
              "au moins 0,3 s par mot (médiane 0,5 s)", "7 cartons : 0,32 à 2,09 s par mot", "tenir le carton 0,5 s par mot", "oeil")
    # O11 musique : calage net dans 1 film sur 11 (photos)
    ctl_musique(R, M, "O11", "note", permis=(sf in ("hommage", "clip")))
    # O12 sommet sonore (ouvertures et clôtures)
    son = M["son"]
    if sf in ("ouverture", "sketch", "cloture"):
        if son and son.get("sommet_10s"):
            pos = son["sommet_10s"]["position"]
            st = "ok" if pos >= 0.6 else "note"
            R.add("O12", "Sommet du son", st, "à %s" % P_(pos), "après 60 %", "7 sur 8",
                  "faire monter la musique vers la fin ; le sommet sur le pic" if st != "ok" else None, "son")
        elif son is None:
            R.add("O12", "Sommet du son", "non_mesure", "—", "après 60 %", "7 sur 8", "fournir le son (piste du rendu, ou --son)", "—")
    # O13 parole jusqu'à la fin
    pa = M["parole"]
    if pa is not None and pa["n"] and sf in ("ouverture", "sketch") and not ann.get("fiction_narree"):
        fb = pa["fin_avant_bout"]
        fmin = g(C, "parole.ouverture.fin_sans_parole_s.valeurs.0", 15.0)
        st = "ok" if fb >= fmin else ("alerte" if fb < 10 else "note")
        R.add("O13", "Fin sans parole", st, "%s sans parole à la fin" % S_(fb), "15 à 33 s de musique seule",
              "3 sur 3 films parlés (hors fiction narrée)", "arrêter la parole 15 à 30 s avant la fin" if st != "ok" else None, "sous-titres")
        R.add("O13b", "Part de parole", "note" if pa["part"] > 0.30 else "ok", P_(pa["part"]), "30 % au plus (hors fiction narrée)", "7 sur 8", None, "sous-titres")
    # O15 bandeaux
    band = [x for x in M["textes"] if x.get("type") == "bandeau"]
    if band:
        tot = [x for x in band if float(x["debut"]) < D / 3]
        R.add("O15", "Bandeaux de nom", "alerte" if tot else "ok", "%d bandeau(x) dans le premier tiers" % len(tot), "après le premier tiers : montrer, puis nommer", "7 sur 7",
              "nommer à la deuxième apparition" if tot else None, "oeil")
    # O16, O17 transition entre décors
    if sf == "transition_decor":
        lo, hi = g(C, "sous_familles.transition_decor.duree_s.cible.0", 15), g(C, "sous_familles.transition_decor.duree_s.cible.1", 30)
        R.add("O16a", "Durée de la transition", "ok" if lo <= D <= hi else "note", S_(D), "%d à %d s" % (lo, hi), "6 transitions de 11 à 31 s", None)
        if M["part_fixes"] is not None:
            fx = [p for p in img if p["fixe"] and p["duree"] >= 0.2]
            R.add("O16", "Plans fixes dans la transition", "alerte" if fx else "ok", "%d" % len(fx), "aucun : un mouvement continu vers l'avant", "0 sur 33",
                  ("remplacer par des plans en mouvement : %s" % liste_tc(R, fx)) if fx else None)
        if der is not None:
            amin = g(C, "sous_familles.transition_decor.arrivee_tenue_avant_parole_s.min", 6.7)
            R.add("O17", "Arrivée tenue", "alerte" if der["duree"] < 6 else ("ok" if der["duree"] >= amin else "note"), S_(der["duree"]),
                  "7 à 11,5 s avant la parole (médiane 9,3 s)", "%s à 11,5 s (5 transitions)" % F(amin, 1),
                  "tenir le plan d'arrivée 7 à 11 s, puis encore sous les premiers mots" if der["duree"] < amin else None)
    if sf in ("ouverture", "sketch") and M["noir_ouverture"] == 0 and not M["seuil_carton"] and not froid:
        R.add("O1b", "Seuil", "note", "aucun noir ni carton avant la première image", "noir 0,5 à 1,5 s, ou carton puis noir", "6 sur 8 ont un seuil",
              "ajouter 0,5 à 1,5 s de noir et de silence au début")


# ---------------------------------------------------------------- rapport

ORDRE = [("alerte", "Ce qui s'écarte"), ("note", "Notes (possible, mais rare dans le corpus)"),
         ("a_verifier", "À vérifier à l'œil"), ("ok", "Ce qui colle"), ("non_mesure", "Non mesuré"), ("sans_objet", "Sans objet")]
SRC = {"calcul": "calcul", "declare": "déclaré dans la timeline", "oeil": "annotation à l'œil", "sous-titres": "sous-titres", "son": "son", "—": "—"}


def rendu(R, M, meta, a, famille):
    D = M["duree"]
    al = R.n("alerte")
    verdict = "conforme" if al == 0 else "s'écarte (%d alerte%s)" % (al, "s" if al > 1 else "")
    L = []
    L.append("# Critique du montage : %s" % os.path.basename(meta["fichier"]))
    L.append("")
    L.append("Famille : %s (%s). Source : %s. Verdict : **%s**." % (FAMILLES[famille], R.contexte,
             {"video": "vidéo rendue", "xml": "XML FCP7", "edl": "EDL CMX3600"}[meta["source"]], verdict))
    L.append("")
    tr = M["transitions"]
    def pl(n, mot, mots=None):
        return "%d %s" % (n, mot if n <= 1 else (mots or mot + "s"))
    L.append("Mesuré : durée %s ; %s, %s, %s ; plan d'image médian %s s (p10 %s, p90 %s) ; "
             "%s plans d'image par minute ; coupes franches %s ; noir d'ouverture %s." % (
                 S_(D), pl(M["n_img"], "plan d'image", "plans d'image"), pl(sum(1 for p in R._plans if p["kind"] == "noir"), "noir"),
                 pl(len(M["cartons"]), "carton"), F(M["med"]), F(M["p10"]), F(M["p90"]), F(M["img_min"], 1), P_(M["coupes_part"]), S_(M["noir_ouverture"])))
    L.append("")
    L.append("Contrôles : %d qui collent, %s, %s, %d à vérifier, %d non mesurés." % (
        R.n("ok"), pl(al, "alerte"), pl(R.n("note"), "note"), R.n("a_verifier"), R.n("non_mesure")))
    for st, titre in ORDRE:
        xs = [c for c in R.c if c["statut"] == st]
        if not xs:
            continue
        L.append("")
        L.append("## %s (%d)" % (titre, len(xs)))
        L.append("")
        for c in xs:
            if st in ("ok", "sans_objet"):
                L.append("- **%s %s** : %s. Cible : %s. Corpus : %s." % (c["id"], c["titre"], c["mesure"], c["cible"], c["base"]))
            elif st == "non_mesure":
                L.append("- **%s %s** : %s" % (c["id"], c["titre"], c["correctif"] or "—"))
            else:
                L.append("- **%s %s** : %s. Cible : %s. Corpus : %s. Source : %s." % (c["id"], c["titre"], c["mesure"], c["cible"], c["base"], SRC.get(c["source"], c["source"])))
                if c["correctif"]:
                    L.append("  - Correctif : %s." % c["correctif"].rstrip("."))
    L.append("")
    L.append("## Timeline mesurée")
    L.append("")
    L.append("| n° | Entrée | Durée | Quoi | Transition d'entrée | Mouvement | Annotation |")
    L.append("|---|---|---|---|---|---|---|")
    for p in R._plans:
        tin = p["tin"] + (" (candidat)" if p["verif"] == "candidat" else "")
        an = ", ".join("%s=%s" % (k, v) for k, v in p["ann"].items()) if p["ann"] else ""
        if p["kind"] == "carton" and p.get("carton_src") == "calcul":
            an = (an + " ; " if an else "") + "carton trouvé au calcul"
        if p.get("textes"):
            an = (an + " ; " if an else "") + "texte : " + " / ".join(p["textes"])
        L.append("| %d | %s | %s | %s | %s | %s | %s |" % (p["n"], R.tc(p["debut"]), F(p["duree"]), p["kind"], tin,
                                                        "—" if p["mouvement"] is None else "%d" % p["mouvement"], an))
    L.append("")
    L.append("Lecture : timecodes à %s i/s depuis %s. « candidat » = fondu trouvé au calcul, à confirmer. "
             "Les seuils et comptes viennent de references/cibles/%s.json (N sur M = observé dans N cas sur les M de la base indiquée : films, plans, coupes… ; convention = choix de la skill)." % (
                 F(R.fps, 3).rstrip("0").rstrip(","), mv.tc(0, R.fps, R.depart), famille))
    for w in meta.get("avertissements") or []:
        L.append("")
        L.append("Avertissement : %s." % w)
    return "\n".join(L) + "\n", verdict


def main(argv):
    ap = argparse.ArgumentParser(description="Critique un montage contre les films des keynotes de sa famille.")
    ap.add_argument("montage", help="vidéo rendue, XML FCP7 ou EDL CMX3600")
    ap.add_argument("--famille", required=True)
    ap.add_argument("--sous-famille", default=None)
    ap.add_argument("--schema", choices=["tardif", "des_le_debut"], default=None, help="produit : révélation tardive ou objet dès le début")
    ap.add_argument("--debut", type=float, default=None, help="vidéo : début du film dans le fichier (s)")
    ap.add_argument("--fin", type=float, default=None, help="vidéo : fin du film dans le fichier (s)")
    ap.add_argument("--sous-titres", default=None, help=".srt ou .vtt (temps du fichier vidéo ; décalés de --debut)")
    ap.add_argument("--annotations", default=None, help="JSON d'annotations à l'œil")
    ap.add_argument("--son", default=None, help="fichier son à mesurer (sinon la piste du rendu)")
    ap.add_argument("--son-debut", type=float, default=None, help="--son : position (s) dans le fichier son de la première image du film (défaut 0)")
    ap.add_argument("--fps", type=float, default=None, help="EDL : cadence de la timeline")
    ap.add_argument("--mesurer-medias", action="store_true", help="XML/EDL : mesurer mouvement et couleur dans les fichiers sources")
    ap.add_argument("--cibles", default=CIBLES)
    ap.add_argument("--sortie", default=None, help="rapport Markdown (défaut : à l'écran)")
    ap.add_argument("--json", default=None, help="rapport JSON")
    ap.add_argument("--planche", default=None, help="vidéo : planche contact des plans (JPEG)")
    ap.add_argument("--silencieux", action="store_true")
    a = ap.parse_args(argv)
    fam = ALIAS.get(a.famille.lower(), a.famille.lower())
    if fam not in FAMILLES:
        sys.stderr.write("famille inconnue : %s (produit, ouverture, documentaire, bandeannonce)\n" % a.famille)
        return 2
    if a.sous_famille and a.sous_famille not in SOUS[fam]:
        sys.stderr.write("sous-famille inconnue pour %s : %s (%s)\n" % (fam, a.sous_famille, ", ".join(SOUS[fam])))
        return 2
    C = charger_cibles(fam, a.cibles)
    a._ann = {}
    if a.annotations:
        try:
            with open(a.annotations, encoding="utf-8") as fh:
                a._ann = json.load(fh)
        except OSError as ex:
            sys.stderr.write("annotations illisibles : %s : %s\n" % (a.annotations, ex.strerror or ex))
            return 2
        except ValueError as ex:
            sys.stderr.write("annotations illisibles : %s : JSON invalide (%s)\n" % (a.annotations, ex))
            return 2
        fautes = valider_annotations(a._ann)
        if fautes:
            sys.stderr.write("annotations illisibles : %s : %s\n" % (a.annotations, " ; ".join(fautes)))
            return 2
    for opt, f in (("--sous-titres", a.sous_titres), ("--son", a.son)):
        if f and not os.path.isfile(f):
            sys.stderr.write("%s %s introuvable\n" % (opt, f))
            return 2
    ext = os.path.splitext(a.montage.rstrip("/"))[1].lower()
    try:
        if ext in (".xml", ".edl", ".xmeml", ".fcpxml", ".fcpxmld"):
            plans, meta = depuis_timeline(a.montage, a)
        else:
            plans, meta = depuis_video(a.montage, a)
    except Exception as ex:
        sys.stderr.write("lecture impossible : %s\n" % ex)
        return 2
    D = meta["duree"]
    appliquer_annotations(plans, a._ann, fam, D)
    subs = None
    if a.sous_titres:
        try:
            subs = mv.lire_sous_titres(a.sous_titres, a.debut or 0.0, (a.debut or 0.0) + D)
        except (OSError, ValueError, IndexError) as ex:
            sys.stderr.write("sous-titres illisibles : %s : %s\n" % (a.sous_titres, ex))
            return 2
    son = None
    src_son = a.son or (a.montage if meta["source"] == "video" and (meta.get("info") or {}).get("audio") else None)
    if src_son:
        s0 = (a.debut or 0.0) if src_son == a.montage else (a.son_debut or 0.0)
        x = mv.lire_audio(src_son, s0, s0 + D)
        son = mv.analyse_son(x)
        if son is not None and son["part_silence_numerique"] >= 0.98:
            # piste muette (un rendu sans musique en porte souvent une) : rien à mesurer, pas un sommet au hasard
            son = None
            if not a.silencieux:
                sys.stderr.write("piste son muette : les contrôles du son restent non mesurés\n")
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
        R.add("V1", "Transitions possiblement manquées", "a_verifier",
              "%d plan(s) dont le début et la fin ne se ressemblent plus" % len(sus), "—",
              "le calcul des fondus est une borne basse (corpus : 54 vrais sur 225 candidats, d'autres manqués)",
              "regarder %s ; un fondu ou un volet vu à l'œil s'ajoute dans annotations.ajouts" % liste_tc(R, sus))
    if not M["mouvement_mesure"]:
        if a.mesurer_medias and meta.get("hors_fichier"):
            pourquoi = ("timecode source hors du fichier pour %d plan(s) : l'entrée lue dans la timeline dépasse la durée du "
                        "fichier, timecode inscrit retranché ; vérifier que la timeline pointe sur les bons fichiers, "
                        "ou critiquer la vidéo rendue" % meta["hors_fichier"])
        elif a.mesurer_medias:
            pourquoi = "fichiers sources introuvables ou illisibles : critiquer la vidéo rendue"
        else:
            pourquoi = "timeline sans image : relancer avec --mesurer-medias (fichiers sources présents) ou critiquer la vidéo rendue"
        R.add("MV", "Mouvement, images fixes, noir et blanc", "non_mesure", "—", "—", "—", pourquoi, "—")
    txt, verdict = rendu(R, M, meta, a, fam)
    if a.planche and meta["source"] == "video":
        t0 = meta["t0"]
        imgs = mv.extraire_images(a.montage, [t0 + (p["debut"] + p["fin"]) / 2 for p in plans], 320, 180)
        leg = ["%d %s %s\n%s%s" % (p["n"], R.tc(p["debut"]), F(p["duree"]), p["kind"], " ?" if p["verif"] == "candidat" else "") for p in plans]
        cand = M["fondus_candidats"]
        for p in cand:
            for dt in (-0.4, -0.15, 0.0, 0.15, 0.4):
                imgs += mv.extraire_images(a.montage, [t0 + p["debut"] + dt], 320, 180)
                leg.append("fondu ? n°%d %+.2f s" % (p["n"], dt))
        mv.planche(imgs, leg, a.planche, colonnes=6)
        txt += "\nPlanche contact : %s\n" % os.path.abspath(a.planche)
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
