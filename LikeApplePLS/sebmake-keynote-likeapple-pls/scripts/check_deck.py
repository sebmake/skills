#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""check_deck.py : contrôle un deck.json avant le rendu et liste les écarts.

Usage :
    python3 check_deck.py deck.json [--brouillon] [--json]

--brouillon : les marqueurs [À FOURNIR] restants et les consignes slide.a_fournir
              deviennent des avertissements (pendant la rédaction ; à retirer avant de présenter).
--json      : sortie machine (erreurs, avertissements, a_valider, infos).

Les propositions [À VALIDER : texte] ne bloquent jamais : elles sont listées à part
(section « À VALIDER »), pour que la livraison les fasse valider une à une.

Design : slide.variante doit exister pour l'archétype (table VARIANTES, copie de la liste du
moteur) ; slide.visuel décrit le visuel à préparer. Avertissement si trois slides de suite ont
le même archétype et la même variante, ou si un bloc de deux slides ou plus n'a aucun moment
visuel (A5, A9, A10, A13, A14, A18 ou variante à image). Voir ../references/designs.md.

Code de sortie : 0 sans erreur bloquante, 1 s'il y a au moins une erreur bloquante,
2 si le fichier est illisible.

Compatible Python 3.9, sans dépendance. Format attendu : ../references/deck-spec.md.
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
# Variantes que build_deck.js sait dessiner (slide.variante), par archétype : copie de la liste du
# moteur (references/designs.md les décrit une à une, deck-spec.md les résume). Sans variante, le
# moteur garde le rendu d'origine de l'archétype ; FIN, COLORIS et FRISE prennent leur première
# variante. Les variantes de FIN, COLORIS et FRISE se posent aussi sur n'importe quel archétype.
# À tenir à jour quand le moteur change.
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
    # Plans de scène : acceptés, rendus en photo plein cadre (avertissement).
    "A22": ["hall-ecran", "scene-mur", "panneau-verre"],
    "A23": ["mot-coupe", "contenu-lisible", "interface-geante", "slide-floue"],
    "A24": ["large-centre", "taille-centre", "decor-sujet"],
    "A25": ["table-flux", "mains-fond-uni", "epaule", "table-haute", "tend-appareil"],
    "FIN": ["signe-seul", "signe-et-ligne", "signe-et-evenement", "signe-sur-photo", "mot-final"],
    "COLORIS": ["rangee-alignee", "rangee-chevauchee", "eventail", "un-par-un", "mur"],
    "FRISE": ["rangee-datee", "generations", "trois-jalons", "courbe-et-saut", "objet-du-passe"],
}
FAMILLES_LIBRES = ("FIN", "COLORIS", "FRISE")       # archétypes du moteur hors catalogue A1 à A25
# Variantes qui posent une photo, une capture, un objet ou un produit : elles comptent comme moment
# visuel (« ARCH/variante » ; « ARCH/ » = l'archétype sans variante).
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
# Sans variante, le rendu d'origine est celui de la première variante pour ces archétypes.
ORIGINE = {"A1": "aplat", "A3": "centre", "A4": "aplat", "A5": "centre", "A7": "centree", "A17": "courte"}
# Champs obligatoires qui changent avec la variante (sinon ceux de REQUIRED pour l'archétype).
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
# Archétypes qui sont toujours un moment visuel fort.
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
FOURNIR_MAX_WORDS = 3          # libellé [À FOURNIR] affiché à l'écran
SURTITRE_MAX_WORDS = 3
DUREE_TOLERANCE = 0.15

MARKER_RE = re.compile(r"\[(?:À|A) FOURNIR[^\]]*\]|\[TO PROVIDE[^\]]*\]", re.I)
FOURNIR_LABEL_RE = re.compile(r"\[(?:(?:À|A) FOURNIR|TO PROVIDE)\s*:?\s*([^\]]*)\]", re.I)
VALIDER_RE = re.compile(r"\[(?:(?:À|A) VALIDER|TO VALIDATE)\s*:?\s*([^\]]*)\]", re.I)
BRACKET_RE = re.compile(r"\[[^\]]*\]|\([^)]*\)")      # indications de scène dans le texte à dire
APPLE_FONT_RE = re.compile(r"^\s*(?:\.?SF(?:\s|$|\s*(?:Pro|Compact|Mono))|San Francisco|New York|-apple-system)", re.I)
# Ce qu'une proposition [À VALIDER] ne contient jamais : chiffre, prix, pourcentage, date.
VALIDER_INTERDITS = [
    ("un chiffre", re.compile(r"\d")),
    ("un pourcentage", re.compile(r"%|\bpour\s?cent\b|\bper\s?cent\b|\bpercent\b", re.I)),
    ("un prix", re.compile(r"[€$£¥]|\b(?:euros?|dollars?|HT|TTC|gratuit(?:e|s|es)?|sans\s+(?:surcoût|frais)|"
                          r"free of charge|for free|at no (?:extra )?cost)\b", re.I)),
    ("une date", re.compile(r"\b(?:janvier|février|fevrier|mars|avril|mai|juin|juillet|août|aout|septembre|octobre|"
                           r"novembre|décembre|decembre|january|february|april|june|july|august|september|october|"
                           r"november|december|trimestre|semestre|quarter)\b|"
                           r"\b(?:in|by|from|until|since|early|late|mid|this|next)[\s-]+(?:may|march)\b", re.I)),
    ("un nombre", re.compile(r"\b(?:deux|trois|quatre|cinq|six|sept|huit|dix|onze|douze|treize|quatorze|quinze|"
                            r"vingts?|trente|quarante|cinquante|soixante|cents?|mille|millions?|milliards?|dizaines?|"
                            r"douzaines?|centaines?|milliers?|moitié|two|three|four|five|six|seven|eight|nine|ten|"
                            r"eleven|twelve|twenty|thirty|forty|fifty|hundreds?|thousands?|millions?|billions?|"
                            r"dozens?|half|twice)\b|"
                            r"\b(?:en|sous|in|within|under)\s+(?:un|une|one|a|an)\s+(?:secondes?|minutes?|heures?|"
                            r"journées?|jours?|semaines?|mois|ans?|années?|seconds?|hours?|days?|weeks?|months?|years?)\b", re.I)),
]
NESTED_RE = re.compile(r"\[(?:(?:À|A) (?:VALIDER|FOURNIR)|TO (?:VALIDATE|PROVIDE))[^\]]*\[", re.I)
# Marqueur ouvert jamais fermé : le rendu l'afficherait tel quel. Un \n dans un marqueur fermé est permis.
UNCLOSED_RE = re.compile(r"\[(?:(?:À|A) (?:VALIDER|FOURNIR)|TO (?:VALIDATE|PROVIDE|CONFIRM))[^\]\[]*$", re.I)
# « les deux » n'est pas un chiffre, ni un sigle comme B2B ou B2C
VALIDER_PERMIS_RE = re.compile(r"\b(?:tous|toutes|les|nos|vos)\s+deux\b|\bboth\b|\b[A-Za-z]+\d+[A-Za-z]\w*", re.I)
TU_RE = re.compile(r"(?<![\w’'])(tu|te|toi|ton|ta|tes)(?![\w’'])|(?<![\w’'])t['’](?=[a-zàâäéèêëîïôöùûüyh])", re.I)
VOUS_RE = re.compile(r"(?<![\w’'])(vous|votre|vos|vôtre|vôtres)(?![\w’'])", re.I)
TON_NOM_RE = re.compile(r"\b(le|un|du|ce|même|bon|mauvais)\s+ton\b", re.I)   # « le ton » n'est pas un tutoiement
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
# Utilitaires
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
    """[À VALIDER : texte] -> texte : une proposition se lit comme du vrai contenu."""
    return VALIDER_RE.sub(lambda m: m.group(1), text_of(s))


def speech_words(s):
    """Mots à dire : propositions comprises, sans [À FOURNIR] ni indications entre crochets ou parenthèses."""
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
    s = re.sub(r"(\d+)\s*h\s*(\d{2})\b", r"\1h\2", s)          # 3 h 10 = une durée
    s = re.sub(r"(\d+)\s*/\s*(\d+)", r"\1/\2", s)              # 24/7 = un rythme
    s = re.sub(r"(\d)[\s  ](?=\d{3}\b)", r"\1", s)    # 1 299 = un nombre
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
    """Renvoie (clé, réglages, reconnu). Une liste de types = public mixte : réglage le plus prudent."""
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
    """« ARCH/variante » que le moteur dessine, ou "" si la variante est inconnue pour cet archétype."""
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
    """La slide porte-t-elle une image (principale, liste, fond, visuel décrit ou image d'élément) ?"""
    if img_path_of(slide) or slide.get("images") or slide.get("image_fond") or slide.get("visuel") is not None:
        return True
    t = slide.get("textes") or {}
    for key in ("tuiles", "elements", "logos", "offres", "coloris", "jalons", "pictos"):
        for x in as_list(t.get(key)) if isinstance(t, dict) else []:
            if (isinstance(x, dict) and x.get("image")) or (key == "pictos" and isinstance(x, str) and x):
                return True
    return False


def element_images(slide):
    """(chemin, libellé) des images portées par la slide hors slide.image : listes, éléments, logos annexes."""
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
    """1920 × 1080, [1920, 1080], {"largeur": 1920, "hauteur": 1080}, 2000 (grand côté) ou « 2000 px de haut »."""
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
    """slide.visuel : un objet (ou une liste d'objets) qui décrit le visuel à préparer."""
    if v is None:
        return
    items = v if isinstance(v, list) else [v]
    for k, it in enumerate(items):
        lab = "slide.visuel" if len(items) == 1 else "slide.visuel[%d]" % (k + 1)
        if not isinstance(it, dict):
            rep.err(where, "%s : objet attendu, {type, brief, fond_transparent, angle, resolution_min}." % lab)
            continue
        inconnus = sorted(set(it) - VISUEL_CHAMPS)
        if inconnus:
            rep.warn(where, "%s : champ(s) inconnu(s) %s (type, brief, fond_transparent, angle, resolution_min, format, chemin)." % (
                lab, ", ".join(inconnus)))
        if not text_of(it.get("type")).strip():
            rep.warn(where, "%s sans type : capture, photo, produit, objet, icone, logo, schema, matiere, pictogrammes, "
                            "vignettes ou video." % lab)
        elif norm_type_visuel(it.get("type")) not in TYPES_VISUEL:
            rep.warn(where, "%s : type « %s » inconnu (capture, photo, produit, objet, icone, logo, schema, matiere, "
                            "pictogrammes, vignettes, video)." % (lab, it.get("type")))
        if not text_of(it.get("brief")).strip():
            rep.warn(where, "%s sans brief : dis ce qu'il doit montrer, son cadrage et sa lumière." % lab)
        if "fond_transparent" in it and not isinstance(it.get("fond_transparent"), bool):
            rep.warn(where, "%s.fond_transparent « %s » : true ou false attendu." % (lab, it.get("fond_transparent")))
        if "angle" in it and not isinstance(it.get("angle"), str):
            rep.warn(where, "%s.angle : texte attendu (face, trois-quarts, profil, dessus…)." % lab)
        if it.get("resolution_min") is not None and not resolution_ok(it.get("resolution_min")):
            rep.warn(where, "%s.resolution_min « %s » : écris « 1920 × 1080 », [1920, 1080] ou un nombre de pixels." % (
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
# Contrôle
# ---------------------------------------------------------------------------
class Report(object):
    def __init__(self):
        self.erreurs, self.avertissements, self.infos = [], [], []
        self.a_valider = []       # (slide, texte proposé) : à faire valider à la livraison

    def err(self, where, msg):
        self.erreurs.append((where, msg))

    def warn(self, where, msg):
        self.avertissements.append((where, msg))

    def info(self, where, msg):
        self.infos.append((where, msg))


def visible_texts(arch, t):
    """Textes affichés sur la slide, avec indication de ce qui compte dans la limite de mots."""
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
                    counted.append("prix")      # le prix compte pour un mot
    elif arch == "AF":
        extra.append(text_of(t.get("attendu")))
    else:
        counted.extend(text_of(t.get(k)) for k in VISIBLE_FIELDS)
        extra.extend(text_of(x) for x in as_list(t.get("lignes")))
    return [c for c in counted if c], [e for e in extra if e]


def check(deck, deck_dir, brouillon=False):
    rep = Report()
    archetypes = {str(a.get("id", "")).upper(): a for a in load_json(os.path.join(DATA, "archetypes.json"), [])}
    archetypes["AF"] = {"id": "AF", "nom": "À fournir"}
    for fam, nom in (("FIN", "Slide finale"), ("COLORIS", "Gamme de coloris"), ("FRISE", "Frise")):
        archetypes[fam] = {"id": fam, "nom": nom}
    table = load_json(os.path.join(DATA, "publics-exigences.json"), {"defaut": "defaut", "publics": {}, "prudence": {}})
    if not archetypes or len(archetypes) < 2:
        rep.warn("deck", "archetypes.json introuvable : contrôle des archétypes limité.")

    if not isinstance(deck, dict):
        rep.err("deck", "Le fichier doit contenir un objet JSON.")
        return rep
    meta = deck.get("meta") or {}
    theme = deck.get("theme") or {}
    slides = deck.get("slides")
    people = {p.get("id"): p for p in as_list(deck.get("intervenants")) if isinstance(p, dict) and p.get("id")}

    # --- meta -------------------------------------------------------------
    if not meta:
        rep.err("meta", "Bloc « meta » absent.")
    if not meta.get("titre"):
        rep.warn("meta", "meta.titre absent.")
    langue = text_of(meta.get("langue") or "fr").lower()[:2]
    if langue not in ("fr", "en"):
        rep.warn("meta", "meta.langue « %s » : fr ou en attendu." % meta.get("langue"))
    registre = text_of(meta.get("registre")).lower()
    if langue == "fr" and registre not in ("tu", "vous"):
        rep.err("meta", "meta.registre doit valoir « tu » ou « vous » (à demander à l'utilisateur).")
    fmt = norm_key(meta.get("format")).replace("-", " ")
    fmt = FORMAT_ALIASES.get(fmt, fmt.replace(" ", "-"))
    if not meta.get("format"):
        rep.err("meta", "meta.format absent : keynote, powerpoint, canva, figma-slides ou video (à demander).")
    elif fmt not in FORMATS:
        rep.err("meta", "meta.format « %s » inconnu : keynote, powerpoint, canva, figma-slides ou video." % meta.get("format"))
    if meta.get("ratio") and re.sub(r"\s", "", text_of(meta.get("ratio"))) != "16:9":
        rep.err("meta", "meta.ratio vaut « %s » : la sortie est toujours en 16:9." % meta.get("ratio"))
    reg_i = text_of(meta.get("registre_intervenants")).lower()
    if reg_i and reg_i not in ("tu", "vous"):
        rep.err("meta", "meta.registre_intervenants « %s » : tu ou vous (à demander à l'utilisateur)." % meta.get("registre_intervenants"))
    if langue == "fr" and not reg_i and len(people) > 1:
        rep.warn("meta", "meta.registre_intervenants absent : préciser si les intervenants se tutoient ou se vouvoient (à demander).")
    if meta.get("variante") and norm_key(meta.get("variante")) not in ("produit", "fonctionnalite", "service", "technologie"):
        rep.warn("meta", "meta.variante « %s » : produit, fonctionnalite, service ou technologie." % meta.get("variante"))
    if meta.get("contexte") and norm_key(meta.get("contexte")) not in ("direct", "preenregistre"):
        rep.warn("meta", "meta.contexte « %s » : direct ou preenregistre." % meta.get("contexte"))
    if meta.get("affichage_source") and meta["affichage_source"] not in ("sous_le_chiffre", "renvoi", "carton_final", "aucun"):
        rep.err("meta", "meta.affichage_source « %s » : sous_le_chiffre, renvoi, carton_final ou aucun." % meta["affichage_source"])
    if not meta.get("public"):
        rep.err("meta", "meta.public absent : la typologie de public décide des procédés gardés (à demander).")
    pub_key, pub, known = resolve_public(meta, table)
    if meta.get("public") and not known:
        rep.warn("meta", "Public « %s » non reconnu : exigences par défaut (%s)." % (
            meta["public"].get("type") if isinstance(meta["public"], dict) else meta["public"], pub_key))
    try:
        cible = float(meta.get("duree_min"))
    except (TypeError, ValueError):
        cible = 0.0
        rep.err("meta", "meta.duree_min absente ou non numérique (durée cible en minutes).")

    # --- thème --------------------------------------------------------------
    cols = theme.get("couleurs") or {}
    if not cols:
        rep.err("theme", "theme.couleurs absent : demander un lien de design system ou des couleurs HEX.")
    for role in ("fond_sombre", "fond_clair", "texte", "accent"):
        if role not in cols:
            rep.err("theme", "Couleur « %s » absente." % role)
    for role, val in cols.items():
        if not hex_ok(val):
            rep.err("theme", "Couleur « %s » = « %s » : code HEX attendu (#RRGGBB)." % (role, val))
    if all(r in cols and hex_ok(cols[r]) for r in ("fond_sombre", "fond_clair", "texte", "accent")):
        fs_, fc, tx, ac = (hex6(cols[r]) for r in ("fond_sombre", "fond_clair", "texte", "accent"))
        light = hex6(cols["texte_sur_sombre"]) if hex_ok(cols.get("texte_sur_sombre", "")) else (fc if contrast(fc, fs_) >= 7 else "FFFFFF")
        sec = hex6(cols["texte_secondaire"]) if hex_ok(cols.get("texte_secondaire", "")) else mix(tx, fc, 0.42)
        pairs = [("texte sur fond clair", tx, fc, 4.5), ("texte sur fond sombre", light, fs_, 4.5),
                 ("texte secondaire sur fond clair", sec, fc, 3.0),
                 ("accent sur fond sombre (chiffres)", ac, fs_, 3.0), ("accent sur fond clair (chiffres)", ac, fc, 3.0)]
        if hex_ok(cols.get("accent2", "")):
            pairs.append(("accent2 sur fond sombre (dégradé du chiffre)", hex6(cols["accent2"]), fs_, 3.0))
        for label, a, b, mini in pairs:
            r = contrast(a, b)
            if r < mini:
                rep.warn("theme", "Contraste faible : %s = %.1f:1 (%.1f:1 au moins)." % (label, r, mini))
    for cle in ("point_accent", "finale_accent"):
        if cle in theme and not isinstance(theme.get(cle), bool):
            rep.warn("theme", "theme.%s « %s » : true ou false attendu." % (cle, theme.get(cle)))
    pol = theme.get("polices") or {}
    if not pol.get("titre") or not pol.get("texte"):
        rep.warn("theme", "Polices titre et texte non précisées : Arial par défaut.")
    for role in ("titre", "texte"):
        p = pol.get(role)
        for nom in ([p.get("nom"), p.get("repli")] if isinstance(p, dict) else [p]):
            if nom and APPLE_FONT_RE.search(text_of(nom)):
                rep.err("theme", "Police %s « %s » : police d'Apple, interdite (la grammaire, jamais la marque). "
                                 "Proposer une linéale libre de droits." % (role, nom))
    if theme.get("logo") and not os.path.exists(os.path.join(deck_dir, theme["logo"])):
        rep.warn("theme", "Logo « %s » introuvable." % theme["logo"])

    # --- intervenants -----------------------------------------------------
    if not people:
        rep.err("intervenants", "Aucun intervenant (id, nom, rôle) : le script ne peut pas être attribué.")
    for pid, p in people.items():
        if MARKER_RE.search(text_of(p.get("role"))) or VALIDER_RE.search(text_of(p.get("role"))):
            rep.warn("intervenants", "Rôle de « %s » en marqueur : il serait répété à chaque prise de parole. "
                                     "Laisse le rôle vide et demande-le une fois, à la livraison." % pid)
    default_speaker = next(iter(people)) if people else ""

    # --- slides -------------------------------------------------------------
    if not isinstance(slides, list) or not slides:
        rep.err("slides", "Aucune slide.")
        return rep
    seen = {}
    total = 0.0
    total_parole = 0              # mots à dire, sur tout le deck
    tu_total = vous_total = 0
    superlatifs_ecran = []
    fonds = []                    # (where, fond, bloc) : contrôle des changements de fond
    sequence = []                 # (where, archétype, variante) : rythme des compositions
    blocs = {}                    # bloc -> {n, moment, where} : un moment visuel par bloc
    for i, s in enumerate(slides):
        if not isinstance(s, dict):
            rep.err("slide %d" % (i + 1), "Slide illisible (objet attendu).")
            continue
        sid = s.get("id") or "slide %d" % (i + 1)
        where = "%02d %s" % (i + 1, sid)
        if not s.get("id"):
            rep.warn(where, "id absent.")
        elif s["id"] in seen:
            rep.err(where, "id en double (déjà utilisé par la slide %d)." % seen[s["id"]])
        else:
            seen[s["id"]] = i + 1
        arch = text_of(s.get("archetype")).upper()
        t = s.get("textes") or {}
        if not isinstance(t, dict):
            rep.err(where, "« textes » doit être un objet.")
            t = {}
        if arch not in archetypes:
            rep.err(where, "Archétype inconnu « %s » (A1 à A25, FIN, COLORIS, FRISE ou AF)." % s.get("archetype"))
        elif arch in SCENES:
            rep.warn(where, "%s est un plan de scène (vidéo) : en slide, il devient une photo plein cadre." % arch)
        elif arch == "A11" and not s.get("variante"):
            rep.warn(where, "A11 sans variante est rendu comme A9 (visuel et légende) : prends une variante "
                            "(legende-laterale, plusieurs-blocs…) pour le schéma au trait et son bloc allumé.")
        fond = text_of(s.get("fond")).lower()
        if fond not in FONDS:
            rep.err(where, "fond « %s » : sombre, clair, image ou accent." % s.get("fond"))
        fonds.append((where, fond, text_of(s.get("bloc")).strip()))

        # Variante de composition (designs.md) et visuel à préparer
        var_raw = s.get("variante")
        var_cle = ""                      # « ARCH/variante » réellement dessinée
        if var_raw not in (None, ""):
            if not isinstance(var_raw, str):
                rep.err(where, "slide.variante : le nom d'une variante attendu (voir designs.md).")
            elif arch in archetypes:
                var_cle = resolve_variante(arch, var_raw)
                if not var_cle:
                    propres = VARIANTES.get(arch, [])
                    rep.err(where, "Variante « %s » inconnue pour %s%s (voir designs.md)." % (
                        var_raw, arch, " : " + ", ".join(propres) if propres else
                        " : cet archétype n'a pas de variante propre ; seules celles de FIN, COLORIS et FRISE s'y posent"))
        elif arch in FAMILLES_LIBRES:
            var_cle = arch + "/" + VARIANTES[arch][0]
        if not var_cle:
            var_cle = arch + "/"
        check_visuel(rep, where, s.get("visuel"))
        if var_cle in VARIANTES_IMAGE and not var_cle.endswith("/") and not has_any_image(s) and arch not in IMAGE_EXPECTED:
            rep.warn(where, "Variante « %s » sans image : repli dessiné à la place (précise image.chemin, image.attendu "
                            "et slide.visuel)." % var_cle.split("/")[1])
        if "profondeur" in s and not isinstance(s.get("profondeur"), bool):
            rep.warn(where, "slide.profondeur « %s » : true ou false attendu (false retire ombre et halo)." % s.get("profondeur"))
        if s.get("appareil") and norm_key(s.get("appareil")) not in APPAREILS:
            rep.warn(where, "slide.appareil « %s » : telephone, tablette, portable ou boitier." % s.get("appareil"))
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
                    rep.warn(where, "etape %s hors de la séquence (1 à 16)." % et)
            except (TypeError, ValueError):
                rep.warn(where, "etape « %s » : numéro de 1 à 16 attendu." % et)

        # Champs obligatoires
        for field in REQUIRED_VARIANTE.get(var_cle, REQUIRED.get(arch, [])):
            v = t.get(field)
            if v is None or (isinstance(v, (str, list)) and len(v) == 0):
                rep.err(where, "Champ textes.%s manquant pour %s." % (field, arch))
        if arch == "A19":
            offres = as_list(t.get("offres")) or [t]
            for o in offres:
                if isinstance(o, dict) and not (o.get("nom") and o.get("prix")):
                    rep.err(where, "Slide de prix : chaque offre a besoin d'un nom et d'un prix.")
            max_offres = 4 if var_cle == "A19/gamme-alignee" else 2
            if len(as_list(t.get("offres"))) > max_offres:
                rep.warn(where, "Slide de prix : %s au plus." % ("quatre produits" if max_offres == 4 else "deux offres"))

        # Images
        img = s.get("image")
        img_path = img if isinstance(img, str) else (img or {}).get("chemin") if isinstance(img, dict) else None
        attendu = text_of(img.get("attendu")).strip() if isinstance(img, dict) else ""
        if img_path:
            if not os.path.exists(os.path.join(deck_dir, img_path)):
                rep.warn(where, "Image à fournir « %s »%s : placeholder dessiné à la place." % (
                    img_path, " (attendu : %s)" % attendu if attendu else " ; précise image.attendu"))
            elif not re.search(r"\.(png|jpe?g|gif)$", img_path, re.I):
                rep.warn(where, "Image « %s » : PNG, JPEG ou GIF attendu." % img_path)
        elif arch in IMAGE_EXPECTED and not (arch == "A11" and var_cle not in ("A11/", "A11/carte-annotee")):
            rep.warn(where, "Image attendue pour %s%s : placeholder dessiné à la place." % (
                arch, " (attendu : %s)" % attendu if attendu else " ; précise image.chemin et image.attendu"))
        if fond == "image" and arch not in IMAGE_EXPECTED and not s.get("image_fond") and (arch in CONTENT_IMAGE or not img_path):
            rep.warn(where, "Fond « image » sans image_fond : fond sombre utilisé.")
        for tile in as_list(t.get("tuiles")):
            if isinstance(tile, dict) and tile.get("image") and not os.path.exists(os.path.join(deck_dir, text_of(tile["image"]))):
                rep.warn(where, "Image de tuile « %s » introuvable." % tile["image"])
        manquantes = [p for p, _ in element_images(s) if not os.path.exists(os.path.join(deck_dir, p))]
        if manquantes:
            rep.warn(where, "Image%s à fournir : %s : repli dessiné à la place." % (
                "s" if len(manquantes) > 1 else "", ", ".join("« %s »" % p for p in manquantes[:6]) + (" …" if len(manquantes) > 6 else "")))
        sans_logo = []
        for lg in as_list(t.get("logos")):
            if isinstance(lg, dict) and lg.get("image") and not os.path.exists(os.path.join(deck_dir, text_of(lg["image"]))):
                rep.warn(where, "Logo « %s » introuvable." % lg["image"])
            elif not (isinstance(lg, dict) and lg.get("image")):
                sans_logo.append(text_of(lg.get("nom") if isinstance(lg, dict) else lg) or "?")
        if sans_logo:
            rep.warn(where, "%d logo%s sans image : %s ; le nom s'écrit en texte à la place." % (
                len(sans_logo), "s" if len(sans_logo) > 1 else "", ", ".join(sans_logo[:5]) + (" …" if len(sans_logo) > 5 else "")))

        # Mots à l'écran
        counted, extra = visible_texts(arch, t)
        n_words = sum(len(words(x)) for x in counted)
        if n_words > MAX_WORDS:
            rep.warn(where, "%d mots à l'écran (%d au plus, hors listes et citations)." % (n_words, MAX_WORDS))
        if arch == "A1" and len(words(t.get("titre"))) > 3:
            rep.warn(where, "Carte-titre : trois mots au plus.")
        if len(words(t.get("surtitre"))) > SURTITRE_MAX_WORDS:
            rep.warn(where, "Surtitre de %d mots : %d au plus." % (len(words(t.get("surtitre"))), SURTITRE_MAX_WORDS))
        if arch == "A5" and len(words(t.get("libelle"))) > 9:
            rep.warn(where, "Libellé du chiffre : neuf mots au plus.")
        if arch == "A4":
            phrases = [p for p in re.split(r"[.!?]+", MARKER_RE.sub("", unvalider(t.get("titre")))) if p.strip()]
            if len(phrases) > 2:
                rep.warn(where, "Phrase-thèse en %d phrases : plus d'une idée ?" % len(phrases))
        if arch in ("A3", "A7", "A8"):
            lignes = as_list(t.get("lignes"))
            max_lignes = 18 if var_cle == "A7/deux-colonnes" else 6
            if len(lignes) > max_lignes:
                rep.warn(where, "%d lignes : %s au plus." % (len(lignes), "dix-huit" if max_lignes == 18 else "six"))
            for l in lignes:
                if len(words(l)) > 6:
                    rep.warn(where, "Ligne longue (%d mots) : « %s »." % (len(words(l)), text_of(l)[:60]))
        if arch == "A14":
            tuiles = as_list(t.get("tuiles"))
            lo, hi = TUILES_BORNES.get(var_cle, (4, 8))
            if tuiles and not lo <= len(tuiles) <= hi:
                rep.warn(where, "Bento : %d à %d tuiles autour du centre (%d)." % (lo, hi, len(tuiles)))
            # Bento logiciel : un nom de fonction et une ligne qui le situe (4 + 5 mots au plus).
            max_mots = 9 if var_cle == "A14/fragments-logiciel" else 6
            for tile in tuiles:
                tw = sum(len(words(tile.get(k))) for k in ("chiffre", "titre", "texte")) if isinstance(tile, dict) else len(words(tile))
                if tw > max_mots:
                    rep.warn(where, "Tuile de bento trop bavarde (%d mots, %d au plus)." % (tw, max_mots))
                if isinstance(tile, dict) and len(as_list(tile.get("lignes"))) > 5:
                    rep.warn(where, "Tuile-liste de bento : 5 lignes au plus (%d)." % len(as_list(tile.get("lignes"))))

        # Une idée : un seul chiffre sur une slide-chiffre
        if arch == "A5":
            groups = number_groups(t.get("chiffre"))
            if len(groups) > 1:
                rep.err(where, "Slide-chiffre avec %d chiffres (%s) : un seul par slide." % (len(groups), ", ".join(groups)))

        # Chiffres et sources
        source = text_of(s.get("source")).strip()
        has_source = bool(source)
        screen = unvalider(" ".join(counted + extra))
        chiffree = (arch == "A5" and t.get("chiffre")) or arch == "A6" or \
                   (arch == "A14" and any(isinstance(x, dict) and x.get("chiffre") for x in as_list(t.get("tuiles")))) or \
                   (arch not in ("A19", "A20") and (t.get("chiffre") or STAT_RE.search(screen)))
        if chiffree and not has_source:
            level = pub.get("source_chiffre", "recommandee")
            if level == "exigee":
                rep.err(where, "Chiffre sans source : le public « %s » l'exige (champ source)." % pub_key)
            elif level == "recommandee":
                rep.warn(where, "Chiffre sans source : recommandée pour le public « %s »." % pub_key)
        if arch == "A6":
            barres = [b for b in as_list(t.get("barres")) if isinstance(b, dict)]
            if barres and not 2 <= len(barres) <= 6:
                rep.warn(where, "Graphique : 2 à 6 barres.")
            sans_etiquette = [b for b in barres if not b.get("etiquette")]
            grad = pub.get("graduation", "valeurs")
            if grad in ("valeurs", "graduee", "exigee") and sans_etiquette and t.get("afficher_valeurs") is False:
                rep.err(where, "Graphique sans valeurs : le public « %s » attend les valeurs écrites." % pub_key)
            if grad == "graduee":
                rep.warn(where, "Le public « %s » attend un graphique gradué (axes, unités, origine à zéro) : "
                                "A6 n'a pas d'axe, seules les valeurs sont écrites. Prévoir un graphique natif si l'axe compte." % pub_key)
            conc = pub.get("concurrent", "anonymes")
            for b in barres:
                if b.get("mise_en_avant"):
                    continue
                lab = text_of(b.get("libelle"))
                if conc == "nommes" and ANONYME_RE.search(lab):
                    rep.warn(where, "Concurrent anonyme « %s » : ce public attend un concurrent nommé et sourcé." % lab)
                if conc == "absents" and CONCURRENT_RE.search(lab):
                    rep.warn(where, "Concurrent « %s » : ce public n'attend aucune comparaison avec la concurrence." % lab)
        if arch == "A19" and pub.get("slide_prix") == "non":
            rep.warn(where, "Slide de prix : le public « %s » n'en attend pas (modèle économique ou rien)." % pub_key)
        if JUSQUA_RE.search(screen):
            j = pub.get("jusqua", "avec_condition")
            if j == "interdit":
                rep.err(where, "« jusqu'à » (up to) à l'écran : interdit pour le public « %s », ne montrer que des mesures réelles." % pub_key)
            elif j in ("valeur_typique", "a_eviter"):
                rep.warn(where, "« jusqu'à » (up to) à l'écran : pour le public « %s », montrer la valeur typique, et le maximum à l'oral avec sa condition." % pub_key)
            elif not has_source:
                rep.warn(where, "« jusqu'à » (up to) sans condition : préciser les conditions dans source.")
        sup_re = SUPERLATIFS_EN if langue == "en" else SUPERLATIFS_FR
        sups = sup_re.findall(screen)
        n3 = N3_RE.findall(screen)
        level = pub.get("superlatifs", "moderes")
        if sups or n3:
            bloc = text_of(s.get("bloc")) or "?"
            superlatifs_ecran.extend((bloc, x) for x in sups)
            if level in ("aucun", "sobres"):
                rep.warn(where, "Superlatif à l'écran (%s) : aucun pour le public « %s »." % (", ".join(sorted(set(sups + n3))), pub_key))
            elif n3 and not has_source:
                rep.warn(where, "Superlatif absolu (%s) sans preuve : il faut une source externe citée, sinon le retirer." % ", ".join(sorted(set(n3))))

        # Marqueurs [À FOURNIR] et consignes slide.a_fournir
        found = []
        for x in all_strings({k: v for k, v in s.items() if k not in ("image", "a_fournir")}):
            found.extend(MARKER_RE.findall(x))
        for x in as_list(s.get("a_fournir")):
            if text_of(x).strip():
                found.append("consigne : %s" % text_of(x).strip().rstrip(". "))
        if arch == "AF":
            att = text_of(t.get("attendu"))
            found.append("slide AF (%s ; préférer l'archétype prévu, avec des [À VALIDER] et des [À FOURNIR] courts)" % (
                att if len(att) <= 70 else att[:69].rstrip() + "…"))
        found = [x for k, x in enumerate(found) if x not in found[:k]]
        if found:
            msg = "Reste à fournir : %s." % " ; ".join(found)
            (rep.warn if brouillon else rep.err)(where, msg)
        # À l'écran, un [À FOURNIR] n'est qu'un libellé court ; la consigne va dans slide.a_fournir.
        a_l_ecran = [x for x in all_strings(t)] + ([text_of(s.get("source"))] if s.get("source") else [])
        for x in a_l_ecran:
            for m in FOURNIR_LABEL_RE.finditer(x):
                n = len(words(m.group(1)))
                if n > FOURNIR_MAX_WORDS:
                    rep.err(where, "Libellé [À FOURNIR] de %d mots à l'écran : « %s ». %d mots au plus ; "
                                   "la consigne complète va dans slide.a_fournir." % (n, m.group(0), FOURNIR_MAX_WORDS))

        for x in all_strings({k: v for k, v in s.items() if k not in ("image",)}):
            if NESTED_RE.search(x):
                rep.err(where, "Marqueurs imbriqués dans « %s » : écris-les côte à côte, "
                               "par exemple [À VALIDER : Disponible dès le] [À FOURNIR : date]." % x[:70])
                break
            if UNCLOSED_RE.search(x):
                rep.err(where, "Marqueur sans « ] » final dans « %s » : il s'afficherait tel quel." % re.sub(r"\s+", " ", x)[:70])
                break

        # Propositions [À VALIDER] : jamais un chiffre, un prix, une date, un témoignage, un logo, une source
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
                        rep.err(where, "[À VALIDER] « %s » contient %s (« %s ») : un chiffre, un prix, un pourcentage ou une "
                                       "date ne se propose pas. Mets [À FOURNIR : libellé] à la place." % (txt[:60], quoi, hit.group(0)))
                        break
        jamais = [("source", [s.get("source")], "une source")]
        if arch == "A17":
            jamais.append(("témoignage", [t.get("citation"), t.get("auteur")], "un témoignage"))
        if arch == "A16":
            jamais.append(("logos", as_list(t.get("logos")), "un logo"))
        if arch == "A19":
            jamais.append(("prix", [o.get("prix") for o in (as_list(t.get("offres")) or [t]) if isinstance(o, dict)], "un prix"))
        if arch == "A20":
            jamais.append(("date", [t.get("titre")], "une date"))
        if arch in ("A5", "A6", "A14") or t.get("chiffre"):
            jamais.append(("chiffre", [t.get("chiffre")] + [b.get(k) for b in as_list(t.get("barres")) + as_list(t.get("tuiles"))
                                                            if isinstance(b, dict) for k in ("chiffre", "etiquette")], "un chiffre"))
        for champ, vals, quoi in jamais:
            if any(VALIDER_RE.search(x) for v in vals for x in all_strings(v)):
                rep.err(where, "[À VALIDER] dans %s (%s) : cela ne se propose pas. Mets [À FOURNIR : libellé] à la place." % (champ, quoi))
        for txt in props:
            rep.a_valider.append((where, txt))

        # Notes
        segs = note_segments(s, default_speaker)
        if not segs:
            rep.err(where, "Notes vides : le script à dire manque.")
        for seg in segs:
            if seg["intervenant"] and people and seg["intervenant"] not in people:
                rep.err(where, "Intervenant « %s » inconnu (voir « intervenants »)." % seg["intervenant"])
        if s.get("intervenant") and people and s["intervenant"] not in people:
            rep.err(where, "slide.intervenant « %s » inconnu." % s["intervenant"])
        note_words = sum(len(speech_words(seg["texte"])) for seg in segs)
        total_parole += note_words

        # Durée
        d = s.get("duree_s")
        try:
            d = float(d)
            if d < 0:
                raise ValueError
        except (TypeError, ValueError):
            rep.err(where, "duree_s absente ou invalide (secondes).")
            d = 0.0
        total += d
        if d > 0 and note_words and note_words / (d / 60.0) > SPEECH_WPM_MAX:
            rep.warn(where, "Script trop long pour %d s : %d mots, soit %d mots/min (%d au plus)." % (
                d, note_words, note_words / (d / 60.0), SPEECH_WPM_MAX))
        elif d == 0 and note_words > 5:
            rep.warn(where, "duree_s vaut 0 alors que le script compte %d mots." % note_words)

        # Registre (heuristique) : notes hors relais et hors citations, plus le texte à l'écran
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
                rep.warn(where, "Registre « vous » attendu, tutoiement trouvé : %s." % ", ".join(sorted(set(x.lower() for x in tu))))
            if registre == "tu" and vous:
                rep.warn(where, "Registre « tu » attendu, vouvoiement trouvé : %s (un « vous » pluriel peut être voulu)." % ", ".join(sorted(set(x.lower() for x in vous))))
            # Relais : registre entre intervenants (meta.registre_intervenants)
            relais = QUOTE_RE.sub(" ", unvalider(" ".join(seg["texte"] for seg in segs if seg.get("type") == "relais")))
            relais = TON_NOM_RE.sub(" ", relais)
            if reg_i == "vous" and TU_RE.search(relais):
                rep.warn(where, "Relais tutoyé alors que les intervenants se vouvoient (meta.registre_intervenants = vous).")
            if reg_i == "tu" and re.search(r"(?<![\w’'])(?<!merci )(?:à vous|je vous (?:rends|repasse|passe|laisse))\b", relais, re.I):
                rep.warn(where, "Relais vouvoyé alors que les intervenants se tutoient (meta.registre_intervenants = tu).")

    # --- bilan global -------------------------------------------------------
    if langue == "fr" and registre == "vous" and tu_total > vous_total:
        rep.err("registre", "Le script tutoie plus qu'il ne vouvoie (%d contre %d) alors que le registre est « vous »." % (tu_total, vous_total))
    if langue == "fr" and registre == "tu" and vous_total > tu_total:
        rep.err("registre", "Le script vouvoie plus qu'il ne tutoie (%d contre %d) alors que le registre est « tu »." % (vous_total, tu_total))
    if langue == "en":
        rep.info("registre", "Présentation en anglais : contrôle tu/vous sans objet.")
    # Débit du script sur la durée visée : il doit se lire en entier, à voix haute, vers 140 mots par minute.
    if cible > 0 and total_parole:
        debit = total_parole / cible
        msg = "Script de %d mots pour %g min, soit %d mots/min (%d visés, %d à %d acceptés ; mots à dire, hors [À FOURNIR] et indications)." % (
            total_parole, cible, debit, SPEECH_WPM_CIBLE, SPEECH_WPM_MIN, SPEECH_WPM_MAX)
        if debit < SPEECH_WPM_MIN:
            rep.warn("script", msg + " Trop court : il manque environ %d mots, ou la durée visée est trop longue." % (
                SPEECH_WPM_CIBLE * cible - total_parole))
        elif debit > SPEECH_WPM_MAX:
            rep.warn("script", msg + " Trop long : environ %d mots de trop pour être dit sans courir." % (
                total_parole - SPEECH_WPM_CIBLE * cible))
        else:
            rep.info("script", msg)
    # Fond : on reste sur le même fond, et on n'en change qu'entre deux blocs.
    for (w1, f1, b1), (w2, f2, b2) in zip(fonds, fonds[1:]):
        if {f1, f2} == {"sombre", "clair"} and (b1 == b2 or not b1 or not b2):
            rep.warn(w2, "Fond %s juste après une slide %s du même bloc : garde le fond du deck, "
                         "et ne change de fond qu'entre deux blocs." % (f2, "claire" if f1 == "clair" else f1))
    # Rythme : pas trois fois de suite la même composition ; un moment visuel par bloc.
    for k in range(2, len(sequence)):
        (w0, a0, v0), (w1, a1, v1), (w2, a2, v2) = sequence[k - 2], sequence[k - 1], sequence[k]
        if a2 and a2 in archetypes and (a0, v0) == (a1, v1) == (a2, v2):
            nom_v = v2.split("/", 1)[1] if "/" in v2 else ""
            rep.warn(w2, "Trois slides de suite en %s, %s : change de composition ou de variante (designs.md, « Choisir un design »)." % (
                a2, "variante %s" % nom_v if nom_v else "sans variante"))
    for nom, b in blocs.items():
        if b["n"] >= 2 and not b["moment"]:
            rep.warn("bloc « %s »" % nom, "Aucun moment visuel (A5, A9, A10, A13, A14, A18 ou variante à image) sur %d slides : "
                                          "prévois-en un (designs.md, « Choisir un design »)." % b["n"])
    if pub.get("superlatifs") == "moderes":
        par_bloc = {}
        for bloc, _ in superlatifs_ecran:
            par_bloc[bloc] = par_bloc.get(bloc, 0) + 1
        for bloc, n in sorted(par_bloc.items()):
            if n > 1:
                rep.warn("ton", "Bloc « %s » : %d superlatifs à l'écran, un seul par bloc pour ce public." % (bloc, n))
    fourchette = pub.get("duree_min_conseillee")
    if cible > 0 and isinstance(fourchette, list) and len(fourchette) == 2 and not fourchette[0] <= cible <= fourchette[1]:
        rep.warn("durée", "Durée cible %g min hors de la fourchette conseillée pour ce public (%s à %s min)." % (cible, fourchette[0], fourchette[1]))
    if cible > 0:
        ecart = (total - cible * 60) / (cible * 60)
        msg = "Durée totale %d min %02d s pour %g min visées (%+.0f %%)." % (total // 60, total % 60, cible, ecart * 100)
        if abs(ecart) > DUREE_TOLERANCE:
            rep.err("durée", msg + " Écart de plus de 15 % : ajuster les durées ou le contenu.")
        else:
            rep.info("durée", msg)
    rep.info("public", "Public « %s » : source %s, affichage %s, graphiques %s, concurrents %s, « jusqu'à » %s, superlatifs %s, slide de prix %s, registre suggéré %s." % (
        pub_key, pub.get("source_chiffre", "?"), meta.get("affichage_source") or pub.get("affichage_source", "sous_le_chiffre"),
        pub.get("graduation", "?"), pub.get("concurrent", "?"), pub.get("jusqua", "?"), pub.get("superlatifs", "?"),
        pub.get("slide_prix", "?"), pub.get("registre_suggere", "?")))
    return rep


def main(argv=None):
    ap = argparse.ArgumentParser(description="Contrôle un deck.json avant le rendu.")
    ap.add_argument("deck")
    ap.add_argument("--brouillon", action="store_true", help="les [À FOURNIR] deviennent des avertissements")
    ap.add_argument("--json", action="store_true", help="sortie JSON")
    a = ap.parse_args(argv)
    try:
        with open(a.deck, encoding="utf-8") as f:
            deck = json.load(f)
    except OSError as e:
        print("Fichier illisible : %s" % e, file=sys.stderr)
        return 2
    except ValueError as e:
        print("JSON invalide : %s" % e, file=sys.stderr)
        return 2
    rep = check(deck, os.path.dirname(os.path.abspath(a.deck)), brouillon=a.brouillon)
    if a.json:
        out = {k: [{"ou": w, "message": m} for w, m in getattr(rep, k)] for k in ("erreurs", "avertissements", "infos")}
        out["a_valider"] = [{"ou": w, "texte": m} for w, m in rep.a_valider]
        print(json.dumps(out, ensure_ascii=False, indent=2))
    else:
        n = len(deck.get("slides") or []) if isinstance(deck, dict) else 0
        print("check_deck : %s (%d slides)" % (os.path.basename(a.deck), n))
        for title, items in (("ERREURS BLOQUANTES", rep.erreurs), ("AVERTISSEMENTS", rep.avertissements),
                             ("À VALIDER : propositions à faire valider à la livraison", rep.a_valider), ("INFOS", rep.infos)):
            if items:
                print("\n%s (%d)" % (title, len(items)))
                for w, m in items:
                    print("  [%s] %s" % (w, m))
        print("\nRésultat : %d erreur(s) bloquante(s), %d avertissement(s), %d proposition(s) à valider." % (
            len(rep.erreurs), len(rep.avertissements), len(rep.a_valider)))
    return 1 if rep.erreurs else 0


if __name__ == "__main__":
    sys.exit(main())
