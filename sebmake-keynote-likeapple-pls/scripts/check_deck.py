#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""check_deck.py: checks a deck.json before rendering and lists the gaps.

Usage:
    python3 check_deck.py deck.json [--brouillon] [--json]

--brouillon : draft mode. Remaining [TO PROVIDE] markers and slide.a_fournir instructions
              become warnings (while writing; remove the flag before presenting).
--json      : machine output (erreurs, avertissements, a_valider, infos).

[TO VALIDATE: text] proposals never block: they are listed separately
(the "TO VALIDATE" section), so the delivery can get them approved one by one.
French decks use [À FOURNIR] and [À VALIDER]; both forms are accepted.

Design: slide.variante must exist for the archetype (VARIANTES table, a copy of the engine's
list); slide.visuel describes the visual to prepare. Warning if three slides in a row have
the same archetype and the same variant, or if a block of two slides or more has no visual
moment (A5, A9, A10, A13, A14, A18 or an image variant). See ../references/designs.md.

Exit code: 0 with no blocking error, 1 if there is at least one blocking error,
2 if the file cannot be read.

Works with Python 3.9, no dependencies. Expected format: ../references/deck-spec.md.
"""
import argparse
import json
import os
import re
import sys
import unicodedata

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "..", "references", "data")

FORMATS = {"keynote", "powerpoint", "canva", "figma-slides", "video"}
FORMAT_ALIASES = {"pptx": "powerpoint", "ppt": "powerpoint", "key": "keynote", "figma": "figma-slides",
                  "figma slides": "figma-slides", "vidéo": "video", "film": "video"}
FONDS = {"sombre", "clair", "image", "accent"}
SCENES = {"A22", "A23", "A24", "A25"}
CONTENT_IMAGE = {"A2", "A9", "A10", "A11", "A13", "A19", "A20"}
IMAGE_EXPECTED = {"A9", "A10", "A11", "A12", "A13", "A18", "A22", "A23", "A24", "A25"}
REQUIRED = {
    "A1": ["titre"], "A2": ["titre"], "A3": ["lignes"], "A4": ["titre"], "A5": ["chiffre", "libelle"],
    "A6": ["titre", "barres"], "A7": ["lignes"], "A8": ["lignes"], "A9": ["titre"], "A11": ["titre"],
    "A14": ["titre", "tuiles"], "A15": ["elements"], "A16": ["logos"], "A17": ["citation", "auteur"],
    "A20": ["titre"], "AF": ["attendu"],
}
VISIBLE_FIELDS = ["titre", "chiffre", "libelle", "mention", "prix", "note", "nom", "fonction", "axe"]
# Variants that build_deck.js can draw (slide.variante), by archetype: a copy of the engine's
# list (references/designs.md describes them one by one, deck-spec.md sums them up). With no
# variant, the engine keeps the archetype's original rendering; FIN, COLORIS and FRISE take their
# first variant. The FIN, COLORIS and FRISE variants can also be set on any archetype.
# Keep this up to date when the engine changes.
VARIANTES = {
    "A1": ["aplat", "degrade", "sur-image", "entoure", "matiere"],
    "A2": ["icone-nom", "icone-cote", "logo-nom", "rangee", "objet-interface", "icone-seule"],
    "A3": ["centre", "droite", "ligne", "numerote", "suffixe", "ligne-active", "couleurs"],
    "A4": ["aplat", "degrade", "mot-accent", "definition", "sur-image", "sourdine", "enchainee"],
    "A5": ["centre", "bloc", "a-cote", "sur-photo", "objet-anneau", "objet-jauge", "contour"],
    "A6": ["barres", "deux-axes", "anneaux", "frise", "classement"],
    "A7": ["centree", "empilement", "a-cote-icone", "a-cote-objet", "deux-colonnes", "sur-photo", "filet"],
    "A8": ["coche-par-ligne", "cercles-puis-coches", "risque-puis-reponse", "picto-par-ligne", "sur-contenu"],
    "A9": ["appareil-centre-mot", "objet-coupe", "objet-liste", "objet-chiffre", "annotee", "empilee"],
    "A10": ["telephone-centre", "tablette-centre", "portable-centre", "zoom-serre", "capture-nue", "rangee"],
    "A11": ["legende-laterale", "plusieurs-blocs", "schema-chiffre", "carte-annotee", "carre-halo"],
    "A12": ["macro-matiere", "capot-ouvert", "eclate-axial", "flux-lumiere"],
    "A13": ["centre-entier", "hero-coupe", "profil-levitation", "coloris"],
    "A14": ["nom-au-centre", "produit-au-centre", "tuiles-chiffres", "mot-geant-et-produit", "theme-et-matieres", "grille-icones",
             "fragments-logiciel"],
    "A15": ["vignettes", "icones", "mots", "nuage", "cartes-libelles", "forme"],
    "A16": ["grille", "ligne", "logo-seul", "mur-dense", "pastilles", "soi-au-centre"],
    "A17": ["courte", "longue", "source-accent", "centree-signature"],
    "A18": ["usage", "exemple-cartouche", "diptyque", "photo-titre"],
    "A19": ["colonne", "deux-offres", "nom-en-haut", "gamme-alignee", "prix-heros", "ancrage"],
    "A20": ["haut-et-gamme", "suite-de-dates", "colonne", "date-et-lieux", "mot-seul"],
    "A21": ["gauche", "droite", "double", "sur-clair", "carte-invite", "carte-portrait"],
    # Stage shots: accepted, rendered as a full-bleed photo (warning).
    "A22": ["hall-ecran", "scene-mur", "panneau-verre"],
    "A23": ["mot-coupe", "contenu-lisible", "interface-geante", "slide-floue"],
    "A24": ["large-centre", "taille-centre", "decor-sujet"],
    "A25": ["table-flux", "mains-fond-uni", "epaule", "table-haute", "tend-appareil"],
    "FIN": ["signe-seul", "signe-et-ligne", "signe-et-evenement", "signe-sur-photo", "mot-final"],
    "COLORIS": ["rangee-alignee", "rangee-chevauchee", "eventail", "un-par-un", "mur"],
    "FRISE": ["rangee-datee", "generations", "trois-jalons", "courbe-et-saut", "objet-du-passe"],
}
FAMILLES_LIBRES = ("FIN", "COLORIS", "FRISE")       # engine archetypes outside the A1 to A25 catalog
# Variants that place a photo, a screenshot, an object or a product: they count as a visual
# moment ("ARCH/variant"; "ARCH/" = the archetype with no variant).
VARIANTES_IMAGE = {
    "A1/sur-image", "A1/matiere", "A4/sur-image", "A5/a-cote", "A5/sur-photo",
    "A7/a-cote-objet", "A7/sur-photo", "A7/filet", "A8/sur-contenu", "A11/carte-annotee",
    "A12/", "A12/macro-matiere", "A12/capot-ouvert", "A12/eclate-axial", "A12/flux-lumiere",
    "A15/vignettes", "A15/icones", "A15/forme",
    "A19/", "A19/colonne", "A19/deux-offres", "A19/nom-en-haut", "A19/gamme-alignee",
    "A20/haut-et-gamme", "A20/colonne", "A20/suite-de-dates", "A20/date-et-lieux",
    "A21/gauche", "A21/droite", "A21/double", "A21/sur-clair", "A21/carte-portrait",
    "FIN/signe-sur-photo", "COLORIS/rangee-alignee", "COLORIS/rangee-chevauchee", "COLORIS/eventail",
    "COLORIS/un-par-un", "COLORIS/mur", "FRISE/trois-jalons", "FRISE/objet-du-passe",
}
VARIANTES_IMAGE.update(a + "/" + v for a in ("A22", "A23", "A24", "A25") for v in [""] + VARIANTES[a])
# With no variant, the original rendering is the first variant for these archetypes.
ORIGINE = {"A1": "aplat", "A3": "centre", "A4": "aplat", "A5": "centre", "A7": "centree", "A17": "courte"}
# Required fields that change with the variant (otherwise those of REQUIRED for the archetype).
REQUIRED_VARIANTE = {
    "A2/rangee": [], "A2/icone-seule": [], "A5/objet-jauge": ["chiffre"],
    "A6/deux-axes": ["titre"], "A6/frise": ["titre"], "A6/classement": ["titre"],
    "A9/objet-chiffre": ["chiffre"], "A9/annotee": [], "A11/carte-annotee": [], "A11/carre-halo": [],
    "A14/produit-au-centre": ["tuiles"], "A14/tuiles-chiffres": ["tuiles"], "A14/grille-icones": ["tuiles"],
    "A14/fragments-logiciel": ["tuiles"],
    "FIN/mot-final": ["titre"],
}
REQUIRED_VARIANTE.update((a + "/" + v, []) for a in ("A15", "A16") for v in VARIANTES[a])
REQUIRED_VARIANTE.update((a + "/" + v, []) for a in FAMILLES_LIBRES for v in VARIANTES[a] if a + "/" + v not in REQUIRED_VARIANTE)
TUILES_BORNES = {"A14/produit-au-centre": (4, 10), "A14/tuiles-chiffres": (4, 10), "A14/mot-geant-et-produit": (4, 10),
                 "A14/theme-et-matieres": (4, 10), "A14/grille-icones": (3, 12), "A14/fragments-logiciel": (6, 11)}
APPAREILS = {"telephone", "tablette", "portable", "boitier"}
# Archetypes that are always a strong visual moment.
MOMENTS_VISUELS = {"A5", "A9", "A10", "A13", "A14", "A18"}
TYPES_VISUEL = {"capture", "photo", "produit", "objet", "icone", "logo", "schema", "matiere", "pictogrammes",
                "vignettes", "video", "image"}
TYPE_VISUEL_ALIASES = {"screenshot": "capture", "ecran": "capture", "interface": "capture", "product": "produit",
                       "rendu": "produit", "object": "objet", "icon": "icone", "diagram": "schema", "texture": "matiere",
                       "pictogramme": "pictogrammes", "pictograms": "pictogrammes", "vignette": "vignettes",
                       "thumbnails": "vignettes", "rush": "video"}
VISUEL_CHAMPS = {"type", "brief", "fond_transparent", "angle", "resolution_min", "format", "chemin"}
MAX_WORDS = 10
SPEECH_WPM_MAX = 170
SPEECH_WPM_MIN = 110
SPEECH_WPM_CIBLE = 140
FOURNIR_MAX_WORDS = 3          # [TO PROVIDE] label shown on screen
SURTITRE_MAX_WORDS = 3
DUREE_TOLERANCE = 0.15

MARKER_RE = re.compile(r"\[(?:À|A) FOURNIR[^\]]*\]|\[TO PROVIDE[^\]]*\]", re.I)
FOURNIR_LABEL_RE = re.compile(r"\[(?:(?:À|A) FOURNIR|TO PROVIDE)\s*:?\s*([^\]]*)\]", re.I)
VALIDER_RE = re.compile(r"\[(?:(?:À|A) VALIDER|TO VALIDATE)\s*:?\s*([^\]]*)\]", re.I)
BRACKET_RE = re.compile(r"\[[^\]]*\]|\([^)]*\)")      # stage directions in the spoken text
APPLE_FONT_RE = re.compile(r"^\s*(?:\.?SF(?:\s|$|\s*(?:Pro|Compact|Mono))|San Francisco|New York|-apple-system)", re.I)
# What a [TO VALIDATE] proposal never contains: figure, price, percentage, date.
VALIDER_INTERDITS = [
    ("a figure", re.compile(r"\d")),
    ("a percentage", re.compile(r"%|\bpour\s?cent\b|\bper\s?cent\b|\bpercent\b", re.I)),
    ("a price", re.compile(r"[€$£¥]|\b(?:euros?|dollars?|HT|TTC|gratuit(?:e|s|es)?|sans\s+(?:surcoût|frais)|"
                          r"free of charge|for free|at no (?:extra )?cost)\b", re.I)),
    ("a date", re.compile(r"\b(?:janvier|février|fevrier|mars|avril|mai|juin|juillet|août|aout|septembre|octobre|"
                           r"novembre|décembre|decembre|january|february|april|june|july|august|september|october|"
                           r"november|december|trimestre|semestre|quarter)\b|"
                           r"\b(?:in|by|from|until|since|early|late|mid|this|next)[\s-]+(?:may|march)\b", re.I)),
    ("a number", re.compile(r"\b(?:deux|trois|quatre|cinq|six|sept|huit|dix|onze|douze|treize|quatorze|quinze|"
                            r"vingts?|trente|quarante|cinquante|soixante|cents?|mille|millions?|milliards?|dizaines?|"
                            r"douzaines?|centaines?|milliers?|moitié|two|three|four|five|six|seven|eight|nine|ten|"
                            r"eleven|twelve|twenty|thirty|forty|fifty|hundreds?|thousands?|millions?|billions?|"
                            r"dozens?|half|twice)\b|"
                            r"\b(?:en|sous|in|within|under)\s+(?:un|une|one|a|an)\s+(?:secondes?|minutes?|heures?|"
                            r"journées?|jours?|semaines?|mois|ans?|années?|seconds?|hours?|days?|weeks?|months?|years?)\b", re.I)),
]
NESTED_RE = re.compile(r"\[(?:(?:À|A) (?:VALIDER|FOURNIR)|TO (?:VALIDATE|PROVIDE))[^\]]*\[", re.I)
# Marker opened and never closed: the render would show it as is. A \n inside a closed marker is allowed.
UNCLOSED_RE = re.compile(r"\[(?:(?:À|A) (?:VALIDER|FOURNIR)|TO (?:VALIDATE|PROVIDE|CONFIRM))[^\]\[]*$", re.I)
# "les deux" / "both" is not a figure, nor is an acronym like B2B or B2C
VALIDER_PERMIS_RE = re.compile(r"\b(?:tous|toutes|les|nos|vos)\s+deux\b|\bboth\b|\b[A-Za-z]+\d+[A-Za-z]\w*", re.I)
TU_RE = re.compile(r"(?<![\w’'])(tu|te|toi|ton|ta|tes)(?![\w’'])|(?<![\w’'])t['’](?=[a-zàâäéèêëîïôöùûüyh])", re.I)
VOUS_RE = re.compile(r"(?<![\w’'])(vous|votre|vos|vôtre|vôtres)(?![\w’'])", re.I)
TON_NOM_RE = re.compile(r"\b(le|un|du|ce|même|bon|mauvais)\s+ton\b", re.I)   # French: "le ton" (the tone) is not the informal "ton"
RELAIS_RE = re.compile(r"(?:c['’]est\s+)?à\s+toi\b|\bje\s+te\s+(?:rends|repasse|passe|laisse)\b", re.I)
QUOTE_RE = re.compile(r"«[^»]*»|“[^”]*”|\"[^\"]*\"")
STAT_RE = re.compile(r"\d\s*(?:%|×|x\b|fois\b|times\b)|jusqu['’]à\s+\d|up to\s+\d", re.I)
JUSQUA_RE = re.compile(r"jusqu['’]à|\bup to\b", re.I)
SUPERLATIFS_FR = re.compile(r"\b(?:le|la|les)\s+plus\s+\w+|\bmeilleur(?:e|s|es)?\b|\bincroyables?\b|\brévolutionnaires?\b|"
                            r"\bsans précédent\b|\bexceptionnel(?:le|s|les)?\b|\binégalé(?:e|s|es)?\b|\bau monde\b", re.I)
SUPERLATIFS_EN = re.compile(r"\b(?:best|ever|incredible|amazing|revolutionary|breakthrough|unprecedented|most\s+\w+|world['’]s first|"
                            r"fastest|biggest|largest|smallest|thinnest|lightest|strongest|easiest|simplest|brightest|greatest)\b", re.I)
N3_RE = re.compile(r"\bau monde\b|\bdu march[ée]\b|\b(?:le|la|les) meilleur(?:e|s|es)?\b|\bnum[ée]ro un\b|\bn°\s?1\b|\bleader\b|"
                   r"\bin the world\b|\bworld['’]s\b|\bnumber one\b|#1\b|\bmarket leader\b|\bbest\b", re.I)
CONCURRENT_RE = re.compile(r"concurren|\bautres? solutions?\b|\bleader\b|\bmarch[ée]\b|competitor|\bothers\b", re.I)
ANONYME_RE = re.compile(r"concurren|\bautres?\b|leader|march[ée]|classique|traditionnel|competitor|others?\b|leading", re.I)


# ---------------------------------------------------------------------------
# Utilities
# ---------------------------------------------------------------------------
def norm_key(s):
    s = unicodedata.normalize("NFD", str(s or ""))
    s = "".join(ch for ch in s if unicodedata.category(ch) != "Mn").lower()
    return re.sub(r"[^a-z0-9]+", "-", s).strip("-")


def as_list(v):
    if v is None:
        return []
    return v if isinstance(v, list) else [v]


def text_of(v):
    return "" if v is None else str(v)


def unvalider(s):
    """[TO VALIDATE: text] -> text: a proposal reads like real content."""
    return VALIDER_RE.sub(lambda m: m.group(1), text_of(s))


def speech_words(s):
    """Spoken words: proposals included, without [TO PROVIDE] or directions in brackets or parentheses."""
    return words(BRACKET_RE.sub(" ", MARKER_RE.sub(" ", unvalider(s))))


def words(s):
    s = MARKER_RE.sub(" ", unvalider(s)).replace("*", " ")
    return [w for w in re.split(r"[\s  ]+", s) if re.search(r"\w", w)]


def all_strings(v):
    if isinstance(v, str):
        yield v
    elif isinstance(v, dict):
        for x in v.values():
            for s in all_strings(x):
                yield s
    elif isinstance(v, list):
        for x in v:
            for s in all_strings(x):
                yield s


def hex_ok(c):
    return bool(re.match(r"^#?([0-9a-fA-F]{3}|[0-9a-fA-F]{6})$", str(c).strip()))


def hex6(c):
    s = str(c).strip().lstrip("#")
    if len(s) == 3:
        s = "".join(ch * 2 for ch in s)
    return s.upper()


def luminance(h):
    out = []
    for i in (0, 2, 4):
        v = int(h[i:i + 2], 16) / 255.0
        out.append(v / 12.92 if v <= 0.03928 else ((v + 0.055) / 1.055) ** 2.4)
    return 0.2126 * out[0] + 0.7152 * out[1] + 0.0722 * out[2]


def contrast(a, b):
    la, lb = luminance(a), luminance(b)
    return (max(la, lb) + 0.05) / (min(la, lb) + 0.05)


def mix(a, b, t):
    ra = [int(a[i:i + 2], 16) for i in (0, 2, 4)]
    rb = [int(b[i:i + 2], 16) for i in (0, 2, 4)]
    return "".join("%02X" % int(round(x + (y - x) * t)) for x, y in zip(ra, rb))


def number_groups(s):
    s = MARKER_RE.sub(" ", unvalider(s))
    s = re.sub(r"(\d+)\s*h\s*(\d{2})\b", r"\1h\2", s)          # 3 h 10 = a duration
    s = re.sub(r"(\d+)\s*/\s*(\d+)", r"\1/\2", s)              # 24/7 = a schedule
    s = re.sub(r"(\d)[\s  ](?=\d{3}\b)", r"\1", s)    # 1 299 = one number
    return re.findall(r"\d+(?:[.,/h]\d+)*", s)


def load_json(path, default):
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError):
        return default


def match_public(label, pubs):
    k = norm_key(label)
    if not k:
        return None
    if k in pubs:
        return k
    best, best_len = None, 0
    for key, row in pubs.items():
        for syn in [key] + list(row.get("synonymes", [])):
            sk = norm_key(syn)
            if not sk:
                continue
            if sk == k:
                return key
            if ("-" + sk + "-") in ("-" + k + "-") and len(sk) > best_len:
                best, best_len = key, len(sk)
    return best


def resolve_public(meta, table):
    """Returns (key, settings, recognized). A list of types = mixed audience: the most cautious setting wins."""
    raw = meta.get("public")
    if isinstance(raw, dict):
        labels = as_list(raw.get("type") or raw.get("types") or raw.get("description"))
    else:
        labels = as_list(raw)
    pubs = table.get("publics", {})
    keys = []
    for l in labels:
        k = match_public(l, pubs)
        if k and k not in keys:
            keys.append(k)
    known = bool(keys)
    if not keys:
        keys = [table.get("defaut", "defaut")]
    row = dict(pubs.get(keys[0], {}))
    order = table.get("prudence", {})
    for k in keys[1:]:
        other = pubs.get(k, {})
        for field, ranks in order.items():
            a, b = row.get(field), other.get(field)
            if b in ranks and (a not in ranks or ranks.index(b) > ranks.index(a)):
                row[field] = b
    if len(keys) > 1:
        lo = [pubs[k].get("duree_min_conseillee") for k in keys if pubs.get(k, {}).get("duree_min_conseillee")]
        row["duree_min_conseillee"] = None if not lo else [max(x[0] for x in lo), min(x[1] for x in lo)]
    return "+".join(keys), row, known


def resolve_variante(arch, variante):
    """"ARCH/variant" that the engine draws, or "" if the variant is unknown for this archetype."""
    v = norm_key(variante)
    if v in VARIANTES.get(arch, []):
        return arch + "/" + v
    for fam in FAMILLES_LIBRES:
        if v in VARIANTES[fam]:
            return fam + "/" + v
    return ""


def img_path_of(slide):
    img = slide.get("image")
    if isinstance(img, str):
        return img
    return text_of(img.get("chemin")) if isinstance(img, dict) else ""


def has_any_image(slide):
    """Does the slide carry an image (main, list, background, described visual or element image)?"""
    if img_path_of(slide) or slide.get("images") or slide.get("image_fond") or slide.get("visuel") is not None:
        return True
    t = slide.get("textes") or {}
    for key in ("tuiles", "elements", "logos", "offres", "coloris", "jalons", "pictos"):
        for x in as_list(t.get(key)) if isinstance(t, dict) else []:
            if (isinstance(x, dict) and x.get("image")) or (key == "pictos" and isinstance(x, str) and x):
                return True
    return False


def element_images(slide):
    """(path, label) of the images the slide carries besides slide.image: lists, elements, extra logos."""
    out = []
    for x in as_list(slide.get("images")):
        p = x if isinstance(x, str) else text_of(x.get("chemin")) if isinstance(x, dict) else ""
        if p:
            out.append((p, text_of(x.get("attendu")) if isinstance(x, dict) else ""))
    for key in ("logo_invite", "logo_systeme", "logo_final"):
        if isinstance(slide.get(key), str) and slide.get(key):
            out.append((slide[key], key))
    t = slide.get("textes") or {}
    if not isinstance(t, dict):
        return out
    for key in ("elements", "offres", "coloris", "jalons"):
        for x in as_list(t.get(key)):
            if isinstance(x, dict) and x.get("image"):
                out.append((text_of(x["image"]), text_of(x.get("titre") or x.get("nom"))))
    for x in as_list(t.get("pictos")):
        p = x if isinstance(x, str) else text_of(x.get("image") or x.get("chemin")) if isinstance(x, dict) else ""
        if p:
            out.append((p, "pictogramme"))
    for col in as_list(t.get("colonnes")):
        for lg in as_list(col.get("logos")) if isinstance(col, dict) else []:
            if isinstance(lg, dict) and lg.get("image"):
                out.append((text_of(lg["image"]), text_of(lg.get("nom"))))
    return out


def norm_type_visuel(t):
    k = norm_key(t)
    return TYPE_VISUEL_ALIASES.get(k, k)


def resolution_ok(r):
    """1920 × 1080, [1920, 1080], {"largeur": 1920, "hauteur": 1080}, 2000 (long side) or "2000 px high"."""
    if isinstance(r, bool):
        return False
    if isinstance(r, (int, float)):
        return r > 0
    if isinstance(r, list):
        return len(r) == 2 and all(isinstance(x, (int, float)) and not isinstance(x, bool) and x > 0 for x in r)
    if isinstance(r, dict):
        vals = [r.get(k) for k in ("largeur", "hauteur", "width", "height", "l", "h") if r.get(k) is not None]
        return bool(vals) and all(isinstance(x, (int, float)) and x > 0 for x in vals)
    return bool(re.search(r"\d{2,5}", text_of(r)))


def check_visuel(rep, where, v):
    """slide.visuel: an object (or a list of objects) that describes the visual to prepare."""
    if v is None:
        return
    items = v if isinstance(v, list) else [v]
    for k, it in enumerate(items):
        lab = "slide.visuel" if len(items) == 1 else "slide.visuel[%d]" % (k + 1)
        if not isinstance(it, dict):
            rep.err(where, "%s: object expected, {type, brief, fond_transparent, angle, resolution_min}." % lab)
            continue
        inconnus = sorted(set(it) - VISUEL_CHAMPS)
        if inconnus:
            rep.warn(where, "%s: unknown field(s) %s (type, brief, fond_transparent, angle, resolution_min, format, chemin)." % (
                lab, ", ".join(inconnus)))
        if not text_of(it.get("type")).strip():
            rep.warn(where, "%s has no type: capture, photo, produit, objet, icone, logo, schema, matiere, pictogrammes, "
                            "vignettes or video." % lab)
        elif norm_type_visuel(it.get("type")) not in TYPES_VISUEL:
            rep.warn(where, "%s: unknown type “%s” (capture, photo, produit, objet, icone, logo, schema, matiere, "
                            "pictogrammes, vignettes, video)." % (lab, it.get("type")))
        if not text_of(it.get("brief")).strip():
            rep.warn(where, "%s has no brief: say what it must show, its framing and its light." % lab)
        if "fond_transparent" in it and not isinstance(it.get("fond_transparent"), bool):
            rep.warn(where, "%s.fond_transparent “%s”: true or false expected." % (lab, it.get("fond_transparent")))
        if "angle" in it and not isinstance(it.get("angle"), str):
            rep.warn(where, "%s.angle: text expected (face, trois-quarts, profil, dessus…)." % lab)
        if it.get("resolution_min") is not None and not resolution_ok(it.get("resolution_min")):
            rep.warn(where, "%s.resolution_min “%s”: write “1920 × 1080”, [1920, 1080] or a number of pixels." % (
                lab, it.get("resolution_min")))


def note_segments(slide, default_speaker):
    n = slide.get("notes")
    if n is None or n == "":
        return []
    if isinstance(n, str):
        return [{"intervenant": slide.get("intervenant") or default_speaker, "texte": n}]
    segs = []
    for s in as_list(n):
        if isinstance(s, str):
            segs.append({"intervenant": slide.get("intervenant") or default_speaker, "texte": s})
        elif isinstance(s, dict):
            segs.append({"intervenant": s.get("intervenant") or slide.get("intervenant") or default_speaker,
                         "texte": text_of(s.get("texte") or s.get("text")), "type": s.get("type")})
    return [s for s in segs if s["texte"].strip()]


# ---------------------------------------------------------------------------
# Checks
# ---------------------------------------------------------------------------
class Report(object):
    def __init__(self):
        self.erreurs, self.avertissements, self.infos = [], [], []
        self.a_valider = []       # (slide, proposed text): to get approved at delivery

    def err(self, where, msg):
        self.erreurs.append((where, msg))

    def warn(self, where, msg):
        self.avertissements.append((where, msg))

    def info(self, where, msg):
        self.infos.append((where, msg))


def visible_texts(arch, t):
    """Texts shown on the slide, split into what counts toward the word limit and what does not."""
    counted, extra = [text_of(t.get("surtitre"))], []
    if arch in ("A3", "A7", "A8"):
        counted.append(text_of(t.get("titre")))
        extra.extend(text_of(x) for x in as_list(t.get("lignes")))
    elif arch == "A17":
        extra.extend([text_of(t.get("citation")), text_of(t.get("auteur"))])
    elif arch == "A14":
        counted.append(text_of(t.get("titre")))
        for tile in as_list(t.get("tuiles")):
            if isinstance(tile, dict):
                extra.extend(text_of(tile.get(k)) for k in ("chiffre", "titre", "texte"))
            else:
                extra.append(text_of(tile))
    elif arch in ("A15", "A16"):
        counted.append(text_of(t.get("titre")))
        for x in as_list(t.get("elements")) + as_list(t.get("logos")):
            extra.append(text_of(x.get("nom") if isinstance(x, dict) else x))
    elif arch == "A6":
        counted.extend([text_of(t.get("titre")), text_of(t.get("axe"))])
        for b in as_list(t.get("barres")):
            if isinstance(b, dict):
                extra.extend([text_of(b.get("libelle")), text_of(b.get("etiquette"))])
    elif arch == "A19":
        offres = as_list(t.get("offres")) or [t]
        for o in offres:
            if isinstance(o, dict):
                counted.extend([text_of(o.get("nom")), text_of(o.get("mention")), text_of(o.get("note"))])
                if o.get("prix"):
                    counted.append("prix")      # the price counts as one word
    elif arch == "AF":
        extra.append(text_of(t.get("attendu")))
    else:
        counted.extend(text_of(t.get(k)) for k in VISIBLE_FIELDS)
        extra.extend(text_of(x) for x in as_list(t.get("lignes")))
    return [c for c in counted if c], [e for e in extra if e]


def check(deck, deck_dir, brouillon=False):
    rep = Report()
    archetypes = {str(a.get("id", "")).upper(): a for a in load_json(os.path.join(DATA, "archetypes.json"), [])}
    archetypes["AF"] = {"id": "AF", "nom": "To provide"}
    for fam, nom in (("FIN", "Final slide"), ("COLORIS", "Colorway lineup"), ("FRISE", "Timeline")):
        archetypes[fam] = {"id": fam, "nom": nom}
    table = load_json(os.path.join(DATA, "publics-exigences.json"), {"defaut": "defaut", "publics": {}, "prudence": {}})
    if not archetypes or len(archetypes) < 2:
        rep.warn("deck", "archetypes.json not found: archetype checks are limited.")

    if not isinstance(deck, dict):
        rep.err("deck", "The file must contain a JSON object.")
        return rep
    meta = deck.get("meta") or {}
    theme = deck.get("theme") or {}
    slides = deck.get("slides")
    people = {p.get("id"): p for p in as_list(deck.get("intervenants")) if isinstance(p, dict) and p.get("id")}

    # --- meta -------------------------------------------------------------
    if not meta:
        rep.err("meta", "Missing “meta” block.")
    if not meta.get("titre"):
        rep.warn("meta", "Missing meta.titre.")
    langue = text_of(meta.get("langue") or "fr").lower()[:2]
    if langue not in ("fr", "en"):
        rep.warn("meta", "meta.langue “%s”: fr or en expected." % meta.get("langue"))
    registre = text_of(meta.get("registre")).lower()
    if langue == "fr" and registre not in ("tu", "vous"):
        rep.err("meta", "meta.registre must be “tu” or “vous” in a French deck (ask the user).")
    fmt = norm_key(meta.get("format")).replace("-", " ")
    fmt = FORMAT_ALIASES.get(fmt, fmt.replace(" ", "-"))
    if not meta.get("format"):
        rep.err("meta", "Missing meta.format: keynote, powerpoint, canva, figma-slides or video (ask the user).")
    elif fmt not in FORMATS:
        rep.err("meta", "Unknown meta.format “%s”: keynote, powerpoint, canva, figma-slides or video." % meta.get("format"))
    if meta.get("ratio") and re.sub(r"\s", "", text_of(meta.get("ratio"))) != "16:9":
        rep.err("meta", "meta.ratio is “%s”: the output is always 16:9." % meta.get("ratio"))
    reg_i = text_of(meta.get("registre_intervenants")).lower()
    if reg_i and reg_i not in ("tu", "vous"):
        rep.err("meta", "meta.registre_intervenants “%s”: tu or vous (ask the user)." % meta.get("registre_intervenants"))
    if langue == "fr" and not reg_i and len(people) > 1:
        rep.warn("meta", "Missing meta.registre_intervenants: say whether the speakers use tu or vous with each other (ask the user).")
    if meta.get("variante") and norm_key(meta.get("variante")) not in ("produit", "fonctionnalite", "service", "technologie"):
        rep.warn("meta", "meta.variante “%s”: produit, fonctionnalite, service or technologie." % meta.get("variante"))
    if meta.get("contexte") and norm_key(meta.get("contexte")) not in ("direct", "preenregistre"):
        rep.warn("meta", "meta.contexte “%s”: direct or preenregistre." % meta.get("contexte"))
    if meta.get("affichage_source") and meta["affichage_source"] not in ("sous_le_chiffre", "renvoi", "carton_final", "aucun"):
        rep.err("meta", "meta.affichage_source “%s”: sous_le_chiffre, renvoi, carton_final or aucun." % meta["affichage_source"])
    if not meta.get("public"):
        rep.err("meta", "Missing meta.public: the audience type decides which devices are kept (ask the user).")
    pub_key, pub, known = resolve_public(meta, table)
    if meta.get("public") and not known:
        rep.warn("meta", "Audience “%s” not recognized: default requirements (%s)." % (
            meta["public"].get("type") if isinstance(meta["public"], dict) else meta["public"], pub_key))
    try:
        cible = float(meta.get("duree_min"))
    except (TypeError, ValueError):
        cible = 0.0
        rep.err("meta", "meta.duree_min missing or not a number (target duration in minutes).")

    # --- theme --------------------------------------------------------------
    cols = theme.get("couleurs") or {}
    if not cols:
        rep.err("theme", "Missing theme.couleurs: ask for a design system link or HEX colors.")
    for role in ("fond_sombre", "fond_clair", "texte", "accent"):
        if role not in cols:
            rep.err("theme", "Missing color “%s”." % role)
    for role, val in cols.items():
        if not hex_ok(val):
            rep.err("theme", "Color “%s” = “%s”: HEX code expected (#RRGGBB)." % (role, val))
    if all(r in cols and hex_ok(cols[r]) for r in ("fond_sombre", "fond_clair", "texte", "accent")):
        fs_, fc, tx, ac = (hex6(cols[r]) for r in ("fond_sombre", "fond_clair", "texte", "accent"))
        light = hex6(cols["texte_sur_sombre"]) if hex_ok(cols.get("texte_sur_sombre", "")) else (fc if contrast(fc, fs_) >= 7 else "FFFFFF")
        sec = hex6(cols["texte_secondaire"]) if hex_ok(cols.get("texte_secondaire", "")) else mix(tx, fc, 0.42)
        pairs = [("text on light background", tx, fc, 4.5), ("text on dark background", light, fs_, 4.5),
                 ("secondary text on light background", sec, fc, 3.0),
                 ("accent on dark background (figures)", ac, fs_, 3.0), ("accent on light background (figures)", ac, fc, 3.0)]
        if hex_ok(cols.get("accent2", "")):
            pairs.append(("accent2 on dark background (figure gradient)", hex6(cols["accent2"]), fs_, 3.0))
        for label, a, b, mini in pairs:
            r = contrast(a, b)
            if r < mini:
                rep.warn("theme", "Low contrast: %s = %.1f:1 (%.1f:1 at least)." % (label, r, mini))
    for cle in ("point_accent", "finale_accent"):
        if cle in theme and not isinstance(theme.get(cle), bool):
            rep.warn("theme", "theme.%s “%s”: true or false expected." % (cle, theme.get(cle)))
    pol = theme.get("polices") or {}
    if not pol.get("titre") or not pol.get("texte"):
        rep.warn("theme", "Title and body fonts not set: Arial by default.")
    for role in ("titre", "texte"):
        p = pol.get(role)
        for nom in ([p.get("nom"), p.get("repli")] if isinstance(p, dict) else [p]):
            if nom and APPLE_FONT_RE.search(text_of(nom)):
                rep.err("theme", "Font %s “%s”: an Apple font, not allowed (the grammar, never the brand). "
                                 "Suggest a free sans-serif." % (role, nom))
    if theme.get("logo") and not os.path.exists(os.path.join(deck_dir, theme["logo"])):
        rep.warn("theme", "Logo “%s” not found." % theme["logo"])

    # --- speakers -----------------------------------------------------
    if not people:
        rep.err("intervenants", "No speaker (id, nom, role): the script cannot be assigned.")
    for pid, p in people.items():
        if MARKER_RE.search(text_of(p.get("role"))) or VALIDER_RE.search(text_of(p.get("role"))):
            rep.warn("intervenants", "Role of “%s” is a marker: it would repeat every time this person speaks. "
                                     "Leave the role empty and ask for it once, at delivery." % pid)
    default_speaker = next(iter(people)) if people else ""

    # --- slides -------------------------------------------------------------
    if not isinstance(slides, list) or not slides:
        rep.err("slides", "No slides.")
        return rep
    seen = {}
    total = 0.0
    total_parole = 0              # spoken words, across the whole deck
    tu_total = vous_total = 0
    superlatifs_ecran = []
    fonds = []                    # (where, fond, bloc): background change check
    sequence = []                 # (where, archetype, variant): layout rhythm
    blocs = {}                    # block -> {n, moment, where}: one visual moment per block
    for i, s in enumerate(slides):
        if not isinstance(s, dict):
            rep.err("slide %d" % (i + 1), "Unreadable slide (object expected).")
            continue
        sid = s.get("id") or "slide %d" % (i + 1)
        where = "%02d %s" % (i + 1, sid)
        if not s.get("id"):
            rep.warn(where, "Missing id.")
        elif s["id"] in seen:
            rep.err(where, "Duplicate id (already used by slide %d)." % seen[s["id"]])
        else:
            seen[s["id"]] = i + 1
        arch = text_of(s.get("archetype")).upper()
        t = s.get("textes") or {}
        if not isinstance(t, dict):
            rep.err(where, "“textes” must be an object.")
            t = {}
        if arch not in archetypes:
            rep.err(where, "Unknown archetype “%s” (A1 to A25, FIN, COLORIS, FRISE or AF)." % s.get("archetype"))
        elif arch in SCENES:
            rep.warn(where, "%s is a stage shot (video): on a slide, it becomes a full-bleed photo." % arch)
        elif arch == "A11" and not s.get("variante"):
            rep.warn(where, "A11 with no variant renders like A9 (visual and caption): pick a variant "
                            "(legende-laterale, plusieurs-blocs…) for the line diagram and its highlighted block.")
        fond = text_of(s.get("fond")).lower()
        if fond not in FONDS:
            rep.err(where, "fond “%s”: sombre, clair, image or accent." % s.get("fond"))
        fonds.append((where, fond, text_of(s.get("bloc")).strip()))

        # Layout variant (designs.md) and visual to prepare
        var_raw = s.get("variante")
        var_cle = ""                      # "ARCH/variant" actually drawn
        if var_raw not in (None, ""):
            if not isinstance(var_raw, str):
                rep.err(where, "slide.variante: a variant name is expected (see designs.md).")
            elif arch in archetypes:
                var_cle = resolve_variante(arch, var_raw)
                if not var_cle:
                    propres = VARIANTES.get(arch, [])
                    rep.err(where, "Unknown variant “%s” for %s%s (see designs.md)." % (
                        var_raw, arch, ": " + ", ".join(propres) if propres else
                        ": this archetype has no variants of its own; only the FIN, COLORIS and FRISE ones apply"))
        elif arch in FAMILLES_LIBRES:
            var_cle = arch + "/" + VARIANTES[arch][0]
        if not var_cle:
            var_cle = arch + "/"
        check_visuel(rep, where, s.get("visuel"))
        if var_cle in VARIANTES_IMAGE and not var_cle.endswith("/") and not has_any_image(s) and arch not in IMAGE_EXPECTED:
            rep.warn(where, "Variant “%s” has no image: a fallback is drawn instead (set image.chemin, image.attendu "
                            "and slide.visuel)." % var_cle.split("/")[1])
        if "profondeur" in s and not isinstance(s.get("profondeur"), bool):
            rep.warn(where, "slide.profondeur “%s”: true or false expected (false removes shadow and halo)." % s.get("profondeur"))
        if s.get("appareil") and norm_key(s.get("appareil")) not in APPAREILS:
            rep.warn(where, "slide.appareil “%s”: telephone, tablette, portable or boitier." % s.get("appareil"))
        sequence.append((where, arch, arch + "/" + ORIGINE[arch] if var_cle == arch + "/" and arch in ORIGINE else var_cle))
        bloc_nom = text_of(s.get("bloc")).strip()
        if bloc_nom:
            b = blocs.setdefault(bloc_nom, {"n": 0, "moment": False, "where": where})
            b["n"] += 1
            if arch in MOMENTS_VISUELS or var_cle in VARIANTES_IMAGE:
                b["moment"] = True
        et = s.get("etape")
        if et not in (None, ""):
            try:
                if not 1 <= int(et) <= 16:
                    rep.warn(where, "etape %s is outside the sequence (1 to 16)." % et)
            except (TypeError, ValueError):
                rep.warn(where, "etape “%s”: a number from 1 to 16 is expected." % et)

        # Required fields
        for field in REQUIRED_VARIANTE.get(var_cle, REQUIRED.get(arch, [])):
            v = t.get(field)
            if v is None or (isinstance(v, (str, list)) and len(v) == 0):
                rep.err(where, "Missing field textes.%s for %s." % (field, arch))
        if arch == "A19":
            offres = as_list(t.get("offres")) or [t]
            for o in offres:
                if isinstance(o, dict) and not (o.get("nom") and o.get("prix")):
                    rep.err(where, "Price slide: each offer needs a name and a price.")
            max_offres = 4 if var_cle == "A19/gamme-alignee" else 2
            if len(as_list(t.get("offres"))) > max_offres:
                rep.warn(where, "Price slide: %s at most." % ("four products" if max_offres == 4 else "two offers"))

        # Images
        img = s.get("image")
        img_path = img if isinstance(img, str) else (img or {}).get("chemin") if isinstance(img, dict) else None
        attendu = text_of(img.get("attendu")).strip() if isinstance(img, dict) else ""
        if img_path:
            if not os.path.exists(os.path.join(deck_dir, img_path)):
                rep.warn(where, "Image to provide “%s”%s: a placeholder is drawn instead." % (
                    img_path, " (expected: %s)" % attendu if attendu else "; set image.attendu"))
            elif not re.search(r"\.(png|jpe?g|gif)$", img_path, re.I):
                rep.warn(where, "Image “%s”: PNG, JPEG or GIF expected." % img_path)
        elif arch in IMAGE_EXPECTED and not (arch == "A11" and var_cle not in ("A11/", "A11/carte-annotee")):
            rep.warn(where, "Image expected for %s%s: a placeholder is drawn instead." % (
                arch, " (expected: %s)" % attendu if attendu else "; set image.chemin and image.attendu"))
        if fond == "image" and arch not in IMAGE_EXPECTED and not s.get("image_fond") and (arch in CONTENT_IMAGE or not img_path):
            rep.warn(where, "“image” background with no image_fond: dark background used.")
        for tile in as_list(t.get("tuiles")):
            if isinstance(tile, dict) and tile.get("image") and not os.path.exists(os.path.join(deck_dir, text_of(tile["image"]))):
                rep.warn(where, "Tile image “%s” not found." % tile["image"])
        manquantes = [p for p, _ in element_images(s) if not os.path.exists(os.path.join(deck_dir, p))]
        if manquantes:
            rep.warn(where, "Image%s to provide: %s: a fallback is drawn instead." % (
                "s" if len(manquantes) > 1 else "", ", ".join("“%s”" % p for p in manquantes[:6]) + (" …" if len(manquantes) > 6 else "")))
        sans_logo = []
        for lg in as_list(t.get("logos")):
            if isinstance(lg, dict) and lg.get("image") and not os.path.exists(os.path.join(deck_dir, text_of(lg["image"]))):
                rep.warn(where, "Logo “%s” not found." % lg["image"])
            elif not (isinstance(lg, dict) and lg.get("image")):
                sans_logo.append(text_of(lg.get("nom") if isinstance(lg, dict) else lg) or "?")
        if sans_logo:
            rep.warn(where, "%d logo%s with no image: %s; the name is written as text instead." % (
                len(sans_logo), "s" if len(sans_logo) > 1 else "", ", ".join(sans_logo[:5]) + (" …" if len(sans_logo) > 5 else "")))

        # Words on screen
        counted, extra = visible_texts(arch, t)
        n_words = sum(len(words(x)) for x in counted)
        if n_words > MAX_WORDS:
            rep.warn(where, "%d words on screen (%d at most, lists and quotes excluded)." % (n_words, MAX_WORDS))
        if arch == "A1" and len(words(t.get("titre"))) > 3:
            rep.warn(where, "Title card: three words at most.")
        if len(words(t.get("surtitre"))) > SURTITRE_MAX_WORDS:
            rep.warn(where, "Kicker of %d words: %d at most." % (len(words(t.get("surtitre"))), SURTITRE_MAX_WORDS))
        if arch == "A5" and len(words(t.get("libelle"))) > 9:
            rep.warn(where, "Figure label: nine words at most.")
        if arch == "A4":
            phrases = [p for p in re.split(r"[.!?]+", MARKER_RE.sub("", unvalider(t.get("titre")))) if p.strip()]
            if len(phrases) > 2:
                rep.warn(where, "Thesis statement in %d sentences: more than one idea?" % len(phrases))
        if arch in ("A3", "A7", "A8"):
            lignes = as_list(t.get("lignes"))
            max_lignes = 18 if var_cle == "A7/deux-colonnes" else 6
            if len(lignes) > max_lignes:
                rep.warn(where, "%d lines: %s at most." % (len(lignes), "eighteen" if max_lignes == 18 else "six"))
            for l in lignes:
                if len(words(l)) > 6:
                    rep.warn(where, "Long line (%d words): “%s”." % (len(words(l)), text_of(l)[:60]))
        if arch == "A14":
            tuiles = as_list(t.get("tuiles"))
            lo, hi = TUILES_BORNES.get(var_cle, (4, 8))
            if tuiles and not lo <= len(tuiles) <= hi:
                rep.warn(where, "Bento: %d to %d tiles around the center (%d)." % (lo, hi, len(tuiles)))
            # Software bento: a feature name and a line that places it (4 + 5 words at most).
            max_mots = 9 if var_cle == "A14/fragments-logiciel" else 6
            for tile in tuiles:
                tw = sum(len(words(tile.get(k))) for k in ("chiffre", "titre", "texte")) if isinstance(tile, dict) else len(words(tile))
                if tw > max_mots:
                    rep.warn(where, "Bento tile too wordy (%d words, %d at most)." % (tw, max_mots))
                if isinstance(tile, dict) and len(as_list(tile.get("lignes"))) > 5:
                    rep.warn(where, "Bento list tile: 5 lines at most (%d)." % len(as_list(tile.get("lignes"))))

        # One idea: a single figure on a figure slide
        if arch == "A5":
            groups = number_groups(t.get("chiffre"))
            if len(groups) > 1:
                rep.err(where, "Figure slide with %d figures (%s): one per slide." % (len(groups), ", ".join(groups)))

        # Figures and sources
        source = text_of(s.get("source")).strip()
        has_source = bool(source)
        screen = unvalider(" ".join(counted + extra))
        chiffree = (arch == "A5" and t.get("chiffre")) or arch == "A6" or \
                   (arch == "A14" and any(isinstance(x, dict) and x.get("chiffre") for x in as_list(t.get("tuiles")))) or \
                   (arch not in ("A19", "A20") and (t.get("chiffre") or STAT_RE.search(screen)))
        if chiffree and not has_source:
            level = pub.get("source_chiffre", "recommandee")
            if level == "exigee":
                rep.err(where, "Figure with no source: the “%s” audience requires one (source field)." % pub_key)
            elif level == "recommandee":
                rep.warn(where, "Figure with no source: recommended for the “%s” audience." % pub_key)
        if arch == "A6":
            barres = [b for b in as_list(t.get("barres")) if isinstance(b, dict)]
            if barres and not 2 <= len(barres) <= 6:
                rep.warn(where, "Chart: 2 to 6 bars.")
            sans_etiquette = [b for b in barres if not b.get("etiquette")]
            grad = pub.get("graduation", "valeurs")
            if grad in ("valeurs", "graduee", "exigee") and sans_etiquette and t.get("afficher_valeurs") is False:
                rep.err(where, "Chart with no values: the “%s” audience expects the values written out." % pub_key)
            if grad == "graduee":
                rep.warn(where, "The “%s” audience expects a scaled chart (axes, units, zero origin): "
                                "A6 has no axis, only the values are written. Plan a native chart if the axis matters." % pub_key)
            conc = pub.get("concurrent", "anonymes")
            for b in barres:
                if b.get("mise_en_avant"):
                    continue
                lab = text_of(b.get("libelle"))
                if conc == "nommes" and ANONYME_RE.search(lab):
                    rep.warn(where, "Anonymous competitor “%s”: this audience expects a named, sourced competitor." % lab)
                if conc == "absents" and CONCURRENT_RE.search(lab):
                    rep.warn(where, "Competitor “%s”: this audience expects no comparison with competitors." % lab)
        if arch == "A19" and pub.get("slide_prix") == "non":
            rep.warn(where, "Price slide: the “%s” audience does not expect one (business model or nothing)." % pub_key)
        if JUSQUA_RE.search(screen):
            j = pub.get("jusqua", "avec_condition")
            if j == "interdit":
                rep.err(where, "“Up to” (jusqu'à) on screen: not allowed for the “%s” audience; show only real measurements." % pub_key)
            elif j in ("valeur_typique", "a_eviter"):
                rep.warn(where, "“Up to” (jusqu'à) on screen: for the “%s” audience, show the typical value, and say the maximum with its condition." % pub_key)
            elif not has_source:
                rep.warn(where, "“Up to” (jusqu'à) with no condition: state the conditions in source.")
        sup_re = SUPERLATIFS_EN if langue == "en" else SUPERLATIFS_FR
        sups = sup_re.findall(screen)
        n3 = N3_RE.findall(screen)
        level = pub.get("superlatifs", "moderes")
        if sups or n3:
            bloc = text_of(s.get("bloc")) or "?"
            superlatifs_ecran.extend((bloc, x) for x in sups)
            if level in ("aucun", "sobres"):
                rep.warn(where, "Superlative on screen (%s): none for the “%s” audience." % (", ".join(sorted(set(sups + n3))), pub_key))
            elif n3 and not has_source:
                rep.warn(where, "Absolute superlative (%s) with no proof: it needs a cited external source, or remove it." % ", ".join(sorted(set(n3))))

        # [TO PROVIDE] markers and slide.a_fournir instructions
        found = []
        for x in all_strings({k: v for k, v in s.items() if k not in ("image", "a_fournir")}):
            found.extend(MARKER_RE.findall(x))
        for x in as_list(s.get("a_fournir")):
            if text_of(x).strip():
                found.append("instruction: %s" % text_of(x).strip().rstrip(". "))
        if arch == "AF":
            att = text_of(t.get("attendu"))
            found.append("AF slide (%s; prefer the planned archetype, with short [TO VALIDATE] and [TO PROVIDE] markers)" % (
                att if len(att) <= 70 else att[:69].rstrip() + "…"))
        found = [x for k, x in enumerate(found) if x not in found[:k]]
        if found:
            msg = "Still to provide: %s." % "; ".join(found)
            (rep.warn if brouillon else rep.err)(where, msg)
        # On screen, a [TO PROVIDE] is only a short label; the instruction goes in slide.a_fournir.
        a_l_ecran = [x for x in all_strings(t)] + ([text_of(s.get("source"))] if s.get("source") else [])
        for x in a_l_ecran:
            for m in FOURNIR_LABEL_RE.finditer(x):
                n = len(words(m.group(1)))
                if n > FOURNIR_MAX_WORDS:
                    rep.err(where, "[TO PROVIDE] label of %d words on screen: “%s”. %d words at most; "
                                   "the full instruction goes in slide.a_fournir." % (n, m.group(0), FOURNIR_MAX_WORDS))

        for x in all_strings({k: v for k, v in s.items() if k not in ("image",)}):
            if NESTED_RE.search(x):
                rep.err(where, "Nested markers in “%s”: write them side by side, "
                               "for example [TO VALIDATE: Available from] [TO PROVIDE: date]." % x[:70])
                break
            if UNCLOSED_RE.search(x):
                rep.err(where, "Marker with no closing “]” in “%s”: it would show as is." % re.sub(r"\s+", " ", x)[:70])
                break

        # [TO VALIDATE] proposals: never a figure, a price, a date, a testimonial, a logo, a source
        props = []
        for x in all_strings({k: v for k, v in s.items() if k not in ("image",)}):
            for m in VALIDER_RE.finditer(x):
                txt = re.sub(r"\s+", " ", m.group(1)).strip()
                cle = txt.lower().rstrip(" .!?…")
                if txt and cle not in [p.lower().rstrip(" .!?…") for p in props]:
                    props.append(txt)
                probe = VALIDER_PERMIS_RE.sub(" ", m.group(1))
                for quoi, rx in VALIDER_INTERDITS:
                    hit = rx.search(probe)
                    if hit:
                        rep.err(where, "[TO VALIDATE] “%s” contains %s (“%s”): a figure, a price, a percentage or a "
                                       "date is never proposed. Use [TO PROVIDE: label] instead." % (txt[:60], quoi, hit.group(0)))
                        break
        jamais = [("source", [s.get("source")], "a source")]
        if arch == "A17":
            jamais.append(("testimonial", [t.get("citation"), t.get("auteur")], "a testimonial"))
        if arch == "A16":
            jamais.append(("logos", as_list(t.get("logos")), "a logo"))
        if arch == "A19":
            jamais.append(("price", [o.get("prix") for o in (as_list(t.get("offres")) or [t]) if isinstance(o, dict)], "a price"))
        if arch == "A20":
            jamais.append(("date", [t.get("titre")], "a date"))
        if arch in ("A5", "A6", "A14") or t.get("chiffre"):
            jamais.append(("figure", [t.get("chiffre")] + [b.get(k) for b in as_list(t.get("barres")) + as_list(t.get("tuiles"))
                                                            if isinstance(b, dict) for k in ("chiffre", "etiquette")], "a figure"))
        for champ, vals, quoi in jamais:
            if any(VALIDER_RE.search(x) for v in vals for x in all_strings(v)):
                rep.err(where, "[TO VALIDATE] in %s (%s): this is never proposed. Use [TO PROVIDE: label] instead." % (champ, quoi))
        for txt in props:
            rep.a_valider.append((where, txt))

        # Notes
        segs = note_segments(s, default_speaker)
        if not segs:
            rep.err(where, "Empty notes: the spoken script is missing.")
        for seg in segs:
            if seg["intervenant"] and people and seg["intervenant"] not in people:
                rep.err(where, "Unknown speaker “%s” (see “intervenants”)." % seg["intervenant"])
        if s.get("intervenant") and people and s["intervenant"] not in people:
            rep.err(where, "Unknown slide.intervenant “%s”." % s["intervenant"])
        note_words = sum(len(speech_words(seg["texte"])) for seg in segs)
        total_parole += note_words

        # Duration
        d = s.get("duree_s")
        try:
            d = float(d)
            if d < 0:
                raise ValueError
        except (TypeError, ValueError):
            rep.err(where, "duree_s missing or invalid (seconds).")
            d = 0.0
        total += d
        if d > 0 and note_words and note_words / (d / 60.0) > SPEECH_WPM_MAX:
            rep.warn(where, "Script too long for %d s: %d words, so %d words/min (%d at most)." % (
                d, note_words, note_words / (d / 60.0), SPEECH_WPM_MAX))
        elif d == 0 and note_words > 5:
            rep.warn(where, "duree_s is 0 but the script has %d words." % note_words)

        # Register (heuristic, French decks only): notes without handovers or quotes, plus the on-screen text
        if langue == "fr" and registre in ("tu", "vous"):
            spoken = " ".join(seg["texte"] for seg in segs if seg.get("type") != "relais")
            sample = unvalider(spoken + " " + " ".join(counted + [e for e in extra if arch != "A17"]))
            sample = QUOTE_RE.sub(" ", RELAIS_RE.sub(" ", sample))
            sample = TON_NOM_RE.sub(" ", sample)
            tu = [m.group(0) for m in TU_RE.finditer(sample)]
            vous = [m.group(0) for m in VOUS_RE.finditer(sample)]
            tu_total += len(tu)
            vous_total += len(vous)
            if registre == "vous" and tu:
                rep.warn(where, "Register “vous” expected, informal “tu” found: %s." % ", ".join(sorted(set(x.lower() for x in tu))))
            if registre == "tu" and vous:
                rep.warn(where, "Register “tu” expected, formal “vous” found: %s (a plural “vous” may be intended)." % ", ".join(sorted(set(x.lower() for x in vous))))
            # Handovers: register between speakers (meta.registre_intervenants)
            relais = QUOTE_RE.sub(" ", unvalider(" ".join(seg["texte"] for seg in segs if seg.get("type") == "relais")))
            relais = TON_NOM_RE.sub(" ", relais)
            if reg_i == "vous" and TU_RE.search(relais):
                rep.warn(where, "Handover uses “tu” but the speakers use “vous” with each other (meta.registre_intervenants = vous).")
            if reg_i == "tu" and re.search(r"(?<![\w’'])(?<!merci )(?:à vous|je vous (?:rends|repasse|passe|laisse))\b", relais, re.I):
                rep.warn(where, "Handover uses “vous” but the speakers use “tu” with each other (meta.registre_intervenants = tu).")

    # --- deck-wide summary -------------------------------------------------------
    if langue == "fr" and registre == "vous" and tu_total > vous_total:
        rep.err("register", "The script uses “tu” more than “vous” (%d to %d) but the register is “vous”." % (tu_total, vous_total))
    if langue == "fr" and registre == "tu" and vous_total > tu_total:
        rep.err("register", "The script uses “vous” more than “tu” (%d to %d) but the register is “tu”." % (vous_total, tu_total))
    if langue == "en":
        rep.info("register", "English presentation: the tu/vous check does not apply.")
    # Speaking rate over the target duration: the script must be read in full, aloud, at about 140 words per minute.
    if cible > 0 and total_parole:
        debit = total_parole / cible
        msg = "Script of %d words for %g min, so %d words/min (%d targeted, %d to %d accepted; spoken words, excluding [TO PROVIDE] and directions)." % (
            total_parole, cible, debit, SPEECH_WPM_CIBLE, SPEECH_WPM_MIN, SPEECH_WPM_MAX)
        if debit < SPEECH_WPM_MIN:
            rep.warn("script", msg + " Too short: about %d words are missing, or the target duration is too long." % (
                SPEECH_WPM_CIBLE * cible - total_parole))
        elif debit > SPEECH_WPM_MAX:
            rep.warn("script", msg + " Too long: about %d words too many to say without rushing." % (
                total_parole - SPEECH_WPM_CIBLE * cible))
        else:
            rep.info("script", msg)
    # Background: stay on the same background, and only change it between two blocks.
    for (w1, f1, b1), (w2, f2, b2) in zip(fonds, fonds[1:]):
        if {f1, f2} == {"sombre", "clair"} and (b1 == b2 or not b1 or not b2):
            rep.warn(w2, "Background %s right after a %s slide in the same block: keep the deck's background, "
                         "and only change backgrounds between two blocks." % (f2, f1))
    # Rhythm: never the same layout three times in a row; one visual moment per block.
    for k in range(2, len(sequence)):
        (w0, a0, v0), (w1, a1, v1), (w2, a2, v2) = sequence[k - 2], sequence[k - 1], sequence[k]
        if a2 and a2 in archetypes and (a0, v0) == (a1, v1) == (a2, v2):
            nom_v = v2.split("/", 1)[1] if "/" in v2 else ""
            rep.warn(w2, "Three slides in a row in %s, %s: change the layout or the variant (designs.md, “Choosing a design”)." % (
                a2, "variant %s" % nom_v if nom_v else "no variant"))
    for nom, b in blocs.items():
        if b["n"] >= 2 and not b["moment"]:
            rep.warn("block “%s”" % nom, "No visual moment (A5, A9, A10, A13, A14, A18 or an image variant) over %d slides: "
                                          "plan one (designs.md, “Choosing a design”)." % b["n"])
    if pub.get("superlatifs") == "moderes":
        par_bloc = {}
        for bloc, _ in superlatifs_ecran:
            par_bloc[bloc] = par_bloc.get(bloc, 0) + 1
        for bloc, n in sorted(par_bloc.items()):
            if n > 1:
                rep.warn("tone", "Block “%s”: %d superlatives on screen, only one per block for this audience." % (bloc, n))
    fourchette = pub.get("duree_min_conseillee")
    if cible > 0 and isinstance(fourchette, list) and len(fourchette) == 2 and not fourchette[0] <= cible <= fourchette[1]:
        rep.warn("duration", "Target duration %g min outside the recommended range for this audience (%s to %s min)." % (cible, fourchette[0], fourchette[1]))
    if cible > 0:
        ecart = (total - cible * 60) / (cible * 60)
        msg = "Total duration %d min %02d s for %g min targeted (%+.0f %%)." % (total // 60, total % 60, cible, ecart * 100)
        if abs(ecart) > DUREE_TOLERANCE:
            rep.err("duration", msg + " Gap of more than 15 %: adjust the durations or the content.")
        else:
            rep.info("duration", msg)
    rep.info("audience", "Audience “%s”: source %s, display %s, charts %s, competitors %s, “up to” %s, superlatives %s, price slide %s, suggested register %s." % (
        pub_key, pub.get("source_chiffre", "?"), meta.get("affichage_source") or pub.get("affichage_source", "sous_le_chiffre"),
        pub.get("graduation", "?"), pub.get("concurrent", "?"), pub.get("jusqua", "?"), pub.get("superlatifs", "?"),
        pub.get("slide_prix", "?"), pub.get("registre_suggere", "?")))
    return rep


def main(argv=None):
    ap = argparse.ArgumentParser(description="Checks a deck.json before rendering.")
    ap.add_argument("deck")
    ap.add_argument("--brouillon", action="store_true", help="draft mode: [TO PROVIDE] markers become warnings")
    ap.add_argument("--json", action="store_true", help="JSON output")
    a = ap.parse_args(argv)
    try:
        with open(a.deck, encoding="utf-8") as f:
            deck = json.load(f)
    except OSError as e:
        print("Cannot read the file: %s" % e, file=sys.stderr)
        return 2
    except ValueError as e:
        print("Invalid JSON: %s" % e, file=sys.stderr)
        return 2
    rep = check(deck, os.path.dirname(os.path.abspath(a.deck)), brouillon=a.brouillon)
    if a.json:
        out = {k: [{"ou": w, "message": m} for w, m in getattr(rep, k)] for k in ("erreurs", "avertissements", "infos")}
        out["a_valider"] = [{"ou": w, "texte": m} for w, m in rep.a_valider]
        print(json.dumps(out, ensure_ascii=False, indent=2))
    else:
        n = len(deck.get("slides") or []) if isinstance(deck, dict) else 0
        print("check_deck: %s (%d slides)" % (os.path.basename(a.deck), n))
        for title, items in (("BLOCKING ERRORS", rep.erreurs), ("WARNINGS", rep.avertissements),
                             ("TO VALIDATE: proposals to get approved at delivery", rep.a_valider), ("INFO", rep.infos)):
            if items:
                print("\n%s (%d)" % (title, len(items)))
                for w, m in items:
                    print("  [%s] %s" % (w, m))
        print("\nResult: %d blocking error(s), %d warning(s), %d proposal(s) to validate." % (
            len(rep.erreurs), len(rep.avertissements), len(rep.a_valider)))
    return 1 if rep.erreurs else 0


if __name__ == "__main__":
    sys.exit(main())
