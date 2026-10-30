#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
fc.py: client for the FilmCraft control channel (Python 3.9, no dependencies).

The app must be launched with its control channel:
    open -a FilmCraft --args --control 9876

Protocol: TCP 127.0.0.1:9876, one JSON line per request {"id", "method", "params"}, one JSON line in reply
{"id", "ok", "result" | "error"}. Methods: engine.commands (the list of commands), engine.execute
{"command", "params"} (one command), ui.screenshot (window capture). The inspections
(sequence.inspect, project.inspect, state.inspect) are COMMANDS: send them through engine.execute.
Time: in "ticks" of 1/254,016,000,000 s (as in Premiere Pro); see commun.TICKS_PAR_S.

Usage:
    python3 fc.py etat                                    project, active sequence, selection
    python3 fc.py commandes [filter]                      commands the app knows (with their parameters)
    python3 fc.py cmd <command> ['<JSON parameters>']     one command (engine.execute)
    python3 fc.py inspecter [sequence]                    sequence.inspect, readable summary (tracks, shots, transitions)
    python3 fc.py image <time_s> <output.png> [sequence]  one frame of the program (file.exportFrame)
    python3 fc.py capture <output.png>                    window capture (ui.screenshot)
    python3 fc.py raw '<JSON request>'                    a raw method: {"method": ..., "params": ...}
    python3 fc.py activer                                 brings the app to the front

Options (or environment variables):
    --port N      (FC_PORT, 9876)   control channel port
    --delai S     (FC_DELAI, 120)   maximum time for a request; a stuck app does not block the terminal
    --relance     on timeout: bring the app to the front and resend the request once
    --brut        full output (otherwise cut at 2,000 characters)
    --autoriser   allow commands that open, save, close or delete (see PROTEGEES)

Exit codes: 0 success; 1 error returned by the app; 2 timeout; 3 no app listening; 4 refused.
"""
import json
import os
import socket
import subprocess
import sys
import time

APP = os.environ.get("FC_APP", "FilmCraft")
TICKS = 254016000000
# Commands that open, save, replace, close or delete: refused without --autoriser.
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
        """engine.execute; raises Erreur if the app replies ok: false. Returns result."""
        if commande in PROTEGEES and not (self.autoriser or autoriser):
            raise PermissionError(commande)
        r = self.requete("engine.execute", {"command": commande, "params": params or {}}, delai)
        if not r.get("ok"):
            raise Erreur("%s : %s" % (commande, r.get("error")))
        return r.get("result")

    def essayer(self, commande, params=None):
        """Like cmd, but returns (ok, result or message) instead of raising."""
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
    """Brings the app to the front (the only use of osascript)."""
    subprocess.run(["osascript", "-e", 'tell application "%s" to activate' % APP], check=False,
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(1.0)


def lancer(port=9876, attente=40):
    """Launches FilmCraft with its control channel if it is not already listening; returns True when it replies."""
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
    """Readable text of a sequence.inspect."""
    lignes = ["%s (id %s): %.3f s, %s frames" % (r.get("name"), r.get("id"), r.get("duration", 0) / TICKS, r.get("durationFrames"))]
    for genre in ("video", "audio"):
        for t in r.get(genre, []):
            lignes.append("  %s (%s): %d items, %d transitions" % (t.get("name"), t.get("id"), len(t.get("items", [])),
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
            activer(); print("in front: %s" % APP); return 0
        if act == "etat":
            p = c.cmd("project.inspect")
            s = c.cmd("state.inspect")
            print("project: %s (%s)%s; active sequence: %s; open sequences: %s" % (
                p.get("name"), p.get("path") or "never saved", " — modified" if p.get("dirty") else "",
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
                print("capture: %s (%sx%s)" % (os.path.abspath(pos[1]), r["result"].get("width"), r["result"].get("height")))
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
        print("refused: %s opens, saves, closes or deletes (add --autoriser if you mean it)" % e)
        return 4
    except (socket.timeout, TimeoutError):
        print("timeout: the app no longer replies. Try: python3 fc.py activer")
        return 2
    except (ConnectionRefusedError, OSError) as e:
        if isinstance(e, ConnectionRefusedError) or "Connection refused" in str(e):
            print("no app listening: open -a %s --args --control %s" % (APP, port or 9876))
            return 3
        raise
    except Erreur as e:
        print(str(e))
        return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
