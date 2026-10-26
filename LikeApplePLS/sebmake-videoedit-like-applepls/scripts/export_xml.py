#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""export_xml.py : montage.json → XML Final Cut Pro 7 (« xmeml », version 4), à importer dans Premiere Pro
(Fichier > Importer) ou DaVinci Resolve (Fichier > Importer > Timeline). Python 3.9, bibliothèque standard.

Usage :
    python3 export_xml.py montage.json [-o montage.xml] [--cartons texte|png] [--verifier]

Pistes : V1 les plans, V2 les cartons ; A1 les paroles, A2 la musique, A3 le son des images (si demandé).
Cartons (chaque carton a aussi un marqueur de séquence qui porte son texte) :
    texte (défaut) : générateur « Text » du format FCP7 seulement pour un carton sur fond noir ; un texte posé
                     sur une image (bandeau, titre dans le décor) ou sur un fond de couleur n'est écrit qu'en
                     marqueur, à poser à la main. Raison : un importeur qui ne lit pas ce générateur le remplace
                     par de la vidéo noire (vu dans FilmCraft) ; sur fond noir, rien ne se voit ; sur une image, elle serait cachée.
    png            : une image PNG par carton (texte et fond déjà dessinés), posée sur V2 ; demande Pillow.
                     Les cartons sont alors des images : critique_montage.py les lira comme telles.
    generateurs    : le générateur « Text » partout (titres modifiables là où le logiciel les convertit ;
                     risque de vidéo noire sur les images, voir plus haut).
--verifier : relit le XML écrit et compare plans, transitions, paroles et musique au montage, image par image
             (et, si lire_timeline.py est là, la lecture indépendante de la critique). Code 0 si tout colle.

Ce que le format ne garantit pas : la conversion des générateurs de texte, la taille et la place exactes du texte,
le nom des transitions autres que Cross Dissolve. À vérifier à l'œil après import. Premiere Pro et Resolve n'étaient
pas installés là où ce script a été écrit : il est testé par relecture et par import dans FilmCraft.
Codes de sortie : 0 succès ; 1 montage incohérent ; 3 vérification en échec.
"""
import argparse
import os
import sys
import xml.etree.ElementTree as ET
from urllib.parse import quote, unquote, urlparse

ICI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ICI)
from commun import (charger_montage, verifier_sources, fps_fraction, i2s, i2ticks, sonder, tc, tc_fichier,  # noqa: E402
                    tc_vers_images, timebase)

EFFETS = {
    "fondu": ("Cross Dissolve", "Cross Dissolve", "Dissolve"),
    "noir": ("Cross Dissolve", "Cross Dissolve", "Dissolve"),
    "blanc": ("Dip to White", "Dip to White", "Dissolve"),
    "poussee": ("Push", "Push", "Slide"),
}
PLACES = {"centre": (0.0, 0.0), "bas_gauche": (-0.32, 0.36), "bas_droite": (0.32, 0.36), "haut_gauche": (-0.32, -0.36)}


def sous(parent, tag, texte=None, **attr):
    e = ET.SubElement(parent, tag, attr)
    if texte is not None:
        e.text = str(texte)
    return e


def rate(parent, fps):
    base, ntsc = timebase(fps)
    r = sous(parent, "rate")
    sous(r, "timebase", base)
    sous(r, "ntsc", "TRUE" if ntsc else "FALSE")
    return r


def timecode(parent, fps, chaine):
    t = sous(parent, "timecode")
    rate(t, fps)
    sous(t, "string", chaine)
    sous(t, "frame", tc_vers_images(chaine, fps))
    sous(t, "displayformat", "NDF")
    return t


def url(chemin):
    return "file://localhost" + quote(os.path.abspath(chemin), safe="/")


def couleur(parent, hexa, alpha=255):
    h = (hexa or "#FFFFFF").lstrip("#")
    v = sous(parent, "value")
    sous(v, "alpha", alpha)
    sous(v, "red", int(h[0:2], 16))
    sous(v, "green", int(h[2:4], 16))
    sous(v, "blue", int(h[4:6], 16))
    return v


def param(effet, pid, nom, valeur=None, vmin=None, vmax=None):
    p = sous(effet, "parameter")
    sous(p, "parameterid", pid)
    sous(p, "name", nom)
    if vmin is not None:
        sous(p, "valuemin", vmin)
        sous(p, "valuemax", vmax)
    if valeur is not None:
        sous(p, "value", valeur)
    return p


class Ecrivain:
    def __init__(self, m, base_json, mode_cartons, sortie):
        self.m = m
        self.fps = fps_fraction(m["format"]["fps"])
        self.base = base_json
        self.mode = mode_cartons
        self.sortie = sortie
        self.fichiers = {}  # chemin → id
        self.n_clip = 0
        self.avert = []
        self.a_poser = []
        self.police_png = None

    # -- fichiers sources
    def ref_fichier(self, parent, chemin, audio_seul=False):
        if chemin in self.fichiers:
            sous(parent, "file", id=self.fichiers[chemin])
            return
        fid = "file-%d" % (len(self.fichiers) + 1)
        self.fichiers[chemin] = fid
        info = sonder(chemin)
        if info.get("absent"):
            self.avert.append("fichier introuvable (sera hors ligne) : %s" % chemin)
        f = sous(parent, "file", id=fid)
        sous(f, "name", os.path.basename(chemin))
        sous(f, "pathurl", url(chemin))
        fps_src = info.get("fps") or self.fps
        rate(f, fps_src)
        if info.get("duree_s"):
            sous(f, "duration", int(round(info["duree_s"] * float(fps_src))))
        timecode(f, fps_src, tc_fichier(chemin, fps_src))
        media = sous(f, "media")
        if info.get("video") or info.get("fixe"):
            v = sous(media, "video")
            sc = sous(v, "samplecharacteristics")
            rate(sc, fps_src)
            sous(sc, "width", info.get("largeur") or self.m["format"]["largeur"])
            sous(sc, "height", info.get("hauteur") or self.m["format"]["hauteur"])
            sous(sc, "anamorphic", "FALSE")
            sous(sc, "pixelaspectratio", "square")
            sous(sc, "fielddominance", "none")
        if info.get("audio"):
            a = sous(media, "audio")
            sc = sous(a, "samplecharacteristics")
            sous(sc, "depth", 16)
            sous(sc, "samplerate", 48000)
            sous(a, "channelcount", info.get("canaux") or 2)

    def clipitem(self, piste, nom, chemin, debut, fin, entree, sortie, media="video", piste_source=1):
        self.n_clip += 1
        c = sous(piste, "clipitem", id="clipitem-%d" % self.n_clip)
        fid = self.fichiers.get(chemin) or "file-%d" % (len(self.fichiers) + 1)
        sous(c, "masterclipid", "masterclip-" + fid.split("-")[1])
        sous(c, "name", nom)
        sous(c, "enabled", "TRUE")
        sous(c, "duration", max(sortie, fin - debut + entree))
        rate(c, self.fps)
        sous(c, "start", debut)
        sous(c, "end", fin)
        sous(c, "in", entree)
        sous(c, "out", sortie)
        sous(c, "pproTicksIn", i2ticks(entree, self.fps))
        sous(c, "pproTicksOut", i2ticks(sortie, self.fps))
        self.ref_fichier(c, chemin)
        if media == "audio":
            st = sous(c, "sourcetrack")
            sous(st, "mediatype", "audio")
            sous(st, "trackindex", piste_source)
        return c

    def transition(self, piste, debut, fin, alignement, genre):
        nom, eid, cat = EFFETS.get(genre, EFFETS["fondu"])
        t = sous(piste, "transitionitem")
        rate(t, self.fps)
        sous(t, "start", debut)
        sous(t, "end", fin)
        sous(t, "alignment", alignement)
        e = sous(t, "effect")
        sous(e, "name", nom)
        sous(e, "effectid", eid)
        sous(e, "effectcategory", cat)
        sous(e, "effecttype", "transition")
        sous(e, "mediatype", "video")
        return t

    def transition_audio(self, piste, debut, fin, alignement):
        t = sous(piste, "transitionitem")
        rate(t, self.fps)
        sous(t, "start", debut)
        sous(t, "end", fin)
        sous(t, "alignment", alignement)
        e = sous(t, "effect")
        sous(e, "name", "Cross Fade (+3dB)")
        sous(e, "effectid", "KGAudioTransCrossFade3dB")
        sous(e, "effectcategory", "audiotransition")
        sous(e, "effecttype", "transition")
        sous(e, "mediatype", "audio")

    def generateur_texte(self, piste, carton, debut, fin):
        self.n_clip += 1
        g = sous(piste, "generatoritem", id="generatoritem-%d" % self.n_clip)
        texte = carton.get("texte") or ""
        if carton.get("deuxieme_ligne"):
            texte = texte + "\r" + carton["deuxieme_ligne"]
        sous(g, "name", (carton.get("texte") or "carton")[:60])
        sous(g, "enabled", "TRUE")
        sous(g, "duration", fin - debut)
        rate(g, self.fps)
        sous(g, "start", debut)
        sous(g, "end", fin)
        sous(g, "in", 0)
        sous(g, "out", fin - debut)
        sous(g, "anamorphic", "FALSE")
        sous(g, "alphatype", "black")
        e = sous(g, "effect")
        sous(e, "name", "Text")
        sous(e, "effectid", "Text")
        sous(e, "effectcategory", "Text")
        sous(e, "effecttype", "generator")
        sous(e, "mediatype", "video")
        param(e, "str", "Text", texte)
        police = (self.m.get("police") or {}).get("famille") or "Arial"   # repli courant, jamais une police Apple
        param(e, "fontname", "Font", police)
        # hauteur des capitales ≈ 0,7 × corps (convention) : corps = taille % × hauteur / 0,7
        corps = round(float(carton.get("taille_pct") or 4.5) / 100.0 * self.m["format"]["hauteur"] / 0.7)
        param(e, "fontsize", "Size", corps, 0, 1000)
        param(e, "fontstyle", "Style", 1, 1, 4)
        align = 2 if carton.get("place", "centre") == "centre" else (3 if carton.get("place", "").endswith("droite") else 1)
        param(e, "fontalign", "Alignment", align, 1, 3)
        p = param(e, "fontcolor", "Font Color")
        couleur(p, (self.m.get("couleurs") or {}).get("texte", "#FFFFFF"))
        h, v = PLACES.get(carton.get("place", "centre"), (0.0, 0.0))
        p = param(e, "origin", "Origin")
        val = sous(p, "value")
        sous(val, "horiz", h)
        sous(val, "vert", v)
        return g

    def generateur_couleur(self, piste, hexa, debut, fin):
        self.n_clip += 1
        g = sous(piste, "generatoritem", id="generatoritem-%d" % self.n_clip)
        sous(g, "name", "Color")
        sous(g, "enabled", "TRUE")
        sous(g, "duration", fin - debut)
        rate(g, self.fps)
        sous(g, "start", debut)
        sous(g, "end", fin)
        sous(g, "in", 0)
        sous(g, "out", fin - debut)
        e = sous(g, "effect")
        sous(e, "name", "Color")
        sous(e, "effectid", "Color")
        sous(e, "effectcategory", "Matte")
        sous(e, "effecttype", "generator")
        sous(e, "mediatype", "video")
        p = param(e, "fillcolor", "Color")
        couleur(p, hexa)
        return g

    def png_carton(self, carton, n, opaque):
        import cartons  # demande Pillow
        if self.police_png is None:
            chemin_police, av = cartons.choisir_police(self.m)
            self.police_png = chemin_police or "police par défaut de Pillow"
            if av:
                self.avert.append(av)
        dossier = os.path.splitext(self.sortie)[0] + "_cartons"
        os.makedirs(dossier, exist_ok=True)
        chemin = os.path.join(dossier, "carton-%02d-%s.png" % (n, carton.get("role", "texte")))
        fond = None
        if opaque:
            f = carton.get("fond")
            fond = {"noir": "#000000", "blanc": "#FFFFFF"}.get(f, f if (f or "").startswith("#") else "#000000")
        cartons.dessiner(chemin, carton, self.m, fond)
        return chemin

    # -- la séquence
    def ecrire(self):
        m, fps = self.m, self.fps
        racine = ET.Element("xmeml", version="4")
        seq = sous(racine, "sequence", id="sequence-1")
        sous(seq, "name", m["titre"])
        sous(seq, "duration", m["duree_img"])
        rate(seq, fps)
        timecode(seq, fps, m["format"].get("tc_debut") or "00:00:00:00")
        media = sous(seq, "media")
        video = sous(media, "video")
        fmt = sous(video, "format")
        sc = sous(fmt, "samplecharacteristics")
        rate(sc, fps)
        sous(sc, "width", m["format"]["largeur"])
        sous(sc, "height", m["format"]["hauteur"])
        sous(sc, "anamorphic", "FALSE")
        sous(sc, "pixelaspectratio", "square")
        sous(sc, "fielddominance", "none")
        v1 = sous(video, "track")
        v2 = sous(video, "track")
        P = m["plans"]

        def a_media_v1(p):
            return media_v1(p, self.mode)
        # V1 : transitions puis plans, dans l'ordre du temps
        for i, p in enumerate(P):
            prev = P[i - 1] if i > 0 else None
            t = p.get("transition") or {}
            d = int(t.get("duree_img") or 0)
            cut = p["debut_img"]
            if t.get("type") in ("fondu", "blanc", "poussee") and d > 0:
                if a_media_v1(p) and prev is not None and a_media_v1(prev):
                    self.transition(v1, cut - d // 2, cut - d // 2 + d, "center", t["type"])
                elif a_media_v1(p):
                    self.transition(v1, cut, cut + d, "start-black", t["type"])
                elif prev is not None and a_media_v1(prev):
                    self.transition(v1, cut - d, cut, "end-black", t["type"])
            if p["type"] == "image":
                self.clipitem(v1, os.path.basename(p["chemin"]), p["chemin"], p["debut_img"], p["debut_img"] + p["duree_img"],
                              p["entree_img"], p["sortie_img"])
            elif p["type"] == "carton" and a_media_v1(p):
                f = p["carton"]["fond"]
                hexa = {"blanc": "#FFFFFF"}.get(f, f)
                if self.mode != "png":
                    self.generateur_couleur(v1, hexa, p["debut_img"], p["debut_img"] + p["duree_img"])
        sous(v1, "enabled", "TRUE")
        sous(v1, "locked", "FALSE")
        # V2 : cartons
        nc = 0
        for i, p in enumerate(P):
            c = p.get("carton")
            if not c:
                continue
            nc += 1
            a = p["debut_img"] + int(c.get("debut_img") or 0)
            b = a + int(c.get("duree_img") or p["duree_img"])
            t = p.get("transition") or {}
            prev = P[i - 1] if i > 0 else None
            nxt = P[i + 1] if i + 1 < len(P) else None
            if p["type"] == "carton" and t.get("type") == "fondu" and t.get("duree_img") and not (prev and prev.get("carton")):
                self.transition(v2, a, a + int(t["duree_img"]), "start-black", "fondu")
            chemin = c.get("logo")
            sur_noir = p["type"] == "carton" and c.get("fond") in (None, "noir")
            if not chemin and self.mode == "texte" and not sur_noir:
                self.a_poser.append("%s « %s » à %s (%s, fond %s)" % (c.get("role"), " · ".join(
                    x for x in (c.get("texte"), c.get("deuxieme_ligne")) if x), tc(a, self.fps, tc_vers_images(
                    self.m["format"].get("tc_debut") or "00:00:00:00", self.fps)), c.get("place"), c.get("fond")))
                continue
            if not chemin and self.mode == "png":
                try:
                    chemin = self.png_carton(c, nc, opaque=(p["type"] == "carton"))
                except ImportError:
                    self.avert.append("Pillow absent : carton %d écrit en générateur de texte" % nc)
            if chemin:
                self.clipitem(v2, os.path.basename(chemin), chemin, a, b, 0, b - a)
            else:
                self.generateur_texte(v2, c, a, b)
            if nxt is not None and p["type"] == "carton" and nxt["type"] == "noir":
                tn = nxt.get("transition") or {}
                if tn.get("type") == "fondu" and tn.get("duree_img"):
                    self.transition(v2, b - int(tn["duree_img"]), b, "end-black", "fondu")
        sous(v2, "enabled", "TRUE")
        sous(v2, "locked", "FALSE")
        # audio
        audio = sous(media, "audio")
        sous(audio, "numOutputChannels", 2)
        fa = sous(audio, "format")
        sca = sous(fa, "samplecharacteristics")
        sous(sca, "depth", 16)
        sous(sca, "samplerate", 48000)
        a1 = sous(audio, "track")
        for q in m.get("paroles", []):
            self.clipitem(a1, os.path.basename(q["chemin"]), q["chemin"], q["debut_img"], q["debut_img"] + q["duree_img"],
                          q["entree_img"], q["sortie_img"], media="audio")
        sous(a1, "enabled", "TRUE")
        sous(a1, "locked", "FALSE")
        a2 = sous(audio, "track")
        mus = m.get("musique")
        if mus:
            c = self.clipitem(a2, os.path.basename(mus["chemin"]), mus["chemin"], mus["debut_img"],
                              mus["debut_img"] + mus["duree_img"], mus["entree_img"], mus["entree_img"] + mus["duree_img"],
                              media="audio")
            if mus.get("niveau_db"):
                f = sous(c, "filter")
                e = sous(f, "effect")
                sous(e, "name", "Audio Levels")
                sous(e, "effectid", "audiolevels")
                sous(e, "effectcategory", "audiolevels")
                sous(e, "effecttype", "audiolevels")
                sous(e, "mediatype", "audio")
                param(e, "level", "Level", round(10 ** (float(mus["niveau_db"]) / 20.0), 6), 0, 3.98109)
            if mus.get("fondu_sortie_img"):
                fin = mus["debut_img"] + mus["duree_img"]
                self.transition_audio(a2, fin - int(mus["fondu_sortie_img"]), fin, "end-black")
        sous(a2, "enabled", "TRUE")
        sous(a2, "locked", "FALSE")
        sons = [p for p in P if p["type"] == "image" and p.get("son_image")]
        if sons:
            a3 = sous(audio, "track")
            for p in sons:
                self.clipitem(a3, os.path.basename(p["chemin"]), p["chemin"], p["debut_img"], p["debut_img"] + p["duree_img"],
                              p["entree_img"], p["sortie_img"], media="audio")
            sous(a3, "enabled", "TRUE")
            sous(a3, "locked", "FALSE")
        # marqueurs
        for mk in m.get("marqueurs", []):
            e = sous(seq, "marker")
            sous(e, "comment", mk.get("texte") or "")
            sous(e, "name", mk.get("nom") or "")
            sous(e, "in", mk["debut_img"])
            sous(e, "out", mk["debut_img"] + mk["duree_img"] if mk.get("duree_img") else -1)
        ET.indent(racine, space="  ")
        corps = ET.tostring(racine, encoding="unicode")
        with open(self.sortie, "w", encoding="utf-8") as f:
            f.write('<?xml version="1.0" encoding="UTF-8"?>\n<!DOCTYPE xmeml>\n')
            f.write(corps)
            f.write("\n")
        return self.sortie


def media_v1(p, mode="texte"):
    """Le plan met-il quelque chose sur V1 ? Une image, ou le fond coloré d'un carton (en mode texte)."""
    if p["type"] == "image":
        return True
    return (p["type"] == "carton" and mode != "png" and (p.get("carton") or {}).get("fond") not in (None, "noir", "image"))


# ---------------------------------------------------------------- vérification

def verifier(chemin_xml, m, mode="texte"):
    """Relit le XML et le compare au montage, image par image. Renvoie la liste des écarts."""
    ecarts = []
    arbre = ET.parse(chemin_xml)
    seq = arbre.getroot().find("sequence")
    fps = fps_fraction(m["format"]["fps"])
    base, ntsc = timebase(fps)
    if int(seq.findtext("rate/timebase")) != base or (seq.findtext("rate/ntsc") == "TRUE") != ntsc:
        ecarts.append("cadence de la séquence")
    if int(seq.findtext("duration")) != m["duree_img"]:
        ecarts.append("durée %s ≠ %s" % (seq.findtext("duration"), m["duree_img"]))
    tc0 = seq.findtext("timecode/string")
    if tc0 != (m["format"].get("tc_debut") or "00:00:00:00") or int(seq.findtext("timecode/frame")) != tc_vers_images(tc0, fps):
        ecarts.append("timecode de départ")
    fichiers = {}
    for f in arbre.getroot().iter("file"):
        if f.find("pathurl") is not None:
            fichiers[f.get("id")] = unquote(urlparse(f.findtext("pathurl")).path)
    pistes_v = seq.findall("media/video/track")
    v1 = [c for c in pistes_v[0] if c.tag == "clipitem"]
    images = [p for p in m["plans"] if p["type"] == "image"]
    if len(v1) != len(images):
        ecarts.append("V1 : %d plans dans le XML, %d dans le montage" % (len(v1), len(images)))
    for c, p in zip(v1, images):
        vals = [int(c.findtext(k)) for k in ("start", "end", "in", "out")]
        att = [p["debut_img"], p["debut_img"] + p["duree_img"], p["entree_img"], p["sortie_img"]]
        if vals != att:
            ecarts.append("plan %d : XML %s ≠ montage %s" % (p["n"], vals, att))
        if vals[1] - vals[0] != vals[3] - vals[2]:
            ecarts.append("plan %d : durée sur la timeline ≠ durée source" % p["n"])
        fid = c.find("file").get("id")
        if fichiers.get(fid) != os.path.abspath(p["chemin"]):
            ecarts.append("plan %d : fichier %s ≠ %s" % (p["n"], fichiers.get(fid), p["chemin"]))
        tk = int(c.findtext("pproTicksIn"))
        if abs(tk - i2ticks(p["entree_img"], fps)) > 1:
            ecarts.append("plan %d : ticks d'entrée" % p["n"])
    # chevauchements sur chaque piste
    for k, tr in enumerate(pistes_v + seq.findall("media/audio/track")):
        items = sorted((int(c.findtext("start")), int(c.findtext("end"))) for c in tr if c.tag in ("clipitem", "generatoritem"))
        for (a, b), (c2, d2) in zip(items, items[1:]):
            if c2 < b:
                ecarts.append("piste %d : chevauchement %d-%d / %d-%d" % (k + 1, a, b, c2, d2))
    # transitions de V1
    attendues = 0
    P = m["plans"]
    for i, p in enumerate(P):
        t = p.get("transition") or {}
        if t.get("type") in ("fondu", "blanc", "poussee") and t.get("duree_img"):
            prev = P[i - 1] if i else None
            if media_v1(p, mode) or (prev is not None and media_v1(prev, mode)):
                attendues += 1
    tv1 = [t for t in pistes_v[0] if t.tag == "transitionitem"]
    if len(tv1) != attendues:
        ecarts.append("V1 : %d transitions, %d attendues" % (len(tv1), attendues))
    for t in tv1:
        a, b = int(t.findtext("start")), int(t.findtext("end"))
        al = t.findtext("alignment")
        coupe = a if al == "start-black" else b if al == "end-black" else (a + b) // 2
        if not any(abs(p["debut_img"] - coupe) <= 1 for p in P):
            ecarts.append("transition %d-%d (%s) hors d'un point de montage" % (a, b, al))
    # paroles et musique
    pistes_a = seq.findall("media/audio/track")
    a1 = [c for c in pistes_a[0] if c.tag == "clipitem"] if pistes_a else []
    if len(a1) != len(m.get("paroles", [])):
        ecarts.append("A1 : %d paroles, %d attendues" % (len(a1), len(m.get("paroles", []))))
    for c, q in zip(a1, m.get("paroles", [])):
        vals = [int(c.findtext(k)) for k in ("start", "end", "in", "out")]
        att = [q["debut_img"], q["debut_img"] + q["duree_img"], q["entree_img"], q["sortie_img"]]
        if vals != att:
            ecarts.append("parole %d : XML %s ≠ montage %s" % (q["n"], vals, att))
    if m.get("musique"):
        a2 = [c for c in pistes_a[1] if c.tag == "clipitem"] if len(pistes_a) > 1 else []
        if len(a2) != 1 or int(a2[0].findtext("end")) - int(a2[0].findtext("start")) != m["musique"]["duree_img"]:
            ecarts.append("A2 : musique absente ou de mauvaise durée")
    return ecarts


def comparer_lecture_critique(chemin_xml, m):
    """Lecture indépendante par lire_timeline.py (outil de la critique), si présent : plans visibles et noirs."""
    try:
        import lire_timeline
    except ImportError:
        return None, []
    lu = lire_timeline.lire_xml(chemin_xml)  # le format est connu : ne pas le déduire de l'extension de -o
    fps = float(fps_fraction(m["format"]["fps"]))
    ecarts = []
    vus = [x for x in lu["plans"] if x["type"] == "image"]
    images = [p for p in m["plans"] if p["type"] == "image"]
    # les plans couverts par un carton opaque (PNG) ne sont plus visibles : on ne compare que les images
    if len(vus) != len(images):
        ecarts.append("lecture critique : %d plans d'image, %d dans le montage" % (len(vus), len(images)))
    for x, p in zip(vus, images):
        if abs(x["debut"] - p["debut_img"] / fps) > 0.5 / fps + 1e-6 or abs(x["fin"] - (p["debut_img"] + p["duree_img"]) / fps) > 0.5 / fps + 1e-6:
            ecarts.append("lecture critique, plan %d : %.3f-%.3f s ≠ %.3f-%.3f s" % (p["n"], x["debut"], x["fin"], p["debut_img"] / fps,
                                                                                  (p["debut_img"] + p["duree_img"]) / fps))
    return lu, ecarts


def main(argv=None):
    ap = argparse.ArgumentParser(description="montage.json → XML FCP7 (Premiere Pro, DaVinci Resolve)")
    ap.add_argument("montage")
    ap.add_argument("-o", "--sortie")
    ap.add_argument("--cartons", choices=["texte", "png", "generateurs"], default="texte")
    ap.add_argument("--verifier", action="store_true")
    a = ap.parse_args(argv)
    m, fautes = charger_montage(a.montage)
    absents = []
    if not fautes:
        fautes, absents = verifier_sources(m)
    if fautes:
        print("montage incohérent :\n  " + "\n  ".join(fautes))
        return 1
    sortie = a.sortie or os.path.splitext(os.path.abspath(a.montage))[0] + ".xml"
    if os.path.splitext(sortie)[1].lower() != ".xml":
        print("  attention : %s ne finit pas par .xml ; la critique et les logiciels de montage le reconnaîtront mieux en .xml"
              % os.path.basename(sortie))
    w = Ecrivain(m, os.path.dirname(os.path.abspath(a.montage)), a.cartons, sortie)
    w.ecrire()
    print("XML FCP7 : %s (%d plans, %d paroles, %s, %d fichiers sources)" % (
        sortie, sum(1 for p in m["plans"] if p["type"] == "image"), len(m.get("paroles", [])),
        "musique" if m.get("musique") else "sans musique", len(w.fichiers)))
    if w.police_png:
        print("  police des cartons : %s" % w.police_png)
    for x in w.avert:
        print("  attention : " + x)
    if w.a_poser:
        print("  textes à poser à la main (marqueurs dans la séquence) ou avec --cartons png :")
        for x in w.a_poser:
            print("    - " + x)
    if a.verifier:
        ecarts = verifier(sortie, m, a.cartons)
        lu, e2 = comparer_lecture_critique(sortie, m) if a.cartons == "texte" else (None, [])
        ecarts += e2
        if ecarts:
            print("vérification : %d écart(s)\n  " % len(ecarts) + "\n  ".join(ecarts))
            return 3
        print("vérification : le XML relu colle au montage, image par image%s" % (
            " ; lecture de la critique d'accord" if lu else ""))
    return 0


if __name__ == "__main__":
    sys.exit(main())
