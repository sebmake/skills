#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
lire_timeline.py : lit une timeline exportée (XML FCP7 « xmeml », ou EDL CMX3600) et la ramène
à une suite de plans visibles. Python 3.9, bibliothèque standard seulement.

    python3 lire_timeline.py montage.xml            # résumé lisible
    python3 lire_timeline.py montage.edl --fps 25   # l'EDL ne dit pas sa cadence : --fps, sinon déduite
    python3 lire_timeline.py montage.xml --json     # structure complète (celle que lit critique_montage.py)

Structure renvoyée par lire(chemin) :
  {"source": "xml"|"edl", "nom", "fps", "depart" (s, timecode de la première image), "duree" (s),
   "plans": [{"debut", "fin", "duree", "type": "image"|"noir"|"uni"|"carton", "nom", "fichier",
              "source_in", "source_out", "piste", "transition_entree", "duree_transition_entree",
              "verif_transition": "declare", "textes": [...] }],
   "textes": [{"debut", "fin", "texte", "sur": "noir"|"image"}],
   "audio": [{"debut", "fin", "nom", "fichier", "piste"}], "avertissements": [...]}

Règles de lecture :
  - piste vidéo du dessus = image visible ; un trou sur toutes les pistes = noir ;
  - générateur « Slug » ou couleur noire = noir ; autre couleur unie = uni (fond de carton) ;
  - générateur de texte (Text, Outline Text, Typewriter, Lower 3rd…) ou titre = texte posé sur ce
    qu'il y a dessous ; un texte sur noir ou sur fond uni fait du plan un « carton » ;
  - transition : Dissolve / Fondu / Cross → fondu_enchaine ; Dip / noir / Black → passage par le noir ;
    alignement start-black / end-black → fondu depuis le noir / au noir ; Wipe, Push, Slide, Iris → volet.
"""
import json
import os
import re
import sys
import xml.etree.ElementTree as ET
from urllib.parse import unquote, urlparse

TEXTE_GEN = re.compile(r"text|texte|titre|title|typewriter|lower ?3rd|caption|crawl|scroll|credits|\.prtl|\.mogrt|graphic|fusion title|text\+", re.I)
NOIR_GEN = re.compile(r"slug|black|noir|blank", re.I)
UNI_GEN = re.compile(r"color|colour|couleur|matte|solid", re.I)


def _f(el, tag, default=None):
    x = el.find(tag)
    if x is None or x.text is None:
        return default
    try:
        return float(x.text)
    except ValueError:
        return default


def _t(el, tag, default=None):
    x = el.find(tag)
    return x.text if (x is not None and x.text is not None) else default


def _rate(el):
    r = el.find("rate") if el is not None else None
    if r is None:
        return None
    tb = _f(r, "timebase")
    if not tb:
        return None
    ntsc = (_t(r, "ntsc", "FALSE") or "FALSE").strip().upper() == "TRUE"
    return tb * 1000.0 / 1001.0 if ntsc else tb


def _genre_transition(nom):
    n = (nom or "").lower()
    if re.search(r"dip|black|noir|fade in fade out", n):
        return "noir"
    if re.search(r"dissolve|fondu|cross|additive|film|blur|morph", n):
        return "fondu_enchaine"
    if re.search(r"wipe|push|slide|iris|volet|zoom|page|split|band|clock|checker|radial", n):
        return "volet"
    return "autre"


def _chemin(url):
    if not url:
        return None
    if url.startswith("file:"):
        p = unquote(urlparse(url).path)
        if re.match(r"^/[A-Za-z]:/", p):
            p = p[1:]
        return p
    return url


def _texte_generateur(el):
    vals = []
    for p in el.iter("parameter"):
        pid = (_t(p, "parameterid", "") or "").lower()
        if pid in ("str", "text", "texte") or "text" in pid:
            v = _t(p, "value")
            if v and not re.match(r"^[\d.\-]+$", v.strip()):
                vals.append(v.strip())
    return " / ".join(vals) if vals else None


def lire_xml(chemin):
    tree = ET.parse(chemin)
    root = tree.getroot()
    seqs = list(root.iter("sequence"))
    if not seqs:
        raise ValueError("aucune <sequence> dans %s" % chemin)
    seq = max(seqs, key=lambda s: len(list(s.iter("clipitem"))))
    fps = _rate(seq) or 25.0
    depart = 0.0
    tcel = seq.find("timecode")
    if tcel is not None:
        fr = _f(tcel, "frame")
        tcfps = _rate(tcel) or fps
        if fr is not None:
            depart = fr / tcfps
        else:
            s = _t(tcel, "string")
            if s and re.match(r"^\d+[:;]\d+[:;]\d+[:;]\d+$", s.strip()):
                h, m, sec, f = [int(x) for x in re.split(r"[:;]", s.strip())]
                depart = h * 3600 + m * 60 + sec + f / round(tcfps)
    avert = []
    files = {}
    for fe in root.iter("file"):
        fid = fe.get("id")
        if fid and (fe.find("pathurl") is not None or fe.find("name") is not None):
            files[fid] = {"nom": _t(fe, "name"), "fichier": _chemin(_t(fe, "pathurl"))}
    items, trans, textes_items = [], [], []
    video = seq.find("media/video")
    pistes = video.findall("track") if video is not None else []
    for pi, tr in enumerate(pistes):
        if (_t(tr, "enabled", "TRUE") or "TRUE").upper() == "FALSE":
            continue
        enfants = list(tr)
        for k, it in enumerate(enfants):
            tag = it.tag
            if tag not in ("clipitem", "generatoritem", "transitionitem"):
                continue
            if (_t(it, "enabled", "TRUE") or "TRUE").upper() == "FALSE":
                continue
            st, en = _f(it, "start", -1), _f(it, "end", -1)
            if tag == "transitionitem":
                eff = it.find("effect")
                nom = (_t(eff, "name") or _t(eff, "effectid") or "") if eff is not None else ""
                trans.append({"piste": pi, "start": st, "end": en, "align": (_t(it, "alignment", "center") or "center").lower(),
                              "genre": _genre_transition(nom), "nom": nom})
                continue
            # bornes -1 : la transition voisine fixe le point de montage
            if st is None or st < 0:
                pr = enfants[k - 1] if k > 0 else None
                if pr is not None and pr.tag == "transitionitem":
                    a, b = _f(pr, "start", 0), _f(pr, "end", 0)
                    al = (_t(pr, "alignment", "center") or "center").lower()
                    st = a if al in ("start", "start-black") else b if al == "end" else (a + b) / 2.0
            if en is None or en < 0:
                nx = enfants[k + 1] if k + 1 < len(enfants) else None
                if nx is not None and nx.tag == "transitionitem":
                    a, b = _f(nx, "start", 0), _f(nx, "end", 0)
                    al = (_t(nx, "alignment", "center") or "center").lower()
                    en = b if al in ("end", "end-black") else a if al == "start" else (a + b) / 2.0
            if st is None or en is None or en <= st:
                continue
            nom = _t(it, "name", "") or ""
            eff = it.find("effect")
            effnom = (_t(eff, "name") or _t(eff, "effectid") or "") if eff is not None else ""
            fe = it.find("file")
            fich = None
            if fe is not None:
                fid = fe.get("id")
                info = files.get(fid, {})
                fich = _chemin(_t(fe, "pathurl")) or info.get("fichier")
                if not nom:
                    nom = _t(fe, "name") or info.get("nom") or ""
            if tag == "generatoritem":
                if TEXTE_GEN.search(effnom) or TEXTE_GEN.search(nom):
                    genre = "texte"
                elif NOIR_GEN.search(effnom) or NOIR_GEN.search(nom):
                    genre = "noir"
                elif UNI_GEN.search(effnom) or UNI_GEN.search(nom):
                    genre = "uni"
                    for p in it.iter("parameter"):
                        v = p.find("value")
                        if v is not None and v.find("red") is not None:
                            try:
                                rgb = [float(v.find(c).text) for c in ("red", "green", "blue")]
                                if max(rgb) <= 12:
                                    genre = "noir"
                            except (TypeError, ValueError, AttributeError):
                                pass
                else:
                    genre = "uni"
                    avert.append("générateur inconnu « %s » (%s) lu comme fond uni" % (effnom or nom, round(st / fps, 2)))
            else:
                genre = "texte" if (TEXTE_GEN.search(nom) and (fich is None or re.search(r"\.(prtl|mogrt|aegraphic)$", fich or "", re.I))) else "image"
            rec = {"piste": pi, "start": st, "end": en, "genre": genre, "nom": nom, "fichier": fich,
                   "in": _f(it, "in"), "out": _f(it, "out")}
            if genre == "texte":
                rec["texte"] = _texte_generateur(it) or nom
                textes_items.append(rec)
            else:
                items.append(rec)
    audio = []
    aud = seq.find("media/audio")
    if aud is not None:
        for pi, tr in enumerate(aud.findall("track")):
            for it in tr.findall("clipitem"):
                st, en = _f(it, "start", -1), _f(it, "end", -1)
                if st is None or en is None or st < 0 or en <= st:
                    continue
                fe = it.find("file")
                fich = None
                if fe is not None:
                    fich = _chemin(_t(fe, "pathurl")) or files.get(fe.get("id"), {}).get("fichier")
                audio.append({"debut": st / fps, "fin": en / fps, "nom": _t(it, "name", ""), "fichier": fich, "piste": pi + 1})
    dur_fr = _f(seq, "duration")
    fin_max = max([x["end"] for x in items + textes_items] + [0])
    total = max(fin_max, dur_fr or 0)
    return _aplatir(items, trans, textes_items, fps, total, depart, "xml", _t(seq, "name", os.path.basename(chemin)), audio, avert)


def _aplatir(items, trans, textes_items, fps, total, depart, source, nom, audio, avert):
    """Image visible = élément de la piste la plus haute ; noir = aucun élément."""
    points = sorted(set([0.0, total] + [x["start"] for x in items + textes_items] + [x["end"] for x in items + textes_items]))
    segs = []
    for a, b in zip(points[:-1], points[1:]):
        if b <= a:
            continue
        cov = [x for x in items if x["start"] <= a and x["end"] >= b]
        top = max(cov, key=lambda x: x["piste"]) if cov else None
        txt = tuple(id(x) for x in textes_items if x["start"] <= a and x["end"] >= b)
        segs.append((a, b, top, txt))
    plans = []
    for a, b, top, txt in segs:
        # un texte qui commence ou finit découpe le plan (un noir, puis un carton)
        key = (id(top) if top is not None else None, txt if (top is None or top["genre"] in ("noir", "uni")) else ())
        if plans and plans[-1]["_k"] == key:
            plans[-1]["_b"] = b
            continue
        genre = top["genre"] if top else "noir"
        plans.append({"_k": key, "_a": a, "_b": b, "_top": top, "type": genre})
    # fusion des noirs voisins (trou + slug), sans texte dessus
    fus = []
    for p in plans:
        if fus and p["type"] == "noir" and fus[-1]["type"] == "noir" and p["_k"][1] == fus[-1]["_k"][1]:
            fus[-1]["_b"] = p["_b"]
            continue
        fus.append(p)
    plans = fus
    out = []
    for i, p in enumerate(plans):
        a, b, top = p["_a"], p["_b"], p["_top"]
        tin, dtr = ("debut" if i == 0 else "coupe"), None
        if i > 0:
            prev = plans[i - 1]
            cands = [t for t in trans if t["start"] - 1 <= a <= t["end"] + 1]
            if top is not None:
                cands = [t for t in cands if t["piste"] == top["piste"]] or cands
            if cands:
                t = min(cands, key=lambda t: abs((t["start"] + t["end"]) / 2 - a))
                dtr = (t["end"] - t["start"]) / fps
                if t["genre"] == "noir" or t["align"] in ("start-black", "end-black") or prev["type"] == "noir" or p["type"] == "noir":
                    if p["type"] == "noir" or t["align"] == "end-black":
                        tin = "fondu_au_noir"
                    elif prev["type"] == "noir" or t["align"] == "start-black":
                        tin = "fondu_depuis_noir"
                    else:
                        tin = "passage_par_le_noir"
                elif t["genre"] == "volet":
                    tin = "volet"
                elif t["genre"] == "fondu_enchaine":
                    tin = "fondu_enchaine"
                else:
                    tin = "autre_transition"
        elif top is not None:
            cands = [t for t in trans if t["start"] <= a + 1 and t["end"] >= a and t["piste"] == top["piste"]]
            if cands:
                tin, dtr = "fondu_depuis_noir", (cands[0]["end"] - cands[0]["start"]) / fps
        rec = {"debut": round(a / fps, 4), "fin": round(b / fps, 4), "duree": round((b - a) / fps, 4),
               "type": p["type"], "nom": top["nom"] if top else "", "fichier": top["fichier"] if top else None,
               "source_in": round(top["in"] / fps, 4) if (top and top.get("in") is not None) else None,
               "source_out": round(top["out"] / fps, 4) if (top and top.get("out") is not None) else None,
               "piste": (top["piste"] + 1) if top else None,
               "transition_entree": tin, "duree_transition_entree": round(dtr, 3) if dtr else None,
               "verif_transition": "declare" if tin != "debut" else None, "textes": []}
        if top is not None and rec["source_in"] is not None and top.get("start") is not None and a > top["start"]:
            rec["source_in"] = round((top["in"] + (a - top["start"])) / fps, 4)
        out.append(rec)
    # fin de film : dernier plan noir si un fondu au noir finit le dernier plan
    for t in trans:
        if t["align"] == "end-black" and abs(t["end"] - total) <= 1 and out:
            out[-1]["sortie_fondu_au_noir"] = round((t["end"] - t["start"]) / fps, 3)
    textes = []
    for x in sorted(textes_items, key=lambda x: x["start"]):
        a, b = x["start"] / fps, x["end"] / fps
        dessous = [p for p in out if p["debut"] < b - 1e-6 and p["fin"] > a + 1e-6]
        sur = "image" if any(p["type"] == "image" for p in dessous) else "noir"
        textes.append({"debut": round(a, 4), "fin": round(b, 4), "texte": x.get("texte") or x.get("nom"), "sur": sur})
        for p in dessous:
            p["textes"].append(x.get("texte") or x.get("nom"))
            if p["type"] in ("noir", "uni"):
                p["type"] = "carton"
    return {"source": source, "nom": nom, "fps": round(fps, 4), "depart": round(depart, 4),
            "duree": round(total / fps, 4), "plans": out, "textes": textes, "audio": audio,
            "avertissements": avert}


TC_RE = re.compile(r"(\d{2})[:;](\d{2})[:;](\d{2})[:;.](\d{2})")


def _tc_frames(s, r):
    m = TC_RE.match(s)
    h, mi, se, f = [int(x) for x in m.groups()]
    return ((h * 60 + mi) * 60 + se) * r + f


def lire_edl(chemin, fps=None):
    txt = open(chemin, encoding="utf-8", errors="replace").read().replace("\r", "")
    lignes = txt.split("\n")
    titre = os.path.basename(chemin)
    ev = []
    maxff = 0
    cur = None
    for ln in lignes:
        if ln.startswith("TITLE:"):
            titre = ln[6:].strip() or titre
            continue
        m = re.match(r"^\s*(\d{1,6})\s+(\S+)\s+(\S+)\s+(C|D|W\d{3}|K\s*B?|KO)\s*(\d{1,4})?\s+"
                     r"(\d{2}[:;]\d{2}[:;]\d{2}[:;.]\d{2})\s+(\d{2}[:;]\d{2}[:;]\d{2}[:;.]\d{2})\s+"
                     r"(\d{2}[:;]\d{2}[:;]\d{2}[:;.]\d{2})\s+(\d{2}[:;]\d{2}[:;]\d{2}[:;.]\d{2})", ln)
        if m:
            num, reel, piste, typ, dur, si, so, ri, ro = m.groups()
            for tcs in (si, so, ri, ro):
                maxff = max(maxff, int(TC_RE.match(tcs).group(4)))
            cur = {"num": int(num), "reel": reel, "piste": piste.upper(), "typ": typ.replace(" ", ""),
                   "dur": int(dur) if dur else 0, "si": si, "so": so, "ri": ri, "ro": ro, "nom": None, "fichier": None}
            ev.append(cur)
            continue
        if cur is not None:
            m2 = re.match(r"^\*\s*(FROM|TO)?\s*CLIP NAME:\s*(.*)$", ln.strip(), re.I)
            if m2:
                if (m2.group(1) or "FROM").upper() == "TO" and cur["typ"] != "C":
                    cur["nom_vers"] = m2.group(2).strip()
                else:
                    cur["nom"] = m2.group(2).strip()
                continue
            m3 = re.match(r"^\*\s*SOURCE FILE:\s*(.*)$", ln.strip(), re.I)
            if m3:
                cur["fichier"] = m3.group(1).strip()
    avert = []
    if fps is None:
        r = maxff + 1
        fps = next((c for c in (24, 25, 30, 48, 50, 60) if c >= r), 30)
        avert.append("cadence déduite de l'EDL : %d i/s (préciser --fps si elle est fausse)" % fps)
    R = int(round(fps))
    vid = [e for e in ev if "V" in e["piste"] or e["piste"] in ("B", "AA/V")]
    if not vid:
        raise ValueError("aucun événement vidéo dans %s" % chemin)
    rec_min = min(_tc_frames(e["ri"], R) for e in vid)
    depart_fr = (rec_min // (3600 * R)) * 3600 * R
    items, trans = [], []
    by_num = {}
    for e in vid:
        by_num.setdefault(e["num"], []).append(e)
    for num in sorted(by_num):
        grp = by_num[num]
        for k, e in enumerate(grp):
            ri, ro = _tc_frames(e["ri"], R) - depart_fr, _tc_frames(e["ro"], R) - depart_fr
            si = _tc_frames(e["si"], R)
            bl = e["reel"].upper() in ("BL", "BLK", "BLACK")
            if e["typ"] == "C":
                if ro > ri:
                    items.append({"piste": 0, "start": ri, "end": ro, "genre": "noir" if bl else "image",
                                  "nom": e["nom"] or e["reel"], "fichier": e.get("fichier"), "in": si, "out": si + (ro - ri)})
            else:
                genre = "fondu_enchaine" if e["typ"] == "D" else "volet" if e["typ"].startswith("W") else "autre"
                prev = grp[k - 1] if k > 0 else None
                prev_bl = prev is not None and prev["reel"].upper() in ("BL", "BLK", "BLACK")
                al = "center"
                if prev_bl:
                    al = "start-black"
                elif bl:
                    al = "end-black"
                d = e["dur"] or 0
                trans.append({"piste": 0, "start": ri, "end": ri + d, "align": al, "genre": "noir" if (prev_bl or bl) else genre,
                              "nom": e["typ"]})
                # l'élément entrant commence au milieu de la transition (alignement centré)
                cut = ri + d / 2.0 if al == "center" else ri
                if al == "end-black":
                    cut = ri + d
                    if items:
                        items[-1]["end"] = max(items[-1]["end"], cut)
                    if ro > cut:
                        items.append({"piste": 0, "start": cut, "end": ro, "genre": "noir",
                                      "nom": "BL", "fichier": None, "in": None, "out": None})
                    continue
                if items and al == "center":
                    items[-1]["end"] = cut
                if ro > cut:
                    items.append({"piste": 0, "start": cut, "end": ro, "genre": "noir" if bl else "image",
                                  "nom": e.get("nom_vers") or e["nom"] or e["reel"], "fichier": e.get("fichier"),
                                  "in": si + (cut - ri), "out": si + (ro - ri)})
    total = max(x["end"] for x in items) if items else 0
    audio = []
    for e in ev:
        if e["piste"].startswith("A") and "V" not in e["piste"]:
            audio.append({"debut": (_tc_frames(e["ri"], R) - depart_fr) / fps, "fin": (_tc_frames(e["ro"], R) - depart_fr) / fps,
                          "nom": e["nom"] or e["reel"], "fichier": e.get("fichier"), "piste": e["piste"]})
    avert.append("une EDL ne porte pas les textes : les cartons sont à déclarer dans les annotations")
    return _aplatir(items, trans, [], fps, total, depart_fr / fps, "edl", titre, audio, avert)


def entree_dans_fichier(plan, lecture):
    """Entrée source d'un plan en secondes depuis la première image de son fichier, ou None.

    Le XML FCP7 la donne déjà ainsi. L'EDL donne le timecode source, qui part du timecode inscrit dans le fichier
    (10:00:00:00 sur bien des caméras) : on le retranche quand le fichier est là."""
    si = plan.get("source_in")
    if si is None:
        return None
    f = plan.get("fichier")
    if lecture.get("source") != "edl" or not f or not os.path.exists(f):
        return si
    from commun import tc_fichier
    return si - _tc_frames(tc_fichier(f), int(round(lecture["fps"]))) / float(lecture["fps"])


def lire(chemin, fps=None):
    ext = os.path.splitext(chemin.rstrip("/"))[1].lower()
    if ext in (".fcpxml", ".fcpxmld"):
        raise ValueError("FCPXML (Final Cut Pro X) n'est pas lu : exporter en XML FCP7 (xmeml) ou en EDL")
    if ext in (".xml", ".fcpxml7", ".xmeml"):
        head = open(chemin, encoding="utf-8", errors="replace").read(4000)
        if "<fcpxml" in head:
            raise ValueError("FCPXML (Final Cut Pro X) n'est pas lu : exporter en XML FCP7 (xmeml) ou en EDL")
        return lire_xml(chemin)
    if ext == ".edl":
        return lire_edl(chemin, fps)
    raise ValueError("format de timeline inconnu : %s (attendu .xml FCP7 ou .edl)" % ext)


def main(argv):
    import argparse
    ap = argparse.ArgumentParser(description="Lit une timeline XML FCP7 ou EDL CMX3600.")
    ap.add_argument("chemin")
    ap.add_argument("--fps", type=float, default=None)
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args(argv)
    try:
        t = lire(a.chemin, a.fps)
    except (ValueError, OSError, ET.ParseError, AttributeError, KeyError) as ex:
        sys.stderr.write("lecture impossible : %s\n" % ex)
        return 2
    if a.json:
        print(json.dumps(t, ensure_ascii=False, indent=1))
        return 0
    print("%s (%s) : %d plans, %.2f s, %.3f i/s" % (t["nom"], t["source"], len(t["plans"]), t["duree"], t["fps"]))
    for i, p in enumerate(t["plans"], 1):
        print("%3d  %7.2f  %6.2f s  %-7s %-20s %s %s" % (i, p["debut"], p["duree"], p["type"], p["transition_entree"],
                                                       (p["nom"] or "")[:30], ("« " + " / ".join(p["textes"]) + " »") if p["textes"] else ""))
    for w in t["avertissements"]:
        print("! " + w)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
