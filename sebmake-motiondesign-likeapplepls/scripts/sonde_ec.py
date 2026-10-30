#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""sonde_ec.py: reads a composition open in EffectCraft and says how it works, in numbers.

It does not look at pixels. It reads the layers themselves (in/out points, parent, anchor, position, scale,
rotation, opacity, markers), rebuilds their place on screen through the parent chain, then derives:

  map          each layer, its role (its name), its parent, its in/out points, what is animated and how many keys,
               its markers. This is the page to read to understand the scene, or to edit it by hand.
  boundaries   the moments where most of what we see changes identity (0.4 s window). Each one is
                 CARRIED   a layer crosses it and moves (>= 2 % of the diagonal) or changes scale (>= 10 %),
                 ANCHORED  the only layer that crosses it is large (>= 3 % of the frame) and does not move,
                 BARE      nothing crosses it: it is a slide change.
               score = (carried + anchored / 2) / boundaries. Exempt: the last 1.2 s (the end) and the moments
               given by --coupes (an intended cut).
  speed        the largest on-screen travel of a layer, in px per frame (scaled to 1,920 wide). Above
               80 px per frame without motion blur, the motion splits into copies.
  frame        the layers named by --cadre (substrings of their name) that leave the frame, and when.

Guides, not verdicts: these thresholds are conventions of the skill (references/scene-demontee.md § 6).
A film cut the keynote way has bare boundaries by design (cut first, P1). The carry-over
score only makes sense for a one-take.

Usage:
  python3 sonde_ec.py "<comp name>" [--pas 0.0667] [--coupes 12.4,20.1] [--cadre "Cursor,Halo 2"]
                      [--carte map.md] [--json probe.json]
Exit codes: 0 read; 1 composition not found or error; 3 no app listening.
Python 3.9, no dependencies; goes through ec.py (channel 9877).
"""
import json
import math
import os
import sys

ICI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ICI)
import ec  # noqa: E402

LECTURE = r'''
function sd_enc(v){if(v===null||v===undefined)return "null";var t=typeof v;if(t==="number")return isFinite(v)?String(Math.round(v*1000)/1000):"null";
 if(t==="boolean")return v?"true":"false";if(t==="string"){var s="",i,c;for(i=0;i<v.length;i++){c=v.charCodeAt(i);
  if(c===34||c===92)s+="\\"+v.charAt(i);else if(c<32||c>126){var h=c.toString(16);while(h.length<4)h="0"+h;s+="\\u"+h;}else s+=v.charAt(i);}return "\""+s+"\"";}
 if(v instanceof Array){var a=[],j;for(j=0;j<v.length;j++)a.push(sd_enc(v[j]));return "["+a.join(",")+"]";}
 var o=[],k;for(k in v)if(v.hasOwnProperty(k))o.push(sd_enc(k)+":"+sd_enc(v[k]));return "{"+o.join(",")+"}";}
var comp=null,i;for(i=1;i<=app.project.numItems;i++){var it=app.project.item(i);if(it instanceof CompItem&&it.name===%(nom)s){comp=it;break;}}
if(!comp){"absente";}else{
try{comp.openInViewer();}catch(e){}
var PAS=%(pas)s,D=comp.duration,L=[],n,tps=[],t;for(t=0;t<D;t+=PAS)tps.push(t);
var NOMS={"A":"ADBE Anchor Point","P":"ADBE Position","S":"ADBE Scale","R":"ADBE Rotate Z","O":"ADBE Opacity"};
for(n=1;n<=comp.numLayers;n++){var l=comp.layer(n),tr=l.property("ADBE Transform Group"),e={i:n,nom:l.name,parent:l.parent?l.parent.index:0,
  entree:l.inPoint,sortie:l.outPoint,actif:l.enabled,flou:false,genre:"",w:0,h:0,rect:null,props:{},reperes:[]};
 try{e.flou=!!l.motionBlur;}catch(x){}
 try{if(l.property("ADBE Text Properties"))e.genre="texte";}catch(x){}
 try{if(!e.genre&&l.property("ADBE Root Vectors Group"))e.genre="forme";}catch(x){}
 try{if(!e.genre&&l.source){e.genre=(l.source.mainSource&&l.source.mainSource.color)?"solide":"media";e.w=l.source.width;e.h=l.source.height;
   try{if(l.hasVideo===false||!(l.source.width>0))e.genre="son";}catch(x){}}}catch(x){}
 try{if(!e.genre&&l.nullLayer)e.genre="nul";}catch(x){}
 if(e.genre==="texte"||e.genre==="forme"){var rs=[];for(var q=0;q<tps.length;q+=Math.max(1,Math.round(1/PAS))){var r=l.sourceRectAtTime(tps[q],false);rs.push([tps[q],r.left,r.top,r.width,r.height]);}e.rect=rs;}
 for(var c in NOMS){if(!NOMS.hasOwnProperty(c))continue;var p=null;try{p=tr.property(NOMS[c]);}catch(x){}if(!p)continue;
   if(p.numKeys>0){var vs=[];for(var u=0;u<tps.length;u++)vs.push(p.valueAtTime(tps[u],false));e.props[c]={cles:p.numKeys,v:vs};}else e.props[c]={cles:0,v:p.value};}
 try{var m=l.property("ADBE Marker");for(var mk=1;mk<=m.numKeys;mk++)e.reperes.push([m.keyTime(mk),m.keyValue(mk).comment]);}catch(x){}
 L.push(e);}
var flouComp=false;try{flouComp=!!comp.motionBlur;}catch(x){}
sd_enc({w:comp.width,h:comp.height,duree:D,fps:comp.frameRate,pas:PAS,flou:flouComp,temps:tps,calques:L});}
'''


def valeur(e, cle, k, defaut):
    p = e["props"].get(cle)
    if not p:
        return defaut
    v = p["v"][k] if p["cles"] else p["v"]
    return v


def matrice(e, k):
    A = valeur(e, "A", k, [0, 0])
    P = valeur(e, "P", k, [0, 0])
    S = valeur(e, "S", k, [100, 100])
    R = valeur(e, "R", k, 0)
    sx, sy = S[0] / 100.0, S[1] / 100.0
    c, s = math.cos(math.radians(R)), math.sin(math.radians(R))
    # screen = P + R·S·(local − A)
    a, b, cc, d = c * sx, s * sx, -s * sy, c * sy
    return [a, b, cc, d, P[0] - (a * A[0] + cc * A[1]), P[1] - (b * A[0] + d * A[1])]


def compose(m1, m2):
    a, b, c, d, e, f = m1
    A, B, C, D, E, F = m2
    return [a * A + c * B, b * A + d * B, a * C + c * D, b * C + d * D, a * E + c * F + e, b * E + d * F + f]


def rect_local(e, t):
    if e["genre"] in ("media", "solide"):
        return [0, 0, e["w"], e["h"]]
    if e["rect"]:
        best = min(e["rect"], key=lambda r: abs(r[0] - t))
        return best[1:]
    return None


def boite(m, r):
    x, y, w, h = r
    pts = [(x, y), (x + w, y), (x, y + h), (x + w, y + h)]
    xs = [m[0] * px + m[2] * py + m[4] for px, py in pts]
    ys = [m[1] * px + m[3] * py + m[5] for px, py in pts]
    return [min(xs), min(ys), max(xs), max(ys)]


def lire(o, nom, pas):
    ok, r, res = ec.lancer_script(o, LECTURE % {"nom": json.dumps(nom), "pas": repr(pas)}, "sonde.jsx")
    v = res.get("result")
    if not ok or not isinstance(v, str) or v == "absente":
        raise RuntimeError("composition not found or unreadable: %s (%s)" % (nom, (res.get("error") or v or r.get("error"))))
    return json.loads(v)


def ecran(C):
    """For each moment: {index: [box, opacity, area]} of the visible layers."""
    par_i = {e["i"]: e for e in C["calques"]}
    W, H = C["w"], C["h"]
    vues = []
    for k, t in enumerate(C["temps"]):
        mats = {}

        def mat(i):
            if i not in mats:
                e = par_i[i]
                m = matrice(e, k)
                mats[i] = compose(mat(e["parent"]), m) if e["parent"] else m
            return mats[i]
        vu = {}
        for e in C["calques"]:
            if not e["actif"] or e["genre"] in ("son", "nul", "") or not (e["entree"] <= t < e["sortie"]):
                continue
            op = valeur(e, "O", k, 100)
            r = rect_local(e, t)
            if op <= 1 or not r or r[2] <= 0 or r[3] <= 0:
                continue
            b = boite(mat(e["i"]), r)
            x0, y0, x1, y1 = max(b[0], 0), max(b[1], 0), min(b[2], W), min(b[3], H)
            aire = max(0, x1 - x0) * max(0, y1 - y0)
            if aire <= 0:
                continue
            fond = e["genre"] == "solide" and aire >= 0.9 * W * H and not e["props"].get("P", {}).get("cles")
            vu[e["i"]] = {"b": b, "op": op, "aire": aire, "fond": fond}
        vues.append(vu)
    return vues


def frontieres(C, vues, coupes):
    W, H = C["w"], C["h"]
    diag = math.hypot(W, H)
    pas = C["pas"]
    f = max(1, int(round(0.4 / pas)))
    T = C["temps"]
    cand = []
    for k in range(len(T) - f):
        a, b = vues[k], vues[k + f]
        tot = sum(v["aire"] for v in a.values() if not v["fond"]) + sum(v["aire"] for v in b.values() if not v["fond"])
        if tot <= 0:
            continue
        change = sum(v["aire"] for i, v in a.items() if not v["fond"] and i not in b) + \
            sum(v["aire"] for i, v in b.items() if not v["fond"] and i not in a)
        if change / tot > 0.5:
            cand.append(k)
    groupes = []
    for k in cand:
        if groupes and k - groupes[-1][-1] <= f:
            groupes[-1].append(k)
        else:
            groupes.append([k])
    res = []
    for g in groupes:
        k0, k1 = g[0], min(g[-1] + f, len(T) - 1)
        t = (T[k0] + T[k1]) / 2
        exempt = t > C["duree"] - 1.2 or any(abs(t - c) < 0.4 for c in coupes)
        a, b = vues[k0], vues[k1]
        survivants = [i for i in a if i in b and not a[i]["fond"]]
        genre, qui = "nue", []
        for i in survivants:
            ba, bb = a[i]["b"], b[i]["b"]
            ca, cb = ((ba[0] + ba[2]) / 2, (ba[1] + ba[3]) / 2), ((bb[0] + bb[2]) / 2, (bb[1] + bb[3]) / 2)
            dep = math.hypot(cb[0] - ca[0], cb[1] - ca[1]) / diag
            ech = math.sqrt(max(b[i]["aire"], 1) / max(a[i]["aire"], 1))
            if dep >= 0.02 or abs(ech - 1) >= 0.10:
                genre = "portée"
                qui.append(i)
        if genre == "nue":
            grands = [i for i in survivants if a[i]["aire"] >= 0.03 * W * H]
            if grands:
                genre, qui = "ancrée", grands
        res.append({"t": round(t, 2), "genre": genre, "exemptee": exempt, "par": qui})
    retenues = [r for r in res if not r["exemptee"]]
    note = None
    if retenues:
        note = (sum(r["genre"] == "portée" for r in retenues) + 0.5 * sum(r["genre"] == "ancrée" for r in retenues)) / len(retenues)
    return res, note


def vitesses(C, vues):
    W = C["w"]
    pas, fps = C["pas"], C["fps"]
    pic = {}
    for k in range(1, len(vues)):
        for i, v in vues[k].items():
            u = vues[k - 1].get(i)
            if not u or v["fond"]:
                continue
            d = max(abs(v["b"][j] - u["b"][j]) for j in range(4))
            px_img = d / (pas * fps) * (1920.0 / W)
            if px_img > pic.get(i, (0, 0))[0]:
                pic[i] = (px_img, C["temps"][k])
    return pic


def cadre(C, vues, motifs):
    W, H = C["w"], C["h"]
    hors = {}
    for e in C["calques"]:
        if not any(m in e["nom"] for m in motifs):
            continue
        par_i = e["i"]
        for k, t in enumerate(C["temps"]):
            r = rect_local(e, t)
            if not (e["entree"] <= t < e["sortie"]) or valeur(e, "O", k, 100) <= 1 or not r or r[2] <= 0 or r[3] <= 0:
                continue   # absent, transparent or not drawn yet (an outline at 0 %): nothing to frame
            v = vues[k].get(par_i)
            if v is None:
                hors.setdefault(e["nom"], []).append(round(t, 2))
            else:
                b = v["b"]
                if b[0] < 0 or b[1] < 0 or b[2] > W or b[3] > H:
                    hors.setdefault(e["nom"] + " (clipped)", []).append(round(t, 2))
    return hors


def plages(ts, pas):
    out = []
    for t in ts:
        if out and t - out[-1][1] <= pas * 1.5:
            out[-1][1] = t
        else:
            out.append([t, t])
    return ", ".join("%.2f–%.2f s" % (a, b) if b > a else "%.2f s" % a for a, b in out)


# Display names for the internal values (the values themselves stay French: they are compared in code and written to --json).
GENRES = {"texte": "text", "forme": "shape", "solide": "solid", "media": "media", "son": "sound", "nul": "null"}
FRONTIERES = {"portée": "carried", "ancrée": "anchored", "nue": "bare"}


def carte_md(C, nom, fr, note, pic):
    par_i = {e["i"]: e for e in C["calques"]}
    L = ["# Map of \"%s\"" % nom, "",
         "%d × %d, %.2f s at %s fps; %d layers, top to bottom. Composition motion blur: %s." % (
             C["w"], C["h"], C["duree"], ("%.3f" % C["fps"]).rstrip("0").rstrip("."), len(C["calques"]), "yes" if C["flou"] else "no"), "",
         "| # | Layer | Kind | Parent | In → out | Animated (keys) | Markers |", "|---|---|---|---|---|---|---|"]
    for e in C["calques"]:
        anim = ", ".join("%s %d" % ({"A": "anchor", "P": "position", "S": "scale", "R": "rotation", "O": "opacity"}[c], p["cles"])
                         for c, p in e["props"].items() if p["cles"])
        rep = "; ".join("%.2f s %s" % (t, c) for t, c in e["reperes"][:6]) + (" …" if len(e["reperes"]) > 6 else "")
        L.append("| %d | %s | %s | %s | %.2f → %.2f s | %s | %s |" % (
            e["i"], e["nom"].replace("|", "/"), GENRES.get(e["genre"], e["genre"]) or "?", par_i[e["parent"]]["nom"].split(" · ")[0] if e["parent"] else "—",
            e["entree"], e["sortie"], anim or "—", rep or "—"))
    L += ["", "## Boundaries", ""]
    if not fr:
        L.append("None: the scene is a single shot, nothing changes identity at once.")
    for r in fr:
        qui = ", ".join(par_i[i]["nom"].split(" · ")[0] for i in r["par"][:3])
        L.append("- %.2f s: **%s**%s%s" % (r["t"], FRONTIERES.get(r["genre"], r["genre"]), (" by " + qui) if qui else "", " (exempt)" if r["exemptee"] else ""))
    if note is not None:
        L.append("")
        L.append("Carry-over score: **%.2f** (guide: under 0.5 = a series of slides; 0.7 and above = a shot that holds together)." % note)
    L += ["", "## Speed", ""]
    top = sorted(pic.items(), key=lambda kv: -kv[1][0])[:5]
    for i, (v, t) in top:
        flou = C["flou"] and par_i[i].get("flou")
        L.append("- %s: %.0f px per frame at %.2f s%s" % (par_i[i]["nom"].split(" · ")[0], v, t,
                                                          " — above 80 without motion blur: splits into copies" if v > 80 and not flou else ""))
    return "\n".join(L) + "\n"


def main(argv):
    if not argv or argv[0] in ("-h", "--help"):
        print(__doc__)
        return 0
    o, pos = ec.lire_options(argv)
    nom = pos[0]
    pas = float(o.reste.get("pas", 1 / 15))
    coupes = [float(x) for x in o.reste.get("coupes", "").split(",") if x.strip()]
    motifs = [x.strip() for x in o.reste.get("cadre", "").split(",") if x.strip()]
    try:
        C = lire(o, nom, pas)
    except ConnectionRefusedError:
        print("sonde_ec: no app listening on %d (open -a EffectCraft --args --control 9877)" % o.port, file=sys.stderr)
        return 3
    except RuntimeError as ex:
        print("sonde_ec: %s" % ex, file=sys.stderr)
        return 1
    vues = ecran(C)
    fr, note = frontieres(C, vues, coupes)
    pic = vitesses(C, vues)
    hors = cadre(C, vues, motifs) if motifs else {}
    md = carte_md(C, nom, fr, note, pic)
    if hors:
        md += "\n## Frame\n\n" + "\n".join("- %s out of frame: %s" % (k, plages(v, pas)) for k, v in hors.items()) + "\n"
    elif motifs:
        md += "\n## Frame\n\nThe watched layers (%s) stay in the frame.\n" % ", ".join(motifs)
    if o.reste.get("carte"):
        open(o.reste["carte"], "w", encoding="utf-8").write(md)
    if o.reste.get("json"):
        json.dump({"frontieres": fr, "note": note, "vitesses": {str(i): v for i, v in pic.items()}, "hors_cadre": hors},
                  open(o.reste["json"], "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(md)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
