#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
mesure_video.py : bibliothèque de mesure commune à analyse_rushes.py et critique_montage.py.
Rien à lancer ici. Python 3.9, numpy, Pillow ; ffmpeg et ffprobe dans le PATH.

Base de lecture (la même que celle du corpus mesuré) :
  - toute vidéo est lue à 29,97 images/s (filtre fps de ffmpeg) ;
  - chaque image est réduite à 288 x 162, puis à 96 x 54 pour les coupes et le mouvement ;
  - les seuils de coupe, de fondu, de noir et la mesure du mouvement sont ceux qui ont servi
    à découper les films du corpus (seuils réglés sur extraits : convention).

Unités :
  - mouvement : somme, par seconde, des écarts moyens de gris (0-255) entre images successives
    (96 x 54). Moins de 10 = image fixe (convention du corpus). Caméra et sujet mêlés ;
  - luminance, saturation : 0 à 1 ;
  - netteté : variance du laplacien sur l'image 288 x 162 (valeur relative : à comparer
    entre prises d'un même tournage, pas entre deux scènes différentes) ;
  - caméra : déplacement global de l'image estimé par corrélation de phase (144 x 81),
    en % de la largeur de l'image.
"""
import json
import math
import os
import re
import subprocess
import sys
import unicodedata
import warnings
from concurrent.futures import ThreadPoolExecutor

try:
    import numpy as np
except ImportError:  # pragma: no cover
    # numpy manque ici : le script se relance avec le Python de ~/.venv-videoedit s'il existe (une seule fois)
    _VENV = os.path.expanduser("~/.venv-videoedit/bin/python")
    if (os.access(_VENV, os.X_OK) and not os.environ.get("VIDEOEDIT_RELANCE")
            and os.path.abspath(sys.executable) != os.path.abspath(_VENV) and sys.argv and os.path.isfile(sys.argv[0])):
        os.environ["VIDEOEDIT_RELANCE"] = "1"
        os.execv(_VENV, [_VENV] + sys.argv)
    if os.environ.get("VIDEOEDIT_RELANCE") or os.path.abspath(sys.executable) == os.path.abspath(_VENV):
        sys.stderr.write("numpy manque aussi dans ~/.venv-videoedit : ~/.venv-videoedit/bin/pip install numpy pillow\n")
    elif os.access(_VENV, os.X_OK):
        sys.stderr.write("numpy manque : lancer le script avec ~/.venv-videoedit/bin/python\n")
    else:
        sys.stderr.write(
            "numpy manque. Créer un environnement : python3 -m venv ~/.venv-videoedit && "
            "~/.venv-videoedit/bin/pip install numpy pillow ; les scripts s'en servent ensuite d'eux-mêmes.\n")
    raise SystemExit(2)

# numpy 2.0.x sur macOS arm64 (Accelerate) signale à tort « divide by zero / overflow / invalid value
# encountered in matmul » sur des produits justes : sans effet sur les mesures, donc tus.
warnings.filterwarnings("ignore", category=RuntimeWarning, message=r".*encountered in matmul")

FPS = 30000 / 1001
WB, HB = 288, 162          # image de lecture
W, H = 96, 54              # image réduite (coupes, mouvement, couleur) : bloc 3 x 3
WS, HS = 144, 81           # image de stabilité : bloc 2 x 2
WT, HT = 48, 27            # vignette de dérive : bloc 6 x 6

# Seuils du découpage du corpus (convention : réglés sur extraits)
DUP = 0.35
CUT_ABS = 5.0
CUT_PEAK = 2.0
CUT_BG = 3.0
CUT_NM = 0.55
# Images presque unies (fond uni, aplat, écran) : une vraie coupe y garde une différence normalisée faible.
# Un saut très fort et isolé entre deux images immobiles compte alors comme une coupe (convention de la skill,
# ajoutée après le calibrage du corpus ; une lumière qui monte sur la même image reste sous CUT_FLAT_NM).
CUT_FLAT_ABS = 40.0
CUT_FLAT_NM = 0.35
CUT_FLAT_ISOLE = 0.05
GRAD_MIN = 8.0
LIN_MAX = 0.35
GRAD_NM = 0.5
MIN_PLAN = 3
BLACK = 10.0
WHITE = 240.0
FIXE = 10.0                # mouvement sous lequel une image est fixe (convention du corpus)


# ---------------------------------------------------------------- outils

def fmt_s(t):
    """12.34 -> '12,3 s' (français)."""
    return ("%.1f s" % t).replace(".", ",")


def fmt_n(x, d=2):
    if x is None:
        return "—"
    return (("%." + str(d) + "f") % x).replace(".", ",")


def tc(t, fps=25.0, depart=0.0):
    """Timecode HH:MM:SS:FF (non drop frame) ; depart = timecode de la première image, en s."""
    t = max(0.0, t + depart)
    r = int(round(fps)) if fps else 25
    f = int(round(t * r))
    hh, rest = divmod(f, 3600 * r)
    mm, rest = divmod(rest, 60 * r)
    ss, ff = divmod(rest, r)
    return "%02d:%02d:%02d:%02d" % (hh, mm, ss, ff)


def med(a):
    a = [x for x in a if x is not None]
    return float(np.median(a)) if len(a) else None


def pct(a, p):
    a = [x for x in a if x is not None]
    return float(np.percentile(a, p)) if len(a) else None


def ffbin(nom):
    return nom


def probe(path):
    """Durée, flux vidéo (taille, cadence, format d'image) et présence de son."""
    cmd = [ffbin("ffprobe"), "-v", "error", "-print_format", "json", "-show_streams", "-show_format", path]
    r = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if r.returncode != 0:
        raise RuntimeError("ffprobe ne lit pas %s : %s" % (path, r.stderr.decode("utf-8", "replace")[:300]))
    d = json.loads(r.stdout.decode("utf-8", "replace"))
    out = {"fichier": os.path.abspath(path), "duree": None, "video": None, "audio": None}
    try:
        out["duree"] = float(d.get("format", {}).get("duration"))
    except (TypeError, ValueError):
        pass
    for s in d.get("streams", []):
        if s.get("codec_type") == "video" and out["video"] is None and s.get("disposition", {}).get("attached_pic", 0) != 1:
            def ratio(x):
                try:
                    a, b = x.split("/")
                    return float(a) / float(b) if float(b) else None
                except Exception:
                    return None
            fps = ratio(s.get("avg_frame_rate") or "") or ratio(s.get("r_frame_rate") or "")
            w, h = int(s.get("width", 0)), int(s.get("height", 0))
            sar = ratio((s.get("sample_aspect_ratio") or "1:1").replace(":", "/")) or 1.0
            rot = 0
            for sd in s.get("side_data_list", []) or []:
                if "rotation" in sd:
                    try:
                        rot = int(sd["rotation"])
                    except (TypeError, ValueError):
                        pass
            if abs(rot) in (90, 270):
                w, h = h, w
            dar = (w * sar / h) if h else 16 / 9
            out["video"] = {"largeur": w, "hauteur": h, "fps": round(fps, 3) if fps else None,
                            "rapport": round(dar, 3), "codec": s.get("codec_name")}
            try:
                if out["duree"] is None:
                    out["duree"] = float(s.get("duration"))
            except (TypeError, ValueError):
                pass
        if s.get("codec_type") == "audio" and out["audio"] is None:
            out["audio"] = {"codec": s.get("codec_name"), "canaux": s.get("channels"),
                            "frequence": int(s.get("sample_rate", 0) or 0)}
    return out


def format_nom(rapport):
    for nom, r in (("16:9", 16 / 9), ("9:16", 9 / 16), ("1:1", 1.0), ("4:3", 4 / 3), ("4:5", 0.8),
                   ("2,39:1", 2.39), ("2:1", 2.0), ("1,85:1", 1.85), ("3:4", 0.75)):
        if abs(rapport - r) / r < 0.03:
            return nom
    return ("%.2f:1" % rapport).replace(".", ",")


# ---------------------------------------------------------------- lecture des images

def _ffmpeg_frames(path, t0, t1, w=WB, h=HB):
    cmd = [ffbin("ffmpeg"), "-v", "error", "-nostdin"]
    if t0 and t0 > 0:
        cmd += ["-ss", "%.3f" % t0]
    if t1 is not None:
        cmd += ["-to", "%.3f" % t1]
    cmd += ["-i", path, "-an", "-sn", "-vf",
            "fps=30000/1001,scale=%d:%d:flags=area,setsar=1" % (w, h),
            "-pix_fmt", "rgb24", "-f", "rawvideo", "-"]
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
    n = w * h * 3
    try:
        while True:
            b = p.stdout.read(n)
            if len(b) < n:
                break
            yield np.frombuffer(b, np.uint8).reshape(h, w, 3)
    finally:
        p.stdout.close()
        p.wait()


def _block(x, k):
    """Moyenne par blocs k x k sur les deux premiers axes."""
    hh, ww = x.shape[0] // k, x.shape[1] // k
    x = x[:hh * k, :ww * k]
    if x.ndim == 2:
        return x.reshape(hh, k, ww, k).mean(axis=(1, 3))
    return x.reshape(hh, k, ww, k, x.shape[2]).mean(axis=(1, 3))


_HANN = None


def _phase_shift(a, b):
    """Déplacement (dx, dy) de b par rapport à a, en pixels de l'image 144 x 81."""
    global _HANN
    if _HANN is None:
        _HANN = np.outer(np.hanning(HS), np.hanning(WS)).astype(np.float32)
    A = np.fft.rfft2((a - a.mean()) * _HANN)
    B = np.fft.rfft2((b - b.mean()) * _HANN)
    R = A * np.conj(B)
    R /= np.abs(R) + 1e-6
    r = np.fft.irfft2(R, s=(HS, WS))
    iy, ix = np.unravel_index(int(np.argmax(r)), r.shape)
    pk = float(r[iy, ix])

    def sub(m, c, p):
        d = m - 2 * c + p
        return 0.0 if abs(d) < 1e-9 else 0.5 * (m - p) / d
    ym, yp = r[(iy - 1) % HS, ix], r[(iy + 1) % HS, ix]
    xm, xp = r[iy, (ix - 1) % WS], r[iy, (ix + 1) % WS]
    dy = iy + sub(ym, pk, yp)
    dx = ix + sub(xm, pk, xp)
    if dy > HS / 2:
        dy -= HS
    if dx > WS / 2:
        dx -= WS
    # convention : déplacement du contenu de a vers b
    return -dx, -dy, pk


def _crop_content(G):
    """Bandes noires constantes (lignes ou colonnes noires dans 80 % des images) : exclues."""
    dark = G.max(axis=2) < 6
    rows = dark.mean(axis=0) >= 0.8
    r0 = 0
    while r0 < H // 3 and rows[r0]:
        r0 += 1
    r1 = H
    while r1 > H - H // 3 and rows[r1 - 1]:
        r1 -= 1
    darkc = G.max(axis=1) < 6
    cols = darkc.mean(axis=0) >= 0.8
    c0 = 0
    while c0 < W // 3 and cols[c0]:
        c0 += 1
    c1 = W
    while c1 > W - W // 3 and cols[c1 - 1]:
        c1 -= 1
    return r0, r1, c0, c1


def _mad(a, b):
    return float(np.abs(a - b).mean())


def _detect(G):
    """Coupes franches et transitions progressives d'un bloc d'images (repris du découpage du corpus).
    Renvoie (cuts, grads) en indices locaux ; grads : (s, e, genre)."""
    r0, r1, c0, c1 = _crop_content(G)
    G = G[:, r0:r1, c0:c1]
    n = len(G)
    m1 = np.zeros(n)
    for i in range(1, n):
        m1[i] = _mad(G[i - 1], G[i])
    lum = G.mean(axis=(1, 2))
    sd = G.std(axis=(1, 2))
    dist = m1 >= DUP
    Z = (G - G.mean(axis=(1, 2), keepdims=True)) / (G.std(axis=(1, 2), keepdims=True) + 4)

    def nm(a, b):
        return float(np.abs(Z[a] - Z[b]).mean())

    def prev_d(i):
        return float(m1[max(1, i - 3):i].max()) if i > 1 else 0.0

    def next_d(i):
        return float(m1[i + 1:min(n, i + 4)].max()) if i + 1 < n else 0.0

    def bg(i, w=12):
        lo, hi = max(1, i - w), min(n, i + w + 1)
        v = [m1[j] for j in range(lo, hi) if dist[j] and abs(j - i) > 1]
        return float(np.median(v)) if v else 0.0

    cuts = []
    i = 1
    while i < n:
        if m1[i] >= CUT_ABS * 0.5:
            if i + 1 < n:
                lo2, hi2 = sorted((m1[i], m1[i + 1]))
                if lo2 >= 0.35 * hi2 and hi2 >= CUT_ABS * 0.75:
                    span = _mad(G[i - 1], G[i + 1])
                    if span >= CUT_ABS and span >= 1.2 * hi2 and nm(i - 1, i + 1) >= CUT_NM \
                            and span >= CUT_PEAK * max(prev_d(i), next_d(i + 1)) and span >= CUT_BG * bg(i):
                        cuts.append(i)
                        i += 2
                        continue
            if m1[i] >= CUT_ABS and m1[i] >= CUT_PEAK * max(prev_d(i), next_d(i)) and m1[i] >= CUT_BG * bg(i) \
                    and nm(i - 1, i) >= CUT_NM:
                cuts.append(i)
                i += 1
                continue
            if m1[i] >= CUT_FLAT_ABS and max(prev_d(i), next_d(i)) <= CUT_FLAT_ISOLE * m1[i] and nm(i - 1, i) >= CUT_FLAT_NM:
                cuts.append(i)
                i += 1
                continue
        i += 1
    cutset = set(cuts)
    Gs = G.reshape(n, -1)
    cutarr = np.zeros(n + 1, int)
    for c in cutset:
        cutarr[c] = 1
    ccum = np.cumsum(cutarr)

    def has_cut(lo, hi):
        lo = max(lo, 0)
        hi = min(hi, n - 1)
        return hi > lo and ccum[hi] - ccum[lo] > 0
    cand = {}
    for k in (4, 8, 15, 25):
        if n <= 2 * k:
            continue
        dk = np.zeros(n)
        for i in range(k, n - k):
            dk[i] = _mad(G[i - k], G[i + k])
        for i in range(k, n - k):
            if dk[i] >= GRAD_MIN and dk[i] == dk[max(k, i - k):min(n - k, i + k + 1)].max() and not has_cut(i - k, i + k):
                cand[i] = max(cand.get(i, 0), dk[i])
    grads = []
    taken = np.zeros(n, bool)
    for c in sorted(cand, key=lambda x: -cand[x]):
        if taken[c]:
            continue
        best = None
        for k in (3, 5, 8, 12, 16, 22, 30):
            a, b = c - k, c + k
            if a < 0 or b >= n or has_cut(a, b) or taken[a:b + 1].any():
                continue
            if _mad(G[a], G[b]) < GRAD_MIN:
                continue
            A, B = Gs[a], Gs[b]
            AB = A - B
            nab = float(np.linalg.norm(AB))
            if nab < 1e-6:
                continue

            def fit(j):
                v = Gs[j] - B
                al = float(v @ AB) / (nab * nab)
                return al, float(np.linalg.norm(v - al * AB)) / nab
            inner = [fit(j) for j in range(a + 1, b)]
            al_in = np.array([x[0] for x in inner])
            r_in = np.array([x[1] for x in inner])
            mid = [j - (a + 1) for j in range(a + 1, b) if abs(j - c) <= max(1, k // 3)]
            rmid = float(np.median(r_in[mid]))
            amid = float(np.median(al_in[mid]))
            mono = float(np.corrcoef(np.arange(len(al_in)), al_in)[0, 1]) if len(al_in) > 2 and al_in.std() > 0 else -1.0
            w = max(2, k // 2)
            lo_out = [j for j in range(a - w, a) if j >= 0 and not has_cut(j, a)]
            hi_out = [j for j in range(b + 1, b + w + 1) if j < n and not has_cut(b, j)]
            if (a - w >= 0 and len(lo_out) < 2) or (b + w < n and len(hi_out) < 2):
                continue
            o1 = float(np.median([fit(j)[0] for j in lo_out])) if lo_out else 1.0
            o2 = float(np.median([fit(j)[0] for j in hi_out])) if hi_out else 0.0
            ok = rmid <= LIN_MAX and 0.25 <= amid <= 0.75 and mono <= -0.9 and 0.8 <= o1 <= 1.25 and -0.25 <= o2 <= 0.2
            if ok and (best is None or rmid < best[0]):
                best = (rmid, k, a, b, al_in)
        if best is None:
            continue
        rmid, k, a, b, al_in = best
        la, lb = lum[a], lum[b]
        ends_flat = (la <= BLACK and sd[a] < 6) or (lb <= BLACK and sd[b] < 6) or \
                    (la >= WHITE and sd[a] < 6) or (lb >= WHITE and sd[b] < 6)
        if not ends_flat and nm(a, b) < GRAD_NM:
            continue
        js = [a + 1 + q for q, al in enumerate(al_in) if 0.1 < al < 0.9]
        s_, e_ = (min(js), max(js)) if js else (c, c)
        if la <= BLACK and sd[a] < 6:
            kind = "fondu_noir_entree"
        elif lb <= BLACK and sd[b] < 6:
            kind = "fondu_noir_sortie"
        elif la >= WHITE and sd[a] < 6:
            kind = "fondu_blanc_entree"
        elif lb >= WHITE and sd[b] < 6:
            kind = "fondu_blanc_sortie"
        else:
            kind = "fondu_enchaine"
        grads.append((s_, e_, kind))
        taken[a:b + 1] = True
    grads.sort()
    return cuts, grads


def lire_series(path, t0=None, t1=None, critique=False, rushes=False, bloc=150.0, marge=4.0, journal=None):
    """Lit la vidéo par blocs et renvoie les séries image par image et les transitions détectées.

    critique=True : garde les profils de lignes (bandes noires) et les vignettes de dérive.
    rushes=True   : calcule aussi netteté et déplacement de caméra.
    Les temps sont relatifs à t0 (0 = première image lue)."""
    info = probe(path)
    if info["video"] is None:
        raise RuntimeError("pas de flux vidéo dans %s" % path)
    dur = info["duree"] or 0.0
    a = max(0.0, t0 or 0.0)
    b = dur if t1 is None else min(dur, t1) if dur else t1
    if b is None or b <= a:
        raise RuntimeError("bornes vides (%s → %s)" % (a, b))
    nglob = int(round((b - a) * FPS))
    S = {k: np.zeros(nglob, np.float32) for k in ("m1", "lum", "sd", "sat", "chr")}
    S["valide"] = np.zeros(nglob, bool)
    if critique:
        S["rm"] = np.zeros((nglob, HB), np.float16)
        S["rs"] = np.zeros((nglob, HB), np.float16)
        S["vig"] = np.zeros((nglob, HT, WT), np.float16)
    if rushes:
        for k in ("net", "dx", "dy", "pk"):
            S[k] = np.zeros(nglob, np.float32)
    cuts_g, grads_g = [], []
    cs = a
    while cs < b - 1e-6:
        ce = min(b, cs + bloc)
        w0, w1 = max(a, cs - marge), min(b, ce + marge)
        off = int(round((w0 - a) * FPS))
        Gl, prev_s = [], None
        rows = []
        for fr in _ffmpeg_frames(path, w0, w1):
            x = fr.astype(np.float32)
            g288 = x @ np.array([0.299, 0.587, 0.114], np.float32)
            g = _block(g288, 3)
            Gl.append(g)
            rgb = _block(x, 3)
            mx, mn = rgb.max(axis=2), rgb.min(axis=2)
            msk = mx > 25
            sat = float(((mx - mn)[msk] / mx[msk]).mean()) if msk.any() else float("nan")
            chrm = float((mx - mn).mean())
            rec = {"lum": float(g.mean()), "sd": float(g.std()), "sat": sat, "chr": chrm}
            if critique:
                rec["rm"] = g288.mean(axis=1)
                rec["rs"] = g288.std(axis=1)
                rec["vig"] = _block(g288, 6)
            if rushes:
                lap = 4 * g288[1:-1, 1:-1] - g288[:-2, 1:-1] - g288[2:, 1:-1] - g288[1:-1, :-2] - g288[1:-1, 2:]
                # netteté rapportée au contraste : une image sombre (fondu) n'est pas floue
                rec["net"] = float(lap.var()) / max(float(g288.var()), 25.0)
                s = _block(g288, 2)[:HS, :WS]
                if prev_s is not None and float(np.abs(s - prev_s).mean()) >= DUP:
                    dx, dy, pk = _phase_shift(prev_s, s)
                else:
                    dx, dy, pk = 0.0, 0.0, 1.0
                rec["dx"], rec["dy"], rec["pk"] = dx, dy, pk
                prev_s = s
            rows.append(rec)
        if not Gl:
            cs = ce
            continue
        G = np.stack(Gl).astype(np.float32)
        del Gl
        cuts, grads = _detect(G)
        n = len(G)
        r0, r1, c0, c1 = _crop_content(G)
        Gc = G[:, r0:r1, c0:c1]
        m1 = np.zeros(n, np.float32)
        for i in range(1, n):
            m1[i] = _mad(Gc[i - 1], Gc[i])
        lum_c = Gc.mean(axis=(1, 2))
        sd_c = Gc.std(axis=(1, 2))
        for i, rec in enumerate(rows):
            rec["lum"], rec["sd"] = float(lum_c[i]), float(sd_c[i])
        core0 = int(round((cs - a) * FPS))
        core1 = int(round((ce - a) * FPS)) if ce < b - 1e-6 else nglob
        for i, rec in enumerate(rows):
            gi = off + i
            if core0 <= gi < core1 and gi < nglob:
                S["m1"][gi] = m1[i]
                for k in ("lum", "sd", "sat", "chr"):
                    S[k][gi] = rec[k]
                S["valide"][gi] = True
                if critique:
                    S["rm"][gi] = rec["rm"]
                    S["rs"][gi] = rec["rs"]
                    S["vig"][gi] = rec["vig"]
                if rushes:
                    for k in ("net", "dx", "dy", "pk"):
                        S[k][gi] = rec[k]
        for c in cuts:
            if core0 <= off + c < core1:
                cuts_g.append(off + c)
        for (s_, e_, kind) in grads:
            mid = off + (s_ + e_) // 2
            if core0 <= mid < core1:
                grads_g.append((off + s_, off + e_, kind))
        if journal:
            journal("  lu %s → %s s" % (fmt_n(cs, 1), fmt_n(ce, 1)))
        cs = ce
    # dernière image valide : la vidéo peut être plus courte que la durée annoncée
    v = np.where(S["valide"])[0]
    n = int(v[-1]) + 1 if len(v) else 0
    for k in list(S):
        S[k] = S[k][:n]
    # trous éventuels aux jointures de blocs : recopie de la voisine
    for i in range(1, n):
        if not S["valide"][i]:
            for k in S:
                if k != "valide":
                    S[k][i] = S[k][i - 1]
    S["n"] = n
    S["t0"] = a
    S["info"] = info
    S["cuts"] = sorted(set(c for c in cuts_g if 0 < c < n))
    S["grads"] = sorted(g for g in grads_g if 0 < g[0] < n)
    return S


# ---------------------------------------------------------------- découpage en plans

def segmenter(S, decisions=None, ajouts=None, garder_candidats=True):
    """Plans à partir des séries. decisions : {temps relatif (s): 'T'|'F'|'C'|'U'|'B'} pour les fondus
    candidats (vus à l'œil) ; ajouts : [(t, type)] transitions ajoutées à l'œil.
    Un fondu enchaîné non vérifié reste un plan à part, marqué verif='candidat'."""
    n = S["n"]
    lum, sd, m1 = S["lum"], S["sd"], S["m1"]
    black = (lum <= BLACK) & (sd < 6)
    white = (lum >= WHITE) & (sd < 6)
    bounds = {0: "debut"}
    verif, tlen = {}, {}
    for i in S["cuts"]:
        bounds[i] = "coupe"
        verif[i] = "auto"
    dec_keys = []
    if decisions:
        for k, v in decisions.items():
            try:
                dec_keys.append((float(k), v))
            except ValueError:
                pass

    def decision(s, e):
        """Décision dont le temps tombe dans le passage (± 0,35 s) ; la plus proche du milieu."""
        a, b, m = s / FPS - 0.35, e / FPS + 0.35, (s + e) / 2 / FPS
        best = None
        for tk, v in dec_keys:
            if a <= tk <= b and (best is None or abs(tk - m) < best[0]):
                best = (abs(tk - m), v)
        return best[1] if best else None
    for (s, e, kind) in S["grads"]:
        code = decision(s, e)
        if code == "F":
            continue
        if code == "C":
            q = int(np.argmax(m1[max(1, s - 1):min(n, e + 2)])) + max(1, s - 1)
            for j in list(bounds):
                if s <= j <= e + 1 and j != 0:
                    del bounds[j]
            bounds[q] = "coupe"
            verif[q] = "oeil"
            continue
        if code == "B" and kind == "fondu_enchaine":
            kind = "fondu_blanc_sortie"
        if kind == "fondu_enchaine" and code is None and not garder_candidats:
            continue
        for j in list(bounds):
            if s <= j <= e + 1 and j != 0:
                del bounds[j]
        L = e - s + 1
        if kind in ("fondu_noir_sortie", "fondu_blanc_sortie"):
            q = e + 1
        elif kind in ("fondu_noir_entree", "fondu_blanc_entree"):
            q = s
        else:
            q = (s + e + 1) // 2
        if q < n:
            bounds[q] = kind
            tlen[q] = L
            if code in ("T", "B"):
                verif[q] = "oeil"
            elif code == "U":
                verif[q] = "douteux" if kind != "fondu_enchaine" else "candidat"
            else:
                verif[q] = "candidat" if kind == "fondu_enchaine" else "auto"
    for (t, typ) in (ajouts or []):
        q = int(round(t * FPS))
        if not (0 < q < n):
            continue
        for j in list(bounds):
            if abs(j - q) <= MIN_PLAN and j != 0:
                del bounds[j]
        bounds[q] = typ
        verif[q] = "oeil"

    def ramp_up(j1):
        t = j1
        while t + 2 < n and t - j1 < 75 and lum[t + 2] > lum[t] + max(0.5, 0.02 * lum[t]):
            t += 1
        t = min(n - 1, t + 1)
        return t if (t - j1 >= 4 and lum[t] >= max(12.0, 2 * lum[j1] + 4)) else None

    def ramp_down(i0):
        t = i0 - 1
        while t - 2 >= 0 and (i0 - 1) - t < 75 and lum[t - 2] > lum[t] + max(0.5, 0.02 * lum[t]):
            t -= 1
        t = max(0, t - 1)
        return t if ((i0 - 1) - t >= 4 and lum[t] >= max(12.0, 2 * lum[i0 - 1] + 4)) else None
    for flat, (nin, nout) in ((black, ("fondu_noir_sortie", "fondu_noir_entree")),
                              (white, ("fondu_blanc_sortie", "fondu_blanc_entree"))):
        i = 0
        while i < n:
            if flat[i]:
                j = i
                while j + 1 < n and flat[j + 1]:
                    j += 1
                if j - i + 1 >= MIN_PLAN:
                    if i > 0:
                        rd = ramp_down(i) if flat is black else None
                        if rd is not None:
                            for q in list(bounds):
                                if rd < q < i and q != 0:
                                    del bounds[q]
                            bounds[i] = nin
                            tlen[i] = i - rd
                            verif[i] = "auto"
                        elif i not in bounds:
                            bounds[i] = "coupe"
                            verif[i] = "auto"
                    if j + 1 < n:
                        ru = ramp_up(j + 1) if flat is black else None
                        if ru is not None:
                            for q in list(bounds):
                                if j + 1 < q <= ru:
                                    del bounds[q]
                            bounds[j + 1] = nout
                            tlen[j + 1] = ru - (j + 1)
                            verif[j + 1] = "auto"
                        elif (j + 1) not in bounds:
                            bounds[j + 1] = "coupe"
                            verif[j + 1] = "auto"
                i = j + 1
            else:
                i += 1
    starts = []
    for q in sorted(bounds):
        if starts and q - starts[-1] < MIN_PLAN and starts[-1] != 0:
            prev = starts[-1]
            if bounds[prev] == "coupe" and bounds[q] != "coupe":
                bounds[prev] = bounds[q]
                if q in tlen:
                    tlen[prev] = tlen[q]
                if q in verif:
                    verif[prev] = verif[q]
            del bounds[q]
            continue
        starts.append(q)
    plans = []
    for k, s in enumerate(starts):
        e = starts[k + 1] if k + 1 < len(starts) else n
        plans.append({"s": s, "e": e, "tin": bounds[s]})
    merged = []
    for p in plans:
        if merged and p["e"] - p["s"] < MIN_PLAN and not black[p["s"]:p["e"]].all():
            merged[-1]["e"] = p["e"]
        else:
            merged.append(p)
    # premier plan trop court (une image à la borne) : rattaché au suivant
    if len(merged) > 1 and merged[0]["e"] - merged[0]["s"] < MIN_PLAN and not black[merged[0]["s"]:merged[0]["e"]].all():
        merged[1]["s"] = merged[0]["s"]
        merged[1]["tin"] = "debut"
        merged = merged[1:]
    noms = {"fondu_noir_entree": "fondu_depuis_noir", "fondu_blanc_entree": "fondu_depuis_blanc",
            "fondu_noir_sortie": "fondu_au_noir", "fondu_blanc_sortie": "fondu_au_blanc"}
    out = []
    for p in merged:
        s, e = p["s"], p["e"]
        tin = noms.get(p["tin"], p["tin"])
        out.append(dict(s=s, e=e, tin=tin, tl=tlen.get(s),
                        vf=verif.get(s, "auto") if tin != "debut" else None,
                        noir=bool(black[s:e].mean() > 0.8), blanc=bool(white[s:e].mean() > 0.8)))
    for k in range(len(out)):
        out[k]["tout"] = out[k + 1]["tin"] if k + 1 < len(out) else "fin"
    return [_mesures_plan(S, p) for p in out]


def _mesures_plan(S, p):
    s, e = p["s"], p["e"]
    lo, hi = s + (2 if e - s > 6 else 0), e - (2 if e - s > 6 else 0)
    if hi <= lo:
        lo, hi = s, e
    mv = S["m1"][max(lo, s + 1):hi]
    dur_int = max(1, hi - max(lo, s + 1)) / FPS
    mouvement = round(float(mv.sum()) / dur_int, 1) if len(mv) else 0.0
    satv = S["sat"][lo:hi]
    satv = satv[~np.isnan(satv)]
    sat = round(float(satv.mean()), 3) if len(satv) else None
    chrv = float(S["chr"][lo:hi].mean()) if hi > lo else 0.0
    lumv = float(S["lum"][lo:hi].mean()) / 255 if hi > lo else float(S["lum"][s]) / 255
    lb = None
    if "rm" in S:
        rm = S["rm"][lo:hi].astype(np.float32)
        rs = S["rs"][lo:hi].astype(np.float32)
        if len(rm):
            blk = float(np.percentile(S["rm"].astype(np.float32), 0.5))
            isbar = ((rm <= blk + 4) & (rs < 2.0)).mean(axis=0) >= 0.9
            top = 0
            while top < HB and isbar[top]:
                top += 1
            bot = 0
            while bot < HB and isbar[HB - 1 - bot]:
                bot += 1
            if 3 <= top < HB // 3 and 3 <= bot < HB // 3 and abs(top - bot) <= 3:
                rap = S["info"]["video"]["rapport"] if S["info"].get("video") else 16 / 9
                lb = {"haut": int(top), "bas": int(bot), "ratio": round(rap * HB / (HB - top - bot), 2)}
                rows = slice(top, HB - bot)
                lumv = float(rm[:, rows].mean()) / 255
    derive = False
    if "vig" in S and (e - s) / FPS >= 2.0:
        a, b = s + (e - s) // 7, e - 1 - (e - s) // 7
        va, vb = S["vig"][a].astype(np.float32), S["vig"][b].astype(np.float32)
        za = (va - va.mean()) / (va.std() + 4)
        zb = (vb - vb.mean()) / (vb.std() + 4)
        derive = bool(float(np.abs(za - zb).mean()) >= 0.75)
    t0, t1 = s / FPS, e / FPS
    d = dict(debut=round(t0, 3), fin=round(t1, 3), duree=round(t1 - t0, 3), images=int(e - s),
             transition_entree=p["tin"], transition_sortie=p["tout"],
             duree_transition_entree=round(p["tl"] / FPS, 2) if (p.get("tl") and str(p["tin"]).startswith("fondu")) else None,
             verif_transition=p["vf"], noir=p["noir"], blanc=p["blanc"],
             lum=round(lumv, 3), sat=sat, nb=bool(sat is not None and sat < 0.06 and chrv < 4),
             letterbox=lb, mouvement=mouvement, fixe=bool(mouvement < FIXE), derive=derive,
             _s=int(s), _e=int(e))
    return d


# ---------------------------------------------------------------- images ponctuelles, cartons, planches

def extraire_image(path, t, w=480, h=270, gris=False):
    """Une image à t secondes (dans le fichier), réduite à w x h."""
    cmd = [ffbin("ffmpeg"), "-v", "error", "-nostdin", "-ss", "%.3f" % max(0.0, t), "-i", path,
           "-frames:v", "1", "-an", "-vf", "scale=%d:%d:flags=area,setsar=1" % (w, h),
           "-pix_fmt", "gray" if gris else "rgb24", "-f", "rawvideo", "-"]
    r = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
    ch = 1 if gris else 3
    if len(r.stdout) < w * h * ch:
        return None
    a = np.frombuffer(r.stdout[:w * h * ch], np.uint8)
    return a.reshape(h, w) if gris else a.reshape(h, w, 3)


def extraire_images(path, temps, w=480, h=270, gris=False, fils=6):
    with ThreadPoolExecutor(max_workers=fils) as ex:
        return list(ex.map(lambda t: extraire_image(path, t, w, h, gris), temps))


def score_carton(img):
    """Indice qu'une image est un carton : fond presque uni, peu d'encre, encre en traits fins.
    img : gris 270 x 480 (uint8). Renvoie (bool, détails). Heuristique : à confirmer à l'œil."""
    if img is None:
        return False, {}
    g = img.astype(np.float32)
    if g.ndim == 3:
        g = g @ np.array([0.299, 0.587, 0.114], np.float32)
    fond = float(np.median(g))
    uni = float((np.abs(g - fond) <= 14).mean())
    encre = np.abs(g - fond) > 60
    part = float(encre.mean())
    det = {"fond": round(fond / 255, 3), "uni": round(uni, 3), "encre": round(part, 4)}
    if uni < 0.82 or part < 0.0015 or part > 0.16:
        return False, det
    er = encre.copy()
    for _ in range(2):
        e2 = er.copy()
        e2[1:, :] &= er[:-1, :]
        e2[:-1, :] &= er[1:, :]
        e2[:, 1:] &= er[:, :-1]
        e2[:, :-1] &= er[:, 1:]
        er = e2
    interieur = float(er.sum()) / max(1.0, float(encre.sum()))
    ys, xs = np.where(encre)
    hbox = (ys.max() - ys.min() + 1) / g.shape[0]
    det.update({"interieur": round(interieur, 3), "hauteur_encre": round(float(hbox), 3)})
    ok = interieur < 0.4 and hbox < 0.6
    return bool(ok), det


def planche(images, legendes, chemin, colonnes=6, w=240, h=135):
    """Planche contact : une vignette par image, légende dessous."""
    from PIL import Image, ImageDraw, ImageFont
    try:
        police = ImageFont.load_default(size=12)      # police vectorielle livrée avec Pillow (accents)
    except TypeError:
        police = ImageFont.load_default()
    n = len(images)
    if n == 0:
        return None
    lignes = int(math.ceil(n / float(colonnes)))
    lh = 30
    im = Image.new("RGB", (colonnes * w, lignes * (h + lh)), (18, 18, 18))
    dr = ImageDraw.Draw(im)
    for k, (a, leg) in enumerate(zip(images, legendes)):
        x, y = (k % colonnes) * w, (k // colonnes) * (h + lh)
        if a is not None:
            t = Image.fromarray(a if a.ndim == 3 else np.stack([a] * 3, axis=2)).resize((w - 4, h - 4))
            im.paste(t, (x + 2, y + 2))
        for j, ligne in enumerate(str(leg).split("\n")[:2]):
            # les polices intégrées n'ont pas toujours les accents : légende sans accents
            ligne = unicodedata.normalize("NFKD", ligne).encode("ascii", "ignore").decode("ascii")
            dr.text((x + 4, y + h + 2 + 13 * j), ligne, fill=(230, 230, 230), font=police)
    os.makedirs(os.path.dirname(os.path.abspath(chemin)), exist_ok=True)
    im.save(chemin, quality=85)
    return chemin


# ---------------------------------------------------------------- son

SR = 16000


def lire_audio(path, t0=None, t1=None, sr=SR):
    cmd = [ffbin("ffmpeg"), "-v", "error", "-nostdin"]
    if t0 and t0 > 0:
        cmd += ["-ss", "%.3f" % t0]
    if t1 is not None:
        cmd += ["-to", "%.3f" % t1]
    cmd += ["-i", path, "-vn", "-ac", "1", "-ar", str(sr), "-f", "f32le", "-"]
    r = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
    x = np.frombuffer(r.stdout, np.float32)
    return x if len(x) else None


def niveau_db(x, sr=SR, pas=0.1):
    k = int(sr * pas)
    n = len(x) // k
    if n == 0:
        return np.zeros(0)
    r = np.sqrt((x[:n * k].reshape(n, k) ** 2).mean(axis=1))
    return 20 * np.log10(r + 1e-9)


def enveloppe_attaques(x, sr=SR, nfft=1024, hop=256):
    """Flux spectral (log) : une valeur toutes les hop/sr secondes."""
    n = 1 + (len(x) - nfft) // hop if len(x) >= nfft else 0
    if n <= 2:
        return np.zeros(0), sr / hop
    win = np.hanning(nfft).astype(np.float32)
    idx = np.arange(nfft)[None, :] + hop * np.arange(n)[:, None]
    fr = x[idx] * win
    mag = np.log1p(100 * np.abs(np.fft.rfft(fr, axis=1)))
    fl = np.maximum(0, np.diff(mag, axis=0)).sum(axis=1)
    fl = np.concatenate([[0.0], fl])
    return fl, sr / hop


def attaques(env, rate, k=1.5, ecart=0.1):
    """Pics du flux spectral au-dessus de la médiane locale + k écarts absolus médians."""
    if len(env) == 0:
        return []
    w = int(rate * 1.5)
    out = []
    last = -1e9
    half = max(1, int(rate * 0.05))
    for i in range(1, len(env) - 1):
        lo, hi = max(0, i - w), min(len(env), i + w)
        loc = env[lo:hi]
        m = float(np.median(loc))
        mad = float(np.median(np.abs(loc - m))) + 1e-6
        if env[i] >= m + k * mad * 3 and env[i] == env[max(0, i - half):i + half + 1].max():
            t = i / rate
            if t - last >= ecart:
                out.append((round(t, 3), float(env[i])))
                last = t
    return out


def affiner_attaques(x, att, sr=SR, nfft=1024):
    """Recale chaque attaque sur la montée d'énergie du signal (fenêtres de 2 ms) : le flux spectral
    date une trame par le début de sa fenêtre, donc trop tôt."""
    if x is None or not att:
        return att
    k = max(1, int(sr * 0.002))
    out = []
    for t, v in att:
        a = int(t * sr)
        b = min(len(x), a + nfft + int(0.02 * sr))
        seg = x[a:b]
        n = len(seg) // k
        if n < 3:
            out.append((t, v))
            continue
        e = np.sqrt((seg[:n * k].reshape(n, k) ** 2).mean(axis=1))
        j = int(np.argmax(np.diff(e)))
        out.append((round((a + (j + 1) * k) / sr, 3), v))
    return out


def tempo(env, rate, bpm_min=60, bpm_max=180, onsets=None):
    """Tempo par autocorrélation du flux ; renvoie (bpm, confiance 0-1, phase en s) ou (None, 0, None)."""
    if len(env) < rate * 6:
        return None, 0.0, None
    e = env - env.mean()
    ac = np.correlate(e, e, mode="full")[len(e) - 1:]
    ac /= ac[0] + 1e-9
    lo, hi = int(rate * 60 / bpm_max), int(rate * 60 / bpm_min)
    if hi >= len(ac):
        return None, 0.0, None
    lag = lo + int(np.argmax(ac[lo:hi]))
    conf = float(max(0.0, ac[lag]))
    # période affinée : peigne sur toute la durée, période à ± 3 % par pas de 1 ms, phase par pas de 5 ms
    n = len(env)
    best = (-1.0, lag / rate, 0.0)
    for per in np.arange(lag / rate * 0.97, lag / rate * 1.03, 0.001):
        nb = int(n / rate / per)
        if nb < 4:
            continue
        for ph in np.arange(0.0, per, 0.005):
            idx = np.round((ph + per * np.arange(nb)) * rate).astype(int)
            idx = idx[idx < n]
            v = float(env[idx].sum()) / len(idx)
            if v > best[0]:
                best = (v, per, ph)
    _, per, ph = best
    if onsets is not None and len(onsets) >= 4:
        # phase recalée sur les attaques affinées : celle qui en met le plus à ± 20 ms de la grille
        o = np.array(onsets)
        cands = np.arange(0.0, per, 0.002)
        sc = [int(np.sum(np.abs(((o - c) / per) - np.round((o - c) / per)) * per <= 0.02)) for c in cands]
        ph = float(cands[int(np.argmax(sc))])
    return round(60.0 / per, 1), round(conf, 3), round(ph, 3)


def analyse_son(x, sr=SR):
    """Niveau, calme du début, sommet, fin, attaques, tempo. Ne sépare pas voix et musique."""
    if x is None or len(x) < sr:
        return None
    db = niveau_db(x, sr, 0.1)
    D = len(x) / sr
    actif = db[db > -60]
    medv = float(np.median(actif)) if len(actif) else -90.0
    debut = float(np.mean(db[:30])) if len(db) >= 30 else float(np.mean(db))
    fin = float(np.mean(db[-30:])) if len(db) >= 30 else float(np.mean(db))
    # sommet : fenêtre de 10 s la plus forte (énergie moyenne)
    sommet = None
    if D >= 12:
        e = 10 ** (db / 10)
        k = 100
        c = np.convolve(e, np.ones(k) / k, mode="valid")
        i = int(np.argmax(c))
        sommet = {"debut": round(i * 0.1, 1), "position": round((i * 0.1 + 5) / D, 3),
                  "db": round(float(10 * np.log10(c[i] + 1e-12)), 1)}
    env, rate = enveloppe_attaques(x, sr)
    att = affiner_attaques(x, attaques(env, rate), sr)
    bpm, conf, ph = tempo(env, rate, onsets=[a for a, _ in att])
    silence = float((db < -50).mean())
    return {"duree": round(D, 2), "niveau_median_db": round(medv, 1),
            "debut_3s_db": round(debut, 1), "ecart_debut_db": round(medv - debut, 1),
            "fin_3s_db": round(fin, 1), "part_silence_numerique": round(silence, 3),
            "sommet_10s": sommet, "attaques": [a for a, _ in att],
            "attaques_fortes": [a for a, v in sorted(att, key=lambda z: -z[1])[:24]],
            "tempo_bpm": bpm, "tempo_confiance": conf, "tempo_phase": ph,
            "courbe_db_par_0_5s": [round(float(v), 1) for v in niveau_db(x, sr, 0.5)]}


def coupes_sur_son(coupes, att, duree, tol=0.07, bpm=None, phase=None):
    """Part des coupes à ± tol s d'une attaque, comparée au hasard (densité d'attaques)."""
    if not coupes or not att or duree <= 0:
        return None
    att = np.array(sorted(att))
    hits = sum(1 for c in coupes if np.min(np.abs(att - c)) <= tol)
    dens = min(1.0, len(att) * 2 * tol / duree)
    out = {"coupes": len(coupes), "sur_attaque": int(hits), "attendu_hasard": round(dens * len(coupes), 1)}
    if bpm:
        per = 60.0 / bpm
        ph = phase or 0.0
        sur = sum(1 for c in coupes if abs(((c - ph) / per) - round((c - ph) / per)) * per <= tol)
        out["sur_temps"] = int(sur)
        out["attendu_temps"] = round(min(1.0, 2 * tol / per) * len(coupes), 1)
    return out


# ---------------------------------------------------------------- sous-titres

def _ts(s):
    s = s.strip().replace(",", ".")
    p = s.split(":")
    if len(p) == 3:
        return int(p[0]) * 3600 + int(p[1]) * 60 + float(p[2])
    if len(p) == 2:
        return int(p[0]) * 60 + float(p[1])
    return float(s)


def lire_sous_titres(path, t0=0.0, t1=None):
    """Répliques (début, fin, texte, mots) d'un .srt ou .vtt, relatives à t0, parole seulement
    (musique, bruitages entre crochets ou parenthèses écartés)."""
    import html
    txt = open(path, encoding="utf-8", errors="replace").read().replace("\r", "")
    out = []
    for blk in re.split(r"\n\s*\n", txt):
        m = re.search(r"(\d*:?\d+:[\d.,]+)\s*-->\s*(\d*:?\d+:[\d.,]+)", blk)
        if not m:
            continue
        a, b = _ts(m.group(1)), _ts(m.group(2))
        t = " ".join(l.strip() for l in blk[m.end():].strip().split("\n") if l.strip())
        t = html.unescape(re.sub(r"<[^>]+>", "", t))
        t = re.sub(r"(align|line|position|size):\S+", "", t).strip()
        if "♪" in t:
            continue
        s = re.sub(r"\[[^\]]*\]|\([^)]*\)", "", t).strip(" -:>")
        s = re.sub(r"^(>>\s*)?[A-ZÀ-Ý][A-ZÀ-Ý .']+:\s*", "", s)
        mots = len(re.findall(r"[0-9A-Za-zÀ-ÿ']+", s))
        if mots == 0:
            continue
        if t1 is not None and (b <= t0 + 0.3 or a >= t1 - 0.3):
            continue
        if b <= t0 + 0.3:
            continue
        aa = max(a, t0) - t0
        bb = (min(b, t1) if t1 is not None else b) - t0
        out.append((round(aa, 3), round(bb, 3), s, mots))
    out.sort()
    return out


def union(iv):
    tot, cur = 0.0, None
    res = []
    for a, b in sorted(iv):
        if cur is None or a > cur[1]:
            if cur:
                res.append(tuple(cur))
            cur = [a, b]
        else:
            cur[1] = max(cur[1], b)
    if cur:
        res.append(tuple(cur))
    return res
