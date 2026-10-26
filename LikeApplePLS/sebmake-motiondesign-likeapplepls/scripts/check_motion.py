#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
check_motion.py : contrôle un motion.json avant de générer le script (Python 3.9, sans dépendance).

    python3 check_motion.py motion.json            rapport lisible ; code 0 = aucune erreur, 1 = erreurs
    python3 check_motion.py motion.json --json     rapport JSON
    python3 check_motion.py motion.json --sans-node  plan temporel estimé sans Node (moins précis)

Ce qui est contrôlé :
  - structure : champs, types, recettes et transitions connues, id uniques, liens (avec, parent, ancien, nom),
    couleurs HEX, polices interdites (la grammaire, jamais la marque) ;
  - durées et amplitudes dans les fourchettes mesurées (erreur) ; écart à une convention (avertissement) ;
  - chevauchements interdits par les principes : plus d'un mouvement majeur à la fois, transitions qui se
    chevauchent, arrivées d'une rangée ou d'une liste au fil de la voix qui se recouvrent, noir trop court ;
  - sorties animées autrement que par coupe ou fondu, balayage vers le bas ou répété, époques mêlées ;
  - textes trop longs pour leur temps à l'écran, mots par type, largeur estimée des lignes ;
  - chiffres sans source, [À FOURNIR] restants ; fichiers manquants (un repli neutre sera dessiné) ;
  - contraste des textes sur le fond.
Le plan temporel exact vient de `node build_motion.mjs <motion.json> --plan` (même dossier que ce script).
Les seuils mesurés viennent de recettes.json (exporté de motion_lib.mjs) ; les conventions sont nommées comme telles.
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
# Mots au plus par type : convention de la skill (les instances mesurées vont de 1 à 8 mots ; aucune ne dépasse 12).
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
    """Plan approché sans Node : entrée d'une seconde pour une recette majeure, présence d'après debut, maintien, fin."""
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
                rap.alerte("option-inconnue", "%s : option « %s » inconnue de la recette (ignorée ou passée telle quelle)" % (ou, k), eid)
            continue
        d = params[k]
        mn, mx = d.get("min"), d.get("max")
        if isinstance(v, (int, float)) and not isinstance(v, bool) and isinstance(mn, (int, float)) and isinstance(mx, (int, float)):
            if v < mn - 1e-9 or v > mx + 1e-9:
                txt = "%s : %s = %s hors de la fourchette %s (%s à %s %s ; %s)" % (ou, k, v, "mesurée" if d.get("statut") == "mesuré" else "de convention",
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

    # ── composition et thème ──
    comp = motion.get("comp") or {}
    if not comp:
        rap.erreur("comp", "bloc « comp » absent")
    fmt = comp.get("format", "16:9")
    if fmt not in FORMATS and not (comp.get("largeur") and comp.get("hauteur")):
        rap.erreur("format", "format « %s » inconnu : 16:9, 9:16 ou 1:1 (ou largeur et hauteur)" % fmt)
    if fmt in ("9:16", "1:1"):
        rap.info("format", "format %s : aucun format vertical ou carré dans le corpus ; distances et tailles en u (1 %% du petit côté) : convention" % fmt)
    W, H = FORMATS.get(fmt, (comp.get("largeur", 1920), comp.get("hauteur", 1080)))
    W, H = comp.get("largeur", W), comp.get("hauteur", H)
    U = min(W, H) / 100.0
    if comp.get("cadence", 30) not in CADENCES:
        rap.alerte("cadence", "cadence %s inhabituelle (24, 25, 29,97, 30, 50 ou 60)" % comp.get("cadence"))
    duree = comp.get("duree")
    if not isinstance(duree, (int, float)) or duree <= 0:
        rap.erreur("duree", "comp.duree doit être un nombre de secondes positif")
        duree = 10
    epoque = comp.get("epoque", "2024-2026")
    if epoque not in ("2024-2026", "2019-2020"):
        rap.erreur("epoque", "époque « %s » inconnue : 2024-2026 ou 2019-2020" % epoque)
    theme = motion.get("theme") or {}
    couleurs = dict({"fond": "#0E1013", "texte": "#F4F4F2", "secondaire": "#9A9CA3", "accent": "#4C8DFF", "voile": "#000000"}, **(theme.get("couleurs") or {}))
    for k, v in couleurs.items():
        if not hexa(v):
            rap.erreur("couleur", "theme.couleurs.%s = %s : un HEX #RRGGBB est attendu" % (k, v))
    for role, liste in (theme.get("polices") or {}).items():
        for nom in (liste if isinstance(liste, list) else [liste]):
            n = str(nom).lower().replace("_", " ")
            if any(x in n for x in POLICES_INTERDITES):
                rap.erreur("police-marque", "police « %s » (%s) : police propre à une marque ; la skill reprend la grammaire, jamais la marque" % (nom, role))
    def couleur(c, defaut):
        if hexa(c):
            return c
        return couleurs.get(c or defaut, couleurs.get(defaut))
    fond_comp = couleur(comp.get("fond"), "fond")

    # ── éléments : structure ──
    els = motion.get("elements") or []
    if not els:
        rap.erreur("elements", "aucun élément")
    ids = {}
    for e in els:
        eid = e.get("id")
        if not eid:
            rap.erreur("id", "élément sans id : %s" % json.dumps(e, ensure_ascii=False)[:80])
            continue
        if eid in ids:
            rap.erreur("id", "id en double : %s" % eid, eid)
        ids[eid] = e
    for e in els:
        eid = e.get("id")
        for k in e:
            if k not in CHAMPS_ELEMENT and not k.startswith("_"):
                rap.alerte("champ", "champ « %s » inconnu (ignoré)" % k, eid)
        typ = e.get("type")
        if typ not in TYPES:
            rap.erreur("type", "type « %s » inconnu (%s)" % (typ, ", ".join(TYPES)), eid)
            continue
        rec = e.get("recette", "coupe")
        if rec not in R:
            rap.erreur("recette", "recette « %s » inconnue (voir references/motion-spec.md, § 4)" % rec, eid)
            continue
        if typ not in R[rec]["types"]:
            rap.erreur("recette-type", "la recette %s ne s'applique pas à un élément %s (types admis : %s)" % (rec, typ, ", ".join(R[rec]["types"])), eid)
        if rec == "avec":
            if e.get("avec") not in ids:
                rap.erreur("avec", "« avec » doit nommer l'élément principal (le surtitre arrive avec son mot : 8 sur 11)", eid)
        elif typ == "surtitre" and rec != "coupe":
            rap.alerte("surtitre-seul", "un surtitre n'a pas d'animation à lui : il arrive avec son mot (8 sur 11, écart ≤ 0,06 s) ; préférer « recette »: « avec »", eid)
        if e.get("parent") is not None and (e["parent"] not in ids or ids[e["parent"]].get("type") != "nul-camera"):
            rap.erreur("parent", "parent « %s » : un élément de type nul-camera est attendu" % e.get("parent"), eid)
        if e.get("sortie", "coupe") not in ("coupe", "fondu"):
            rap.erreur("sortie", "sortie « %s » : le texte et les objets sortent par une coupe (15 sur 18) ou un fondu (3) ; aucune sortie ne bouge, ne rétrécit ni ne floute (0 sur 18)" % e.get("sortie"), eid)
        if "debut" in e and isinstance(e["debut"], (int, float)) and e["debut"] < 0:
            rap.erreur("debut", "début négatif", eid)
        if not isinstance(e.get("position", [50, 50]), list) or len(e.get("position", [50, 50])) != 2:
            rap.erreur("position", "position = [x %, y %] attendue", eid)
        verifier_params(rap, rec, e.get("options"), R[rec]["params"], rec, eid)
        o = e.get("options") or {}
        for lien in ("ancien", "nom"):
            if lien in o and o[lien] not in ids:
                rap.erreur("lien", "options.%s = « %s » : élément introuvable" % (lien, o[lien]), eid)
        if rec in ("mot-remplace", "mot-fondu-enchaine", "mot-glisse") and "ancien" not in o:
            rap.erreur("lien", "%s demande options.ancien (le mot qui s'en va)" % rec, eid)
        if rec == "nom-remonte" and "nom" not in o:
            rap.erreur("lien", "nom-remonte demande options.nom (le nom qui remonte : 5 sur 5)", eid)
        rep = R[rec].get("epoque", "toutes")
        if rep not in ("toutes", epoque):
            rap.alerte("epoque", "recette %s datée %s dans un film %s : choisir une époque et s'y tenir (convention ; la courbe d'arrivée change d'une époque à l'autre : 21 instances en 2019-2020, 56 en 2024-2026)" % (rec, rep, epoque), eid)
        balayages = 0
        for q in e.get("puis") or []:
            qr = q.get("recette")
            if qr not in COMPLEMENTS:
                rap.erreur("puis", "« puis » accepte %s ; « %s » refusé" % (", ".join(COMPLEMENTS), qr), eid)
                continue
            if typ not in R[qr]["types"]:
                rap.erreur("recette-type", "%s ne s'applique pas à un élément %s" % (qr, typ), eid)
            verifier_params(rap, qr, q.get("options"), R[qr]["params"], "puis/" + qr, eid)
            if qr == "balayage-lumiere":
                balayages += 1
                if (q.get("options") or {}).get("sens") == "bas":
                    rap.erreur("balayage-bas", "balayage vers le bas : jamais vu (0 sur 11 ; gauche 4, haut 4, droite 3)", eid)
            if qr == "assombrir-autour" and (q.get("options") or {}).get("niveau", 40) >= 75:
                rap.erreur("voile-noir", "voile à %s %% : jamais jusqu'au noir (max 73 %%, 20 sur 20)" % (q.get("options") or {}).get("niveau"), eid)
        if rec == "balayage-lumiere":
            balayages += 1
        if balayages > 1:
            rap.erreur("balayage-repete", "%d balayages sur le même élément : un seul passage par plan (11 sur 11)" % balayages, eid)
        # fichiers
        fichiers = []
        if e.get("fichier"):
            fichiers.append(e["fichier"])
        fichiers += [f for f in (e.get("fichiers") or []) if f]
        fichiers += [p.get("fichier") for p in (e.get("pieces") or []) if p.get("fichier")]
        for f in fichiers:
            chem = f if os.path.isabs(f) else os.path.join(base, f)
            if not os.path.exists(chem):
                rap.alerte("fichier-absent", "fichier absent : %s → un repli neutre (cadre et diagonales) sera dessiné" % f, eid)
        if typ in ("image", "capture", "icone") and not fichiers and rec != "eclate":
            rap.alerte("fichier-absent", "aucun fichier : un repli neutre sera dessiné", eid)
        if rec == "empilement" and len(e.get("fichiers") or []) < 2:
            rap.erreur("empilement", "empilement demande « fichiers » (deux écrans au moins)", eid)
        if rec == "carton-groupes" and len(e.get("groupes") or []) < 2:
            rap.erreur("groupes", "carton-groupes demande « groupes » (deux groupes de sens au moins ; jamais mot à mot : 0 sur 145)", eid)
        if typ == "liste" and not e.get("lignes"):
            rap.erreur("lignes", "une liste demande « lignes »", eid)
        # chiffres et sources
        contenu = " ".join([str(e.get("contenu") or "")] + [str(x) for x in (e.get("lignes") or [])] + [str(x) for x in (e.get("groupes") or [])])
        a_fournir = "[À FOURNIR]" in contenu or "[À FOURNIR]" in str(e.get("source") or "") or "[A FOURNIR]" in contenu.upper()
        if typ == "chiffre":
            if a_fournir:
                rap.alerte("a-fournir", "chiffre [À FOURNIR] : la valeur et sa source restent à donner avant la diffusion", eid)
            elif re.search(r"\d", contenu) and not str(e.get("source") or "").strip():
                rap.erreur("source", "chiffre « %s » sans « source » : aucun chiffre sans source" % contenu.strip(), eid)
            if "compteur" in json.dumps(o) or "compte" in o:
                rap.erreur("compteur", "le chiffre héros ne compte jamais (0 sur 27) : il arrive d'un bloc, l'échelle l'anime", eid)
        elif typ in TEXTES:
            if a_fournir:
                rap.alerte("a-fournir", "texte qui contient [À FOURNIR]", eid)
            elif re.search(r"\d", contenu) and not str(e.get("source") or "").strip():
                rap.alerte("source", "le texte contient un chiffre sans « source »", eid)

    # ── plan temporel ──
    pl = None if sans_node else plan_node(chemin)
    approche = pl is None
    if approche:
        pl = plan_estime(motion, table)
        rap.info("plan", "plan temporel estimé sans Node : durées d'entrée approchées (lancer avec Node pour un contrôle exact)")
    P = {p["id"]: p for p in pl["elements"]}

    for e in els:
        eid = e.get("id")
        p = P.get(eid)
        if not p or e.get("type") not in TYPES or e.get("recette", "coupe") not in R:
            continue
        typ, rec = e["type"], p["recette"]
        if p["fin"] > duree + 1e-6 or p["sortieDebut"] > duree + 1e-6:
            rap.alerte("hors-comp", "l'élément dure au-delà de la composition (%.2f s > %s s)" % (p["fin"], duree), eid)
        if p["sortieDebut"] < p["finEntree"] - 1e-6:
            rap.erreur("sortie-avant-entree", "la sortie (%.2f s) tombe avant la fin de l'entrée (%.2f s)" % (p["sortieDebut"], p["finEntree"]), eid)
        # lecture
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
                (rap.erreur if visible < 0.6 * besoin else rap.alerte)("lecture", "%d mot(s) visible(s) %.2f s : il faut %.1f s (1,2 s + 0,3 s par mot : convention de lecture ; erreur sous 60 %% de ce temps)" % (len(m), visible, besoin), eid)
            maxi = MOTS_MAX.get(typ)
            if typ == "liste":
                for l in e.get("lignes") or []:
                    if len(mots(l)) > MOTS_MAX["liste"]:
                        rap.alerte("mots", "ligne de %d mots (%d au plus, convention)" % (len(mots(l)), MOTS_MAX["liste"]), eid)
            elif maxi and len(m) > maxi and not e.get("groupes"):
                (rap.erreur if typ == "phrase" and len(m) > 12 else rap.alerte)("mots", "%d mots pour un %s (%d au plus : convention ; aucune instance mesurée au-delà de 12)" % (len(m), typ, maxi), eid)
            if typ == "chiffre" and e.get("libelle") and len(mots(e["libelle"])) > MOTS_MAX["libelle"]:
                rap.alerte("mots", "libellé de %d mots (5 au plus, convention)" % len(mots(e["libelle"])), eid)
            # largeur estimée (0,55 × corps par caractère pour une linéale : convention)
            tailles = {"titre": 10, "phrase": 5.4, "liste": 4.4, "chiffre": 30}
            corps = (e.get("taille") or tailles.get(typ, 6)) * U
            lignes = e.get("lignes") or (e["groupes"] and [" ".join(e["groupes"])] if e.get("groupes") else None) or str(e.get("contenu") or "").split("\n")
            for l in lignes:
                larg = len(str(l)) * 0.55 * corps
                if larg > 0.9 * W:
                    rap.alerte("largeur", "ligne « %s » ≈ %d px pour une image de %d px : couper la ligne ou réduire la taille" % (str(l)[:30], larg, W), eid)
        # contraste avec le fond uni présent au début du texte (le dernier élément « fond » sans fichier, sinon la composition)
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
                    rap.alerte("contraste", "contraste %.1f:1 entre le texte (%s) et le fond (%s) : 4,5:1 au moins (convention de lisibilité)" % (c, ct, fond), eid)
        # règles propres aux recettes
        o = p.get("options") or {}
        if rec == "empilement" and o.get("intervalle", 1.67) < o.get("T", 0.79) - 1e-6:
            rap.erreur("empilement-chevauche", "intervalle %.2f s < durée d'une arrivée %.2f s : les arrivées ne se chevauchent jamais (11 sur 11)" % (o.get("intervalle"), o.get("T")), eid)
        if rec == "liste-au-fil" and o.get("intervalle", 2.0) < o.get("T_position", 0.95):
            rap.erreur("liste-chevauche", "une ligne au fil de la voix arrive avant la fin de la précédente", eid)
        if rec == "zoom-detail" and e.get("type") != "nul-camera":
            tient = p["sortieDebut"] - p["finEntree"]
            if tient < 2.5:
                rap.alerte("maintien-detail", "%.1f s sur le détail après le zoom : on laisse regarder (maintien médian 7,2 s, p25 2,5 s ; 2,5 à 7 s : convention)" % tient, eid)
        if rec == "logo-fin" and not p.get("avec"):
            tient = p["sortieDebut"] - p["finEntree"]
            if tient < 1.25:
                rap.alerte("maintien-nom", "nom de fin tenu %.2f s : 2,6 s médian (1,25 à 4,7 ; 17 noms)" % tient, eid)
            y = (e.get("position") or [50, 50])[1]
            if not 47 <= y <= 51:
                rap.info("place-nom", "nom de fin à %s %% de la hauteur : centre vertical entre 47 et 51 %% dans 15 cas sur 20" % y, eid)
        if rec in ("chiffre-pose", "chiffre-croissance") and o.get("retard_libelle", 0.23) < 0:
            rap.erreur("libelle-avant", "le libellé arrive après son chiffre (+0,23 s de milieu à milieu des fondus, 15 sur 18), jamais avant", eid)
        if rec == "assombrir-autour" and o.get("niveau", 40) >= 75:
            rap.erreur("voile-noir", "voile à %s %% : jamais jusqu'au noir (max 73 %%, 20 sur 20)" % o.get("niveau"), eid)

    # ── temps vide après une coupe : de la coupe à la première trace visible (debut + départ doux de la courbe) ──
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
            rap.info("temps-vide", "fond vide visible %.2f s après la coupe de %.2f s : il tient d'habitude 0,13 à 0,23 s avant que les éléments n'entrent (135 cas) ; seule l'entrée latérale part sur la coupe (8 sur 8)" % (vide, coupe), e.get("id"))
        elif vide > 0.30 and (p.get("apparition") or 0) > 0:
            rap.alerte("temps-vide", "fond vide visible %.2f s après la coupe de %.2f s (debut à +%.2f s, puis %.2f s avant 2 %% d'opacité) : 0,13 à 0,23 s mesurés (135 cas) ; avancer « debut » d'environ %.2f s (tolérance 0,30 s : convention)"
                       % (vide, coupe, p["debut"] - coupe, p.get("apparition") or 0, vide - 0.18), e.get("id"))

    # ── transitions ──
    trs = motion.get("transitions") or []
    for t in trs:
        typ = t.get("type")
        if typ not in TR:
            rap.erreur("transition", "transition « %s » inconnue (%s)" % (typ, ", ".join(TR)))
            continue
        for k in ("de", "vers"):
            for i in t.get(k) or []:
                if i not in ids:
                    rap.erreur("transition-lien", "transition %s à %s s : « %s » introuvable" % (typ, t.get("temps"), i))
        if not isinstance(t.get("temps"), (int, float)):
            rap.erreur("transition-temps", "transition %s sans « temps »" % typ)
        verifier_params(rap, typ, t.get("options"), TR[typ]["params"], "transition " + typ, None)
        if typ == "raccord" and (t.get("de") or []) and (t.get("vers") or []) and t["de"][0] in ids and t["vers"][0] in ids:
            a, b = ids[t["de"][0]], ids[t["vers"][0]]
            pa, pb = a.get("position") or [50, 50], b.get("position") or [50, 50]
            d = (((pa[0] - pb[0]) * W / 100.0) ** 2 + ((pa[1] - pb[1]) * H / 100.0) ** 2) ** 0.5 / U
            ta, tb = a.get("taille"), b.get("taille")
            if d > 5:
                rap.alerte("raccord", "raccord %s → %s : le centre bouge de %.1f u ; il bouge de 3,2 %% H en médiane, 5 %% H ou moins dans 13 cas sur 22" % (t["de"][0], t["vers"][0], d))
            if isinstance(ta, (int, float)) and isinstance(tb, (int, float)) and ta > 0 and not 0.90 <= tb / ta <= 1.12:
                rap.alerte("raccord", "raccord %s → %s : la taille change de ×%.2f ; entre ×0,90 et ×1,12 dans 21 cas sur 22" % (t["de"][0], t["vers"][0], tb / ta))
        if typ in ("glissade", "poussee") and (t.get("options") or {}).get("sens") in ("haut", "bas"):
            rap.erreur("glissade-verticale", "glissade verticale : jamais vue (horizontal 32 sur 32)")
    tp = [x for x in pl["transitions"] if x["type"] in TR]
    for i in range(len(tp)):
        for j in range(i + 1, len(tp)):
            a, b = tp[i], tp[j]
            if a["duree"] > 0 and b["duree"] > 0 and chevauche(a["temps"], a["fin"], b["temps"], b["fin"]):
                rap.erreur("transitions-chevauchent", "%s (%.2f–%.2f s) et %s (%.2f–%.2f s) se chevauchent : une transition ne chevauche pas la suivante (25 sur 25)" % (a["type"], a["temps"], a["fin"], b["type"], b["temps"], b["fin"]))

    # ── une chose à la fois : mouvements majeurs ──
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
                rap.erreur("deux-mouvements", "deux mouvements majeurs à la fois : %s « %s » (%.2f–%.2f s) et %s « %s » (%.2f–%.2f s). Les éléments arrivent l'un après l'autre (rangées 11 sur 11 ; libellé +0,23 s, 15 sur 18). Décaler l'un, ou les lier (avec, options.nom), ou poser « simultane »: true si c'est voulu."
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
        print("lecture impossible : %s" % e)
        return 1
    rap, pl = controler(motion, chemin, sans_node="--sans-node" in argv)
    err = [i for i in rap.items if i["niveau"] == "erreur"]
    if "--json" in argv:
        print(json.dumps({"erreurs": len(err), "items": rap.items}, ensure_ascii=False, indent=1))
    else:
        noms = {"erreur": "ERREUR", "avertissement": "attention", "info": "info"}
        for niveau in ("erreur", "avertissement", "info"):
            for i in rap.items:
                if i["niveau"] == niveau:
                    print("%-9s %s%s" % (noms[niveau], "[%s] " % i["element"] if i["element"] else "", i["message"]))
        nb = {n: sum(1 for i in rap.items if i["niveau"] == n) for n in ("erreur", "avertissement", "info")}
        print("— %d erreur(s), %d avertissement(s), %d info(s) — %s" % (nb["erreur"], nb["avertissement"], nb["info"], os.path.basename(chemin)))
    return 1 if err else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
