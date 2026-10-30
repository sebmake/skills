#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""filmcraft_build.py: builds the sequence of montage.json in FilmCraft, through its control channel, then checks it.

Usage:
    python3 filmcraft_build.py montage.json [--projet nouveau|ouvert] [--nom NAME] [--images FOLDER]
                               [--enregistrer PATH.fcproj] [--rendre film.mp4] [--rapport report.json] [--port 9876]
                               [--simulation]

Steps (one FilmCraft command each; exact list in the contract and in COMMANDES below):
  1. project: a new project named after the edit (default), or the open project (--projet ouvert);
     nothing is saved, except --enregistrer to a file THAT DOES NOT EXIST YET (never over an existing one);
  2. a bin "<name> footage", import of the footage, the music and the logos;
  3. a sequence in the edit's format (3 video tracks, 3 audio tracks);
  4. V1: each shot in its place, in point and duration to the frame (clip audio cut); colored backgrounds of title cards;
  5. V2: title cards as native titles (editable), at the edit's size and position;
  6. A1 speech, A2 music (level, fade-out, ducking under the speech), A3 picture sound and one-off sound effects;
     tracks named by their role; subtitles imported from an SRT (track C1);
  7. transitions: centered cross dissolves, fades up from black, fades to black, dip to white, push;
  8. sequence markers (structure beats, title cards);
  9. check with sequence.inspect: each shot, each speech item, the music, each transition;
 10. --images: one program frame in the middle of each shot (file.exportFrame) and a contact sheet (ffmpeg);
 10 bis. --capture: a capture of the FilmCraft window, sequence open; --carte: the edit map (tracks,
     items, what each one does), to read to understand the edit or to retouch it by hand;
 11. --rendre: the H.264 video of the whole edit (file.exportMedia, from 0 to the duration: a final black
     is a gap on V1, and a "whole sequence" export stops at the last item, without it).

--simulation: opens no connection; prints the list of commands that would be sent, parameters shortened
(full in --rapport), to test without the app. --images is then ignored: there is no frame to export.
FilmCraft must run with its channel: open -a FilmCraft --args --control 9876 (the script launches it if it does not reply).
Exit codes: 0 sequence built and correct; 1 error; 2 FilmCraft unreachable; 3 mismatches found by the check.
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
             "file.exportFrame", "file.exportMedia", "file.saveAs", "timeline.setTrack", "captions.import",
             "essentialSound.setType", "essentialSound.set", "essentialSound.generateDucking"]
NOMS_PISTES = [("V1", "Picture"), ("V2", "Titles and text"), ("A1", "Speech and voice"), ("A2", "Music"),
               ("A3", "Picture sound and gestures")]


class Simule:
    """Stands in for the client: records the commands, makes up IDs, one range per kind
    (media 1001…, bins 2001…, color mattes 3001…, clips 5001…, transitions 7001…, sequences 9001…)
    so that, reading the list back, you know what each command refers to."""
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
        self.items = {}      # path -> project item
        self.clips_v1 = {}   # shot n -> clip
        self.clips_v2 = {}   # shot n -> graphics clip
        self.clips_a = []    # (speech n, clip)
        self.clip_musique = None
        self.clips_sons = []    # (n, clip) of the one-off sounds on A3
        self.attenuation = None
        self.transitions = []
        self.ecarts = []
        self.notes = []
        self.seq = None

    def ticks(self, n_img):
        return int(Fraction(int(n_img)) / self.fps * TICKS_PAR_S)

    # 1-2. project, bin, import
    def preparer(self):
        nom = self.a.nom or self.m["titre"]
        if self.a.projet == "nouveau":
            self.c.cmd("file.newProject", {"name": nom}, autoriser=True)
            self.notes.append("new project \"%s\" (not saved)" % nom)
        else:
            p = self.c.cmd("project.inspect")
            if p is not None and not p.get("name"):
                raise SystemExit("no project open in FilmCraft")
        b = self.c.cmd("file.newBin", {"name": "%s footage" % nom})
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
        for x in self.m.get("sons", []):
            if x["chemin"] not in chemins:
                chemins.append(x["chemin"])
        manquants = [x for x in chemins if not os.path.exists(x)]
        if manquants:
            raise SystemExit("files not found: %s" % ", ".join(manquants))
        params = {"paths": chemins}
        if chutier is not None:
            params["bin"] = chutier
        r = self.c.cmd("file.import", params, delai=600)
        if r.get("errors"):
            raise SystemExit("import refused: %s" % r["errors"])
        if len(r.get("items", [])) != len(chemins):
            raise SystemExit("import: %d items for %d files" % (len(r.get("items", [])), len(chemins)))
        self.items = dict(zip(chemins, r["items"]))
        return nom

    # 3. sequence
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

    # 5. V2: title cards
    def piste_v2(self):
        H, L = self.m["format"]["hauteur"], self.m["format"]["largeur"]
        police = (self.m.get("police") or {}).get("famille") or "Arial"   # same fallback as export_xml.py, never an Apple font
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

    # 6. sound
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
        for x in self.m.get("sons", []):
            clip = self.placer(self.items[x["chemin"]], "A3", x["debut_img"], x.get("entree_img", 0), x["duree_img"], video=False, audio=True)
            self.clips_sons.append((x.get("n"), clip))
        # the music ducks under the speech: Essential Sound roles, then ducking generated by the app
        if mus and mus.get("attenuation_db") and self.clip_musique is not None and self.clips_a:
            paroles = [c for _, c in self.clips_a if c is not None]
            self.c.cmd("essentialSound.setType", {"clips": paroles, "type": "dialogue"})
            self.c.cmd("essentialSound.setType", {"clips": [self.clip_musique], "type": "music"})
            if self.clips_sons:
                self.c.cmd("essentialSound.setType", {"clips": [c for _, c in self.clips_sons if c is not None], "type": "sfx"})
            self.c.cmd("essentialSound.set", {"clips": [self.clip_musique], "key": "ducking.reduceDb", "value": -abs(float(mus["attenuation_db"]))})
            r = self.c.cmd("essentialSound.generateDucking", {"clips": [self.clip_musique]})
            self.attenuation = r
            self.notes.append("music ducked by %.0f dB under the speech (FilmCraft Essential Sound)" % abs(float(mus["attenuation_db"])))

    # 6 bis. named tracks, subtitles
    def habiller(self):
        for piste, nom in NOMS_PISTES:
            self.c.essayer("timeline.setTrack", {"track": piste, "name": nom}) if hasattr(self.c, "essayer") else \
                self.c.cmd("timeline.setTrack", {"track": piste, "name": nom})
        st = self.m.get("sous_titres")
        if st:
            self.c.cmd("captions.import", {"path": os.path.abspath(st), "name": "Subtitles"})
            self.notes.append("subtitles imported: %s" % os.path.basename(st))

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
            # title cards: the text comes in and goes out with the black
            if p["type"] == "carton" and p["n"] in self.clips_v2 and not (prev and prev.get("carton")):
                self.transitions.append(("V2", "in", p["n"], self.c.cmd("sequence.applyVideoTransition",
                                                                         {"clip": self.clips_v2[p["n"]], "effect": "cross_dissolve", "frames": d, "edge": "in"})))
            if p["type"] == "noir" and prev is not None and prev["type"] == "carton" and prev["n"] in self.clips_v2:
                self.transitions.append(("V2", "out", prev["n"], self.c.cmd("sequence.applyVideoTransition",
                                                                            {"clip": self.clips_v2[prev["n"]], "effect": "cross_dissolve", "frames": d, "edge": "out"})))

    # 8. markers
    def marqueurs(self):
        for mk in self.m.get("marqueurs", []):
            prm = {"target": "program", "time": self.ticks(mk["debut_img"]), "name": mk.get("nom") or "", "comment": mk.get("texte") or ""}
            if mk.get("duree_img"):
                prm["durationFrames"] = int(mk["duree_img"])
            self.c.cmd("markers.add", prm)

    # 9. check
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
                self.ecarts.append("shot %d missing from V1" % p["n"])
                continue
            vals = (img(it["start"]), img(it["end"]), img(it["sourceIn"]), img(it["sourceOut"]))
            att = (p["debut_img"], p["debut_img"] + p["duree_img"], p["entree_img"], p["sortie_img"])
            if vals != att:
                self.ecarts.append("shot %d: FilmCraft %s ≠ edit %s" % (p["n"], vals, att))
        attendus_v1 = len(images) + sum(1 for p in self.m["plans"] if p["type"] == "carton" and p["n"] in self.clips_v1)
        if len(v[0]["items"]) != attendus_v1:
            self.ecarts.append("V1: %d items, %d expected" % (len(v[0]["items"]), attendus_v1))
        if len(v[1]["items"]) != len(self.clips_v2):
            self.ecarts.append("V2: %d items, %d title cards" % (len(v[1]["items"]), len(self.clips_v2)))
        a = r["audio"]
        a1 = {it["clip"]: it for it in a[0]["items"]}
        for (n, clip), q in zip(self.clips_a, self.m.get("paroles", [])):
            it = a1.get(clip)
            if it is None or (img(it["start"]), img(it["end"]), img(it["sourceIn"])) != (q["debut_img"], q["debut_img"] + q["duree_img"], q["entree_img"]):
                self.ecarts.append("speech %d: position or in point" % n)
        if self.m.get("musique"):
            it = {x["clip"]: x for x in a[1]["items"]}.get(self.clip_musique)
            if it is None or img(it["end"]) - img(it["start"]) != self.m["musique"]["duree_img"]:
                self.ecarts.append("music missing or wrong duration")
            elif self.m["musique"].get("niveau_db"):
                vol = next((e for e in it.get("effects", []) if e.get("effect") == "volume"), None)
                if vol is None or "%.1f" % float(self.m["musique"]["niveau_db"]) not in str(vol["params"].get("level")):
                    self.ecarts.append("music level not applied")
        if self.clips_sons:
            a3 = {x["clip"] for x in a[2]["items"]}
            manquants = [n for n, c in self.clips_sons if c not in a3]
            if manquants:
                self.ecarts.append("sounds missing from A3: %s" % manquants)
        # transitions: count, alignment and position
        tv = {tr["id"]: tr for t in v for tr in t.get("transitions", [])}
        for piste, bord, n, res in self.transitions:
            tid = (res or {}).get("transition")
            tr = tv.get(tid)
            if tr is None:
                self.ecarts.append("transition of shot %d missing" % n)
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
                self.ecarts.append("transition of shot %d: %s at %d, expected %s at %d" % (n, tr.get("align"), debut, t_att[0], t_att[1]))
        if img(r["duration"]) != self.m["duree_img"]:
            # a sequence ends at its last item: a final black does not count
            dernier = self.m["plans"][-1]
            if not (dernier["type"] == "noir" and img(r["duration"]) == dernier["debut_img"]):
                self.ecarts.append("duration %d ≠ %d frames" % (img(r["duration"]), self.m["duree_img"]))
        return r

    # 10 bis. app capture and edit map
    def capture(self, chemin):
        fc.activer()
        self.c.essayer("sequence.open", {"item": self.seq}) if hasattr(self.c, "essayer") else None
        for z in ("view.zoomToSequence", "timeline.zoomToSequence", "timeline.zoomToFit"):
            if hasattr(self.c, "essayer") and self.c.essayer(z, {})[0]:
                break
        r = self.c.requete("ui.screenshot", {"path": chemin}) if hasattr(self.c, "requete") else {"ok": False}
        if r.get("ok") and os.path.exists(chemin):
            self.notes.append("FilmCraft capture: %s" % chemin)
        else:
            self.notes.append("capture failed (%s)" % (r.get("error") or "simulation"))

    def carte(self, chemin, insp):
        fps = self.fps
        s_ = lambda ticks: float(Fraction(int(ticks)) / TICKS_PAR_S)
        m = self.m
        L = ["# Edit map \"%s\"" % (self.a.nom or m["titre"]), "",
             "%d × %d, %s fps, %.2f s. Each track has a role. Retouch in FilmCraft, then read it back (`fc.py inspecter`, "
             "`lire_timeline.py`) and carry the changes into `montage.json`." % (m["format"]["largeur"], m["format"]["hauteur"],
                                                                         m["format"]["fps"], m["duree_img"] / float(fps)), "",
             "| Track | Role | Items | From → to | What to know |", "|---|---|---|---|---|"]
        roles = {
            "V1": "the shots, end to end, no gaps (a gap = a black)",
            "V2": "title cards and text, editable native titles",
            "A1": "each speech item or voice-over line at its time; Essential Sound type \"dialogue\"",
            "A2": "the music; its level, its fade-out, and its ducking under the speech (generated volume keyframes)",
            "A3": "picture sound and one-off sound effects (gestures, clicks)",
        }
        if insp:
            for k, t in enumerate(insp.get("video", [])[:2] + insp.get("audio", [])[:3]):
                piste = (["V1", "V2"] + ["A1", "A2", "A3"])[k]
                its = t.get("items", [])
                deb = "%.2f → %.2f s" % (s_(its[0]["start"]), s_(its[-1]["end"])) if its else "—"
                L.append("| %s · %s | %s | %d | %s | %s |" % (piste, dict(NOMS_PISTES)[piste], roles[piste], len(its), deb,
                                                             "%d transition(s)" % len(t.get("transitions", [])) if t.get("transitions") else ""))
        if m.get("sous_titres"):
            L.append("| C1 · Subtitles | the subtitles, imported from `%s`; one subtitle = one spoken sentence | — | — | "
                     "retouch them in the Subtitles panel; redo the SRT to keep the changes |" % os.path.basename(m["sous_titres"]))
        L += ["", "Markers: %d (structure beats, title cards)." % len(m.get("marqueurs", []))]
        if self.attenuation is not None:
            L.append("Ducking: generated by FilmCraft on the music (%s)." % json.dumps(self.attenuation, ensure_ascii=False)[:160])
        with open(chemin, "w", encoding="utf-8") as f:
            f.write("\n".join(L) + "\n")
        self.notes.append("edit map: %s" % chemin)

    # 10. check frames
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
    ap = argparse.ArgumentParser(description="montage.json -> FilmCraft sequence")
    ap.add_argument("montage")
    ap.add_argument("--projet", choices=["nouveau", "ouvert"], default="nouveau")
    ap.add_argument("--nom", help="sequence name (default: edit title)")
    ap.add_argument("--images", help="folder for the check frames (one per shot) and the contact sheet")
    ap.add_argument("--enregistrer", help="a .fcproj path that does not exist yet")
    ap.add_argument("--rendre", help="H.264 video (.mp4) that does not exist yet: the whole edit, final black included")
    ap.add_argument("--capture", help="PNG capture of the FilmCraft window, sequence open")
    ap.add_argument("--carte", help="edit map in Markdown (tracks, roles, items)")
    ap.add_argument("--rapport")
    ap.add_argument("--port", type=int, default=9876)
    ap.add_argument("--simulation", action="store_true")
    a = ap.parse_args(argv)
    if a.images:
        a.images = os.path.abspath(a.images)    # FilmCraft does not share our working directory: absolute paths only
    if a.rendre:
        a.rendre = os.path.abspath(a.rendre)
        if os.path.exists(a.rendre):
            print("refused: %s already exists; the skill never writes over a file" % a.rendre)
            return 1
    m, fautes = charger_montage(a.montage)
    absents = []
    if not fautes:
        fautes, absents = verifier_sources(m)
    if fautes:
        print("inconsistent edit:\n  " + "\n  ".join(fautes))
        return 1
    for x in absents:
        print("  warning: file not found (FilmCraft will not be able to import it): %s" % x)
    if a.enregistrer and os.path.exists(a.enregistrer):
        print("refused: %s already exists; the skill never saves over a project" % a.enregistrer)
        return 1
    if a.simulation:
        client = Simule()
    else:
        if not fc.lancer(a.port):
            print("FilmCraft unreachable on port %d: open -a FilmCraft --args --control %d; or use --simulation" % (a.port, a.port))
            return 2
        client = fc.Client(a.port, relance=True)
    b = Constructeur(m, client, a)
    try:
        nom = b.preparer()
        b.sequence(nom)
        b.piste_v1()
        b.piste_v2()
        b.pistes_son()
        b.habiller()
        b.transitions_()
        b.marqueurs()
        insp = b.verifier()
        if a.carte:
            b.carte(os.path.abspath(a.carte), insp)
        if a.capture and not a.simulation:
            b.capture(os.path.abspath(a.capture))
        planche = None
        if a.images and not a.simulation:
            planche, n = b.images(a.images)
            b.notes.append("%d check frames%s" % (n, ("; contact sheet: %s" % planche) if planche else ""))
        if a.rendre:
            r = client.cmd("file.exportMedia", {"path": a.rendre, "format": "h264", "sequence": b.seq, "range": "custom",
                                                "startSeconds": 0, "endSeconds": i2s(m["duree_img"], m["format"]["fps"]),
                                                "wait": True}, delai=900)
            if not a.simulation:
                n_img = ((r or {}).get("result") or {}).get("frames")
                b.notes.append("rendered video: %s (%s frames)" % (a.rendre, n_img))
                if n_img is not None and int(n_img) != int(m["duree_img"]):
                    b.ecarts.append("rendered video: %s frames, %d expected" % (n_img, m["duree_img"]))
        if a.enregistrer and not a.simulation:
            client.cmd("file.saveAs", {"path": os.path.abspath(a.enregistrer)}, autoriser=True)
            b.notes.append("project saved: %s" % os.path.abspath(a.enregistrer))
    except fc.Erreur as e:
        print("FilmCraft refused a command: %s" % e)
        return 1
    rapport = {"sequence": b.seq, "nom": nom, "plans_v1": len(b.clips_v1), "cartons_v2": len(b.clips_v2),
               "paroles": len(b.clips_a), "musique": bool(b.clip_musique), "sons": len(b.clips_sons), "transitions": len(b.transitions),
               "ecarts": b.ecarts, "notes": b.notes}
    if a.simulation:
        rapport["commandes"] = client.journal
    if a.rapport:
        with open(a.rapport, "w", encoding="utf-8") as f:
            json.dump(rapport, f, ensure_ascii=False, indent=1)
    print("FilmCraft%s: sequence \"%s\" (id %s) — %d shots on V1, %d title cards on V2, %d speech items, %s, %d sounds, %d transitions" % (
        " (simulation)" if a.simulation else "", nom, b.seq, len(b.clips_v1), len(b.clips_v2), len(b.clips_a),
        "music" if b.clip_musique else "no music", len(b.clips_sons), len(b.transitions)))
    for x in b.notes:
        print("  " + x)
    if a.simulation:
        for k, c in enumerate(client.journal, 1):
            p = json.dumps(c["params"], ensure_ascii=False)
            print("  %3d  %-34s %s" % (k, c["command"], p if len(p) <= 110 else p[:109] + "…"))
        print("  %d commands listed above, none sent%s" % (
            len(client.journal), ("; full parameters in %s" % a.rapport) if a.rapport else "; full parameters with --rapport"))
        if a.images:
            print("  --images ignored in simulation (no frame to export)")
        return 0
    if b.ecarts:
        print("check: %d mismatch(es)\n  " % len(b.ecarts) + "\n  ".join(b.ecarts))
        return 3
    print("check (sequence.inspect): every shot, speech item and transition is in place, to the frame")
    return 0


if __name__ == "__main__":
    sys.exit(main())
