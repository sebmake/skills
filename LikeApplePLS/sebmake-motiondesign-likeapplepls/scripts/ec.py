#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ec.py : client du canal de contrôle d'EffectCraft (Python 3.9, sans dépendance).

L'app doit être lancée avec son canal de contrôle :
    open -a EffectCraft --args --control 9877

Usage :
    python3 ec.py script <fichier.jsx>                  exécute un script (JavaScript des scripts After Effects)
    python3 ec.py code '<javascript>'                   exécute un bout de code
    python3 ec.py frame "<comp>" <temps_s> <sortie.png> [côté_max]
                                                        une image de contrôle
    python3 ec.py frames "<comp>" <dossier> [--pas 0.5] [--debut 0] [--fin <durée>] [--max 960]
                                                        une image toutes les --pas secondes
    python3 ec.py render "<comp>" <sortie.mp4> [--format h264] [--garder 1]
                                                        file de rendu → fichier vidéo (attend la fin) ; l'élément
                                                        rendu est retiré de la file, sauf avec --garder 1
    python3 ec.py cmd <commande> ['<paramètres JSON>']  une commande de engine.commands
    python3 ec.py raw '<requête JSON>'                  une méthode brute : {"method": ..., "params": ...}
    python3 ec.py commandes [filtre]                    liste des commandes connues de l'app
    python3 ec.py activer                               met l'app au premier plan (elle ne répond qu'ainsi)

Options communes (ou variables d'environnement) :
    --port N      (EC_PORT, 9877)      port du canal de contrôle
    --delai S     (EC_DELAI, 180)      délai maximal d'une requête ; une app bloquée ne bloque pas le terminal
    --relance     sur délai dépassé : met l'app au premier plan et renvoie la requête une fois
    --brut        (EC_BRUT=1)          sortie complète (sinon tronquée à 2 000 caractères)
    --autoriser   autorise les commandes qui touchent au projet entier (voir PROTEGEES)

Codes de sortie : 0 succès ; 1 erreur renvoyée par l'app ; 2 délai dépassé ; 3 aucune app à l'écoute ; 4 refusé.

Pièges connus (voir ../references/motion-spec.md, § 9) :
  - l'app ne traite les requêtes que si sa fenêtre est au premier plan : `activer`, ou --relance ;
  - editor.state est une commande (engine.execute), pas une méthode ;
  - un rendu long dépasse le délai par défaut : `render` prend --delai 1800 sauf mention contraire.
"""
import json
import os
import socket
import subprocess
import sys
import time

APP = os.environ.get("EC_APP", "EffectCraft")
# Commandes qui enregistrent, ouvrent, remplacent ou ferment le projet de l'utilisateur.
PROTEGEES = {"file.save", "file.saveAs", "file.open", "file.newProject", "file.revert", "file.close",
             "file.incrementAndSave", "file.openDemoProject", "app.quit", "file.quit", "project.deleteWithoutConfirmation"}


class Options:
    def __init__(self):
        self.port = int(os.environ.get("EC_PORT", "9877"))
        self.delai = float(os.environ.get("EC_DELAI", "180"))
        self.delai_donne = False
        self.relance = False
        self.brut = bool(os.environ.get("EC_BRUT"))
        self.autoriser = False
        self.reste = {}


def lire_options(argv):
    o, pos, i = Options(), [], 0
    while i < len(argv):
        a = argv[i]
        if a == "--port":
            o.port = int(argv[i + 1]); i += 2
        elif a == "--delai":
            o.delai = float(argv[i + 1]); o.delai_donne = True; i += 2
        elif a == "--relance":
            o.relance = True; i += 1
        elif a == "--brut":
            o.brut = True; i += 1
        elif a == "--autoriser":
            o.autoriser = True; i += 1
        elif a.startswith("--") and i + 1 < len(argv):
            o.reste[a[2:]] = argv[i + 1]; i += 2
        else:
            pos.append(a); i += 1
    return o, pos


def activer():
    """Met l'app au premier plan (seul usage d'osascript permis)."""
    subprocess.run(["osascript", "-e", 'tell application "%s" to activate' % APP], check=False,
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(1.0)


def requete(o, methode, params=None):
    def une_fois():
        with socket.create_connection(("127.0.0.1", o.port), timeout=10) as s:
            s.settimeout(o.delai)
            s.sendall((json.dumps({"id": 1, "method": methode, "params": params or {}}) + "\n").encode("utf-8"))
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
        if not o.relance:
            raise
        activer()
        return une_fois()


def executer(o, commande, params=None):
    if commande in PROTEGEES and not o.autoriser:
        raise PermissionError(commande)
    return requete(o, "engine.execute", {"command": commande, "params": params or {}})


def lancer_script(o, code, nom):
    r = executer(o, "script.run", {"code": code, "name": nom})
    res = r.get("result") or {}
    ok = bool(r.get("ok")) and not res.get("error")
    return ok, r, res


def afficher(o, r):
    texte = json.dumps(r, ensure_ascii=False)
    print(texte if o.brut else texte[:2000])


def duree_comp(o, comp):
    code = ('var c = null; for (var i = 1; i <= app.project.numItems; i++) { var it = app.project.item(i);'
            ' if (it instanceof CompItem && it.name === %s) { c = it; break; } } c ? String(c.duration) : "absente";') % json.dumps(comp)
    ok, r, res = lancer_script(o, code, "duree.jsx")
    v = res.get("result")
    try:
        return float(v)
    except (TypeError, ValueError):
        raise RuntimeError("composition introuvable : %s" % comp)


def main(argv):
    o, a = lire_options(argv)
    if not a:
        print(__doc__); return 1
    act = a[0]
    try:
        if act == "activer":
            activer(); print("premier plan : %s" % APP); return 0
        if act in ("script", "code"):
            code = open(a[1], encoding="utf-8-sig").read() if act == "script" else a[1]
            nom = os.path.basename(a[1]) if act == "script" else "code.jsx"
            ok, r, res = lancer_script(o, code, nom)
            if r.get("ok"):
                print(res.get("result"), "|", json.dumps(res.get("error"), ensure_ascii=False) if res.get("error") else "", res.get("output") or "")
            else:
                afficher(o, r)
            return 0 if ok else 1
        if act == "frame":
            r = requete(o, "render.frame", {"comp": a[1], "time": float(a[2]), "path": os.path.abspath(a[3]),
                                            "max_side": int(a[4]) if len(a) > 4 else 1920})
            afficher(o, r); return 0 if r.get("ok") else 1
        if act == "frames":
            comp, dossier = a[1], a[2]
            os.makedirs(dossier, exist_ok=True)
            pas = float(o.reste.get("pas", "0.5")); debut = float(o.reste.get("debut", "0"))
            fin = float(o.reste["fin"]) if "fin" in o.reste else duree_comp(o, comp) - 1e-3
            cote = int(o.reste.get("max", "960"))
            t, n, echecs = debut, 0, 0
            while t <= fin + 1e-9:
                chemin = os.path.abspath(os.path.join(dossier, "t%06.2f.png" % t))
                r = requete(o, "render.frame", {"comp": comp, "time": round(t, 4), "path": chemin, "max_side": cote})
                n += 1; echecs += 0 if r.get("ok") else 1
                if not r.get("ok"):
                    afficher(o, r)
                t += pas
            print("%d images dans %s (%d échecs)" % (n, dossier, echecs)); return 0 if not echecs else 1
        if act == "render":
            if not o.delai_donne:
                o.delai = 1800.0
            comp, sortie = a[1], os.path.abspath(a[2])
            fmt = o.reste.get("format", "h264")
            os.makedirs(os.path.dirname(sortie), exist_ok=True)
            r = executer(o, "renderQueue.add", {"comp": comp, "format": fmt, "output": sortie})
            if not r.get("ok"):
                afficher(o, r); return 1
            r = executer(o, "renderQueue.render", {"wait": True})
            existe = os.path.exists(sortie)
            if not o.brut:
                print("rendu : %s" % ("terminé" if r.get("ok") else json.dumps(r, ensure_ascii=False)[:2000]))
            else:
                afficher(o, r)
            if "garder" not in o.reste:
                # la file ne garde pas l'élément rendu (sinon elle s'allonge à chaque rendu)
                try:
                    lst = executer(o, "renderQueue.list", {}).get("result") or {}
                    for it in (lst.get("items") if isinstance(lst, dict) else lst) or []:
                        if os.path.abspath(str(it.get("outputPath") or "")) == sortie and it.get("status") == "Done":
                            executer(o, "renderQueue.remove", {"item": it.get("id")})
                except Exception:
                    pass
            print("fichier : %s (%s)" % (sortie, "%d octets" % os.path.getsize(sortie) if existe else "absent"))
            return 0 if r.get("ok") and existe else 1
        if act == "cmd":
            r = executer(o, a[1], json.loads(a[2]) if len(a) > 2 else {})
            afficher(o, r); return 0 if r.get("ok") else 1
        if act == "raw":
            q = json.loads(a[1])
            if q.get("method") == "engine.execute" and (q.get("params") or {}).get("command") in PROTEGEES and not o.autoriser:
                raise PermissionError(q["params"]["command"])
            r = requete(o, q["method"], q.get("params"))
            afficher(o, r); return 0 if r.get("ok") else 1
        if act == "commandes":
            r = requete(o, "engine.commands")
            filtre = a[1].lower() if len(a) > 1 else ""
            for c in r.get("result") or []:
                if filtre in c.get("id", "").lower():
                    print("%s  %s" % (c.get("id"), (c.get("params") or "")[:140]))
            return 0
        print(__doc__); return 1
    except PermissionError as e:
        print("refusé : %s touche au projet entier (ajouter --autoriser si c'est voulu)" % e); return 4
    except (socket.timeout, TimeoutError):
        print("délai dépassé (%.0f s) : l'app ne répond plus. Essayer : python3 ec.py activer" % o.delai); return 2
    except ConnectionRefusedError:
        print("aucune app à l'écoute sur %d : open -a %s --args --control %d" % (o.port, APP, o.port)); return 3
    except RuntimeError as e:
        print(str(e)); return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
