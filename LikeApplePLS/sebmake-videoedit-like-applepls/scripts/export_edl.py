#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""export_edl.py : montage.json → EDL CMX3600, le format le plus ancien et le plus lu (Premiere Pro, DaVinci Resolve,
FilmCraft, et la plupart des autres logiciels de montage). Python 3.9, bibliothèque standard.

Usage :
    python3 export_edl.py montage.json [-o montage.edl] [--sans-audio] [--verifier]

Ce que porte l'EDL : une seule piste vidéo (V1), les noirs (bobine BL), les fondus (D + durée en images),
le passage au blanc (D + commentaire), les paroles (A), la musique (A2), le son des images (A3, si demandé).
Ce qu'elle ne porte pas : les cartons (écrits en commentaires « * CARTON »), la poussée (écrite en coupe
+ commentaire), le niveau de la musique, les marqueurs (en commentaires « * MARQUEUR »).
Bobine : l'identifiant du rush, 8 caractères au plus ; le fichier est donné par « * FROM CLIP NAME » et
« * SOURCE FILE ». Le timecode source part du timecode inscrit dans le fichier (00:00:00:00 s'il n'y en a pas).
Cadences NTSC (23,976, 29,97) : timecode non drop-frame compté à 24 ou 30 images, comme le font les logiciels.

--verifier : relit l'EDL écrite (lecture indépendante) et retrouve chaque plan : point de montage, entrée source,
             fondus ; puis, si lire_timeline.py est là, compare la lecture de la critique.
Codes de sortie : 0 succès ; 1 montage incohérent ; 3 vérification en échec.
"""
import argparse
import os
import re
import sys

ICI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ICI)
from commun import charger_montage, fps_fraction, verifier_sources, tc, tc_fichier, tc_vers_images, timebase  # noqa: E402


def bobine(ident, prises):
    b = re.sub(r"[^A-Za-z0-9_]", "", str(ident)).upper()[:8] or "AX"
    k = 2
    base = b
    while b in prises.values() and prises.get(ident) != b:
        suf = str(k)
        b = base[:8 - len(suf)] + suf
        k += 1
    prises[ident] = b
    return b


class EDL:
    def __init__(self, m):
        self.m = m
        self.fps = fps_fraction(m["format"]["fps"])
        self.rec0 = tc_vers_images(m["format"].get("tc_debut") or "00:00:00:00", self.fps)
        self.n = 0
        self.lignes = []
        self.bobines = {}
        self.tc_src = {}

    def src0(self, chemin):
        if chemin not in self.tc_src:
            self.tc_src[chemin] = tc_vers_images(tc_fichier(chemin, self.fps), self.fps)
        return self.tc_src[chemin]

    def tcs(self, n):
        return tc(n, self.fps)

    def ev(self, reel, piste, typ, si, so, ri, ro, duree=None):
        champ = "%-4s" % typ if not duree else "%-4s %03d" % (typ, duree)
        return "%03d  %-8s %-5s %-8s %s %s %s %s" % (self.n, reel, piste, champ, self.tcs(si), self.tcs(so),
                                                    self.tcs(ri + self.rec0), self.tcs(ro + self.rec0))

    def commentaires(self, p, vers=False):
        out = []
        if p is not None and p.get("chemin"):
            out.append("* %s CLIP NAME: %s" % ("TO" if vers else "FROM", os.path.basename(p["chemin"])))
            out.append("* SOURCE FILE: %s" % os.path.abspath(p["chemin"]))
        return out

    def ecrire(self, avec_audio=True):
        m, P = self.m, self.m["plans"]
        L = ["TITLE: %s" % m["titre"][:70], "FCM: NON-DROP FRAME", ""]
        base, ntsc = timebase(self.fps)
        L.insert(2, "* CADENCE: %s IMAGES/S%s" % (m["format"]["fps"], " (NTSC, TIMECODE COMPTE A %d)" % base if ntsc else ""))
        # fin effective de chaque plan sur V1 (un fondu centré ou au noir avance la fin de l'événement)
        for i, p in enumerate(P):
            t = p.get("transition") or {}
            typ = t.get("type", "coupe")
            d = int(t.get("duree_img") or 0)
            prev = P[i - 1] if i > 0 else None
            nxt = P[i + 1] if i + 1 < len(P) else None
            a, b = p["debut_img"], p["debut_img"] + p["duree_img"]
            # ce plan finit plus tôt si le suivant entre par un fondu centré, ou si un fondu au noir le suit
            fin = b
            tn = (nxt or {}).get("transition") or {}
            dn = int(tn.get("duree_img") or 0)
            if nxt is not None and tn.get("type") in ("fondu", "blanc") and dn:
                if nxt["type"] == "image" and p["type"] == "image":
                    fin = b - dn // 2
                elif nxt["type"] != "image" and p["type"] == "image":
                    fin = b - dn
            self.n += 1
            reel = "BL" if p["type"] != "image" else bobine(p["source"], self.bobines)
            src_a = (self.src0(p["chemin"]) + p["entree_img"]) if p["type"] == "image" else 0
            if typ in ("fondu", "blanc") and d and prev is not None and (p["type"] == "image" or prev["type"] == "image"):
                # l'événement commence au début du fondu ; ligne « de » (plan d'avant, durée nulle), puis « vers »
                if prev["type"] == "image" and p["type"] == "image":
                    debut = a - d // 2
                elif p["type"] == "image":
                    debut = a  # sortie du noir : le fondu est dans les premières images du plan
                else:
                    debut = a - d  # départ au noir : le fondu est dans les dernières images du plan d'avant
                if prev["type"] == "image":
                    pr = bobine(prev["source"], self.bobines)
                    s_prev = self.src0(prev["chemin"]) + prev["entree_img"] + (debut - prev["debut_img"])
                    L.append(self.ev(pr, "V", "C", s_prev, s_prev, debut, debut))
                else:
                    L.append(self.ev("BL", "V", "C", 0, 0, debut, debut))
                s_in = src_a - (a - debut) if p["type"] == "image" else 0
                L.append(self.ev(reel, "V", "D", s_in, s_in + (fin - debut), debut, fin, duree=d))
                L += self.commentaires(prev if prev["type"] == "image" else None)
                L += self.commentaires(p if p["type"] == "image" else None, vers=True)
                if typ == "blanc":
                    L.append("* EFFECT NAME: DIP TO WHITE")
                else:
                    L.append("* EFFECT NAME: CROSS DISSOLVE")
            else:
                L.append(self.ev(reel, "V", "C", src_a, src_a + (fin - a), a, fin))
                L += self.commentaires(p if p["type"] == "image" else None)
                if typ == "poussee":
                    L.append("* EFFET A REFAIRE : POUSSEE (PUSH) DE %d IMAGES" % d)
            c = p.get("carton")
            if c:
                ca = a + int(c.get("debut_img") or 0)
                cb = ca + int(c.get("duree_img") or p["duree_img"])
                L.append("* CARTON (%s, %s, fond %s) %s-%s : %s" % (c.get("role"), c.get("place"), c.get("fond"),
                                                                 self.tcs(ca + self.rec0), self.tcs(cb + self.rec0),
                                                                 (" · ".join(x for x in (c.get("texte"), c.get("deuxieme_ligne")) if x)
                                                                  or c.get("logo") or "").replace("\n", " ")))
            L.append("")
        if avec_audio:
            for q in m.get("paroles", []):
                self.n += 1
                s = self.src0(q["chemin"]) + q["entree_img"]
                L.append(self.ev(bobine(q["source"], self.bobines), "A", "C", s, s + q["duree_img"], q["debut_img"],
                                 q["debut_img"] + q["duree_img"]))
                L += ["* FROM CLIP NAME: %s" % os.path.basename(q["chemin"]), "* SOURCE FILE: %s" % os.path.abspath(q["chemin"]), ""]
            mus = m.get("musique")
            if mus:
                self.n += 1
                s = self.src0(mus["chemin"]) + mus["entree_img"]
                L.append(self.ev("MUSIQUE", "A2", "C", s, s + mus["duree_img"], mus["debut_img"], mus["debut_img"] + mus["duree_img"]))
                L += ["* FROM CLIP NAME: %s" % os.path.basename(mus["chemin"]), "* SOURCE FILE: %s" % os.path.abspath(mus["chemin"])]
                if mus.get("niveau_db"):
                    L.append("* NIVEAU A REGLER : %s DB" % mus["niveau_db"])
                if mus.get("fondu_sortie_img"):
                    L.append("* FONDU DE SORTIE A FAIRE : %d IMAGES" % mus["fondu_sortie_img"])
                L.append("")
            for p in P:
                if p["type"] == "image" and p.get("son_image"):
                    self.n += 1
                    s = self.src0(p["chemin"]) + p["entree_img"]
                    L.append(self.ev(bobine(p["source"], self.bobines), "A3", "C", s, s + p["duree_img"], p["debut_img"],
                                     p["debut_img"] + p["duree_img"]))
                    L += self.commentaires(p) + [""]
        for mk in m.get("marqueurs", []):
            L.append("* MARQUEUR %s : %s %s" % (self.tcs(mk["debut_img"] + self.rec0), mk.get("nom") or "", mk.get("texte") or ""))
        return "\n".join(L).rstrip() + "\n"


# ---------------------------------------------------------------- vérification

LIGNE = re.compile(r"^(\d{3})\s+(\S+)\s+(\S+)\s+(C|D)\s*(\d{3})?\s+(\S+) (\S+) (\S+) (\S+)\s*$")


def relire(chemin, fps):
    evs, cur = [], None
    for ligne in open(chemin, encoding="utf-8"):
        x = LIGNE.match(ligne.rstrip("\n"))
        if x:
            n, reel, piste, typ, dur, si, so, ri, ro = x.groups()
            cur = {"n": int(n), "reel": reel, "piste": piste, "typ": typ, "dur": int(dur or 0),
                   "si": tc_vers_images(si, fps), "so": tc_vers_images(so, fps), "ri": tc_vers_images(ri, fps),
                   "ro": tc_vers_images(ro, fps), "fichier": None}
            evs.append(cur)
        elif cur is not None and ligne.startswith("* SOURCE FILE:"):
            cur["fichier"] = ligne.split(":", 1)[1].strip()
    return evs


def verifier(chemin, m):
    fps = fps_fraction(m["format"]["fps"])
    rec0 = tc_vers_images(m["format"].get("tc_debut") or "00:00:00:00", fps)
    evs = relire(chemin, fps)
    ecarts = []
    v = [e for e in evs if e["piste"] == "V"]
    # reconstruire les plans : un événement de durée nulle est la ligne « de » d'un fondu
    plans = []
    for e in v:
        if e["ro"] == e["ri"]:
            continue
        coupe = e["ri"] - rec0
        if e["typ"] == "D":
            prev_bl = plans and plans[-1]["reel"] == "BL"
            if e["reel"] == "BL":
                coupe = e["ri"] - rec0 + e["dur"]  # départ au noir : le noir commence à la fin du fondu
            elif not prev_bl:
                coupe = e["ri"] - rec0 + e["dur"] // 2  # fondu centré
            if plans:
                plans[-1]["fin"] = coupe
        plans.append({"reel": e["reel"], "debut": coupe, "fin": e["ro"] - rec0, "src": e["si"] + (coupe - (e["ri"] - rec0)),
                      "fichier": e["fichier"], "typ": e["typ"], "dur": e["dur"]})
    # les noirs et cartons consécutifs du montage forment un seul trou ; on compare les images
    images = [p for p in m["plans"] if p["type"] == "image"]
    vus = [p for p in plans if p["reel"] != "BL"]
    if len(vus) != len(images):
        ecarts.append("V : %d plans d'image relus, %d dans le montage" % (len(vus), len(images)))
    t_src = {}
    for x, p in zip(vus, images):
        if p["chemin"] not in t_src:
            t_src[p["chemin"]] = tc_vers_images(tc_fichier(p["chemin"], fps), fps)
        att = (p["debut_img"], p["debut_img"] + p["duree_img"], t_src[p["chemin"]] + p["entree_img"])
        if (x["debut"], x["fin"], x["src"]) != att:
            ecarts.append("plan %d : EDL (%d, %d, src %d) ≠ montage %s" % (p["n"], x["debut"], x["fin"], x["src"], att))
        if x["fichier"] != os.path.abspath(p["chemin"]):
            ecarts.append("plan %d : fichier %s" % (p["n"], x["fichier"]))
    fin_edl = max((e["ro"] - rec0 for e in v), default=0)
    if fin_edl != m["duree_img"]:
        ecarts.append("fin de l'EDL %d ≠ durée du montage %d" % (fin_edl, m["duree_img"]))
    a = [e for e in evs if e["piste"] == "A"]
    if len(a) != len(m.get("paroles", [])):
        ecarts.append("A : %d paroles relues, %d attendues" % (len(a), len(m.get("paroles", []))))
    for e, q in zip(a, m.get("paroles", [])):
        if (e["ri"] - rec0, e["ro"] - rec0) != (q["debut_img"], q["debut_img"] + q["duree_img"]):
            ecarts.append("parole %d : position" % q["n"])
    return ecarts


def comparer_lecture_critique(chemin, m):
    try:
        import lire_timeline
    except ImportError:
        return None, []
    fps = float(fps_fraction(m["format"]["fps"]))
    lu = lire_timeline.lire_edl(chemin, round(fps))  # le format est connu : ne pas le déduire de l'extension de -o
    ecarts = []
    vus = [x for x in lu["plans"] if x["type"] == "image"]
    images = [p for p in m["plans"] if p["type"] == "image"]
    base, _ = timebase(fps_fraction(m["format"]["fps"]))
    if len(vus) != len(images):
        ecarts.append("lecture critique : %d plans d'image, %d dans le montage" % (len(vus), len(images)))
    for x, p in zip(vus, images):
        # la critique lit l'EDL à la cadence entière du timecode
        d, f = p["debut_img"] / float(base), (p["debut_img"] + p["duree_img"]) / float(base)
        if abs(x["debut"] - d) > 0.6 / base or abs(x["fin"] - f) > 0.6 / base:
            ecarts.append("lecture critique, plan %d : %.3f-%.3f ≠ %.3f-%.3f" % (p["n"], x["debut"], x["fin"], d, f))
        # l'entrée que la critique mesure dans le fichier (--mesurer-medias) : timecode source moins timecode du fichier
        e = lire_timeline.entree_dans_fichier(x, lu)
        if e is not None and abs(e * lu["fps"] - p["entree_img"]) > 0.6:
            ecarts.append("lecture critique, plan %d : entrée dans le fichier %.0f images ≠ %d" % (p["n"], e * lu["fps"], p["entree_img"]))
    return lu, ecarts


def main(argv=None):
    ap = argparse.ArgumentParser(description="montage.json → EDL CMX3600")
    ap.add_argument("montage")
    ap.add_argument("-o", "--sortie")
    ap.add_argument("--sans-audio", action="store_true")
    ap.add_argument("--verifier", action="store_true")
    a = ap.parse_args(argv)
    m, fautes = charger_montage(a.montage)
    absents = []
    if not fautes:
        fautes, absents = verifier_sources(m)
    if fautes:
        print("montage incohérent :\n  " + "\n  ".join(fautes))
        return 1
    sortie = a.sortie or os.path.splitext(os.path.abspath(a.montage))[0] + ".edl"
    if os.path.splitext(sortie)[1].lower() != ".edl":
        print("  attention : %s ne finit pas par .edl ; la critique et les logiciels de montage la reconnaîtront mieux en .edl"
              % os.path.basename(sortie))
    e = EDL(m)
    try:
        texte = e.ecrire(avec_audio=not a.sans_audio)
    except ValueError as x:
        print("montage incohérent :\n  %s" % x)
        return 1
    with open(sortie, "w", encoding="utf-8") as f:
        f.write(texte)
    print("EDL CMX3600 : %s (%d événements ; cartons en commentaires)" % (sortie, e.n))
    for x in absents:
        print("  attention : fichier introuvable (sera hors ligne) : %s" % x)
    if a.verifier:
        ecarts = verifier(sortie, m)
        lu, e2 = comparer_lecture_critique(sortie, m)
        ecarts += e2
        if ecarts:
            print("vérification : %d écart(s)\n  " % len(ecarts) + "\n  ".join(ecarts))
            return 3
        print("vérification : l'EDL relue colle au montage, image par image%s" % (" ; lecture de la critique d'accord" if lu else ""))
    return 0


if __name__ == "__main__":
    sys.exit(main())
