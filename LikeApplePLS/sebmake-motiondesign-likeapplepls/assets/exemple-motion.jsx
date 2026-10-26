// exemple-motion : script généré par build_motion.mjs (skill sebmake-motiondesign-likeapplepls) depuis exemple-motion.json.
// ExtendScript ES3 : After Effects (Fichier > Scripts > Exécuter le fichier de script) ou EffectCraft (script.run).
// Composition 1920 × 1080, 30 i/s, 20 s, époque 2024-2026. 1 u = 10.8 px (1 % du petit côté).
// Recettes : balayage-lumiere, camera-poussee, chiffre-pose, coupe, liste-cascade, logo-fin, panneau-pose, produit-entree, titre-fondu-montee, zoom-detail.
// Courbes (cubic-bezier → KeyframeEase calculée par md_anime ; vitesses en multiple de la vitesse moyenne) :
//   ease-in-out      (0.42, 0, 0.58, 1)  sortie 42 % × 0 ; entrée 42 % × 0 — opacité du chiffre posé (ajustement commun, 18 chiffres) ; voile d’interface
//   easeInOutCubic   (0.645, 0.045, 0.355, 1)  sortie 64.5 % × 0.07 ; entrée 64.5 % × 0 — opacité des titres « fondu + montée » 4 sur 4 ; lignes de cascade 11 sur 13
//   easeInOutQuint   (0.86, 0, 0.07, 1)  sortie 86 % × 0 ; entrée 93 % × 0 — montée des lignes de cascade (0,10 s) 7 lignes sur 11 ; cascade rapide (0,05 s)
//   easeOutExpo      (0.19, 1, 0.22, 1)  sortie 19 % × 5.263 ; entrée 78 % × 0 — montée des titres 4 sur 4 ; échelle du chiffre posé 11 sur 18
//   out-cubic        (0.33, 1, 0.68, 1)  sortie 33 % × 3.03 ; entrée 32 % × 0 — entrée latérale floue 8 sur 8 (courbe groupée, erreur 0,075)
//   out-expo         (0.16, 1, 0.3, 1)  sortie 16 % × 6.25 ; entrée 70 % × 0 — panneau latéral (1 sur 4 mesurés) ; fond qui se floute (fin en douceur 8 sur 14)
//   zoom-2024        (0.56, 0.32, 0.19, 0.98)  sortie 56 % × 0.571 ; entrée 81 % × 0.025 — zoom dans un détail, 2024-2026 : 18 instances, erreur 0,028
// Relancer le script remplace la composition du même nom. Rien n'est enregistré : enregistrez le projet vous-même.
(function () {
var NOM = "exemple-motion", W = 1920, H = 1080, U = 10.8, IPS = 30, DUREE = 20;
var THEME = {"repli":"#2A2C31","repli_trait":"#55585F"};
var C = {
  "ease-in-out": [0.42, 0, 0.58, 1],
  "easeInOutCubic": [0.645, 0.045, 0.355, 1],
  "easeInOutQuint": [0.86, 0, 0.07, 1],
  "easeOutExpo": [0.19, 1, 0.22, 1],
  "out-cubic": [0.33, 1, 0.68, 1],
  "out-expo": [0.16, 1, 0.3, 1],
  "zoom-2024": [0.56, 0.32, 0.19, 0.98]
};
function md_rgb(h) { h = String(h).replace("#", ""); return [parseInt(h.substr(0, 2), 16) / 255, parseInt(h.substr(2, 2), 16) / 255, parseInt(h.substr(4, 2), 16) / 255]; }
function md_tr(l) { return l.property("ADBE Transform Group"); }
function md_cale(t) { return Math.round(t / FD) * FD; }
function md_tab(x, n) { var a = []; for (var i = 0; i < n; i++) a.push(x); return a; }
function md_dims(p) { var t = p.propertyValueType; if (t === PropertyValueType.ThreeD) return 3; if (t === PropertyValueType.TwoD) return 2; return 1; }
function md_comp(v, j) { return (v instanceof Array) ? v[j] : v; }
// KeyframeEase d'une cubic-bezier b = [x1, y1, x2, y2] ; cote = "sortie" (clé de départ) ou "entree" (clé d'arrivée)
function md_ease(b, dv, T, cote) {
  var x1 = b[0], y1 = b[1], x2 = b[2], y2 = b[3], m = dv / T, inf, pente;
  if (cote === "sortie") {
    if (x1 <= 0.000001 && y1 <= 0.000001) { inf = 0.1; pente = x2 > 0.000001 ? y2 / x2 : 1; }
    else { inf = Math.max(0.1, x1 * 100); pente = y1 / Math.max(x1, 0.001); }
  } else {
    if (x2 >= 0.999999 && y2 >= 0.999999) { inf = 0.1; pente = x1 < 0.999999 ? (1 - y1) / (1 - x1) : 1; }
    else { inf = Math.max(0.1, (1 - x2) * 100); pente = (1 - y2) / Math.max(1 - x2, 0.001); }
  }
  return new KeyframeEase(pente * m, Math.min(100, inf));
}
function md_garde(p, k, cote, n) {
  try { var e = cote === "in" ? p.keyInTemporalEase(k) : p.keyOutTemporalEase(k); if (e && e.length === n) return e; } catch (x) {}
  return md_tab(new KeyframeEase(0, 33.333), n);
}
var MD_CLES = 0;
// Pose deux clés (t0, v0) → (t1, v1) et la courbe b (null = linéaire). Temps calés sur l'image, au moins une image d'écart.
function md_anime(p, t0, v0, t1, v1, b) {
  var KI = KeyframeInterpolationType;
  t0 = md_cale(t0); t1 = md_cale(t1); if (t1 < t0 + FD * 0.999) t1 = t0 + FD;
  p.setValueAtTime(t0, v0); p.setValueAtTime(t1, v1); MD_CLES += 2;
  var k0 = p.nearestKeyIndex(t0), k1 = p.nearestKeyIndex(t1);
  if (!b || (b[0] === 0 && b[1] === 0 && b[2] === 1 && b[3] === 1)) {
    p.setInterpolationTypeAtKey(k0, p.keyInInterpolationType(k0), KI.LINEAR);
    p.setInterpolationTypeAtKey(k1, KI.LINEAR, p.keyOutInterpolationType(k1));
    return;
  }
  p.setInterpolationTypeAtKey(k0, p.keyInInterpolationType(k0), KI.BEZIER);
  p.setInterpolationTypeAtKey(k1, KI.BEZIER, p.keyOutInterpolationType(k1));
  var n = md_dims(p), so = [], si = [], T = t1 - t0;
  for (var j = 0; j < n; j++) { var dv = md_comp(v1, j) - md_comp(v0, j); so.push(md_ease(b, dv, T, "sortie")); si.push(md_ease(b, dv, T, "entree")); }
  p.setTemporalEaseAtKey(k0, md_garde(p, k0, "in", n), so);
  p.setTemporalEaseAtKey(k1, si, md_garde(p, k1, "out", n));
}
// Valeur tenue à partir de t (clé HOLD) : un saut net, sans courbe.
function md_saut(p, t, v) { t = md_cale(t); p.setValueAtTime(t, v); MD_CLES += 1; var k = p.nearestKeyIndex(t); p.setInterpolationTypeAtKey(k, p.keyInInterpolationType(k), KeyframeInterpolationType.HOLD); }
function md_valeur(p, t) { return p.numKeys ? p.valueAtTime(md_cale(t), false) : p.value; }
function md_police(liste) {
  try { if (app.fonts && app.fonts.getFontsByPostScriptName) { for (var i = 0; i < liste.length; i++) { var f = app.fonts.getFontsByPostScriptName(liste[i]); if (f && f.length) return liste[i]; } } } catch (e) {}
  return liste[0];
}
function md_repere(l, t, texte) { try { var m = new MarkerValue(texte); l.property("ADBE Marker").setValueAtTime(md_cale(t), m); } catch (e) {} }
// Un élément : le calque, ses propriétés (position en dimensions séparées), sa taille à l'écran.
function md_el(l, cx, cy, w, h) {
  var tg = md_tr(l), pos = tg.property("ADBE Position");
  if (!pos.dimensionsSeparated) pos.dimensionsSeparated = true;
  var x = tg.property("ADBE Position_0"), y = tg.property("ADBE Position_1");
  x.setValue(cx); y.setValue(cy);
  return { l: l, x: x, y: y, s: tg.property("ADBE Scale"), o: tg.property("ADBE Opacity"), r: tg.property("ADBE Rotate Z"), a: tg.property("ADBE Anchor Point"), w: w, h: h, cx: cx, cy: cy, ech: 100, repli: false };
}
function md_texte(nom, chaine, polices, corps, coul, just, interligne, approche) {
  var l = comp.layers.addText(chaine); l.name = nom;
  var p = l.property("ADBE Text Properties").property("ADBE Text Document"), d = p.value;
  d.font = md_police(polices); d.fontSize = corps; d.fillColor = md_rgb(coul); d.applyFill = true; d.applyStroke = false;
  d.justification = just === "gauche" ? ParagraphJustification.LEFT_JUSTIFY : (just === "droite" ? ParagraphJustification.RIGHT_JUSTIFY : ParagraphJustification.CENTER_JUSTIFY);
  if (approche) d.tracking = approche;
  if (interligne) { try { d.autoLeading = false; d.leading = interligne; } catch (e) {} }
  p.setValue(d);
  return l;
}
// Texte posé par son centre (ou par son bord gauche, au milieu de la hauteur).
function md_placerTexte(l, x, y, gauche) {
  var r = l.sourceRectAtTime(0, false);
  md_tr(l).property("ADBE Anchor Point").setValue([gauche ? r.left : r.left + r.width / 2, r.top + r.height / 2]);
  var e = md_el(l, x, y, r.width, r.height); return e;
}
function md_largeurTexte(chaine, polices, corps) { var l = md_texte("mesure", chaine, polices, corps, "#FFFFFF", "gauche"); var r = l.sourceRectAtTime(0, false); l.remove(); return { gauche: r.left, droite: r.left + r.width, haut: r.top, bas: r.top + r.height }; }
var MD_IMPORTS = {}, MD_REPLIS = [];
// Dossier du script (After Effects : $.fileName) ; vide si l'outil ne le donne pas (EffectCraft via script.run).
var MD_BASE = (function () { try { if (typeof $ !== "undefined" && $.fileName) return new File($.fileName).parent.fsName; } catch (e) {} return ""; })();
// chemin = [relatif au script, absolu au moment de la génération] : on essaie l'un puis l'autre.
function md_importer(chemin) {
  var cands = (chemin instanceof Array) ? [] : [chemin];
  if (chemin instanceof Array) { if (MD_BASE && chemin[0]) cands.push(MD_BASE + "/" + chemin[0]); if (chemin[1]) cands.push(chemin[1]); }
  var cle = cands.join("|");
  if (MD_IMPORTS.hasOwnProperty(cle)) return MD_IMPORTS[cle];
  var it = null;
  for (var k = 0; k < cands.length && !it; k++) {
    try {
      var f = new File(cands[k]);
      for (var i = 1; i <= app.project.numItems; i++) { var c = app.project.item(i); try { if (c instanceof FootageItem && c.file && c.file.fsName === f.fsName) { it = c; break; } } catch (e1) {} }
      if (!it) { var io = new ImportOptions(f); if (io.canImportAs(ImportAsType.FOOTAGE)) io.importAs = ImportAsType.FOOTAGE; it = app.project.importFile(io); }
    } catch (e) { it = null; }
  }
  MD_IMPORTS[cle] = it; return it;
}
function md_nomFichier(chemin) { return (chemin instanceof Array) ? (chemin[0] || chemin[1]) : chemin; }
function md_forme(nom, w, h, rayon, coul, contour, ep) {
  var l = comp.layers.addShape(); l.name = nom; md_tr(l).property("ADBE Anchor Point").setValue([0, 0]);
  var g = l.property("ADBE Root Vectors Group").addProperty("ADBE Vector Group"); g.name = "Forme";
  var c = g.property("ADBE Vectors Group");
  var r = c.addProperty("ADBE Vector Shape - Rect"); r.property("ADBE Vector Rect Size").setValue([w, h]); r.property("ADBE Vector Rect Roundness").setValue(rayon || 0);
  if (coul) c.addProperty("ADBE Vector Graphic - Fill").property("ADBE Vector Fill Color").setValue(md_rgb(coul));
  if (contour) { var s = c.addProperty("ADBE Vector Graphic - Stroke"); s.property("ADBE Vector Stroke Color").setValue(md_rgb(contour)); s.property("ADBE Vector Stroke Width").setValue(ep || 2); }
  return l;
}
function md_rond(nom, d, coul) {
  var l = comp.layers.addShape(); l.name = nom; md_tr(l).property("ADBE Anchor Point").setValue([0, 0]);
  var g = l.property("ADBE Root Vectors Group").addProperty("ADBE Vector Group"); g.name = "Rond";
  var c = g.property("ADBE Vectors Group"); var e = c.addProperty("ADBE Vector Shape - Ellipse"); e.property("ADBE Vector Ellipse Size").setValue([d[0], d[1]]);
  c.addProperty("ADBE Vector Graphic - Fill").property("ADBE Vector Fill Color").setValue(md_rgb(coul));
  return l;
}
// Repli neutre quand un fichier manque : un cadre arrondi et ses deux diagonales, au format attendu.
function md_repli(nom, w, h, coul, trait) {
  var l = md_forme(nom, w, h, Math.min(w, h) * 0.06, coul, trait, Math.max(2, U * 0.2));
  var g = l.property("ADBE Root Vectors Group").addProperty("ADBE Vector Group"); g.name = "Diagonales";
  var c = g.property("ADBE Vectors Group");
  var d1 = c.addProperty("ADBE Vector Shape - Group"), s1 = new Shape(); s1.vertices = [[-w / 2, -h / 2], [w / 2, h / 2]]; s1.closed = false; d1.property("ADBE Vector Shape").setValue(s1);
  var d2 = c.addProperty("ADBE Vector Shape - Group"), s2 = new Shape(); s2.vertices = [[w / 2, -h / 2], [-w / 2, h / 2]]; s2.closed = false; d2.property("ADBE Vector Shape").setValue(s2);
  var st = c.addProperty("ADBE Vector Graphic - Stroke"); st.property("ADBE Vector Stroke Color").setValue(md_rgb(trait)); st.property("ADBE Vector Stroke Width").setValue(Math.max(1, U * 0.12));
  return l;
}
// Image : importée et mise à la hauteur voulue (px) ; sinon repli neutre au ratio donné.
function md_image(nom, chemin, haut, larg, ratio, cx, cy) {
  var it = chemin ? md_importer(chemin) : null, e;
  if (it) {
    var l = comp.layers.add(it); l.name = nom;
    var s = haut ? haut / it.height * 100 : larg / it.width * 100;
    e = md_el(l, cx, cy, it.width * s / 100, it.height * s / 100); e.s.setValue([s, s, 100]); e.ech = s; e.sw = it.width; e.sh = it.height;
    return e;
  }
  var h = haut || larg / ratio, w = larg || haut * ratio;
  var r = md_repli("[REPLI] " + nom + (chemin ? " (fichier absent : " + md_nomFichier(chemin) + ")" : ""), w, h, THEME.repli, THEME.repli_trait);
  MD_REPLIS.push(nom + (chemin ? " \u2190 " + md_nomFichier(chemin) : ""));
  e = md_el(r, cx, cy, w, h); e.repli = true; e.sw = w; e.sh = h; return e;
}
function md_solide(nom, coul, w, h) { var l = comp.layers.addSolid(md_rgb(coul), nom, Math.round(w), Math.round(h), 1); return md_el(l, W / 2, H / 2, w, h); }
function md_nul(nom, ax, ay) { var n = comp.layers.addNull(); n.name = nom; md_tr(n).property("ADBE Anchor Point").setValue([ax, ay]); var e = md_el(n, ax, ay, 0, 0); return e; }
function md_flou(e, bords) { var fx = e.l.Effects.addProperty("ADBE Gaussian Blur 2"); if (bords) { try { fx.property(3).setValue(1); } catch (x) {} } return fx.property(1); }
// Flou gaussien : le réglage « Flou » vaut 2 σ (mesuré dans EffectCraft : 2,00 / 1,98 / 1,97 pour 10, 20, 40).
function md_sigma(s) { return 2 * s; }
function md_cache(cible, cache) {
  cache.moveBefore(cible);
  if (typeof cible.setTrackMatte === "function") { cible.setTrackMatte(cache, TrackMatteType.ALPHA); }
  else { cible.trackMatteType = TrackMatteType.ALPHA; }
}
function md_presence(e, t0, t1) { e.l.inPoint = Math.max(0, md_cale(t0)); e.l.outPoint = Math.min(comp.duration, md_cale(t1)); }
function md_bornes(e) {
  try { if (e.l.source && e.l.source.width) return { left: 0, top: 0, width: e.l.source.width, height: e.l.source.height }; } catch (x) {}
  var r = e.l.sourceRectAtTime(0, false); return { left: r.left, top: r.top, width: r.width, height: r.height };
}
try { app.beginUndoGroup(NOM); } catch (e0) {}
// relancer remplace la composition du même nom ; ses solides (sans fichier, utilisés par elle seule) partent avec elle, sinon ils resteraient orphelins dans le projet
for (var i0 = app.project.numItems; i0 >= 1; i0--) { var it0 = app.project.item(i0); if (it0 instanceof CompItem && it0.name === NOM) { var so0 = [];
  for (var j0 = 1; j0 <= it0.numLayers; j0++) { try { var s0 = it0.layer(j0).source; if (s0 && s0 instanceof FootageItem && !s0.file && s0.mainSource && s0.mainSource.color && s0.usedIn.length === 1) so0.push(s0); } catch (e3) {} }
  it0.remove(); for (var k0 = 0; k0 < so0.length; k0++) { try { so0[k0].remove(); } catch (e4) {} } } }
var comp = app.project.items.addComp(NOM, W, H, 1, DUREE, IPS);
var FD = comp.frameDuration;
comp.bgColor = md_rgb("#0E1013");
try { comp.openInViewer(); } catch (e1) {} // indispensable dans EffectCraft : sans comp active, interpolations et eases sont ignorées
comp.motionBlur = true; try { comp.shutterAngle = 120; comp.shutterPhase = -60; } catch (e2) {} // obturateur 118° mesuré (74 à 169°) ; phase centrée : convention

// ═══ 1. Calques, de l’arrière vers l’avant ═══

// ── fond (fond) : coupe — Déjà plein à la première image 
var e_fond = md_solide("fond \u2014 fond uni", "#0E1013", W, H);

// ── surtitre (surtitre) : titre-fondu-montee — 4 titres sur 29 (2024 ×2, 2025, 2026), identiques au centième dans 3 cas sur 4. Opacité ea
var e_surtitre = md_placerTexte(md_texte("surtitre \u2014 Nouveau", "Nouveau", ["Inter-Medium","ArialMT"], 34.56, "#4C8DFF", "centre", 0, 0), 960, 442.8);

// ── titre (titre) : titre-fondu-montee — 4 titres sur 29 (2024 ×2, 2025, 2026), identiques au centième dans 3 cas sur 4. Opacité ea
var e_titre = md_placerTexte(md_texte("titre \u2014 Un objet, rien de plus.", "Un objet, rien de plus.", ["Inter-SemiBold","Inter-Bold","Arial-BoldMT"], 97.2, "#F4F4F2", "centre", 0, -10), 960, 540);

// ── cam-produit (nul-camera) : camera-poussee — Avancée de caméra 
var e_cam_produit = md_nul("cam-produit \u2014 nul de cam\u00e9ra", 960, 540);

// ── produit (image) : produit-entree — Le produit arrive par la droite sur la coupe (7 sur 7 à ± 0,1 s), freine et se pose 
var e_produit = md_image("produit \u2014 image", ["exemple/produit.png",""], 777.6, 0, 0.64, 960, 561.6);

// ── liste (liste) : liste-cascade — 3 listes (2024, 2025 ×2), 10 écarts de 0,093 à 0,113 s ; chaque ligne fond en easeInOutCub
var e_liste = { lignes: [], pas: 110.16 };
(function () { var L = ["L\u00e9ger.","Silencieux.","Fait pour durer."], pol = ["Inter-Regular","ArialMT"], maxw = 0, ls = [];
  for (var i = 0; i < L.length; i++) { var l = md_texte("liste \u2014 ligne " + (i + 1), L[i], pol, 64.8, "#F4F4F2", "gauche", 0, 0); ls.push(l); maxw = Math.max(maxw, l.sourceRectAtTime(0, false).width); }
  for (var j = 0; j < ls.length; j++) { var y = 540 + (j - (ls.length - 1) / 2) * 110.16; e_liste.lignes.push(md_placerTexte(ls[j], 960 - maxw / 2, y, true)); }
  e_liste.largeur = maxw; })();

// ── chiffre (chiffre) : chiffre-pose — 18 chiffres sur 27 (nov. 2020 2, sept. 2025 14, sept. 2026 2) 
var e_chiffre = md_placerTexte(md_texte("chiffre \u2014 [\u00c0 FOURNIR]", "[\u00c0 FOURNIR]", ["Inter-Bold","Arial-BoldMT"], 151.2, "#F4F4F2", "centre", 0, -20), 960, 496.8);
var e_chiffre_lib = md_placerTexte(md_texte("chiffre \u2014 libell\u00e9", "heures d'autonomie", ["Inter-Regular","ArialMT"], 39.96, "#9A9CA3", "centre", 0, 0), 960, 496.8 + e_chiffre.h / 2 + 55.944);

// ── cam-panneau (nul-camera) : zoom-detail — Zoom dans un détail 
var e_cam_panneau = md_nul("cam-panneau \u2014 nul de cam\u00e9ra", 960, 540);

// ── panneau (capture) : panneau-pose — Panneau qui arrive 
var e_panneau = md_image("panneau \u2014 capture", ["exemple/panneau.png",""], 604.8, 0, 1.5, 960, 561.6);

// ── logo (logo) : logo-fin — Nom ou logo de fin 
var e_logo = md_image("logo \u2014 logo", ["exemple/logo.png",""], 97.2, 0, 4.2, 960, 529.2);
if (e_logo.repli) { e_logo.l.remove(); MD_REPLIS.pop(); MD_REPLIS.push("logo : logo absent, remplac\u00e9 par le nom"); e_logo = md_placerTexte(md_texte("logo \u2014 nom (repli du logo)", "exemple", ["Inter-SemiBold","Inter-Bold","Arial-BoldMT"], 58.32, "#F4F4F2", "centre", 0, -10), 960, 529.2); }

// ── mention (phrase) : logo-fin — Nom ou logo de fin 
var e_mention = md_placerTexte(md_texte("mention \u2014 Bient\u00f4t disponible.", "Bient\u00f4t disponible.", ["Inter-Regular","ArialMT"], 30.24, "#9A9CA3", "centre", 0, 0), 960, 637.2);

// ═══ 2. Parentage (nuls neutres : rien ne bouge) ═══
e_produit.l.parent = e_cam_produit.l;
e_panneau.l.parent = e_cam_panneau.l;

// ═══ 3. Animations ═══

// fond : coupe (début 0 s, fin d’entrée 0 s, présence jusqu’à 20 s)

// surtitre : titre-fondu-montee (début 0.1 s, fin d’entrée 1.333 s, présence jusqu’à 3 s)
md_repere(e_surtitre.l, 0.1, "titre-fondu-montee : opacit\u00e9 easeInOutCubic T 0.77 s ; mont\u00e9e 15.3 u easeOutExpo T 0.92 s");
md_anime(e_surtitre.o, 0.1, 0, 0.87, 100, C["easeInOutCubic"]);
md_anime(e_surtitre.y, 0.4, e_surtitre.cy + 165.24, 1.32, e_surtitre.cy, C["easeOutExpo"]);

// titre : titre-fondu-montee (début 0.1 s, fin d’entrée 1.333 s, présence jusqu’à 3 s)
md_repere(e_titre.l, 0.1, "titre-fondu-montee : opacit\u00e9 easeInOutCubic T 0.77 s ; mont\u00e9e 15.3 u easeOutExpo T 0.92 s");
md_anime(e_titre.o, 0.1, 0, 0.87, 100, C["easeInOutCubic"]);
md_anime(e_titre.y, 0.4, e_titre.cy + 165.24, 1.32, e_titre.cy, C["easeOutExpo"]);

// cam-produit : camera-poussee (début 3 s, fin d’entrée 3 s, présence jusqu’à 6.4 s)
md_repere(e_cam_produit.l, 3, "camera-poussee");
md_anime(e_cam_produit.s, 3, [100, 100, 100], 6.4, [105, 105, 100], null); // linéaire, du début à la fin du plan

// produit : produit-entree (début 3 s, fin d’entrée 3.9 s, présence jusqu’à 6.4 s)
md_repere(e_produit.l, 3, "produit-entree : par la droite, out-cubic T 0.9 s, flou de boug\u00e9 120\u00b0");
md_anime(e_produit.x, 3, W + e_produit.w / 2 + 21.6, 3.9, e_produit.cx, C["out-cubic"]); e_produit.l.motionBlur = true;

// liste : liste-cascade (début 6.467 s, fin d’entrée 7.833 s, présence jusqu’à 9.6 s)
// une ligne toutes les 0.1 s ; opacité easeInOutCubic T 1.14 s ; montée 21 u easeInOutQuint T 1.17 s
for (var i_e_liste = 0; i_e_liste < e_liste.lignes.length; i_e_liste++) { var q = e_liste.lignes[i_e_liste], t = 6.467 + i_e_liste * 0.1;
  md_anime(q.o, t, 0, t + 1.14, 100, C["easeInOutCubic"]);
  md_anime(q.y, t, q.cy + 226.8, t + 1.17, q.cy, C["easeInOutQuint"]);
  md_repere(q.l, t, "liste-cascade : ligne " + (i_e_liste + 1)); md_presence(q, 6.467, 9.6); }

// chiffre : chiffre-pose (début 9.8 s, fin d’entrée 10.467 s, présence jusqu’à 12.4 s)
md_repere(e_chiffre.l, 9.8, "chiffre-pose : \u00d74.1 \u2192 1 easeOutExpo T 0.67 s ; opacit\u00e9 T 0.358 s ; flou \u03c3 6.7 u \u2192 0");
md_anime(e_chiffre.s, 9.8, [e_chiffre.ech * 4.1, e_chiffre.ech * 4.1, 100], 10.47, [e_chiffre.ech, e_chiffre.ech, 100], C["easeOutExpo"]);
md_anime(e_chiffre.o, 9.8, 0, 10.158, 100, C["ease-in-out"]);
var f_e_chiffre = md_flou(e_chiffre, false); md_anime(f_e_chiffre, 9.8, md_sigma(72.36), 10.47, 0, C["easeOutExpo"]);
md_anime(e_chiffre_lib.o, 9.967, 0, 10.45, 100, C["ease-in-out"]); md_presence(e_chiffre_lib, 9.967, 12.4); md_repere(e_chiffre_lib.l, 9.967, "libell\u00e9 : milieu du fondu +0.23 s apr\u00e8s celui du chiffre, fondu sur place 0.483 s");

// cam-panneau : zoom-detail (début 13.3 s, fin d’entrée 14.267 s, présence jusqu’à 20 s)
md_repere(e_cam_panneau.l, 13.3, "zoom-detail : \u00d72 vers le point 64.2,60.1 %, zoom-2024, T 0.95 s");
(function () { var b = { left: 0, top: 0, width: W, height: H }, ax = b.left + b.width * 0.642, ay = b.top + b.height * 0.601, a0 = e_cam_panneau.a.value, k = e_cam_panneau.ech / 100;
  e_cam_panneau.a.setValue([ax, ay]); var px0 = md_valeur(e_cam_panneau.x, 13.3) + (ax - a0[0]) * k, py0 = md_valeur(e_cam_panneau.y, 13.3) + (ay - a0[1]) * k;
  if (e_cam_panneau.x.numKeys === 0) e_cam_panneau.x.setValue(px0); if (e_cam_panneau.y.numKeys === 0) e_cam_panneau.y.setValue(py0);
  md_anime(e_cam_panneau.s, 13.3, [e_cam_panneau.ech, e_cam_panneau.ech, 100], 14.25, [e_cam_panneau.ech * 2, e_cam_panneau.ech * 2, 100], C["zoom-2024"]);
  md_anime(e_cam_panneau.x, 13.3, px0, 14.25, 960, C["zoom-2024"]); md_anime(e_cam_panneau.y, 13.3, py0, 14.25, 540, C["zoom-2024"]); })();

// panneau : panneau-pose (début 12.6 s, fin d’entrée 13.267 s, présence jusqu’à 16.9 s)
md_repere(e_panneau.l, 12.6, "panneau-pose : depuis bas, out-expo, T 0.668 s (0.36 s visibles)");
md_anime(e_panneau.y, 12.6, e_panneau.cy + 432, 13.268, e_panneau.cy, C["out-expo"]);
md_anime(e_panneau.o, 12.6, 0, 12.823, 100, null); // convention : fondu sur le premier tiers

// logo : logo-fin (début 17.4 s, fin d’entrée 17.4 s, présence jusqu’à 20 s)
md_repere(e_logo.l, 17.4, "logo-fin : \u00e0 la coupe, immobile");

// mention : logo-fin (début 17.4 s, fin d’entrée 17.4 s, présence jusqu’à 20 s)
md_repere(e_mention.l, 17.4, "logo-fin : \u00e0 la coupe, immobile");

// ═══ 4. Présence des calques (points d’entrée et de sortie) ═══
md_presence(e_fond, 0, 20);
md_presence(e_surtitre, 0.1, 3);
md_presence(e_titre, 0.1, 3);
md_presence(e_produit, 3, 6.4);
md_presence(e_chiffre, 9.8, 12.4);
md_presence(e_panneau, 12.6, 16.9);
md_presence(e_logo, 17.4, 20);
md_presence(e_mention, 17.4, 20);

// ═══ 5. Transitions ═══

// transition passage-noir à 16.4 s : panneau → logo, mention
(function () { var n = md_solide("Noir \u2014 passage-noir 16.4 s", "#000000", W, H);
  md_anime(n.o, 16.4, 0, 16.9, 100, null); md_anime(n.o, 17.4, 100, 17.9, 0, null); md_presence(n, 16.4, 17.933); md_repere(n.l, 16.4, "passage-noir : linéaire 0.5 s, noir 0.5 s, linéaire 0.5 s");
  if (e_panneau.l.outPoint > md_cale(16.9)) e_panneau.l.outPoint = md_cale(16.9);
  if (e_logo.l.inPoint < md_cale(17.4)) e_logo.l.inPoint = md_cale(17.4);
  if (e_mention.l.inPoint < md_cale(17.4)) e_mention.l.inPoint = md_cale(17.4);
})();

// ═══ 6. Lumières (elles copient l’élément animé, d’où leur place à la fin) ═══
// produit : balayage-lumiere, linéaire T 0.5 s, vers la gauche, bande 31 % de l’objet (une seule fois)
(function () { var cible = e_produit, b = md_bornes(cible), bw = b.width * 0.31, bh = Math.sqrt(b.width * b.width + b.height * b.height) * 1.2;
  var vert = false, L = vert ? bh : bw, Hh = vert ? bw : bh;
  var band = md_el(md_forme("produit \u2014 filet de lumi\u00e8re", L, Hh, 0, "#FFFFFF"), 0, 0, L, Hh); band.l.parent = cible.l; band.l.moveBefore(cible.l);
  band.x.setValue(b.left + b.width / 2); band.y.setValue(b.top + b.height / 2); band.r.setValue(20); band.o.setValue(45); band.l.blendingMode = BlendingMode.ADD; md_flou(band, false).setValue(md_sigma(bw * 0.1));
  md_anime(band.x, 4.1, b.left + b.width + bw, 4.6, b.left - bw, null); md_presence(band, 4.1, 4.667);
  var copie = cible.l.duplicate(); copie.name = "produit \u2014 cache du filet"; md_cache(band.l, copie); md_repere(band.l, 4.1, "balayage-lumiere"); })();

// ═══ 7. Caméra ═══

try { app.endUndoGroup(); } catch (e3) {}
return NOM + " : " + comp.numLayers + " calques, " + MD_CLES + " cl\u00e9s" + (MD_REPLIS.length ? " ; replis : " + MD_REPLIS.join(" | ") : " ; aucun repli");
})();
