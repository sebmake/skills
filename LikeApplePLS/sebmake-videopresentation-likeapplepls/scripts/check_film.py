#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
check_film.py : contrôle un film.json avant la planche et le rendu (Python 3.9, sans dépendance).

    python3 check_film.py film.json              # rapport lisible ; code 0 = aucun blocage, 1 = erreurs
    python3 check_film.py film.json --json       # rapport JSON (utilisé par build_film.js)
    python3 check_film.py film.json --resolu R   # contrôle aussi les sorties résolues par le moteur
                                                 # (déclinaisons « auto », durées ajustées, lignes réelles)

Ce qui est contrôlé :
  - structure : champs obligatoires, couleurs HEX, polices interdites, id uniques, recettes connues ;
  - voix et musique : aucun champ de voix ; musique locale, droits confirmés, ou null ;
  - durées : somme des plans contre la cible (±10 %), bornes 60–120 s (film) et 15–60 s (réseaux) ;
  - lecture : durée d'un carton selon ses mots (1,2 s + 0,3 s × mots ; nom ≥ 2,5 s) ;
  - mots : 12 au plus par carton, 6 au plus d'un bloc, 1 à 4 pour un libellé ou un nom ;
  - zones sûres et largeur des lignes par format (9:16, 1:1, 16:9) ;
  - chiffres : aucun chiffre sans source ; [À FOURNIR] listés ;
  - visuels manquants (repli dessiné neutre au rendu) ;
  - place du nom (≥ 76 % du film) et de la révélation (≥ 60 %) ; cadence des cartons ;
  - contraste des couleurs de texte sur les fonds (≥ 4,5:1 exigé, ≥ 7:1 conseillé).
Les seuils viennent des analyses du corpus (voir ../references/film-spec.md, § 7).
"""
import json
import math
import os
import re
import sys

RECETTES = {
    "noir": {"emplacements": [], "textes": []},
    "lisere": {"emplacements": ["objet"], "textes": []},
    "macro": {"emplacements": ["image"], "textes": ["libelle"]},
    "orbite": {"emplacements": ["objet|vues"], "textes": ["libelle"]},
    "eclate": {"emplacements": ["pieces|objet"], "textes": ["libelle"]},
    "revelation": {"emplacements": ["objet"], "textes": ["nom"]},
    "panneau": {"emplacements": ["capture"], "textes": ["libelle"]},
    "empilement": {"emplacements": ["captures"], "textes": ["libelle"]},
    "carton": {"emplacements": [], "textes": ["phrase", "mot", "chiffre"]},
    "mot-sur-image": {"emplacements": ["image"], "textes": ["phrase", "mot"]},
    "mur": {"emplacements": ["elements"], "textes": ["libelle"]},
    "fin": {"emplacements": [], "textes": ["nom"]},
}
DEFAUTS_COULEURS = {"fond_sombre": "#0E1013", "fond_clair": "#F2F1EE", "texte_sur_sombre": "#F4F4F2", "texte_sur_clair": "#16171A"}
ROLES = ["accroche", "contexte", "preuve", "revelation", "chute", "respiration", "fin"]
TRANSITIONS = ["coupe", "fondu", "noir"]
FONDS = ["sombre", "clair", "accent", "noir"]
VISUELLES = ["lisere", "macro", "orbite", "eclate", "revelation", "panneau", "empilement", "mot-sur-image", "mur"]
POLICES_INTERDITES = ["sf pro", "sf pro display", "sf pro text", "sf compact", "sf mono", "new york",
                      "san francisco", "-apple-system", "blinkmacsystemfont", "system-ui", "ui-sans-serif", "myriad"]
SIGNATURES = [r"shot on", r"tourn[ée] (avec|sur)", r"film[ée] (avec|sur)", r"\b9:41\b", r"one more thing"]

FORMATS = {
    "16:9": {"W": 1920, "H": 1080, "sure": (192, 108, 1728, 972), "ligneMax": 1267, "carMax": 42,
             "tailles": {"carton": 58, "mot": 150, "nomHeros": 124, "nomDiscret": 56, "libelle": 68, "legende": 34}},
    "9:16": {"W": 1080, "H": 1920, "sure": (65, 230, 1015, 1498), "ligneMax": 800, "carMax": 22,
             "tailles": {"carton": 72, "mot": 150, "nomHeros": 132, "nomDiscret": 76, "libelle": 76, "legende": 42}},
    "1:1": {"W": 1080, "H": 1080, "sure": (86, 86, 994, 994), "ligneMax": 908, "carMax": 26,
            "tailles": {"carton": 62, "mot": 124, "nomHeros": 116, "nomDiscret": 68, "libelle": 64, "legende": 38}},
}
LARGEUR = {"regular": 0.55, "gras": 0.6}
MIN_RECETTE = {"noir": 0.5, "lisere": 2.0, "macro": 1.5, "orbite": 2.5, "eclate": 3.0, "revelation": 3.0,
               "panneau": 2.0, "empilement": 2.5, "carton": 1.5, "mot-sur-image": 1.5, "mur": 2.5, "fin": 2.5}
BUDGETS = [(20, 4, 16), (37, 7, 32), (52, 10, 45), (999, 14, 60)]  # (durée ≤, cartons, mots) — declinaisons.md § 3.2


class Rapport(object):
    def __init__(self):
        self.erreurs, self.avertissements, self.par_plan = [], [], {}

    def _note(self, sortie, plan, msg):
        if plan:
            self.par_plan.setdefault(sortie or "film", {}).setdefault(plan, []).append(msg)

    def err(self, msg, plan=None, sortie=None):
        self.erreurs.append(msg)
        self._note(sortie, plan, "✗ " + msg.split(" : ", 1)[-1])

    def avert(self, msg, plan=None, sortie=None):
        self.avertissements.append(msg)
        self._note(sortie, plan, "· " + msg.split(" : ", 1)[-1])


def nb_mots(s):
    return len([w for w in str(s or "").split() if re.search(r"[^\W_]", w, re.UNICODE)])


def hex_rgb(h):
    v = str(h or "").strip().lstrip("#")
    if len(v) == 3:
        v = "".join(c * 2 for c in v)
    if not re.match(r"^[0-9a-fA-F]{6}$", v):
        return None
    return [int(v[i:i + 2], 16) for i in (0, 2, 4)]


def luminance(h):
    out = 0.0
    for x, k in zip(hex_rgb(h), (0.2126, 0.7152, 0.0722)):
        v = x / 255.0
        v = v / 12.92 if v <= 0.03928 else ((v + 0.055) / 1.055) ** 2.4
        out += v * k
    return out


def contraste(a, b):
    la, lb = sorted([luminance(a), luminance(b)], reverse=True)
    return (la + 0.05) / (lb + 0.05)


def lecture_min(texte):
    """Durée minimale d'un carton (grammaire-film.md § 6.4), en secondes."""
    t = texte.get("type")
    if t == "nom":
        return 2.5
    if t == "chiffre":
        return max(1.5, 1.2 + 0.3 * (nb_mots(texte.get("libelle")) + 1))
    n = nb_mots(texte.get("contenu"))
    if t == "mot":
        return max(1.0, 1.2 + 0.3 * n)
    return max(1.5, 1.2 + 0.3 * n)


def lecture_conseil(texte):
    """Durée conseillée (grammaire-film.md § 6.4) : 1,5 s + 0,3 s × mots, jamais moins de 2 s."""
    n = nb_mots(texte.get("contenu") or texte.get("libelle"))
    return max(2.0, 1.5 + 0.3 * n)


def duree_nom_empilement(n_captures):
    """Plan minimal d'un empilement suivi du nom en déclinaison (même calcul que minimumPlan du moteur)."""
    n = min(5, n_captures or 3)
    return math.ceil((0.5 + n * 0.2 + 0.4 + 2.8) * 10) / 10.0


def besoin_texte(rec, t, premier_reseau=False, avec_nom=False, produit="", n_captures=0):
    """Durée minimale d'un plan pour que son texte se lise (même calcul que minimumPlan du moteur)."""
    if rec == "revelation":
        return 4.0 if avec_nom else 0.0
    if rec == "empilement" and avec_nom:
        return duree_nom_empilement(n_captures)
    if rec == "fin":
        return 2.5 + (0.0 if premier_reseau else 0.3)
    if not t:
        return 0.0
    typ = t.get("type")
    lmin = lecture_min(t)
    if typ == "chiffre":
        return round(lmin + 0.6, 1)
    if typ == "libelle":
        return math.ceil((lmin + 0.6) * 10 - 1e-6) / 10.0
    if typ == "nom":
        return lmin + 0.3
    n = nb_mots(t.get("contenu"))
    aff = "bloc" if typ == "mot" else (t.get("affichage") or ("groupes" if n > 6 else "bloc"))
    etapes = 1 if aff == "bloc" else (n if aff == "mot-a-mot" else (len(t.get("groupes") or []) or (2 if n <= 9 else 3)))
    construction = (etapes - 1) * (0.4 if aff == "mot-a-mot" else 0.8)
    lecture = construction + max(lmin - construction, 1.0 + 0.1 * n) if etapes > 1 else lmin
    marge = 0.4 if premier_reseau else (0.6 if rec == "carton" else 0.8)  # entrée + sortie
    return math.ceil((lecture + marge) * 10 - 1e-6) / 10.0


def lignes_estimees(contenu, fmt, taille, gras, car_max, ligne_par_groupe=False, groupes=None):
    mots = str(contenu or "").split()
    if not mots:
        return [], taille
    unites = groupes if (ligne_par_groupe and groupes) else [contenu]
    lignes = []
    for u in unites:
        cur = []
        for w in str(u).split():
            if cur and len(" ".join(cur + [w])) > car_max:
                lignes.append(" ".join(cur))
                cur = []
            cur.append(w)
        if cur:
            lignes.append(" ".join(cur))
    k = LARGEUR["gras"] if gras else LARGEUR["regular"]
    plus = max(len(l) for l in lignes)
    if plus * k * taille > fmt["ligneMax"]:
        taille = max(taille * 0.72, fmt["ligneMax"] / (plus * k))
    return lignes, taille


def resoudre_standalone(film, rap):
    """Sorties sans le moteur : le film tel quel, les déclinaisons à liste explicite (durées ajustées)."""
    pid = dict((p.get("id"), p) for p in film.get("plans", []))
    sorties = []
    if "16:9" in (film.get("meta", {}).get("formats") or ["16:9"]):
        t = 0.0
        plans = []
        for p in film.get("plans", []):
            plans.append({"id": p.get("id"), "recette": p.get("recette"), "role": p.get("role", ""), "debut": t,
                          "duree": float(p.get("duree_s") or 0), "entree": p.get("transition", "coupe"),
                          "texte": p.get("texte"), "textes": None, "avecNom": False})
            t += float(p.get("duree_s") or 0)
        sorties.append({"id": "film", "format": "16:9", "reseau": False, "cible": film["meta"].get("duree_cible_s"), "total": t, "plans": plans})
    for d in film.get("declinaisons", []) or []:
        if d.get("regle") == "auto" or not d.get("plans"):
            rap.avert("déclinaison %s : sélection « auto » calculée par le moteur, contrôlée au build (build_film.js)" % d.get("id"))
            continue
        items = []
        for x in d["plans"]:
            x = {"id": x} if isinstance(x, str) else x
            p = pid.get(x.get("id"))
            if not p or p.get("recette") == "noir":
                continue
            mn = max(MIN_RECETTE.get(p.get("recette"), 1.5),
                     besoin_texte(p.get("recette"), p.get("texte"), not items, bool(x.get("avec_nom")),
                                  n_captures=len((p.get("visuels") or {}).get("captures") or [])))
            fixe = (x.get("duree_s") or 0) > 0
            items.append({"p": p, "x": x, "fixe": fixe, "duree": float(x["duree_s"]) if fixe else float(p.get("duree_s") or 0),
                          "naturel": float(p.get("duree_s") or 1), "min": mn, "bloque": False})
        cible = float(d.get("duree_cible_s") or 30)
        fixe = sum(i["duree"] for i in items if i["fixe"])
        libres = [i for i in items if not i["fixe"]]
        for _ in range(20):
            bloq = sum(i["duree"] for i in libres if i["bloque"])
            act = [i for i in libres if not i["bloque"]]
            if not act:
                break
            f = (cible - fixe - bloq) / sum(i["naturel"] for i in act)
            change = False
            for i in act:
                i["duree"] = i["naturel"] * f
                if i["duree"] < i["min"]:
                    i["duree"], i["bloque"], change = i["min"], True, True
            if not change:
                break
        t = 0.0
        plans = []
        for i in items:
            dd = round(i["duree"], 1)
            plans.append({"id": i["p"]["id"], "recette": i["p"]["recette"], "role": i["p"].get("role", ""), "debut": t, "duree": dd,
                          "entree": "coupe" if not plans else i["p"].get("transition", "coupe"), "texte": i["p"].get("texte"),
                          "textes": None, "avecNom": bool(i["x"].get("avec_nom")),
                          "nCaptures": len((i["p"].get("visuels") or {}).get("captures") or [])})
            t += dd
        if plans and plans[0]["recette"] == "carton" and (plans[0].get("texte") or {}).get("type") != "chiffre" \
                and pid.get(plans[0]["id"], {}).get("fond") != "accent" \
                and any(q.get("visuels") for q in film.get("plans", [])):
            plans[0]["fondImage"] = True  # le moteur pose le produit flouté derrière un carton d'ouverture
        sorties.append({"id": d.get("id"), "format": d.get("format"), "reseau": True, "cible": cible, "total": t, "plans": plans})
    return sorties


# ---------------------------------------------------------------------------
def controle_structure(film, base, rap):
    meta = film.get("meta") or {}
    for k in ("titre", "produit", "message", "public", "formats", "duree_cible_s"):
        if not meta.get(k):
            rap.err("meta.%s : champ obligatoire manquant" % k)
    # aucune voix
    def cherche_voix(o, chemin):
        if isinstance(o, dict):
            for k, v in o.items():
                if str(k).lower() in ("voix", "voice", "voiceover", "voix_off", "narration", "tts", "script_voix"):
                    rap.err("%s.%s : aucune voix dans ce film (ni voix off, ni synthèse vocale)" % (chemin, k))
                cherche_voix(v, chemin + "." + str(k))
        elif isinstance(o, list):
            for i, v in enumerate(o):
                cherche_voix(v, "%s[%d]" % (chemin, i))
    cherche_voix(film, "film")

    theme = film.get("theme") or {}
    coul = theme.get("couleurs") or {}
    if not coul.get("accent"):
        rap.err("theme.couleurs.accent : obligatoire (une seule couleur forte)")
    for k, v in coul.items():
        if hex_rgb(v) is None:
            rap.err("theme.couleurs.%s : HEX invalide « %s »" % (k, v))
    if coul.get("fond_clair", "").upper() in ("#FFFFFF", "#FFF"):
        rap.avert("theme.couleurs.fond_clair : blanc pur ; les fonds clairs du corpus ne le sont jamais (0/7)")
    for role, p in (theme.get("polices") or {}).items():
        for nom in [p.get("famille")] + list(p.get("repli") or []):
            if str(nom or "").lower() in POLICES_INTERDITES:
                rap.err("theme.polices.%s : police propre à une marque refusée (%s)" % (role, nom))
        if p.get("fichier") and not os.path.exists(os.path.join(base, p["fichier"])):
            rap.avert("theme.polices.%s.fichier introuvable : %s (le repli sera utilisé)" % (role, p["fichier"]))
    logo = theme.get("logo") or {}
    for k, v in logo.items():
        if v and not os.path.exists(os.path.join(base, v)):
            rap.avert("theme.logo.%s introuvable : %s (la fin se fera sans logo)" % (k, v))

    m = film.get("musique")
    if m:
        f = str(m.get("fichier") or "")
        if re.match(r"^https?:", f, re.I):
            rap.err("musique.fichier : adresse web refusée ; fichier local fourni par l'utilisateur, ou musique: null")
        elif not f or not os.path.exists(os.path.join(base, f)):
            rap.err("musique.fichier introuvable : %s" % f)
        if m.get("droits_confirmes") is not True:
            rap.err("musique.droits_confirmes doit valoir true (l'utilisateur a les droits), sinon musique: null")
        if m.get("caler_coupes"):
            rap.avert("musique.caler_coupes : convention (le calage des coupes sur la musique n'est pas démontré dans le corpus : 16 coupes sur 62, 16,4 au hasard)")

    ids = set()
    for i, p in enumerate(film.get("plans") or []):
        pid = p.get("id")
        if not pid or not re.match(r"^[a-z0-9-]+$", str(pid)):
            rap.err("plans[%d] : id manquant ou invalide" % i)
        if pid in ids:
            rap.err("plans[%d] : id en double %s" % (i, pid))
        ids.add(pid)
        rec = p.get("recette")
        if rec not in RECETTES:
            rap.err("%s : recette inconnue « %s » (connues : %s)" % (pid, rec, ", ".join(sorted(RECETTES))), pid)
            continue
        if not (float(p.get("duree_s") or 0) > 0):
            rap.err("%s : duree_s manquante" % pid, pid)
        if p.get("role") and p["role"] not in ROLES:
            rap.avert("%s : role inconnu « %s » (%s)" % (pid, p["role"], ", ".join(ROLES)), pid)
        if p.get("transition") and p["transition"] not in TRANSITIONS:
            rap.err("%s : transition inconnue « %s » (%s)" % (pid, p["transition"], ", ".join(TRANSITIONS)), pid)
        if p.get("fond") and p["fond"] not in FONDS:
            rap.err("%s : fond inconnu « %s »" % (pid, p["fond"]), pid)
        # visuels
        vis = p.get("visuels") or {}
        for empl in RECETTES[rec]["emplacements"]:
            options = empl.split("|")
            fournis = [o for o in options if vis.get(o)]
            if not fournis:
                rap.avert("%s : visuel « %s » non fourni → repli dessiné neutre" % (pid, empl.replace("|", " ou ")), pid)
                continue
            vals = vis[fournis[0]]
            for v in (vals if isinstance(vals, list) else [vals]):
                if v and not os.path.exists(os.path.join(base, v)):
                    rap.avert("%s : visuel introuvable %s → repli dessiné neutre" % (pid, v), pid)
        if rec == "orbite" and vis.get("objet") and not vis.get("vues"):
            rap.avert("%s : une seule vue → rotation limitée à ±12° (au-delà, une photo à plat se voit comme une carte)" % pid, pid)
        if rec == "eclate" and not vis.get("pieces"):
            rap.avert("%s : pas de pièces fournies → l'objet est découpé en bandes (aucun intérieur inventé)" % pid, pid)
        # textes
        t = p.get("texte")
        if t:
            controle_texte(p, t, rap)
        elif rec == "carton":
            rap.err("%s : un carton sans texte" % pid, pid)
        mv = p.get("mouvement") or {}
        if rec == "panneau" and mv.get("detail"):
            z = mv["detail"].get("zone")
            if not (isinstance(z, list) and len(z) == 4 and all(0 <= float(v) <= 100 for v in z) and z[0] + z[2] <= 100.5 and z[1] + z[3] <= 100.5):
                rap.err("%s : mouvement.detail.zone doit être [x, y, largeur, hauteur] en %% de la capture" % pid, pid)
        if rec == "orbite" and abs(float(mv.get("angle", 12))) > 12:
            rap.avert("%s : angle > 12° ramené à 12° (recettes.md, orbite)" % pid, pid)

    for d in film.get("declinaisons") or []:
        if d.get("format") not in FORMATS:
            rap.err("déclinaison %s : format inconnu %s (16:9, 9:16, 1:1)" % (d.get("id"), d.get("format")))
        for x in d.get("plans") or []:
            x = {"id": x} if isinstance(x, str) else x
            if x.get("id") not in ids:
                rap.err("déclinaison %s : plan inconnu %s" % (d.get("id"), x.get("id")))


def controle_texte(p, t, rap):
    pid, rec = p.get("id"), p.get("recette")
    typ = t.get("type")
    if typ not in RECETTES[rec]["textes"]:
        rap.err("%s : texte de type « %s » impossible dans la recette %s (possibles : %s)" % (pid, typ, rec, ", ".join(RECETTES[rec]["textes"]) or "aucun"), pid)
        return
    champs = [t.get("contenu"), t.get("libelle"), t.get("ligne")] + list(t.get("groupes") or [])
    tout = " ".join(str(c) for c in champs if c)
    for sig in SIGNATURES:
        if re.search(sig, tout, re.I):
            rap.err("%s : signature ou formule de marque interdite (« %s »)" % (pid, sig), pid)
    if "!" in tout:
        rap.avert("%s : point d'exclamation (0 sur 14 phrases du corpus)" % pid, pid)
    if "[À FOURNIR" in tout or "[A FOURNIR" in tout:
        rap.avert("%s : texte [À FOURNIR] à compléter" % pid, pid)
    # chiffres sans source
    sans_marque = re.sub(r"\[À FOURNIR[^\]]*\]", "", tout)
    if re.search(r"\d", sans_marque) and not t.get("source"):
        rap.err("%s : chiffre sans source dans le texte (« %s ») ; un chiffre vient de l'utilisateur, avec texte.source" % (pid, sans_marque.strip()[:60]), pid)
    if typ == "chiffre":
        if t.get("chiffre") in (None, ""):
            rap.avert("%s : chiffre non fourni → [À FOURNIR] estompé à l'écran" % pid, pid)
        elif not t.get("source"):
            rap.err("%s : chiffre « %s » sans source (texte.source)" % (pid, t.get("chiffre")), pid)
        if not t.get("libelle"):
            rap.avert("%s : chiffre sans libellé (le libellé porte la base de comparaison)" % pid, pid)
        return
    c = t.get("contenu") or ""
    n = nb_mots(c)
    if typ in ("phrase", "mot") and not c:
        rap.err("%s : texte.contenu vide" % pid, pid)
    if typ == "phrase":
        if n > 12:
            rap.err("%s : %d mots ; 12 au plus par carton (106 cartons sur 109) — couper en deux cartons" % (pid, n), pid)
        elif n > 6 and t.get("affichage") == "bloc":
            rap.avert("%s : %d mots affichés d'un bloc ; au-delà de 6, construire en groupes (grammaire-film.md § 6.4)" % (pid, n), pid)
        if c and c.upper() == c and re.search(r"[A-Z]{4,}", c):
            rap.avert("%s : phrase en capitales ; casse de phrase attendue (13/14)" % pid, pid)
        if t.get("groupes"):
            if re.sub(r"\s+", " ", " ".join(t["groupes"])).strip() != re.sub(r"\s+", " ", c).strip():
                rap.err("%s : texte.groupes ne redonne pas texte.contenu (les mots ne changent jamais)" % pid, pid)
            if len(t["groupes"]) > 3:
                rap.avert("%s : plus de 3 groupes (2 ou 3 : grammaire-film.md § 6.4)" % pid, pid)
    if typ == "mot" and n > 2:
        rap.avert("%s : un « mot » de %d mots ; 1 ou 2 attendus" % (pid, n), pid)
    if typ in ("libelle", "nom") and n > 4:
        rap.avert("%s : %s de %d mots ; 1 à 4 attendus" % (pid, typ, n), pid)


def controle_sortie(film, s, rap):
    sid, fmt_nom = s["id"], s["format"]
    fmt = FORMATS.get(fmt_nom)
    if not fmt:
        return
    plans = s["plans"]
    total = s["total"] or sum(p["duree"] for p in plans)
    cible = float(s.get("cible") or 0)
    etiquette = "film" if sid == "film" else "déclinaison %s" % sid
    if cible:
        ecart = (total - cible) / cible
        if abs(ecart) > 0.10:
            rap.err("%s : durée %.1f s pour une cible de %.0f s (écart %+.0f %%, ±10 %% permis)" % (etiquette, total, cible, ecart * 100))
    if not s["reseau"]:
        if total < 60 or total > 120:
            rap.avert("film : %.1f s ; le film produit vise 1 à 2 min" % total)
        if total > 68.5:
            rap.avert("film : %.1f s sans voix ; aucun film produit sans voix du corpus ne dépasse 68,5 s → chapitres séparés par un noir ou un carton (convention)" % total)
    else:
        if total < 14 or total > 61:
            rap.avert("%s : %.1f s ; les déclinaisons visent 15 à 60 s" % (etiquette, total))

    n_cartons, mots_total, temps_texte = 0, 0, 0.0
    precedent_texte = False
    for i, p in enumerate(plans):
        pid, rec, d = p["id"], p["recette"], float(p["duree"])
        t = p.get("texte")
        if d < MIN_RECETTE.get(rec, 1.0) - 0.05:
            rap.avert("%s : %s de %.1f s, sous le minimum de la recette (%.1f s)" % (etiquette, pid, d, MIN_RECETTE.get(rec, 1.0)), pid, sid)
        affiche = None
        if t and t.get("type") in ("phrase", "mot", "chiffre"):
            affiche = t
        elif rec == "fin":
            affiche = {"type": "nom", "contenu": (t or {}).get("contenu") or film["meta"].get("produit")}
        elif rec in ("revelation", "empilement") and p.get("avecNom"):
            affiche = {"type": "nom", "contenu": ((t or {}).get("contenu") if (t or {}).get("type") == "nom" else None) or film["meta"].get("produit")}
        elif t and t.get("type") == "libelle":
            affiche = t
        if affiche:
            n_cartons += 1
            mots = nb_mots(affiche.get("contenu") or affiche.get("libelle")) + (1 if affiche.get("type") == "chiffre" else 0)
            if rec == "fin" and t and t.get("ligne"):
                mots += nb_mots(t.get("ligne"))
            mots_total += mots
            lmin = lecture_min(affiche)
            premier_reseau = s["reseau"] and i == 0
            if rec == "revelation" and p.get("avecNom"):
                # le nom arrive à max(1,2 ; D − 3,0) + 0,3 s et tient jusqu'à la fin du plan
                dispo = d - max(1.2, d - 3.0) - 0.3
                if dispo + 0.01 < lmin:
                    rap.err("%s : %s laisse %.1f s au nom ; il faut %.1f s (plan d'au moins 4,0 s)" % (etiquette, pid, dispo, lmin), pid, sid)
            elif rec == "empilement" and p.get("avecNom"):
                besoin = duree_nom_empilement(p.get("nCaptures") or 0)
                if d + 0.01 < besoin:
                    rap.err("%s : %s dure %.1f s ; les écrans puis le nom demandent %.1f s" % (etiquette, pid, d, besoin), pid, sid)
            elif rec in ("carton", "mot-sur-image") and affiche.get("type") in ("phrase", "mot"):
                n = nb_mots(affiche.get("contenu"))
                aff = affiche.get("affichage") or ("groupes" if n > 6 else "bloc")
                if affiche.get("type") == "mot":
                    aff = "bloc"
                etapes = 1 if aff == "bloc" else (n if aff == "mot-a-mot" else (len(affiche.get("groupes") or []) or (2 if n <= 9 else 3)))
                besoin = besoin_texte(rec, affiche, premier_reseau)
                if d + 0.01 < besoin:
                    rap.err("%s : %s dure %.1f s ; il faut %.1f s pour lire « %s » (1,2 s + 0,3 s × %d mots, plus l'entrée et la sortie%s ; grammaire-film.md § 6.4)" % (
                        etiquette, pid, d, besoin, (affiche.get("contenu") or "")[:50], n, ", construit en %d temps" % etapes if etapes > 1 else ""), pid, sid)
                elif d + 0.01 < math.ceil((lecture_conseil(affiche) + 0.55) * 10 - 1e-6) / 10.0:
                    rap.avert("%s : %s tient %.1f s ; durée conseillée (1,5 s + 0,3 s × mots, entrée et sortie comprises) : %.1f s" % (
                        etiquette, pid, d, math.ceil((lecture_conseil(affiche) + 0.55) * 10 - 1e-6) / 10.0), pid, sid)
            elif affiche.get("type") == "chiffre":
                if d + 0.01 < lmin + 0.6:
                    rap.err("%s : %s dure %.1f s ; le chiffre et son libellé demandent %.1f s" % (etiquette, pid, d, lmin + 0.6), pid, sid)
            elif affiche.get("type") == "libelle":
                if d + 0.01 < 0.6 + lmin:
                    rap.err("%s : %s dure %.1f s ; le libellé demande %.1f s" % (etiquette, pid, d, 0.6 + lmin), pid, sid)
            else:  # nom de fin
                dispo = d - (0.0 if premier_reseau else 0.3)
                if dispo + 0.01 < lmin:
                    rap.err("%s : %s laisse %.1f s au nom ; il faut %.1f s (nom ≥ 2,5 s : grammaire-film.md § 6.4)" % (etiquette, pid, dispo, lmin), pid, sid)
            temps_texte += min(d, max(lmin, d - 0.4))
            # deux cartons de suite sans image
            est_carton = rec == "carton"
            if est_carton and precedent_texte:
                rap.avert("%s : %s suit un autre carton sans plan d'image entre les deux (grammaire-film.md § 6.7)" % (etiquette, pid), pid, sid)
            precedent_texte = est_carton
            controle_zone(film, s, p, affiche, fmt, fmt_nom, rap)
        else:
            precedent_texte = False

    if total > 0 and not s["reseau"]:
        # assez de matière ? un visuel nourrit 2 à 3 plans : 7 visuels pour 60 s, 10 pour 90 s, 14 pour 120 s
        distincts = set()
        for q in film.get("plans", []):
            for v in (q.get("visuels") or {}).values():
                for f in (v if isinstance(v, list) else [v]):
                    if f:
                        distincts.add(f)
        besoin = int(round(7 + max(0.0, total - 60) * 7 / 60.0))
        if len(distincts) < besoin:
            rap.avert("film : %d visuels distincts pour %.0f s ; il en faut environ %d, sinon le film se répète "
                      "(grammaire-film.md § 3) : demander d'autres visuels ou raccourcir" % (len(distincts), total, besoin))
        par_min = n_cartons / (total / 60.0)
        part = temps_texte / total
        if par_min < 6 or par_min > 10:
            rap.avert("film : %.1f cartons par minute ; convention 6 à 10 sans voix (grammaire-film.md § 6.2)" % par_min)
        if part < 0.30 or part > 0.45:
            rap.avert("film : texte à l'écran %.0f %% du temps ; convention 30 à 45 %% (grammaire-film.md § 6.2 ; attendu au-dessus pour un logiciel)" % (part * 100))
        coupes = len(plans) / (total / 60.0)
        if coupes < 12 or coupes > 33:
            rap.avert("film : %.0f plans par minute ; repères 19 (révélation) à 33 (logiciel)" % coupes)
        # place du nom et de la révélation
        fins = [p for p in plans if p["recette"] == "fin"]
        if not fins:
            rap.avert("film : pas de plan « fin » ; sans voix, le film finit sur le nom (convention)")
        else:
            f = fins[0]
            pos = f["debut"] / total
            if pos < 0.76:
                rap.avert("film : le nom arrive à %.0f %% ; jamais avant 76 %% dans le corpus (0/20)" % (pos * 100), f["id"], sid)
            if plans[-1]["recette"] != "fin":
                rap.avert("film : le dernier plan n'est pas la fin (le nom ferme le film, 21/24)")
        revs = [p for p in plans if p["recette"] == "revelation"]
        if revs and revs[0]["debut"] / total < 0.60:
            rap.avert("film : révélation de l'objet entier à %.0f %% ; observée après 60 %% dans 13 films sur 14" % (revs[0]["debut"] / total * 100), revs[0]["id"], sid)
        if plans and plans[0]["recette"] == "fin":
            rap.err("film : le nom ouvre le film ; le nom est la chute, jamais le titre")
    if s["reseau"] and plans:
        if plans[0]["recette"] == "noir":
            rap.err("%s : ouvre sur du noir ; image 0 pleine en réseau" % etiquette)
        if plans[0]["recette"] == "fin":
            rap.err("%s : ouvre sur le nom ; pas de logo ni de nom en ouverture (21/24)" % etiquette)
        visibles = [p for p in plans if (p["recette"] in VISUELLES or p.get("fondImage")) and p["debut"] < 3.0]
        if not visibles:
            rap.avert("%s : aucun plan de produit avant 3 s (declinaisons.md § 2)" % etiquette)
        premier_txt = plans[0].get("texte")
        if not premier_txt:
            rap.avert("%s : pas de carton lisible dans la première seconde (le fil se regarde son coupé : declinaisons.md § 2)" % etiquette)
        for lim, cartons, mots in BUDGETS:
            if total <= lim:
                if n_cartons > cartons:
                    rap.avert("%s : %d textes ; budget du gabarit %d (declinaisons.md § 3.2)" % (etiquette, n_cartons, cartons))
                if mots_total > mots:
                    rap.avert("%s : %d mots ; budget du gabarit %d (declinaisons.md § 3.2)" % (etiquette, mots_total, mots))
                break
        if plans[-1]["recette"] != "fin":
            rap.avert("%s : ne finit pas sur le nom (carton de fin 2,5 à 3,5 s)" % etiquette)
        elif not (2.4 <= plans[-1]["duree"] <= 4.6):
            rap.avert("%s : carton de fin de %.1f s ; 2,5 à 3,5 s conseillé" % (etiquette, plans[-1]["duree"]), plans[-1]["id"], sid)


def controle_zone(film, s, p, t, fmt, fmt_nom, rap):
    """Largeur des lignes et hauteur du bloc dans la zone sûre du format."""
    sid, pid = s["id"], p["id"]
    x0, y0, x1, y1 = fmt["sure"]
    typ = t.get("type")
    rec = p["recette"]
    tailles = fmt["tailles"]
    gras = typ in ("mot", "nom", "libelle", "chiffre")
    if typ == "nom":
        mv = {}
        for q in film.get("plans", []):
            if q.get("id") == pid:
                mv = q.get("mouvement") or {}
        taille = tailles["nomDiscret"] if mv.get("taille") == "discret" else tailles["nomHeros"]
    elif typ == "mot":
        taille = tailles["mot"]
    elif typ == "libelle":
        taille = tailles["libelle"]
    elif typ == "chiffre":
        return
    else:
        taille = tailles["carton"] * (1.15 if rec == "mot-sur-image" else 1)
    largeur = fmt["ligneMax"]
    if typ == "libelle":
        largeur = fmt["W"] * (0.22 if fmt_nom == "16:9" else 0.8 if fmt_nom == "9:16" else 0.84)
    k = LARGEUR["gras"] if gras else LARGEUR["regular"]
    car_max = max(6, int(largeur / (k * taille)))
    if typ == "phrase":
        car_max = min(car_max, fmt["carMax"])
    contenu = t.get("contenu") or ""
    # lignes réelles du moteur si disponibles
    reel = None
    for x in (p.get("textes") or []):
        if x.get("contenu") == contenu:
            reel = x
    if reel:
        n_lignes, taille_eff = reel.get("lignes", 1), reel.get("taille", taille)
    else:
        lignes, taille_eff = lignes_estimees(contenu, fmt, taille, gras, car_max, fmt_nom == "9:16", t.get("groupes"))
        n_lignes = len(lignes)
    mot_long = max([len(w) for w in contenu.split()] or [0])
    if mot_long * k * taille_eff > largeur + 1:
        rap.err("%s (%s) : %s : le mot le plus long ne tient pas dans la ligne (%d px)" % ("film" if sid == "film" else sid, fmt_nom, pid, largeur), pid, sid)
    if taille_eff < taille * 0.95:
        rap.avert("%s (%s) : %s : texte réduit à %d px pour tenir (corps prévu %d)" % ("film" if sid == "film" else sid, fmt_nom, pid, taille_eff, taille), pid, sid)
    h_bloc = n_lignes * taille_eff * 1.18
    if h_bloc > (y1 - y0) * 0.5:
        rap.err("%s (%s) : %s : bloc de %d lignes trop haut pour la zone sûre" % ("film" if sid == "film" else sid, fmt_nom, pid, n_lignes), pid, sid)
    elif fmt_nom == "9:16" and n_lignes > 4 and typ == "phrase":
        rap.avert("%s (9:16) : %s : %d lignes ; viser 2 à 3 lignes en vertical" % (sid, pid, n_lignes), pid, sid)
    for l in (contenu.split() and [contenu]):
        if typ == "phrase" and len(l) > fmt["carMax"] and n_lignes == 1:
            rap.avert("%s (%s) : %s : ligne de %d caractères ; %d au plus" % (sid, fmt_nom, pid, len(l), fmt["carMax"]), pid, sid)


def controle_contraste(film, rap):
    c = (film.get("theme") or {}).get("couleurs") or {}
    paires = [("texte_sur_sombre", "fond_sombre"), ("texte_sur_clair", "fond_clair")]
    for t, f in paires:
        if hex_rgb(c.get(t)) and hex_rgb(c.get(f)):
            r = contraste(c[t], c[f])
            if r < 4.5:
                rap.err("theme : contraste %s / %s = %.1f:1 ; 4,5:1 au moins" % (t, f, r))
            elif r < 7:
                rap.avert("theme : contraste %s / %s = %.1f:1 ; viser 7:1" % (t, f, r))
    if hex_rgb(c.get("accent")):
        meilleurs = max(contraste(c["accent"], c.get(x)) for x in ("texte_sur_sombre", "texte_sur_clair") if hex_rgb(c.get(x)))
        if any((p.get("fond") == "accent") for p in film.get("plans", [])) and meilleurs < 4.5:
            rap.err("theme : aucun texte ne se lit sur l'accent (%.1f:1) ; ne pas utiliser fond « accent »" % meilleurs)
    if any(p.get("recette") == "mot-sur-image" for p in film.get("plans", [])):
        rap.avert("mot-sur-image : vérifier le contraste réel sur l'image (≥ 7:1 conseillé) avec « npx hyperframes check »")


def main(argv):
    if not argv or argv[0].startswith("--"):
        print(__doc__)
        return 2
    fichier = argv[0]
    en_json = "--json" in argv
    resolu = None
    if "--resolu" in argv:
        resolu = argv[argv.index("--resolu") + 1]
    rap = Rapport()
    try:
        with open(fichier, encoding="utf-8") as f:
            film = json.load(f)
    except Exception as e:  # noqa
        rap.err("film.json illisible : %s" % e)
        film = None
    if film is not None:
        # mêmes valeurs par défaut que le moteur
        theme = film.setdefault("theme", {})
        coul = dict(DEFAUTS_COULEURS)
        coul.update(theme.get("couleurs") or {})
        theme["couleurs"] = coul
        base = os.path.dirname(os.path.abspath(fichier))
        controle_structure(film, base, rap)
        controle_contraste(film, rap)
        if resolu:
            with open(resolu, encoding="utf-8") as f:
                sorties = json.load(f)["sorties"]
        else:
            sorties = resoudre_standalone(film, rap) if not rap.erreurs else []
        for s in sorties:
            controle_sortie(film, s, rap)
    if en_json:
        print(json.dumps({"erreurs": rap.erreurs, "avertissements": rap.avertissements, "parPlan": rap.par_plan}, ensure_ascii=False))
    else:
        print("Contrôle de %s" % fichier)
        print("  %d erreur(s), %d avertissement(s)" % (len(rap.erreurs), len(rap.avertissements)))
        for e in rap.erreurs:
            print("  ✗ " + e)
        for a in rap.avertissements:
            print("  · " + a)
        if not rap.erreurs:
            print("  → aucun blocage : la planche peut être faite (node build_film.js film.json --planche).")
    return 1 if rap.erreurs else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
