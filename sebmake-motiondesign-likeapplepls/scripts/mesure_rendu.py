#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""mesure_rendu.py: reads an MP4 render in numbers: where it moves, where it breathes, where it cuts, how it sounds.

  python3 mesure_rendu.py render.mp4                       energy map, rest, cuts, bursts, shots, sound
  python3 mesure_rendu.py render.mp4 --ref reference.mp4   the same reading of a reference, next to it
  python3 mesure_rendu.py render.mp4 --json measure.json

The energy map: one character per 1/12 s, one line per 4 s, from calm " " to cut "@". Energy is the
mean gray difference between two neighboring frames (0 to 255), read on the frame scaled down to 160 px wide.

  still        difference < 0.5: nothing moves       calm         difference < 2: almost nothing
  cut          difference >= 20 and >= 4 × the median of its neighbors: the image changes at once
  burst        at least 3 large changes (difference > 8) within 1.5 s
  shots        durations between two cuts; their coefficient of variation (standard deviation / mean) tells
               whether the film cuts to a metronome (low CV) or varies its durations

Guides (conventions of the skill, references/scene-demontee.md § 6). None blocks; each one is read:
  pace         shot CV >= 0.25 as soon as there are at least 3 cuts
  rest         >= 25 % still frames and a calm stretch of at least 1 s (pauses give gestures their weight)
  sound        peak <= -3 dBFS, no clipped sample; share of silence (50 ms windows under -40 dB)
A film edited the keynote way cuts often; a UI one-take almost never does. Compare
with a reference of the same kind (--ref) rather than with a threshold.

Python 3.9, no dependencies; ffmpeg and ffprobe.
"""
import json
import math
import operator
import re
import subprocess
import sys

CARACTERES = " .:-=+*#%@"
FPS_E, LARGEUR = 12, 160


def duree(video):
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", video],
                       capture_output=True, text=True, check=True)
    return float(r.stdout.strip())


def energie(video):
    sonde = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=width,height",
                            "-of", "csv=p=0", video], capture_output=True, text=True, check=True).stdout.strip().split(",")
    w, h = int(sonde[0]), int(sonde[1])
    H = max(2, int(round(LARGEUR * h / w / 2)) * 2)
    taille = LARGEUR * H
    p = subprocess.Popen(["ffmpeg", "-v", "error", "-i", video, "-vf", "fps=%d,scale=%d:%d,format=gray" % (FPS_E, LARGEUR, H),
                          "-f", "rawvideo", "-"], stdout=subprocess.PIPE)
    prec, ecarts = None, []
    while True:
        img = p.stdout.read(taille)
        if len(img) < taille:
            break
        if prec is not None:
            ecarts.append(sum(map(abs, map(operator.sub, img, prec))) / taille)
        prec = img
    p.wait()
    return ecarts


def lire_son(video):
    p = subprocess.run(["ffmpeg", "-v", "error", "-i", video, "-vn", "-ac", "1", "-ar", "8000", "-f", "s16le", "-"],
                       capture_output=True)
    brut = p.stdout
    if not brut:
        return None
    import array
    a = array.array("h")
    a.frombytes(brut[: len(brut) // 2 * 2])
    if sys.byteorder == "big":
        a.byteswap()
    crete = max(1, max(abs(x) for x in a))
    satures = sum(1 for x in a if x >= 32767 or x <= -32768)
    n = 400   # 50 ms
    silences, fen = 0, 0
    for i in range(0, len(a) - n + 1, n):
        rms = math.sqrt(sum(x * x for x in a[i:i + n]) / n) / 32768
        fen += 1
        if 20 * math.log10(rms + 1e-9) < -40:
            silences += 1
    out = {"crete_dbfs": round(20 * math.log10(crete / 32768), 1), "satures": satures,
           "silence": round(silences / max(1, fen), 3)}
    r = subprocess.run(["ffmpeg", "-nostats", "-i", video, "-vn", "-af", "ebur128=peak=true", "-f", "null", "-"],
                       capture_output=True, text=True)
    m = re.findall(r"I:\s+(-?[\d.]+) LUFS", r.stderr)
    tp = re.findall(r"Peak:\s+(-?[\d.]+) dBFS", r.stderr)
    if m:
        out["lufs"] = float(m[-1])
    if tp:
        out["crete_vraie_dbtp"] = float(tp[-1])
    return out


def analyser(video):
    E = energie(video)
    D = duree(video)
    n = len(E)
    pas = 1.0 / FPS_E
    coupes = []
    for i, e in enumerate(E):
        voisins = sorted(E[max(0, i - 3):i] + E[i + 1:i + 4]) or [0]
        med = voisins[len(voisins) // 2]
        if e >= 20 and e >= 4 * max(med, 0.5) and not (coupes and (i + 1) * pas - coupes[-1] < 0.2):
            coupes.append(round((i + 1) * pas, 2))   # two frames in a row above the threshold: a single cut
    immobile = sum(1 for e in E if e < 0.5) / max(1, n)
    calme = sum(1 for e in E if e < 2) / max(1, n)
    plus_long, cour = 0, 0
    for e in E:
        cour = cour + 1 if e < 2 else 0
        plus_long = max(plus_long, cour)
    grands = [(i + 1) * pas for i, e in enumerate(E) if e > 8]
    rafales, i = [], 0
    while i < len(grands):
        j = i
        while j + 1 < len(grands) and grands[j + 1] - grands[i] <= 1.5:
            j += 1
        if j - i + 1 >= 3:
            rafales.append([round(grands[i], 2), round(grands[j], 2)])
            i = j + 1
        else:
            i += 1
    bornes = [0.0] + coupes + [D]
    plans = [round(b - a, 2) for a, b in zip(bornes, bornes[1:]) if b - a > 0.05]
    cv = None
    if len(plans) >= 3:
        moy = sum(plans) / len(plans)
        cv = math.sqrt(sum((x - moy) ** 2 for x in plans) / len(plans)) / moy
    def car(e):
        if e < 0.5:
            return " "
        return CARACTERES[min(len(CARACTERES) - 1, 1 + int(math.log2(e / 0.5) * 1.2))]
    carte = []
    par = int(4 * FPS_E)
    for k in range(0, n, par):
        carte.append("%6.1fs |%s|" % (k * pas, "".join(car(e) for e in E[k:k + par]).ljust(par)))
    return {"fichier": video, "duree_s": round(D, 2), "immobile": round(immobile, 3), "calme": round(calme, 3),
            "plus_long_calme_s": round(plus_long * pas, 2), "coupes": coupes, "rafales": rafales, "plans_s": plans,
            "cv_plans": round(cv, 2) if cv is not None else None, "carte": carte, "son": lire_son(video)}


def reperes(m):
    L = []
    if m["cv_plans"] is not None:
        L.append(("pace", m["cv_plans"] >= 0.25, "shot CV %.2f (guide >= 0.25)" % m["cv_plans"]))
    else:
        L.append(("pace", None, "fewer than 3 cuts: one continuous piece, pace cannot be read"))
    L.append(("rest", m["immobile"] >= 0.25 and m["plus_long_calme_s"] >= 1.0,
              "still %.0f %%, longest calm %.1f s (guide >= 25 %% and >= 1 s)" % (100 * m["immobile"], m["plus_long_calme_s"])))
    L.append(("burst", bool(m["rafales"]) or None, "%d burst(s) %s" % (len(m["rafales"]), m["rafales"][:4])))
    s = m["son"]
    if s:
        L.append(("sound", s["crete_dbfs"] <= -3 and s["satures"] == 0,
                  "peak %.1f dBFS, %d clipped, silence %.0f %%%s" % (s["crete_dbfs"], s["satures"], 100 * s["silence"],
                                                                     (", %.1f LUFS" % s["lufs"]) if "lufs" in s else "")))
    else:
        L.append(("sound", None, "no audio track"))
    return L


def imprimer(m, titre):
    print("── %s · %s (%.2f s)" % (titre, m["fichier"], m["duree_s"]))
    for l in m["carte"]:
        print("  " + l)
    print("  cuts: %s" % (", ".join("%.2f" % c for c in m["coupes"]) or "none"))
    print("  shots: %s" % m["plans_s"][:20])
    for nom, ok, txt in reperes(m):
        etat = "ok" if ok else ("—" if ok is None else "off")
        print("  %-6s %-9s %s" % (etat, nom, txt))


def main(argv):
    if not argv or argv[0] in ("-h", "--help"):
        print(__doc__)
        return 0
    video = argv[0]
    ref = argv[argv.index("--ref") + 1] if "--ref" in argv else None
    m = analyser(video)
    imprimer(m, "render")
    out = {"rendu": m}
    if ref:
        r = analyser(ref)
        print()
        imprimer(r, "reference")
        out["reference"] = r
    if "--json" in argv:
        json.dump(out, open(argv[argv.index("--json") + 1], "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
