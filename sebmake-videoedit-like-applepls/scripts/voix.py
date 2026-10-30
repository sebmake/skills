#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""voix.py: a synthetic voice-over when the user has no recorded voice.

Engines, from best to fallback:
  edge-tts   very natural neural voices (Vivienne, Denise, Henri, Rémy, Éloïse…), free, no account.
             Goes through Microsoft's online service (internet required; unofficial service: fine for internal
             use and drafts, flag it for a published film). Install once, with the user's
             consent:  python3 -m venv ~/.venv-sebmake-voix && ~/.venv-sebmake-voix/bin/pip install edge-tts
  say        macOS speech synthesis (Thomas, Amélie…), already installed, robotic: only to time a draft.

  python3 voix.py etat                                      which engines are present, and the install command
  python3 voix.py audition phrases.txt [--voix Vivienne,Denise,Henri,Remy,Eloise] [--lignes 1,2] [--sortie audition/]
                                                            the same sentences in several voices, for listening
  python3 voix.py generer phrases.txt --voix Vivienne [--vitesse -4%] [--sortie voix/] [--moteur edge|say]
                                                            one file per sentence + voix.json (duration, time of each word)

phrases.txt: one sentence per line, as it will be spoken (blank lines are ignored). The texts are the user's,
or proposed and then approved by them: never generated without their consent.

voix.json: [{"n", "fichier", "texte", "duree_s", "mots": [{"t", "fin", "mot"}]}]. Times are relative to the start of
the sentence. They are used to place sentences without overlap, to put a move or a click on the word that
announces it, and to build the subtitles. With `say`, there are no word times (empty list).

The Python that runs edge-tts: $SEBMAKE_VOIX_PY, else ~/.venv-sebmake-voix/bin/python, else this one.
Exit codes: 0 success; 1 error; 2 engine missing (the install command is printed). Python 3.9; ffmpeg, ffprobe.
"""
import json
import os
import subprocess
import sys
import tempfile
import time

VOIX = {   # short names -> edge-tts voices (French); a full name (xx-XX-…Neural) passes through as is
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
    for essai in range(3):   # the service sometimes returns "No audio was received": a transient failure, seen in testing
        r = subprocess.run([py, "-c", EDGE, texte, v, vitesse, sortie], capture_output=True, text=True)
        if not r.returncode and os.path.exists(sortie) and os.path.getsize(sortie) > 0:
            break
        time.sleep(1.5 * (essai + 1))
    if r.returncode or not os.path.exists(sortie) or os.path.getsize(sortie) == 0:
        raise RuntimeError("edge-tts failed (internet? voice \"%s\"?): %s" % (v, (r.stderr or "").strip()[-300:]))
    return json.loads(r.stdout.strip() or "[]")


def dire_say(texte, voix, sortie):
    v = VOIX_SAY.get(voix.lower(), voix if voix.lower() not in VOIX else "Thomas")
    with tempfile.TemporaryDirectory() as d:
        aiff = os.path.join(d, "v.aiff")
        r = subprocess.run(["say", "-v", v, "-o", aiff, texte], capture_output=True, text=True)
        if r.returncode:
            raise RuntimeError("say failed (is voice \"%s\" installed?): %s" % (v, r.stderr.strip()))
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
        print("edge-tts is not installed. For better results (natural, free voices), with your consent:\n  " + INSTALLER)
        sys.exit(2)
    if voulu == "say" and not a_say():
        print("no voice engine available: install edge-tts:\n  " + INSTALLER)
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
        print("edge-tts: %s" % ("installed (%s)" % py if py else "missing — for better results, with consent:\n  " + INSTALLER))
        print("say (macOS): %s" % ("available, as a fallback for a draft" if a_say() else "missing"))
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
        print("play these to the user: choose a voice by ear, on the same text (engine: %s)" % eng)
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
    print("%d sentences, %.1f s of voice-over in total; voix.json in %s (engine %s, voice %s)" % (len(res), sum(r["duree_s"] for r in res), dos, eng, v))
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main(sys.argv[1:]))
    except RuntimeError as e:
        print("voix.py: %s" % e, file=sys.stderr)
        sys.exit(1)
