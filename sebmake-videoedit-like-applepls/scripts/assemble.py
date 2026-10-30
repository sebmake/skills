#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""assemble.py: rushes.json (+ family, duration, music) → montage.json, a timeline that follows the measured targets.

Usage:
    python3 assemble.py rushes.json --famille produit [--schema revelation_tardive] [--duree 32]
                        [--musique musique.wav] [--fps 25] [--sortie montage.json] [--tc-debut 00:00:00:00]
    python3 assemble.py rushes.json --famille documentaire --schema pose
    python3 assemble.py --musique musique.wav --reperes           (only the cue points measured in the music)

Families and schemas: see ../references/montage-spec.md § 2.6. The targets come from gabarits.json.

What the script does, in order:
  1. reads the footage (duration and frame rate from ffprobe if missing);
  2. measures the music if there is one: sound start, peak, sharp attacks (§ 3 below);
  3. places the family's main cue points (black, hook, reveal, name, peak, landing…) where they were observed,
     and snaps those that allow it to a music attack (± 0.6 s, convention);
  4. fills each section with takes chosen by shot size, subject, role, movement
     and rating, without repeating a clip while others remain;
  5. measures the resulting timeline against the targets ("controle" block) and writes what it decided ("journal").

§ 3. Music measurement (standard library, ffmpeg to decode): energy in 20 ms slices;
  sound start = first slice less than 40 dB below the maximum; peak = maximum of the energy smoothed over 2 s;
  attack = a rise of at least 6 dB over 100 ms, local maximum within ± 140 ms. Thresholds: convention.

Output: montage.json and, on standard output, the timeline table to show before exporting.
Exit codes: 0 success; 1 input error; 2 timeline produced with deviations (see journal).
"""
import argparse
import array
import json
import math
import os
import re
import shlex
import subprocess
import sys
import unicodedata
from fractions import Fraction

ICI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ICI)
from commun import (chemin_absolu, ecrire_json, fps_affiche, fps_fraction, i2s, lire_json, s2i,  # noqa: E402
                    sonder, timebase, verifier_montage)

# ---------------------------------------------------------------- vocabulary

ALIAS_VALEUR = {"tg": "detail", "tgp": "detail", "macro": "detail", "1": "detail", "d": "detail",
                "g": "serre", "gp": "serre", "s": "serre", "2": "serre", "gros": "serre",
                "r": "rapproche", "tres_gros": "detail", "ensemble": "large", "m": "moyen", "pm": "moyen", "3": "entier",
                "l": "large", "4": "large", "pe": "large", "a": "abstrait"}
VALEURS = ["detail", "serre", "rapproche", "moyen", "entier", "large", "abstrait"]
SUJETS = ["objet", "piece", "matiere", "decor", "lumiere", "geste", "ecran", "personne", "entretien", "illustration",
          "oeuvre", "photo", "archive"]
FPS_ADMIS = [Fraction(24000, 1001), Fraction(24), Fraction(25), Fraction(30000, 1001), Fraction(30), Fraction(50),
             Fraction(60000, 1001), Fraction(60)]
FIXE = 10.0  # movement per second below which a shot is static (the corpus reading convention, the same as the review's)


def mot_code(x):
    """"Pièce", "décor", "œuvre", "très gros" → piece, decor, oeuvre, tres_gros: values are written without accents."""
    if x is None:
        return None
    s = str(x).strip().lower().replace("œ", "oe").replace("æ", "ae")
    s = "".join(c for c in unicodedata.normalize("NFKD", s) if not unicodedata.combining(c))
    return re.sub(r"[\s\-]+", "_", s) or None
RANG = {"detail": 1, "serre": 2, "abstrait": 2, "rapproche": 3, "moyen": 4, "entier": 5, "large": 6}
SERRES = {"detail", "serre"}
FAMILLES = {
    "produit": ["revelation_tardive", "objet_des_le_debut"],
    "ouverture": ["ouverture", "transition_decor", "cloture"],
    "documentaire": ["pose", "choral"],
    "bande_annonce": ["catalogue_blocs", "catalogue_mele", "oeuvre", "usage"],
}


ALIAS_FAMILLE = {"produit_revelation": "produit", "revelation": "produit", "ouverture_ambiance": "ouverture",
                 "documentaire_temoignage": "documentaire", "temoignage": "documentaire", "bandeannonce": "bande_annonce",
                 "bande_annonce_usage": "bande_annonce", "usage": "bande_annonce", "sketch": "ouverture", "cloture": "ouverture"}


ALIAS_SCHEMA = {"tardif": "revelation_tardive", "des_le_debut": "objet_des_le_debut", "catalogue_par_blocs": "catalogue_blocs",
                "sketch": "ouverture", "hommage": "cloture"}


def pour_la_critique(famille, schema, rushes):
    """critique_montage.py arguments that match this edit (same families, other names)."""
    ecran = any(r.sujet == "ecran" for r in rushes)
    if famille == "produit":
        if schema == "revelation_tardive":
            return {"famille": "produit", "sous_famille": "logiciel" if ecran else "revelation_objet", "schema": "tardif"}
        return {"famille": "produit", "sous_famille": "logiciel" if ecran else "usage_gamme", "schema": "des_le_debut"}
    if famille == "bande_annonce":
        return {"famille": "bandeannonce", "sous_famille": "catalogue_par_blocs" if schema == "catalogue_blocs" else schema}
    return {"famille": famille, "sous_famille": schema}


def borne(x, lo, hi):
    return max(lo, min(hi, x))


def mediane(v):
    v = sorted(v)
    if not v:
        return None
    n = len(v)
    return v[n // 2] if n % 2 else (v[n // 2 - 1] + v[n // 2]) / 2.0


def g_v(e, defaut=None):
    """Chosen value of a template entry."""
    if isinstance(e, dict):
        return e.get("v", defaut)
    return e if e is not None else defaut


# ---------------------------------------------------------------- music

def analyser_musique(chemin):
    sr, pas = 11000, 220  # 20 ms slices
    r = subprocess.run(["ffmpeg", "-v", "error", "-i", chemin, "-ac", "1", "-ar", str(sr), "-f", "s16le", "-"],
                       capture_output=True)
    if r.returncode != 0 or not r.stdout:
        raise RuntimeError("unreadable music: %s" % chemin)
    a = array.array("h")
    a.frombytes(r.stdout[: len(r.stdout) // 2 * 2])
    if sys.byteorder == "big":
        a.byteswap()
    n = len(a) // pas
    db = []
    for i in range(n):
        seg = a[i * pas:(i + 1) * pas]
        e = sum(x * x for x in seg) / float(pas)
        db.append(10 * math.log10(e + 1e-9) - 90.3)  # 0 dB = full scale
    duree = len(a) / float(sr)
    if not db:
        return {"duree_s": duree, "debut_son_s": 0.0, "fin_son_s": duree, "sommet_s": 0.0, "attaques": []}
    dmax = max(db)
    if dmax < -60:
        # nothing above −60 dB full scale: a silent file has no start, no peak and no attack
        return {"duree_s": round(duree, 3), "muette": True, "debut_son_s": None, "fin_son_s": None, "sommet_s": None,
                "attaques": []}
    seuil = dmax - 40
    debut = next((i for i, v in enumerate(db) if v > seuil), 0) * 0.02
    fin = (len(db) - next((i for i, v in enumerate(reversed(db)) if v > seuil), 0)) * 0.02
    # energy smoothed over 2 s (100 slices), linear
    lin = [10 ** (v / 10.0) for v in db]
    fen = 100
    cum = [0.0]
    for v in lin:
        cum.append(cum[-1] + v)
    lisse = [(cum[min(len(lin), i + fen // 2)] - cum[max(0, i - fen // 2)]) for i in range(len(lin))]
    sommet = max(range(len(lisse)), key=lambda i: lisse[i]) * 0.02
    # attacks: a rise of 6 dB or more over 100 ms, local maximum within ± 7 slices
    montee = [0.0] * len(db)
    for i in range(5, len(db)):
        montee[i] = db[i] - min(db[i - 5:i])
    attaques = []
    for i in range(5, len(db)):
        if montee[i] >= 6 and db[i] > seuil and montee[i] == max(montee[max(0, i - 7):i + 8]):
            attaques.append((round(i * 0.02, 2), round(montee[i], 1)))
    # keep one attack per 0.25 s (the strongest)
    garde = []
    for t, f in attaques:
        if garde and t - garde[-1][0] < 0.25:
            if f > garde[-1][1]:
                garde[-1] = (t, f)
        else:
            garde.append((t, f))
    return {"duree_s": round(duree, 3), "debut_son_s": round(debut, 2), "fin_son_s": round(fin, 2),
            "sommet_s": round(sommet, 2), "attaques": [{"t": t, "force_db": f} for t, f in garde]}


# ---------------------------------------------------------------- footage

class Rush:
    def __init__(self, d, base, marge):
        if not isinstance(d, dict) or d.get("id") in (None, ""):
            raise ValueError("a clip without \"id\": %s" % json.dumps(d, ensure_ascii=False)[:80])
        self.id = str(d["id"])
        self.chemin = chemin_absolu(d.get("chemin"), base)
        self.description = d.get("description", "")
        v = mot_code(d.get("valeur"))
        self.valeur = ALIAS_VALEUR.get(v, v) if v else None
        self.sujet = mot_code(d.get("sujet"))
        self.mouvement = mot_code(d.get("mouvement"))
        self.direction = mot_code(d.get("direction"))
        r = d.get("role") or []
        self.role = [mot_code(x) for x in ([r] if isinstance(r, str) else list(r))]
        # movement-per-second curve (analyse_rushes.py): measures the passage actually used, close to the review's measure
        self.courbe = d.get("_courbe") or None
        self.courbe_t = (d.get("_courbe_debut"), d.get("_courbe_fin"))
        try:
            self.note = float(d.get("note") or 3)
        except (TypeError, ValueError):
            raise ValueError("take %s: rating \"%s\": must be a number from 1 to 5" % (self.id, d.get("note")))
        self.meilleur = d.get("meilleur_s")
        self.personne = d.get("personne")
        self.fonction = d.get("fonction")
        self.bloc = d.get("bloc")
        self.titre_bloc = d.get("titre_bloc")
        self.scene = d.get("scene")
        self.synchro = d.get("synchro")
        self.son_image = bool(d.get("son_image", False))
        info = sonder(self.chemin) if self.chemin else {"fixe": False}
        self.absent = bool(info.get("absent"))
        self.fixe = bool(info.get("fixe"))
        self.duree = d.get("duree_s") or info.get("duree_s")
        self.fps = fps_fraction(d["fps"]) if d.get("fps") else info.get("fps")
        self.a_son = bool(info.get("audio"))
        if self.fixe:
            self.prises = [[0.0, 3600.0]]
        elif d.get("prises"):
            self.prises = [[float(a), float(b)] for a, b in d["prises"]]
        elif self.duree:
            m = marge if self.duree > 4 * marge + 0.5 else 0.0
            self.prises = [[m, float(self.duree) - m]]
        else:
            self.prises = []
        self.paroles = []
        for k, p in enumerate(d.get("paroles") or []):
            if not isinstance(p, dict):
                raise ValueError("take %s: speech line %d: expected an object {\"entree_s\", \"sortie_s\", \"texte\"}" % (self.id, k + 1))
            e, s = p.get("entree_s", p.get("entree")), p.get("sortie_s", p.get("sortie"))  # "entree", "sortie" accepted
            for cle, v in (("entree_s", e), ("sortie_s", s)):
                if v is None:
                    raise ValueError("take %s: speech line %d has no \"%s\"" % (self.id, k + 1, cle))
            try:
                e, s, note = float(e), float(s), float(p.get("note") or 3)
            except (TypeError, ValueError):
                raise ValueError("take %s: speech line %d: entree_s, sortie_s and note are numbers (decimal point)"
                                 % (self.id, k + 1))
            self.paroles.append({"entree_s": e, "sortie_s": s,
                                 "texte": p.get("texte"), "ordre": p.get("ordre"), "note": note,
                                 "chapitre": p.get("chapitre"), "role": p.get("role"), "k": k})
        self.utilise = []  # intervals already used [a, b] in source seconds

    def dispo_max(self):
        return max([b - a for a, b in self.prises] or [0.0])

    def mouvement_passage(self, a, b):
        """Movement per second between a and b (source s), read from the analysis curve; None without a curve.

        The curve sums gray-level differences in packets of 29 frames read at 29.97 fps (analyse_rushes.py):
        it is the review's measure (--mesurer-medias), brought down to the passage used in the edit."""
        t0, t1 = self.courbe_t
        if not self.courbe or t0 is None or b <= a:
            return None
        pas = 29 / (30000 / 1001.0)
        total = 0.0
        for k, v in enumerate(self.courbe):
            x0 = t0 + k * pas
            x1 = min(t0 + (k + 1) * pas, t1 if t1 is not None else x0 + pas)
            if x1 <= x0:
                continue
            recouvre = min(b, x1) - max(a, x0)
            if recouvre > 0:
                total += float(v) * recouvre / (x1 - x0)
        return total / (b - a)

    def __repr__(self):
        return "<%s %s/%s>" % (self.id, self.valeur, self.sujet)


# The analyse_rushes.py curve, brought down to the passage used, comes close to the review's measure without matching it
# (packets of 29 frames versus the shot's exact frames): a shot at 10.3 here can read 9.8 in the review. The check
# therefore counts any shot under 10.5 as static, so that an "ok" from assemble.py does not hide a review alert (convention).
FIXE_CONTROLE = FIXE + 0.5


def est_fixe(p):
    """Static shot for the check: movement measured on the used passage under 10.5 (a margin over the review's
    threshold of 10), otherwise the clip's label."""
    if p.get("mouvement_mesure") is not None:
        return p["mouvement_mesure"] < FIXE_CONTROLE
    return p.get("mouvement") == "fixe"


def categorie_mouvement(v):
    """Mean gray difference per second → fixe (< 10), lent (10-50), moyen (50-200), fort (≥ 200): corpus reading bounds."""
    if v is None:
        return None
    v = float(v)
    return "fixe" if v < 10 else "lent" if v < 50 else "moyen" if v < 200 else "fort"


CHAMPS_LIBRES = ("valeur", "sujet", "role", "note", "personne", "fonction", "paroles", "bloc", "titre_bloc", "scene",
                 "synchro", "meilleur_s", "direction", "son_image", "description")


def depuis_analyse(d, marge=0.0):
    """analyse_rushes.py output ("fichiers" → "prises") → list of clips: one detected take = one clip.

    Fields filled in by eye in the take (valeur, sujet, role, paroles…) are kept as they are."""
    out = []
    for f in d.get("fichiers", []):
        racine = os.path.splitext(f.get("nom") or os.path.basename(f["fichier"]))[0]
        for pr in f.get("prises", []):
            if pr.get("noir"):
                continue        # an all-black take is not a picture: the film's blacks are placed by the edit
            a, b = float(pr["debut"]), float(pr["fin"])
            fen = [[a, b]]
            for z in pr.get("a_eviter") or []:
                nouv = []
                for x, y in fen:
                    if z["fin"] <= x or z["debut"] >= y:
                        nouv.append([x, y])
                        continue
                    if z["debut"] - x >= 0.5:
                        nouv.append([x, z["debut"]])
                    if y - z["fin"] >= 0.5:
                        nouv.append([z["fin"], y])
                fen = nouv
            # conventional margin at both ends of each window (start, stop, the frame of the neighboring cut)
            fen = [[x + marge, y - marge] if y - x > 4 * marge + 0.5 else [x, y] for x, y in fen]
            r = {"id": "%s-%d" % (racine, pr.get("numero", len(out) + 1)), "chemin": f["fichier"], "prises": fen,
                 "mouvement": categorie_mouvement(pr.get("mouvement")) if not pr.get("fixe") else "fixe",
                 "description": "%s, take %s" % (f.get("nom"), pr.get("numero")),
                 "_courbe": pr.get("courbe_mouvement_par_s"), "_courbe_debut": a, "_courbe_fin": b}
            sens = ((pr.get("camera") or {}).get("sens") or "")
            if any(w in sens for w in ("left", "right", "gauche", "droite")):  # French: older rushes.json
                r["direction"] = "lateral"
            moments = pr.get("moments") or []
            if any(x.get("type") == "naissance_lumiere" for x in moments):
                r["role"] = ["accroche"]
            pics = [x for x in moments if x.get("type") == "pic_mouvement"]
            if pics:
                x = max(pics, key=lambda y: y.get("score") or 0)
                r["meilleur_s"] = (x["debut"] + x["fin"]) / 2.0
            for k in CHAMPS_LIBRES:
                if pr.get(k) is not None:
                    r[k] = pr[k]
            if pr.get("notes"):
                r["description"] += " — " + str(pr["notes"])
            out.append(r)
    return out


def charger_rushes(chemin, marge):
    """rushes.json written by hand ("rushes"), analyse_rushes.py output ("fichiers"), or both at once:
    a photo or an unanalyzed file goes into "rushes" next to the analyzed takes."""
    d = lire_json(chemin)
    base = os.path.dirname(os.path.abspath(chemin))
    if isinstance(d, dict) and "fichiers" in d:
        projet = {k: v for k, v in d.items() if k not in ("fichiers", "musiques", "lecture", "erreurs", "resume", "rushes",
                                                          "annotations_non_retrouvees")}
        if d.get("musiques"):
            projet["_musiques_analyse"] = [x["fichier"] for x in d["musiques"] if x.get("fichier")]
        rushes = [Rush(x, base, marge) for x in depuis_analyse(d, marge)]
        sans = sum(1 for r in rushes if not r.valeur or not r.sujet)
        if sans:
            projet.setdefault("_avertissements", []).append(
                "%d takes out of %d have no shot size or no subject: fill them in by eye in the file (contact sheet), otherwise shots are chosen blind"
                % (sans, len(rushes)))
        if d.get("annotations_non_retrouvees"):
            projet.setdefault("_avertissements", []).append(
                "%d annotated takes not found in the last analysis (\"annotations_non_retrouvees\"): carry them over by hand"
                % len(d["annotations_non_retrouvees"]))
        if d.get("rushes"):
            ajout = [Rush(x, base, marge) for x in d["rushes"]]
            projet.setdefault("_avertissements", []).append(
                "analyzed takes: %d; added by hand (\"rushes\"): %d; edited together" % (len(rushes), len(ajout)))
            rushes += ajout
    else:
        liste = d if isinstance(d, list) else d.get("rushes", [])
        projet = {} if isinstance(d, list) else d
        rushes = [Rush(x, base, marge) for x in liste]
    for r in rushes:
        if r.sujet and r.sujet not in SUJETS:
            projet.setdefault("_avertissements", []).append(
                "unknown subject: \"%s\", take %s; read as is, it counts for no rule (subjects: %s)"
                % (r.sujet, r.id, ", ".join(SUJETS)))
        if r.valeur and r.valeur not in VALEURS:
            projet.setdefault("_avertissements", []).append(
                "unknown shot size: \"%s\", take %s; read as is (sizes: %s)" % (r.valeur, r.id, ", ".join(VALEURS)))
    return projet, rushes, base


# ---------------------------------------------------------------- choosing takes

class Choix:
    def __init__(self, rushes, journal):
        self.rushes = rushes
        self.journal = journal
        self.compte = {r.id: 0 for r in rushes}
        self.precedent = None
        self._dit = set()

    def _dire(self, cle, message):
        """One journal line per situation, not one per shot."""
        if cle not in self._dit:
            self._dit.add(cle)
            self.journal.append(message)

    @staticmethod
    def _accepte(r, veut):
        ex = veut.get("exiger") or {}
        if ex.get("sujets") and r.sujet not in ex["sujets"]:
            return False
        if ex.get("valeurs") and r.valeur not in ex["valeurs"]:
            return False
        if ex.get("personne") and r.personne != ex["personne"]:
            return False
        if ex.get("bloc") is not None and r.bloc != ex["bloc"]:
            return False
        if ex.get("scene") is not None and r.scene != ex["scene"]:
            return False
        for cond in veut.get("exclure") or []:
            if all(Choix._colle(r, k, v) for k, v in cond.items()):
                return False
        if veut.get("sans_fixe") and r.mouvement == "fixe":
            return False
        return True

    @staticmethod
    def _colle(r, k, v):
        val = getattr(r, k)
        vs = v if isinstance(v, (list, tuple, set)) else [v]
        if isinstance(val, list):
            return bool(set(val) & set(vs))
        return val in vs

    def _score(self, r, veut):
        s = 0.0
        if veut.get("roles") and set(veut["roles"]) & set(r.role):
            s += 5
        if veut.get("sujets") and r.sujet in veut["sujets"]:
            s += 3
        if veut.get("valeurs") and r.valeur in veut["valeurs"]:
            s += 2 + (0.5 if r.valeur == veut["valeurs"][0] else 0)
        if veut.get("mouvements") and r.mouvement in veut["mouvements"]:
            s += 1
        if veut.get("directions") and r.direction in veut["directions"]:
            s += 1.5
        if veut.get("personne") and r.personne == veut["personne"]:
            s += 3
        if veut.get("bloc") is not None and r.bloc == veut["bloc"]:
            s += 4
        s += 0.3 * (r.note - 3)
        s -= 2.5 * self.compte[r.id]
        if self.precedent is not None and r.id == self.precedent:
            s -= 10
        if r.role and not (set(veut.get("roles") or []) & set(r.role)) and set(r.role) & {"revelation", "fin", "gamme", "bouton", "signature"}:
            s -= 4  # keep reserved shots for their place
        return s

    def _fenetre(self, r, duree, avant, apres, libre):
        """In point (s) for a given duration, or None. libre=True: only a place that overlaps no
        picture already used; libre=False: the best place, even if already used."""
        if r.fixe:
            # a still image: always the same picture, taken from its start; once used, it is no longer free
            return None if (libre and r.utilise) else 0.0
        besoin = duree + avant + apres
        for a, b in r.prises:
            if b - a < besoin - 1e-6:
                continue
            if r.meilleur is not None and a + avant <= r.meilleur <= b - apres:
                e = borne(r.meilleur - duree / 2.0, a + avant, b - apres - duree)
            else:
                e = a + avant  # the movement starts at the beginning of the take (pull back, rotation)
            if not libre:
                return e
            # look for a place that does not overlap a used one
            essais = [e] + [u[1] + 0.04 + avant for u in r.utilise]
            # the previous shot's clip, picked up where it stopped: a cut that would not show
            suite = r.utilise[-1] if (r.id == self.precedent and r.utilise) else None
            for e2 in essais:
                if e2 < a + avant - 1e-6 or e2 + duree + apres > b + 1e-6:
                    continue
                if suite and (abs(e2 - suite[1]) < 0.5 or abs(e2 + duree - suite[0]) < 0.5):
                    continue
                if all(e2 + duree <= u[0] or e2 >= u[1] for u in r.utilise):
                    return e2
        return None

    @staticmethod
    def _dire_exigence(ex):
        return "; ".join("%s %s" % (k, "/".join(str(x) for x in v) if isinstance(v, (list, tuple)) else v)
                         for k, v in sorted(ex.items()))

    def choisir(self, veut, duree, avant=0.0, apres=0.0, temps=None):
        """Returns (clip, in_s, duration_s); the duration may be shortened if no clip is long enough.

        A free place in any suitable clip comes before pictures already used;
        each fallback (requirement dropped, pictures replayed) is written to the journal."""
        quand = " (section \"%s\")" % temps if temps else ""
        cands = [r for r in self.rushes if not r.absent and r.prises and self._accepte(r, veut)]
        if not cands and veut.get("exiger") and veut.get("repli", True):
            veut2 = {k: v for k, v in veut.items() if k not in ("exiger",)}
            cands = [r for r in self.rushes if not r.absent and r.prises and self._accepte(r, veut2)]
            if cands:
                ex = self._dire_exigence(veut["exiger"])
                self._dire(("exiger", temps, ex), "requirement \"%s\" dropped%s: no clip meets it, shot taken without it"
                           % (ex, quand))
        if not cands:
            return None
        # the same still image twice in a row would make an invisible cut: never
        meilleurs = [r for r in sorted(cands, key=lambda r: -self._score(r, veut))
                     if not (r.fixe and r.id == self.precedent)]
        if not meilleurs:
            return None
        for libre in (True, False):
            for r in meilleurs:
                e = self._fenetre(r, duree, avant, apres, libre)
                if e is not None:
                    if not libre:
                        self._signaler_reprise(r, e, duree, quand)
                    return self._prendre(r, e, duree)
        # none long enough: the longest available, shortened
        r = max(meilleurs[:4], key=lambda x: (x.dispo_max(), self._score(x, veut)))
        d = r.dispo_max() - avant - apres
        if d <= 0.2:
            return None
        a, b = max(r.prises, key=lambda w: w[1] - w[0])
        self._signaler_reprise(r, a + avant, d, quand)
        return self._prendre(r, a + avant, d)

    def _signaler_reprise(self, r, e, d, quand):
        if r.fixe:
            if r.utilise:
                self.journal.append("%s (still image) used %d times%s: no other suitable clip has a free place "
                                    "long enough (more footage needed)" % (r.id, len(r.utilise) + 1, quand))
            return
        deja = [u for u in r.utilise if e < u[1] and e + d > u[0]]
        if deja:
            commun = sum(min(e + d, u[1]) - max(e, u[0]) for u in deja)
            self.journal.append("%s %.2f → %.2f s replays %.2f s of pictures already used%s: no other suitable clip has "
                                "a free place long enough (more footage needed)" % (r.id, e, e + d, commun, quand))

    def _prendre(self, r, e, d):
        r.utilise.append([e, e + d])
        self.compte[r.id] += 1
        self.precedent = r.id
        return r, e, d


# ---------------------------------------------------------------- timeline

def texte_carton(texte, deuxieme_ligne=None):
    """The text of a marker or of a list to place by hand: "Lou Martin · designer" for a two-line lower third."""
    return " · ".join(x for x in (texte, deuxieme_ligne) if x)


class Timeline:
    def __init__(self, fps, journal):
        self.fps = fps
        self.t = 0  # frames
        self.plans = []
        self.paroles = []
        self.marqueurs = []
        self.journal = journal
        self._temps = None

    def img(self, s):
        return s2i(s, self.fps)

    def _ajouter(self, p, fin_img, temps):
        d = fin_img - self.t
        if d <= 0:
            return None
        p["n"] = len(self.plans) + 1
        p["temps"] = temps
        p["debut_img"] = self.t
        p["duree_img"] = d
        p["debut_s"] = round(i2s(self.t, self.fps), 3)
        p["duree_s"] = round(i2s(d, self.fps), 3)
        p.setdefault("transition", {"type": "coupe"})
        p.setdefault("carton", None)
        if temps != self._temps:
            self.marqueurs.append({"debut_img": self.t, "duree_img": 0, "nom": temps, "texte": ""})
            self._temps = temps
        self.plans.append(p)
        self.t = fin_img
        return p

    def noir(self, fin_s, temps, transition=None, notes=""):
        return self._ajouter({"type": "noir", "transition": transition or {"type": "coupe"}, "notes": notes},
                             self.img(fin_s), temps)

    def carton(self, fin_s, temps, texte, role, fond="noir", taille=4.5, place="centre", transition=None,
               notes="", deuxieme_ligne=None, logo=None):
        p = self._ajouter({"type": "carton", "transition": transition or {"type": "coupe"}, "notes": notes},
                          self.img(fin_s), temps)
        if p:
            p["carton"] = {"role": role, "texte": texte, "debut_img": 0, "duree_img": p["duree_img"], "place": place,
                           "taille_pct": taille, "fond": fond}
            if deuxieme_ligne:
                p["carton"]["deuxieme_ligne"] = deuxieme_ligne
            if logo:
                p["carton"]["logo"] = logo
            self.marqueurs.append({"debut_img": p["debut_img"], "duree_img": p["duree_img"], "nom": "title card " + role,
                                   "texte": texte_carton(texte, deuxieme_ligne) or (logo and os.path.basename(logo)) or ""})
        return p

    def image(self, rush, entree_s, fin_s, temps, transition=None, notes="", sync=False):
        fin_img = self.img(fin_s)
        d = fin_img - self.t
        if d <= 0:
            return None
        e = self.img(entree_s)
        p = {"type": "image", "source": rush.id, "chemin": rush.chemin, "entree_img": e, "sortie_img": e + d,
             "entree_s": round(i2s(e, self.fps), 3), "sortie_s": round(i2s(e + d, self.fps), 3),
             "transition": transition or {"type": "coupe"}, "valeur": rush.valeur, "sujet": rush.sujet,
             "mouvement": rush.mouvement, "son_image": rush.son_image, "personne": rush.personne, "notes": notes}
        if sync:
            p["sync"] = True
        return self._ajouter(p, fin_img, temps)

    def parole(self, rush, entree_s, debut_s, duree_s, personne=None, texte=None):
        d = self.img(debut_s + duree_s) - self.img(debut_s)
        e = self.img(entree_s)
        q = {"n": len(self.paroles) + 1, "source": rush.id, "chemin": rush.chemin, "debut_img": self.img(debut_s),
             "duree_img": d, "entree_img": e, "sortie_img": e + d, "debut_s": round(debut_s, 3),
             "duree_s": round(i2s(d, self.fps), 3), "entree_s": round(i2s(e, self.fps), 3), "personne": personne,
             "texte": texte, "piste": "A1"}
        self.paroles.append(q)
        return q

    def poser_carton(self, plan, texte, role, debut_s, duree_s, place, taille, fond="image", deuxieme_ligne=None,
                     logo=None):
        """A text over a picture shot (track V2)."""
        if plan is None:
            return None
        deb = borne(self.img(debut_s), 0, plan["duree_img"] - 1)
        dur = borne(self.img(duree_s), 1, plan["duree_img"] - deb)
        plan["carton"] = {"role": role, "texte": texte, "debut_img": deb, "duree_img": dur, "place": place,
                          "taille_pct": taille, "fond": fond}
        if deuxieme_ligne:
            plan["carton"]["deuxieme_ligne"] = deuxieme_ligne
        if logo:
            plan["carton"]["logo"] = logo
        self.marqueurs.append({"debut_img": plan["debut_img"] + deb, "duree_img": dur, "nom": "title card " + role,
                               "texte": texte_carton(texte, deuxieme_ligne)})
        return plan["carton"]


# ---------------------------------------------------------------- assembler

class Assembleur:
    def __init__(self, args, gab, projet, rushes, base):
        self.args = args
        self.G = gab
        self.projet = projet
        self.rushes = rushes
        self.base = base
        self.journal = []
        self.famille = args.famille
        self.schema = args.schema
        fps = args.fps or projet.get("fps")
        choisie = bool(fps)
        if not fps:
            cad = [r.fps for r in rushes if r.fps]
            fps = max(set(cad), key=cad.count) if cad else 25
            if not cad:
                self.journal.append("no frame rate read from the footage: 25 fps (convention)")
        self.fps = fps_fraction(fps)
        fichiers = {}
        for r in rushes:
            if r.fps:
                fichiers.setdefault(fps_fraction(r.fps), set()).add(r.chemin)
        if len(fichiers) > 1:
            def _f(x):
                return str(fps_affiche(x))
            self.journal.append(
                "mixed frame rates: %s; timeline at %s fps (%s); clips at another rate will be converted by "
                "the software, check this on import (logiciels.md § 5)%s"
                % (", ".join("%d file(s) at %s" % (len(v), _f(k)) for k, v in sorted(fichiers.items(), key=lambda kv: -len(kv[1]))),
                   _f(self.fps), "chosen" if choisie else "the rate of most takes",
                   "" if choisie else "; use --fps to choose another"))
        self.tl = Timeline(self.fps, self.journal)
        self.choix = Choix(rushes, self.journal)
        self.var = g_v(gab["communs"]["variation_durees"])
        self.tol = g_v(gab["communs"]["tolerance_musique_s"])
        self.musique = None
        self.reperes = None
        mus = args.musique or projet.get("musique")
        if args.musique in ("aucune", "none"):
            mus = None
        elif not mus and projet.get("_musiques_analyse"):
            sons = projet["_musiques_analyse"]
            if len(sons) == 1:
                mus = sons[0]
                self.journal.append("music: %s (the only sound file in the analysis); --musique aucune to do without it"
                                    % os.path.basename(mus))
            else:
                self.journal.append("%d sound files in the analysis (%s): none is taken by default; set --musique"
                                    % (len(sons), ", ".join(os.path.basename(x) for x in sons)))
        if mus:
            mus = chemin_absolu(mus, base if not args.musique else os.getcwd())
            try:
                self.reperes = analyser_musique(mus)
                self.musique = mus
                if self.reperes.get("muette"):
                    self.journal.append("the music supplied is silent (nothing above −60 dB): edit without music "
                                        "or cue points, timed on the picture")
                    self.reperes, self.musique = None, None
            except (RuntimeError, OSError) as e:
                self.journal.append("music unreadable or not found (%s): edit without music" % e)
        self.D = None
        self.nom = projet.get("nom")
        self.police = projet.get("police") or {"famille": None, "fichier": None}
        self.couleurs = projet.get("couleurs") or {"fond": "#000000", "texte": "#FFFFFF"}
        self.logo = chemin_absolu(projet.get("logo"), base) if projet.get("logo") else None
        self.controle = []

    # -- tools
    def log(self, *m):
        self.journal.append(" ".join(str(x) for x in m))

    def combler(self, fin_s, temps):
        """Black "for lack of pictures" up to fin_s, always reported in the journal."""
        t = i2s(self.tl.t, self.fps)
        if fin_s - t > 0:
            self.log("%s: %.2f s of pictures missing (%.2f → %.2f s), no clip long enough; black instead (more footage needed)"
                     % (temps, fin_s - t, t, fin_s))
        self.tl.noir(fin_s, temps, notes="for lack of pictures")

    def duree(self, cle_gab, defaut):
        if self.args.duree:
            return float(self.args.duree)
        e = cle_gab
        v, plage = g_v(e, defaut), e.get("plage") if isinstance(e, dict) else None
        if self.reperes:
            fin = self.reperes["fin_son_s"]
            if plage and plage[0] <= fin <= plage[1] * 1.15:
                self.log("duration taken from the music: the sound ends at %.1f s" % fin)
                return round(fin, 2)
            if plage and fin > plage[1] * 1.15:
                self.log("music of %.1f s, longer than the family (%s to %s s): film of %.1f s, music faded out"
                         % (fin, plage[0], plage[1], v))
        return float(v)

    def caler(self, t, lo=None, hi=None, nom=""):
        """Snaps a major change to the strongest attack within ± tolerance (convention)."""
        if not self.reperes:
            return t
        lo = -1e9 if lo is None else lo
        hi = 1e9 if hi is None else hi
        cands = [a for a in self.reperes["attaques"] if abs(a["t"] - t) <= self.tol and lo <= a["t"] <= hi]
        if not cands:
            return t
        a = max(cands, key=lambda x: (x["force_db"], -abs(x["t"] - t)))
        if nom and abs(a["t"] - t) * float(self.fps) >= 1:
            self.log("%s: snapped to a music attack, %.2f s → %.2f s" % (nom, t, a["t"]))
        return a["t"]

    def cible_tiers(self, tiers):
        D = self.D

        def f(t):
            k = 0 if t < D / 3.0 else (1 if t < 2 * D / 3.0 else 2)
            return tiers[k]
        return f

    def remplir(self, t1, temps, cible, plage, veut_fn, notes="", premier_trans=None):
        """Fills the timeline up to t1 (s) with picture shots. cible(t) → target duration; veut_fn(k, t) → criteria.

        The math is done in frames: each shot moves forward at least one frame, so the loop always ends."""
        k = 0
        lo, hi = plage
        fin_img = s2i(t1, self.fps)
        une = 1.0 / float(self.fps)
        while fin_img - self.tl.t > 0:
            t = i2s(self.tl.t, self.fps)
            reste = i2s(fin_img - self.tl.t, self.fps)
            c = borne(cible(t) * self.var[k % len(self.var)], lo, hi)
            if reste < c * 1.5 or reste - c < lo:
                c = reste
            pris = self.choix.choisir(veut_fn(k, t), c, temps=temps)
            if pris is None or pris[2] < une:
                self.log("%s: no clip fits at %.1f s; black instead" % (temps, t))
                self.tl.noir(t + max(c, une), temps, notes="for lack of a clip")
                k += 1
                continue
            r, e, d = pris
            fin = t + min(d, c)
            if s2i(fin, self.fps) <= self.tl.t:
                fin = t + une
            trans = premier_trans if (k == 0 and premier_trans) else None
            self.tl.image(r, e, fin, temps, transition=trans, notes=notes)
            k += 1

    # -- placing the music
    def poser_musique(self):
        if not self.musique:
            return None
        D_img = self.tl.t
        mus_img = s2i(self.reperes["duree_s"], self.fps)
        d = min(D_img, mus_img)
        fondu = 0
        if mus_img > D_img:
            fondu = s2i(g_v(self.G["communs"]["fondu_sortie_musique_s"]), self.fps)
        elif mus_img < D_img - s2i(1.0, self.fps):
            self.log("the music (%.1f s) ends before the film (%.1f s)" % (self.reperes["duree_s"], i2s(D_img, self.fps)))
        niveau = -12.0 if self.tl.paroles else 0.0
        if self.tl.paroles:
            self.log("music at −12 dB under the voices (convention: low enough for a clear voice); raise it by hand in the pauses")
        return {"chemin": self.musique, "debut_img": 0, "entree_img": 0, "duree_img": d, "fondu_sortie_img": fondu,
                "niveau_db": niveau, "piste": "A2",
                "reperes": {"debut_son_s": self.reperes["debut_son_s"], "fin_son_s": self.reperes["fin_son_s"],
                            "sommet_s": self.reperes["sommet_s"],
                            "attaques_s": [a["t"] for a in self.reperes["attaques"]][:60]}}

    # ============================================================ PRODUCT
    def produit(self):
        g = self.G["produit"]
        D = self.D = self.duree(g["duree_s"], 32.0)
        if not (g["duree_s"]["plage"][0] <= D <= g["duree_s"]["plage"][1]):
            self.log("duration %.1f s outside the observed range (24 to 51 s, 13 films without voice)" % D)
        schema = self.schema
        logiciel = any(r.sujet == "ecran" for r in self.rushes)
        taille_nom = g["nom_taille_pct"]["logiciel" if logiciel else "objet"]
        noir0 = g_v(g["noir_ouverture_s"])
        if self.reperes:
            noir0 = self.caler(noir0, 0.33, 1.6, "fade up from black")
        fin_noir = g_v(g["noir_final_s"])
        nom_dur = g_v(g["nom_duree_s"]) if self.nom else 0.0
        nom_start = D - fin_noir - nom_dur
        if self.nom and self.reperes:
            ns = self.caler(nom_start, 0.83 * D, 0.96 * D, "name")
            nom_dur = borne(D - fin_noir - ns, 1.27, 4.5)
            fin_noir = borne(D - ns - nom_dur, 0.1, 2.81)
            nom_start = D - fin_noir - nom_dur
        if not self.nom:
            self.log("no name supplied: with no speaker after the film, the skill always writes the name (convention); please supply it")
        exclure_entier = [{"valeur": "entier", "sujet": ["objet", "ecran", None]}]
        reserve = [{"role": ["revelation"]}]
        motif = [["detail", "serre"], ["serre", "detail"], ["large", "abstrait", "moyen"]]

        def veut_montee(k, t):
            vals = motif[k % 3]
            return {"valeurs": vals, "sujets": ["piece", "matiere", "geste", "decor", "lumiere", "ecran"],
                    "exclure": exclure_entier + reserve if schema == "revelation_tardive" else reserve}

        # 1. black, then the picture appears
        self.tl.noir(noir0, "ouverture", notes="opening black: 13 films out of 16, median 1.1 s (observed)")
        fondu = {"type": "fondu", "duree": g_v(g["fondu_depuis_noir_s"])}
        q1, q3 = g_v(g["plan_quartiles_s"])
        tiers = [g_v(g["plan_debut_s"]), g_v(g["plan_milieu_s"]), g_v(g["plan_debut_s"])]
        if schema == "revelation_tardive":
            # 2. hook: a world or a material, never the whole object
            acc = borne(g_v(g["premier_plan_s"]), *g["premier_plan_s"]["plage"])
            pris = self.choix.choisir({"roles": ["accroche"], "sujets": ["decor", "matiere", "lumiere"],
                                       "valeurs": ["large", "detail", "abstrait"], "exclure": exclure_entier + reserve},
                                      acc)
            if pris:
                r, e, d = pris
                self.tl.image(r, e, noir0 + d, "accroche", transition=fondu,
                              notes="hook: a setting or a material, never the whole object (observed 10 out of 10); the picture fades up from black (8 out of 16)")
            # 3. reveal: place and duration
            un = 2.0 / float(self.fps)  # a two-frame margin to stay within the range after rounding
            lo = max(0.69 * D + un, nom_start - g["revelation_tenu_s"]["plage"][1])
            hi = min(0.82 * D - un, nom_start - g["revelation_tenu_s"]["plage"][0])
            if lo > hi:
                rev_start = min(0.82 * D, nom_start - 4.89)
                self.log("film too short to hold the reveal 4.9 s between 69 and 82 %%: reveal at %.0f %%" % (100 * rev_start / D))
            else:
                # between the median place (77 %) and the median hold (8 s), brought back into the observed range
                cand = (borne(nom_start - g_v(g["revelation_tenu_s"]), lo, hi) + borne(g_v(g["revelation_place"]) * D, lo, hi)) / 2.0
                rev_start = self.caler(cand, lo, hi, "reveal") if self.reperes else cand
            # 4. peak: 5 shots of 1.17 s in the first half, before the reveal
            pic = g["pic"]
            n_pic, d_pic = pic["n"], pic["v"]
            t_acc = i2s(self.tl.t, self.fps)
            pic_start = max(t_acc + q1, min(pic["place"] * D, 0.5 * D - n_pic * d_pic))
            if pic_start + n_pic * d_pic > rev_start - q1:
                n_pic = max(0, int((rev_start - q1 - pic_start) / d_pic))
                self.log("peak cut down to %d shots for lack of room before the reveal" % n_pic)
            if self.reperes and n_pic:
                pic_start = self.caler(pic_start, t_acc + q1, 0.5 * D - n_pic * d_pic, "peak")
            # 5. build-up before the peak
            self.remplir(pic_start, "montee", self.cible_tiers(tiers), (q1, q3), veut_montee,
                         notes="build-up: tighten on details (65 to 70 % tight shots, observed); match on movement to check by eye (12 out of 16)")
            # 6. peak
            for k in range(n_pic):
                t = i2s(self.tl.t, self.fps)
                pr = self.choix.choisir({"mouvements": ["fort", "moyen"], "valeurs": ["detail", "serre"],
                                         "exclure": exclure_entier + reserve}, d_pic)
                if pr:
                    r, e, d = pr
                    self.tl.image(r, e, t + min(d, d_pic), "pic",
                                  notes="fast passage: 5 shots of 1.17 s, first half (8 out of 11)")
            # 7. build-up after the peak
            self.remplir(rev_start, "montee", self.cible_tiers(tiers), (q1, q3), veut_montee,
                         notes="build-up: details, parts, gestures; never the whole object before the reveal")
            # 8. reveal and end
            rev_start = i2s(self.tl.t, self.fps)
            tenu = nom_start - rev_start
            d_rev = min(tenu, g["revelation_tenu_s"]["plage"][1])
            # the reveal requires the whole object: without it, no fallback to another shot (it would not be a reveal)
            pr = self.choix.choisir({"roles": ["revelation"], "sujets": ["objet", "ecran"], "valeurs": ["entier"],
                                     "directions": ["recul", "rotation"], "exiger": {"valeurs": ["entier"]}, "repli": False},
                                    d_rev, temps="revelation")
            if pr is None:
                self.log("no shot of the whole object (size \"entier\"): the reveal is missing; shoot a clip of the whole object, "
                         "or mark a take \"entier\" in rushes.json if it shows it")
            else:
                r, e, d = pr
                self.tl.image(r, e, rev_start + d, "revelation",
                              notes="reveal: the whole object, alone, held; between 69 and 82 % (median 77 %, 10 films); pulling back in 5 out of 10")
            if nom_start - i2s(self.tl.t, self.fps) > 0.5:
                pr = self.choix.choisir({"roles": ["fin", "gamme"], "sujets": ["objet", "ecran"], "valeurs": ["entier", "large"],
                                         "exiger": {"valeurs": ["entier", "large"]}}, nom_start - i2s(self.tl.t, self.fps),
                                        temps="fin")
                if pr:
                    r, e, d = pr
                    self.tl.image(r, e, i2s(self.tl.t, self.fps) + d, "fin",
                                  notes="last picture shot: the whole object (13 out of 16)")
        else:
            # object from the start
            premier = borne(g_v(g["premier_plan_s"]), *g["premier_plan_s"]["plage"])
            pr = self.choix.choisir({"roles": ["accroche", "revelation"], "sujets": ["objet", "ecran"],
                                     "valeurs": ["entier"], "exiger": {"valeurs": ["entier", "large"]}}, premier, temps="accroche")
            if pr:
                r, e, d = pr
                self.tl.image(r, e, noir0 + d, "accroche", transition=fondu,
                              notes="object from the start: the whole object between 1 and 18 % of the duration (5 films)")
            dern = borne(g_v(g["dernier_plan_s"]), *g["dernier_plan_s"]["plage"])
            dern = min(dern, max(4.0, nom_start - i2s(self.tl.t, self.fps) - 4 * q1))
            fin_usages = nom_start - dern
            pic = g["pic"]
            n_pic, d_pic = pic["n"], pic["v"]
            t_acc = i2s(self.tl.t, self.fps)
            pic_start = max(t_acc + q1, min(pic["place"] * D, 0.5 * D - n_pic * d_pic))
            if pic_start + n_pic * d_pic > fin_usages - q1:
                n_pic = 0
            cadence = g_v(g["plan_logiciel_s"]) if logiciel else g_v(g["plan_debut_s"])

            def veut_usage(k, t):
                return {"sujets": ["geste", "ecran", "objet", "personne"], "valeurs": ["serre", "entier", "detail"],
                        "exclure": [{"role": ["fin", "gamme"]}]}
            if n_pic:
                self.remplir(pic_start, "usages", lambda t: cadence, (q1, q3), veut_usage,
                             notes="one shot per use or per feature, the object in hand or on screen")
                for k in range(n_pic):
                    t = i2s(self.tl.t, self.fps)
                    pr = self.choix.choisir({"mouvements": ["fort", "moyen"], "sujets": ["geste", "ecran"]}, d_pic)
                    if pr:
                        r, e, d = pr
                        self.tl.image(r, e, t + min(d, d_pic), "pic", notes="fast passage: 5 shots of 1.17 s (11 films)")
            self.remplir(fin_usages, "usages", lambda t: cadence, (q1, q3), veut_usage,
                         notes="one shot per use or per feature")
            t = i2s(self.tl.t, self.fps)
            pr = self.choix.choisir({"roles": ["gamme", "fin"], "sujets": ["objet", "ecran"], "valeurs": ["entier", "large"],
                                     "exiger": {"valeurs": ["entier", "large"]}}, nom_start - t, temps="fin")
            if pr:
                r, e, d = pr
                self.tl.image(r, e, t + d, "fin", notes="end on a product range (2 films) or the whole object held, then the name (3)")
        # name, then black
        t = i2s(self.tl.t, self.fps)
        if nom_start - t > 1.0 / float(self.fps) and self.tl.plans and self.tl.plans[-1]["type"] == "image":
            self.log("%.1f s of pictures missing before the name: the last shot is too short (clip to lengthen)" % (nom_start - t))
            self.tl.noir(nom_start, "fin", notes="for lack of pictures")
        if self.nom:
            self.tl.carton(nom_start + nom_dur, "nom", self.nom, "nom", fond=g_v(g["nom_fond"]), taille=taille_nom,
                           notes="name alone, centered, on a plain background (5 out of 5); between 83 and 96 %% (7 films); size %s %% (%s)"
                           % (taille_nom, "hero, software" if logiciel else "discreet, object"))
        self.tl.noir(D, "fin", transition={"type": "fondu", "duree": min(g_v(g["fondu_au_noir_s"]), 0.4 * (nom_dur or 2))},
                     notes="short final black (8 out of 16, median 0.95 s); no logo alone, no date, no slogan (0 out of 16)")

    # ============================================================ OPENING
    def ouverture(self):
        g = self.G["ouverture"]
        if self.schema == "transition_decor":
            return self.transition_decor()
        if self.schema == "cloture":
            return self.cloture()
        D = self.D = self.duree(g["duree_s"], 90.0)
        carton = self.projet.get("carton_ouverture")
        if carton:
            mots = len(carton.split())
            dc = max(g_v(g["carton_duree_min_s"]), g_v(g["carton_s_par_mot"]) * mots)
            self.tl.noir(0.5, "seuil", notes="threshold: black and silence")
            self.tl.carton(0.5 + dc, "seuil", carton, "titre", fond="noir", taille=4.0,
                           notes="threshold title card: at least 0.5 s per word (median of 7 title cards)")
            self.tl.noir(0.5 + dc + g_v(g["noir_apres_carton_s"]), "seuil", notes="black after the title card: 0.8 to 1.5 s (convention; observed 0.8 to 4.3 s)")
        else:
            seuil = g_v(g["seuil_noir_s"])
            if self.reperes:
                seuil = self.caler(seuil, 0.5, 1.5, "fade up from black")
            self.tl.noir(seuil, "seuil", notes="threshold: 0.5 to 1.5 s of black (6 out of 8 have a threshold)")
        t0 = i2s(self.tl.t, self.fps)
        p1 = borne(g_v(g["premier_plan_s"]), *g["premier_plan_s"]["plage"])
        pr = self.choix.choisir({"roles": ["accroche", "ouverture"], "valeurs": ["detail", "abstrait", "large"],
                                 "sujets": ["lumiere", "matiere", "decor"], "exclure": [{"role": ["fin", "arrivee"]}]}, p1)
        if pr:
            r, e, d = pr
            self.tl.image(r, e, t0 + d, "premier_plan", transition={"type": "fondu", "duree": g_v(g["fondu_depuis_noir_s"])},
                          notes="first shot of 5 to 10 s (5 out of 8), a detail or a light (4 out of 7) or a place (3 out of 7)")
        tiers = g_v(g["plan_tiers_s"])
        q1, q3 = g_v(g["plan_quartiles_s"])
        med = mediane(tiers)
        dern = borne(max(g_v(g["dernier_plan_s"]), g["dernier_plan_s"]["ratio_min"] * med), *g["dernier_plan_s"]["plage"])
        noir_fin = g_v(g["noir_final_s"])
        fin_img = D - noir_fin
        dern_start = fin_img - dern
        att = g["atterrissage"]
        d_att, x = [], tiers[2]
        for k in range(att["n"]):
            x *= att["facteur"]
            d_att.append(x)
        att_start = dern_start - sum(d_att)
        pic = g["pic"]
        ecart = min(2.0, 0.03 * D)       # body between the peak and the landing: 2 s, less in a short film (convention)
        fin_pic = pic["place"][0] * D + pic["n"] * pic["v"] + ecart
        if att_start < fin_pic and fin_img - fin_pic > g["dernier_plan_s"]["plage"][0]:
            # short film: the landing and the last shot tighten so the peak stays after 60 %
            # (grammar § 9.1: relative places are kept; durations: convention)
            d_att = d_att[-3:]
            dern = max(g["dernier_plan_s"]["plage"][0], min(dern, fin_img - fin_pic - 3 * q1))
            reste = max(0.0, fin_img - fin_pic - dern)
            d_att = [d * reste / sum(d_att) for d in d_att] if reste > 0 else []
            att_start = fin_img - dern - sum(d_att)
            self.log("%.0f s film: landing tightened (%d shots, %.1f s, then a last shot of %.1f s) "
                     "to keep the peak after 60 %% of the duration (convention)" % (D, len(d_att), sum(d_att), dern))
        pos = sum(pic["place"]) / 2.0
        if self.reperes and pic["place"][0] * D <= self.reperes["sommet_s"] <= pic["place"][1] * D:
            pos = self.reperes["sommet_s"] / D
            self.log("peak placed on the music's high point (%.1f s)" % self.reperes["sommet_s"])
        pic_start = pos * D - pic["n"] * pic["v"] / 2.0
        pic_start = borne(pic_start, i2s(self.tl.t, self.fps) + 2, att_start - pic["n"] * pic["v"] - ecart)
        if self.reperes:
            pic_start = self.caler(pic_start, pic["place"][0] * D, pic["place"][1] * D, "peak")
        scenes = sorted(set(r.scene for r in self.rushes if r.scene is not None))
        motif = [["large", "moyen", "entier"], ["serre", "rapproche"], ["detail", "serre"], ["serre", "detail", "moyen"]]

        def veut_corps(k, t):
            v = {"valeurs": motif[k % 4], "exclure": [{"role": ["fin", "arrivee"]}]}
            if scenes:
                idx = min(len(scenes) - 1, int((t - t0) / max(1.0, att_start - t0) * len(scenes)))
                v["exiger"] = {"scene": scenes[idx]}
            return v
        p10, p90 = g_v(g["plan_p10_p90_s"])
        self.remplir(pic_start, "corps", self.cible_tiers(tiers), (p10, p90), veut_corps,
                     notes="body: shots of 0.9 to 2.1 s (median 1.33 s, 337 shots); a scene opens wide, then tightens (8 out of 11)")
        for k in range(pic["n"]):
            t = i2s(self.tl.t, self.fps)
            pr = self.choix.choisir({"mouvements": ["fort", "moyen"], "valeurs": ["detail", "serre"],
                                     "exclure": [{"role": ["fin", "arrivee"]}]}, pic["v"])
            if pr:
                r, e, d = pr
                self.tl.image(r, e, t + min(d, pic["v"]), "pic",
                              notes="peak: 5 shots of 0.4 to 0.7 s between 60 and 80 %% (5 out of 7), on the strongest moment of the sound")
        self.remplir(att_start, "corps", self.cible_tiers(tiers), (p10, p90), veut_corps, notes="body")
        for k, d in enumerate(d_att):
            t = i2s(self.tl.t, self.fps)
            pr = self.choix.choisir({"valeurs": ["moyen", "large", "entier"], "exclure": [{"role": ["fin", "arrivee"]}]}, d)
            if pr:
                r, e, dd = pr
                self.tl.image(r, e, t + dd, "atterrissage",
                              notes="landing: 3 to 5 shots that get longer (observed by eye); 4 shots, factor 1.35 (convention)")
        t = i2s(self.tl.t, self.fps)
        pr = self.choix.choisir({"roles": ["fin", "arrivee"], "valeurs": ["large"], "sujets": ["decor", "personne"]}, fin_img - t)
        if pr:
            r, e, d = pr
            p = self.tl.image(r, e, t + d, "atterrissage",
                              notes="last shot: wide (5 out of 7), 5 to 11 s, at least 3.5 times the median shot (7 out of 7)")
            titre = self.nom
            if titre and p:
                # the title starts after 85 % of the duration: earlier, the review (O9) reads it as "in the middle"
                apres_img = int(math.floor(0.85 * D * self.fps + 1e-6)) + 1
                au_plus = i2s(max(1, p["debut_img"] + p["duree_img"] - apres_img), self.fps)
                dt = min(g_v(g["titre_fin_s"]), i2s(p["duree_img"], self.fps), au_plus)
                self.tl.poser_carton(p, titre, "titre", i2s(p["duree_img"], self.fps) - dt, dt, "centre", 4.5,
                                     fond="image")
                self.log("title placed in the last shot, after 85 %% of the duration, for %.2f s (title in the set at the end: 2 out of 8)" % dt)
                if dt < g["titre_fin_s"]["plage"][0]:
                    self.log("DEVIATION title: only %.2f s between 85 %% of the duration and the end of the last shot (observed %s to %s s); lengthen the film or the last shot"
                             % (dt, g["titre_fin_s"]["plage"][0], g["titre_fin_s"]["plage"][1]))
        if i2s(self.tl.t, self.fps) < fin_img - 0.05:
            self.combler(fin_img, "atterrissage")
        self.tl.noir(D, "fin", notes="short final black: convention (in a keynote, the stage follows)")

    def transition_decor(self):
        g = self.G["ouverture"]["transition_decor"]
        D = self.D = self.duree(g["duree_s"], 24.0)
        arrivee = borne(g_v(g["arrivee_s"]), *g["arrivee_s"]["plage"])
        n = max(1, int(g_v(g["plans"])) - 1)
        poids = [1.6 ** k for k in range(n)]
        reste = D - arrivee
        durs = [reste * p / sum(poids) for p in poids]
        self.log("target transition between places: %d departure shots (%s s), then an arrival of %.1f s; brisk departure, slow arrival (observed); ×1.6 progression (convention)"
                 % (n, ", ".join("%.1f" % d for d in durs), arrivee))
        bougent = [r for r in self.rushes if not r.absent and r.prises and r.mouvement != "fixe"]
        larges = [r for r in bougent if r.valeur == "large"]
        self.log("%d moving takes out of %d (no static shot: 0 out of 33), %d of them wide for the arrival"
                 % (len(bougent), len(self.rushes), len(larges)))
        for k, d in enumerate(durs):
            t = i2s(self.tl.t, self.fps)
            pr = self.choix.choisir({"directions": ["avant"], "mouvements": ["moyen", "fort", "lent"], "sans_fixe": True,
                                     "exclure": [{"role": ["arrivee", "fin"]}]}, d, temps="depart")
            if pr:
                r, e, dd = pr
                self.tl.image(r, e, t + dd, "depart",
                              notes="continuous forward movement (6 out of 6), no static shot (0 out of 33); hide the cut in a dark passage (14 out of 30)")
        t = i2s(self.tl.t, self.fps)
        pr = self.choix.choisir({"roles": ["arrivee", "fin"], "valeurs": ["large"], "sans_fixe": True}, D - t, temps="arrivee")
        if pr:
            r, e, d = pr
            p = self.tl.image(r, e, t + d, "arrivee",
                              notes="arrival: the longest shot (4 out of 5), held 7 to 11.5 s before the speech (median 9.3 s)")
            if p and p["duree_s"] < D - t - 0.05:
                self.log("arrival held %.2f s instead of %.2f s: no moving clip long enough" % (p["duree_s"], D - t))
            if p and p.get("valeur") != "large":
                self.log("arrival on a \"%s\" shot, not a wide shot: no wide moving clip (to shoot)"
                         % (p.get("valeur") or "no size"))
        if i2s(self.tl.t, self.fps) < D - 0.05:
            self.combler(D, "arrivee")
        if self.nom:
            self.log("no text in a transition between places (0 out of 6): the name is not written")

    def cloture(self):
        g = self.G["ouverture"]["cloture"]
        D = self.D = self.duree(self.G["ouverture"]["duree_s"], 90.0)
        self.tl.noir(g_v(g["noir_s"]), "seuil", notes="black 0.9 s (1 film)")
        carton = self.projet.get("carton_ouverture")
        if carton:
            mots = carton.split()
            if len(mots) > g_v(g["carton_mots_max"]):
                self.log("opening title card of %d words: 11 at most (1 film)" % len(mots))
            dc = max(1.94, 0.5 * len(mots))
            self.tl.carton(i2s(self.tl.t, self.fps) + dc, "seuil", carton, "titre", fond="noir", taille=4.0,
                           notes="opening title card, 0.5 s per word")
        sig = g_v(g["signature_s"])
        pic = g["pic"]
        pic_start = pic["place"] * D - pic["n"] * pic["v"] / 2.0
        fin_images = D - sig
        t0 = i2s(self.tl.t, self.fps)
        self.placer_voix(t0 + 4.0, fin_images - 2.0, "choral", couverture_max=0.65)
        personnes_nommees = set()

        def veut(k, t):
            return {"sujets": ["personne", "entretien", "photo"], "valeurs": ["rapproche", "serre", "moyen"]}
        cible = lambda t: g_v(g["plan_s"]) if t < 2 * D / 3.0 else g_v(g["plan_dernier_tiers_s"])
        self.remplir(pic_start, "visages", cible, (0.5, 3.2), veut, notes="faces; last third faster (median shot 0.98 s, 1 film)")
        for k in range(pic["n"]):
            t = i2s(self.tl.t, self.fps)
            pr = self.choix.choisir({"mouvements": ["fort", "moyen"]}, pic["v"])
            if pr:
                r, e, d = pr
                self.tl.image(r, e, t + min(d, pic["v"]), "pic", notes="peak around 90 % (1 film)")
        dern = 2 * g_v(g["plan_s"])
        self.remplir(fin_images - dern, "visages", cible, (0.5, 3.2), veut, notes="faces")
        t = i2s(self.tl.t, self.fps)
        pr = self.choix.choisir({"roles": ["fin"], "valeurs": ["large"], "sujets": ["decor", "personne", "illustration"],
                                 "exiger": {"valeurs": ["large"]}}, fin_images - t, temps="fin")
        if pr:
            r, e, d = pr
            self.tl.image(r, e, t + d, "fin", notes="end on the place or the person, wide (observed in openings 5 out of 7); duration: two body shots (convention)")
        if i2s(self.tl.t, self.fps) < fin_images - 0.05:
            self.remplir(fin_images, "visages", cible, (0.5, 3.2), veut, notes="faces")
        # lower thirds after the first third, never at the first appearance
        vus = set()
        for p in self.tl.plans:
            if p["type"] != "image":
                continue
            r = next(x for x in self.rushes if x.id == p["source"])
            if r.personne and r.personne in vus and r.personne not in personnes_nommees and p["debut_s"] > D / 3.0:
                self.tl.poser_carton(p, r.personne, "bandeau", 0, min(g_v(g["bandeau_s"]), p["duree_s"]), "bas_gauche",
                                     g_v(self.G["communs"]["taille_bandeau_pct"]), deuxieme_ligne=r.fonction)
                personnes_nommees.add(r.personne)
            if r.personne:
                vus.add(r.personne)
        if self.logo:
            self.tl.carton(D, "signature", None, "logo", fond="noir", taille=8, logo=self.logo,
                           notes="signature shot 1.5 to 3.5 s: the user's logo (convention)")
        elif self.nom:
            self.tl.carton(D, "signature", self.nom, "nom", fond="noir", taille=4.5, notes="signature shot: the name (convention, no logo)")
        else:
            self.tl.noir(D, "signature", notes="no logo and no name supplied")

    # ============================================================ VOICES (documentary, closing)
    def prises_de_parole(self):
        prises = []
        for r in self.rushes:
            if r.synchro:
                continue  # another angle: its speech is the main clip's
            for p in r.paroles:
                if p.get("role") == "bouton":
                    continue
                prises.append(dict(p, rush=r))
        if any(p.get("ordre") is not None for p in prises):
            prises.sort(key=lambda p: (p.get("ordre") is None, p.get("ordre") or 0, self.rushes.index(p["rush"]), p["entree_s"]))
        else:
            prises.sort(key=lambda p: (self.rushes.index(p["rush"]), p["entree_s"]))
        return prises

    def placer_voix(self, t_debut, t_fin_max, regime, couverture_max=None):
        """Places the speech takes on A1, from t_debut on, separated by a silence; breaths in the "pose" regime."""
        g = self.G["documentaire"]
        prises = self.prises_de_parole()
        sil = g_v(g["silence_entre_prises_s"])
        resp = g_v(g["respiration_s"])
        t = t_debut
        derniere_resp = t_debut
        posees = []
        budget = None
        if couverture_max:
            budget = couverture_max * (t_fin_max - t_debut)
        total = 0.0
        for p in prises:
            L = p["sortie_s"] - p["entree_s"]
            if t + L > t_fin_max + 1e-6 or (budget is not None and total + L > budget):
                self.log("take \"%s\" left out: no more room" % (p.get("texte") or p["rush"].id)[:40])
                continue
            q = self.tl.parole(p["rush"], p["entree_s"], t, L, personne=p["rush"].personne, texte=p.get("texte"))
            q["_rush"] = p["rush"]
            q["_chapitre"] = p.get("chapitre")
            posees.append(q)
            total += L
            t += L + sil
            if regime == "pose" and t - derniere_resp >= 60.0 / g_v(g["respiration_par_minute"]):
                debut_resp = t - sil
                t = debut_resp + resp  # the silence becomes a breath
                derniere_resp = t
                self.tl.marqueurs.append({"debut_img": s2i(debut_resp, self.fps), "duree_img": s2i(resp, self.fps),
                                          "nom": "breath", "texte": "music alone: raise it"})
        return posees

    # ============================================================ DOCUMENTARY
    def documentaire(self):
        g = self.G["documentaire"]
        regime = self.schema
        R = g[regime]
        prises = self.prises_de_parole()
        if not prises:
            raise SystemExit("documentary: no speech in the footage (the \"paroles\" field of the interviews)")
        # opening
        noir0 = g_v(g["noir_ouverture_s"])
        self.tl.noir(noir0, "ouverture", notes="the film starts from black (6 out of 8)")
        these = self.projet.get("these")
        t_img = noir0
        if these:
            mots = len(these.split())
            if mots > 12:
                self.log("thesis of %d words: 12 at most (observed)" % mots)
            dc = borne(0.5 * mots, 3.17, 4.74)
            self.tl.carton(noir0 + dc, "ouverture", these, "these", fond="noir", taille=5.5,
                           notes="question or thesis at the opening (2 out of 8), small, centered, no box")
            t_img = noir0 + dc
        premiere = max(g_v(g["premiere_parole_s"]), t_img + 2.0)
        # target length: the requested duration, otherwise all the speech
        D_vise = float(self.args.duree) if self.args.duree else None
        fin_parole = (D_vise - g_v(R["derniere_parole_avant_fin_s"])) if D_vise else 1e9
        voix = self.placer_voix(premiere, fin_parole, regime)
        if not voix:
            raise SystemExit("documentary: no take fits in the requested duration")
        t_last = i2s(voix[-1]["debut_img"] + voix[-1]["duree_img"], self.fps)
        logo_d = g_v(g["choral"]["logo_s"]) if (regime == "choral" and (self.logo or self.nom)) else 0.0
        D = self.D = D_vise if D_vise else t_last + g_v(R["derniere_parole_avant_fin_s"])
        if regime == "choral" and logo_d:
            D = max(D, t_last + 1.0 + logo_d)
        if not (g["duree_s"]["plage"][0] <= D <= g["duree_s"]["plage"][1]):
            self.log("duration %.1f s outside the observed range (78 to 324 s, 8 films)" % D)
        # face windows
        visages = self.fenetres_visage(voix, D, regime)
        # end
        if regime == "pose":
            fin_debut = D - borne(g_v(R["plan_final_s"]), *R["plan_final_s"]["plage"])
        else:
            raf = R["rafale_finale"]
            fin_debut = D - logo_d - raf["n"] * raf["v"]
        visages = [v for v in visages if v[0] < fin_debut - 0.5]
        visages = [(a, min(b, fin_debut), *rest) for a, b, *rest in visages]
        tiers = g_v(R["plan_tiers_s"])
        lo, hi = g_v(R["plan_plage_s"])
        bandeau_fait = set()
        nb_personnes = len(set(v["personne"] for v in voix if v.get("personne")))

        def veut_illu(k, t):
            parle = next((v for v in voix if v["debut_img"] <= s2i(t, self.fps) < v["debut_img"] + v["duree_img"]), None)
            v = {"sujets": ["illustration", "personne", "oeuvre", "photo", "archive", "decor", "geste"],
                 "exclure": [{"sujet": ["entretien"]}, {"role": ["fin"]}],
                 "valeurs": ["large", "moyen"] if k % 3 == 0 else ["detail", "serre", "moyen"]}
            if parle and parle.get("personne"):
                v["personne"] = parle["personne"]
            return v
        premier = True
        for (a, b, rush, src_e, personne) in visages:
            self.remplir(a, "illustration", self.cible_tiers(tiers), (lo, hi), veut_illu,
                         premier_trans={"type": "fondu", "duree": 0.9} if premier else None,
                         notes="the voice runs over the illustration (two thirds of the time, observed)")
            premier = False
            t = i2s(self.tl.t, self.fps)
            if b - t < 0.5:
                continue
            p = self.tl.image(rush, src_e + (t - a), b, "entretien", sync=True,
                              notes="face: static shot (18 out of 20), mostly medium close-up; 3.2 s at most (p90 of 162 shots)")
            if p and personne and personne not in bandeau_fait and nb_personnes:
                self.tl.poser_carton(p, personne, "bandeau", 0, min(g_v(g["bandeau_s"]), p["duree_s"]), "bas_gauche",
                                     g_v(self.G["communs"]["taille_bandeau_pct"]), deuxieme_ligne=rush.fonction)
                bandeau_fait.add(personne)
        self.remplir(fin_debut, "illustration", self.cible_tiers(tiers), (lo, hi), veut_illu,
                     premier_trans={"type": "fondu", "duree": 0.9} if premier else None, notes="illustration")
        t = i2s(self.tl.t, self.fps)
        if regime == "pose":
            pr = self.choix.choisir({"roles": ["fin"], "valeurs": ["large"], "exclure": [{"sujet": ["entretien"]}]}, D - t)
            if pr:
                r, e, d = pr
                self.tl.image(r, e, t + d, "fin", notes="calm ending: one shot held 5.7 to 8.1 s, preferably wide (5 out of 5)")
            if i2s(self.tl.t, self.fps) < D - 0.05:
                self.combler(D, "fin")
        else:
            raf = R["rafale_finale"]
            for k in range(raf["n"]):
                t = i2s(self.tl.t, self.fps)
                pr = self.choix.choisir({"sujets": ["oeuvre", "objet", "ecran"], "exclure": [{"sujet": ["entretien", "personne"]}],
                                         "exiger": {"sujets": ["oeuvre", "objet", "ecran", "illustration"]}}, raf["v"],
                                        temps="rafale")
                if pr:
                    r, e, d = pr
                    self.tl.image(r, e, t + min(d, raf["v"]), "rafale",
                                  notes="final burst: 3 to 5 shots of 0.29 to 0.42 s, works, never a face (4 out of 4)")
            if self.logo:
                self.tl.carton(D, "fin", None, "logo", fond="noir", taille=8, logo=self.logo, notes="the user's logo, 2.2 to 4.2 s (5 out of 8)")
            elif self.nom:
                self.tl.carton(D, "fin", self.nom, "nom", fond="noir", taille=4.5, notes="no logo: the name (convention)")
            else:
                t = i2s(self.tl.t, self.fps)
                pr = self.choix.choisir({"sujets": ["oeuvre", "illustration"], "exclure": [{"sujet": ["entretien"]}]}, D - t)
                if pr:
                    r, e, d = pr
                    self.tl.image(r, e, t + d, "fin", notes="no logo and no name: one last work (convention)")
                if i2s(self.tl.t, self.fps) < D - 0.05:
                    self.tl.noir(D, "fin")
        for q in self.tl.paroles:
            q.pop("_rush", None)
            q.pop("_chapitre", None)

    def fenetres_visage(self, voix, D, regime):
        """When do we see the person speaking: the voice first, the face 3 s later; a third of the speech on the face.

        Returns windows (start_s, end_s, clip, source_in_at_start_s, person)."""
        g = self.G["documentaire"]
        part = g_v(g["parole_sur_visage"])
        avant = g_v(g["voix_avant_visage_s"])
        dec = g_v(g["decalage_coupe_voix_s"])
        fmax = g_v(g["entretien_max_s"])
        ecart = 2 * g_v(g[regime]["plan_tiers_s"])[1]
        vus = set()
        budget = 0.0
        out = []
        compte = {}
        for q in voix:
            r = q["_rush"]
            a = i2s(q["debut_img"], self.fps)
            b = a + i2s(q["duree_img"], self.fps)
            budget += part * (b - a)
            premier = r.personne not in vus
            debut = a + (avant if premier else dec)
            if premier and (b - a) < avant + 1.0:
                continue  # the person comes in by voice; their face will come with a later take
            vus.add(r.personne)
            while budget >= 1.0 and b - debut >= 1.0:
                f = min(fmax, budget, b - debut)
                angle = self.angle(r, compte, out[-1] if out else None)
                rush, decal = angle if angle else (r, 0.0)
                out.append((debut, debut + f, rush, q["entree_s"] + decal + (debut - a), r.personne))
                budget -= f
                debut = debut + f + ecart
        return out

    def angle(self, r, compte, precedent):
        """Another synchronized angle of the same person, chosen to approach medium close-up 53 %, medium 26 %,
        close-up/extreme close-up 21 % (observed)."""
        cibles = g_v(self.G["documentaire"]["valeurs_entretien"])
        angles = [(r, 0.0)] + [(x, float(x.synchro.get("decalage_s", 0.0))) for x in self.rushes
                               if x.synchro and x.synchro.get("avec") == r.id]
        if len(angles) == 1:
            return None
        tot = sum(compte.values()) + 1

        def manque(a):
            v = a[0].valeur if a[0].valeur in cibles else ("serre" if a[0].valeur == "detail" else a[0].valeur)
            return cibles.get(v, 0) - compte.get(v, 0) / float(tot)
        if precedent and precedent[4] == r.personne:
            rp = RANG.get(precedent[2].valeur, 3)
            plus_serres = [a for a in angles if RANG.get(a[0].valeur, 3) < rp]
            if plus_serres:
                angles = plus_serres
        a = max(angles, key=manque)
        v = a[0].valeur
        compte[v] = compte.get(v, 0) + 1
        return a

    # ============================================================ TRAILER
    def bande_annonce(self):
        g = self.G["bande_annonce"]
        schema = self.schema
        if schema == "usage":
            return self.usage()
        D = self.D = self.duree(g["duree_s"], 89.0)
        tiers = g_v(g["plan_tiers_s"])
        repliques = []
        bouton = None
        for r in self.rushes:
            for p in r.paroles:
                if p.get("role") == "bouton" or "bouton" in r.role:
                    bouton = (r, p)
                else:
                    repliques.append((r, p))
        if bouton is None and repliques and schema == "oeuvre":
            bouton = repliques.pop()
        # closing
        titre_d = g_v(g["titre_final_s"])
        noir_fin = g_v(g["noir_final_s"])
        t_titre = D - noir_fin - titre_d
        if bouton:
            Lb = borne(bouton[1]["sortie_s"] - bouton[1]["entree_s"], *g["bouton_s"]["plage"])
            ferm = g_v(g["noir_avant_bouton_s"]) + Lb + g_v(g["noir_apres_bouton_s"])
        else:
            Lb = 0
            ferm = g_v(g["noir_avant_bouton_s"])
        f_start = t_titre - ferm
        pic = g["pic"]
        pic_end = min(pic["place"][1] * D, f_start)
        pic_start = max(pic["place"][0] * D, pic_end - 10.0)
        noir0 = g_v(g["noir_ouverture_s"])
        self.tl.noir(noir0, "noir", notes="opening in black: 7 out of 7, median 0.6 s")
        blocs = []
        for r in self.rushes:
            if r.bloc is not None and r.bloc not in blocs:
                blocs.append(r.bloc)
        mention = self.projet.get("mention")
        if schema == "oeuvre" and mention:
            t = i2s(self.tl.t, self.fps)
            self.tl.carton(t + 2.24, "noir", mention, "mention", fond="noir", taille=2.5,
                           notes="3-word mention, very small, on black, 2.2 s (2 out of 2 works)")
        elif schema == "oeuvre":
            self.log("trailer for a work: a short mention on black opens it (2 out of 2); supply the \"mention\" field")
        if schema == "oeuvre":
            self.log("credits (8 to 12 words, between 29 and 45 %%, 2 works): place them by hand if there are any")
        acc_fin = g_v(g["accroche_fin"]) * D
        # lines: the first right at the start, then spread outside the peak
        self.planifier_repliques(repliques, noir0 + 0.5, pic_start, D)

        def veut_acc(k, t):
            v = {"valeurs": ["large"] if k % 3 != 2 else ["moyen", "serre"], "exclure": [{"role": ["bouton", "fin", "signature"]}]}
            if k % 3 != 2:
                v["exiger"] = {"valeurs": ["large"]}  # wide shots first: at least 35 % in the first third (39 to 56 % observed)
            elif blocs:
                v["bloc"] = blocs[k % len(blocs)]
            return v
        self.remplir(acc_fin, "accroche", lambda t: g_v(g["plan_ouverture_s"]), (0.5, 2.9), veut_acc,
                     notes="hook: wide shots first (6 out of 6), a line within the first seconds (4 out of 5)")
        # announcement: punch words on black, the picture rises under the text
        chocs = self.projet.get("mots_chocs") or []
        if schema.startswith("catalogue") and chocs:
            for m in chocs[:3]:
                t = i2s(self.tl.t, self.fps)
                self.tl.carton(t + g_v(g["mot_choc_s"]), "annonce", m, "mot_choc", fond="noir", taille=6.0,
                               notes="punch word of 1 or 2 words, 1.0 to 2.3 s, between 15 and 25 % (5 in 2 films)")
                pr = self.choix.choisir({"valeurs": ["large", "moyen"], "exclure": [{"role": ["bouton", "fin"]}]}, tiers[0])
                if pr:
                    r, e, d = pr
                    self.tl.image(r, e, t + g_v(g["mot_choc_s"]) + d, "annonce", transition={"type": "fondu", "duree": 0.5},
                                  notes="the picture rises under the text (3 out of 5): the only place for a cross dissolve")
        elif schema.startswith("catalogue"):
            self.log("no punch words supplied: the announcement is skipped")
        # body
        if schema == "catalogue_blocs" and blocs:
            bloc_d = g_v(g["bloc_s"])
            titre_b = g_v(g["titre_bloc_s"])
            corps_d = pic_start - i2s(self.tl.t, self.fps)
            if corps_d / bloc_d > len(blocs):
                # few subjects: longer blocks (up to 7.8 s, the longest of the 21 observed) before repeating a subject
                bloc_d = min(g["bloc_s"]["plage"][1], corps_d / float(len(blocs)))
                if corps_d / bloc_d > len(blocs) + 0.5:
                    self.log("%d subjects for %.0f s of body: some subjects come back; supply more subjects or shorten" % (len(blocs), corps_d))
            k = 0
            while pic_start - i2s(self.tl.t, self.fps) > bloc_d * 0.6:
                b = blocs[k % len(blocs)]
                t = i2s(self.tl.t, self.fps)
                fin_bloc = min(pic_start, t + bloc_d)
                if pic_start - fin_bloc < bloc_d * 0.6:
                    fin_bloc = pic_start
                titre = next((r.titre_bloc for r in self.rushes if r.bloc == b and r.titre_bloc), None) or str(b)
                self.tl.carton(t + titre_b, "bloc", titre, "titre_bloc", fond="noir", taille=4.0,
                               notes="the title opens its block (20 out of 21), 1.0 s (20 titles)")
                self.remplir(fin_bloc, "bloc", self.cible_tiers(tiers), (0.5, 1.7),
                             lambda kk, tt, b=b: {"bloc": b, "exiger": {"bloc": b}, "valeurs": ["large", "moyen", "serre"],
                                                  "exclure": [{"role": ["bouton", "fin"]}]},
                             notes="4.5 s block (21 blocks), 3 to 6 shots")
                k += 1
            if k < len(blocs):
                self.log("%d blocks edited for %d subjects: lengthen the film or cut down the subjects" % (k, len(blocs)))
        else:
            def veut_corps(k, t):
                v = {"valeurs": ["moyen", "serre", "large", "rapproche"], "exclure": [{"role": ["bouton", "fin"]}]}
                if blocs:
                    v["bloc"] = blocs[k % len(blocs)]
                return v
            self.remplir(pic_start, "corps", self.cible_tiers(tiers), (0.5, 3.5 if schema == "oeuvre" else 1.7), veut_corps,
                         notes="body: shots get shorter third after third (last third faster 6 out of 6)")
        # peak
        def veut_pic(k, t):
            v = {"mouvements": ["fort", "moyen"], "exclure": [{"role": ["bouton", "fin"]}]}
            if blocs:
                v["bloc"] = blocs[k % len(blocs)]
            return v
        self.remplir(pic_end, "pic", lambda t: pic["v"], (pic["plage"][0], 0.85), veut_pic,
                     notes="peak: the shortest shots (0.62 s), mixed subjects, less speech (6 out of 6)")
        if i2s(self.tl.t, self.fps) < f_start - 0.05:
            self.remplir(f_start, "pic", lambda t: pic["v"], (pic["plage"][0], 0.85), veut_pic, notes="peak")
        # closing
        t = i2s(self.tl.t, self.fps)
        self.tl.noir(t + g_v(g["noir_avant_bouton_s"]), "fermeture", notes="black between the peak and what follows (4 out of 6)")
        if bouton:
            r, p = bouton
            t = i2s(self.tl.t, self.fps)
            self.tl.image(r, p["entree_s"], t + Lb, "bouton", transition={"type": "fondu", "duree": g_v(g["fondu_depuis_noir_s"])},
                          sync=True, notes="button: a single line over 1 or 2 shots (4 out of 6), fades up from black (4 out of 4)")
            self.tl.parole(r, p["entree_s"], t, min(Lb, p["sortie_s"] - p["entree_s"]), personne=r.personne, texte=p.get("texte"))
            self.tl.noir(t + Lb + g_v(g["noir_apres_bouton_s"]), "fermeture", notes="black")
        else:
            self.log("no button (closing line): observed in 4 trailers out of 6, optional")
        self.titre_final(D - noir_fin, titre_d, g)
        self.tl.noir(D, "fermeture", notes="final black (convention)")
        self.tl.paroles.sort(key=lambda q: q["debut_img"])
        for i, q in enumerate(self.tl.paroles):
            q["n"] = i + 1

    def titre_final(self, fin, titre_d, g):
        trans = {"type": "fondu", "duree": g_v(g["fondu_depuis_noir_s"])}
        if self.logo:
            self.tl.carton(fin, "titre", None, "logo", fond="noir", taille=8, logo=self.logo, transition=trans,
                           notes="final title or logo: 8 out of 8, 2.5 to 4.8 s, fades up from black (4 out of 6)")
        elif self.nom:
            self.tl.carton(fin, "titre", self.nom, "titre", fond="noir", taille=6.0, transition=trans,
                           notes="final title: 8 out of 8, 2.5 to 4.8 s, fades up from black (4 out of 6); never end on a picture (8 out of 8)")
        else:
            self.log("no title and no logo supplied: a trailer ends on its title (8 out of 8); please supply one")
            self.tl.noir(fin, "titre")

    def planifier_repliques(self, repliques, t0, t1, D):
        """Places the lines on A1: the first right at the start, the others spread up to the peak, ~48 % of the time at most."""
        g = self.G["bande_annonce"]
        if not repliques:
            self.log("no lines supplied: trailer without speech (music only)")
            return
        cible = g_v(g["part_parole"]) * D
        rmax = g_v(g["replique_max_s"])
        sel, total = [], 0.0
        for r, p in sorted(repliques, key=lambda x: (x[1].get("ordre") is None, x[1].get("ordre") or 0)):
            L = p["sortie_s"] - p["entree_s"]
            if L > rmax + 0.05:
                self.log("line of %.1f s shortened to 3.1 s (p90 of 108 lines)" % L)
                L = rmax
            if total + L > min(cible, 0.8 * (t1 - t0)):
                break
            sel.append((r, p, L))
            total += L
        if not sel:
            return
        libre = (t1 - t0) - total
        pas = libre / float(len(sel))
        t = t0
        for r, p, L in sel:
            self.tl.parole(r, p["entree_s"], t, L, personne=r.personne, texte=p.get("texte"))
            t += L + pas
        self.log("%d lines placed (%.0f %% of the time; observed 28 to 58 %%); the line runs over the cut (94 out of 108)"
                 % (len(sel), 100 * total / D))

    def usage(self):
        g = self.G["bande_annonce"]
        u = g["usage"]
        D = self.D = self.duree(g["duree_usage_s"], 60.0)
        tiers = g_v(u["plan_tiers_s"])
        noir0 = g_v(g["noir_ouverture_s"])
        self.tl.noir(noir0, "ouverture", notes="black, then a shot that reveals the situation (2 out of 2)")
        pr = self.choix.choisir({"roles": ["ouverture", "accroche"], "valeurs": ["large"], "directions": ["avant", "lateral"]},
                                g_v(u["ouverture_plan_s"]))
        if pr:
            r, e, d = pr
            self.tl.image(r, e, noir0 + d, "ouverture", transition={"type": "fondu", "duree": g_v(g["fondu_depuis_noir_s"])},
                          notes="a long take that reveals the scene (5.1 s, 1 film) or a glow from the object")
        nom_d = g_v(u["nom_s"]) if (self.nom or self.logo) else 0
        phrase = self.projet.get("phrase")
        phr_d = g_v(u["phrase_s"]) if phrase else 0
        # text appears only in the last 10 % (2 out of 2): the sentence and the name fit in 0.1 × D
        dispo = 0.1 * D - 2.0 / float(self.fps)
        if phrase and phr_d + nom_d > dispo:
            phr_d = max(dispo - nom_d, 0.5 * len(phrase.split()), 1.0)
            if phr_d + nom_d > dispo:
                self.log("the sentence and the name go past the last 10 %% (%.1f s for %.1f s): film too short or sentence too long" % (phr_d + nom_d, dispo))
        fin_scenes = D - nom_d - phr_d
        pic = u["pic"]
        pic_start = pic["place"][0] * D
        pic_end = min(pic["place"][1] * D, fin_scenes)
        scenes = sorted(set(r.scene for r in self.rushes if r.scene is not None))
        role_cycle = [{"valeurs": ["large"], "sujets": ["decor", "personne"]},
                      {"sujets": ["personne"], "valeurs": ["moyen", "rapproche"]},
                      {"sujets": ["objet", "ecran", "piece"], "valeurs": ["serre", "detail", "entier"],
                       "exiger": {"sujets": ["objet", "ecran", "piece"]}},
                      {"sujets": ["geste", "ecran", "objet"], "valeurs": ["serre", "detail"]}]
        t_debut = i2s(self.tl.t, self.fps)

        def veut(k, t):
            v = dict(role_cycle[k % 4])
            v["exclure"] = [{"role": ["fin", "gamme"]}]
            if scenes:
                idx = min(len(scenes) - 1, int((t - t_debut) / max(1.0, pic_start - t_debut) * len(scenes)))
                v["exiger"] = {"scene": scenes[idx]}
            return v
        if not scenes:
            self.log("no numbered scenes: shots follow the cycle situation, person, object, effect (observed 2 out of 2)")
        self.remplir(pic_start, "scenes", self.cible_tiers(tiers), (0.5, 3.0), veut,
                     notes="everyday scene: situation, person, the object, what the object does; the object one shot in three (2 out of 2)")
        self.remplir(pic_end, "pic", lambda t: pic["v"], (pic["plage"][0], pic["plage"][1]),
                     lambda k, t: {"mouvements": ["fort", "moyen"], "exclure": [{"role": ["fin", "gamme"]}]},
                     notes="peak: alternating scenes, shots of 0.4 to 0.8 s (1 film out of 2)")
        if i2s(self.tl.t, self.fps) < fin_scenes - 0.05:
            t = i2s(self.tl.t, self.fps)
            pr = self.choix.choisir({"roles": ["fin", "gamme"], "sujets": ["objet"], "valeurs": ["entier", "serre"]}, fin_scenes - t)
            if pr:
                r, e, d = pr
                self.tl.image(r, e, t + d, "fin", notes="the object")
            if i2s(self.tl.t, self.fps) < fin_scenes - 0.05:
                self.tl.noir(fin_scenes, "fin")
        if phrase:
            mots = len(phrase.split())
            if not 3 <= mots <= 9:
                self.log("sentence of %d words: 3 to 9 observed (2 films)" % mots)
            t = i2s(self.tl.t, self.fps)
            self.tl.carton(t + phr_d, "fin", phrase, "phrase", fond="noir", taille=4.5,
                           notes="a sentence of 3 to 9 words, then the name (2 out of 2)")
        if nom_d:
            self.titre_final(D, nom_d, g)
        elif i2s(self.tl.t, self.fps) < D - 0.05:
            self.tl.noir(D, "fin")

    # ============================================================ check
    def mesurer(self):
        fps = self.fps
        P = self.tl.plans
        D = i2s(self.tl.t, fps)
        imgs = [p for p in P if p["type"] == "image"]
        durs = [i2s(p["duree_img"], fps) for p in imgs]
        trans = [p["transition"]["type"] for p in P[1:]]
        coupes = sum(1 for x in trans if x == "coupe") / float(len(trans) or 1)
        c = self.controle

        def ajoute(id_, mesure, cible, statut, base, ok=None):
            if ok is None and isinstance(cible, (list, tuple)) and mesure is not None:
                ok = cible[0] - 1e-6 <= mesure <= cible[1] + 1e-6
            c.append({"id": id_, "mesure": None if mesure is None else round(mesure, 3), "cible": cible, "statut": statut,
                      "base": base, "ok": ok})
        f = self.famille
        if f == "produit":
            g = self.G["produit"]
            ajoute("duree_s", D, g["duree_s"]["plage"], "observe", g["duree_s"]["base"])
            ajoute("plan_median_s", mediane(durs), g["plan_median_film"]["plage"], "observe", g["plan_median_film"]["base"])
            ajoute("plans_par_minute", len(imgs) / D * 60, g["plans_par_minute"]["plage"], "observe", g["plans_par_minute"]["base"])
            ajoute("part_coupes", coupes, [0.8, 1.0], "observe", g["coupes_min"]["base"])
            rev = next((p for p in P if p["temps"] == "revelation"), None)
            if self.schema == "revelation_tardive":
                ajoute("revelation_objet_entier", 1.0 if rev and rev.get("valeur") == "entier" else 0.0, [1, 1], "observe",
                       "a reveal shows the whole object: 10 films out of 10; without an \"entier\" shot, no reveal")
                if rev:
                    ajoute("revelation_place", rev["debut_s"] / D, g["revelation_place"]["plage"], "observe",
                           g["revelation_place"]["base"])
                premier = imgs[0] if imgs else None
                ajoute("premier_plan_pas_objet_entier", 1.0 if premier and not (premier["valeur"] == "entier") else 0.0, [1, 1],
                       "observe", "first shot = whole object: 0 out of 10 late-reveal films")
                deux_tiers = [p for p in imgs if p["debut_s"] < 2 * D / 3.0]
                part = sum(1 for p in deux_tiers if p["valeur"] in SERRES) / float(len(deux_tiers) or 1)
                ajoute("part_serre_deux_premiers_tiers", part, [0.5, 1.0], "observe", "65 to 70 % (alert under 50 %)")
            nom = next((p for p in P if p["temps"] == "nom"), None)
            ajoute("nom_place", nom["debut_s"] / D if nom else None, g["nom_place"]["plage"], "observe", g["nom_place"]["base"],
                   ok=None if nom else False)
            if nom:
                ajoute("nom_duree_s", nom["duree_s"], g["nom_duree_s"]["plage"], "observe", g["nom_duree_s"]["base"])
            if imgs:
                ajoute("dernier_plan_image_s", durs[-1], [4.0, 99], "observe", "at least 4 s in 13 out of 16")
                ajoute("plus_long_plan_s", max(durs), [5.0, 99], "observe", "a shot of at least 5 s: 14 out of 16")
            fe = sum(1 for i, p in enumerate(P[1:], 1) if p["transition"]["type"] == "fondu" and P[i - 1]["type"] == "image" and p["type"] == "image")
            ajoute("fondus_enchaines", fe, [0, 1], "observe", "at most 1 per film (16 films)")
            if imgs:
                ajoute("part_plans_fixes", sum(1 for p in imgs if est_fixe(p)) / float(len(imgs)), [0.0, 0.25],
                       "convention", "observed: 14 static shots out of 197 (7 %); 25 % threshold: convention, the review's (K15); a shot counts as static under 10.5, a margin over the review's measure; above that, the footage moves too little: shoot movement, or state the deviation")
        elif f == "ouverture":
            g = self.G["ouverture"]
            if self.schema == "transition_decor":
                gt = g["transition_decor"]
                ajoute("duree_s", D, gt["duree_s"]["plage"], "observe", gt["duree_s"]["base"])
                ajoute("plans", len(imgs), gt["plans"]["plage"], "observe", gt["plans"]["base"])
                if durs:
                    ajoute("arrivee_plus_long", 1.0 if durs[-1] == max(durs) else 0.0, [1, 1], "observe", "arrival = longest shot 4 out of 5")
                ajoute("plans_fixes", sum(1 for p in imgs if est_fixe(p)), [0, 0], "observe",
                       "0 out of 33; movement measured on the used passage, close to the review's measure (O16): static under 10.5")
            elif self.schema == "cloture":
                gc = g["cloture"]
                ajoute("duree_s", D, g["duree_s"]["plage"], "convention", g["duree_s"]["base"])
                ajoute("plan_median_s", mediane(durs), None, "observe", "reference: 1.08 s in the only closing film measured (v2-09)")
                ajoute("changements_par_minute", (len(P) - 1) / D * 60, None, "observe", "reference: 45.1 in the only film measured")
                if self.tl.paroles:
                    pp = sum(q["duree_img"] for q in self.tl.paroles) / float(self.tl.t)
                    ajoute("part_parole", pp, [0.5, 0.65], "convention", "people's voices 66 % of the time (1 film); target 50 to 65 %")
                ajoute("signature_s", i2s(P[-1]["duree_img"], fps),
                       gc["signature_s"]["plage"], "observe", gc["signature_s"]["base"])
            else:
                ajoute("duree_s", D, g["duree_s"]["plage"], "convention", g["duree_s"]["base"])
                corps = durs[1:-1] if len(durs) > 2 else durs
                ajoute("plan_median_corps_s", mediane(corps), [0.9, 2.1], "observe", "median 1.33 s; alert outside 0.9-2.1 s")
                ch = len(P) - 1
                ajoute("changements_par_minute", ch / D * 60, g["changements_par_minute"]["plage"], "observe",
                       g["changements_par_minute"]["base"])
                if self.schema == "ouverture" and durs:
                    ajoute("premier_plan_s", durs[0], [5.0, 99], "observe", "at least 5 s: 5 out of 8")
                    ajoute("dernier_plan_s", durs[-1], [5.0, 99], "observe", "at least 5 s: 6 out of 8")
                    ajoute("dernier_sur_median", durs[-1] / (mediane(corps) or 1), [3.5, 99], "observe", "at least 3.5 times: 7 out of 7")
                    pics = [p for p in P if p["temps"] == "pic"]
                    if pics:
                        ajoute("pic_place", pics[0]["debut_s"] / D, g["pic"]["place"], "observe", g["pic"]["base"])
                    hn = [p["transition"]["type"] for i, p in enumerate(P[1:], 1) if p["type"] != "noir" and P[i - 1]["type"] != "noir"]
                    ajoute("part_coupes", sum(1 for x in hn if x == "coupe") / float(len(hn) or 1), [0.95, 1.0], "observe",
                           "97.8 % cuts (359 out of 367); fades with black are at the entrance (6 out of 6) and do not count here")
                    # same bounds as the review (O9): a text that starts between 15 and 85 % of the duration
                    milieu = [p for p in P if p.get("carton")
                              and 0.15 * D <= p["debut_s"] + i2s(p["carton"].get("debut_img", 0), self.fps) <= 0.85 * D]
                    ajoute("textes_au_milieu", len(milieu), [0, 0], "observe", "0 out of 7 between 15 and 85 % of the duration")
        elif f == "documentaire":
            g = self.G["documentaire"]
            R = g[self.schema]
            par = sum(q["duree_img"] for q in self.tl.paroles) / float(self.tl.t or 1)
            ajoute("duree_s", D, g["duree_s"]["plage"], "observe", g["duree_s"]["base"])
            ajoute("couverture_parole", par, g["couverture_parole"]["plage"], "observe", g["couverture_parole"]["base"])
            sur_visage = 0
            for q in self.tl.paroles:
                for p in imgs:
                    if p.get("sync"):
                        a = max(q["debut_img"], p["debut_img"])
                        b = min(q["debut_img"] + q["duree_img"], p["debut_img"] + p["duree_img"])
                        sur_visage += max(0, b - a)
            tot = sum(q["duree_img"] for q in self.tl.paroles) or 1
            ajoute("parole_sur_visage", sur_visage / float(tot), g["parole_sur_visage"]["plage"], "observe", g["parole_sur_visage"]["base"])
            if self.tl.paroles:
                ajoute("premiere_parole_s", self.tl.paroles[0]["debut_s"], g["premiere_parole_s"]["plage"], "observe", g["premiere_parole_s"]["base"])
                fin_p = i2s(self.tl.paroles[-1]["debut_img"] + self.tl.paroles[-1]["duree_img"], fps)
                ajoute("derniere_parole_avant_fin_s", D - fin_p, R["derniere_parole_avant_fin_s"]["plage"], "observe",
                       R["derniere_parole_avant_fin_s"]["base"])
            ent = [i2s(p["duree_img"], fps) for p in imgs if p.get("sync")]
            if ent:
                ajoute("entretien_max_s", max(ent), [0, 3.2], "observe", g["entretien_max_s"]["base"])
            ajoute("plan_median_s", mediane(durs), [1.8, 2.2] if self.schema == "pose" else [1.0, 1.5], "observe",
                   "calm 1.84 to 2.19 s (5/5); choral 1.03 to 1.53 s (3/3)")
            ajoute("part_coupes", coupes, [0.95, 1.0], "observe", "98 % cuts (594 out of 606)")
        else:
            g = self.G["bande_annonce"]
            if self.schema == "usage":
                ajoute("duree_s", D, g["duree_usage_s"]["plage"], "observe", g["duree_usage_s"]["base"])
            else:
                ajoute("duree_s", D, g["duree_s"]["plage"], "observe", g["duree_s"]["base"])
            ajoute("plan_median_s", mediane(durs), [0.75, 1.2] if self.schema != "usage" else [1.0, 1.7], "observe",
                   "trailer 0.73 to 1.65 s per film; usage 1.03 and 1.67 s")
            t3 = [mediane([i2s(p["duree_img"], fps) for p in imgs if k * D / 3 <= p["debut_s"] < (k + 1) * D / 3] or [0]) for k in range(3)]
            ajoute("dernier_tiers_plus_rapide", 1.0 if t3[2] < t3[0] else 0.0, [1, 1], "observe", "6 out of 6")
            ajoute("part_coupes", coupes, [0.9, 1.0], "observe", "92 % cuts")
            fin = P[-2] if len(P) > 1 and P[-1]["type"] == "noir" else (P[-1] if P else None)
            ajoute("finit_sur_titre", 1.0 if fin and fin["type"] == "carton" else 0.0, [1, 1], "observe", "8 out of 8")
            if imgs:
                ajoute("part_plans_fixes", sum(1 for p in imgs if est_fixe(p)) / float(len(imgs)), [0.0, 0.25], "convention",
                       "observed: 29 static shots out of 384 (7.6 %); 15 % at most targeted, review alert above 25 % (B10); "
                       "a shot counts as static under 10.5, a margin over the review's measure; "
                       "above that, the footage moves too little: shoot movement, or state the deviation")
            if self.schema != "usage":
                large = [p for p in imgs if p["debut_s"] < D / 3.0]
                part = sum(1 for p in large if p["valeur"] == "large") / float(len(large) or 1)
                ajoute("part_large_premier_tiers", part, [0.35, 1.0], "convention", g["part_large_debut_min"]["base"])
                if self.tl.paroles:
                    pp = sum(q["duree_img"] for q in self.tl.paroles) / float(self.tl.t)
                    ajoute("part_parole", pp, g["part_parole"]["plage"], "observe", g["part_parole"]["base"])

    # ============================================================ output
    def construire(self):
        f = self.famille
        if f == "produit":
            self.produit()
        elif f == "ouverture":
            self.ouverture()
        elif f == "documentaire":
            self.documentaire()
        elif f == "bande_annonce":
            self.bande_annonce()
        if f in ("bande_annonce",) or self.schema == "cloture":
            self.montrer_qui_parle()
        self.recaler_sync()
        for q in self.tl.paroles:
            q.pop("_rush", None)
            q.pop("_chapitre", None)
        self.verifier_marges()
        rid = {r.id: r for r in self.rushes}
        for p in self.tl.plans:
            r = rid.get(p.get("source")) if p["type"] == "image" else None
            mm = r.mouvement_passage(p["entree_s"], p["sortie_s"]) if r else None
            if mm is not None:
                p["mouvement_mesure"] = round(mm, 1)
        self.mesurer()
        obtenue = i2s(self.tl.t, self.fps)
        if abs(obtenue - self.D) > 0.5:
            conseil = ""
            if self.famille == "ouverture" and self.schema == "ouverture" and self.D < 30:
                conseil = "; under 30 s, the opening form (threshold, 5 s first shot, body, peak, landing) does not hold:" \
                          " use --schema transition_decor (11 to 31 s observed)"
            self.log("resulting duration %.1f s instead of the %.1f s requested%s" % (obtenue, self.D, conseil))
        fmt = self.projet.get("format") or {}
        lg, ht = fmt.get("largeur", 1920), fmt.get("hauteur", 1080)
        if lg <= ht:
            self.log("format %d × %d (%s, convention): no export reframes; reframe by hand every shot wider "
                     "than the sequence, on its subject, without bars (grammaire-montage.md § 9.2)" % (lg, ht, "1:1" if lg == ht else "vertical"))
        m = {
            "version": 1,
            "titre": self.projet.get("projet") or "TEST-montage",
            "famille": self.famille,
            "schema": self.schema,
            "duree_cible_s": round(self.D, 3),
            "duree_s": round(i2s(self.tl.t, self.fps), 3),
            "duree_img": self.tl.t,
            "format": {"largeur": (self.projet.get("format") or {}).get("largeur", 1920),
                       "hauteur": (self.projet.get("format") or {}).get("hauteur", 1080),
                       "fps": fps_affiche(self.fps), "tc_debut": self.args.tc_debut},
            "police": self.police,
            "couleurs": self.couleurs,
            "musique": self.poser_musique(),
            "plans": self.tl.plans,
            "paroles": self.tl.paroles,
            "marqueurs": self.tl.marqueurs,
            "controle": self.controle,
            "critique": pour_la_critique(self.famille, self.schema, self.rushes),
            "journal": self.journal,
        }
        return m

    def recaler_sync(self):
        """Sync shots: the source in point is recomputed in frames from the speech running under it (lips to the frame)."""
        rid = {r.id: r for r in self.rushes}
        for p in self.tl.plans:
            if not p.get("sync"):
                continue
            r = rid[p["source"]]
            maitre, decal = r.id, 0
            if r.synchro:
                maitre, decal = r.synchro.get("avec"), s2i(float(r.synchro.get("decalage_s", 0.0)), self.fps)
            q = next((q for q in self.tl.paroles if q["source"] == maitre
                      and q["debut_img"] <= p["debut_img"] < q["debut_img"] + q["duree_img"]), None)
            if q is None:
                q = next((q for q in self.tl.paroles if q["source"] == maitre
                          and q["debut_img"] < p["debut_img"] + p["duree_img"] <= q["debut_img"] + q["duree_img"]), None)
            if q is None:
                continue
            e = q["entree_img"] + (p["debut_img"] - q["debut_img"]) + decal
            if e < 0:
                continue
            p["entree_img"], p["sortie_img"] = e, e + p["duree_img"]
            p["entree_s"], p["sortie_s"] = round(i2s(e, self.fps), 3), round(i2s(e + p["duree_img"], self.fps), 3)

    def montrer_qui_parle(self):
        """Line: the shot that starts during the sentence shows the person saying it (sync picture).

        The sentence starts on another shot and runs over the cut (94 out of 108, observed)."""
        rid = {r.id: r for r in self.rushes}
        for q in self.tl.paroles:
            r = rid.get(q["source"])
            if r is None or not r.a_son or r.sujet in ("photo",):
                continue
            a, b = q["debut_img"], q["debut_img"] + q["duree_img"]
            for p in self.tl.plans:
                if p["type"] != "image" or p["debut_img"] <= a or p["debut_img"] >= b - s2i(0.4, self.fps):
                    continue
                if p["source"] == r.id:
                    break
                e = q["entree_img"] + (p["debut_img"] - a)
                lo = s2i(min(w[0] for w in r.prises), self.fps)
                hi = s2i(max(w[1] for w in r.prises), self.fps)
                if e < lo or e + p["duree_img"] > hi:
                    continue
                p.update({"source": r.id, "chemin": r.chemin, "entree_img": e, "sortie_img": e + p["duree_img"],
                          "entree_s": round(i2s(e, self.fps), 3), "sortie_s": round(i2s(e + p["duree_img"], self.fps), 3),
                          "valeur": r.valeur, "sujet": r.sujet, "mouvement": r.mouvement, "sync": True,
                          "notes": "the person speaking, in sync picture; the sentence started on the previous shot (94 out of 108)"})
                break

    def verifier_marges(self):
        """Dissolves between two pictures: each clip needs duree/2 of handle; otherwise shorten it or cut."""
        P = self.tl.plans
        rid = {r.id: r for r in self.rushes}
        for i, p in enumerate(P):
            t = p.get("transition") or {}
            if t.get("type") in ("fondu", "blanc", "poussee"):
                d_img = s2i(t.get("duree", 0.5), self.fps)
                t["duree_img"] = d_img
                if i > 0 and P[i - 1]["type"] == "image" and p["type"] == "image":
                    a, b = rid[P[i - 1]["source"]], rid[p["source"]]
                    apres = (s2i(max(w[1] for w in a.prises) if not a.fixe else 1e5, self.fps) - P[i - 1]["sortie_img"])
                    avant = p["entree_img"] - (0 if b.fixe else s2i(min(w[0] for w in b.prises), self.fps))
                    marge = 2 * min(apres, avant)
                    if marge < d_img:
                        if marge >= 2:
                            t["duree_img"] = marge
                            self.log("shot %d: dissolve shortened to %d frames for lack of handles in the footage" % (p["n"], marge))
                        else:
                            p["transition"] = {"type": "coupe"}
                            self.log("shot %d: dissolve replaced by a cut, no handles in the footage" % p["n"])
                            continue
                elif p["type"] == "noir" and i > 0:
                    t["duree_img"] = min(d_img, P[i - 1]["duree_img"])
                else:
                    t["duree_img"] = min(d_img, p["duree_img"])
                t["duree"] = round(i2s(t["duree_img"], self.fps), 3)


def tableau(m):
    lignes = ["", "%s · %s (%s) · %.2f s · %s fps" % (m["titre"], m["famille"], m["schema"], m["duree_s"], m["format"]["fps"]),
              "", " n  section        start   length shot                         in→out            transition   title card"]
    for p in m["plans"]:
        if p["type"] == "image":
            quoi = "%s %s/%s" % (p["source"], p.get("valeur") or "?", p.get("sujet") or "?")
            es = "%6.2f→%6.2f" % (p["entree_s"], p["sortie_s"])
        else:
            quoi = p["type"]
            es = ""
        t = p["transition"]["type"] + ("" if p["transition"]["type"] == "coupe" else " %.2f" % p["transition"].get("duree", 0))
        c = p.get("carton")
        ct = ("%s \"%s\"" % (c["role"], (c.get("texte") or "logo")[:24])) if c else ""
        lignes.append("%3d  %-13s %6.2f  %6.2f  %-28s %-16s  %-11s  %s" % (p["n"], p["temps"][:13], p["debut_s"], p["duree_s"],
                                                                            quoi[:28], es, t, ct))
    if m["paroles"]:
        lignes += ["", "Speech (A1):"]
        for q in m["paroles"]:
            lignes.append("  %2d  %6.2f → %6.2f  %s  %s" % (q["n"], q["debut_s"], q["debut_s"] + q["duree_s"], q.get("personne") or q["source"],
                                                           (q.get("texte") or "")[:50]))
    if m["musique"]:
        lignes += ["", "Music (A2): %s, %.2f s, level %s dB" % (os.path.basename(m["musique"]["chemin"]),
                                                               m["musique"]["duree_img"] / float(fps_fraction(m["format"]["fps"])),
                                                               m["musique"]["niveau_db"])]
    lignes += ["", "Check:"]
    for c in m["controle"]:
        etat = "ok " if c["ok"] else ("DEVIATION" if c["ok"] is False else "info")
        lignes.append("  %s %-32s %-8s target %-14s (%s)" % (etat, c["id"], c["mesure"], c["cible"], c["base"]))
    if m["journal"]:
        lignes += ["", "Journal:"] + ["  - " + j for j in m["journal"]]
    return "\n".join(lignes)


class _Arguments(argparse.ArgumentParser):
    """A usage error exits with code 1 (nothing is written), not 2: 2 means "timeline produced with deviations"."""
    def error(self, message):
        self.print_usage(sys.stderr)
        self.exit(1, "%s: error: %s\n" % (self.prog, message))


def main(argv=None):
    ap = _Arguments(description="rushes.json → montage.json")
    ap.add_argument("rushes", nargs="?")
    ap.add_argument("--famille", help="produit, ouverture, documentaire, bande_annonce (aliases: bandeannonce, produit_revelation…)")
    ap.add_argument("--schema")
    ap.add_argument("--duree", type=float)
    ap.add_argument("--musique", help="audio file, or \"aucune\" to ignore the one in rushes.json")
    ap.add_argument("--fps")
    ap.add_argument("--tc-debut", default="00:00:00:00")
    ap.add_argument("--sortie")
    ap.add_argument("--gabarits", default=os.path.join(ICI, "gabarits.json"))
    ap.add_argument("--reperes", action="store_true", help="measure the music only")
    ap.add_argument("--verifier-gabarits", action="store_true",
                    help="compare gabarits.json with the measured targets (references/cibles) and stop")
    ap.add_argument("--muet", action="store_true", help="do not print the table")
    a = ap.parse_args(argv)
    if a.verifier_gabarits:
        n, lignes = verifier_gabarits(lire_json(a.gabarits), os.path.join(os.path.dirname(ICI), "references", "cibles"))
        print("\n".join(lignes))
        print("%d deviation(s) between gabarits.json and the targets" % n)
        return 2 if n else 0
    if a.reperes:
        if not a.musique:
            ap.error("--reperes requires --musique")
        print(json.dumps(analyser_musique(a.musique), ensure_ascii=False, indent=1))
        return 0
    if not a.rushes or not a.famille:
        ap.error("rushes.json and --famille are required")
    if a.duree is not None and not a.duree > 0:
        ap.error("--duree %s: a duration in seconds, greater than 0" % a.duree)
    if a.fps is not None:
        try:
            f = fps_fraction(a.fps)
        except (ValueError, ZeroDivisionError):
            f = None
        if f not in FPS_ADMIS:
            ap.error("--fps %s: 23.976, 24, 25, 29.97, 30, 50, 59.94 or 60 (montage-spec.md § 2)" % a.fps)
    tc0 = re.match(r"^\d{2}:[0-5]\d:[0-5]\d[:;](\d{2})$", a.tc_debut or "")
    if not tc0:
        ap.error("--tc-debut %s: expected HH:MM:SS:FF, for example 00:00:00:00 or 01:00:00:00" % a.tc_debut)
    a.famille = ALIAS_FAMILLE.get(a.famille.lower().replace("-", "_"), a.famille.lower())
    if a.famille not in FAMILLES:
        ap.error("unknown family: %s (choices: %s)" % (a.famille, ", ".join(sorted(FAMILLES))))
    gab = lire_json(a.gabarits)
    if a.schema is None:
        a.schema = None
    try:
        projet, rushes, base = charger_rushes(a.rushes, g_v(gab["communs"]["marge_prise_s"]))
    except (OSError, ValueError) as e:
        print("rushes.json unreadable: %s" % e, file=sys.stderr)
        return 1
    except KeyError as e:
        print("rushes.json unreadable: field \"%s\" missing" % e.args[0], file=sys.stderr)
        return 1
    except (TypeError, AttributeError) as e:
        print("rushes.json unreadable: a field does not have the expected type (montage-spec.md § 1): %s" % e, file=sys.stderr)
        return 1
    if not rushes:
        print("no clips in %s" % a.rushes)
        return 1
    manquants = [r.id for r in rushes if r.absent]
    if a.schema is None:
        a.schema = choisir_schema(a.famille, rushes)
    a.schema = ALIAS_SCHEMA.get(a.schema, a.schema)
    if a.schema not in FAMILLES[a.famille]:
        print("unknown schema for %s: %s (choices: %s)" % (a.famille, a.schema, ", ".join(FAMILLES[a.famille])))
        return 1
    asm = Assembleur(a, gab, projet, rushes, base)
    if int(tc0.group(1)) >= timebase(asm.fps)[0]:
        ap.error("--tc-debut %s: at %s fps, frames run from 00 to %02d"
                 % (a.tc_debut, fps_affiche(asm.fps), timebase(asm.fps)[0] - 1))
    for x in projet.get("_avertissements", []):
        asm.log(x)
    if manquants:
        asm.log("clips not found, left out: %s" % ", ".join(manquants))
    m = asm.construire()
    fautes = verifier_montage(m)
    if fautes:
        m["journal"] += ["INCONSISTENCY: " + f for f in fautes]
    for c in m["controle"]:
        if c["ok"] is False:
            m["journal"].append("DEVIATION %s: %s, outside the target %s (%s); %s"
                                % (c["id"], c["mesure"], c["cible"], c["statut"], c["base"]))
    sortie = a.sortie or os.path.join(os.path.dirname(os.path.abspath(a.rushes)), "montage.json")
    ecrire_json(sortie, m)
    ecrire_json(os.path.splitext(sortie)[0] + ".annotations.json", annotations_critique(m))
    if not a.muet:
        print(tableau(m))
    cq = m["critique"]
    print("\nmontage.json: %s" % sortie)
    q = shlex.quote
    mus = (m.get("musique") or {}).get("chemin")
    print("review of the raw export ($PY = the Python that has numpy and Pillow):\n  $PY %s %s --famille %s --sous-famille %s%s"
          " --annotations %s --mesurer-medias%s"
          % (q(os.path.join(ICI, "critique_montage.py")), q(os.path.splitext(sortie)[0] + ".xml"), cq["famille"], cq["sous_famille"],
             (" --schema " + cq["schema"]) if cq.get("schema") else "", q(os.path.splitext(sortie)[0] + ".annotations.json"),
             (" --son %s --son-debut %.3f" % (q(mus), i2s(m["musique"].get("entree_img") or 0, m["format"]["fps"])))
             if mus and not m["musique"].get("debut_img") else ""))
    ecarts = [c for c in m["controle"] if c["ok"] is False]
    return 2 if (ecarts or fautes) else 0


def verifier_gabarits(gab, dossier_cibles):
    """Compares each value in gabarits.json with its source in references/cibles/<famille>.json ("src" field).

    Only reads sources of the form "famille dotted.path"; the others are reported as not checkable."""
    cibles, lignes, ecarts = {}, [], 0
    for f in ("produit", "ouverture", "documentaire", "bandeannonce"):
        ch = os.path.join(dossier_cibles, f + ".json")
        if os.path.exists(ch):
            cibles[f] = lire_json(ch)

    def resoudre(src):
        parts = src.split(" ", 1)
        if len(parts) != 2 or parts[0] not in cibles or "/" in parts[1] or "[" in parts[1]:
            return None, False
        x = cibles[parts[0]]
        for k in parts[1].strip().split("."):
            if isinstance(x, dict) and k in x:
                x = x[k]
            elif isinstance(x, list) and k.isdigit() and int(k) < len(x):
                x = x[int(k)]
            else:
                return None, True
        return x, True

    def entrees(d, prefixe=""):
        for k, v in d.items():
            if isinstance(v, dict) and "src" in v:
                yield prefixe + k, v
            elif isinstance(v, dict):
                for x in entrees(v, prefixe + k + "."):
                    yield x
    for nom, e in entrees(gab):
        src_val, lisible = resoudre(e["src"])
        if not lisible:
            lignes.append("  ·  %-45s source not checkable: %s" % (nom, e["src"]))
            continue
        if src_val is None:
            lignes.append("  ?  %-45s source not found: %s" % (nom, e["src"]))
            ecarts += 1
            continue
        v, plage = e.get("v"), e.get("plage")
        if e.get("derive"):
            lignes.append("  ok %-45s v=%s derived: %s" % (nom, v, e["derive"]))
            continue
        ref = src_val.get("mediane", src_val.get("valeur")) if isinstance(src_val, dict) else src_val
        ok = True
        if isinstance(v, (int, float)) and isinstance(ref, (int, float)) and e.get("statut") == "observe":
            ok = abs(v - ref) <= max(0.02 * abs(ref), 0.011)
        if ok and plage and isinstance(src_val, dict) and "min" in src_val and "max" in src_val and e.get("statut") == "observe":
            ok = abs(plage[0] - src_val["min"]) <= 0.011 * max(1, abs(src_val["min"])) or "cible" in src_val or "quartiles" in src_val
        lignes.append("  %s %-45s v=%s source=%s" % ("ok" if ok else "≠ ", nom, v, json.dumps(src_val, ensure_ascii=False)[:90]))
        ecarts += 0 if ok else 1
    return ecarts, lignes


TYPES_TEXTE = {"nom": "nom", "titre": "nom", "phrase": "phrase", "these": "these", "bandeau": "bandeau",
               "titre_bloc": "titre_bloc", "mot_choc": "mot", "credit": "carton", "mention": "carton", "logo": "logo"}


def annotations_critique(m):
    """Annotations in the critique_montage.py format (--annotations), drawn from what the edit already knows:
    size and type of each shot, reveal, name, closing, texts. They hold for the raw export of this edit;
    after changes in the editing software, redo them by eye."""
    fps = fps_fraction(m["format"]["fps"])
    P = m["plans"]
    a = {"sous_famille": m["critique"].get("sous_famille")}
    if m["critique"].get("schema"):
        a["schema"] = m["critique"]["schema"]
    rev = next((p for p in P if p["temps"] == "revelation" and p.get("valeur") == "entier"), None)
    if rev and m["critique"].get("schema") == "tardif":
        a["revelation"] = round(rev["debut_s"], 3)
    ferm = next((p for p in P if p["temps"] == "fermeture"), None)
    if ferm and m["famille"] == "bande_annonce":
        a["fermeture"] = round(ferm["debut_s"], 3)
    pts, textes = [], []
    for p in P:
        milieu = round(i2s(p["debut_img"] + p["duree_img"] / 2.0, fps), 3)
        if p["type"] == "image":
            sujet = p.get("sujet")
            typ = {"entretien": "entretien", "personne": "personne", "illustration": "illustration",
                   "objet": "objet", "ecran": "objet"}.get(sujet, "image")
            x = {"t": milieu, "type": typ, "objet": sujet in ("objet", "ecran", "piece"), "visage": sujet in ("entretien", "personne")}
            if p.get("valeur"):
                x["valeur"] = p["valeur"]
            if p.get("personne"):
                x["personne"] = p["personne"]
            pts.append(x)
        elif p["type"] == "noir":
            pts.append({"t": milieu, "valeur": "noir", "type": "noir"})
        c = p.get("carton")
        if c:
            d = i2s(p["debut_img"] + int(c.get("debut_img") or 0), fps)
            f = d + i2s(int(c.get("duree_img") or p["duree_img"]), fps)
            t = {"type": TYPES_TEXTE.get(c.get("role"), "carton"), "debut": round(d, 3), "fin": round(f, 3),
                 "mots": len((c.get("texte") or "").split()), "boite": False}
            if c.get("place") == "centre":
                t["place"] = "centre"
            textes.append(t)
            if c.get("role") in ("nom", "titre") and "nom" not in a:
                a["nom"] = [round(d, 3), round(f, 3)]
            if p["type"] == "carton":
                pts.append({"t": milieu, "valeur": "texte", "type": "logo" if c.get("logo") else "carton"})
    a["plans_par_temps"] = pts
    a["textes"] = textes
    return a


def choisir_schema(famille, rushes):
    """The default schema from the footage (convention, see montage-spec.md § 2.6)."""
    if famille == "produit":
        return "objet_des_le_debut" if any(r.sujet == "ecran" for r in rushes) and not any("revelation" in r.role for r in rushes) else "revelation_tardive"
    if famille == "ouverture":
        return "ouverture"
    if famille == "documentaire":
        personnes = set(r.personne for r in rushes if r.paroles and r.personne)
        prises = [p["sortie_s"] - p["entree_s"] for r in rushes for p in r.paroles]
        return "choral" if len(personnes) >= 4 or (prises and mediane(prises) < 4.0) else "pose"
    if famille == "bande_annonce":
        if any(r.bloc is not None for r in rushes):
            return "catalogue_blocs" if any(r.titre_bloc for r in rushes) else "catalogue_mele"
        if any(r.sujet == "objet" for r in rushes) and any(r.sujet == "personne" for r in rushes) and not any(r.paroles for r in rushes):
            return "usage"
        return "oeuvre"
    return None


if __name__ == "__main__":
    sys.exit(main())
