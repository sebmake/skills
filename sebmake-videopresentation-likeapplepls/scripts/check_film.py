#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
check_film.py: checks a film.json before the review sheet and the render (Python 3.9, no dependencies).

    python3 check_film.py film.json              # readable report; exit code 0 = nothing blocking, 1 = errors
    python3 check_film.py film.json --json       # JSON report (used by build_film.js)
    python3 check_film.py film.json --resolu R   # also checks the outputs resolved by the engine
                                                 # ("auto" cut-downs, adjusted durations, real lines)

What it checks:
  - structure: required fields, HEX colors, banned fonts, unique ids, known recipes;
  - voice and music: no voice field; local music with confirmed rights, or null;
  - durations: sum of shots against the target (±10%), bounds 60-120 s (film) and 15-60 s (social);
  - reading: card duration from its word count (1.2 s + 0.3 s × words; name ≥ 2.5 s);
  - words: 12 at most per card, 6 at most in one block, 1 to 4 for a label or a name;
  - safe zones and line width per format (9:16, 1:1, 16:9);
  - figures: no figure without a source; [TO PROVIDE] items listed;
  - missing visuals (neutral drawn fallback at render time);
  - position of the name (≥ 76% of the film) and of the reveal (≥ 60%); card pace;
  - contrast of text colors on backgrounds (≥ 4.5:1 required, ≥ 7:1 recommended).
The thresholds come from the corpus analyses (see ../references/film-spec.md, § 7).
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
SIGNATURES = [r"shot on", r"(filmed|recorded|made) (with|on) (an? )?(iphone|ipad|mac)", r"tourn[ée] (avec|sur)", r"film[ée] (avec|sur)", r"\b9:41\b", r"one more thing"]

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
BUDGETS = [(20, 4, 16), (37, 7, 32), (52, 10, 45), (999, 14, 60)]  # (duration ≤, cards, words) — declinaisons.md § 3.2


class Rapport(object):
    def __init__(self):
        self.erreurs, self.avertissements, self.par_plan = [], [], {}

    def _note(self, sortie, plan, msg):
        if plan:
            self.par_plan.setdefault(sortie or "film", {}).setdefault(plan, []).append(msg)

    def err(self, msg, plan=None, sortie=None):
        self.erreurs.append(msg)
        self._note(sortie, plan, "✗ " + msg.split(": ", 1)[-1])

    def avert(self, msg, plan=None, sortie=None):
        self.avertissements.append(msg)
        self._note(sortie, plan, "· " + msg.split(": ", 1)[-1])


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
    """Minimum duration of a card (grammaire-film.md § 6.4), in seconds."""
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
    """Recommended duration (grammaire-film.md § 6.4): 1.5 s + 0.3 s × words, never under 2 s."""
    n = nb_mots(texte.get("contenu") or texte.get("libelle"))
    return max(2.0, 1.5 + 0.3 * n)


def duree_nom_empilement(n_captures):
    """Minimum length of an empilement shot followed by the name in a cut-down (same math as the engine's minimumPlan)."""
    n = min(5, n_captures or 3)
    return math.ceil((0.5 + n * 0.2 + 0.4 + 2.8) * 10) / 10.0


def besoin_texte(rec, t, premier_reseau=False, avec_nom=False, produit="", n_captures=0):
    """Minimum shot duration for its text to be read (same math as the engine's minimumPlan)."""
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
    marge = 0.4 if premier_reseau else (0.6 if rec == "carton" else 0.8)  # entry + exit
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
    """Outputs without the engine: the film as is, and cut-downs with an explicit list (adjusted durations)."""
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
            rap.avert("cut-down %s: \"auto\" selection computed by the engine, checked at build time (build_film.js)" % d.get("id"))
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
            plans[0]["fondImage"] = True  # the engine puts the blurred product behind an opening card
        sorties.append({"id": d.get("id"), "format": d.get("format"), "reseau": True, "cible": cible, "total": t, "plans": plans})
    return sorties


# ---------------------------------------------------------------------------
def controle_structure(film, base, rap):
    meta = film.get("meta") or {}
    for k in ("titre", "produit", "message", "public", "formats", "duree_cible_s"):
        if not meta.get(k):
            rap.err("meta.%s: required field missing" % k)
    # no voice
    def cherche_voix(o, chemin):
        if isinstance(o, dict):
            for k, v in o.items():
                if str(k).lower() in ("voix", "voice", "voiceover", "voix_off", "narration", "tts", "script_voix"):
                    rap.err("%s.%s: no voice in this film (no voice-over, no speech synthesis)" % (chemin, k))
                cherche_voix(v, chemin + "." + str(k))
        elif isinstance(o, list):
            for i, v in enumerate(o):
                cherche_voix(v, "%s[%d]" % (chemin, i))
    cherche_voix(film, "film")

    theme = film.get("theme") or {}
    coul = theme.get("couleurs") or {}
    if not coul.get("accent"):
        rap.err("theme.couleurs.accent: required (a single strong color)")
    for k, v in coul.items():
        if hex_rgb(v) is None:
            rap.err("theme.couleurs.%s: invalid HEX \"%s\"" % (k, v))
    if coul.get("fond_clair", "").upper() in ("#FFFFFF", "#FFF"):
        rap.avert("theme.couleurs.fond_clair: pure white; light backgrounds in the corpus never are (0/7)")
    for role, p in (theme.get("polices") or {}).items():
        for nom in [p.get("famille")] + list(p.get("repli") or []):
            if str(nom or "").lower() in POLICES_INTERDITES:
                rap.err("theme.polices.%s: brand-specific font refused (%s)" % (role, nom))
        if p.get("fichier") and not os.path.exists(os.path.join(base, p["fichier"])):
            rap.avert("theme.polices.%s.fichier not found: %s (the fallback will be used)" % (role, p["fichier"]))
    logo = theme.get("logo") or {}
    for k, v in logo.items():
        if v and not os.path.exists(os.path.join(base, v)):
            rap.avert("theme.logo.%s not found: %s (the end will have no logo)" % (k, v))

    m = film.get("musique")
    if m:
        f = str(m.get("fichier") or "")
        if re.match(r"^https?:", f, re.I):
            rap.err("musique.fichier: web address refused; use a local file provided by the user, or musique: null")
        elif not f or not os.path.exists(os.path.join(base, f)):
            rap.err("musique.fichier not found: %s" % f)
        if m.get("droits_confirmes") is not True:
            rap.err("musique.droits_confirmes must be true (the user has the rights), otherwise musique: null")
        if m.get("caler_coupes"):
            rap.avert("musique.caler_coupes: convention (cutting to the music is not shown in the corpus: 16 cuts out of 62, 16.4 by chance)")

    ids = set()
    for i, p in enumerate(film.get("plans") or []):
        pid = p.get("id")
        if not pid or not re.match(r"^[a-z0-9-]+$", str(pid)):
            rap.err("plans[%d]: id missing or invalid" % i)
        if pid in ids:
            rap.err("plans[%d]: duplicate id %s" % (i, pid))
        ids.add(pid)
        rec = p.get("recette")
        if rec not in RECETTES:
            rap.err("%s: unknown recipe \"%s\" (known: %s)" % (pid, rec, ", ".join(sorted(RECETTES))), pid)
            continue
        if not (float(p.get("duree_s") or 0) > 0):
            rap.err("%s: duree_s missing" % pid, pid)
        if p.get("role") and p["role"] not in ROLES:
            rap.avert("%s: unknown role \"%s\" (%s)" % (pid, p["role"], ", ".join(ROLES)), pid)
        if p.get("transition") and p["transition"] not in TRANSITIONS:
            rap.err("%s: unknown transition \"%s\" (%s)" % (pid, p["transition"], ", ".join(TRANSITIONS)), pid)
        if p.get("fond") and p["fond"] not in FONDS:
            rap.err("%s: unknown fond \"%s\"" % (pid, p["fond"]), pid)
        # visuals
        vis = p.get("visuels") or {}
        for empl in RECETTES[rec]["emplacements"]:
            options = empl.split("|")
            fournis = [o for o in options if vis.get(o)]
            if not fournis:
                rap.avert("%s: visual \"%s\" not provided → neutral drawn fallback" % (pid, empl.replace("|", " or ")), pid)
                continue
            vals = vis[fournis[0]]
            for v in (vals if isinstance(vals, list) else [vals]):
                if v and not os.path.exists(os.path.join(base, v)):
                    rap.avert("%s: visual not found %s → neutral drawn fallback" % (pid, v), pid)
        if rec == "orbite" and vis.get("objet") and not vis.get("vues"):
            rap.avert("%s: a single view → rotation limited to ±12° (beyond that, a flat photo looks like a card)" % pid, pid)
        if rec == "eclate" and not vis.get("pieces"):
            rap.avert("%s: no parts provided → the object is cut into bands (no invented interior)" % pid, pid)
        # texts
        t = p.get("texte")
        if t:
            controle_texte(p, t, rap)
        elif rec == "carton":
            rap.err("%s: a card with no text" % pid, pid)
        mv = p.get("mouvement") or {}
        if rec == "panneau" and mv.get("detail"):
            z = mv["detail"].get("zone")
            if not (isinstance(z, list) and len(z) == 4 and all(0 <= float(v) <= 100 for v in z) and z[0] + z[2] <= 100.5 and z[1] + z[3] <= 100.5):
                rap.err("%s: mouvement.detail.zone must be [x, y, width, height] in %% of the screenshot" % pid, pid)
        if rec == "orbite" and abs(float(mv.get("angle", 12))) > 12:
            rap.avert("%s: angle > 12° brought back to 12° (recettes.md, orbite)" % pid, pid)

    for d in film.get("declinaisons") or []:
        if d.get("format") not in FORMATS:
            rap.err("cut-down %s: unknown format %s (16:9, 9:16, 1:1)" % (d.get("id"), d.get("format")))
        for x in d.get("plans") or []:
            x = {"id": x} if isinstance(x, str) else x
            if x.get("id") not in ids:
                rap.err("cut-down %s: unknown shot %s" % (d.get("id"), x.get("id")))


def controle_texte(p, t, rap):
    pid, rec = p.get("id"), p.get("recette")
    typ = t.get("type")
    if typ not in RECETTES[rec]["textes"]:
        rap.err("%s: text of type \"%s\" not possible in recipe %s (possible: %s)" % (pid, typ, rec, ", ".join(RECETTES[rec]["textes"]) or "none"), pid)
        return
    champs = [t.get("contenu"), t.get("libelle"), t.get("ligne")] + list(t.get("groupes") or [])
    tout = " ".join(str(c) for c in champs if c)
    for sig in SIGNATURES:
        if re.search(sig, tout, re.I):
            rap.err("%s: banned signature or brand phrase (\"%s\")" % (pid, sig), pid)
    if "!" in tout:
        rap.avert("%s: exclamation mark (0 out of 14 sentences in the corpus)" % pid, pid)
    if "[TO PROVIDE" in tout:
        rap.avert("%s: [TO PROVIDE] text to complete" % pid, pid)
    # figures without a source
    sans_marque = re.sub(r"\[TO PROVIDE[^\]]*\]", "", tout)
    if re.search(r"\d", sans_marque) and not t.get("source"):
        rap.err("%s: figure without a source in the text (\"%s\"); a figure comes from the user, with texte.source" % (pid, sans_marque.strip()[:60]), pid)
    if typ == "chiffre":
        if t.get("chiffre") in (None, ""):
            rap.avert("%s: figure not provided → [TO PROVIDE] shown dimmed on screen" % pid, pid)
        elif not t.get("source"):
            rap.err("%s: figure \"%s\" without a source (texte.source)" % (pid, t.get("chiffre")), pid)
        if not t.get("libelle"):
            rap.avert("%s: figure without a label (the label carries the basis of comparison)" % pid, pid)
        return
    c = t.get("contenu") or ""
    n = nb_mots(c)
    if typ in ("phrase", "mot") and not c:
        rap.err("%s: texte.contenu is empty" % pid, pid)
    if typ == "phrase":
        if n > 12:
            rap.err("%s: %d words; 12 at most per card (106 cards out of 109) — split into two cards" % (pid, n), pid)
        elif n > 6 and t.get("affichage") == "bloc":
            rap.avert("%s: %d words shown in one block; beyond 6, build in groups (grammaire-film.md § 6.4)" % (pid, n), pid)
        if c and c.upper() == c and re.search(r"[A-Z]{4,}", c):
            rap.avert("%s: sentence in capitals; sentence case expected (13/14)" % pid, pid)
        if t.get("groupes"):
            if re.sub(r"\s+", " ", " ".join(t["groupes"])).strip() != re.sub(r"\s+", " ", c).strip():
                rap.err("%s: texte.groupes does not add up to texte.contenu (the words never change)" % pid, pid)
            if len(t["groupes"]) > 3:
                rap.avert("%s: more than 3 groups (2 or 3: grammaire-film.md § 6.4)" % pid, pid)
    if typ == "mot" and n > 2:
        rap.avert("%s: a \"mot\" of %d words; 1 or 2 expected" % (pid, n), pid)
    if typ in ("libelle", "nom") and n > 4:
        rap.avert("%s: %s of %d words; 1 to 4 expected" % (pid, typ, n), pid)


def controle_sortie(film, s, rap):
    sid, fmt_nom = s["id"], s["format"]
    fmt = FORMATS.get(fmt_nom)
    if not fmt:
        return
    plans = s["plans"]
    total = s["total"] or sum(p["duree"] for p in plans)
    cible = float(s.get("cible") or 0)
    etiquette = "film" if sid == "film" else "cut-down %s" % sid
    if cible:
        ecart = (total - cible) / cible
        if abs(ecart) > 0.10:
            rap.err("%s: duration %.1f s for a target of %.0f s (gap %+.0f%%, ±10%% allowed)" % (etiquette, total, cible, ecart * 100))
    if not s["reseau"]:
        if total < 60 or total > 120:
            rap.avert("film: %.1f s; the product film aims for 1 to 2 min" % total)
        if total > 68.5:
            rap.avert("film: %.1f s with no voice; no voiceless product film in the corpus runs past 68.5 s → chapters separated by black or a card (convention)" % total)
    else:
        if total < 14 or total > 61:
            rap.avert("%s: %.1f s; cut-downs aim for 15 to 60 s" % (etiquette, total))

    n_cartons, mots_total, temps_texte = 0, 0, 0.0
    precedent_texte = False
    for i, p in enumerate(plans):
        pid, rec, d = p["id"], p["recette"], float(p["duree"])
        t = p.get("texte")
        if d < MIN_RECETTE.get(rec, 1.0) - 0.05:
            rap.avert("%s: %s of %.1f s, under the recipe minimum (%.1f s)" % (etiquette, pid, d, MIN_RECETTE.get(rec, 1.0)), pid, sid)
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
                # the name arrives at max(1.2, D − 3.0) + 0.3 s and holds until the end of the shot
                dispo = d - max(1.2, d - 3.0) - 0.3
                if dispo + 0.01 < lmin:
                    rap.err("%s: %s leaves %.1f s for the name; it needs %.1f s (shot of at least 4.0 s)" % (etiquette, pid, dispo, lmin), pid, sid)
            elif rec == "empilement" and p.get("avecNom"):
                besoin = duree_nom_empilement(p.get("nCaptures") or 0)
                if d + 0.01 < besoin:
                    rap.err("%s: %s lasts %.1f s; the screens and then the name need %.1f s" % (etiquette, pid, d, besoin), pid, sid)
            elif rec in ("carton", "mot-sur-image") and affiche.get("type") in ("phrase", "mot"):
                n = nb_mots(affiche.get("contenu"))
                aff = affiche.get("affichage") or ("groupes" if n > 6 else "bloc")
                if affiche.get("type") == "mot":
                    aff = "bloc"
                etapes = 1 if aff == "bloc" else (n if aff == "mot-a-mot" else (len(affiche.get("groupes") or []) or (2 if n <= 9 else 3)))
                besoin = besoin_texte(rec, affiche, premier_reseau)
                if d + 0.01 < besoin:
                    rap.err("%s: %s lasts %.1f s; reading \"%s\" needs %.1f s (1.2 s + 0.3 s × %d words, plus entry and exit%s; grammaire-film.md § 6.4)" % (
                        etiquette, pid, d, (affiche.get("contenu") or "")[:50], besoin, n, ", built in %d steps" % etapes if etapes > 1 else ""), pid, sid)
                elif d + 0.01 < math.ceil((lecture_conseil(affiche) + 0.55) * 10 - 1e-6) / 10.0:
                    rap.avert("%s: %s holds %.1f s; recommended duration (1.5 s + 0.3 s × words, entry and exit included): %.1f s" % (
                        etiquette, pid, d, math.ceil((lecture_conseil(affiche) + 0.55) * 10 - 1e-6) / 10.0), pid, sid)
            elif affiche.get("type") == "chiffre":
                if d + 0.01 < lmin + 0.6:
                    rap.err("%s: %s lasts %.1f s; the figure and its label need %.1f s" % (etiquette, pid, d, lmin + 0.6), pid, sid)
            elif affiche.get("type") == "libelle":
                if d + 0.01 < 0.6 + lmin:
                    rap.err("%s: %s lasts %.1f s; the label needs %.1f s" % (etiquette, pid, d, 0.6 + lmin), pid, sid)
            else:  # end name
                dispo = d - (0.0 if premier_reseau else 0.3)
                if dispo + 0.01 < lmin:
                    rap.err("%s: %s leaves %.1f s for the name; it needs %.1f s (name ≥ 2.5 s: grammaire-film.md § 6.4)" % (etiquette, pid, dispo, lmin), pid, sid)
            temps_texte += min(d, max(lmin, d - 0.4))
            # two cards in a row with no image
            est_carton = rec == "carton"
            if est_carton and precedent_texte:
                rap.avert("%s: %s follows another card with no image shot in between (grammaire-film.md § 6.7)" % (etiquette, pid), pid, sid)
            precedent_texte = est_carton
            controle_zone(film, s, p, affiche, fmt, fmt_nom, rap)
        else:
            precedent_texte = False

    if total > 0 and not s["reseau"]:
        # enough material? one visual feeds 2 to 3 shots: 7 visuals for 60 s, 10 for 90 s, 14 for 120 s
        distincts = set()
        for q in film.get("plans", []):
            for v in (q.get("visuels") or {}).values():
                for f in (v if isinstance(v, list) else [v]):
                    if f:
                        distincts.add(f)
        besoin = int(round(7 + max(0.0, total - 60) * 7 / 60.0))
        if len(distincts) < besoin:
            rap.avert("film: %d distinct visuals for %.0f s; it needs about %d, otherwise the film repeats itself "
                      "(grammaire-film.md § 3): ask for more visuals or shorten it" % (len(distincts), total, besoin))
        par_min = n_cartons / (total / 60.0)
        part = temps_texte / total
        if par_min < 6 or par_min > 10:
            rap.avert("film: %.1f cards per minute; convention is 6 to 10 with no voice (grammaire-film.md § 6.2)" % par_min)
        if part < 0.30 or part > 0.45:
            rap.avert("film: text on screen %.0f%% of the time; convention is 30 to 45%% (grammaire-film.md § 6.2; higher is expected for software)" % (part * 100))
        coupes = len(plans) / (total / 60.0)
        if coupes < 12 or coupes > 33:
            rap.avert("film: %.0f shots per minute; benchmarks are 19 (reveal) to 33 (software)" % coupes)
        # position of the name and of the reveal
        fins = [p for p in plans if p["recette"] == "fin"]
        if not fins:
            rap.avert("film: no \"fin\" shot; with no voice, the film ends on the name (convention)")
        else:
            f = fins[0]
            pos = f["debut"] / total
            if pos < 0.76:
                rap.avert("film: the name arrives at %.0f%%; never before 76%% in the corpus (0/20)" % (pos * 100), f["id"], sid)
            if plans[-1]["recette"] != "fin":
                rap.avert("film: the last shot is not the end (the name closes the film, 21/24)")
        revs = [p for p in plans if p["recette"] == "revelation"]
        if revs and revs[0]["debut"] / total < 0.60:
            rap.avert("film: reveal of the whole object at %.0f%%; observed after 60%% in 13 films out of 14" % (revs[0]["debut"] / total * 100), revs[0]["id"], sid)
        if plans and plans[0]["recette"] == "fin":
            rap.err("film: the name opens the film; the name is the payoff, never the title")
    if s["reseau"] and plans:
        if plans[0]["recette"] == "noir":
            rap.err("%s: opens on black; frame 0 must be full on social" % etiquette)
        if plans[0]["recette"] == "fin":
            rap.err("%s: opens on the name; no logo or name at the opening (21/24)" % etiquette)
        visibles = [p for p in plans if (p["recette"] in VISUELLES or p.get("fondImage")) and p["debut"] < 3.0]
        if not visibles:
            rap.avert("%s: no product shot before 3 s (declinaisons.md § 2)" % etiquette)
        premier_txt = plans[0].get("texte")
        if not premier_txt:
            rap.avert("%s: no readable card in the first second (feeds are watched with the sound off: declinaisons.md § 2)" % etiquette)
        for lim, cartons, mots in BUDGETS:
            if total <= lim:
                if n_cartons > cartons:
                    rap.avert("%s: %d texts; template budget is %d (declinaisons.md § 3.2)" % (etiquette, n_cartons, cartons))
                if mots_total > mots:
                    rap.avert("%s: %d words; template budget is %d (declinaisons.md § 3.2)" % (etiquette, mots_total, mots))
                break
        if plans[-1]["recette"] != "fin":
            rap.avert("%s: does not end on the name (end card 2.5 to 3.5 s)" % etiquette)
        elif not (2.4 <= plans[-1]["duree"] <= 4.6):
            rap.avert("%s: end card of %.1f s; 2.5 to 3.5 s recommended" % (etiquette, plans[-1]["duree"]), plans[-1]["id"], sid)


def controle_zone(film, s, p, t, fmt, fmt_nom, rap):
    """Line width and block height inside the format's safe zone."""
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
    # the engine's real lines, if available
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
        rap.err("%s (%s): %s: the longest word does not fit on the line (%d px)" % ("film" if sid == "film" else sid, fmt_nom, pid, largeur), pid, sid)
    if taille_eff < taille * 0.95:
        rap.avert("%s (%s): %s: text shrunk to %d px to fit (planned size %d)" % ("film" if sid == "film" else sid, fmt_nom, pid, taille_eff, taille), pid, sid)
    h_bloc = n_lignes * taille_eff * 1.18
    if h_bloc > (y1 - y0) * 0.5:
        rap.err("%s (%s): %s: block of %d lines too tall for the safe zone" % ("film" if sid == "film" else sid, fmt_nom, pid, n_lignes), pid, sid)
    elif fmt_nom == "9:16" and n_lignes > 4 and typ == "phrase":
        rap.avert("%s (9:16): %s: %d lines; aim for 2 to 3 lines in vertical" % (sid, pid, n_lignes), pid, sid)
    for l in (contenu.split() and [contenu]):
        if typ == "phrase" and len(l) > fmt["carMax"] and n_lignes == 1:
            rap.avert("%s (%s): %s: line of %d characters; %d at most" % (sid, fmt_nom, pid, len(l), fmt["carMax"]), pid, sid)


def controle_contraste(film, rap):
    c = (film.get("theme") or {}).get("couleurs") or {}
    paires = [("texte_sur_sombre", "fond_sombre"), ("texte_sur_clair", "fond_clair")]
    for t, f in paires:
        if hex_rgb(c.get(t)) and hex_rgb(c.get(f)):
            r = contraste(c[t], c[f])
            if r < 4.5:
                rap.err("theme: contrast %s / %s = %.1f:1; 4.5:1 at least" % (t, f, r))
            elif r < 7:
                rap.avert("theme: contrast %s / %s = %.1f:1; aim for 7:1" % (t, f, r))
    if hex_rgb(c.get("accent")):
        meilleurs = max(contraste(c["accent"], c.get(x)) for x in ("texte_sur_sombre", "texte_sur_clair") if hex_rgb(c.get(x)))
        if any((p.get("fond") == "accent") for p in film.get("plans", [])) and meilleurs < 4.5:
            rap.err("theme: no text is readable on the accent (%.1f:1); do not use fond \"accent\"" % meilleurs)
    if any(p.get("recette") == "mot-sur-image" for p in film.get("plans", [])):
        rap.avert("mot-sur-image: check the real contrast on the image (≥ 7:1 recommended) with \"npx hyperframes check\"")


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
        rap.err("film.json unreadable: %s" % e)
        film = None
    if film is not None:
        # same defaults as the engine
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
        print("Check of %s" % fichier)
        print("  %d error(s), %d warning(s)" % (len(rap.erreurs), len(rap.avertissements)))
        for e in rap.erreurs:
            print("  ✗ " + e)
        for a in rap.avertissements:
            print("  · " + a)
        if not rap.erreurs:
            print("  → nothing blocking: the review sheet can be made (node build_film.js film.json --planche).")
    return 1 if rap.erreurs else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
