#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""scene_ec.py: scene.json -> scene breakdown in layers (.jsx script, ES3), then runs it in EffectCraft.

A scene breakdown is a UI one-take made readable: each mechanism has its own layer, named by its role,
and can be edited by hand in the tool.

  Background      a solid in the theme color
  Window          the filmed interface alone (video or image), WITHOUT a camera
  Camera          there is no camera layer: the camera is the window's anchor point (what we look at, in window px)
                  and its scale (zoom × 100); its position stays at the center of the frame
  Children        halos and the cursor have the window as parent: they are placed in window px and follow the
                  camera with no math
  Screen          subtitles, title card and texts stay fixed, on top of everything
  Sound           each voice at its moment, the music offset to land in the right place, one-shot sounds

Usage:
  python3 scene_ec.py scene.json                       writes scene.jsx next to it, then runs it (ec.py script)
  python3 scene_ec.py scene.json --jsx-seul            writes the script without running it
  python3 scene_ec.py scene.json --prefixe TEST-       prefixes the composition name (trials)
  python3 scene_ec.py scene.json -o other.jsx

Format: references/scene-demontee.md. Paths are relative to the scene.json folder.
Exit codes: 0 success; 1 scene unreadable or inconsistent; 2 error at run time (message from the app).
Python 3.9, no dependencies. The output script uses only var and function (ES3): it also runs in After Effects.
"""
import json
import os
import subprocess
import sys

ICI = os.path.dirname(os.path.abspath(__file__))
FORMATS = {"16:9": (1920, 1080), "9:16": (1080, 1920), "1:1": (1080, 1080), "16:9-4k": (3840, 2160)}

# Arrival on a camera key -> interpolation and ease influence (in %), on both sides of the segment.
# Conventions of the skill, tuned by eye on two films; not measurements from the keynote corpus.
ARRIVEES = {
    "pose":     ("BEZIER", 66, 66),   # a camera move that settles: slow start and slow end
    "suit":     ("BEZIER", 33, 33),   # follow a moving subject: near linear, no jolt
    "fouette":  ("BEZIER", 88, 88),   # go fast from one point to another: all the travel in the middle
    "lineaire": ("LINEAR", 0, 0),     # tracking at constant speed
    "coupe":    ("HOLD", 0, 0),       # no travel: the image jumps to the key (a cut inside the shot)
}


def faute(msg):
    print("scene_ec: " + msg, file=sys.stderr)
    sys.exit(1)


def num(v):
    return ("%.4f" % v).rstrip("0").rstrip(".") if isinstance(v, float) else str(v)


def js(v):
    """JS literal safe in ES3 (non-ASCII characters escaped)."""
    return json.dumps(v, ensure_ascii=True)


def lire_srt(chemin):
    blocs, txt = [], open(chemin, encoding="utf-8-sig").read().replace("\r\n", "\n").strip().split("\n\n")
    def s(h):
        h, ms = h.strip().replace(".", ",").split(",")
        a, b, c = h.split(":")
        return int(a) * 3600 + int(b) * 60 + int(c) + int(ms) / 1000
    for b in txt:
        lignes = b.strip().split("\n")
        i = next((k for k, l in enumerate(lignes) if "-->" in l), None)
        if i is None:
            continue
        a, z = lignes[i].split("-->")
        blocs.append([s(a), s(z), " ".join(lignes[i + 1:]).strip()])
    return blocs


def deux_lignes(t, limite):
    if len(t) <= limite or "\r" in t:
        return t
    esp = [i for i, c in enumerate(t) if c == " "]
    if not esp:
        return t
    k = min(esp, key=lambda i: abs(i - len(t) / 2))
    return t[:k] + "\r" + t[k + 1:]


def charger(chemin):
    try:
        S = json.load(open(chemin, encoding="utf-8"))
    except (OSError, ValueError) as ex:
        faute("%s unreadable: %s" % (chemin, ex))
    base = os.path.dirname(os.path.abspath(chemin))
    absolu = lambda f: f if os.path.isabs(f) else os.path.normpath(os.path.join(base, f))
    c = S.get("comp") or faute("\"comp\" block expected")
    if c.get("format", "16:9") not in FORMATS:
        faute("unknown format: %s (16:9, 16:9-4k, 9:16, 1:1)" % c.get("format"))
    if not c.get("duree"):
        faute("comp.duree expected (s)")
    f = S.get("fenetre") or faute("\"fenetre\" block expected")
    for k in ("fichier", "largeur", "hauteur"):
        if not f.get(k):
            faute("fenetre.%s expected" % k)
    f["fichier"] = absolu(f["fichier"])
    if not os.path.exists(f["fichier"]):
        faute("window file not found: %s" % f["fichier"])
    try:
        r = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=width,height",
                            "-of", "csv=p=0", f["fichier"]], capture_output=True, text=True)
        fw, fh = [int(v) for v in r.stdout.strip().split(",")[:2]]
    except (OSError, ValueError):
        fw, fh = f["largeur"], f["hauteur"]
    W_, H_ = FORMATS[c.get("format", "16:9")]
    if fw > W_ or fh > H_:
        faute("the window (%d × %d) is larger than the composition (%d × %d): EffectCraft then misplaces its children. "
              "Make it smaller, or use the 16:9-4k format to zoom sharply into a ×2 window." % (fw, fh, W_, H_))
    if (fw, fh) != (f["largeur"], f["hauteur"]):
        faute("fenetre.largeur × hauteur (%s × %s) ≠ the file (%d × %d): coordinates are in file px"
              % (f["largeur"], f["hauteur"], fw, fh))
    cam = S.get("camera") or {}
    cles = cam.get("cles") or [{"t": 0, "x": f["largeur"] / 2, "y": f["hauteur"] / 2, "zoom": 1}]
    for i, k in enumerate(cles):
        if i:   # a key without x, y or zoom keeps those of the previous key: a rest is written {"t": …, "arrivee": "coupe"}
            for c_ in ("x", "y", "zoom"):
                k.setdefault(c_, cles[i - 1].get(c_, 1 if c_ == "zoom" else 0))
        if k.get("arrivee", "pose") not in ARRIVEES:
            faute("camera, key %d: unknown arrival \"%s\" (%s)" % (i + 1, k.get("arrivee"), ", ".join(ARRIVEES)))
        if i and k["t"] <= cles[i - 1]["t"]:
            faute("camera: keys must be in time order (key %d at %.3f s)" % (i + 1, k["t"]))
    cam["cles"] = cles
    S["camera"] = cam
    E = S.setdefault("ecran", {})
    st = E.get("sous_titres")
    if isinstance(st, str):
        E["sous_titres"] = lire_srt(absolu(st))
    son = S.setdefault("son", {})
    for v in son.get("voix", []) + son.get("sons", []):
        v["fichier"] = absolu(v["fichier"])
    if son.get("musique"):
        son["musique"]["fichier"] = absolu(son["musique"]["fichier"])
    for v in son.get("voix", []) + son.get("sons", []) + ([son["musique"]] if son.get("musique") else []):
        if not os.path.exists(v["fichier"]):
            faute("sound file not found: %s" % v["fichier"])
    return S


ENTETE = r'''// Scene breakdown, written by scene_ec.py from %(source)s. Fix the scene.json, not this script: it gets rewritten.
// ES3 (var, function): runs in EffectCraft and in After Effects.
function sd_rgb(h){h=h.replace("#","");return[parseInt(h.substr(0,2),16)/255,parseInt(h.substr(2,2),16)/255,parseInt(h.substr(4,2),16)/255];}
function sd_tr(l){return l.property("ADBE Transform Group");}
function sd_contenu(g){return g.property("ADBE Vectors Group");}
function sd_ease(p,k,cote,inf){var e=new KeyframeEase(0,Math.max(0.1,inf));for(var d=1;d<=3;d++){try{var a=[],i;for(i=0;i<d;i++)a.push(e);
  var ki=p.keyInTemporalEase(k),ko=p.keyOutTemporalEase(k);if(cote==="in")p.setTemporalEaseAtKey(k,a,ko.length===d?ko:a);else p.setTemporalEaseAtKey(k,ki.length===d?ki:a,a);return;}catch(x){}}}
function sd_type(p,k,cote,genre){var T=KeyframeInterpolationType[genre];if(cote==="in")p.setInterpolationTypeAtKey(k,T,p.keyOutInterpolationType(k));else p.setInterpolationTypeAtKey(k,p.keyInInterpolationType(k),T);}
function sd_segment(p,k,genre,infOut,infIn){sd_type(p,k,"out",genre);sd_type(p,k+1,"in",genre==="HOLD"?"LINEAR":genre);if(genre==="BEZIER"){sd_ease(p,k,"out",infOut);sd_ease(p,k+1,"in",infIn);}}
function sd_import(ch){return app.project.importFile(new ImportOptions(new File(ch)));}
function sd_repere(l,t,txt){try{l.property("ADBE Marker").setValueAtTime(t,new MarkerValue(txt));}catch(e){}}
function sd_texte(nom,s,police,corps,coul,x,y){var l=comp.layers.addText(s);l.name=nom;var p=l.property("ADBE Text Properties").property("ADBE Text Document");var d=p.value;
  d.font=police;d.fontSize=corps;d.fillColor=sd_rgb(coul);d.applyFill=true;d.applyStroke=false;d.justification=ParagraphJustification.CENTER_JUSTIFY;p.setValue(d);sd_tr(l).property("ADBE Position").setValue([x,y]);return l;}
function sd_boite(nom,w,h,x,y,rnd,coul,op){var l=comp.layers.addShape();l.name=nom;sd_tr(l).property("ADBE Anchor Point").setValue([0,0]);sd_tr(l).property("ADBE Position").setValue([0,0]);
  var g=l.property("ADBE Root Vectors Group").addProperty("ADBE Vector Group");var r=sd_contenu(g).addProperty("ADBE Vector Shape - Rect");r.property("ADBE Vector Rect Size").setValue([w,h]);r.property("ADBE Vector Rect Position").setValue([x,y]);r.property("ADBE Vector Rect Roundness").setValue(rnd);
  sd_contenu(g).addProperty("ADBE Vector Graphic - Fill").property("ADBE Vector Fill Color").setValue(sd_rgb(coul));sd_tr(l).property("ADBE Opacity").setValue(op);return l;}
for(var i=app.project.numItems;i>=1;i--){var it=app.project.item(i);if(it instanceof CompItem&&it.name===%(nom)s)it.remove();}
var comp=app.project.items.addComp(%(nom)s,%(W)d,%(H)d,1,%(duree)s,%(fps)s);
try{comp.openInViewer();}catch(e){}   // EffectCraft ignores the curves of a composition that is not open
'''


def generer(S, source, prefixe=""):
    c, f, CAM, th = S["comp"], S["fenetre"], S["camera"], S.get("theme", {})
    W, H = FORMATS[c.get("format", "16:9")]
    nom = prefixe + c.get("nom", "Scene breakdown")
    D = float(c["duree"])
    u = min(W, H) / 1080.0   # fixed screen sizes (subtitles, title card): 1 in 1080p, 2 in 4K
    fond, texte, accent = th.get("fond", "#101418"), th.get("texte", "#F2F4F7"), th.get("accent", "#F2C94C")
    voile, police = th.get("voile", "#05070A"), th.get("police", "Inter-Medium")
    police_titre = th.get("police_titre", "Inter-Bold")
    js_ = [ENTETE % {"source": os.path.basename(source), "nom": js(nom), "W": W, "H": H, "duree": num(D), "fps": num(c.get("fps", 30))}]
    A = js_.append
    flou = bool(CAM.get("flou_de_bouge"))

    # 1 · the background
    A('var fond=comp.layers.addSolid(sd_rgb(%s),"Background",%d,%d,1);' % (js(fond), W, H))

    # 2 · the window carries the camera: its anchor = the point of the window we look at, its scale = zoom × 100,
    #     its position stays at the center of the frame. Halos and cursor are its children, in window px.
    #     No "camera" null layer: EffectCraft does not apply a null's scale to a child image (seen in testing,
    #     the image stays at 100 %%); and the window is not larger than the composition (beyond that, it misplaces its children).
    A('var fen=comp.layers.add(sd_import(%s));fen.name="Window · the camera lives here (anchor = what we look at, scale = zoom)";' % js(f["fichier"]))
    A('fen.startTime=%s;' % num(float(f.get("debut", 0))))
    A('var CA=sd_tr(fen).property("ADBE Anchor Point"),CP=sd_tr(fen).property("ADBE Position"),CE=sd_tr(fen).property("ADBE Scale"),CO=sd_tr(fen).property("ADBE Opacity");CP.setValue([%d,%d]);' % (W // 2, H // 2))
    cles = CAM["cles"]
    for k in cles:
        z = float(k.get("zoom", 1)) * 100
        A('CA.setValueAtTime(%s,[%s,%s]);CE.setValueAtTime(%s,[%s,%s]);' % (num(float(k["t"])), num(float(k["x"])), num(float(k["y"])), num(float(k["t"])), num(z), num(z)))
    for i in range(len(cles) - 1):
        genre, io, ii = ARRIVEES[cles[i + 1].get("arrivee", "pose")]
        A('sd_segment(CA,%d,"%s",%d,%d);sd_segment(CE,%d,"%s",%d,%d);' % (i + 1, genre, io, ii, i + 1, genre, io, ii))
    for i, k in enumerate(cles):
        note = k.get("note") or ""
        etiquette = "%s · zoom ×%s%s" % (k.get("arrivee", "pose") if i else "start", ("%.2f" % float(k.get("zoom", 1))).rstrip("0").rstrip("."), (" · " + note) if note else "")
        A('sd_repere(fen,%s,%s);' % (num(float(k["t"])), js(etiquette)))
    if f.get("apparition"):
        a0, a1 = f["apparition"]
        A('CO.setValueAtTime(%s,0);CO.setValueAtTime(%s,100);' % (num(float(a0)), num(float(a1))))
    if flou:
        A('try{comp.motionBlur=true;fen.motionBlur=true;}catch(e){}')

    # 3 · the halos, children of the window (window px)
    for i, h in enumerate(S.get("enfants", {}).get("halos", [])):
        x, y, w, hh = h["rect"]
        m = h.get("marge", 8)
        t0, t1 = float(h["t0"]), float(h["t1"])
        A('(function(){var l=comp.layers.addShape();l.name=%s;l.parent=fen;sd_tr(l).property("ADBE Anchor Point").setValue([0,0]);sd_tr(l).property("ADBE Position").setValue([%s,%s]);'
          'var g=l.property("ADBE Root Vectors Group").addProperty("ADBE Vector Group");var b=sd_contenu(g).addProperty("ADBE Vector Shape - Rect");'
          'b.property("ADBE Vector Rect Size").setValue([%s,%s]);b.property("ADBE Vector Rect Roundness").setValue(%s);'
          'var tm=sd_contenu(g).addProperty("ADBE Vector Filter - Trim");var st=sd_contenu(g).addProperty("ADBE Vector Graphic - Stroke");'
          'st.property("ADBE Vector Stroke Color").setValue(sd_rgb(%s));st.property("ADBE Vector Stroke Width").setValue(%s);'
          'var e=tm.property("ADBE Vector Trim End");e.setValueAtTime(%s,0);e.setValueAtTime(%s,100);'
          'var o=sd_tr(l).property("ADBE Opacity");o.setValueAtTime(%s,100);o.setValueAtTime(%s,100);o.setValueAtTime(%s,0);sd_repere(l,%s,%s);})();'
          % (js("Halo %d · child of the window%s" % (i + 1, (" · " + h["nom"]) if h.get("nom") else "")),
             num(x + w / 2), num(y + hh / 2), num(float(w + 2 * m)), num(float(hh + 2 * m)), num(float(h.get("arrondi", 12))),
             js(h.get("couleur", accent)), num(float(h.get("epaisseur", 3))),
             num(t0), num(t0 + 0.45), num(t0), num(t1), num(t1 + 0.3), num(t0), js("the outline draws in 0.45 s, fades out in 0.3 s")))

    # 4 · the cursor, child of the window: its positions are those of the clicked elements
    cu = S.get("enfants", {}).get("curseur")
    if cu and cu.get("points"):
        P = cu["points"]
        A('var cur=comp.layers.addShape();cur.name="Cursor · child of the window (positions = clicked elements)";cur.parent=fen;sd_tr(cur).property("ADBE Anchor Point").setValue([0,0]);'
          'var cg=cur.property("ADBE Root Vectors Group").addProperty("ADBE Vector Group");var cp=sd_contenu(cg).addProperty("ADBE Vector Shape - Group");var sh=new Shape();'
          'sh.vertices=[[0,0],[23,17],[12,19],[19,33],[14,35],[7,21],[0,29]];sh.closed=true;cp.property("ADBE Vector Shape").setValue(sh);'
          'var cs=sd_contenu(cg).addProperty("ADBE Vector Graphic - Stroke");cs.property("ADBE Vector Stroke Color").setValue(sd_rgb(%s));cs.property("ADBE Vector Stroke Width").setValue(2.4);'
          'sd_contenu(cg).addProperty("ADBE Vector Graphic - Fill").property("ADBE Vector Fill Color").setValue(sd_rgb(%s));'
          'var UP=sd_tr(cur).property("ADBE Position"),US=sd_tr(cur).property("ADBE Scale"),UO=sd_tr(cur).property("ADBE Opacity");'
          % (js(cu.get("contour", "#FFFFFF")), js(cu.get("couleur", fond))))
        A('UO.setValueAtTime(%s,0);UO.setValueAtTime(%s,100);UO.setValueAtTime(%s,100);UO.setValueAtTime(%s,0);'
          % (num(max(0.0, P[0]["t"] - 0.3)), num(float(P[0]["t"])), num(float(P[-1]["t"])), num(P[-1]["t"] + 0.3)))
        for p in P:
            A('UP.setValueAtTime(%s,[%s,%s]);' % (num(float(p["t"])), num(float(p["x"])), num(float(p["y"]))))
        A('for(var k=1;k<UP.numKeys;k++)sd_segment(UP,k,"BEZIER",50,50);')
        e0 = float(cu.get("echelle", 100))
        A('US.setValue([%s,%s]);' % (num(e0), num(e0)))
        for t in cu.get("clics", []):
            A('US.setValueAtTime(%s,[%s,%s]);US.setValueAtTime(%s,[%s,%s]);US.setValueAtTime(%s,[%s,%s]);sd_repere(cur,%s,"click");'
              % (num(t - 0.04), num(e0), num(e0), num(float(t)), num(e0 * 0.84), num(e0 * 0.84), num(t + 0.14), num(e0), num(e0), num(float(t))))

    # 5 · the screen: fixed subtitles, above the window
    E = S.get("ecran", {})
    corps = float(E.get("corps_sous_titres", 29)) * u
    limite = int(E.get("caracteres_par_ligne", 64))
    for i, (a, b, t) in enumerate(E.get("sous_titres", [])):
        t = deux_lignes(t, limite)
        lignes = t.split("\r")
        w = min(W - 160 * u, corps * 0.54 * max(len(x) for x in lignes) + 56 * u)
        h = 24 * u + corps * 1.38 * len(lignes)
        bas = H - 48 * u
        A('var sb=sd_boite("Subtitle background %d",%d,%d,%d,%d,%s,%s,82);sb.inPoint=%s;sb.outPoint=%s;'
          % (i + 1, round(w), round(h), W // 2, round(bas - h / 2), num(14 * u), js(voile), num(float(a)), num(float(b))))
        A('var st=sd_texte("Subtitle %d",%s,%s,%s,%s,%d,%d);st.inPoint=%s;st.outPoint=%s;'
          % (i + 1, js(t), js(police), num(corps), js(texte), W // 2, round(bas - h + 12 * u + corps), num(float(a)), num(float(b))))
    for i, tx in enumerate(E.get("textes", [])):
        A('var tx=sd_texte(%s,%s,%s,%s,%s,%s,%s);tx.inPoint=%s;tx.outPoint=%s;'
          % (js("Text %d · fixed on screen" % (i + 1)), js(tx["texte"]), js(tx.get("police", police)), num(float(tx.get("corps", 48))),
             js(tx.get("couleur", texte)), num(float(tx["x"])), num(float(tx["y"])), num(float(tx["t0"])), num(float(tx["t1"]))))

    # 6 · the title card, on top of everything; the window appears as it fades out
    it = E.get("intertitre")
    if it:
        t1 = float(it["t1"])
        A('var cf=comp.layers.addSolid(sd_rgb(%s),"Title card · background",%d,%d,1);var cfo=sd_tr(cf).property("ADBE Opacity");cfo.setValueAtTime(%s,100);cfo.setValueAtTime(%s,0);'
          % (js(fond), W, H, num(t1 - 0.45), num(t1)))
        A('var ct=sd_texte("Title card · title",%s,%s,%s,%s,%d,%d);ct.outPoint=%s;' % (js(it.get("titre", "")), js(police_titre), num(92 * u), js(texte), W // 2, H // 2 + 20 * u, num(t1)))
        if it.get("sous_titre"):
            A('var cl=sd_texte("Title card · subtitle",%s,%s,%s,%s,%d,%d);cl.outPoint=%s;' % (js(it["sous_titre"]), js(police), num(30 * u), js(th.get("secondaire", texte)), W // 2, H // 2 + 90 * u, num(t1)))
        if it.get("etiquette"):
            lw = (40 + 15 * len(it["etiquette"])) * u
            A('var cb=sd_boite("Title card · label",%d,%d,%d,%d,%s,%s,100);cb.outPoint=%s;var cn=sd_texte(%s,%s,%s,%s,%s,%d,%d);cn.outPoint=%s;'
              % (lw, 44 * u, W // 2, H // 2 - 88 * u, num(8 * u), js(accent), num(t1), js("Title card · " + it["etiquette"]), js(it["etiquette"]),
                 js(police_titre), num(26 * u), js(fond), W // 2, H // 2 - 78 * u, num(t1)))

    # 7 · the sound: each voice at its moment, the music offset, one-shot sounds
    son = S.get("son", {})
    for i, v in enumerate(son.get("voix", [])):
        A('var v=comp.layers.add(sd_import(%s));v.name=%s;v.startTime=%s;'
          % (js(v["fichier"]), js("Voice %d · %.2f s%s" % (i + 1, float(v["t"]), (" · " + v["texte"][:40]) if v.get("texte") else "")), num(float(v["t"]))))
    for i, v in enumerate(son.get("sons", [])):
        A('var sx=comp.layers.add(sd_import(%s));sx.name=%s;sx.startTime=%s;' % (js(v["fichier"]), js("Sound %d · %s" % (i + 1, v.get("nom", "gesture"))), num(float(v["t"]))))
    mu = son.get("musique")
    if mu:
        d = float(mu.get("decalage", 0))
        A('var mu=comp.layers.add(sd_import(%s));mu.name=%s;mu.startTime=%s;'
          % (js(mu["fichier"]), js("Music%s" % ((" · offset by %.2f s" % d) if d else "")), num(-d)))
    if flou:   # motion blur on each layer that moves with the camera (the window and its children)
        A('for(var q=1;q<=comp.numLayers;q++){var lq=comp.layer(q);if(lq===fen||lq.parent===fen){try{lq.motionBlur=true;}catch(e){}}}')
    A('"ok "+comp.numLayers+" layers";')
    return nom, "\n".join(js_) + "\n"


def verifier_es3(code):
    import re
    for motif, quoi in ((r"\blet\s", "let"), (r"\bconst\s", "const"), (r"=>", "arrow function"), (r"`", "template literal")):
        if re.search(motif, code):
            return quoi
    return None


def main(argv):
    if not argv or argv[0] in ("-h", "--help"):
        print(__doc__)
        return 0
    src = argv[0]
    prefixe = argv[argv.index("--prefixe") + 1] if "--prefixe" in argv else ""
    sortie = argv[argv.index("-o") + 1] if "-o" in argv else os.path.splitext(src)[0] + ".jsx"
    S = charger(src)
    nom, code = generer(S, src, prefixe)
    ecart = verifier_es3(code)
    if ecart:
        faute("ES3 violation in the output script (%s): generator bug" % ecart)
    open(sortie, "w", encoding="utf-8").write(code)
    n = sum(1 for l in code.split(";") if "layers.add" in l)
    print("script: %s (composition \"%s\", %d layers)" % (sortie, nom, n))
    if "--jsx-seul" in argv:
        return 0
    r = subprocess.run([sys.executable, os.path.join(ICI, "ec.py"), "script", sortie], capture_output=True, text=True)
    print((r.stdout or "").strip()[:600])
    if r.returncode:
        print((r.stderr or "").strip()[:600], file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
