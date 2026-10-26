#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""filmcraft_build.py : construit la séquence de montage.json dans FilmCraft, par son canal de contrôle, puis la vérifie.

Usage :
    python3 filmcraft_build.py montage.json [--projet nouveau|ouvert] [--nom NOM] [--images DOSSIER]
                               [--enregistrer CHEMIN.fcproj] [--rendre film.mp4] [--rapport rapport.json] [--port 9876]
                               [--simulation]

Étapes (une commande FilmCraft chacune, liste exacte dans le contrat et dans COMMANDES ci-dessous) :
  1. projet : nouveau projet nommé comme le montage (défaut), ou le projet ouvert (--projet ouvert) ;
     rien n'est enregistré, sauf --enregistrer vers un fichier QUI N'EXISTE PAS ENCORE (jamais par-dessus) ;
  2. un chutier « <nom> rushes », import des rushes, de la musique et des logos ;
  3. une séquence au format du montage (3 pistes vidéo, 3 pistes son) ;
  4. V1 : chaque plan à sa place, entrée et durée à l'image près (son du rush coupé) ; fonds colorés des cartons ;
  5. V2 : les cartons en titres natifs (modifiables), à la taille et à la place du montage ;
  6. A1 paroles, A2 musique (niveau, fondu de sortie), A3 son des images ;
  7. transitions : fondus enchaînés centrés, sorties du noir, départs au noir, passage au blanc, poussée ;
  8. marqueurs de séquence (temps de la structure, cartons) ;
  9. vérification par sequence.inspect : chaque plan, chaque parole, la musique, chaque transition ;
 10. --images : une image du programme au milieu de chaque plan (file.exportFrame) et une planche (ffmpeg) ;
 11. --rendre : la vidéo H.264 de toute la durée du montage (file.exportMedia, de 0 à la durée : un noir final
     est un trou sur V1, et un export « séquence entière » s'arrête au dernier élément, sans lui).

--simulation : n'ouvre aucune connexion ; imprime la liste des commandes qui seraient envoyées, paramètres abrégés
(complets dans --rapport), pour tester sans l'app. --images est alors ignoré : il n'y a aucune image à exporter.
FilmCraft doit tourner avec son canal : open -a FilmCraft --args --control 9876 (le script le lance s'il ne répond pas).
Codes de sortie : 0 séquence construite et conforme ; 1 erreur ; 2 FilmCraft injoignable ; 3 écarts à la vérification.
"""
import argparse
import json
import os
import subprocess
import sys
from fractions import Fraction

ICI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ICI)
from commun import TICKS_PAR_S, charger_montage, fps_fraction, i2s, verifier_sources  # noqa: E402
import fc  # noqa: E402

EFFETS_FC = {"fondu": "cross_dissolve", "blanc": "dip_to_white", "poussee": "push"}
COMMANDES = ["project.inspect", "file.newProject", "file.newBin", "file.import", "file.newSequence", "sequence.open",
             "sequence.inspect", "timeline.place", "file.newColorMatte", "graphics.newText", "graphics.set", "graphics.align",
             "effects.setParam", "sequence.applyVideoTransition", "sequence.applyAudioTransition", "markers.add",
             "file.exportFrame", "file.exportMedia", "file.saveAs"]


class Simule:
    """Remplace le client : note les commandes, invente des identifiants, une plage par genre
    (médias 1001…, chutiers 2001…, caches de couleur 3001…, clips 5001…, transitions 7001…, séquences 9001…)
    pour qu'on sache, en relisant la liste, ce que chaque commande désigne."""
    DEBUTS = {"media": 1000, "chutier": 2000, "cache": 3000, "clip": 5000, "transition": 7000, "sequence": 9000}

    def __init__(self):
        self.journal = []
        self.n = dict(self.DEBUTS)

    def _id(self, genre):
        self.n[genre] += 1
        return self.n[genre]

    def cmd(self, commande, params=None, delai=None, autoriser=False):
        self.journal.append({"command": commande, "params": params or {}})
        if commande == "file.import":
            return {"items": [self._id("media") for _ in params["paths"]], "errors": []}
        if commande == "file.newSequence":
            return {"sequence": self._id("sequence")}
        if commande == "file.newBin":
            return {"bin": self._id("chutier")}
        if commande in ("timeline.place",):
            return {"clips": [self._id("clip")]}
        if commande == "graphics.newText":
            return {"clip": params.get("clip") or self._id("clip"), "layer": 0}
        if commande == "file.newColorMatte":
            return {"item": self._id("cache")}
        if commande in ("sequence.applyVideoTransition", "sequence.applyAudioTransition"):
            return {"transition": self._id("transition")}
        if commande == "sequence.inspect":
            return None
        return None


class Constructeur:
    def __init__(self, m, client, args):
        self.m = m
        self.c = client
        self.a = args
        self.fps = fps_fraction(m["format"]["fps"])
        self.items = {}      # chemin → item du projet
        self.clips_v1 = {}   # n du plan → clip
        self.clips_v2 = {}   # n du plan → clip graphique
        self.clips_a = []    # (parole n, clip)
        self.clip_musique = None
        self.transitions = []
        self.ecarts = []
        self.notes = []
        self.seq = None

    def ticks(self, n_img):
        return int(Fraction(int(n_img)) / self.fps * TICKS_PAR_S)

    # 1-2. projet, chutier, import
    def preparer(self):
        nom = self.a.nom or self.m["titre"]
        if self.a.projet == "nouveau":
            self.c.cmd("file.newProject", {"name": nom}, autoriser=True)
            self.notes.append("nouveau projet « %s » (non enregistré)" % nom)
        else:
            p = self.c.cmd("project.inspect")
            if p is not None and not p.get("name"):
                raise SystemExit("aucun projet ouvert dans FilmCraft")
        b = self.c.cmd("file.newBin", {"name": "%s rushes" % nom})
        chutier = b.get("bin") if b else None
        chemins = []
        for p in self.m["plans"]:
            if p["type"] == "image" and p["chemin"] not in chemins:
                chemins.append(p["chemin"])
            c = p.get("carton") or {}
            if c.get("logo") and c["logo"] not in chemins:
                chemins.append(c["logo"])
        for q in self.m.get("paroles", []):
            if q["chemin"] not in chemins:
                chemins.append(q["chemin"])
        if self.m.get("musique") and self.m["musique"]["chemin"] not in chemins:
            chemins.append(self.m["musique"]["chemin"])
        manquants = [x for x in chemins if not os.path.exists(x)]
        if manquants:
            raise SystemExit("fichiers introuvables : %s" % ", ".join(manquants))
        params = {"paths": chemins}
        if chutier is not None:
            params["bin"] = chutier
        r = self.c.cmd("file.import", params, delai=600)
        if r.get("errors"):
            raise SystemExit("import refusé : %s" % r["errors"])
        if len(r.get("items", [])) != len(chemins):
            raise SystemExit("import : %d éléments pour %d fichiers" % (len(r.get("items", [])), len(chemins)))
        self.items = dict(zip(chemins, r["items"]))
        return nom

    # 3. séquence
    def sequence(self, nom):
        f = self.m["format"]
        r = self.c.cmd("file.newSequence", {"name": nom, "width": f["largeur"], "height": f["hauteur"],
                                            "fps": float(self.fps), "video": 3, "audio": 3})
        self.seq = r["sequence"]
        self.c.cmd("sequence.open", {"item": self.seq})

    def placer(self, item, piste, debut, entree, duree, video=True, audio=False):
        p = {"item": item, "track": piste, "time": self.ticks(debut), "insert": False, "sourceIn": self.ticks(entree),
             "duration": self.ticks(duree), "video": video, "audio": audio}
        r = self.c.cmd("timeline.place", p)
        return (r.get("clips") or [None])[0]

    # 4. V1
    def piste_v1(self):
        for p in self.m["plans"]:
            if p["type"] == "image":
                self.clips_v1[p["n"]] = self.placer(self.items[p["chemin"]], "V1", p["debut_img"], p["entree_img"], p["duree_img"])
            elif p["type"] == "carton" and (p.get("carton") or {}).get("fond") not in (None, "noir", "image"):
                f = p["carton"]["fond"]
                hexa = {"blanc": "#ffffff"}.get(f, f)
                r = self.c.cmd("file.newColorMatte", {"color": hexa.lower(), "seconds": i2s(p["duree_img"], self.fps)})
                self.clips_v1[p["n"]] = self.placer(r["item"], "V1", p["debut_img"], 0, p["duree_img"])

    # 5. V2 : cartons
    def piste_v2(self):
        H, L = self.m["format"]["hauteur"], self.m["format"]["largeur"]
        police = (self.m.get("police") or {}).get("famille") or "Arial"   # même repli que export_xml.py, jamais une police Apple
        texte_c = (self.m.get("couleurs") or {}).get("texte", "#FFFFFF")
        for p in self.m["plans"]:
            c = p.get("carton")
            if not c:
                continue
            a = p["debut_img"] + int(c.get("debut_img") or 0)
            d = int(c.get("duree_img") or p["duree_img"])
            if c.get("logo"):
                self.clips_v2[p["n"]] = self.placer(self.items[c["logo"]], "V2", a, 0, d)
                continue
            corps = max(8, int(round(float(c.get("taille_pct") or 4.5) / 100.0 * H / 0.7)))
            prm = {"text": c.get("texte") or "", "size": corps, "seconds": i2s(d, self.fps), "track": 1, "time": self.ticks(a), "font": police}
            r = self.c.cmd("graphics.newText", prm)
            clip = r["clip"]
            couleur = texte_c
            if c.get("fond") == "blanc" and couleur.upper() == "#FFFFFF":
                couleur = "#000000"
            place = c.get("place", "centre")
            if place == "centre":
                self.c.cmd("graphics.set", {"clip": clip, "layer": 0, "props": {"align": "center", "fill_color": couleur.lower()}})
                self.c.cmd("graphics.align", {"clip": clip, "layers": [0], "align": "hcenter", "to": "frame"})
                self.c.cmd("graphics.align", {"clip": clip, "layers": [0], "align": "vcenter", "to": "frame"})
            else:
                droite = place.endswith("droite")
                x = L * (0.92 if droite else 0.08)
                y = H * (0.1 if place.startswith("haut") else 0.9) + (0 if place.startswith("haut") else -corps * (1.1 if c.get("deuxieme_ligne") else 0))
                self.c.cmd("graphics.set", {"clip": clip, "layer": 0, "props": {"align": "right" if droite else "left",
                                                                               "position": [round(x), round(y)], "fill_color": couleur.lower()}})
                if c.get("deuxieme_ligne"):
                    prm2 = {"clip": clip, "text": c["deuxieme_ligne"], "size": int(corps * 0.75), "font": police}
                    self.c.cmd("graphics.newText", prm2)
                    self.c.cmd("graphics.set", {"clip": clip, "layer": 1, "props": {"align": "right" if droite else "left",
                                                                                   "position": [round(x), round(H * 0.9)],
                                                                                   "fill_color": couleur.lower()}})
            self.clips_v2[p["n"]] = clip

    # 6. son
    def pistes_son(self):
        for q in self.m.get("paroles", []):
            clip = self.placer(self.items[q["chemin"]], "A1", q["debut_img"], q["entree_img"], q["duree_img"], video=False, audio=True)
            self.clips_a.append((q["n"], clip))
        mus = self.m.get("musique")
        if mus:
            self.clip_musique = self.placer(self.items[mus["chemin"]], "A2", mus["debut_img"], mus["entree_img"], mus["duree_img"],
                                            video=False, audio=True)
            if mus.get("niveau_db"):
                self.c.cmd("effects.setParam", {"clip": self.clip_musique, "effect": 0, "param": "level", "value": float(mus["niveau_db"])})
            if mus.get("fondu_sortie_img"):
                self.c.cmd("sequence.applyAudioTransition", {"clip": self.clip_musique, "effect": "constant_power",
                                                             "frames": int(mus["fondu_sortie_img"]), "edge": "out"})
        for p in self.m["plans"]:
            if p["type"] == "image" and p.get("son_image"):
                self.placer(self.items[p["chemin"]], "A3", p["debut_img"], p["entree_img"], p["duree_img"], video=False, audio=True)

    # 7. transitions
    def transitions_(self):
        P = self.m["plans"]
        for i, p in enumerate(P):
            t = p.get("transition") or {}
            if t.get("type") not in EFFETS_FC or not t.get("duree_img"):
                continue
            eff, d = EFFETS_FC[t["type"]], int(t["duree_img"])
            prev = P[i - 1] if i > 0 else None
            if p["n"] in self.clips_v1:
                self.transitions.append(("V1", "in", p["n"], self.c.cmd("sequence.applyVideoTransition",
                                                                         {"clip": self.clips_v1[p["n"]], "effect": eff, "frames": d, "edge": "in"})))
            elif prev is not None and prev["n"] in self.clips_v1:
                self.transitions.append(("V1", "out", prev["n"], self.c.cmd("sequence.applyVideoTransition",
                                                                            {"clip": self.clips_v1[prev["n"]], "effect": eff, "frames": d, "edge": "out"})))
            # cartons : le texte entre et sort avec le noir
            if p["type"] == "carton" and p["n"] in self.clips_v2 and not (prev and prev.get("carton")):
                self.transitions.append(("V2", "in", p["n"], self.c.cmd("sequence.applyVideoTransition",
                                                                         {"clip": self.clips_v2[p["n"]], "effect": "cross_dissolve", "frames": d, "edge": "in"})))
            if p["type"] == "noir" and prev is not None and prev["type"] == "carton" and prev["n"] in self.clips_v2:
                self.transitions.append(("V2", "out", prev["n"], self.c.cmd("sequence.applyVideoTransition",
                                                                            {"clip": self.clips_v2[prev["n"]], "effect": "cross_dissolve", "frames": d, "edge": "out"})))

    # 8. marqueurs
    def marqueurs(self):
        for mk in self.m.get("marqueurs", []):
            prm = {"target": "program", "time": self.ticks(mk["debut_img"]), "name": mk.get("nom") or "", "comment": mk.get("texte") or ""}
            if mk.get("duree_img"):
                prm["durationFrames"] = int(mk["duree_img"])
            self.c.cmd("markers.add", prm)

    # 9. vérification
    def verifier(self):
        r = self.c.cmd("sequence.inspect", {"item": self.seq})
        if r is None:
            return None
        fps = self.fps
        img = lambda ticks: int(round(Fraction(int(ticks)) / TICKS_PAR_S * fps))
        v = r["video"]
        v1 = {it["clip"]: it for it in v[0]["items"]}
        images = [p for p in self.m["plans"] if p["type"] == "image"]
        for p in images:
            it = v1.get(self.clips_v1.get(p["n"]))
            if it is None:
                self.ecarts.append("plan %d absent de V1" % p["n"])
                continue
            vals = (img(it["start"]), img(it["end"]), img(it["sourceIn"]), img(it["sourceOut"]))
            att = (p["debut_img"], p["debut_img"] + p["duree_img"], p["entree_img"], p["sortie_img"])
            if vals != att:
                self.ecarts.append("plan %d : FilmCraft %s ≠ montage %s" % (p["n"], vals, att))
        attendus_v1 = len(images) + sum(1 for p in self.m["plans"] if p["type"] == "carton" and p["n"] in self.clips_v1)
        if len(v[0]["items"]) != attendus_v1:
            self.ecarts.append("V1 : %d éléments, %d attendus" % (len(v[0]["items"]), attendus_v1))
        if len(v[1]["items"]) != len(self.clips_v2):
            self.ecarts.append("V2 : %d éléments, %d cartons" % (len(v[1]["items"]), len(self.clips_v2)))
        a = r["audio"]
        a1 = {it["clip"]: it for it in a[0]["items"]}
        for (n, clip), q in zip(self.clips_a, self.m.get("paroles", [])):
            it = a1.get(clip)
            if it is None or (img(it["start"]), img(it["end"]), img(it["sourceIn"])) != (q["debut_img"], q["debut_img"] + q["duree_img"], q["entree_img"]):
                self.ecarts.append("parole %d : place ou entrée" % n)
        if self.m.get("musique"):
            it = {x["clip"]: x for x in a[1]["items"]}.get(self.clip_musique)
            if it is None or img(it["end"]) - img(it["start"]) != self.m["musique"]["duree_img"]:
                self.ecarts.append("musique absente ou de mauvaise durée")
            elif self.m["musique"].get("niveau_db"):
                vol = next((e for e in it.get("effects", []) if e.get("effect") == "volume"), None)
                if vol is None or "%.1f" % float(self.m["musique"]["niveau_db"]) not in str(vol["params"].get("level")):
                    self.ecarts.append("niveau de la musique non appliqué")
        # transitions : nombre, alignement et place
        tv = {tr["id"]: tr for t in v for tr in t.get("transitions", [])}
        for piste, bord, n, res in self.transitions:
            tid = (res or {}).get("transition")
            tr = tv.get(tid)
            if tr is None:
                self.ecarts.append("transition du plan %d absente" % n)
                continue
            p = next(x for x in self.m["plans"] if x["n"] == n)
            t_att = None
            nxt = self.m["plans"][self.m["plans"].index(p) + 1] if bord == "out" else p
            d = int((nxt.get("transition") or {}).get("duree_img") or 0)
            if bord == "in":
                prev_media = self.m["plans"].index(p) > 0 and self.m["plans"][self.m["plans"].index(p) - 1]["n"] in self.clips_v1
                t_att = ("center", p["debut_img"] - d // 2) if (piste == "V1" and prev_media) else ("start", p["debut_img"])
            else:
                t_att = ("end", p["debut_img"] + p["duree_img"] - d)
            debut = img(tr["start"])
            if tr.get("align") != t_att[0] or abs(debut - t_att[1]) > 1:
                self.ecarts.append("transition du plan %d : %s à %d, attendu %s à %d" % (n, tr.get("align"), debut, t_att[0], t_att[1]))
        if img(r["duration"]) != self.m["duree_img"]:
            # une séquence finit à son dernier élément : un noir final n'y compte pas
            dernier = self.m["plans"][-1]
            if not (dernier["type"] == "noir" and img(r["duration"]) == dernier["debut_img"]):
                self.ecarts.append("durée %d ≠ %d images" % (img(r["duration"]), self.m["duree_img"]))
        return r

    # 10. images de contrôle
    def images(self, dossier):
        os.makedirs(dossier, exist_ok=True)
        faites = []
        for p in self.m["plans"]:
            milieu = p["debut_img"] + p["duree_img"] // 2
            chemin = os.path.join(dossier, "plan-%02d.png" % p["n"])
            self.c.cmd("file.exportFrame", {"path": chemin, "format": "png", "target": "program", "time": self.ticks(milieu),
                                            "sequence": self.seq})
            if os.path.exists(chemin):
                faites.append(chemin)
        if faites:
            planche = os.path.join(dossier, "planche.jpg")
            cols = 6
            rangs = (len(faites) + cols - 1) // cols
            r = subprocess.run(["ffmpeg", "-v", "error", "-y", "-framerate", "1", "-i", os.path.join(dossier, "plan-%02d.png"),
                                "-vf", "scale=320:-1,tile=%dx%d:padding=4:color=black" % (cols, rangs), "-frames:v", "1", planche])
            if r.returncode == 0:
                return planche, len(faites)
        return None, len(faites)


def main(argv=None):
    ap = argparse.ArgumentParser(description="montage.json → séquence FilmCraft")
    ap.add_argument("montage")
    ap.add_argument("--projet", choices=["nouveau", "ouvert"], default="nouveau")
    ap.add_argument("--nom", help="nom de la séquence (défaut : titre du montage)")
    ap.add_argument("--images", help="dossier des images de contrôle (une par plan) et de la planche")
    ap.add_argument("--enregistrer", help="chemin .fcproj qui n'existe pas encore")
    ap.add_argument("--rendre", help="vidéo H.264 (.mp4) qui n'existe pas encore : toute la durée du montage, noir final compris")
    ap.add_argument("--rapport")
    ap.add_argument("--port", type=int, default=9876)
    ap.add_argument("--simulation", action="store_true")
    a = ap.parse_args(argv)
    if a.images:
        a.images = os.path.abspath(a.images)    # FilmCraft n'a pas le même dossier courant : chemins absolus seulement
    if a.rendre:
        a.rendre = os.path.abspath(a.rendre)
        if os.path.exists(a.rendre):
            print("refusé : %s existe déjà ; la skill n'écrit jamais par-dessus un fichier" % a.rendre)
            return 1
    m, fautes = charger_montage(a.montage)
    absents = []
    if not fautes:
        fautes, absents = verifier_sources(m)
    if fautes:
        print("montage incohérent :\n  " + "\n  ".join(fautes))
        return 1
    for x in absents:
        print("  attention : fichier introuvable (FilmCraft ne pourra pas l'importer) : %s" % x)
    if a.enregistrer and os.path.exists(a.enregistrer):
        print("refusé : %s existe déjà ; la skill n'enregistre jamais par-dessus un projet" % a.enregistrer)
        return 1
    if a.simulation:
        client = Simule()
    else:
        if not fc.lancer(a.port):
            print("FilmCraft injoignable sur le port %d : open -a FilmCraft --args --control %d ; sinon --simulation" % (a.port, a.port))
            return 2
        client = fc.Client(a.port, relance=True)
    b = Constructeur(m, client, a)
    try:
        nom = b.preparer()
        b.sequence(nom)
        b.piste_v1()
        b.piste_v2()
        b.pistes_son()
        b.transitions_()
        b.marqueurs()
        b.verifier()
        planche = None
        if a.images and not a.simulation:
            planche, n = b.images(a.images)
            b.notes.append("%d images de contrôle%s" % (n, (" ; planche : %s" % planche) if planche else ""))
        if a.rendre:
            r = client.cmd("file.exportMedia", {"path": a.rendre, "format": "h264", "sequence": b.seq, "range": "custom",
                                                "startSeconds": 0, "endSeconds": i2s(m["duree_img"], m["format"]["fps"]),
                                                "wait": True}, delai=900)
            if not a.simulation:
                n_img = ((r or {}).get("result") or {}).get("frames")
                b.notes.append("vidéo rendue : %s (%s images)" % (a.rendre, n_img))
                if n_img is not None and int(n_img) != int(m["duree_img"]):
                    b.ecarts.append("vidéo rendue : %s images, %d attendues" % (n_img, m["duree_img"]))
        if a.enregistrer and not a.simulation:
            client.cmd("file.saveAs", {"path": os.path.abspath(a.enregistrer)}, autoriser=True)
            b.notes.append("projet enregistré : %s" % os.path.abspath(a.enregistrer))
    except fc.Erreur as e:
        print("FilmCraft a refusé une commande : %s" % e)
        return 1
    rapport = {"sequence": b.seq, "nom": nom, "plans_v1": len(b.clips_v1), "cartons_v2": len(b.clips_v2),
               "paroles": len(b.clips_a), "musique": bool(b.clip_musique), "transitions": len(b.transitions),
               "ecarts": b.ecarts, "notes": b.notes}
    if a.simulation:
        rapport["commandes"] = client.journal
    if a.rapport:
        with open(a.rapport, "w", encoding="utf-8") as f:
            json.dump(rapport, f, ensure_ascii=False, indent=1)
    print("FilmCraft%s : séquence « %s » (id %s) — %d plans sur V1, %d cartons sur V2, %d paroles, %s, %d transitions" % (
        " (simulation)" if a.simulation else "", nom, b.seq, len(b.clips_v1), len(b.clips_v2), len(b.clips_a),
        "musique" if b.clip_musique else "sans musique", len(b.transitions)))
    for x in b.notes:
        print("  " + x)
    if a.simulation:
        for k, c in enumerate(client.journal, 1):
            p = json.dumps(c["params"], ensure_ascii=False)
            print("  %3d  %-34s %s" % (k, c["command"], p if len(p) <= 110 else p[:109] + "…"))
        print("  %d commandes listées ci-dessus, aucune envoyée%s" % (
            len(client.journal), (" ; paramètres complets dans %s" % a.rapport) if a.rapport else " ; paramètres complets avec --rapport"))
        if a.images:
            print("  --images ignoré en simulation (aucune image à exporter)")
        return 0
    if b.ecarts:
        print("vérification : %d écart(s)\n  " % len(b.ecarts) + "\n  ".join(b.ecarts))
        return 3
    print("vérification (sequence.inspect) : chaque plan, parole et transition est à sa place, à l'image près")
    return 0


if __name__ == "__main__":
    sys.exit(main())
