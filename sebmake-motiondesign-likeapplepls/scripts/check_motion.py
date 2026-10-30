#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
check_motion.py: checks a motion.json before the script is generated (Python 3.9, no dependencies).

    python3 check_motion.py motion.json            readable report; exit 0 = no errors, 1 = errors
    python3 check_motion.py motion.json --json     JSON report
    python3 check_motion.py motion.json --sans-node  timing plan estimated without Node (less precise)

What it checks:
  - structure: fields, types, known recipes and transitions, unique ids, links (avec, parent, ancien, nom),
    HEX colors, banned fonts (the grammar, never the brand);
  - durations and amplitudes inside the measured ranges (error); departure from a convention (warning);
  - overlaps the principles forbid: more than one major move at a time, transitions that
    overlap, row arrivals or voice-paced list lines that overlap, black that is too short;
  - exits animated other than by a cut or a fade, a downward or repeated sweep, mixed eras;
  - texts too long for their time on screen, words per type, estimated line width;
  - numbers without a source, remaining [TO PROVIDE]; missing files (a neutral placeholder will be drawn);
  - text contrast against the background.
The exact timing plan comes from `node build_motion.mjs <motion.json> --plan` (same folder as this script).
The measured thresholds come from recettes.json (exported from motion_lib.mjs); conventions are named as such.
"""
import json
import os
import re
import subprocess
import sys

ICI = os.path.dirname(os.path.abspath(__file__))
TYPES = ["titre", "phrase", "surtitre", "liste", "chiffre", "logo", "image", "capture", "icone", "forme", "fond", "nul-camera"]
TEXTES = ["titre", "phrase", "surtitre", "liste", "chiffre"]
FORMATS = {"16:9": (1920, 1080), "9:16": (1080, 1920), "1:1": (1080, 1080)}
CADENCES = [24, 25, 29.97, 30, 50, 60]
POLICES_INTERDITES = ["sf pro", "sfpro", "sf-pro", "sf compact", "sf mono", "new york", "newyork", "san francisco", "sanfrancisco",
                      "-apple-system", "blinkmacsystemfont", "system-ui", "myriad", "apple garamond", "applegaramond"]
COMPLEMENTS = ["assombrir-autour", "balayage-lumiere", "revelation-lumiere"]
# Maximum words per type: a skill convention (measured instances run from 1 to 8 words; none goes past 12).
MOTS_MAX = {"titre": 6, "phrase": 12, "surtitre": 4, "liste": 6, "libelle": 5}
CHAMPS_ELEMENT = {"id", "type", "contenu", "fichier", "fichiers", "lignes", "groupes", "pieces", "libelle", "source", "position", "taille", "largeur",
                  "ratio", "couleur", "couleur_libelle", "taille_libelle", "position_libelle", "contour", "coins", "forme", "police", "alignement",
                  "interligne", "recette", "debut", "maintien", "fin", "sortie", "options", "puis", "avec", "parent", "profondeur", "camera", "nom",
                  "simultane", "note"}


class Rapport:
    def __init__(self):
        self.items = []

    def ajoute(self, niveau, code, message, element=None):
        self.items.append({"niveau": niveau, "code": code, "element": element, "message": message})

    def erreur(self, code, message, element=None):
        self.ajoute("erreur", code, message, element)

    def alerte(self, code, message, element=None):
        self.ajoute("avertissement", code, message, element)

    def info(self, code, message, element=None):
        self.ajoute("info", code, message, element)


def hexa(c):
    return isinstance(c, str) and re.match(r"^#[0-9A-Fa-f]{6}$", c) is not None


def luminance(h):
    h = h.lstrip("#")
    r, g, b = [int(h[i:i + 2], 16) / 255.0 for i in (0, 2, 4)]
    def lin(c):
        return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4
    return 0.2126 * lin(r) + 0.7152 * lin(g) + 0.0722 * lin(b)


def contraste(a, b):
    la, lb = luminance(a), luminance(b)
    hi, lo = max(la, lb), min(la, lb)
    return (hi + 0.05) / (lo + 0.05)


def mots(texte):
    return [m for m in re.split(r"\s+", str(texte or "").strip()) if re.search(r"\w", m)]


def charger_table():
    with open(os.path.join(ICI, "recettes.json"), encoding="utf-8") as f:
        return json.load(f)


def plan_node(chemin):
    try:
        r = subprocess.run(["node", os.path.join(ICI, "build_motion.mjs"), chemin, "--plan"], capture_output=True, text=True, timeout=60)
        if r.returncode == 0:
            return json.loads(r.stdout)
    except (OSError, ValueError, subprocess.TimeoutExpired):
        pass
    return None


def plan_estime(motion, table):
    """Rough plan without Node: a one-second entrance for a major recipe, presence from debut, maintien, fin."""
    comp = motion.get("comp", {})
    duree = comp.get("duree", 10)
    tous = {e.get("id"): e for e in motion.get("elements", [])}
    out = []
    for e in motion.get("elements", []):
        rec = e.get("recette", "coupe")
        debut = e.get("debut", 0)
        if rec == "avec" and e.get("avec") in tous:
            ref = tous[e["avec"]]
            rec, debut = ref.get("recette", "coupe"), ref.get("debut", 0)
        r = table["recettes"].get(rec, {})
        entree = 1.0 if r.get("majeur") else 0.5
        fin_entree = debut + entree
        if "fin" in e:
            sd = e["fin"]
        elif "maintien" in e:
            sd = fin_entree + e["maintien"]
        else:
            sd = duree
        out.append({"id": e.get("id"), "type": e.get("type"), "recette": rec, "debut": debut, "finEntree": fin_entree, "sortieDebut": sd,
                    "fin": sd + (1.15 if e.get("sortie") == "fondu" else 0), "sortie": e.get("sortie", "coupe"),
                    "mouvements": [{"de": debut, "a": fin_entree, "majeur": True, "quoi": rec}] if r.get("majeur") else [],
                    "options": e.get("options", {}), "puis": [], "avec": e.get("avec") if e.get("recette") == "avec" else None})
    trs = []
    for t in motion.get("transitions", []):
        d = {"fondu-enchaine": 0.54, "passage-noir": 1.5, "glissade": 0.89, "poussee": 0.75, "montee-du-noir": 0.9, "bascule-lumiere": 2.4}.get(t.get("type"), 0.5)
        trs.append({"type": t.get("type"), "temps": t.get("temps", 0), "de": t.get("de", []), "vers": t.get("vers", []), "duree": d,
                    "fin": t.get("temps", 0) + d, "majeur": t.get("type") in ("glissade", "poussee"), "options": t.get("options", {})})
    return {"comp": comp, "elements": out, "transitions": trs, "approche": True}


def verifier_params(rap, nom, options, params, ou, eid):
    for k, v in (options or {}).items():
        if k not in params:
            if k not in ("nom", "ancien", "cible", "temps", "fond", "point", "fenetre", "depuis", "sens", "mode", "entree", "direction", "deplacement"):
                rap.alerte("option-inconnue", "%s: option \"%s\" unknown to the recipe (ignored or passed through as is)" % (ou, k), eid)
            continue
        d = params[k]
        mn, mx = d.get("min"), d.get("max")
        if isinstance(v, (int, float)) and not isinstance(v, bool) and isinstance(mn, (int, float)) and isinstance(mx, (int, float)):
            if v < mn - 1e-9 or v > mx + 1e-9:
                txt = "%s: %s = %s outside the %s range (%s to %s %s; %s)" % (ou, k, v, "measured" if d.get("statut") == "mesuré" else "convention",
                                                                                 mn, mx, d.get("unite", ""), d.get("note", ""))
                if d.get("statut") == "mesuré":
                    rap.erreur("hors-mesure", txt, eid)
                else:
                    rap.alerte("hors-convention", txt, eid)


def chevauche(a0, a1, b0, b1, marge=1.0 / 30):
    return a0 < b1 - marge and b0 < a1 - marge


def controler(motion, chemin, sans_node=False):
    rap = Rapport()
    table = charger_table()
    R, TR = table["recettes"], table["transitions"]
    base = os.path.dirname(os.path.abspath(chemin))

    # ── composition and theme ──
    comp = motion.get("comp") or {}
    if not comp:
        rap.erreur("comp", "\"comp\" block missing")
    fmt = comp.get("format", "16:9")
    if fmt not in FORMATS and not (comp.get("largeur") and comp.get("hauteur")):
        rap.erreur("format", "unknown format \"%s\": 16:9, 9:16 or 1:1 (or largeur and hauteur)" % fmt)
    if fmt in ("9:16", "1:1"):
        rap.info("format", "format %s: no vertical or square format in the corpus; distances and sizes in u (1 %% of the short side): convention" % fmt)
    W, H = FORMATS.get(fmt, (comp.get("largeur", 1920), comp.get("hauteur", 1080)))
    W, H = comp.get("largeur", W), comp.get("hauteur", H)
    U = min(W, H) / 100.0
    if comp.get("cadence", 30) not in CADENCES:
        rap.alerte("cadence", "unusual frame rate %s (24, 25, 29.97, 30, 50 or 60)" % comp.get("cadence"))
    duree = comp.get("duree")
    if not isinstance(duree, (int, float)) or duree <= 0:
        rap.erreur("duree", "comp.duree must be a positive number of seconds")
        duree = 10
    epoque = comp.get("epoque", "2024-2026")
    if epoque not in ("2024-2026", "2019-2020"):
        rap.erreur("epoque", "unknown era \"%s\": 2024-2026 or 2019-2020" % epoque)
    theme = motion.get("theme") or {}
    couleurs = dict({"fond": "#0E1013", "texte": "#F4F4F2", "secondaire": "#9A9CA3", "accent": "#4C8DFF", "voile": "#000000"}, **(theme.get("couleurs") or {}))
    for k, v in couleurs.items():
        if not hexa(v):
            rap.erreur("couleur", "theme.couleurs.%s = %s: a #RRGGBB HEX is expected" % (k, v))
    for role, liste in (theme.get("polices") or {}).items():
        for nom in (liste if isinstance(liste, list) else [liste]):
            n = str(nom).lower().replace("_", " ")
            if any(x in n for x in POLICES_INTERDITES):
                rap.erreur("police-marque", "font \"%s\" (%s): a brand's own font; the skill borrows the grammar, never the brand" % (nom, role))
    def couleur(c, defaut):
        if hexa(c):
            return c
        return couleurs.get(c or defaut, couleurs.get(defaut))
    fond_comp = couleur(comp.get("fond"), "fond")

    # ── elements: structure ──
    els = motion.get("elements") or []
    if not els:
        rap.erreur("elements", "no elements")
    ids = {}
    for e in els:
        eid = e.get("id")
        if not eid:
            rap.erreur("id", "element without an id: %s" % json.dumps(e, ensure_ascii=False)[:80])
            continue
        if eid in ids:
            rap.erreur("id", "duplicate id: %s" % eid, eid)
        ids[eid] = e
    for e in els:
        eid = e.get("id")
        for k in e:
            if k not in CHAMPS_ELEMENT and not k.startswith("_"):
                rap.alerte("champ", "unknown field \"%s\" (ignored)" % k, eid)
        typ = e.get("type")
        if typ not in TYPES:
            rap.erreur("type", "unknown type \"%s\" (%s)" % (typ, ", ".join(TYPES)), eid)
            continue
        rec = e.get("recette", "coupe")
        if rec not in R:
            rap.erreur("recette", "unknown recipe \"%s\" (see references/motion-spec.md, § 4)" % rec, eid)
            continue
        if typ not in R[rec]["types"]:
            rap.erreur("recette-type", "recipe %s does not apply to a %s element (allowed types: %s)" % (rec, typ, ", ".join(R[rec]["types"])), eid)
        if rec == "avec":
            if e.get("avec") not in ids:
                rap.erreur("avec", "\"avec\" must name the main element (the kicker arrives with its word: 8 out of 11)", eid)
        elif typ == "surtitre" and rec != "coupe":
            rap.alerte("surtitre-seul", "a kicker has no animation of its own: it arrives with its word (8 out of 11, gap ≤ 0.06 s); prefer \"recette\": \"avec\"", eid)
        if e.get("parent") is not None and (e["parent"] not in ids or ids[e["parent"]].get("type") != "nul-camera"):
            rap.erreur("parent", "parent \"%s\": an element of type nul-camera is expected" % e.get("parent"), eid)
        if e.get("sortie", "coupe") not in ("coupe", "fondu"):
            rap.erreur("sortie", "exit \"%s\": text and objects leave by a cut (15 out of 18) or a fade (3); no exit moves, shrinks or blurs (0 out of 18)" % e.get("sortie"), eid)
        if "debut" in e and isinstance(e["debut"], (int, float)) and e["debut"] < 0:
            rap.erreur("debut", "negative start", eid)
        if not isinstance(e.get("position", [50, 50]), list) or len(e.get("position", [50, 50])) != 2:
            rap.erreur("position", "position = [x %, y %] expected", eid)
        verifier_params(rap, rec, e.get("options"), R[rec]["params"], rec, eid)
        o = e.get("options") or {}
        for lien in ("ancien", "nom"):
            if lien in o and o[lien] not in ids:
                rap.erreur("lien", "options.%s = \"%s\": element not found" % (lien, o[lien]), eid)
        if rec in ("mot-remplace", "mot-fondu-enchaine", "mot-glisse") and "ancien" not in o:
            rap.erreur("lien", "%s needs options.ancien (the word that leaves)" % rec, eid)
        if rec == "nom-remonte" and "nom" not in o:
            rap.erreur("lien", "nom-remonte needs options.nom (the name that rises: 5 out of 5)", eid)
        rep = R[rec].get("epoque", "toutes")
        if rep not in ("toutes", epoque):
            rap.alerte("epoque", "recipe %s dated %s in a %s film: pick one era and stick to it (convention; the arrival curve changes from one era to the other: 21 instances in 2019-2020, 56 in 2024-2026)" % (rec, rep, epoque), eid)
        balayages = 0
        for q in e.get("puis") or []:
            qr = q.get("recette")
            if qr not in COMPLEMENTS:
                rap.erreur("puis", "\"puis\" accepts %s; \"%s\" refused" % (", ".join(COMPLEMENTS), qr), eid)
                continue
            if typ not in R[qr]["types"]:
                rap.erreur("recette-type", "%s does not apply to a %s element" % (qr, typ), eid)
            verifier_params(rap, qr, q.get("options"), R[qr]["params"], "puis/" + qr, eid)
            if qr == "balayage-lumiere":
                balayages += 1
                if (q.get("options") or {}).get("sens") == "bas":
                    rap.erreur("balayage-bas", "downward sweep: never seen (0 out of 11; left 4, up 4, right 3)", eid)
            if qr == "assombrir-autour" and (q.get("options") or {}).get("niveau", 40) >= 75:
                rap.erreur("voile-noir", "scrim at %s %%: never all the way to black (max 73 %%, 20 out of 20)" % (q.get("options") or {}).get("niveau"), eid)
        if rec == "balayage-lumiere":
            balayages += 1
        if balayages > 1:
            rap.erreur("balayage-repete", "%d sweeps on the same element: one pass per shot (11 out of 11)" % balayages, eid)
        # files
        fichiers = []
        if e.get("fichier"):
            fichiers.append(e["fichier"])
        fichiers += [f for f in (e.get("fichiers") or []) if f]
        fichiers += [p.get("fichier") for p in (e.get("pieces") or []) if p.get("fichier")]
        for f in fichiers:
            chem = f if os.path.isabs(f) else os.path.join(base, f)
            if not os.path.exists(chem):
                rap.alerte("fichier-absent", "missing file: %s → a neutral placeholder (frame and diagonals) will be drawn" % f, eid)
        if typ in ("image", "capture", "icone") and not fichiers and rec != "eclate":
            rap.alerte("fichier-absent", "no file: a neutral placeholder will be drawn", eid)
        if rec == "empilement" and len(e.get("fichiers") or []) < 2:
            rap.erreur("empilement", "empilement needs \"fichiers\" (at least two screens)", eid)
        if rec == "carton-groupes" and len(e.get("groupes") or []) < 2:
            rap.erreur("groupes", "carton-groupes needs \"groupes\" (at least two meaning groups; never word by word: 0 out of 145)", eid)
        if typ == "liste" and not e.get("lignes"):
            rap.erreur("lignes", "a list needs \"lignes\"", eid)
        # numbers and sources
        contenu = " ".join([str(e.get("contenu") or "")] + [str(x) for x in (e.get("lignes") or [])] + [str(x) for x in (e.get("groupes") or [])])
        source_ = str(e.get("source") or "")
        # [TO PROVIDE]; the French placeholder of older files still counts
        a_fournir = any(x in contenu.upper() or x in source_.upper() for x in ("[TO PROVIDE]", "[À FOURNIR]", "[A FOURNIR]"))
        if typ == "chiffre":
            if a_fournir:
                rap.alerte("a-fournir", "number [TO PROVIDE]: the value and its source must be given before release", eid)
            elif re.search(r"\d", contenu) and not str(e.get("source") or "").strip():
                rap.erreur("source", "number \"%s\" without \"source\": no number without a source" % contenu.strip(), eid)
            if "compteur" in json.dumps(o) or "compte" in o:
                rap.erreur("compteur", "the hero number never counts up (0 out of 27): it arrives in one piece, scale animates it", eid)
        elif typ in TEXTES:
            if a_fournir:
                rap.alerte("a-fournir", "text contains [TO PROVIDE]", eid)
            elif re.search(r"\d", contenu) and not str(e.get("source") or "").strip():
                rap.alerte("source", "the text contains a number without \"source\"", eid)

    # ── timing plan ──
    pl = None if sans_node else plan_node(chemin)
    approche = pl is None
    if approche:
        pl = plan_estime(motion, table)
        rap.info("plan", "timing plan estimated without Node: entrance durations are approximate (run with Node for an exact check)")
    P = {p["id"]: p for p in pl["elements"]}

    for e in els:
        eid = e.get("id")
        p = P.get(eid)
        if not p or e.get("type") not in TYPES or e.get("recette", "coupe") not in R:
            continue
        typ, rec = e["type"], p["recette"]
        if p["fin"] > duree + 1e-6 or p["sortieDebut"] > duree + 1e-6:
            rap.alerte("hors-comp", "the element lasts past the composition (%.2f s > %s s)" % (p["fin"], duree), eid)
        if p["sortieDebut"] < p["finEntree"] - 1e-6:
            rap.erreur("sortie-avant-entree", "the exit (%.2f s) falls before the entrance ends (%.2f s)" % (p["sortieDebut"], p["finEntree"]), eid)
        # reading
        if typ in TEXTES and typ != "surtitre":
            m = mots(e.get("contenu")) if typ != "liste" else sum((mots(l) for l in e.get("lignes") or []), [])
            if e.get("groupes"):
                m = sum((mots(g) for g in e["groupes"]), [])
            if typ == "chiffre":
                m = ["chiffre"] + mots(e.get("libelle"))
            visible = p["sortieDebut"] - p["debut"]
            besoin = 1.2 + 0.3 * len(m)
            if rec == "liste-au-fil":
                o = p.get("options") or {}
                besoin += (len(e.get("lignes") or []) - 1) * o.get("intervalle", 2.0)
            if visible + 1e-6 < besoin:
                (rap.erreur if visible < 0.6 * besoin else rap.alerte)("lecture", "%d word(s) visible %.2f s: needs %.1f s (1.2 s + 0.3 s per word: reading convention; error below 60 %% of that time)" % (len(m), visible, besoin), eid)
            maxi = MOTS_MAX.get(typ)
            if typ == "liste":
                for l in e.get("lignes") or []:
                    if len(mots(l)) > MOTS_MAX["liste"]:
                        rap.alerte("mots", "line of %d words (%d at most, convention)" % (len(mots(l)), MOTS_MAX["liste"]), eid)
            elif maxi and len(m) > maxi and not e.get("groupes"):
                (rap.erreur if typ == "phrase" and len(m) > 12 else rap.alerte)("mots", "%d words for a %s (%d at most: convention; no measured instance above 12)" % (len(m), typ, maxi), eid)
            if typ == "chiffre" and e.get("libelle") and len(mots(e["libelle"])) > MOTS_MAX["libelle"]:
                rap.alerte("mots", "label of %d words (5 at most, convention)" % len(mots(e["libelle"])), eid)
            # estimated width (0.55 × font size per character for a sans serif: convention)
            tailles = {"titre": 10, "phrase": 5.4, "liste": 4.4, "chiffre": 30}
            corps = (e.get("taille") or tailles.get(typ, 6)) * U
            lignes = e.get("lignes") or (e["groupes"] and [" ".join(e["groupes"])] if e.get("groupes") else None) or str(e.get("contenu") or "").split("\n")
            for l in lignes:
                larg = len(str(l)) * 0.55 * corps
                if larg > 0.9 * W:
                    rap.alerte("largeur", "line \"%s\" ≈ %d px for a %d px frame: break the line or reduce the size" % (str(l)[:30], larg, W), eid)
        # contrast with the solid background present when the text starts (the last "fond" element without a file, else the composition)
        if typ in TEXTES:
            fond = fond_comp
            for f in els:
                pf = P.get(f.get("id"))
                if f.get("type") == "fond" and not f.get("fichier") and pf and pf["debut"] <= p["debut"] + 1e-6 < pf["fin"]:
                    fond = couleur(f.get("couleur"), "fond")
            ct = couleur(e.get("couleur"), "secondaire" if typ == "surtitre" else "texte")
            if hexa(ct) and hexa(fond):
                c = contraste(ct, fond)
                if c < 4.5:
                    rap.alerte("contraste", "contrast %.1f:1 between the text (%s) and the background (%s): 4.5:1 at least (legibility convention)" % (c, ct, fond), eid)
        # recipe-specific rules
        o = p.get("options") or {}
        if rec == "empilement" and o.get("intervalle", 1.67) < o.get("T", 0.79) - 1e-6:
            rap.erreur("empilement-chevauche", "interval %.2f s < one arrival's duration %.2f s: arrivals never overlap (11 out of 11)" % (o.get("intervalle"), o.get("T")), eid)
        if rec == "liste-au-fil" and o.get("intervalle", 2.0) < o.get("T_position", 0.95):
            rap.erreur("liste-chevauche", "a voice-paced line arrives before the previous one has finished", eid)
        if rec == "zoom-detail" and e.get("type") != "nul-camera":
            tient = p["sortieDebut"] - p["finEntree"]
            if tient < 2.5:
                rap.alerte("maintien-detail", "%.1f s on the detail after the zoom: let people look (median hold 7.2 s, p25 2.5 s; 2.5 to 7 s: convention)" % tient, eid)
        if rec == "logo-fin" and not p.get("avec"):
            tient = p["sortieDebut"] - p["finEntree"]
            if tient < 1.25:
                rap.alerte("maintien-nom", "end name held %.2f s: 2.6 s median (1.25 to 4.7; 17 names)" % tient, eid)
            y = (e.get("position") or [50, 50])[1]
            if not 47 <= y <= 51:
                rap.info("place-nom", "end name at %s %% of the height: vertical center between 47 and 51 %% in 15 cases out of 20" % y, eid)
        if rec in ("chiffre-pose", "chiffre-croissance") and o.get("retard_libelle", 0.23) < 0:
            rap.erreur("libelle-avant", "the label arrives after its number (+0.23 s from fade midpoint to fade midpoint, 15 out of 18), never before", eid)
        if rec == "assombrir-autour" and o.get("niveau", 40) >= 75:
            rap.erreur("voile-noir", "scrim at %s %%: never all the way to black (max 73 %%, 20 out of 20)" % o.get("niveau"), eid)

    # ── empty time after a cut: from the cut to the first visible trace (debut + the curve's soft start) ──
    fins = sorted(set([0.0] + [round(p["fin"], 2) for p in pl["elements"] if p["fin"] < duree - 1e-6]))
    for e in els:
        p = P.get(e.get("id"))
        if not p or p["recette"] in ("coupe", "produit-entree", "mot-remplace") or e.get("type") in ("fond", "nul-camera") or p.get("avec"):
            continue
        if p["recette"] == "logo-fin" and (p.get("options") or {}).get("entree") == "coupe":
            continue
        avant = [f for f in fins if f <= p["debut"] + 0.05 and p["debut"] - f < 0.6]
        if not avant:
            continue
        coupe = max(avant)
        vide = p["debut"] - coupe + (p.get("apparition") or 0)
        if vide < 0.10:
            rap.info("temps-vide", "empty background visible %.2f s after the cut at %.2f s: it usually holds 0.13 to 0.23 s before elements enter (135 cases); only the side entrance starts on the cut (8 out of 8)" % (vide, coupe), e.get("id"))
        elif vide > 0.30 and (p.get("apparition") or 0) > 0:
            rap.alerte("temps-vide", "empty background visible %.2f s after the cut at %.2f s (debut at +%.2f s, then %.2f s before 2 %% opacity): 0.13 to 0.23 s measured (135 cases); move \"debut\" earlier by about %.2f s (tolerance 0.30 s: convention)"
                       % (vide, coupe, p["debut"] - coupe, p.get("apparition") or 0, vide - 0.18), e.get("id"))

    # ── transitions ──
    trs = motion.get("transitions") or []
    for t in trs:
        typ = t.get("type")
        if typ not in TR:
            rap.erreur("transition", "unknown transition \"%s\" (%s)" % (typ, ", ".join(TR)))
            continue
        for k in ("de", "vers"):
            for i in t.get(k) or []:
                if i not in ids:
                    rap.erreur("transition-lien", "transition %s at %s s: \"%s\" not found" % (typ, t.get("temps"), i))
        if not isinstance(t.get("temps"), (int, float)):
            rap.erreur("transition-temps", "transition %s without \"temps\"" % typ)
        verifier_params(rap, typ, t.get("options"), TR[typ]["params"], "transition " + typ, None)
        if typ == "raccord" and (t.get("de") or []) and (t.get("vers") or []) and t["de"][0] in ids and t["vers"][0] in ids:
            a, b = ids[t["de"][0]], ids[t["vers"][0]]
            pa, pb = a.get("position") or [50, 50], b.get("position") or [50, 50]
            d = (((pa[0] - pb[0]) * W / 100.0) ** 2 + ((pa[1] - pb[1]) * H / 100.0) ** 2) ** 0.5 / U
            ta, tb = a.get("taille"), b.get("taille")
            if d > 5:
                rap.alerte("raccord", "match cut %s → %s: the center moves %.1f u; it moves 3.2 %% H at the median, 5 %% H or less in 13 cases out of 22" % (t["de"][0], t["vers"][0], d))
            if isinstance(ta, (int, float)) and isinstance(tb, (int, float)) and ta > 0 and not 0.90 <= tb / ta <= 1.12:
                rap.alerte("raccord", "match cut %s → %s: the size changes by ×%.2f; between ×0.90 and ×1.12 in 21 cases out of 22" % (t["de"][0], t["vers"][0], tb / ta))
        if typ in ("glissade", "poussee") and (t.get("options") or {}).get("sens") in ("haut", "bas"):
            rap.erreur("glissade-verticale", "vertical slide: never seen (horizontal 32 out of 32)")
    tp = [x for x in pl["transitions"] if x["type"] in TR]
    for i in range(len(tp)):
        for j in range(i + 1, len(tp)):
            a, b = tp[i], tp[j]
            if a["duree"] > 0 and b["duree"] > 0 and chevauche(a["temps"], a["fin"], b["temps"], b["fin"]):
                rap.erreur("transitions-chevauchent", "%s (%.2f–%.2f s) and %s (%.2f–%.2f s) overlap: a transition never overlaps the next one (25 out of 25)" % (a["type"], a["temps"], a["fin"], b["type"], b["temps"], b["fin"]))

    # ── one thing at a time: major moves ──
    lies = {}
    for e in els:
        eid = e.get("id")
        groupe = {eid}
        if e.get("avec"):
            groupe.add(e["avec"])
        o = e.get("options") or {}
        if o.get("nom"):
            groupe.add(o["nom"])
        if o.get("ancien"):
            groupe.add(o["ancien"])
        if e.get("parent"):
            groupe.add(e["parent"])
        for g in groupe:
            lies.setdefault(g, set()).update(groupe)
    mvts = []
    for p in pl["elements"]:
        for m in p.get("mouvements") or []:
            if m.get("majeur"):
                mvts.append((p["id"], m["de"], m["a"], m.get("quoi", p["recette"])))
        for q in p.get("puis") or []:
            for m in q.get("mouvements") or []:
                if m.get("majeur"):
                    mvts.append((p["id"], m["de"], m["a"], m.get("quoi", q["recette"])))
    for t in tp:
        if t.get("majeur"):
            mvts.append(("transition " + t["type"], t["temps"], t["fin"], t["type"]))
            for i in (t.get("de") or []) + (t.get("vers") or []):
                lies.setdefault("transition " + t["type"], set()).add(i)
                lies.setdefault(i, set()).add("transition " + t["type"])
    vus = set()
    for i in range(len(mvts)):
        for j in range(i + 1, len(mvts)):
            a, b = mvts[i], mvts[j]
            if a[0] == b[0] or b[0] in lies.get(a[0], set()):
                continue
            ea, eb = ids.get(a[0], {}), ids.get(b[0], {})
            if ea.get("simultane") or eb.get("simultane"):
                continue
            if chevauche(a[1], a[2], b[1], b[2]):
                cle = (a[0], b[0])
                if cle in vus:
                    continue
                vus.add(cle)
                rap.erreur("deux-mouvements", "two major moves at once: %s \"%s\" (%.2f–%.2f s) and %s \"%s\" (%.2f–%.2f s). Elements arrive one after the other (rows 11 out of 11; label +0.23 s, 15 out of 18). Shift one, or link them (avec, options.nom), or set \"simultane\": true if it is intended."
                           % (a[0], a[3], a[1], a[2], b[0], b[3], b[1], b[2]))
    return rap, pl


def main(argv):
    if not argv or argv[0] in ("-h", "--help"):
        print(__doc__)
        return 1
    chemin = argv[0]
    try:
        with open(chemin, encoding="utf-8") as f:
            motion = json.load(f)
    except (OSError, ValueError) as e:
        print("cannot read: %s" % e)
        return 1
    rap, pl = controler(motion, chemin, sans_node="--sans-node" in argv)
    err = [i for i in rap.items if i["niveau"] == "erreur"]
    if "--json" in argv:
        print(json.dumps({"erreurs": len(err), "items": rap.items}, ensure_ascii=False, indent=1))
    else:
        noms = {"erreur": "ERROR", "avertissement": "warning", "info": "info"}
        for niveau in ("erreur", "avertissement", "info"):
            for i in rap.items:
                if i["niveau"] == niveau:
                    print("%-9s %s%s" % (noms[niveau], "[%s] " % i["element"] if i["element"] else "", i["message"]))
        nb = {n: sum(1 for i in rap.items if i["niveau"] == n) for n in ("erreur", "avertissement", "info")}
        print("— %d error(s), %d warning(s), %d info(s) — %s" % (nb["erreur"], nb["avertissement"], nb["info"], os.path.basename(chemin)))
    return 1 if err else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
