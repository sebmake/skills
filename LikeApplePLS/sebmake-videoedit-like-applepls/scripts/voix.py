#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""voix.py : une voix off de synthèse quand l'utilisateur n'a pas de voix enregistrée.

Moteurs, du meilleur au repli :
  edge-tts   voix neuronales très naturelles (Vivienne, Denise, Henri, Rémy, Éloïse…), gratuites, sans compte.
             Passe par le service en ligne de Microsoft (internet requis ; service non officiel : parfait pour
             l'interne et les brouillons, à signaler pour un film publié). À installer une fois, avec l'accord de
             l'utilisateur :  python3 -m venv ~/.venv-sebmake-voix && ~/.venv-sebmake-voix/bin/pip install edge-tts
  say        la synthèse de macOS (Thomas, Amélie…), déjà installée, robotique : seulement pour caler un brouillon.

  python3 voix.py etat                                      quels moteurs sont là, et la commande d'installation
  python3 voix.py audition phrases.txt [--voix Vivienne,Denise,Henri,Remy,Eloise] [--lignes 1,2] [--sortie audition/]
                                                            les mêmes phrases dans plusieurs voix, à faire écouter
  python3 voix.py generer phrases.txt --voix Vivienne [--vitesse -4%] [--sortie voix/] [--moteur edge|say]
                                                            un fichier par phrase + voix.json (durée, instant de chaque mot)

phrases.txt : une phrase par ligne, telle qu'elle sera dite (les lignes vides sont ignorées). Les textes sont ceux de
l'utilisateur, ou proposés puis validés par lui : jamais générés sans son accord.

voix.json : [{"n", "fichier", "texte", "duree_s", "mots": [{"t", "fin", "mot"}]}] — les temps sont relatifs au début de
la phrase. Ils servent à placer les phrases sans chevauchement, à poser un mouvement ou un clic sur le mot qui
l'annonce, et à tirer les sous-titres. Avec `say`, pas d'instant des mots (liste vide).

Le Python qui porte edge-tts : $SEBMAKE_VOIX_PY, sinon ~/.venv-sebmake-voix/bin/python, sinon celui-ci.
Codes : 0 succès ; 1 erreur ; 2 moteur absent (la commande d'installation est imprimée). Python 3.9 ; ffmpeg, ffprobe.
"""
import json
import os
import subprocess
import sys
import tempfile
import time

VOIX = {   # noms courts → voix edge-tts (français) ; un nom complet (xx-XX-…Neural) passe tel quel
    "vivienne": "fr-FR-VivienneMultilingualNeural", "denise": "fr-FR-DeniseNeural", "henri": "fr-FR-HenriNeural",
    "remy": "fr-FR-RemyMultilingualNeural", "rémy": "fr-FR-RemyMultilingualNeural", "eloise": "fr-FR-EloiseNeural",
    "éloïse": "fr-FR-EloiseNeural",
}
VOIX_SAY = {"thomas": "Thomas", "amelie": "Amélie", "amélie": "Amélie"}
INSTALLER = "python3 -m venv ~/.venv-sebmake-voix && ~/.venv-sebmake-voix/bin/pip install edge-tts"

EDGE = r'''
import asyncio, json, sys, edge_tts
texte, voix, vitesse, sortie = sys.argv[1:5]
async def go():
    try:
        c = edge_tts.Communicate(texte, voix, rate=vitesse, boundary="WordBoundary")
    except TypeError:
        c = edge_tts.Communicate(texte, voix, rate=vitesse)
    mots = []
    with open(sortie, "wb") as f:
        async for m in c.stream():
            if m["type"] == "audio":
                f.write(m["data"])
            elif m["type"] == "WordBoundary":
                mots.append({"t": round(m["offset"] / 1e7, 3), "fin": round((m["offset"] + m["duration"]) / 1e7, 3), "mot": m["text"]})
    print(json.dumps(mots, ensure_ascii=False))
asyncio.run(go())
'''


def python_edge():
    for p in (os.environ.get("SEBMAKE_VOIX_PY"), os.path.expanduser("~/.venv-sebmake-voix/bin/python"), sys.executable):
        if p and os.path.exists(p):
            r = subprocess.run([p, "-c", "import edge_tts"], capture_output=True)
            if r.returncode == 0:
                return p
    return None


def a_say():
    return sys.platform == "darwin" and subprocess.run(["which", "say"], capture_output=True).returncode == 0


def duree(chemin):
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", chemin],
                       capture_output=True, text=True)
    return round(float(r.stdout.strip()), 3)


def dire_edge(py, texte, voix, vitesse, sortie):
    v = VOIX.get(voix.lower(), voix)
    for essai in range(3):   # le service renvoie parfois « No audio was received » : un échec passager, vu au test
        r = subprocess.run([py, "-c", EDGE, texte, v, vitesse, sortie], capture_output=True, text=True)
        if not r.returncode and os.path.exists(sortie) and os.path.getsize(sortie) > 0:
            break
        time.sleep(1.5 * (essai + 1))
    if r.returncode or not os.path.exists(sortie) or os.path.getsize(sortie) == 0:
        raise RuntimeError("edge-tts a échoué (internet ? voix « %s » ?) : %s" % (v, (r.stderr or "").strip()[-300:]))
    return json.loads(r.stdout.strip() or "[]")


def dire_say(texte, voix, sortie):
    v = VOIX_SAY.get(voix.lower(), voix if voix.lower() not in VOIX else "Thomas")
    with tempfile.TemporaryDirectory() as d:
        aiff = os.path.join(d, "v.aiff")
        r = subprocess.run(["say", "-v", v, "-o", aiff, texte], capture_output=True, text=True)
        if r.returncode:
            raise RuntimeError("say a échoué (voix « %s » installée ?) : %s" % (v, r.stderr.strip()))
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", aiff, "-b:a", "128k", sortie], check=True)
    return []


def lire_phrases(chemin):
    return [l.strip() for l in open(chemin, encoding="utf-8") if l.strip()]


def options(argv):
    o, pos, i = {}, [], 0
    while i < len(argv):
        if argv[i].startswith("--") and i + 1 < len(argv):
            o[argv[i][2:]] = argv[i + 1]
            i += 2
        else:
            pos.append(argv[i])
            i += 1
    return o, pos


def moteur(o):
    py = python_edge()
    voulu = o.get("moteur", "edge" if py else "say")
    if voulu == "edge" and not py:
        print("edge-tts n'est pas installé. Pour de meilleurs résultats (voix naturelles, gratuites), avec votre accord :\n  " + INSTALLER)
        sys.exit(2)
    if voulu == "say" and not a_say():
        print("aucun moteur de voix disponible : installer edge-tts :\n  " + INSTALLER)
        sys.exit(2)
    return voulu, py


def main(argv):
    if not argv or argv[0] in ("-h", "--help"):
        print(__doc__)
        return 0
    act = argv[0]
    o, pos = options(argv[1:])
    if act == "etat":
        py = python_edge()
        print("edge-tts : %s" % ("installé (%s)" % py if py else "absent — pour de meilleurs résultats, avec accord :\n  " + INSTALLER))
        print("say (macOS) : %s" % ("disponible, en repli pour un brouillon" if a_say() else "absent"))
        return 0
    if act not in ("audition", "generer"):
        print(__doc__)
        return 1
    phrases = lire_phrases(pos[0])
    eng, py = moteur(o)
    vitesse = o.get("vitesse", "-4%")
    if act == "audition":
        noms = [x.strip() for x in o.get("voix", "Vivienne,Denise,Henri,Remy,Eloise" if eng == "edge" else "Thomas,Amélie").split(",")]
        lignes = [int(x) - 1 for x in o.get("lignes", "1,2").split(",")]
        texte = " ".join(phrases[i] for i in lignes if i < len(phrases))
        dos = o.get("sortie", "audition")
        os.makedirs(dos, exist_ok=True)
        for v in noms:
            f = os.path.join(dos, "%s.mp3" % v.lower())
            (dire_edge(py, texte, v, vitesse, f) if eng == "edge" else dire_say(texte, v, f))
            print("%-10s %s (%.1f s)" % (v, f, duree(f)))
        print("à faire écouter : une voix se choisit à l'oreille, sur le même texte (moteur : %s)" % eng)
        return 0
    v = o.get("voix", "Vivienne" if eng == "edge" else "Thomas")
    dos = o.get("sortie", "voix")
    os.makedirs(dos, exist_ok=True)
    res = []
    for n, t in enumerate(phrases, 1):
        f = os.path.join(dos, "v%02d.mp3" % n)
        mots = dire_edge(py, t, v, vitesse, f) if eng == "edge" else dire_say(t, v, f)
        res.append({"n": n, "fichier": os.path.abspath(f), "texte": t, "duree_s": duree(f), "mots": mots})
        print("v%02d  %5.2f s  %s" % (n, res[-1]["duree_s"], t))
    json.dump({"moteur": eng, "voix": v, "vitesse": vitesse, "phrases": res}, open(os.path.join(dos, "voix.json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    print("%d phrases, %.1f s de voix au total ; voix.json dans %s (moteur %s, voix %s)" % (len(res), sum(r["duree_s"] for r in res), dos, eng, v))
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main(sys.argv[1:]))
    except RuntimeError as e:
        print("voix.py : %s" % e, file=sys.stderr)
        sys.exit(1)
