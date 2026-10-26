#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
fc.py : client du canal de contrôle de FilmCraft (Python 3.9, sans dépendance).

L'app doit être lancée avec son canal de contrôle :
    open -a FilmCraft --args --control 9876

Protocole : TCP 127.0.0.1:9876, une ligne JSON par requête {"id", "method", "params"}, une ligne JSON en réponse
{"id", "ok", "result" | "error"}. Méthodes : engine.commands (la liste des commandes), engine.execute
{"command", "params"} (une commande), ui.screenshot (capture de la fenêtre). Les inspections
(sequence.inspect, project.inspect, state.inspect) sont des COMMANDES : on les passe par engine.execute.
Temps : en « ticks » de 1/254 016 000 000 s (comme Premiere Pro) ; voir commun.TICKS_PAR_S.

Usage :
    python3 fc.py etat                                    projet, séquence active, sélection
    python3 fc.py commandes [filtre]                      commandes connues de l'app (avec leurs paramètres)
    python3 fc.py cmd <commande> ['<paramètres JSON>']    une commande (engine.execute)
    python3 fc.py inspecter [séquence]                    sequence.inspect, résumé lisible (pistes, plans, transitions)
    python3 fc.py image <temps_s> <sortie.png> [séquence] une image du programme (file.exportFrame)
    python3 fc.py capture <sortie.png>                    capture de la fenêtre (ui.screenshot)
    python3 fc.py raw '<requête JSON>'                    une méthode brute : {"method": ..., "params": ...}
    python3 fc.py activer                                 met l'app au premier plan

Options (ou variables d'environnement) :
    --port N      (FC_PORT, 9876)   port du canal de contrôle
    --delai S     (FC_DELAI, 120)   délai maximal d'une requête ; une app bloquée ne bloque pas le terminal
    --relance     sur délai dépassé : met l'app au premier plan et renvoie la requête une fois
    --brut        sortie complète (sinon tronquée à 2 000 caractères)
    --autoriser   autorise les commandes qui ouvrent, enregistrent, ferment ou suppriment (voir PROTEGEES)

Codes de sortie : 0 succès ; 1 erreur renvoyée par l'app ; 2 délai dépassé ; 3 aucune app à l'écoute ; 4 refusé.
"""
import json
import os
import socket
import subprocess
import sys
import time

APP = os.environ.get("FC_APP", "FilmCraft")
TICKS = 254016000000
# Commandes qui ouvrent, enregistrent, remplacent, ferment ou suppriment : refusées sans --autoriser.
PROTEGEES = {"file.save", "file.saveAs", "file.saveAll", "file.saveCopy", "file.saveAsTemplate", "file.open",
             "file.close", "file.closeProject", "file.closeAllProjects", "file.closeAllOtherProjects", "file.revert",
             "file.recover", "file.discardRecovery", "file.newProject", "file.newProjectFromTemplate",
             "file.openDemoProject", "file.projectManager", "project.delete", "media.makeOffline",
             "edit.removeUnused", "app.quit", "file.quit"}


class Erreur(Exception):
    pass


class Client:
    def __init__(self, port=None, delai=None, relance=False, autoriser=False):
        self.port = int(port or os.environ.get("FC_PORT", "9876"))
        self.delai = float(delai or os.environ.get("FC_DELAI", "120"))
        self.relance = relance
        self.autoriser = autoriser
        self.n = 0

    def requete(self, methode, params=None, delai=None):
        def une_fois():
            self.n += 1
            with socket.create_connection(("127.0.0.1", self.port), timeout=10) as s:
                s.settimeout(delai or self.delai)
                s.sendall((json.dumps({"id": self.n, "method": methode, "params": params or {}}) + "\n").encode("utf-8"))
                tampon = b""
                while not tampon.endswith(b"\n"):
                    bloc = s.recv(1 << 16)
                    if not bloc:
                        break
                    tampon += bloc
            return json.loads(tampon.decode("utf-8"))
        try:
            return une_fois()
        except (socket.timeout, TimeoutError):
            if not self.relance:
                raise
            activer()
            return une_fois()

    def cmd(self, commande, params=None, delai=None, autoriser=False):
        """engine.execute ; lève Erreur si l'app répond ok: false. Renvoie result."""
        if commande in PROTEGEES and not (self.autoriser or autoriser):
            raise PermissionError(commande)
        r = self.requete("engine.execute", {"command": commande, "params": params or {}}, delai)
        if not r.get("ok"):
            raise Erreur("%s : %s" % (commande, r.get("error")))
        return r.get("result")

    def essayer(self, commande, params=None):
        """Comme cmd, mais renvoie (ok, résultat ou message) au lieu de lever."""
        try:
            return True, self.cmd(commande, params)
        except Erreur as e:
            return False, str(e)

    def commandes(self):
        r = self.requete("engine.commands")
        return r.get("result") or []

    def en_ecoute(self):
        try:
            with socket.create_connection(("127.0.0.1", self.port), timeout=2):
                return True
        except OSError:
            return False


def activer():
    """Met l'app au premier plan (seul usage d'osascript)."""
    subprocess.run(["osascript", "-e", 'tell application "%s" to activate' % APP], check=False,
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(1.0)


def lancer(port=9876, attente=40):
    """Lance FilmCraft avec son canal de contrôle s'il n'écoute pas déjà ; renvoie True quand il répond."""
    c = Client(port)
    if c.en_ecoute():
        return True
    subprocess.run(["open", "-a", APP, "--args", "--control", str(port)], check=False)
    for _ in range(attente):
        time.sleep(1)
        if c.en_ecoute():
            time.sleep(1)
            return True
    return False


def resume_sequence(r, fps=None):
    """Texte lisible d'un sequence.inspect."""
    lignes = ["%s (id %s) : %.3f s, %s images" % (r.get("name"), r.get("id"), r.get("duration", 0) / TICKS, r.get("durationFrames"))]
    for genre in ("video", "audio"):
        for t in r.get(genre, []):
            lignes.append("  %s (%s) : %d éléments, %d transitions" % (t.get("name"), t.get("id"), len(t.get("items", [])),
                                                                       len(t.get("transitions", []))))
            for it in t.get("items", []):
                lignes.append("    %-4s %-28s %8.3f → %8.3f  source %7.3f → %7.3f" % (
                    it.get("clip"), (it.get("name") or "")[:28], it["start"] / TICKS, it["end"] / TICKS,
                    it.get("sourceIn", 0) / TICKS, it.get("sourceOut", 0) / TICKS))
            for tr in t.get("transitions", []):
                lignes.append("    ~ %-18s %8.3f + %.3f s (%s) %s→%s" % (tr.get("effect"), tr["start"] / TICKS, tr["duration"] / TICKS,
                                                                       tr.get("align"), tr.get("from"), tr.get("to")))
    return "\n".join(lignes)


def main(argv):
    port = delai = None
    relance = brut = autoriser = False
    pos, i = [], 0
    while i < len(argv):
        a = argv[i]
        if a == "--port":
            port = argv[i + 1]; i += 2
        elif a == "--delai":
            delai = argv[i + 1]; i += 2
        elif a == "--relance":
            relance = True; i += 1
        elif a == "--brut":
            brut = True; i += 1
        elif a == "--autoriser":
            autoriser = True; i += 1
        else:
            pos.append(a); i += 1
    if not pos:
        print(__doc__)
        return 1
    c = Client(port, delai, relance, autoriser)

    def montrer(x):
        t = json.dumps(x, ensure_ascii=False, indent=1)
        print(t if brut else t[:2000])
    act = pos[0]
    try:
        if act == "activer":
            activer(); print("premier plan : %s" % APP); return 0
        if act == "etat":
            p = c.cmd("project.inspect")
            s = c.cmd("state.inspect")
            print("projet : %s (%s)%s ; séquence active : %s ; séquences ouvertes : %s" % (
                p.get("name"), p.get("path") or "jamais enregistré", " — modifié" if p.get("dirty") else "",
                s.get("active_sequence"), s.get("open_sequences")))
            return 0
        if act == "commandes":
            filtre = pos[1].lower() if len(pos) > 1 else ""
            for x in c.commandes():
                if filtre in x.get("id", "").lower():
                    print("%s%s  %s" % (x.get("id"), "" if x.get("enabled", True) else " [inactive]", (x.get("params") or "") if brut else (x.get("params") or "")[:160]))
            return 0
        if act == "cmd":
            montrer(c.cmd(pos[1], json.loads(pos[2]) if len(pos) > 2 else {}))
            return 0
        if act == "inspecter":
            r = c.cmd("sequence.inspect", {"item": int(pos[1])} if len(pos) > 1 else {})
            print(resume_sequence(r) if not brut else json.dumps(r, ensure_ascii=False, indent=1))
            return 0
        if act == "image":
            p = {"path": os.path.abspath(pos[2]), "format": "png", "target": "program", "time": int(round(float(pos[1]) * TICKS))}
            if len(pos) > 3:
                p["sequence"] = int(pos[3])
            montrer(c.cmd("file.exportFrame", p))
            return 0
        if act == "capture":
            r = c.requete("ui.screenshot")
            if r.get("ok"):
                import shutil
                shutil.copy(r["result"]["path"], os.path.abspath(pos[1]))
                print("capture : %s (%sx%s)" % (os.path.abspath(pos[1]), r["result"].get("width"), r["result"].get("height")))
                return 0
            montrer(r)
            return 1
        if act == "raw":
            q = json.loads(pos[1])
            if q.get("method") == "engine.execute" and (q.get("params") or {}).get("command") in PROTEGEES and not autoriser:
                raise PermissionError(q["params"]["command"])
            montrer(c.requete(q["method"], q.get("params")))
            return 0
        print(__doc__)
        return 1
    except PermissionError as e:
        print("refusé : %s ouvre, enregistre, ferme ou supprime (ajouter --autoriser si c'est voulu)" % e)
        return 4
    except (socket.timeout, TimeoutError):
        print("délai dépassé : l'app ne répond plus. Essayer : python3 fc.py activer")
        return 2
    except (ConnectionRefusedError, OSError) as e:
        if isinstance(e, ConnectionRefusedError) or "Connection refused" in str(e):
            print("aucune app à l'écoute : open -a %s --args --control %s" % (APP, port or 9876))
            return 3
        raise
    except Erreur as e:
        print(str(e))
        return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
