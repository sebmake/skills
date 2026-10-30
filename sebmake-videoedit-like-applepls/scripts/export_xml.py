#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""export_xml.py: montage.json -> Final Cut Pro 7 XML ("xmeml", version 4), to import into Premiere Pro
(File > Import) or DaVinci Resolve (File > Import > Timeline). Python 3.9, standard library.

Usage:
    python3 export_xml.py montage.json [-o montage.xml] [--cartons texte|png] [--verifier]

Tracks: V1 the shots, V2 the title cards; A1 the speech, A2 the music, A3 the picture sound (if requested).
Title cards (each title card also gets a sequence marker that carries its text):
    texte (default): the FCP7 "Text" generator, only for a title card on black. Text laid over
                     a picture (lower third, title in the scene) or over a colored background is written only as a
                     marker, to place by hand. Reason: an importer that does not read this generator replaces it
                     with black video (seen in FilmCraft); on black nothing shows; over a picture, it would hide it.
    png            : one PNG image per title card (text and background already drawn), placed on V2; needs Pillow.
                     The title cards are then pictures: critique_montage.py will read them as such.
    generateurs    : the "Text" generator everywhere (editable titles where the software converts them;
                     risk of black video over pictures, see above).
--verifier: reads the written XML back and compares shots, transitions, speech and music to the edit, frame by frame
            (and, if lire_timeline.py is present, the review's independent reading). Exit code 0 if everything matches.

What the format does not guarantee: conversion of the text generators, the exact size and position of the text,
the names of transitions other than Cross Dissolve. Check by eye after import. Premiere Pro and Resolve were not
installed where this script was written: it is tested by reading back and by importing into FilmCraft.
Exit codes: 0 success; 1 inconsistent edit; 3 check failed.
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
        self.fichiers = {}  # path -> id
        self.n_clip = 0
        self.avert = []
        self.a_poser = []
        self.police_png = None

    # -- source files
    def ref_fichier(self, parent, chemin, audio_seul=False):
        if chemin in self.fichiers:
            sous(parent, "file", id=self.fichiers[chemin])
            return
        fid = "file-%d" % (len(self.fichiers) + 1)
        self.fichiers[chemin] = fid
        info = sonder(chemin)
        if info.get("absent"):
            self.avert.append("file not found (will be offline): %s" % chemin)
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
        sous(g, "name", (carton.get("texte") or "title card")[:60])
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
        police = (self.m.get("police") or {}).get("famille") or "Arial"   # common fallback, never an Apple font
        param(e, "fontname", "Font", police)
        # cap height ≈ 0.7 × font size (convention): font size = size % × height / 0.7
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
        import cartons  # needs Pillow
        if self.police_png is None:
            chemin_police, av = cartons.choisir_police(self.m)
            self.police_png = chemin_police or "Pillow default font"
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

    # -- the sequence
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
        # V1: transitions then shots, in time order
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
        # V2: title cards
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
                self.a_poser.append("%s \"%s\" at %s (%s, background %s)" % (c.get("role"), " · ".join(
                    x for x in (c.get("texte"), c.get("deuxieme_ligne")) if x), tc(a, self.fps, tc_vers_images(
                    self.m["format"].get("tc_debut") or "00:00:00:00", self.fps)), c.get("place"), c.get("fond")))
                continue
            if not chemin and self.mode == "png":
                try:
                    chemin = self.png_carton(c, nc, opaque=(p["type"] == "carton"))
                except ImportError:
                    self.avert.append("Pillow missing: title card %d written as a text generator" % nc)
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
        # markers
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
    """Does the shot put anything on V1? A picture, or the colored background of a title card (in texte mode)."""
    if p["type"] == "image":
        return True
    return (p["type"] == "carton" and mode != "png" and (p.get("carton") or {}).get("fond") not in (None, "noir", "image"))


# ---------------------------------------------------------------- check

def verifier(chemin_xml, m, mode="texte"):
    """Reads the XML back and compares it to the edit, frame by frame. Returns the list of mismatches."""
    ecarts = []
    arbre = ET.parse(chemin_xml)
    seq = arbre.getroot().find("sequence")
    fps = fps_fraction(m["format"]["fps"])
    base, ntsc = timebase(fps)
    if int(seq.findtext("rate/timebase")) != base or (seq.findtext("rate/ntsc") == "TRUE") != ntsc:
        ecarts.append("sequence frame rate")
    if int(seq.findtext("duration")) != m["duree_img"]:
        ecarts.append("duration %s ≠ %s" % (seq.findtext("duration"), m["duree_img"]))
    tc0 = seq.findtext("timecode/string")
    if tc0 != (m["format"].get("tc_debut") or "00:00:00:00") or int(seq.findtext("timecode/frame")) != tc_vers_images(tc0, fps):
        ecarts.append("start timecode")
    fichiers = {}
    for f in arbre.getroot().iter("file"):
        if f.find("pathurl") is not None:
            fichiers[f.get("id")] = unquote(urlparse(f.findtext("pathurl")).path)
    pistes_v = seq.findall("media/video/track")
    v1 = [c for c in pistes_v[0] if c.tag == "clipitem"]
    images = [p for p in m["plans"] if p["type"] == "image"]
    if len(v1) != len(images):
        ecarts.append("V1: %d shots in the XML, %d in the edit" % (len(v1), len(images)))
    for c, p in zip(v1, images):
        vals = [int(c.findtext(k)) for k in ("start", "end", "in", "out")]
        att = [p["debut_img"], p["debut_img"] + p["duree_img"], p["entree_img"], p["sortie_img"]]
        if vals != att:
            ecarts.append("shot %d: XML %s ≠ edit %s" % (p["n"], vals, att))
        if vals[1] - vals[0] != vals[3] - vals[2]:
            ecarts.append("shot %d: timeline duration ≠ source duration" % p["n"])
        fid = c.find("file").get("id")
        if fichiers.get(fid) != os.path.abspath(p["chemin"]):
            ecarts.append("shot %d: file %s ≠ %s" % (p["n"], fichiers.get(fid), p["chemin"]))
        tk = int(c.findtext("pproTicksIn"))
        if abs(tk - i2ticks(p["entree_img"], fps)) > 1:
            ecarts.append("shot %d: in-point ticks" % p["n"])
    # overlaps on each track
    for k, tr in enumerate(pistes_v + seq.findall("media/audio/track")):
        items = sorted((int(c.findtext("start")), int(c.findtext("end"))) for c in tr if c.tag in ("clipitem", "generatoritem"))
        for (a, b), (c2, d2) in zip(items, items[1:]):
            if c2 < b:
                ecarts.append("track %d: overlap %d-%d / %d-%d" % (k + 1, a, b, c2, d2))
    # V1 transitions
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
        ecarts.append("V1: %d transitions, %d expected" % (len(tv1), attendues))
    for t in tv1:
        a, b = int(t.findtext("start")), int(t.findtext("end"))
        al = t.findtext("alignment")
        coupe = a if al == "start-black" else b if al == "end-black" else (a + b) // 2
        if not any(abs(p["debut_img"] - coupe) <= 1 for p in P):
            ecarts.append("transition %d-%d (%s) not on an edit point" % (a, b, al))
    # speech and music
    pistes_a = seq.findall("media/audio/track")
    a1 = [c for c in pistes_a[0] if c.tag == "clipitem"] if pistes_a else []
    if len(a1) != len(m.get("paroles", [])):
        ecarts.append("A1: %d speech items, %d expected" % (len(a1), len(m.get("paroles", []))))
    for c, q in zip(a1, m.get("paroles", [])):
        vals = [int(c.findtext(k)) for k in ("start", "end", "in", "out")]
        att = [q["debut_img"], q["debut_img"] + q["duree_img"], q["entree_img"], q["sortie_img"]]
        if vals != att:
            ecarts.append("speech %d: XML %s ≠ edit %s" % (q["n"], vals, att))
    if m.get("musique"):
        a2 = [c for c in pistes_a[1] if c.tag == "clipitem"] if len(pistes_a) > 1 else []
        if len(a2) != 1 or int(a2[0].findtext("end")) - int(a2[0].findtext("start")) != m["musique"]["duree_img"]:
            ecarts.append("A2: music missing or wrong duration")
    return ecarts


def comparer_lecture_critique(chemin_xml, m):
    """Independent reading by lire_timeline.py (the review's tool), if present: visible shots and blacks."""
    try:
        import lire_timeline
    except ImportError:
        return None, []
    lu = lire_timeline.lire_xml(chemin_xml)  # the format is known: do not infer it from the -o extension
    fps = float(fps_fraction(m["format"]["fps"]))
    ecarts = []
    vus = [x for x in lu["plans"] if x["type"] == "image"]
    images = [p for p in m["plans"] if p["type"] == "image"]
    # shots covered by an opaque title card (PNG) are no longer visible: compare only the picture shots
    if len(vus) != len(images):
        ecarts.append("review reading: %d picture shots, %d in the edit" % (len(vus), len(images)))
    for x, p in zip(vus, images):
        if abs(x["debut"] - p["debut_img"] / fps) > 0.5 / fps + 1e-6 or abs(x["fin"] - (p["debut_img"] + p["duree_img"]) / fps) > 0.5 / fps + 1e-6:
            ecarts.append("review reading, shot %d: %.3f-%.3f s ≠ %.3f-%.3f s" % (p["n"], x["debut"], x["fin"], p["debut_img"] / fps,
                                                                                  (p["debut_img"] + p["duree_img"]) / fps))
    return lu, ecarts


def main(argv=None):
    ap = argparse.ArgumentParser(description="montage.json -> FCP7 XML (Premiere Pro, DaVinci Resolve)")
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
        print("inconsistent edit:\n  " + "\n  ".join(fautes))
        return 1
    sortie = a.sortie or os.path.splitext(os.path.abspath(a.montage))[0] + ".xml"
    if os.path.splitext(sortie)[1].lower() != ".xml":
        print("  warning: %s does not end in .xml; the review and editing software recognize it better as .xml"
              % os.path.basename(sortie))
    w = Ecrivain(m, os.path.dirname(os.path.abspath(a.montage)), a.cartons, sortie)
    w.ecrire()
    print("FCP7 XML: %s (%d shots, %d speech items, %s, %d source files)" % (
        sortie, sum(1 for p in m["plans"] if p["type"] == "image"), len(m.get("paroles", [])),
        "music" if m.get("musique") else "no music", len(w.fichiers)))
    if w.police_png:
        print("  title card font: %s" % w.police_png)
    for x in w.avert:
        print("  warning: " + x)
    if w.a_poser:
        print("  text to place by hand (markers in the sequence) or with --cartons png:")
        for x in w.a_poser:
            print("    - " + x)
    if a.verifier:
        ecarts = verifier(sortie, m, a.cartons)
        lu, e2 = comparer_lecture_critique(sortie, m) if a.cartons == "texte" else (None, [])
        ecarts += e2
        if ecarts:
            print("check: %d mismatch(es)\n  " % len(ecarts) + "\n  ".join(ecarts))
            return 3
        print("check: the XML read back matches the edit, frame by frame%s" % (
            "; the review's reading agrees" if lu else ""))
    return 0


if __name__ == "__main__":
    sys.exit(main())
