#!/usr/bin/env node
/*
 * build_deck.js : rend un deck.json en présentation 16:9 (.pptx) et, en option, en aperçu HTML.
 *
 *   node build_deck.js deck.json sortie.pptx [--preview sortie.html] [--polices auto|repli]
 *
 * Polices : le .pptx écrit toujours celles du thème (nom exact), même absentes de cette machine ;
 * l'aperçu prend alors la police de repli, et la console le signale. --polices repli écrit le repli.
 * Le .pptx s'ouvre dans PowerPoint et dans Keynote, et s'importe dans Canva. Chaque slide entre
 * par un fondu, et les éléments décrits par slide.build apparaissent en fondu, au clic.
 * L'aperçu HTML reprend la même mise en page (mêmes coordonnées, mêmes tailles), sans les
 * animations. Ajoutez #qa à son adresse pour entourer en rouge les textes qui débordent.
 *
 * Variantes de composition : slide.variante (nom exact des fiches design, par exemple « centre-entier »
 * pour A13, « nom-au-centre » pour A14) pose le contenu visuel, la profondeur (ombre de contact sur
 * fond clair, halo doux, objet qui sort du cadre) et, quand une image manque, le repli dessiné de la
 * fiche, sans nombre ni marque. FIN, COLORIS et FRISE se posent sur n'importe quel archétype. Sans
 * variante, chaque archétype garde son rendu d'origine. Liste : section « VARIANTES DE COMPOSITION ».
 *
 * Tous les réglages visuels (corps, graisses, suivis, interlignes, positions, couleurs, durées) sont
 * dans STYLE, plus bas : ce sont les mesures de ../references/style-visuel.md.
 * Format de deck.json : voir ../references/deck-spec.md.
 */
'use strict';

const fs = require('fs');
const path = require('path');
const zlib = require('zlib');

let PptxGenJS;
try {
  PptxGenJS = require('pptxgenjs');
} catch (e) {
  console.error('pptxgenjs est introuvable. Lancez « npm install » dans ' + __dirname + ' puis relancez.');
  process.exit(2);
}
function loadJSZip() {
  try {
    return require(require.resolve('jszip', { paths: [path.dirname(require.resolve('pptxgenjs')), __dirname] }));
  } catch (e) {
    return null;
  }
}

// ===========================================================================
// STYLE : tous les réglages visuels du moteur, tirés de ../references/style-visuel.md (mesures
// relevées sur les keynotes du corpus, converties pour le canevas de 10 × 5,625 in).
// - Positions en pouces. « cy » est le centre visé de la zone des capitales d'un bloc : la boîte
//   est posée par son centre, en alignement vertical « milieu » (style-visuel §0).
// - Corps en points, donnés pour une police dont la capitale fait 0,728 em (Inter) : le moteur les
//   ajuste à la capitale de la police écrite, pour garder la même hauteur de capitale.
// - [corps maximal, plancher] : le moteur réduit jusqu'à ce que le texte tienne, sans descendre
//   sous le plancher ; au-delà, il le signale : il faut couper des mots, pas réduire encore.
// ===========================================================================
const STYLE = {
  // Par police : capitale par em (§0), suivi en em pour [≥ 50 pt, 28 à 50 pt, < 28 pt] (§2.2), et
  // facteur de l'estimation de largeur (étalonnée sur Arial, prudente pour les autres polices).
  polices: {
    'inter tight': { cap: 0.728, suivi: [-0.02, -0.02, 0], largeur: 0.96 },
    inter: { cap: 0.728, suivi: [-0.035, -0.035, -0.02], largeur: 1 },
    'helvetica neue': { cap: 0.714, suivi: [-0.045, -0.03, -0.01], largeur: 0.97 },
    helvetica: { cap: 0.717, suivi: [-0.045, -0.03, -0.01], largeur: 0.97 },
    arial: { cap: 0.716, suivi: [-0.06, -0.045, -0.015], largeur: 0.93 },
    defaut: { cap: 0.72, suivi: [-0.03, -0.025, -0.01], largeur: 1 }
  },
  capReference: 0.728,
  suivi: { max: -0.07, sansSerrageSous: 14 },       // jamais au-delà de −0,07 em, aucun serrage sous 14 pt
  // Interligne en multiple de la cap (§2.3) : interligne (pt) = k × cap par em × corps. Les listes
  // gardent l'interligne des titres et posent le reste du pas en espace après le paragraphe.
  interligne: { titre: 1.6, citation: 1.5, sommaire: 1.4, objet: 1.5, liste: 1.95, liste2: 3.1, courte: 1.8, texte: 1.6 },
  // Graisse (§2.1) : demi-gras (face « SemiBold » installée, sinon le gras de la famille) pour les
  // titres, noms, chiffres, listes, citations et prix ; regular pour le gris et les mentions.
  graisse: { texte: 'regular' },
  // Mélanges de couleur (§2.4) : texte secondaire à 53 % du texte vers le fond ; l'autre barre d'un
  // graphique, gris à 45 % ; tuiles de bento sur fond sombre, texte mélangé à 12 %.
  couleur: { secondaire: 0.53, autre: 0.55, tuileSombre: 0.12 },
  // Surtitre : corps = 0,42 × le titre, entre 16 et 28 pt ; ligne de base à 0,45 cap au-dessus du
  // haut des capitales du titre. En accent et demi-gras si l'accent de la slide est libre, sinon gris.
  surtitre: { rapport: 0.42, min: 16, max: 28, ecart: 0.45 },
  A1: { corps: [100, 64], uneLigne: 6.4, large: [64, 56], deuxLignes: [72, 60], x: 0.6, w: 8.8, cy: 2.81 },
  // Slide finale (un mot) : plus gros, centré à 47,5 % H ; en pleine page d'accent, la seule du deck,
  // si son texte (fond_sombre ou blanc) s'y lit à 4,5:1 et si theme.finale_accent ne vaut pas false.
  finale: { corps: [120, 64], cy: 2.67, pleinePageAccent: true, contraste: 4.5 },
  A2: { icone: 1.9, nom: [56, 32], ecart: 0.42, cy: 2.81 },
  A3: { corps: { 1: 80, 2: 80, 3: 80, 4: 68, 5: 56, 6: 44, 7: 40, 8: 36 }, plancher: 28, x: 1.0, w: 8.0, cy: 2.75 },
  A4: { corps: [50, 44], x: 1.2, w: 7.6, cy: 2.73 },
  A5: { chiffre: [144, 110], largeur: 8.0, cy: 2.81, cyDeuxLignes: 2.56, libelle: [24, 18], libelleCy: 4.5, libelleHautDeuxLignes: 3.54, libelleX: 0.8, libelleW: 8.4, surtitre: 24, surtitreEcart: 0.25 },
  A6: { titre: [28, 22], titreHaut: 0.5, titreHautSurtitre: 0.8, zone: { x: 1.5, y: 1.9, w: 7.0, h: 2.4 }, barre: 0.06, etiquette: [23, 14], axe: 16 },
  A7: { lignes: [36, 28], x: 1.0, w: 8.0, cy: 2.64, titre: 24 },
  A8: { lignes: [34, 24], picto: 1.12, ecart: 0.75, largeurMax: 7.4, cy: 2.64, titre: 24 },
  A9: { objet: 5.6, colonne: { x: 6.3, w: 3.4 }, titre: [34, 26], lignes: 24, ecartLignes: 0.28, cy: 2.81 },
  A10: { capture: 0.85, appareil: 5.2, rayon: 0.12 },
  A13: { h: 4.6, w: 8.0 },
  A14: { marge: 0.09, gouttiere: 0.085, rayon: 0.2, centre: { w: 3.9, h: 2.25 }, nom: [60, 36], titre: [24, 15], libelle: 12, chiffre: [48, 28], pad: 0.17 },
  A15: { libelle: [11, 8] },
  A16: { titre: 24, logoH: 0.56, rangee: 1.1, largeur: 8.0, nom: [20, 14] },
  A17: { citation: [36, 28], x: 0.92, w: 7.6, auteur: [26, 18], ecart: 0.53, cy: 2.81 },
  A18: { titre: [42, 28], note: [11, 9] },
  A19: { nom: [40, 28], petit: 16, prix: [36, 28], ecartNomHaut: 0.48, ecartNomColonne: 0.25, ecartPetit: 0.16, ecartOffres: 0.79, nomHaut: 0.72, objetHaut: { y: 2.7, bas: 4.9, w: 6.0 }, colonne: { cx: 7.0, w: 4.2 }, objetColonne: { cx: 2.5, w: 2.8, y: 0.26, h: 5.1 }, deuxColonnes: [2.75, 7.25], heros: [144, 110], periode: 18, cy: 2.81,
    // Deux offres sans visuel (convention) : la pile garde ses rapports mais grandit pour tenir la place.
    sansVisuel: { nom: [56, 36], petit: 20, prix: [52, 32], ecartPetit: 0.24 } },
  A20: { libelle: 16, libelleHaut: 0.45, mot: [40, 30], ecart: 0.19, visuel: { y: 1.6, bas: 5.0, w: 9.2 }, seul: { libelle: 24, ecart: 0.47 } },
  A21: { corps: 16, x: 0.54, bases: [4.75, 5.08] },
  AF: { titre: [50, 36] },
  SOURCES: { titre: [20, 14], liste: [13, 8] },
  source: [11, 9],
  // [À FOURNIR] : un emplacement, pas du contenu. Son libellé est estompé à toutes les tailles :
  // couleur du texte qu'il remplace (jamais l'accent : voir markerInk), à « texte » d'opacité (alpha
  // du run dans le .pptx), jamais en dégradé ; souligné en pointillé d'accent, discret (« opacite »). Le soulignement d'une police
  // grossit avec le corps (Arial : 0,07 em, soit 10 pt de points sous un chiffre de 144 pt) : au-dessus
  // de « seuil » pt, le moteur le remplace par un filet pointillé d'épaisseur fixe, posé sous la ligne
  // de base (« ecart » em, borné en points), le même dans le .pptx et l'aperçu, chacun placé pour sa police.
  // « chasse » : [demi-gras ou gras, regular], rapport réel / estimé de la largeur du marqueur, mesuré dans
  // l'aperçu avec le facteur de la police affichée.
  marqueur: { texte: 0.4, trait: 'dotted', opacite: 0.7, seuil: 26, epaisseur: 1.5, ecart: 0.085, ecartPt: [3, 12], chasse: [0.99, 0.99] },
  // Interface schématique d'une image qui manque (§5.2) : carte sans trait, barres grises à bouts
  // ronds, longueurs 100 / 72 / 48 %, une tous les 0,16 in, une seule ligne en accent.
  // Carte claire sur fond sombre, grise à 5 % sur fond blanc ; accent en pastille sous 1,8:1.
  schema: { rayon: 0.12, barre: 0.08, pas: 0.16, longueurs: [1, 0.72, 0.48], carteGrise: 0.05, barres: [0.22, 0.38], contrasteBarre: 1.8, ombre: { flou: 0.3, decalage: 0.08, opacite: 0.12 }, appareil: { coin: 0.13, bord: 0.03 } },
  // Équilibrage des lignes : pénalité d'une ligne qui finit sur un mot-outil, en part du carré de
  // la longueur moyenne (0,25 : une ligne une fois et demie plus longue que l'autre reste préférée).
  coupure: { motOutil: 0.25 },
  transition: { vitesse: 'fast' },                // fondu de 0,5 s entre les slides
  apparition: { duree_ms: 400, suite_ms: 600 }    // fondu d'entrée ; délai d'une apparition « qui suit »
};

// ---------------------------------------------------------------------------
// Constantes de mise en page (pouces). LAYOUT_16x9 = 10 x 5,625.
// ---------------------------------------------------------------------------
const W = 10;
const H = 5.625;
const M = 0.6;
const FOURNIR_SRC = '\\[(?:À|A) FOURNIR[^\\]]*\\]|\\[TO PROVIDE[^\\]]*\\]';
const VALIDER_SRC = '\\[(?:(?:À|A) VALIDER|TO VALIDATE|TO CONFIRM)[^\\]]*\\]';
// Début de marqueur, fermé ou non : ce qui en reste après le retrait des marqueurs fermés est un oubli de « ] ».
const OUVERT_SRC = '\\[(?:(?:À|A) (?:VALIDER|FOURNIR)|TO (?:VALIDATE|PROVIDE|CONFIRM))';
const DATA_DIR = path.join(__dirname, '..', 'references', 'data');

// Archétypes dont l'image (slide.image) est le contenu, pas le fond.
const CONTENT_IMAGE = new Set(['A2', 'A9', 'A10', 'A11', 'A13', 'A19', 'A20']);
// Archétypes plein cadre : l'image couvre toute la slide.
const FULL_BLEED = new Set(['A12', 'A18', 'A21', 'A22', 'A23', 'A24', 'A25']);

const LABELS = {
  fr: {
    build: 'APPARITIONS', timing: 'MINUTAGE', source: 'SOURCE', relay: 'relais', sep: ' : ',
    toValidate: 'À VALIDER', toProvide: 'À FOURNIR', role: 'fonction',
    sourceShown: 'affichée sur la slide', sourceFinal: 'reportée au carton final', sourceHidden: 'non affichée',
    sourcesTitle: 'Sources et mentions', missingFile: 'introuvable', slideWord: 'slide',
    noNotes: '[À FOURNIR : script de cette slide]', markerDefault: 'à fournir', content: 'contenu',
    finalNotes: 'Carton final : sources et mentions. Il reste à l\'écran pendant les remerciements ; on ne le commente pas.',
    sourceRef: (n) => 'Source ' + n + ' · en fin de présentation', sourceRenvoi: 'renvoi n°',
    image: 'Image', q: (s) => '« ' + s + ' »',
    cap: { interface: 'Capture à fournir', appareil: 'Capture à fournir', objet: 'Visuel à fournir', photo: 'Photo à fournir', carte: 'Carte à fournir', icone: 'Icône à fournir', logo: 'Logo à fournir', tuile: 'Image à fournir', fragment: 'Composant à fournir' },
    kind: { interface: 'capture', appareil: 'capture', objet: 'visuel', photo: 'photo', carte: 'carte', icone: 'icône', logo: 'logo', tuile: 'image', fragment: 'composant' },
    parts: { surtitre: 'surtitre', titre: 'titre', lignes: 'ligne', chiffre: 'chiffre', libelle: 'libellé', visuel: 'visuel', barres: 'barre', tuiles: 'tuile', centre: 'tuile centrale', prix: 'prix', nom: 'nom', date: 'date', citation: 'citation', auteur: 'auteur', logos: 'logo', note: 'note', fonction: 'fonction', coches: 'coches' }
  },
  en: {
    build: 'BUILD', timing: 'TIMING', source: 'SOURCE', relay: 'handover', sep: ': ',
    toValidate: 'TO VALIDATE', toProvide: 'TO PROVIDE', role: 'role',
    sourceShown: 'shown on the slide', sourceFinal: 'moved to the final card', sourceHidden: 'not shown',
    sourcesTitle: 'Sources and notes', missingFile: 'not found', slideWord: 'slide',
    noNotes: '[TO PROVIDE: script for this slide]', markerDefault: 'to provide', content: 'content',
    finalNotes: 'Final card: sources and legal notes. Leave it on screen during the thanks; do not comment on it.',
    sourceRef: (n) => 'Source ' + n + ' · see the final slide', sourceRenvoi: 'note no. ',
    image: 'Image', q: (s) => '“' + s + '”',
    cap: { interface: 'Screenshot to provide', appareil: 'Screenshot to provide', objet: 'Visual to provide', photo: 'Photo to provide', carte: 'Map to provide', icone: 'Icon to provide', logo: 'Logo to provide', tuile: 'Image to provide', fragment: 'Component to provide' },
    kind: { interface: 'screenshot', appareil: 'screenshot', objet: 'visual', photo: 'photo', carte: 'map', icone: 'icon', logo: 'logo', tuile: 'image', fragment: 'component' },
    parts: { surtitre: 'kicker', titre: 'title', lignes: 'line', chiffre: 'figure', libelle: 'label', visuel: 'visual', barres: 'bar', tuiles: 'tile', centre: 'centre tile', prix: 'price', nom: 'name', date: 'date', citation: 'quote', auteur: 'author', logos: 'logo', note: 'note', fonction: 'role', coches: 'checks' }
  }
};

// ---------------------------------------------------------------------------
// Petits utilitaires
// ---------------------------------------------------------------------------
function readJSON(file, fallback) {
  try {
    return JSON.parse(fs.readFileSync(file, 'utf8'));
  } catch (e) {
    return fallback;
  }
}
function arr(v) {
  if (v === undefined || v === null) return [];
  return Array.isArray(v) ? v : [v];
}
function str(v) {
  return v === undefined || v === null ? '' : String(v);
}
function round2(n) {
  return Math.round(n * 1000) / 1000;
}
function clamp(v, a, b) {
  return Math.max(a, Math.min(b, v));
}
function escHtml(s) {
  return String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
}
function escXml(s) {
  return String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
}
// Nom de police écrit tel quel par pptxgenjs dans un attribut XML (typeface="…") : échappé ici, sinon
// un nom comme « Grotesk & Co » rend le .pptx illisible.
function xmlFace(s) {
  return escXml(String(s).replace(/[\x00-\x08\x0B\x0C\x0E-\x1F]/g, ''));
}
function unescXml(s) {
  return String(s).replace(/&quot;/g, '"').replace(/&apos;/g, '\'').replace(/&lt;/g, '<').replace(/&gt;/g, '>').replace(/&amp;/g, '&');
}
function normKey(s) {
  return String(s || '')
    .normalize('NFD').replace(/[\u0300-\u036f]/g, '')
    .toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-+|-+$/g, '');
}
function fmtTime(sec) {
  sec = Math.max(0, Math.round(sec));
  const m = Math.floor(sec / 60);
  const s = sec % 60;
  return m + ':' + String(s).padStart(2, '0');
}
function uniq(list) {
  const out = [];
  list.forEach((x) => { if (x && !out.includes(x)) out.push(x); });
  return out;
}
function rng(seed) {
  let s = Math.abs(Math.floor(seed)) % 233280 || 7;
  return () => {
    s = (s * 9301 + 49297) % 233280;
    return s / 233280;
  };
}

// Couleurs ------------------------------------------------------------------
function hex(c, fallback, label, warnings) {
  if (c === undefined || c === null || c === '') return fallback;
  const s = String(c).trim().replace(/^#/, '');
  if (/^[0-9a-f]{3}$/i.test(s)) return s.split('').map((ch) => ch + ch).join('').toUpperCase();
  if (/^[0-9a-f]{6}$/i.test(s)) return s.toUpperCase();
  if (warnings) warnings.push('Couleur « ' + label + ' » illisible (' + c + ') : valeur par défaut utilisée.');
  return fallback;
}
function rgbOf(h) {
  return [parseInt(h.slice(0, 2), 16), parseInt(h.slice(2, 4), 16), parseInt(h.slice(4, 6), 16)];
}
function mix(a, b, t) {
  const A = rgbOf(a);
  const B = rgbOf(b);
  return A.map((v, i) => Math.round(v + (B[i] - v) * t).toString(16).padStart(2, '0')).join('').toUpperCase();
}
function lum(h) {
  return rgbOf(h).map((v) => {
    v /= 255;
    return v <= 0.03928 ? v / 12.92 : Math.pow((v + 0.055) / 1.055, 2.4);
  }).reduce((acc, v, i) => acc + v * [0.2126, 0.7152, 0.0722][i], 0);
}
function contrast(a, b) {
  const la = lum(a);
  const lb = lum(b);
  return (Math.max(la, lb) + 0.05) / (Math.min(la, lb) + 0.05);
}
function readableOn(bg, a, b) {
  return contrast(bg, a) >= contrast(bg, b) ? a : b;
}
// Texte posé sur la couleur d'accent : blanc si le contraste suffit pour un grand texte gras (3:1),
// sinon le fond sombre du thème (ou un quasi-noir).
function onAccent(bg, dark) {
  if (contrast(bg, 'FFFFFF') >= 3) return 'FFFFFF';
  return dark && contrast(bg, dark) >= 3 ? dark : readableOn(bg, 'FFFFFF', '111111');
}
// Accent utilisé pour du texte : l'accent lui-même s'il se lit sur le fond, sinon l'accent
// rapproché de la couleur du texte juste assez pour se lire (3:1).
function textAccent(bg, accent, fg) {
  if (contrast(bg, accent) >= 2.6) return accent;
  for (let t = 0.1; t <= 1.0001; t += 0.1) {
    const c = mix(accent, fg, t);
    if (contrast(bg, c) >= 3) return c;
  }
  return fg;
}
// Encre d'un [À FOURNIR] : la couleur du texte qu'il remplace, sauf l'accent. Un accent à 40 %
// d'opacité vire au brun sur un fond sombre et se lit comme une vraie valeur mal imprimée : le
// marqueur prend alors la couleur du texte (gris estompé), et seul son pointillé reste d'accent.
function markerInk(c, color) {
  if (!color || c.P.fond === 'accent') return color;
  const acc = [c.T.accent, c.T.accent2, c.P.accent, c.P.accent2, c.P.accentTxt, c.P.accent2Txt].filter(Boolean).map((h) => String(h).toUpperCase());
  return acc.includes(String(color).toUpperCase()) ? c.P.fg : color;
}

// ---------------------------------------------------------------------------
// Typographie et mesure du texte (estimation prudente, commune au .pptx et à l'aperçu)
// ---------------------------------------------------------------------------
const NBSP = ' ';
function typo(s, lang) {
  s = str(s);
  // Pas de coupure entre un nombre et son unité, ni dans un nombre à milliers.
  s = s.replace(/(\d) (?=\d{3}(?!\d))/g, '$1' + NBSP);
  s = s.replace(/(\d) (?=(?:%|€|\$|£|×|x\b|°|h\b|min\b|s\b|j\b|km\b|kg\b|m\b|Go\b|To\b|GB\b|TB\b|HT\b|TTC\b|fois\b|jours?\b|mois\b|ans?\b|heures?\b|minutes?\b|secondes?\b|semaines?\b|sites?\b|clients?\b|times\b|hours?\b|days?\b|years?\b))/g, '$1' + NBSP);
  s = s.replace(/([€$£]) (?=(?:HT|TTC)\b)/g, '$1' + NBSP);
  if (lang === 'fr') {
    s = s.replace(/ ([:;!?»])/g, NBSP + '$1').replace(/« /g, '«' + NBSP);
  }
  return s;
}
function charW(ch) {
  if (ch === ' ' || ch === NBSP) return 0.28;
  if (/[0-9]/.test(ch)) return 0.58;
  if (/[.,;:'’!|ijlI1]/.test(ch)) return 0.28;
  if (/[frt]/.test(ch)) return 0.37;
  if (/[mwMW@]/.test(ch)) return 0.86;
  if (/[«»"“”()[\]\-–—/]/.test(ch)) return 0.4;
  if (/[€$£%&#×]/.test(ch)) return 0.66;
  if (ch !== ch.toLowerCase()) return 0.7;
  return 0.55;
}
// Police de chaque rôle (titre, texte) : clé de STYLE.polices, fixée par main() d'après la police
// écrite dans le .pptx (capitale, suivi) ; « mesure » liste aussi celle de l'aperçu quand la police
// manque ici (le repli) : la largeur estimée prend la plus large des deux.
// « ici » : la clé de la police que l'aperçu affiche (le repli quand la police du thème manque).
const FONT = { titre: { cle: 'defaut', mesure: ['defaut'], ici: 'defaut' }, texte: { cle: 'defaut', mesure: ['defaut'], ici: 'defaut' } };
function pol(role) {
  const f = FONT[role] || FONT.texte;
  return STYLE.polices[f.cle] || STYLE.polices.defaut;
}
function widthFactor(role) {
  const f = FONT[role] || FONT.texte;
  return Math.max.apply(null, (f.mesure || [f.cle]).map((k) => (STYLE.polices[k] || STYLE.polices.defaut).largeur));
}
// wf : facteur de largeur imposé (celui d'une seule police) ; par défaut, le plus large des polices du rôle.
function textWidth(s, pt, heavy, track, role, wf) {
  let u = 0;
  let n = 0;
  for (const ch of s) {
    u += charW(ch);
    n += 1;
  }
  return (u * (heavy ? 1.07 : 1) * 1.04 * (wf || widthFactor(role)) + n * (track || 0)) * pt / 72;
}
function wrapInfo(s, pt, heavy, w, track, role) {
  const words = s.split(/ +/).filter((x) => x.length);
  if (!words.length) return { lines: 1, maxWord: 0, widest: 0 };
  const sp = textWidth(' ', pt, heavy, track, role);
  let lines = 1;
  let cur = 0;
  let maxWord = 0;
  let widest = 0;
  for (const wd of words) {
    const ww = textWidth(wd, pt, heavy, track, role);
    if (ww > maxWord) maxWord = ww;
    if (cur === 0) cur = ww;
    else if (cur + sp + ww <= w) cur += sp + ww;
    else {
      widest = Math.max(widest, cur);
      lines += 1;
      cur = ww;
    }
  }
  return { lines, maxWord, widest: Math.max(widest, cur) };
}
// Marqueurs ------------------------------------------------------------------
// [À VALIDER : texte] : une proposition, affichée comme du vrai contenu (marqueur retiré).
// [À FOURNIR : libellé] : ce qui manque ; à l'écran, le libellé seul, estompé, souligné en pointillé
// (entre crochets pour Canva, qui perd l'estompé à l'import : voir parseInline).
// Un marqueur peut contenir un \n : on le lit sur tout le texte, avant la coupure en lignes (para).
function markerInner(m) {
  const s = String(m).slice(1, -1);
  const i = s.indexOf(':');
  return i < 0 ? '' : s.slice(i + 1).replace(/^[\s\u00A0]+|[\s\u00A0]+$/g, '');
}
function hasFournir(s) {
  return new RegExp(FOURNIR_SRC, 'i').test(str(s));
}
function fournirLabels(s) {
  return (str(s).match(new RegExp(FOURNIR_SRC, 'gi')) || []).map((m) => markerInner(m));
}
function stripValider(s, found) {
  return str(s).replace(new RegExp(VALIDER_SRC, 'gi'), (m) => {
    const inner = markerInner(m);
    // Une proposition sur deux lignes est listée sur une seule.
    const key = inner.replace(/\s*\n\s*/g, ' ');
    if (found && key && !found.includes(key)) found.push(key);
    return inner;
  });
}
// Texte riche : *accent* et marqueurs [À FOURNIR …]. crochets : le libellé garde des crochets
// visibles (« [date] »), pour un format qui perd l'estompé (Canva).
function parseInline(text, lang, crochets) {
  const out = [];
  const re = new RegExp('(' + FOURNIR_SRC + ')|\\*([^*]+)\\*', 'gi');
  let last = 0;
  let m;
  while ((m = re.exec(text))) {
    if (m.index > last) out.push({ t: text.slice(last, m.index) });
    if (m[1]) {
      const label = markerInner(m[1]) || (LABELS[lang] || LABELS.fr).markerDefault;
      out.push({ t: crochets ? '[' + label + ']' : label, marker: true });
    }
    // Un [À FOURNIR] écrit dans un *accent* reste un marqueur (estompé, dans la couleur du texte),
    // jamais un texte en clair en accent plein.
    else if (hasFournir(m[2])) parseInline(m[2], lang, crochets).forEach((r) => { if (r.t) out.push(Object.assign(r, { accent: true })); });
    else out.push({ t: m[2], accent: true });
    last = re.lastIndex;
  }
  if (last < text.length) out.push({ t: text.slice(last) });
  if (!out.length) out.push({ t: '' });
  return out;
}
// Point final (ou ! ?) d'un titre en couleur d'accent.
function accentPoint(runs) {
  const last = runs[runs.length - 1];
  if (!last || last.marker || last.accent) return runs;
  const m = /([^.!?…])([.!?])$/.exec(last.t) || (/^[.!?]$/.test(last.t) ? [last.t, '', last.t] : null);
  if (!m || /\.\.$|…$/.test(last.t)) return runs;
  const head = last.t.slice(0, -1);
  const out = runs.slice(0, -1);
  if (head) out.push(Object.assign({}, last, { t: head }));
  out.push({ t: last.t.slice(-1), accent: true, point: true });
  return out;
}
function shortLabel(s, maxWords) {
  let t = str(s).replace(/\([^)]*\)/g, ' ').replace(/\s+/g, ' ').trim();
  t = t.split(/[;,.!?](?:\s|$)/)[0].trim();
  const words = t.split(' ').filter(Boolean);
  if (words.length > (maxWords || 7)) t = words.slice(0, maxWords || 7).join(' ') + '…';
  return t;
}

// ---------------------------------------------------------------------------
// Images : dimensions lues dans l'en-tête (PNG, JPEG, GIF), sans dépendance
// ---------------------------------------------------------------------------
// Partie opaque d'un PNG détouré (RGBA ou gris + alpha, 8 bits, non entrelacé), en fraction de
// l'image : un produit livré avec des marges transparentes se cale, s'ombre et se coupe sur son
// contour réel, pas sur le cadre du fichier. null si l'image est opaque ou illisible.
const CONTENT_CACHE = new Map();
function pngContent(file, buf) {
  if (CONTENT_CACHE.has(file)) return CONTENT_CACHE.get(file);
  let box = null;
  try {
    box = pngAlphaBox(buf);
  } catch (e) {
    box = null;
  }
  if (box && box.w > 0.985 && box.h > 0.985) box = null;
  CONTENT_CACHE.set(file, box);
  return box;
}
function pngAlphaBox(buf) {
  let o = 8;
  let w = 0;
  let h = 0;
  let depth = 0;
  let ct = 0;
  let lace = 0;
  const idat = [];
  while (o + 8 <= buf.length) {
    const len = buf.readUInt32BE(o);
    const type = buf.toString('ascii', o + 4, o + 8);
    const d = buf.slice(o + 8, o + 8 + len);
    if (type === 'IHDR') {
      w = d.readUInt32BE(0);
      h = d.readUInt32BE(4);
      depth = d[8];
      ct = d[9];
      lace = d[12];
    } else if (type === 'IDAT') idat.push(d);
    else if (type === 'IEND') break;
    o += 12 + len;
  }
  if (depth !== 8 || lace || (ct !== 6 && ct !== 4) || !w || !h || w * h > 40e6) return null;
  const bpp = ct === 6 ? 4 : 2;
  const stride = w * bpp;
  const raw = zlib.inflateSync(Buffer.concat(idat));
  if (raw.length < (stride + 1) * h) return null;
  let prev = Buffer.alloc(stride);
  let cur = Buffer.alloc(stride);
  let x0 = w;
  let y0 = h;
  let x1 = -1;
  let y1 = -1;
  for (let y = 0; y < h; y++) {
    const f = raw[y * (stride + 1)];
    const at = y * (stride + 1) + 1;
    for (let i = 0; i < stride; i++) {
      const a = i >= bpp ? cur[i - bpp] : 0;
      const b = prev[i];
      const cc = i >= bpp ? prev[i - bpp] : 0;
      let v = raw[at + i];
      if (f === 1) v += a;
      else if (f === 2) v += b;
      else if (f === 3) v += (a + b) >> 1;
      else if (f === 4) {
        const pp = a + b - cc;
        const pa = Math.abs(pp - a);
        const pb = Math.abs(pp - b);
        const pc = Math.abs(pp - cc);
        v += pa <= pb && pa <= pc ? a : pb <= pc ? b : cc;
      }
      cur[i] = v & 255;
    }
    for (let x = 0; x < w; x++) {
      if (cur[x * bpp + bpp - 1] > 12) {
        if (x < x0) x0 = x;
        if (x > x1) x1 = x;
        if (y < y0) y0 = y;
        y1 = y;
      }
    }
    const t = prev;
    prev = cur;
    cur = t;
  }
  if (x1 < 0) return null;
  return { x: x0 / w, y: y0 / h, w: (x1 - x0 + 1) / w, h: (y1 - y0 + 1) / h };
}
function imageInfo(file) {
  let buf;
  try {
    buf = fs.readFileSync(file);
  } catch (e) {
    return null;
  }
  if (buf.length > 24 && buf.readUInt32BE(0) === 0x89504e47) {
    return { type: 'png', mime: 'image/png', w: buf.readUInt32BE(16), h: buf.readUInt32BE(20), buf, content: pngContent(file, buf) };
  }
  if (buf.length > 4 && buf[0] === 0xff && buf[1] === 0xd8) {
    let o = 2;
    while (o + 9 < buf.length) {
      if (buf[o] !== 0xff) {
        o += 1;
        continue;
      }
      const mk = buf[o + 1];
      if (mk === 0xff) {
        o += 1;
        continue;
      }
      if (mk === 0xd8 || mk === 0x01 || (mk >= 0xd0 && mk <= 0xd7)) {
        o += 2;
        continue;
      }
      if (mk >= 0xc0 && mk <= 0xcf && mk !== 0xc4 && mk !== 0xc8 && mk !== 0xcc) {
        return { type: 'jpeg', mime: 'image/jpeg', h: buf.readUInt16BE(o + 5), w: buf.readUInt16BE(o + 7), buf };
      }
      o += 2 + buf.readUInt16BE(o + 2);
    }
    return null;
  }
  if (buf.length > 10 && buf.slice(0, 3).toString('ascii') === 'GIF') {
    return { type: 'gif', mime: 'image/gif', w: buf.readUInt16LE(6), h: buf.readUInt16LE(8), buf };
  }
  return null;
}

// ---------------------------------------------------------------------------
// Polices : celles du thème dans le .pptx ; installées ici ou non, pour l'aperçu et la mesure
// ---------------------------------------------------------------------------
let fontFileIndex = null;
function installedFontNames() {
  if (fontFileIndex) return fontFileIndex;
  const home = process.env.HOME || process.env.USERPROFILE || '';
  const dirs = [
    path.join(home, 'Library', 'Fonts'), '/Library/Fonts', '/System/Library/Fonts', '/System/Library/Fonts/Supplemental',
    'C:\\Windows\\Fonts', path.join(process.env.LOCALAPPDATA || '', 'Microsoft', 'Windows', 'Fonts'),
    '/usr/share/fonts', '/usr/local/share/fonts', path.join(home, '.fonts'), path.join(home, '.local', 'share', 'fonts')
  ];
  const names = [];
  const walk = (d, depth) => {
    let list;
    try {
      list = fs.readdirSync(d, { withFileTypes: true });
    } catch (e) {
      return;
    }
    for (const ent of list) {
      if (ent.isDirectory()) {
        if (depth < 3) walk(path.join(d, ent.name), depth + 1);
      } else if (/\.(ttf|otf|ttc|dfont|woff2?)$/i.test(ent.name)) {
        names.push(ent.name.toLowerCase().replace(/[^a-z0-9]/g, ''));
      }
    }
  };
  dirs.forEach((d) => walk(d, 0));
  fontFileIndex = names;
  return names;
}
function fontInstalled(name) {
  const key = String(name).toLowerCase().replace(/[^a-z0-9]/g, '');
  if (!key) return false;
  return installedFontNames().some((f) => f.startsWith(key));
}
function fontSpec(v, fallbackName) {
  if (!v) return { nom: fallbackName, repli: fallbackName };
  if (typeof v === 'string') return { nom: v, repli: fallbackName };
  return { nom: v.nom || v.name || fallbackName, repli: v.repli || v.fallback || fallbackName };
}

// Clé de mesure d'une police (STYLE.polices) : capitale, suivi et largeur.
function fontKey(name) {
  const k = String(name || '').toLowerCase().replace(/[^a-z0-9]+/g, ' ').trim();
  if (k.startsWith('inter tight')) return 'inter tight';
  if (k.startsWith('inter')) return 'inter';
  if (k.startsWith('helvetica neue')) return 'helvetica neue';
  if (k.startsWith('helvetica')) return 'helvetica';
  if (k.startsWith('arial')) return 'arial';
  return 'defaut';
}
// Face demi-grasse installée (style-visuel §2.1) : le nom de famille hérité de la face, tel que les
// fichiers statiques le déclarent (« Inter SemiBold », « Inter Tight SemiBold », « Inter 18pt
// SemiBold »). Sans elle, le demi-gras devient le gras de la famille.
function semiFace(name) {
  if (!name) return null;
  for (const cand of [name + ' SemiBold', name + ' 18pt SemiBold', name + ' DemiBold']) {
    if (fontInstalled(cand)) return cand;
  }
  return null;
}

// ---------------------------------------------------------------------------
// Thème
// ---------------------------------------------------------------------------
function resolveTheme(theme, mode, warnings, fontNotes) {
  theme = theme || {};
  const c = theme.couleurs || theme.colors || {};
  const T = {};
  T.nom = theme.nom || 'Theme';
  T.fondSombre = hex(c.fond_sombre, '111418', 'fond_sombre', warnings);
  T.fondClair = hex(c.fond_clair, 'FFFFFF', 'fond_clair', warnings);
  T.texte = hex(c.texte, '15181C', 'texte', warnings);
  T.accent = hex(c.accent, 'C2410C', 'accent', warnings);
  T.accent2 = hex(c.accent2, T.accent, 'accent2', warnings);
  // Dégradé du chiffre héros seulement si accent2 est donné et diffère de l'accent.
  T.gradient = !!c.accent2 && T.accent2 !== T.accent;
  const lightDefault = contrast(T.fondClair, T.fondSombre) >= 7 ? T.fondClair : 'FFFFFF';
  T.texteSombre = hex(c.texte_sur_sombre, lightDefault, 'texte_sur_sombre', warnings);
  // Texte secondaire : celui de l'utilisateur s'il se lit à 4,5:1, sinon 53 % du texte vers le fond.
  const secondary = (given, fg, bg, label) => {
    const auto = mix(fg, bg, STYLE.couleur.secondaire);
    const h = hex(given, null, label, warnings);
    if (!h) return auto;
    if (contrast(h, bg) >= 4.5) return h;
    warnings.push('Couleur « ' + label + ' » sous 4,5:1 sur son fond : gris calculé à la place (53 % du texte vers le fond).');
    return auto;
  };
  T.texteSec = secondary(c.texte_secondaire, T.texte, T.fondClair, 'texte_secondaire');
  T.texteSecSombre = secondary(c.texte_secondaire_sur_sombre, T.texteSombre, T.fondSombre, 'texte_secondaire_sur_sombre');
  T.pointAccent = theme.point_accent !== false;
  T.finaleAccent = theme.finale_accent !== false;

  const pols = theme.polices || theme.fonts || {};
  const ft = fontSpec(pols.titre || pols.title, 'Arial');
  const fx = fontSpec(pols.texte || pols.body || pols.titre, 'Arial');
  // Le .pptx écrit toujours la police demandée : il sera projeté sur la machine de l'utilisateur, pas
  // sur celle qui le construit. Seul --polices repli écrit le repli. Si la police manque ici, l'aperçu
  // s'affiche dans le repli, et la mesure des textes prend la plus large des deux polices.
  const absentes = [];
  const replis = [];
  const pick = (f) => {
    if (mode === 'repli') return { ecrite: f.repli, ici: f.repli };
    if (f.nom === f.repli || fontInstalled(f.nom)) return { ecrite: f.nom, ici: f.nom };
    if (!absentes.includes(f.nom)) absentes.push(f.nom);
    if (!replis.includes(f.repli)) replis.push(f.repli);
    return { ecrite: f.nom, ici: f.repli };
  };
  const pt = pick(ft);
  const px = pick(fx);
  if (absentes.length) {
    const q = (l) => l.map((n) => '« ' + n + ' »').join(' et ');
    const s = absentes.length > 1;
    fontNotes.push('Police' + (s ? 's ' : ' ') + q(absentes) + ' absente' + (s ? 's' : '') + ' de cette machine : le .pptx ' + (s ? 'les écrit' : 'l\'écrit') + ' quand même, l\'aperçu s\'affiche en '
      + q(replis) + ' ; installez-' + (s ? 'les' : 'la') + ' sur la machine qui présente.');
  }
  T.fontTitre = pt.ecrite;
  T.fontTexte = px.ecrite;
  T.semiTitre = semiFace(T.fontTitre);
  T.semiTexte = semiFace(T.fontTexte);
  T.cleTitre = fontKey(T.fontTitre);
  T.cleTexte = fontKey(T.fontTexte);
  T.mesureTitre = uniq([T.cleTitre, fontKey(pt.ici)]);
  T.mesureTexte = uniq([T.cleTexte, fontKey(px.ici)]);
  T.iciTitre = fontKey(pt.ici);
  T.iciTexte = fontKey(px.ici);
  T.cssTitre = cssFamily(T.fontTitre, ft);
  T.cssTexte = cssFamily(T.fontTexte, fx);
  T.logo = theme.logo || null;
  return T;
}
function cssFamily(written, f) {
  const q = (n) => '\'' + String(n).replace(/'/g, '') + '\'';
  return uniq([written, f.nom, f.repli, 'Arial']).map(q).concat(['sans-serif']).join(', ');
}
// Graisse d'un paragraphe → face écrite dans le .pptx, gras ou non, et graisse CSS de l'aperçu.
function faceOf(T, role, wt) {
  const fam = role === 'titre' ? T.fontTitre : T.fontTexte;
  const semi = role === 'titre' ? T.semiTitre : T.semiTexte;
  if (wt === 'semi') return semi ? { face: semi, bold: false, css: 600 } : { face: fam, bold: true, css: 700 };
  if (wt === 'bold') return { face: fam, bold: true, css: 700 };
  return { face: fam, bold: false, css: 400 };
}
function palette(T, fond) {
  const C = STYLE.couleur;
  let P;
  if (fond === 'clair') {
    const bg = T.fondClair;
    P = {
      fond: 'clair', bg, fg: T.texte, fg2: T.texteSec, accent: T.accent, accent2: T.accent2,
      // Tuiles : blanches sur un fond gris clair ; gris très clair si le fond est déjà blanc.
      surface: contrast(bg, 'FFFFFF') > 1.04 ? mix(bg, 'FFFFFF', 0.8) : mix(bg, T.texte, 0.05)
    };
  } else if (fond === 'accent') {
    // Pleine page en couleur d'accent (slide finale) : l'accent du texte devient la couleur du texte.
    const bg = T.accent;
    const fg = readableOn(bg, T.fondSombre, T.texteSombre);
    P = { fond: 'accent', bg, fg, fg2: mix(fg, bg, 0.35), accent: fg, accent2: fg, surface: mix(bg, fg, 0.1) };
  } else {
    const bg = T.fondSombre;
    P = {
      fond: fond === 'image' ? 'image' : 'sombre', bg, fg: T.texteSombre, fg2: T.texteSecSombre,
      accent: T.accent, accent2: T.accent2, surface: mix(bg, T.texteSombre, C.tuileSombre)
    };
  }
  P.other = mix(P.fg, P.bg, C.autre);
  P.line = mix(P.fg, P.bg, 0.6);
  P.accentTxt = textAccent(P.bg, P.accent, P.fg);
  P.accent2Txt = textAccent(P.bg, P.accent2, P.fg);
  return P;
}

// ---------------------------------------------------------------------------
// Table des publics (même fichier que check_deck.py)
// ---------------------------------------------------------------------------
function loadPublics() {
  return readJSON(path.join(DATA_DIR, 'publics-exigences.json'), { defaut: 'defaut', publics: {}, prudence: {} });
}
function matchPublic(label, pubs) {
  const k = normKey(label);
  if (!k) return null;
  if (pubs[k]) return k;
  let best = null;
  let bestLen = 0;
  for (const key of Object.keys(pubs)) {
    for (const syn of [key].concat(pubs[key].synonymes || [])) {
      const sk = normKey(syn);
      if (!sk) continue;
      if (sk === k) return key;
      if (('-' + k + '-').includes('-' + sk + '-') && sk.length > bestLen) {
        best = key;
        bestLen = sk.length;
      }
    }
  }
  return best;
}
// meta.public : texte, ou { type, description } ; type peut être une liste (public mixte) :
// chaque réglage prend alors la valeur la plus prudente (ordre « prudence » du fichier).
function resolvePublic(meta, table) {
  const raw = meta && meta.public;
  let labels = [];
  if (raw && typeof raw === 'object' && !Array.isArray(raw)) labels = arr(raw.type || raw.types || raw.description);
  else labels = arr(raw);
  const pubs = table.publics || {};
  const keys = [];
  labels.forEach((l) => {
    const k = matchPublic(l, pubs);
    if (k && !keys.includes(k)) keys.push(k);
  });
  const reconnu = keys.length > 0;
  if (!keys.length) keys.push(table.defaut && pubs[table.defaut] ? table.defaut : Object.keys(pubs)[0] || 'defaut');
  const out = Object.assign({}, pubs[keys[0]] || {});
  const order = table.prudence || {};
  keys.slice(1).forEach((k) => {
    const row = pubs[k] || {};
    Object.keys(order).forEach((field) => {
      const ranks = order[field];
      if (ranks.indexOf(row[field]) > ranks.indexOf(out[field])) out[field] = row[field];
    });
  });
  return Object.assign(out, { cle: keys.join('+'), reconnu });
}

// ---------------------------------------------------------------------------
// Composition d'une slide : liste d'éléments positionnés, rendus ensuite en .pptx et en HTML.
// Chaque élément (ou paragraphe) porte un groupe d'apparition « g » (titre, lignes…) et,
// pour les listes, un rang « sub » : c'est ce que les animations ciblent.
// ---------------------------------------------------------------------------
class SlideCtx {
  constructor(deck, slide, index, env) {
    this.deck = deck;
    this.slide = slide;
    this.index = index;
    this.env = env;
    this.T = env.T;
    this.lang = env.lang;
    this.L = LABELS[env.lang] || LABELS.fr;
    this.t = slide.textes || {};
    const arch = String(slide.archetype || '').toUpperCase();
    this.arch = arch;
    this.renderArch = arch;
    let fond = String(slide.fond || '').toLowerCase();
    if (!['sombre', 'clair', 'image', 'accent'].includes(fond)) fond = 'sombre';
    // Slide finale d'un mot (A1) : pleine page en couleur d'accent, la seule du deck, si le texte
    // s'y lit à 4,5:1 (style-visuel, « Slide finale ») et si le thème le permet (theme.finale_accent :
    // false pour une charte qui plafonne la surface d'accent ; la finale garde alors son fond).
    const vf = normKey(slide.variante);
    this.isFinal = index === env.finalIndex && (arch === 'A1' || arch === 'FIN') && (!vf || vf === 'aplat' || vf === 'mot-final');
    if (this.isFinal && STYLE.finale.pleinePageAccent && this.T.finaleAccent && (fond === 'sombre' || fond === 'clair')) {
      const PA = palette(this.T, 'accent');
      if (contrast(PA.bg, PA.fg) >= STYLE.finale.contraste) fond = 'accent';
    }
    this.fond = fond;
    this.P = palette(this.T, fond);
    this.items = [];
    this.warnings = [];
    this.proposals = [];   // [À VALIDER] affichés à l'écran
    this.fournirs = [];    // libellés [À FOURNIR] affichés à l'écran
    this.missing = [];     // images manquantes (placeholder dessiné)
    this.phs = [];         // placeholders dessinés (groupés dans le .pptx)
    this.names = {};
    this.curPh = null;
    this.accentWords = false;   // un mot *en accent* dans un texte de la slide
    this.accentUsed = false;    // l'accent est déjà pris (chiffre, barre, coches, ligne active) : surtitre en gris
    this.sourceText = slide.source ? String(slide.source) : '';
    const mode = env.sourceMode;
    // sous_le_chiffre : la source en clair sous le chiffre ; renvoi : un renvoi numéroté sous le
    // chiffre et la source complète au carton final ; carton_final : rien sur la slide.
    this.sourceOnSlide = !!this.sourceText && (mode === 'sous_le_chiffre' || mode === 'renvoi');
    this.sourceRef = 0;
    this.sourceDisplay = this.sourceText;
    if (this.sourceText && (mode === 'renvoi' || mode === 'carton_final')) {
      // Une même source garde le même numéro.
      const known = env.sourceIndex[this.sourceText];
      this.sourceNew = !known;
      if (!known) {
        env.sourceCounter += 1;
        env.sourceIndex[this.sourceText] = env.sourceCounter;
      }
      this.sourceRef = env.sourceIndex[this.sourceText];
      if (mode === 'renvoi') this.sourceDisplay = this.L.sourceRef(this.sourceRef);
    }
    this.sourceDone = false;
  }

  warn(msg) {
    if (!this.warnings.includes(msg)) this.warnings.push(msg);
  }

  // Ajoute un élément, avec un nom unique sur la slide (volet de sélection de PowerPoint).
  add(it) {
    const base = it.name || it.k;
    const n = (this.names[base] || 0) + 1;
    this.names[base] = n;
    it.name = n > 1 ? base + ' ' + n : base;
    if (this.curPh !== null && it.ph === undefined) {
      it.ph = this.curPh;
      const ph = this.phs[this.curPh];
      if (it.g === undefined) {
        it.g = ph.g;
        it.sub = ph.sub;
      }
    }
    this.items.push(it);
    return it;
  }

  // Champ de texte : valeur ou marqueur visible. Le champ principal d'une slide (titre, lignes,
  // chiffre, citation) qui manque prend le libellé tiré de la slide (hint), pas le nom du champ :
  // « titre », « lignes » ou « contenu » à l'écran sont des mots de l'atelier.
  f(field, label) {
    const v = this.t[field];
    if (v === undefined || v === null || String(v).trim() === '') {
      if (!this.hintUsed && ['titre', 'lignes', 'chiffre', 'citation'].includes(field)) {
        const h = this.hint();
        if (h) {
          this.hintUsed = true;
          label = h;
        }
      }
      return this.lang === 'en' ? '[TO PROVIDE: ' + label + ']' : '[À FOURNIR : ' + label + ']';
    }
    return String(v);
  }

  // Libellé court (3 mots au plus) de ce que la slide doit montrer : le début de textes.attendu,
  // sinon, pour une slide AF, son identifiant (« s13-garanties » → « Garanties »). Jamais un
  // libellé qui commence par un nombre (« 3 ou 4 garanties » se lirait comme un chiffre).
  hint() {
    const ok = (s) => {
      s = str(s).replace(/\s+/g, ' ').trim();
      const n = s.split(' ').filter(Boolean).length;
      return s && n <= 3 && !/^\d/.test(s) && !/[[\]*]/.test(s) ? s : '';
    };
    // « La slide de démonstration, à préparer… » → « démonstration » : ni article, ni « slide de ».
    const lead = /^(?:(?:la|le|les|un|une|des|the|an?)\s+|l['’]\s*)?(?:(?:slide|diapo|écran|ecran|screen)s?\s+(?:(?:de|du|des|of|for)\s+|d['’]\s*))?/i;
    let h = ok(str(this.t.attendu).split(/\s*[:;,.(]\s/)[0].replace(lead, ''));
    if (!h && this.arch === 'AF' && this.slide.id) {
      // Un identifiant qui n'est qu'un code (« af », « a9 », « s12 ») ne dit rien : on le laisse.
      const id = String(this.slide.id).replace(/^[a-z]?\d+[-_ ]*/i, '').replace(/[-_]+/g, ' ').trim();
      h = /[a-zà-ÿ]{3,}/i.test(id) && !/^(?:af|a\d+|slide|diapo)$/i.test(id) ? ok(id) : '';
      if (h) h = h.charAt(0).toUpperCase() + h.slice(1);
    }
    return h;
  }

  // Paragraphes d'un texte (un par ligne). o : rel (proportion du corps de la zone) ou pt (corps
  // fixe, ajusté à la police), gap (espace après, en pouces) ou gapK (en caps), wt (semi, regular,
  // bold), color, font (titre, texte), align, track, lh (interligne en caps), g, sub, subLines,
  // point (point final en accent), grad (dégradé du chiffre héros).
  para(text, o) {
    o = o || {};
    // Les marqueurs se lisent sur tout le texte, avant la coupure en lignes : une proposition
    // [À VALIDER : …\n…] garde ses deux lignes ; un libellé [À FOURNIR] revient sur une seule.
    const whole = stripValider(text, this.proposals).replace(new RegExp(FOURNIR_SRC, 'gi'), (m) => m.replace(/\s*\n\s*/g, ' '));
    if (new RegExp(OUVERT_SRC, 'i').test(whole.replace(new RegExp(FOURNIR_SRC, 'gi'), ''))) {
      this.warn('Marqueur sans « ] » final : il s\'affiche tel quel. Fermez-le dans deck.json.');
    }
    const lines = whole.split(/\n/);
    return lines.map((line, li) => {
      const raw = line;
      fournirLabels(raw).forEach((l) => { if (l && !this.fournirs.includes(l)) this.fournirs.push(l); });
      let runs = parseInline(typo(raw, this.lang), this.lang, this.env.crochets);
      if (runs.some((r) => r.accent)) this.accentWords = true;
      if (o.point && this.T.pointAccent) runs = accentPoint(runs);
      // Dégradé du chiffre héros : jamais sur un [À FOURNIR], qui reste estompé, d'une seule couleur.
      if (o.grad) runs = runs.map((r) => (r.marker ? r : Object.assign({}, r, { grad: true })));
      return {
        runs, rel: o.rel || 1, pt: o.pt ? scalePt(o.pt, o.font || 'texte') : undefined, gap: o.gap || 0, gapK: o.gapK,
        wt: o.wt, color: o.color, font: o.font, align: o.align, track: o.track, lh: o.lh, g: o.g, sub: o.subLines ? li : o.sub
      };
    });
  }

  // Corps le plus grand qui tient. o.stages : essais successifs { w, size, min, maxLines, maxTotal }
  // (largeur de mesure, corps, plancher, lignes permises par paragraphe et en tout).
  fitParas(item, o) {
    const stages = o.stages || [{ size: o.size, min: o.min, maxLines: o.maxLines, maxTotal: o.maxTotal }];
    for (const st of stages) {
      const size = scalePt(st.size !== undefined ? st.size : o.size || 18, item.font);
      const min = scalePt(st.min !== undefined ? st.min : (o.min !== undefined ? o.min : Math.min(st.size || o.size || 18, 12)), item.font);
      const probe = Object.assign({}, item, { w: st.w || item.w, size, min });
      const s = fitSize(probe, { maxLines: o.noWrap ? 1 : st.maxLines, maxTotal: st.maxTotal });
      if (s !== null) return s;
    }
    return null;
  }
  // Corps qui tient, sans rien ajouter à la slide (null si rien ne tient).
  fit(o) {
    const font = o.font || 'texte';
    const item = { paras: o.paras, w: o.w, h: o.h || 99, font, wt: o.wt || STYLE.graisse.texte, lh: o.lh || STYLE.interligne.texte, min: 0 };
    return this.fitParas(item, o);
  }

  // Ajoute une zone de texte ajustée à sa boîte. Corps (size, min, stages) en points de référence ;
  // fixed : corps final, sans ajustement.
  text(o) {
    const font = o.font || 'texte';
    const paras = o.paras || this.para(o.text === undefined ? '' : o.text, { color: o.color, wt: o.wt, font });
    const stages = o.stages || [{ size: o.size || 18, min: o.min, maxLines: o.maxLines, maxTotal: o.maxTotal }];
    const last = stages[stages.length - 1];
    const lastSize = last.size !== undefined ? last.size : (o.size || 18);
    const item = {
      k: 'text', x: o.x, y: o.y, w: o.w, h: o.h, paras,
      size: scalePt(stages[0].size !== undefined ? stages[0].size : (o.size || 18), font),
      min: scalePt(last.min !== undefined ? last.min : (o.min !== undefined ? o.min : Math.min(lastSize, 12)), font),
      wt: o.wt || STYLE.graisse.texte, align: o.align || 'left', valign: o.valign || 'middle', color: o.color || this.P.fg,
      font, lh: o.lh || STYLE.interligne.texte, name: o.name || 'Texte', g: o.g, sub: o.sub, noWrap: !!o.noWrap
    };
    if (o.fixed) item.fitted = o.fixed;
    else {
      item.fitted = this.fitParas(item, Object.assign({}, o, { stages }));
      if (item.fitted === null) {
        this.warn('Texte trop long pour sa place (' + item.name + ') : raccourcissez-le.');
        // En dernier recours, sous le plancher, pour ne pas sortir de la slide.
        item.fitted = fitSize(Object.assign({}, item, { size: item.min, min: Math.max(9, item.min * 0.6) }), { maxLines: o.noWrap ? 1 : undefined }) || item.min;
      }
    }
    if (o.balance && !o.noWrap) balanceParas(item);
    return this.add(item);
  }

  // Une ligne posée par sa ligne de base, au corps final o.size (sans ajustement).
  line(o) {
    const font = o.font || 'texte';
    const paras = o.paras || this.para(o.text, { color: o.color, wt: o.wt, font });
    const lh = o.lh || STYLE.interligne.titre;
    const cap = pol(font).cap * o.size / 72;
    const L = lh * cap;
    const h = L + 2 * PAD;
    return this.add({
      k: 'text', x: o.x, y: o.base - cap / 2 - h / 2, w: o.w, h, paras, size: o.size, min: o.size, fitted: o.size,
      wt: o.wt || STYLE.graisse.texte, align: o.align || 'center', valign: 'middle', color: o.color || this.P.fg,
      font, lh, name: o.name || 'Texte', g: o.g, sub: o.sub, noWrap: !!o.noWrap
    });
  }

  // Surtitre (style-visuel §3, « Surtitre ») : 0,42 × le corps du titre, entre 16 et 28 pt, sa ligne
  // de base à 0,45 cap au-dessus du haut des capitales du titre (geo : textGeom du titre). En accent
  // et demi-gras si l'accent de la slide est libre ; sinon en gris secondaire, regular.
  kicker(geo, o) {
    o = o || {};
    const s = this.t.surtitre;
    if (!s || !String(s).trim() || !geo) return null;
    const S = STYLE.surtitre;
    const size = o.size ? scalePt(o.size, 'texte')
      : clamp(Math.round(geo.firstSize * S.rapport * 2) / 2, scalePt(S.min, 'texte'), scalePt(S.max, 'texte'));
    const accent = o.accent !== undefined ? o.accent : !(this.accentUsed || this.accentWords);
    const color = o.color || (accent ? this.P.accentTxt : this.P.fg2);
    const base = geo.capTop - (o.ecart !== undefined ? o.ecart : S.ecart) * geo.capH;
    return this.line({ text: s, x: o.x, w: o.w, base, size, wt: o.wt || (accent ? 'semi' : 'regular'), color, align: o.align, font: 'texte', name: 'Surtitre', g: o.g || 'surtitre' });
  }

  rect(o) {
    return this.add(Object.assign({ k: 'rect' }, o));
  }
  round(o) {
    return this.add(Object.assign({ k: 'round' }, o));
  }
  ellipse(o) {
    return this.add(Object.assign({ k: 'ellipse' }, o));
  }
  check(o) {
    return this.add(Object.assign({ k: 'check' }, o));
  }

  imageSpec(spec) {
    if (!spec) return null;
    if (typeof spec === 'string') return { chemin: spec };
    return spec;
  }

  // Image dans une boîte ; si elle manque, placeholder dessiné aux couleurs du thème.
  // o : g, sub (groupe d'apparition), kind (forcer un type de placeholder), full (plein cadre),
  // alignX / alignY (left, right, top, bottom ; centre par défaut), radius (coins arrondis),
  // phBox(kind) (boîte du placeholder, si elle diffère de celle de l'image).
  // Retourne le rectangle dessiné de l'image, ou null quand un placeholder la remplace.
  image(box, spec, mode, name, o) {
    o = o || {};
    spec = this.imageSpec(spec);
    const attendu = spec ? str(spec.attendu || spec.libelle || spec.alt) : '';
    if (spec && spec.chemin) {
      const abs = path.resolve(this.env.deckDir, spec.chemin);
      const info = imageInfo(abs);
      if (info && info.w > 0 && info.h > 0) {
        const m = spec.ajustement === 'couvrir' ? 'cover' : spec.ajustement === 'contenir' ? 'contain' : (mode || 'contain');
        let r = { x: box.x, y: box.y, w: box.w, h: box.h };
        if (m === 'contain') {
          // Rectangle exact de l'image entière dans sa boîte : le même dans le .pptx et l'aperçu.
          const s = Math.min(box.w / info.w, box.h / info.h);
          const dw = info.w * s;
          const dh = info.h * s;
          r = {
            x: o.alignX === 'left' ? box.x : o.alignX === 'right' ? box.x + box.w - dw : box.x + (box.w - dw) / 2,
            y: o.alignY === 'top' ? box.y : o.alignY === 'bottom' ? box.y + box.h - dh : box.y + (box.h - dh) / 2,
            w: dw, h: dh
          };
        }
        this.add(Object.assign({ k: 'image', abs, info, mode: m === 'cover' ? 'cover' : 'fill', radius: o.radius || 0, name: name || 'Image', alt: attendu || path.basename(abs), g: o.g, sub: o.sub }, r));
        return r;
      }
      const reason = fs.existsSync(abs) ? 'illisible (PNG, JPEG ou GIF attendu)' : this.L.missingFile;
      this.warn('Image « ' + spec.chemin + ' » ' + reason + ' : placeholder dessiné à la place, à remplacer.');
    } else {
      this.warn('Image attendue' + (attendu ? ' (« ' + attendu + ' »)' : '') + ' : placeholder dessiné à la place.');
    }
    const kind = placeholderKind(this, spec, attendu, o);
    this.missing.push({ kind, attendu, chemin: spec && spec.chemin ? spec.chemin : '' });
    const pbox = (o.phBox && o.phBox(kind)) || box;
    drawPlaceholder(this, pbox, kind, attendu, Object.assign({ name }, o));
    return null;
  }

  sourceLine(o) {
    if (!this.sourceOnSlide || this.sourceDone) return;
    o = o || {};
    this.text({ x: o.x === undefined ? M : o.x, y: o.y === undefined ? 5.02 : o.y, w: o.w || W - 2 * M, h: o.h || 0.34, text: this.sourceDisplay, size: STYLE.source[0], min: STYLE.source[1], color: this.P.fg2, align: o.align || 'center', valign: 'top', font: 'texte', lh: STYLE.interligne.titre, name: 'Source', g: o.g });
    this.sourceDone = true;
  }
}

// Mesure ---------------------------------------------------------------------
function roleOf(it, p) {
  return (p && p.font) || it.font || 'texte';
}
function paraSize(it, p, s) {
  return p.pt ? p.pt : s * (p.rel || 1);
}
function paraWeight(it, p) {
  return (p && p.wt) || it.wt || STYLE.graisse.texte;
}
function heavy(wt) {
  return wt === 'semi' || wt === 'bold';
}
// Corps de référence (Inter) → corps qui donne la même hauteur de capitale dans la police du rôle.
function scalePt(pt, role) {
  if (pt === undefined || pt === null) return pt;
  return Math.round(pt * STYLE.capReference / pol(role).cap * 2) / 2;
}
// Suivi (em) selon la police et le corps (style-visuel §2.2).
function trackFor(role, ps) {
  if (ps < STYLE.suivi.sansSerrageSous) return 0;
  const s = pol(role).suivi;
  return Math.max(STYLE.suivi.max, ps >= 50 ? s[0] : ps >= 28 ? s[1] : s[2]);
}
function paraTrack(it, p, ps) {
  return p.track !== undefined ? p.track : trackFor(roleOf(it, p), ps);
}
function capIn(role, ps) {
  return pol(role).cap * ps / 72;
}
// Interligne exact (pouces) : k × hauteur de capitale.
function paraLineH(it, p, ps) {
  return (p.lh || it.lh || STYLE.interligne.texte) * capIn(roleOf(it, p), ps);
}
function paraGap(it, p, ps) {
  return p.gapK !== undefined ? p.gapK * capIn(roleOf(it, p), ps) : (p.gap || 0);
}
function paraInfo(it, p, ps, w) {
  const textOnly = p.runs.map((r) => r.t).join('');
  return wrapInfo(textOnly, ps, heavy(paraWeight(it, p)), w || it.w, paraTrack(it, p, ps), roleOf(it, p));
}
function layoutHeight(it, s, opts) {
  opts = opts || {};
  let hTot = 0;
  let ok = true;
  let total = 0;
  it.paras.forEach((p, i) => {
    const ps = paraSize(it, p, s);
    const info = paraInfo(it, p, ps);
    if (info.maxWord > it.w) ok = false;
    if (opts.maxLines && info.lines > opts.maxLines) ok = false;
    total += info.lines;
    hTot += info.lines * paraLineH(it, p, ps);
    if (i < it.paras.length - 1) hTot += paraGap(it, p, ps);
  });
  if (opts.maxTotal && total > opts.maxTotal) ok = false;
  return { h: hTot, ok, lines: total };
}
function fitSize(it, opts) {
  opts = opts || {};
  const floor = Math.max(it.min || 0, opts.floor || 0);
  for (let s = it.size; s >= floor - 1e-9; s -= (s > 48 ? 2 : 1)) {
    const r = layoutHeight(it, s, opts);
    if (r.ok && r.h <= it.h + 1e-6) return Math.round(s * 2) / 2;
  }
  return null;
}

// Géométrie verticale d'une zone de texte ajustée (pouces) : ses lignes, le haut des capitales de
// la première, la ligne de base de la dernière. Le centre d'une ligne est celui de ses capitales.
const PAD = 0.06;
function textGeom(it) {
  const lines = [];
  let y = 0;
  it.paras.forEach((p, i) => {
    const ps = paraSize(it, p, it.fitted);
    const L = paraLineH(it, p, ps);
    const cap = capIn(roleOf(it, p), ps);
    const n = it.noWrap ? 1 : paraInfo(it, p, ps).lines;
    for (let j = 0; j < n; j++) {
      lines.push({ c: y + L / 2, cap, L, ps });
      y += L;
    }
    if (i < it.paras.length - 1) y += paraGap(it, p, ps);
  });
  if (!lines.length) lines.push({ c: 0, cap: 0, L: 0, ps: it.fitted || 0 });
  const top = it.valign === 'top' ? it.y : it.valign === 'bottom' ? it.y + it.h - y : it.y + (it.h - y) / 2;
  lines.forEach((l) => { l.c += top; });
  const a = lines[0];
  const z = lines[lines.length - 1];
  return { top, h: y, n: lines.length, lines, capTop: a.c - a.cap / 2, capH: a.cap, firstSize: a.ps, base: z.c + z.cap / 2 };
}
// Zone de texte centrée sur cy (centre de la zone des capitales), resserrée sur son texte.
function centerBox(c, o) {
  const room = o.room !== undefined ? o.room : 2 * Math.max(0.6, Math.min(o.cy - 0.15, H - 0.15 - o.cy));
  const it = c.text(Object.assign({}, o, { y: o.cy - room / 2, h: room, valign: 'middle' }));
  const g = textGeom(it);
  it.h = g.h + 2 * PAD;
  it.y = o.cy - it.h / 2;
  return { it, g: textGeom(it) };
}
// Zone de texte posée par le haut des capitales de sa première ligne.
function topBox(c, o) {
  const it = c.text(Object.assign({}, o, { y: 0, h: o.room || H, valign: 'top' }));
  return placeTop(it, o.capTop);
}
function placeTop(it, capTop) {
  const g = textGeom(Object.assign({}, it, { y: 0, valign: 'top' }));
  it.valign = 'middle';
  it.h = g.h + 2 * PAD;
  it.y = capTop - g.capTop - PAD;
  return { it, g: textGeom(it) };
}
function shiftItems(items, dy) {
  items.forEach((it) => {
    if (it.k === 'check') it.cy += dy;
    else it.y += dy;
  });
}

// Équilibre les lignes d'un texte d'affichage : même nombre de lignes, largeur la plus
// régulière possible (évite un mot seul en dernière ligne). Les coupures deviennent des
// paragraphes, identiques dans le .pptx et dans l'aperçu.
function balanceParas(it) {
  const out = [];
  it.paras.forEach((p) => {
    const ps = paraSize(it, p, it.fitted);
    const hv = heavy(paraWeight(it, p));
    const tr = paraTrack(it, p, ps);
    const role = roleOf(it, p);
    const full = p.runs.map((r) => r.t).join('');
    const n = wrapInfo(full, ps, hv, it.w, tr, role).lines;
    if (n < 2 || n > 4) {
      out.push(p);
      return;
    }
    const lines = evenLines(full, ps, hv, it.w, n, tr, role);
    if (lines.length !== n) {
      out.push(p);
      return;
    }
    // Répartit les runs (accent, marqueurs) sur les lignes trouvées.
    const pieces = splitRuns(p.runs, lines);
    pieces.forEach((runs, i) => out.push(Object.assign({}, p, { runs, gap: i < pieces.length - 1 ? 0 : p.gap, gapK: i < pieces.length - 1 ? undefined : p.gapK })));
  });
  it.paras = out;
}
// Mots-outils qui ne finissent pas une ligne d'affichage (articles, prépositions, négation…).
const WEAK_END = /^(?:le|la|les|un|une|des|du|de|à|au|aux|en|et|ou|ne|n'|par|pour|sur|sous|sans|avec|dans|chez|vers|son|sa|ses|ce|cet|cette|ces|votre|vos|notre|nos|leur|leurs|mon|ma|mes|qui|que|dont|plus|a|an|the|of|to|in|on|at|for|with|and|or|by|from|your|our|my|its|their|is|are)$/i;
// Coupe en exactement n lignes, chacune <= w, les plus régulières possible
// (somme des écarts au carré à la longueur moyenne la plus petite).
function evenLines(s, pt, hv, w, n, track, role) {
  const words = s.split(/ +/).filter((x) => x.length);
  if (words.length < n || words.length > 40) return greedyLines(s, pt, hv, w, track, role);
  const ww = words.map((x) => textWidth(x, pt, hv, track, role));
  const sp = textWidth(' ', pt, hv, track, role);
  const lineW = (i, j) => {
    let t = 0;
    for (let k = i; k < j; k++) t += ww[k] + (k > i ? sp : 0);
    return t;
  };
  const total = lineW(0, words.length);
  const mean = (total - sp * (n - 1)) / n;
  const memo = new Map();
  const best = (i, left) => {
    const key = i + ':' + left;
    if (memo.has(key)) return memo.get(key);
    let res = null;
    if (left === 1) {
      const lw = lineW(i, words.length);
      res = lw <= w ? { cost: (lw - mean) * (lw - mean), cuts: [] } : null;
    } else {
      for (let j = i + 1; j <= words.length - (left - 1); j++) {
        const lw = lineW(i, j);
        if (lw > w) break;
        const rest = best(j, left - 1);
        if (!rest) continue;
        // Une ligne ne finit pas sur un mot-outil (« Une panne ne / prévient jamais. ») : la
        // coupure suit le sens, comme dans les keynotes, quitte à des lignes moins égales.
        const weak = WEAK_END.test(words[j - 1].replace(/[«»"“”]/g, '')) ? STYLE.coupure.motOutil * mean * mean : 0;
        const cost = (lw - mean) * (lw - mean) + weak + rest.cost;
        if (!res || cost < res.cost) res = { cost, cuts: [j].concat(rest.cuts) };
      }
    }
    memo.set(key, res);
    return res;
  };
  const r = best(0, n);
  if (!r) return greedyLines(s, pt, hv, w, track, role);
  const out = [];
  let start = 0;
  r.cuts.concat([words.length]).forEach((end) => {
    out.push(words.slice(start, end).join(' '));
    start = end;
  });
  return out;
}
function greedyLines(s, pt, hv, w, track, role) {
  const words = s.split(/ +/).filter((x) => x.length);
  const sp = textWidth(' ', pt, hv, track, role);
  const lines = [];
  let cur = '';
  let curW = 0;
  for (const wd of words) {
    const ww = textWidth(wd, pt, hv, track, role);
    if (!cur) {
      cur = wd;
      curW = ww;
    } else if (curW + sp + ww <= w) {
      cur += ' ' + wd;
      curW += sp + ww;
    } else {
      lines.push(cur);
      cur = wd;
      curW = ww;
    }
  }
  if (cur) lines.push(cur);
  return lines;
}
function splitRuns(runs, lines) {
  // Coupe la suite de runs aux frontières de lignes (les espaces de coupure sont retirés).
  const flat = [];
  runs.forEach((r) => {
    for (const ch of r.t) flat.push({ ch, r });
  });
  const text = flat.map((x) => x.ch).join('').replace(/ +/g, ' ');
  if (text.trim() !== lines.join(' ')) return [runs];
  const out = [];
  let idx = 0;
  const chars = flat.filter((x, i) => !(x.ch === ' ' && flat[i - 1] && flat[i - 1].ch === ' '));
  while (idx < chars.length && chars[idx].ch === ' ') idx += 1;
  lines.forEach((line) => {
    const seg = chars.slice(idx, idx + line.length);
    idx += line.length;
    while (idx < chars.length && chars[idx].ch === ' ') idx += 1;
    const lr = [];
    seg.forEach((x) => {
      const last = lr[lr.length - 1];
      if (last && last.src === x.r) last.t += x.ch;
      else lr.push({ t: x.ch, src: x.r });
    });
    out.push(lr.map((r) => Object.assign({}, r.src, { t: r.t })));
  });
  return out;
}

// ---------------------------------------------------------------------------
// Placeholders dessinés (style-visuel §5.2) : une image qui manque devient une interface
// schématique, un appareil générique, un objet, une photo ou une carte, aux couleurs de la slide.
// Aucun chiffre ni texte inventé, aucun trait, aucune consigne à l'écran : des aplats, des barres
// grises et une seule ligne en accent. Ce que l'image doit montrer part dans les notes.
// ---------------------------------------------------------------------------
const KIND_RX = {
  appareil: /\b(mobile|telephones?|smartphones?|portables?|android|phones?|tablettes?|tablets?)\b/,
  carte: /\b(cartes? (?:de|du|des)|plans? de (?:la )?ville|zones? desservies?|maps?|territoires?)\b/,
  interface: /\b(captures?|ecrans?|interfaces?|tableaux? de bord|dashboards?|pages?|applis?|applications?|logiciels?|modules?|demos?|factures?|listes?|screens?|screenshots?|ui|web|sites?|espaces? clients?|portails?|suivis?)\b/,
  photo: /\b(photos?|portraits?|equipes?|personnes?|scenes?|decors?|ambiances?|paysages?|people|team|crowd|lifestyle)\b/,
  objet: /\b(produits?|boitiers?|objets?|capteurs?|machines?|vehicules?|emballages?|packagings?|bouteilles?|hardware|products?|box|coffrets?)\b/
};
const VARIANT_RX = [
  ['tableau', /\b(tableaux? de bord|dashboards?|statistiques?|kpi|indicateurs?|graphiques?|charts?|analytics|rapports?|reporting)\b/],
  ['liste', /\b(listes?|suivis?|statuts?|historiques?|lists?|tables?|inbox|commandes|toutes les)\b/],
  ['document', /\b(factures?|documents?|details?|fiches?|formulaires?|devis|bons? de|contrats?|invoices?|forms?|records?|e-mails?|mails?)\b/]
];
function normText(s) {
  return String(s || '').normalize('NFD').replace(/[̀-ͯ]/g, '').toLowerCase()
    .replace(/[’`]/g, '\'');
}
function placeholderKind(c, spec, attendu, o) {
  const forced = normText(spec && (spec.rendu || spec.placeholder || spec.type));
  const map = { interface: 'interface', capture: 'interface', ecran: 'interface', appareil: 'appareil', telephone: 'appareil', mobile: 'appareil', objet: 'objet', produit: 'objet', photo: 'photo', carte: 'carte', map: 'carte' };
  if (map[forced]) return map[forced];
  if (o.kind) return o.kind;
  const t = normText(attendu + ' ' + (spec && spec.chemin ? path.basename(spec.chemin).replace(/[-_.]/g, ' ') : ''));
  if (KIND_RX.appareil.test(t)) return 'appareil';
  if (KIND_RX.carte.test(t)) return 'carte';
  if (KIND_RX.interface.test(t)) return 'interface';
  if (KIND_RX.photo.test(t)) return 'photo';
  if (KIND_RX.objet.test(t)) return 'objet';
  if (['A13', 'A19', 'A20'].includes(c.renderArch)) return 'objet';
  return 'interface';
}
// Couleurs d'un schéma. L'écran se lit comme une vraie capture en mode clair, quel que soit le fond
// de la slide : sur fond sombre, une carte claire (fond_clair, ou blanc) ; sur fond clair, une
// carte blanche, ou grise à 5 % si le fond est déjà blanc, ses aplats intérieurs devenant blancs.
// Une carte sombre à 8 % (itération 2, première version) se lisait comme un écran de chargement.
function schemaColors(c) {
  const P = c.P;
  const T = c.T;
  const SC = STYLE.schema;
  const dark = lum(P.bg) < 0.35;
  const ink = lum(T.texte) < 0.35 ? T.texte : '15181C';
  let card;
  if (dark) card = contrast(T.fondClair, P.bg) >= 7 ? T.fondClair : 'FFFFFF';
  else card = contrast(P.bg, 'FFFFFF') > 1.04 ? 'FFFFFF' : mix(P.bg, ink, SC.carteGrise);
  const white = contrast(card, 'FFFFFF') < 1.04;
  const C = {
    dark, card, shadow: !dark,
    sub: white ? mix(card, ink, 0.045) : 'FFFFFF',   // aplats intérieurs (lignes, cartes, champs), sans trait
    bar: mix(card, ink, SC.barres[0]),
    strong: mix(card, ink, SC.barres[1]),
    soft: mix(card, ink, 0.1),
    accent: P.accent,
    bezel: dark ? mix(P.bg, P.fg, 0.2) : mix(P.bg, ink, 0.85)
  };
  // Un accent clair (jaune sur blanc : 1,1:1) disparaît en barre fine : il devient alors une
  // pastille pleine, avec un trait sombre dedans, et la ligne mise en avant se teinte d'accent.
  C.accentFaint = contrast(card, P.accent) < SC.contrasteBarre;
  C.onAccent = mix(onAccent(P.accent, ink), P.accent, 0.3);
  C.tint = mix(C.sub === 'FFFFFF' ? 'FFFFFF' : C.sub, P.accent, 0.22);
  return C;
}
// La ligne mise en avant d'un schéma : une barre d'accent, ou une pastille si l'accent est trop clair.
function hiBar(c, C, x, y, w, h) {
  if (!C.accentFaint) {
    pill(c, x, y, w, h, C.accent, 'Schéma ligne en avant');
    return;
  }
  const ph = h * 2.6;
  pill(c, x - ph * 0.35, y + h / 2 - ph / 2, w + ph * 0.7, ph, C.accent, 'Schéma ligne en avant');
  pill(c, x, y, w * 0.72, h, C.onAccent, 'Schéma ligne en avant trait');
}
function drawPlaceholder(c, box, kind, attendu, o) {
  const L = c.L;
  const cap = L.cap[kind] || L.cap.interface;
  const short = shortLabel(str(stripValider(attendu)).replace(new RegExp(FOURNIR_SRC, 'gi'), (m) => markerInner(m)), 6);
  // Nom du groupe dans le volet de sélection du .pptx : il dit quoi remplacer, sans rien afficher.
  const label = cap + (short ? ' · ' + short : '');
  const ph = { id: c.phs.length, name: label, kind, g: o.g, sub: o.sub };
  c.phs.push(ph);
  c.curPh = ph.id;
  try {
    const C = schemaColors(c);
    const rnd = rng(31 * (c.index + 1) + Math.round(box.x * 10) + Math.round(box.y * 7));
    if (kind === 'photo') drawPhoto(c, o.full ? { x: 0, y: 0, w: W, h: H } : box, C, !!o.full);
    else if (kind === 'objet') drawObject(c, box, C);
    else if (kind === 'carte') drawMap(c, box, C, rnd);
    else if (kind === 'appareil') drawPhone(c, box, C);
    else if (kind === 'icone') drawIcon(c, box);
    else if (kind === 'logo') drawLogo(c, box, C, attendu);
    // Tuile d'image (mur, bento) : un aplat voisin des tuiles, pas un écran clair au milieu du mur.
    else if (kind === 'tuile') c.round({ x: box.x, y: box.y, w: box.w, h: box.h, fill: C.dark ? mix(c.P.bg, c.P.fg, 0.16) : C.sub, radius: Math.min(STYLE.A14.rayon, box.w / 4, box.h / 4), name: 'Schéma' });
    else drawWindow(c, box, C, rnd, interfaceVariant(attendu, c.index));
  } finally {
    c.curPh = null;
  }
}
function interfaceVariant(attendu, index) {
  const t = normText(attendu);
  for (const [v, rx] of VARIANT_RX) if (rx.test(t)) return v;
  return ['liste', 'document', 'tableau'][index % 3];
}
function pill(c, x, y, w, h, fill, name) {
  if (w <= 0 || h <= 0) return;
  c.round({ x, y, w, h, fill, radius: h / 2, name: name || 'Schéma' });
}
// Fenêtre d'application : carte sans trait, un mot-titre en barre forte, une colonne de navigation
// si la place le permet, puis le contenu (liste, tableau de bord ou document).
function drawWindow(c, b, C, rnd, variant) {
  const SC = STYLE.schema;
  const bh = SC.barre;
  c.round({ x: b.x, y: b.y, w: b.w, h: b.h, fill: C.card, radius: Math.min(SC.rayon, b.w / 6, b.h / 6), shadow: C.shadow, name: 'Schéma fenêtre' });
  const pad = clamp(Math.min(b.w, b.h) * 0.07, 0.1, 0.3);
  if (b.h < 1.3 || b.w < 1.8) {
    // Petite carte : un mot-titre, trois barres, une en accent.
    pill(c, b.x + pad, b.y + pad, (b.w - 2 * pad) * 0.5, bh * 1.2, C.strong);
    for (let i = 0; i < 3; i++) {
      const y = b.y + pad + (i + 1.6) * SC.pas;
      if (y + bh > b.y + b.h - pad * 0.6) break;
      if (i === 1) hiBar(c, C, b.x + pad, y, (b.w - 2 * pad) * SC.longueurs[i], bh);
      else pill(c, b.x + pad, y, (b.w - 2 * pad) * SC.longueurs[i], bh, C.bar);
    }
    return;
  }
  pill(c, b.x + pad, b.y + pad, b.w * 0.18, bh * 1.3, C.strong);
  pill(c, b.x + b.w - pad - b.w * 0.14, b.y + pad - bh * 0.35, b.w * 0.14, bh * 2, C.sub);
  const y0 = b.y + pad + bh * 1.3 + pad;
  const bottom = b.y + b.h - pad;
  let cx = b.x + pad;
  let cw = b.w - 2 * pad;
  if (b.w >= 4.2) {
    const sw = b.w * 0.2;
    const lens = [0.85, 0.6, 0.75, 0.5, 0.7, 0.55, 0.65];
    for (let i = 0; i < 7 && y0 + i * 0.3 + bh <= bottom; i++) pill(c, b.x + pad, y0 + i * 0.3, (sw - pad * 1.5) * lens[i], bh, C.bar);
    cx = b.x + sw + pad * 0.5;
    cw = b.w - sw - pad * 1.5;
  }
  const area = { x: cx, y: y0, w: cw, h: bottom - y0 };
  if (area.h < 0.4) return;
  if (variant === 'tableau') drawDashboard(c, area, C, rnd);
  else if (variant === 'document') drawDocument(c, area, C, rnd);
  else drawList(c, area, C);
}
function drawList(c, a, C) {
  const SC = STYLE.schema;
  const rh = clamp(a.h / 6, 0.4, 0.6);
  const rows = Math.max(2, Math.floor((a.h + 0.07) / rh));
  const hi = Math.min(rows - 1, 1);
  const tw = a.w * 0.5;
  for (let i = 0; i < rows; i++) {
    const y = a.y + i * rh;
    const h = rh - 0.07;
    c.round({ x: a.x, y, w: a.w, h, fill: i === hi ? C.tint : C.sub, radius: Math.min(0.08, h / 3), name: i === hi ? 'Schéma ligne en avant' : 'Schéma ligne' });
    const d = Math.min(0.22, h * 0.5);
    c.ellipse({ x: a.x + 0.12, y: y + (h - d) / 2, w: d, h: d, fill: C.bar, name: 'Schéma' });
    const tx = a.x + 0.12 + d + 0.14;
    const ty = y + h / 2 - (SC.pas + SC.barre) / 2;
    pill(c, tx, ty, tw * SC.longueurs[i % 3], SC.barre, C.strong);
    pill(c, tx, ty + SC.pas, tw * SC.longueurs[(i + 1) % 3] * 0.6, SC.barre, C.bar);
    // Colonne d'état : une pastille par ligne, en accent sur la ligne mise en avant.
    const sw = a.w * 0.13;
    const sh = Math.min(0.2, h * 0.42);
    pill(c, a.x + a.w - 0.12 - sw, y + h / 2 - sh / 2, sw, sh, i === hi ? C.accent : C.soft, i === hi ? 'Schéma état en avant' : 'Schéma');
  }
}
function drawDashboard(c, a, C, rnd) {
  const SC = STYLE.schema;
  const g = 0.1;
  const kh = clamp(a.h * 0.3, 0.45, 0.8);
  const kw = (a.w - 2 * g) / 3;
  for (let k = 0; k < 3; k++) {
    const x = a.x + k * (kw + g);
    c.round({ x, y: a.y, w: kw, h: kh, fill: C.sub, radius: 0.08, name: 'Schéma carte' });
    pill(c, x + 0.12, a.y + 0.14, kw * 0.4, SC.barre, C.bar);
    pill(c, x + 0.12, a.y + kh - 0.14 - SC.barre * 2, kw * (0.5 + rnd() * 0.25), SC.barre * 2, C.strong);
  }
  const cy = a.y + kh + g;
  const ch = a.h - kh - g;
  if (ch < 0.5) return;
  c.round({ x: a.x, y: cy, w: a.w, h: ch, fill: C.sub, radius: 0.08, name: 'Schéma graphique' });
  pill(c, a.x + 0.14, cy + 0.14, a.w * 0.2, SC.barre, C.bar);
  const n = 9;
  const pad = 0.2;
  const step = (a.w - 2 * pad) / n;
  const bw = step * 0.5;
  const base = cy + ch - 0.16;
  const topY = cy + 0.4;
  for (let i = 0; i < n; i++) {
    const bh = Math.max(0.06, (base - topY) * (0.3 + rnd() * 0.7));
    c.round({ x: a.x + pad + i * step + bw * 0.5, y: base - bh, w: bw, h: bh, fill: i === 5 ? C.accent : C.bar, radius: Math.min(bw / 2, 0.05), name: i === 5 ? 'Schéma barre en avant' : 'Schéma' });
  }
}
function drawDocument(c, a, C, rnd) {
  const SC = STYLE.schema;
  const dw = a.w * 0.62;
  c.round({ x: a.x, y: a.y, w: dw, h: a.h, fill: C.sub, radius: 0.08, name: 'Schéma document' });
  const pad = 0.18;
  const iw = dw - 2 * pad;
  pill(c, a.x + pad, a.y + pad, iw * 0.4, SC.barre * 1.4, C.strong);
  for (let i = 0; i < 2; i++) pill(c, a.x + pad, a.y + pad + 0.3 + i * SC.pas, iw * 0.55 * SC.longueurs[i + 1], SC.barre, C.bar);
  let y = a.y + pad + 0.3 + 2 * SC.pas + 0.16;
  const stepY = SC.pas * 1.8;
  const rows = Math.max(2, Math.floor((a.y + a.h - pad - 0.32 - y) / stepY));
  const hi = Math.min(rows - 1, 1 + Math.floor(rnd() * 2));
  for (let i = 0; i < rows; i++) {
    if (i === hi) hiBar(c, C, a.x + pad, y, iw * 0.55 * SC.longueurs[i % 3], SC.barre);
    else pill(c, a.x + pad, y, iw * 0.55 * SC.longueurs[i % 3], SC.barre, C.bar);
    pill(c, a.x + pad + iw * 0.78, y, iw * 0.22, SC.barre, C.bar);
    y += stepY;
  }
  pill(c, a.x + pad + iw * 0.6, a.y + a.h - pad - SC.barre * 1.4, iw * 0.4, SC.barre * 1.4, C.strong);
  // Panneau latéral : champs en aplat, un bouton.
  const px = a.x + dw + 0.14;
  const pw = a.w - dw - 0.14;
  if (pw < 0.5) return;
  for (let i = 0; i < 3; i++) {
    const fy = a.y + i * 0.62;
    if (fy + 0.5 > a.y + a.h - 0.45) break;
    pill(c, px, fy + 0.04, pw * 0.45, SC.barre, C.bar);
    c.round({ x: px, y: fy + 0.2, w: pw, h: 0.28, fill: C.sub, radius: 0.06, name: 'Schéma champ' });
  }
  c.round({ x: px, y: a.y + a.h - 0.3, w: pw, h: 0.3, fill: C.strong, radius: 0.15, name: 'Schéma bouton' });
}
// Appareil générique : coins à 13 % de la largeur, bord de 3 %, ni encoche ni bouton.
function drawPhone(c, b, C) {
  const SC = STYLE.schema;
  const ph = b.h;
  const pw = Math.min(b.w * 0.92, ph * 0.49);
  const x0 = b.x + (b.w - pw) / 2;
  c.round({ x: x0, y: b.y, w: pw, h: ph, fill: C.bezel, radius: pw * SC.appareil.coin, shadow: C.shadow, name: 'Schéma appareil' });
  const e = pw * SC.appareil.bord;
  const sx = x0 + e;
  const sy = b.y + e;
  const sw = pw - 2 * e;
  const sh = ph - 2 * e;
  c.round({ x: sx, y: sy, w: sw, h: sh, fill: C.card, radius: pw * (SC.appareil.coin - SC.appareil.bord), name: 'Schéma écran' });
  const p = sw * 0.09;
  const ix = sx + p;
  const iw = sw - 2 * p;
  pill(c, ix, sy + sh * 0.09, iw * 0.55, SC.barre * 1.4, C.strong);
  pill(c, ix, sy + sh * 0.09 + SC.pas * 1.2, iw * 0.35, SC.barre, C.bar);
  const ct = sy + sh * 0.2;
  const cardH = sh * 0.12;
  const gap = sh * 0.025;
  for (let i = 0; i < 4; i++) {
    const y = ct + i * (cardH + gap);
    c.round({ x: ix, y, w: iw, h: cardH, fill: i === 1 ? C.tint : C.sub, radius: Math.min(0.1, cardH * 0.25), name: 'Schéma carte' });
    const d = cardH * 0.42;
    c.ellipse({ x: ix + cardH * 0.25, y: y + (cardH - d) / 2, w: d, h: d, fill: C.bar, name: 'Schéma' });
    const tx = ix + cardH * 0.25 + d + cardH * 0.22;
    const tw = ix + iw - tx - cardH * 0.25;
    const ty = y + cardH / 2 - (SC.pas * 0.8 + SC.barre) / 2;
    if (i === 1) hiBar(c, C, tx, ty, tw * SC.longueurs[i % 3], SC.barre);
    else pill(c, tx, ty, tw * SC.longueurs[i % 3], SC.barre, C.strong);
    pill(c, tx, ty + SC.pas * 0.8, tw * 0.5, SC.barre, C.bar);
  }
  pill(c, ix, sy + sh * 0.9, iw, Math.max(SC.barre * 2.6, sh * 0.055), C.strong, 'Schéma bouton');
}
// Objet : une silhouette simple et un voyant d'accent ; ombre de contact sur fond clair seulement.
function drawObject(c, b, C) {
  const s = Math.min(b.w, b.h) * 0.7;
  const cx = b.x + b.w / 2;
  const top = b.y + (b.h - s) / 2;
  if (!C.dark) c.ellipse({ x: cx - s * 0.5, y: top + s * 0.96, w: s, h: s * 0.1, fill: c.P.fg, transparency: 90, name: 'Schéma ombre' });
  c.round({ x: cx - s * 0.5, y: top, w: s, h: s, fill: mix(c.P.bg, c.P.fg, C.dark ? 0.16 : 0.1), radius: s * 0.22, name: 'Schéma objet' });
  c.round({ x: cx - s * 0.34, y: top + s * 0.2, w: s * 0.68, h: s * 0.42, fill: mix(c.P.bg, c.P.fg, C.dark ? 0.08 : 0.18), radius: s * 0.08, name: 'Schéma face' });
  const d = s * 0.07;
  c.ellipse({ x: cx - d / 2, y: top + s * 0.76, w: d, h: d, fill: C.accent, name: 'Schéma voyant' });
}
// Photo : un fond un peu plus clair que la slide et deux halos neutres. Plus de reflet d'accent :
// l'accent translucide sur un fond sombre virait au kaki.
function drawPhoto(c, b, C, full) {
  const ink = c.P.fg;
  const base = mix(c.P.bg, ink, C.dark ? 0.07 : 0.06);
  if (full) {
    c.rect({ x: b.x, y: b.y, w: b.w, h: b.h, fill: base, name: 'Schéma photo' });
    c.ellipse({ x: b.x + b.w * 0.45, y: b.y - b.h * 0.35, w: b.w * 0.75, h: b.h * 1.25, fill: ink, transparency: 93, name: 'Schéma lumière' });
    c.ellipse({ x: b.x - b.w * 0.15, y: b.y + b.h * 0.45, w: b.w * 0.7, h: b.h * 0.95, fill: ink, transparency: 95, name: 'Schéma lumière' });
  } else {
    c.round({ x: b.x, y: b.y, w: b.w, h: b.h, fill: base, radius: Math.min(STYLE.schema.rayon, b.w / 6, b.h / 6), name: 'Schéma photo' });
    c.ellipse({ x: b.x + b.w * 0.36, y: b.y + b.h * 0.1, w: b.w * 0.56, h: b.h * 0.76, fill: ink, transparency: 91, name: 'Schéma lumière' });
    c.ellipse({ x: b.x + b.w * 0.08, y: b.y + b.h * 0.42, w: b.w * 0.4, h: b.h * 0.48, fill: ink, transparency: 94, name: 'Schéma lumière' });
  }
}
function drawMap(c, b, C, rnd) {
  c.round({ x: b.x, y: b.y, w: b.w, h: b.h, fill: C.card, radius: Math.min(STYLE.schema.rayon, b.w / 6, b.h / 6), shadow: C.shadow, name: 'Schéma carte' });
  const t = 0.022;
  for (let i = 1; i < 6; i++) c.rect({ x: b.x + 0.1, y: b.y + b.h * i / 6 + (rnd() - 0.5) * 0.1, w: b.w - 0.2, h: t, fill: C.soft, name: 'Schéma rue' });
  for (let i = 1; i < 8; i++) c.rect({ x: b.x + b.w * i / 8 + (rnd() - 0.5) * 0.15, y: b.y + 0.1, w: t, h: b.h - 0.2, fill: C.soft, name: 'Schéma rue' });
  c.rect({ x: b.x + 0.1, y: b.y + b.h * 0.55, w: b.w - 0.2, h: t * 2, fill: C.bar, name: 'Schéma axe' });
  c.ellipse({ x: b.x + b.w * 0.3, y: b.y + b.h * 0.2, w: b.w * 0.42, h: b.h * 0.58, fill: c.P.accent, transparency: 75, name: 'Schéma zone' });
  const d = Math.min(b.w, b.h) * 0.07;
  c.ellipse({ x: b.x + b.w * 0.51 - d / 2, y: b.y + b.h * 0.49 - d / 2, w: d, h: d, fill: c.P.accent, name: 'Schéma repère' });
}
function drawIcon(c, b) {
  const s = Math.min(b.w, b.h);
  const x = b.x + (b.w - s) / 2;
  const y = b.y + (b.h - s) / 2;
  c.round({ x, y, w: s, h: s, fill: c.P.accent, radius: s * 0.24, name: 'Schéma icône' });
  c.ellipse({ x: x + s * 0.3, y: y + s * 0.3, w: s * 0.4, h: s * 0.4, line: onAccent(c.P.accent, c.T.fondSombre), lineW: Math.max(2, s * 6), name: 'Schéma' });
}
// Logo à fournir : son nom (ou son marqueur) dans le style du texte, sans cadre.
function drawLogo(c, b, C, nom) {
  if (!str(nom).trim()) {
    pill(c, b.x + b.w * 0.2, b.y + b.h / 2 - 0.06, b.w * 0.6, 0.12, C.bar);
    return;
  }
  c.text({ x: b.x, y: b.y, w: b.w, h: b.h, text: nom, size: STYLE.A16.nom[0], min: STYLE.A16.nom[1], maxTotal: 2, wt: 'semi', color: c.P.fg2, align: 'center', font: 'texte', lh: STYLE.interligne.titre, name: 'Logo nom' });
}

// ---------------------------------------------------------------------------
// Archétypes : les fiches de style-visuel.md §3. Chaque bloc de texte est posé par le centre de sa
// zone des capitales (centerBox) ou par le haut de ses capitales (topBox, placeTop) ; les mêmes
// positions servent au .pptx et à l'aperçu.
// ---------------------------------------------------------------------------
const R = {};
const K = STYLE.interligne;
const FULL_W = W - 2 * M;
// Texte tel qu'il s'affiche (marqueurs retirés), pour estimer une largeur.
function shownText(c, s) {
  return parseInline(typo(stripValider(s), c.lang), c.lang, c.env.crochets).map((r) => r.t).join('');
}
// Essais d'un mot ou d'un nom très gros (A1) : une ligne dans 6,4 in, puis une ligne large, puis deux lignes.
function bigStages(max, multi) {
  const A = STYLE.A1;
  if (multi) return [{ w: A.w, size: Math.min(max, A.deuxLignes[0]), min: A.deuxLignes[1], maxLines: 1 }];
  return [
    { w: A.uneLigne, size: max, min: A.corps[1], maxLines: 1 },
    { w: A.w, size: A.large[0], min: A.large[1], maxLines: 1 },
    { w: A.w, size: A.deuxLignes[0], min: A.deuxLignes[1], maxTotal: 2 }
  ];
}

R.A1 = (c) => {
  const A = STYLE.A1;
  const S = c.isFinal ? STYLE.finale : A;
  const paras = c.para(c.f('titre', 'titre'), { wt: 'semi', font: 'titre', g: 'titre', point: true });
  const t = centerBox(c, { x: A.x, w: A.w, cy: S.cy, paras, stages: bigStages(S.corps[0], paras.length > 1), wt: 'semi', align: 'center', font: 'titre', lh: K.titre, balance: true, name: 'Titre' });
  c.kicker(t.g, { x: A.x, w: A.w, align: 'center' });
  c.sourceLine();
};

R.A2 = (c) => {
  const S = STYLE.A2;
  const spec = c.slide.image || (c.T.logo ? { chemin: c.T.logo, attendu: 'logo' } : { attendu: c.lang === 'en' ? 'icon or logo' : 'icône ou logo' });
  const paras = c.para(c.f('titre', 'nom'), { wt: 'semi', font: 'titre', g: 'titre' });
  const t = topBox(c, { x: M, w: FULL_W, capTop: 0, paras, size: S.nom[0], min: S.nom[1], maxTotal: 2, wt: 'semi', align: 'center', font: 'titre', lh: K.titre, balance: true, name: 'Nom' });
  const top = S.cy - (S.icone + S.ecart + (t.g.base - t.g.capTop)) / 2;
  const g = placeTop(t.it, top + S.icone + S.ecart).g;
  c.image({ x: W / 2 - S.icone / 2, y: top, w: S.icone, h: S.icone }, spec, 'contain', 'Icône', { g: 'visuel', kind: 'icone' });
  c.kicker({ capTop: top, capH: g.capH, firstSize: g.firstSize }, { x: M, w: FULL_W, align: 'center', ecart: 0.9 });
  c.sourceLine();
};

// Lignes d'une liste : la ligne active (actif, de 1 à n) en activeColor, les autres en idleColor.
function listParas(c, lines, o) {
  const actif = Number(c.t.actif) || 0;
  const out = [];
  lines.forEach((l, i) => {
    let color = o.color;
    if (actif) color = i + 1 === actif ? o.activeColor : o.idleColor;
    c.para(l, { color, wt: 'semi', font: o.font, gapK: o.gapK, g: 'lignes', sub: i }).forEach((p) => out.push(p));
  });
  return out;
}

R.A3 = (c) => {
  const S = STYLE.A3;
  const lines = arr(c.t.lignes);
  if (!lines.length) lines.push(c.f('lignes', 'lignes'));
  c.accentUsed = !!(Number(c.t.actif) || 0);
  const paras = listParas(c, lines, { color: c.P.fg, activeColor: c.P.accentTxt, idleColor: c.P.fg2, font: 'titre' });
  const size = S.corps[clamp(lines.length, 1, 8)];
  const t = centerBox(c, { x: S.x, w: S.w, cy: S.cy, paras, size, min: Math.min(size, S.plancher), maxLines: 1, wt: 'semi', align: 'center', font: 'titre', lh: K.sommaire, name: 'Sommaire' });
  c.kicker(t.g, { x: S.x, w: S.w, align: 'center' });
  c.sourceLine();
};

R.A4 = (c) => {
  const S = STYLE.A4;
  // Avec des retours à la ligne voulus (\n), chaque ligne reste entière.
  const paras = c.para(c.f('titre', 'phrase'), { wt: 'semi', font: 'titre', g: 'titre', subLines: true, point: true });
  const stages = [{ size: S.corps[0], min: S.corps[1], maxLines: paras.length > 1 ? 1 : 2, maxTotal: 2 }];
  const t = centerBox(c, { x: S.x, w: S.w, cy: S.cy, paras, stages, wt: 'semi', align: 'center', font: 'titre', lh: K.titre, balance: true, name: 'Phrase' });
  c.kicker(t.g, { x: S.x, w: S.w, align: 'center' });
  c.sourceLine();
};

// A5 : chiffre héros centré sur le milieu, libellé en bas (mise en page a) ; si le libellé tient
// sur deux lignes, le bloc entier remonte et le libellé suit le chiffre (mise en page b).
R.A5 = (c) => {
  const S = STYLE.A5;
  c.accentUsed = true;
  const grad = c.T.gradient && c.P.accent === c.T.accent && contrast(c.P.bg, c.T.accent) >= 2.6 && contrast(c.P.bg, c.T.accent2) >= 2.6;
  const color = c.P.accentTxt;
  const heroParas = c.para(c.f('chiffre', 'chiffre'), { wt: 'semi', font: 'titre', color, grad });
  const libParas = c.para(c.f('libelle', 'libellé'), { wt: 'semi', font: 'texte', g: 'libelle' });
  const oneLine = c.fit({ paras: libParas, w: S.libelleW, size: S.libelle[0], min: S.libelle[1], maxLines: 1, wt: 'semi', font: 'texte', lh: K.titre }) !== null;
  const hero = centerBox(c, { x: M, w: FULL_W, cy: oneLine ? S.cy : S.cyDeuxLignes, paras: heroParas, stages: [{ w: S.largeur, size: S.chiffre[0], min: S.chiffre[1], maxLines: 1 }], noWrap: true, wt: 'semi', align: 'center', font: 'titre', color, lh: K.titre, name: 'Chiffre', g: 'chiffre' });
  if (grad) {
    // Le dégradé suit la boîte : on la resserre sur le chiffre pour qu'il le parcoure en entier.
    const p = hero.it.paras[0];
    const ps = paraSize(hero.it, p, hero.it.fitted);
    const est = textWidth(p.runs.map((r) => r.t).join(''), ps, true, paraTrack(hero.it, p, ps), 'titre');
    const w = Math.min(FULL_W, est * 1.04 + 0.1);
    hero.it.x = (W - w) / 2;
    hero.it.w = w;
    hero.it.grad = true;
  }
  const lib = oneLine
    ? centerBox(c, { x: S.libelleX, w: S.libelleW, cy: S.libelleCy, paras: libParas, size: S.libelle[0], min: S.libelle[1], maxLines: 1, wt: 'semi', align: 'center', font: 'texte', lh: K.titre, name: 'Libellé', g: 'libelle' })
    : topBox(c, { x: S.libelleX, w: S.libelleW, capTop: S.libelleHautDeuxLignes, paras: libParas, size: S.libelle[0], min: S.libelle[1], maxTotal: 2, wt: 'semi', align: 'center', font: 'texte', lh: K.titre, balance: true, name: 'Libellé', g: 'libelle' });
  // Surtitre au corps du libellé, ligne de base à 0,25 cap du chiffre au-dessus de lui.
  c.kicker(hero.g, { x: M, w: FULL_W, align: 'center', size: S.surtitre, ecart: S.surtitreEcart });
  c.sourceLine({ y: lib.g.base + 0.2, x: S.libelleX, w: S.libelleW, g: 'libelle' });
};

// A6 : barres horizontales fines à bouts ronds ; libellé au départ (colonne alignée à droite),
// étiquette au bout ; soi en accent, l'autre en gris ; aucun axe chiffré.
R.A6 = (c) => {
  const S = STYLE.A6;
  c.accentUsed = true;
  const hasSur = !!(c.t.surtitre && String(c.t.surtitre).trim());
  const tParas = c.para(c.f('titre', 'titre du graphique'), { wt: 'semi', font: 'titre', g: 'titre' });
  const t = topBox(c, { x: M, w: FULL_W, capTop: hasSur ? S.titreHautSurtitre : S.titreHaut, paras: tParas, size: S.titre[0], min: S.titre[1], maxTotal: 2, wt: 'semi', align: 'center', font: 'titre', lh: K.titre, balance: true, name: 'Titre' });
  c.kicker(t.g, { x: M, w: FULL_W, align: 'center' });
  let bars = arr(c.t.barres).slice(0, 6);
  if (!bars.length) bars = [{ libelle: c.f('barres', 'barres'), valeur: 1 }];
  const Z = S.zone;
  const n = bars.length;
  const pitch = Z.h / n;
  const lab = clamp(Math.round(pitch * 72 * 0.36), S.etiquette[1], S.etiquette[0]);
  const labPt = scalePt(lab, 'texte');
  const vals = bars.map((b) => Math.max(0, Number(b.valeur) || 0));
  const maxV = Math.max.apply(null, vals) || 1;
  const showValues = c.t.afficher_valeurs === undefined ? ['valeurs', 'graduee', 'exigee'].includes(c.env.pub.graduation) : !!c.t.afficher_valeurs;
  const unite = c.t.unite ? ' ' + c.t.unite : '';
  const ets = bars.map((b) => {
    const et = b.etiquette !== undefined ? String(b.etiquette) : '';
    return et || (showValues ? String(b.valeur) + unite : '');
  });
  const textW = (t) => (t ? textWidth(shownText(c, t), labPt, true, trackFor('texte', labPt), 'texte') : 0);
  const etW = Math.max.apply(null, [0].concat(ets.map(textW)));
  // Libellés au départ des barres, alignés à droite dans leur colonne ; étiquettes au bout.
  const labels = bars.map((b) => str(b.libelle) || c.f('_', 'libellé'));
  const labW = Math.min(3.0, Math.max.apply(null, labels.map(textW)) + 0.05);
  const barX = Z.x + labW + 0.25;
  const maxLen = Math.max(1, Z.x + Z.w - barX - etW - 0.2);
  bars.forEach((b, i) => {
    const hl = !!b.mise_en_avant;
    const barCy = Z.y + pitch * (i + 0.5);
    const len = Math.max(S.barre * 2, vals[i] / maxV * maxLen);
    const room = Math.max(0.5, pitch);
    centerBox(c, { x: Z.x, w: labW, cy: barCy, room, text: labels[i], size: lab, min: S.etiquette[1], maxTotal: 2, wt: 'semi', color: hl ? c.P.fg : c.P.fg2, align: 'right', font: 'texte', lh: K.titre, balance: true, name: 'Libellé barre ' + (i + 1), g: 'barres', sub: i });
    c.round({ x: barX, y: barCy - S.barre / 2, w: len, h: S.barre, fill: hl ? c.P.accent : c.P.other, radius: S.barre / 2, name: 'Barre ' + (i + 1), g: 'barres', sub: i });
    if (ets[i]) centerBox(c, { x: barX + len + 0.15, w: etW + 0.3, cy: barCy, room, text: ets[i], size: lab, min: S.etiquette[1], noWrap: true, wt: 'semi', color: hl ? c.P.fg : c.P.fg2, align: 'left', font: 'texte', lh: K.titre, name: 'Valeur barre ' + (i + 1), g: 'barres', sub: i });
  });
  const axe = c.t.axe ? String(c.t.axe) : '';
  if (axe) topBox(c, { x: barX, w: Z.x + Z.w - barX, capTop: Z.y + Z.h + 0.2, text: axe, size: S.axe, min: 12, maxLines: 1, color: c.P.fg2, align: 'left', font: 'texte', lh: K.titre, name: 'Axe' });
  c.sourceLine();
};

// Titre secondaire d'une liste (A7, A8) : gris, regular, posé une cap au-dessus des lignes.
function listHeading(c, geo, o) {
  if (!c.t.titre) return geo;
  const hd = c.line({ text: c.t.titre, x: o.x, w: o.w, base: geo.capTop - geo.capH, size: scalePt(o.size, 'texte'), wt: 'regular', color: c.P.fg2, align: o.align, font: 'texte', name: 'Titre', g: 'titre' });
  return textGeom(hd);
}

R.A7 = (c) => {
  const S = STYLE.A7;
  const lines = arr(c.t.lignes);
  if (!lines.length) lines.push(c.f('lignes', 'lignes'));
  // Pas des lignes : 1,95 cap (3 à 6 lignes), 3,1 cap (2 lignes) ; l'interligne reste celui des
  // titres, le reste du pas va en espace après la ligne.
  const pitchK = c._pitchK || (lines.length === 2 ? K.liste2 : K.liste);
  const paras = listParas(c, lines, { color: c.P.fg, activeColor: c.P.fg, idleColor: c.P.fg2, font: 'titre', gapK: pitchK - K.titre });
  const stages = [{ size: S.lignes[0], min: S.lignes[1], maxLines: 1 }, { size: S.lignes[1], min: 24, maxLines: 2 }];
  const t = centerBox(c, { x: S.x, w: S.w, cy: S.cy, paras, stages, wt: 'semi', align: 'center', font: 'titre', lh: K.titre, name: 'Liste' });
  const geo = listHeading(c, t.g, { x: S.x, w: S.w, align: 'center', size: S.titre });
  c.kicker(geo, { x: S.x, w: S.w, align: 'center' });
  c.sourceLine();
};

// A8 : pictogrammes d'accent posés sur la ligne de base, texte aligné à gauche dans un bloc centré.
R.A8 = (c) => {
  const S = STYLE.A8;
  let lines = arr(c.t.lignes).slice(0, 7);
  if (!lines.length) lines = [c.f('lignes', 'lignes')];
  const coche = c.t.coche !== false;
  c.accentUsed = coche;
  const n = lines.length;
  const lineParas = lines.map((l, i) => c.para(l, { wt: 'semi', font: 'texte', g: 'lignes', sub: i }));
  const cap0 = capIn('texte', scalePt(S.lignes[0], 'texte'));
  const avail = S.largeurMax - cap0 * (S.picto + S.ecart);
  let size = null;
  lineParas.forEach((ps) => {
    const s = c.fit({ paras: ps, w: avail, size: S.lignes[0], min: S.lignes[1], maxLines: 1, wt: 'semi', font: 'texte' });
    if (s === null) c.warn('Ligne trop longue pour la liste à coches : raccourcissez-la (5 mots au plus).');
    const v = s === null ? scalePt(S.lignes[1], 'texte') : s;
    size = size === null ? v : Math.min(size, v);
  });
  const cap = capIn('texte', size);
  const pitch = K.liste * cap;
  const d = S.picto * cap;
  const gap = S.ecart * cap;
  const tw = Math.max.apply(null, lineParas.map((ps) => wrapInfo(ps.map((p) => p.runs.map((r) => r.t).join('')).join(' '), size, true, 99, trackFor('texte', size), 'texte').widest));
  const x0 = Math.max(M, (W - (d + gap + tw)) / 2);
  const cy0 = S.cy - (n - 1) * pitch / 2;
  lineParas.forEach((ps, i) => {
    const base = cy0 + i * pitch + cap / 2;
    const iy = base - d;
    // Une ligne qui n'est qu'un [À FOURNIR] garde sa case vide : une coche pleine la donnerait pour acquise.
    const aFournir = ps.some((p) => p.runs.some((r) => r.marker)) && ps.every((p) => p.runs.every((r) => r.marker || !r.t.trim()));
    if (coche && !aFournir) {
      c.ellipse({ x: x0, y: iy, w: d, h: d, fill: c.P.accent, name: 'Coche ' + (i + 1), g: 'lignes', sub: i });
      c.check({ cx: x0 + d / 2, cy: iy + d / 2, d, color: onAccent(c.P.accent, c.T.fondSombre), name: 'Coche ' + (i + 1) + ' trait', g: 'lignes', sub: i });
    } else {
      c.ellipse({ x: x0, y: iy, w: d, h: d, line: c.P.line, lineW: 1.5, name: 'Case vide ' + (i + 1), g: 'lignes', sub: i });
    }
    c.line({ paras: ps, x: x0 + d + gap, w: Math.min(tw + 0.5, W - (x0 + d + gap) - 0.2), base, size, wt: 'semi', align: 'left', font: 'texte', name: 'Ligne ' + (i + 1), g: 'lignes', sub: i });
  });
  const geo = listHeading(c, { capTop: cy0 - cap / 2, capH: cap, firstSize: size }, { x: x0, w: W - x0 - M, align: 'left', size: S.titre });
  c.kicker(geo, { x: x0, w: W - x0 - M, align: 'left' });
  c.sourceLine();
};

// A9 : l'objet sur 56 % de la largeur, à fond perdu ; l'affirmation centrée dans la colonne libre.
function sideBySide(c, defaultLabel) {
  const S = STYLE.A9;
  const right = c.t.cote === 'droite';
  const zx = right ? W - S.objet : 0;
  const col = right ? { x: W - S.colonne.x - S.colonne.w, w: S.colonne.w } : S.colonne;
  const box = { x: zx + 0.3, y: 0.3, w: S.objet - 0.6, h: H - 0.6 };
  const phBox = (kind) => {
    // Un écran schématique reste entier : coupé par le bord, sa colonne de navigation passait
    // pour une erreur de cadrage (un objet, lui, peut sortir du cadre).
    if (kind === 'interface' || kind === 'carte') return { x: right ? zx + 0.2 : 0.5, y: 0.72, w: S.objet - 0.7, h: 4.2 };
    if (kind === 'appareil') return { x: zx, y: 0.31, w: S.objet, h: 5.0 };
    if (kind === 'objet') return { x: zx + 0.4, y: 0.6, w: S.objet - 0.8, h: 4.4 };
    return box;
  };
  c.image(box, c.slide.image || { attendu: defaultLabel }, 'contain', 'Visuel', { g: 'visuel', phBox });
  const lines = arr(c.t.lignes).slice(0, 3);
  const align = lines.length ? 'left' : 'center';
  const paras = c.para(c.f('titre', 'titre'), { wt: 'semi', font: 'titre', g: 'titre', lh: K.objet });
  if (lines.length) paras[paras.length - 1].gap = S.ecartLignes;
  // Pas de 1,8 cap entre deux lignes ; une ligne qui passe sur deux garde un interligne serré.
  lines.forEach((l, i) => c.para(l, { pt: S.lignes, wt: 'regular', font: 'texte', color: c.P.fg2, g: 'lignes', sub: i, lh: K.objet, gapK: K.courte - K.objet + 0.25 }).forEach((p) => paras.push(p)));
  const t = centerBox(c, { x: col.x, w: col.w, cy: S.cy, paras, size: S.titre[0], min: S.titre[1], wt: 'semi', align, font: 'titre', lh: K.objet, balance: true, name: 'Texte' });
  c.kicker(t.g, { x: col.x, w: col.w, align });
  c.sourceLine();
}
R.A9 = (c) => sideBySide(c, c.lang === 'en' ? 'product or screen' : 'produit ou écran');
R.A11 = (c) => {
  c.warn('A11 (schéma à bloc surligné) est rendu comme A9 : visuel à gauche, légende à droite.');
  sideBySide(c, c.lang === 'en' ? 'diagram with the highlighted block' : 'schéma avec le bloc surligné');
};

// A10 : capture nue sur 85 % de la hauteur, coins arrondis, aucun texte ; un appareil sur 5,2 in.
R.A10 = (c) => {
  const S = STYLE.A10;
  const h = S.capture * H;
  const box = { x: 0.5, y: (H - h) / 2, w: W - 1.0, h };
  const phBox = (kind) => {
    if (kind === 'appareil') return { x: 0.5, y: (H - S.appareil) / 2, w: W - 1.0, h: S.appareil };
    if (kind === 'interface' || kind === 'carte') return { x: (W - h * 1.6) / 2, y: (H - h) / 2, w: h * 1.6, h };
    return box;
  };
  c.image(box, c.slide.image || { attendu: c.lang === 'en' ? 'screenshot' : 'capture d\'écran' }, 'contain', 'Écran', { g: 'visuel', radius: S.rayon, phBox });
  c.sourceLine();
};

R.A13 = (c) => {
  const S = STYLE.A13;
  c.image({ x: (W - S.w) / 2, y: (H - S.h) / 2, w: S.w, h: S.h }, c.slide.image || { attendu: c.lang === 'en' ? 'cut-out product' : 'produit détouré' }, 'contain', 'Produit', { g: 'visuel' });
  c.sourceLine();
};

function fullBleed(c, defaultLabel) {
  const S = STYLE.A18;
  c.image({ x: 0, y: 0, w: W, h: H }, c.slide.image || { attendu: defaultLabel }, 'cover', 'Photo', { kind: 'photo', full: true });
  const tw = FULL_W - (c.t.note ? 3.6 : 0);
  if (c.t.titre || c.t.surtitre) {
    c.rect({ x: 0, y: H - 1.7, w: W, h: 1.7, fill: '000000', transparency: 50, name: 'Voile' });
    const paras = c.para(c.f('titre', 'titre'), { wt: 'semi', font: 'titre', color: 'FFFFFF', g: 'titre' });
    const t = c.text({ x: M, y: H - 1.55, w: tw, h: 1.15, paras, size: S.titre[0], min: S.titre[1], wt: 'semi', align: 'left', valign: 'bottom', color: 'FFFFFF', font: 'titre', lh: K.titre, name: 'Titre' });
    c.kicker(textGeom(t), { x: M, w: tw, align: 'left', color: c.accentWords ? 'E8E8E8' : undefined });
  }
  if (c.t.note) {
    const bw = 3.4;
    c.round({ x: W - M - bw, y: H - 0.98, w: bw, h: 0.52, fill: '000000', transparency: 45, radius: 0.08, name: 'Cartouche', g: 'note' });
    c.text({ x: W - M - bw + 0.14, y: H - 0.98, w: bw - 0.28, h: 0.52, text: c.t.note, size: S.note[0], min: S.note[1], color: 'FFFFFF', align: 'left', valign: 'middle', font: 'texte', lh: K.titre, name: 'Note', g: 'note' });
  }
  if (c.sourceOnSlide) {
    c.rect({ x: 0, y: H - 0.42, w: W, h: 0.42, fill: '000000', transparency: 45, name: 'Voile source' });
    c.text({ x: M, y: H - 0.38, w: FULL_W, h: 0.34, text: c.sourceDisplay, size: 10, min: 9, color: 'FFFFFF', align: 'left', valign: 'middle', font: 'texte', lh: K.titre, name: 'Source' });
    c.sourceDone = true;
  }
}
R.A12 = (c) => fullBleed(c, c.lang === 'en' ? 'exploded or inside view' : 'vue éclatée ou intérieure');
R.A18 = (c) => fullBleed(c, c.lang === 'en' ? 'full-bleed photo' : 'photo plein cadre');
['A22', 'A23', 'A24', 'A25'].forEach((k) => {
  R[k] = (c) => {
    c.warn(k + ' est un plan de scène (vidéo) : en slide, il est rendu comme une photo plein cadre.');
    fullBleed(c, c.lang === 'en' ? 'photo of the scene' : 'photo de la scène');
  };
});

// A14 : bento jusqu'aux bords (marge et gouttière de 0,09 in), même rayon pour toutes les tuiles,
// tuile centrale de 3,9 × 2,25 in en accent, tuiles en aplat sans bordure ni ombre.
R.A14 = (c) => {
  const S = STYLE.A14;
  let tiles = arr(c.t.tuiles).slice(0, 8);
  if (arr(c.t.tuiles).length > 8) c.warn('Bento : 8 tuiles au plus autour du titre ; les suivantes sont ignorées.');
  while (tiles.length < 4) tiles.push({ titre: c.lang === 'en' ? '[TO PROVIDE: tile]' : '[À FOURNIR : tuile]' });
  const n = tiles.length;
  const m = S.marge;
  const g = S.gouttiere;
  const reserve = c.sourceOnSlide ? 0.32 : 0;
  const GW = W - 2 * m;
  const GH = H - 2 * m - reserve;
  const side = (GW - 2 * g - S.centre.w) / 2;
  const sideH = (GH - 2 * g - S.centre.h) / 2;
  const cw = [side, S.centre.w, side];
  const rh = [sideH, S.centre.h, sideH];
  const cell = (col, row, cs, rs) => {
    cs = cs || 1;
    rs = rs || 1;
    let x = m;
    for (let i = 0; i < col; i++) x += cw[i] + g;
    let y = m;
    for (let j = 0; j < row; j++) y += rh[j] + g;
    let w = -g;
    for (let i = col; i < col + cs; i++) w += cw[i] + g;
    let h = -g;
    for (let j = row; j < row + rs; j++) h += rh[j] + g;
    return { x, y, w, h };
  };
  const LAYOUTS = {
    8: [[0, 0], [1, 0], [2, 0], [0, 1], [2, 1], [0, 2], [1, 2], [2, 2]],
    7: [[0, 0, 1, 2], [1, 0], [2, 0], [2, 1], [0, 2], [1, 2], [2, 2]],
    6: [[0, 0, 1, 2], [1, 0], [2, 0, 1, 2], [0, 2], [1, 2], [2, 2]],
    5: [[0, 0, 1, 2], [1, 0], [2, 0, 1, 2], [0, 2, 2, 1], [2, 2]],
    4: [[0, 0, 1, 3], [1, 0], [2, 0, 1, 3], [1, 2]]
  };
  const rad = (b) => Math.min(S.rayon, 0.25 * Math.min(b.w, b.h));
  const center = cell(1, 1);
  const onAcc = onAccent(c.P.accent, c.T.fondSombre);
  c.round({ x: center.x, y: center.y, w: center.w, h: center.h, fill: c.P.accent, radius: rad(center), name: 'Tuile centrale', g: 'centre' });
  const cParas = c.para(c.f('titre', 'nom'), { wt: 'semi', font: 'titre', color: onAcc, g: 'centre' });
  const ct = centerBox(c, { x: center.x + 0.2, w: center.w - 0.4, cy: center.y + center.h / 2, room: center.h - 0.3, paras: cParas, size: S.nom[0], min: S.nom[1], maxTotal: 2, wt: 'semi', align: 'center', color: onAcc, font: 'titre', lh: K.titre, balance: true, name: 'Titre central', g: 'centre' });
  c.kicker(ct.g, { x: center.x + 0.2, w: center.w - 0.4, align: 'center', color: onAcc, wt: 'semi', g: 'centre' });
  LAYOUTS[n].forEach((spec, i) => {
    const b = cell(spec[0], spec[1], spec[2], spec[3]);
    const tile = typeof tiles[i] === 'string' ? { titre: tiles[i] } : (tiles[i] || {});
    c.round({ x: b.x, y: b.y, w: b.w, h: b.h, fill: c.P.surface, radius: rad(b), name: 'Tuile ' + (i + 1), g: 'tuiles', sub: i });
    const pad = S.pad;
    let area = { x: b.x + pad, y: b.y + pad, w: b.w - 2 * pad, h: b.h - 2 * pad };
    const paras = [];
    let size = S.titre;
    const label = (s) => c.para(s, { pt: S.libelle, wt: 'regular', font: 'texte', color: c.P.fg2 }).forEach((p) => paras.push(p));
    if (tile.image) {
      const ih = area.h * 0.62;
      c.image({ x: area.x, y: area.y, w: area.w, h: ih }, tile.image, 'contain', 'Visuel tuile ' + (i + 1), { g: 'tuiles', sub: i });
      area = { x: area.x, y: area.y + ih + 0.06, w: area.w, h: area.h - ih - 0.06 };
    }
    if (tile.chiffre) {
      size = S.chiffre;
      c.para(tile.chiffre, { wt: 'semi', font: 'titre', color: c.P.accentTxt, gap: 0.04 }).forEach((p) => paras.push(p));
      if (tile.titre) label(tile.titre);
      if (tile.texte) label(tile.texte);
    } else if (tile.image) {
      // Sous une image, le titre devient un libellé : il se regarde, il ne se lit pas.
      size = [S.libelle, 11];
      label(tile.titre || (c.lang === 'en' ? '[TO PROVIDE: tile]' : '[À FOURNIR : tuile]'));
      if (tile.texte) label(tile.texte);
    } else {
      c.para(tile.titre || (c.lang === 'en' ? '[TO PROVIDE: tile]' : '[À FOURNIR : tuile]'), { wt: 'semi', font: 'texte', color: c.P.fg, gap: tile.texte ? 0.06 : 0 }).forEach((p) => paras.push(p));
      if (tile.texte) label(tile.texte);
    }
    c.text({ x: area.x, y: area.y, w: area.w, h: area.h, paras, size: size[0], min: size[1], maxTotal: 4, wt: 'semi', align: 'left', valign: 'bottom', font: 'texte', lh: K.titre, balance: !tile.chiffre, name: 'Texte tuile ' + (i + 1), g: 'tuiles', sub: i });
  });
  c.sourceLine({ y: H - m - reserve + 0.05, h: 0.3 });
};

R.A15 = (c) => {
  let items = arr(c.t.elements);
  if (!items.length) items = [c.f('elements', 'éléments du mur')];
  const cols = 6;
  const rows = 5;
  const tw = 1.72;
  const th = 1.22;
  const g = 0.12;
  const x0 = -0.38;
  const y0 = -0.22;
  let k = 0;
  for (let r = 0; r < rows; r++) {
    for (let col = 0; col < cols; col++) {
      const x = x0 + col * (tw + g) + (r % 2 ? 0.45 : 0);
      const y = y0 + r * (th + g);
      const it = items[k % items.length];
      k += 1;
      const label = typeof it === 'string' ? it : (it.titre || '');
      if (it && typeof it === 'object' && it.image) {
        c.image({ x, y, w: tw, h: th }, it.image, 'cover', 'Mur ' + k, { kind: 'tuile' });
      } else {
        c.round({ x, y, w: tw, h: th, fill: c.P.surface, radius: 0.12, name: 'Mur ' + k });
      }
      if (label) c.text({ x: x + 0.12, y: y + th - 0.5, w: tw - 0.24, h: 0.4, text: label, size: STYLE.A15.libelle[0], min: STYLE.A15.libelle[1], color: c.P.fg2, align: 'left', valign: 'bottom', font: 'texte', lh: K.titre, name: 'Mur libellé ' + k });
    }
  }
};

// A16 : logos monochromes hauts de 0,56 in au plus, rangées tous les 1,1 in, grille de 8 in centrée.
R.A16 = (c) => {
  const S = STYLE.A16;
  let logos = arr(c.t.logos).slice(0, 15);
  if (!logos.length) logos = [{ nom: c.f('logos', 'logos') }];
  const n = logos.length;
  const rows = Math.ceil(n / 5);
  const cols = Math.ceil(n / rows);
  const cellW = S.largeur / cols;
  const head = !!c.t.titre;
  const cy = 2.81 + (head ? 0.25 : 0);
  const firstCy = cy - (rows - 1) * S.rangee / 2;
  logos.forEach((lg, i) => {
    const logo = typeof lg === 'string' ? { nom: lg } : lg;
    const r = Math.floor(i / cols);
    const col = i % cols;
    const inRow = Math.min(cols, n - r * cols);
    const x = (W - S.largeur) / 2 + (cols - inRow) * cellW / 2 + col * cellW;
    const box = { x: x + 0.2, y: firstCy + r * S.rangee - S.logoH / 2, w: cellW - 0.4, h: S.logoH };
    c.image(box, logo.image ? { chemin: logo.image, attendu: logo.nom } : { attendu: logo.nom || 'logo' }, 'contain', 'Logo ' + (i + 1), { kind: 'logo', g: 'logos', sub: i });
  });
  const topCap = firstCy - S.logoH / 2;
  let geo = { capTop: topCap, capH: capIn('texte', scalePt(S.titre, 'texte')) * 1.4, firstSize: scalePt(S.titre, 'texte') };
  if (head) {
    const hd = c.line({ text: c.t.titre, x: M, w: FULL_W, base: topCap - 0.5, size: scalePt(S.titre, 'texte'), wt: 'regular', color: c.P.fg2, align: 'center', font: 'texte', name: 'Titre', g: 'titre' });
    geo = textGeom(hd);
  }
  c.kicker(geo, { x: M, w: FULL_W, align: 'center' });
  c.sourceLine();
};

// A17 : citation alignée à gauche à 0,92 in, source grise 0,53 in sous la dernière ligne de base,
// bloc centré sur le milieu.
R.A17 = (c) => {
  const S = STYLE.A17;
  let q = c.f('citation', 'citation').trim();
  if (!/^[«"“]/.test(q) && !hasFournir(q)) q = c.lang === 'fr' ? '« ' + q + ' »' : '“' + q + '”';
  const qt = topBox(c, { x: S.x, w: S.w, capTop: 0, paras: c.para(q, { wt: 'semi', font: 'titre', g: 'citation' }), size: S.citation[0], min: S.citation[1], maxTotal: 4, wt: 'semi', align: 'left', font: 'titre', lh: K.citation, balance: true, name: 'Citation' });
  const at = topBox(c, { x: S.x, w: S.w, capTop: 0, text: c.f('auteur', 'auteur'), size: S.auteur[0], min: S.auteur[1], maxTotal: 2, color: c.P.fg2, align: 'left', font: 'texte', lh: K.titre, balance: true, name: 'Auteur', g: 'auteur' });
  const total = (qt.g.base - qt.g.capTop) + S.ecart + (at.g.base - at.g.capTop);
  const q2 = placeTop(qt.it, S.cy - total / 2);
  placeTop(at.it, q2.g.base + S.ecart);
  c.kicker(q2.g, { x: S.x, w: S.w, align: 'left' });
  c.sourceLine({ x: S.x, w: S.w, align: 'left' });
};

// A19 : une offre en pile (nom, petit « À partir de », prix, précision), posée à partir du haut
// des capitales du nom ; écarts mesurés. Retourne les éléments créés et la géométrie du nom.
function offerStack(c, o, x, w, align, capTop, sub, ecartNom, big) {
  const S = Object.assign({}, STYLE.A19, big ? STYLE.A19.sansVisuel : {});
  const start = c.items.length;
  const name = topBox(c, { x, w, capTop, paras: c.para(str(o.nom) || c.f('_', 'nom'), { wt: 'semi', font: 'titre', g: 'nom', sub }), size: S.nom[0], min: S.nom[1], maxTotal: 2, wt: 'semi', align, font: 'titre', lh: K.titre, balance: true, name: 'Nom', g: 'nom', sub });
  let base = name.g.base;
  let ecart = ecartNom;
  if (o.mention) {
    const m = topBox(c, { x, w, capTop: base + ecart, text: o.mention, size: S.petit, min: 12, maxLines: 1, color: c.P.fg2, align, font: 'texte', lh: K.titre, name: 'Mention', g: 'prix', sub });
    base = m.g.base;
    ecart = S.ecartPetit;
  }
  const p = topBox(c, { x, w, capTop: base + ecart, paras: c.para(str(o.prix) || c.f('_', 'prix'), { wt: 'semi', font: 'titre', g: 'prix', sub }), size: S.prix[0], min: S.prix[1], maxLines: 1, wt: 'semi', align, font: 'titre', lh: K.titre, name: 'Prix', g: 'prix', sub });
  base = p.g.base;
  if (o.note) base = topBox(c, { x, w, capTop: base + S.ecartPetit, text: o.note, size: S.petit, min: 12, maxTotal: 2, color: c.P.fg2, align, font: 'texte', lh: K.titre, name: 'Précision', g: 'prix', sub }).g.base;
  return { items: c.items.slice(start), nameItem: name.it, capTop, base, h: base - capTop };
}
// Prix seul d'un service : le prix au corps du chiffre héros (A5), le nom en haut, la période dessous.
function priceHero(c, o) {
  const S = STYLE.A19;
  const A5 = STYLE.A5;
  const hero = centerBox(c, { x: M, w: FULL_W, cy: A5.cy, paras: c.para(str(o.prix) || c.f('_', 'prix'), { wt: 'semi', font: 'titre', g: 'prix' }), stages: [{ w: A5.largeur, size: S.heros[0], min: S.heros[1], maxLines: 1 }], noWrap: true, wt: 'semi', align: 'center', font: 'titre', lh: K.titre, name: 'Prix', g: 'prix' });
  let above = hero.g;
  let ecart = A5.surtitreEcart * hero.g.capH;
  if (o.mention) {
    const m = c.line({ text: o.mention, x: M, w: FULL_W, base: hero.g.capTop - ecart, size: scalePt(A5.surtitre, 'texte'), wt: 'regular', color: c.P.fg2, align: 'center', font: 'texte', name: 'Mention', g: 'prix' });
    above = textGeom(m);
    ecart = S.ecartNomHaut;
  }
  const nm = topBox(c, { x: M, w: FULL_W, capTop: 0, paras: c.para(str(o.nom) || c.f('_', 'nom'), { wt: 'semi', font: 'titre', g: 'nom' }), size: S.nom[0], min: S.nom[1], maxTotal: 2, wt: 'semi', align: 'center', font: 'titre', lh: K.titre, balance: true, name: 'Nom', g: 'nom' });
  const g = placeTop(nm.it, above.capTop - ecart - (nm.g.base - nm.g.capTop)).g;
  if (o.note) centerBox(c, { x: A5.libelleX, w: A5.libelleW, cy: A5.libelleCy, text: o.note, size: S.periode, min: 14, maxLines: 1, color: c.P.fg2, align: 'center', font: 'texte', lh: K.titre, name: 'Précision', g: 'prix' });
  return g;
}
R.A19 = (c) => {
  const S = STYLE.A19;
  let offres = arr(c.t.offres).slice(0, 2);
  if (!offres.length) offres = [{ nom: c.t.titre, mention: c.t.mention, prix: c.t.prix, note: c.t.note }];
  const img = c.slide.image;
  const spec = c.imageSpec(img);
  const info = spec && spec.chemin ? imageInfo(path.resolve(c.env.deckDir, spec.chemin)) : null;
  if (offres.length === 1 && !img) {
    c.kicker(priceHero(c, offres[0]), { x: M, w: FULL_W, align: 'center' });
  } else if (offres.length === 1 && info && info.w / info.h >= 1.3) {
    // « Haut » : le nom en haut, l'objet dessous, sur 6 in au plus.
    const st = offerStack(c, offres[0], M, FULL_W, 'center', S.nomHaut, undefined, S.ecartNomHaut);
    const top = Math.max(S.objetHaut.y, st.base + 0.3);
    c.image({ x: (W - S.objetHaut.w) / 2, y: top, w: S.objetHaut.w, h: S.objetHaut.bas - top }, img, 'contain', 'Produit', { g: 'visuel' });
    c.kicker(textGeom(st.nameItem), { x: M, w: FULL_W, align: 'center' });
  } else if (img || offres.length === 1) {
    // « Colonne droite » : l'objet à gauche, les offres empilées et centrées à 7 in.
    // L'objet tient 91 % de la hauteur, centré vers 25 % de la largeur ; sa largeur suit ses
    // proportions (de 2,8 à 4,2 in), pour qu'un objet trapu remplisse sa moitié comme un objet élancé.
    const O = S.objetColonne;
    const ow = clamp(info ? O.h * info.w / info.h : 3.7, O.w, 4.2);
    c.image({ x: O.cx - ow / 2, y: O.y, w: ow, h: O.h }, img, 'contain', 'Produit', { g: 'visuel' });
    const x = S.colonne.cx - S.colonne.w / 2;
    const stacks = [];
    let cap = 0;
    offres.forEach((o, i) => {
      const st = offerStack(c, o, x, S.colonne.w, 'center', cap, offres.length > 1 ? i : undefined, S.ecartNomColonne);
      stacks.push(st);
      cap = st.base + S.ecartOffres;
    });
    const total = stacks[stacks.length - 1].base;
    stacks.forEach((st) => shiftItems(st.items, S.cy - total / 2));
    c.kicker(textGeom(stacks[0].nameItem), { x, w: S.colonne.w, align: 'center' });
  } else {
    // Deux offres sans visuel : côte à côte, alignées sur leur nom, le bloc centré sur le milieu.
    const stacks = offres.map((o, i) => offerStack(c, o, S.deuxColonnes[i] - S.colonne.w / 2, S.colonne.w, 'center', 0, i, S.ecartNomColonne, true));
    const total = Math.max.apply(null, stacks.map((st) => st.base));
    stacks.forEach((st) => shiftItems(st.items, S.cy - total / 2));
    c.kicker(textGeom(stacks[0].nameItem), { x: M, w: FULL_W, align: 'center', ecart: 1.4 });
  }
  c.sourceLine();
};

// A20 : petit libellé gris en haut, le mot ou la date dessous, le visuel calé en bas ; sans visuel,
// libellé de 24 pt et mot au corps de la carte-titre, le bloc centré sur le milieu.
R.A20 = (c) => {
  const S = STYLE.A20;
  const img = c.slide.image;
  const label = c.t.libelle ? String(c.t.libelle) : '';
  const motParas = c.para(c.f('titre', 'date'), { wt: 'semi', font: 'titre', g: 'date' });
  let geo;
  if (img) {
    let base = null;
    if (label) {
      const l = topBox(c, { x: M, w: FULL_W, capTop: S.libelleHaut, text: label, size: S.libelle, min: 12, maxLines: 1, color: c.P.fg2, align: 'center', font: 'texte', lh: K.titre, name: 'Libellé', g: 'libelle' });
      base = l.g.base;
      geo = l.g;
    }
    const m = topBox(c, { x: M, w: FULL_W, capTop: base === null ? S.libelleHaut : base + S.ecart, paras: motParas, size: S.mot[0], min: S.mot[1], maxTotal: 2, wt: 'semi', align: 'center', font: 'titre', lh: K.titre, balance: true, name: 'Date', g: 'date' });
    if (!geo) geo = m.g;
    const V = S.visuel;
    const top = Math.max(V.y, m.g.base + 0.3);
    c.image({ x: (W - V.w) / 2, y: top, w: V.w, h: V.bas - top }, img, 'contain', 'Produit', { g: 'visuel', alignY: 'bottom', phBox: () => ({ x: (W - 6.4) / 2, y: top + 0.1, w: 6.4, h: V.bas - top - 0.1 }) });
  } else {
    const A = STYLE.A1;
    const m = topBox(c, { x: A.x, w: A.w, capTop: 0, paras: motParas, stages: bigStages(A.corps[0], motParas.length > 1), wt: 'semi', align: 'center', font: 'titre', lh: K.titre, balance: true, name: 'Date', g: 'date' });
    const l = label ? topBox(c, { x: M, w: FULL_W, capTop: 0, text: label, size: S.seul.libelle, min: 16, maxLines: 1, color: c.P.fg2, align: 'center', font: 'texte', lh: K.titre, name: 'Libellé', g: 'libelle' }) : null;
    const gap = l ? S.seul.ecart * m.g.capH : 0;
    const lh = l ? l.g.base - l.g.capTop : 0;
    const top = A.cy - (lh + gap + (m.g.base - m.g.capTop)) / 2;
    if (l) {
      geo = placeTop(l.it, top).g;
      placeTop(m.it, geo.base + gap);
    } else {
      geo = placeTop(m.it, top).g;
    }
  }
  c.kicker(geo, { x: M, w: FULL_W, align: 'center', ecart: 0.9 });
  c.sourceLine();
};

// A21 : nom et fonction au même corps, en bas à gauche, en blanc sur l'image, sans fond ni ombre.
R.A21 = (c) => {
  const S = STYLE.A21;
  const who = c.env.people[c.t.intervenant || c.slide.intervenant] || {};
  const nom = c.t.nom || who.nom || c.f('nom', 'nom');
  const fonction = c.t.fonction || who.role || c.f('fonction', 'fonction');
  const img = c.slide.image;
  if (img) c.image({ x: 0, y: 0, w: W, h: H }, img, 'cover', 'Photo', { kind: 'photo', full: true });
  const size = scalePt(S.corps, 'texte');
  c.line({ text: nom, x: S.x, w: 6, base: S.bases[0], size, wt: 'semi', color: img ? 'FFFFFF' : c.P.fg, align: 'left', font: 'texte', name: 'Nom', g: 'nom' });
  c.line({ text: fonction, x: S.x, w: 6, base: S.bases[1], size, wt: 'regular', color: img ? 'FFFFFF' : c.P.fg2, align: 'left', font: 'texte', name: 'Fonction', g: 'fonction' });
};

// AF : slide entière à fournir. Avec archetype_prevu, la slide est rendue dans cet archétype
// (les champs manquants deviennent des [À FOURNIR] courts) ; sinon, un libellé centré.
R.AF = (c) => {
  let label = str(c.t.titre || c.t.libelle).trim();
  if (!label) label = c.lang === 'en' ? '[TO PROVIDE: ' + (c.hint() || c.L.content) + ']' : '[À FOURNIR : ' + (c.hint() || c.L.content) + ']';
  else if (!hasFournir(label)) label = c.lang === 'en' ? '[TO PROVIDE: ' + label + ']' : '[À FOURNIR : ' + label + ']';
  const S = STYLE.A4;
  const t = centerBox(c, { x: S.x, w: S.w, cy: S.cy, paras: c.para(label, { wt: 'semi', font: 'titre', g: 'titre' }), size: STYLE.AF.titre[0], min: STYLE.AF.titre[1], wt: 'semi', align: 'center', font: 'titre', lh: K.titre, balance: true, name: 'Titre' });
  c.kicker(t.g, { x: S.x, w: S.w, align: 'center' });
};

R.SOURCES = (c) => {
  const S = STYLE.SOURCES;
  topBox(c, { x: M, w: FULL_W, capTop: 0.6, text: c.L.sourcesTitle, size: S.titre[0], min: S.titre[1], maxLines: 1, wt: 'semi', color: c.P.fg2, align: 'left', font: 'texte', lh: K.titre, name: 'Titre' });
  const paras = [];
  c.env.collectedSources.forEach((s) => {
    const line = s.n + '. ' + s.text + ' (' + c.L.slideWord + (s.slides.length > 1 ? 's ' : ' ') + s.slides.join(', ') + ')';
    c.para(line, { color: c.P.fg2, gap: 0.1 }).forEach((p) => paras.push(p));
  });
  c.text({ x: M, y: 1.25, w: FULL_W, h: H - 1.25 - 0.5, paras, size: S.liste[0], min: S.liste[1], align: 'left', valign: 'top', font: 'texte', lh: K.titre, name: 'Sources' });
};

// [À FOURNIR] en grand corps (au-dessus de STYLE.marqueur.seuil) : le soulignement de la police
// deviendrait une rangée de gros points. On le retire du texte (r.ul = false) et on pose, juste
// avant la zone de texte (donc dessous), un filet pointillé d'épaisseur fixe sous la portion du
// marqueur. Seulement pour un paragraphe d'une ligne ; au-delà, le soulignement reste celui du texte.
function markerRules(c) {
  const MK = STYLE.marqueur;
  const inserts = [];
  c.items.forEach((it, idx) => {
    if (it.k !== 'text' || !it.paras.some((p) => p.runs.some((r) => r.marker))) return;
    const geo = textGeom(it);
    let li = 0;
    it.paras.forEach((p) => {
      const ps = paraSize(it, p, it.fitted);
      const n = it.noWrap ? 1 : paraInfo(it, p, ps).lines;
      const line = geo.lines[li];
      li += n;
      if (n !== 1 || !line || ps < MK.seuil || !p.runs.some((r) => r.marker)) return;
      const hv = heavy(paraWeight(it, p));
      const tr = paraTrack(it, p, ps);
      const role = roleOf(it, p);
      // Position et largeur estimées pour chaque sortie avec la police qu'elle affiche : le .pptx avec
      // la police écrite (cle), l'aperçu avec celle qu'il montre ici (ici, le repli si elle manque).
      // k corrige la table des chasses, mesuré dans l'aperçu (rapport réel / estimé).
      const k = hv ? MK.chasse[0] : MK.chasse[1];
      const F = FONT[role] || FONT.texte;
      const facteur = (key) => (STYLE.polices[key] || STYLE.polices.defaut).largeur;
      const align = p.align || it.align;
      const spans = (wf) => {
        const wOf = (s) => textWidth(s, ps, hv, tr, role, wf) * k;
        const lw = wOf(p.runs.map((r) => r.t).join(''));
        const x0 = align === 'center' ? it.x + (it.w - lw) / 2 : align === 'right' ? it.x + it.w - lw : it.x;
        const out = [];
        let acc = 0;
        p.runs.forEach((r) => {
          const rw = wOf(r.t);
          if (r.marker) {
            const lead = wOf(r.t.match(/^\s*/)[0]);
            const trail = wOf(r.t.match(/\s*$/)[0]);
            out.push({ x: x0 + acc + lead, w: Math.max(0.05, rw - lead - trail) });
          }
          acc += rw;
        });
        return out;
      };
      const ecrite = spans(facteur(F.cle));
      const vue = spans(facteur(F.ici || F.cle));
      const thick = MK.epaisseur / 72;
      const y = line.c + line.cap / 2 + clamp(ps * MK.ecart, MK.ecartPt[0], MK.ecartPt[1]) / 72;
      let mi = 0;
      p.runs.forEach((r) => {
        if (r.marker) {
          r.ul = false;
          const a = ecrite[mi];
          const b = vue[mi];
          mi += 1;
          inserts.push({ before: idx, it: { k: 'rule', x: a.x, y: y - thick / 2, w: a.w, xh: b.x, wh: b.w, h: thick, pt: MK.epaisseur, color: c.P.accentTxt, name: 'Soulignement', g: p.g !== undefined ? p.g : it.g, sub: p.sub !== undefined ? p.sub : it.sub, ph: it.ph } });
        }
      });
    });
  });
  inserts.sort((a, b) => b.before - a.before).forEach((ins) => {
    const n = (c.names[ins.it.name] || 0) + 1;
    c.names[ins.it.name] = n;
    if (n > 1) ins.it.name += ' ' + n;
    if (ins.it.ph === undefined) delete ins.it.ph;
    c.items.splice(ins.before, 0, ins.it);
  });
}

// ---------------------------------------------------------------------------
// Composition d'une slide (fond + archétype + logo)
// ---------------------------------------------------------------------------
function composeSlide(deck, slide, index, env) {
  const c = new SlideCtx(deck, slide, index, env);
  let fn = R[c.arch];
  // Variante de composition (fiches design) : sans variante, le rendu d'origine de l'archétype.
  const hit = slide.variante || VARIANTE_DEFAUT[c.arch] ? resolveVariant(c.arch, slide.variante) : null;
  if (hit && hit.fn) {
    c.variante = hit.key;
    c.renderArch = hit.arch;
    fn = hit.fn;
  } else if (slide.variante) {
    const known = variantNames(c.arch);
    c.warn('Variante « ' + slide.variante + ' » inconnue pour ' + c.arch + (known.length ? ' (variantes : ' + known.join(', ') + ')' : '') + ' : rendu par défaut de l\'archétype.');
  }
  if (c.arch === 'AF') {
    const prevu = String(c.t.archetype_prevu || slide.archetype_prevu || '').toUpperCase();
    if (prevu && prevu !== 'AF' && R[prevu]) {
      c.renderArch = prevu;
      fn = R[prevu];
    }
  }
  // Avec une variante, le fond ne vient que d'image_fond (slide.image est son contenu), et rien
  // pour une variante qui pose déjà sa photo à fond perdu.
  if (c.fond === 'image' && !FULL_BLEED.has(c.renderArch) && !(c.variante && OWN_PHOTO.has(c.variante))) {
    const bgSpec = slide.image_fond || (!CONTENT_IMAGE.has(c.renderArch) && !c.variante ? slide.image : null);
    if (bgSpec) {
      c.image({ x: 0, y: 0, w: W, h: H }, bgSpec, 'cover', 'Image de fond', { kind: 'photo', full: true });
      const voile = slide.voile === undefined ? 45 : Math.max(0, Math.min(100, Number(slide.voile) || 0));
      if (voile > 0) c.rect({ x: 0, y: 0, w: W, h: H, fill: '000000', transparency: 100 - voile, name: 'Voile' });
    } else {
      c.warn('Fond « image » sans image_fond : fond sombre utilisé.');
    }
  }
  if (fn) {
    fn(c);
  } else {
    c.warn('Archétype inconnu « ' + slide.archetype + ' » : libellé [À FOURNIR] à la place.');
    c.renderArch = 'AF';
    c.t = { titre: c.L.content };
    R.AF(c);
  }
  markerRules(c);
  if (slide.logo && env.T.logo) {
    const abs = path.resolve(env.deckDir, env.T.logo);
    const info = imageInfo(abs);
    if (info) {
      const s = Math.min(1.2 / info.w, 0.38 / info.h);
      c.add({ k: 'image', x: W - 0.45 - info.w * s, y: H - 0.42 - info.h * s, w: info.w * s, h: info.h * s, abs, info, mode: 'fill', name: 'Logo', alt: 'logo' });
    } else c.warn('Logo « ' + env.T.logo + ' » introuvable : non affiché.');
  }
  return c;
}

// ---------------------------------------------------------------------------
// Apparitions : slide.build (phrases pour l'orateur) → animations d'entrée en fondu, au clic.
// Chaque archétype a ses groupes, dans l'ordre de lecture. Une phrase qui nomme un groupe
// (« le chiffre », « les trois lignes une à une », « la tuile centrale ») le fait apparaître ;
// une phrase qui dit « déjà à l'écran » le laisse affiché ; « ensemble » regroupe ; « puis »
// sépare ; « suit » enchaîne sans clic. Un groupe jamais nommé apparaît avec le groupe qui
// le précède, ou reste affiché s'il vient en premier. Sans build, rien n'est animé.
// ---------------------------------------------------------------------------
const KW = {
  surtitre: /\b(?:surtitres?|sur-titres?|kickers?|eyebrows?|overlines?)\b/,
  titre: /\b(?:titres?|titles?|noms?|names?|phrases?|sentences?|mots?|words?|headings?|headlines?|accroches?|slogans?|statements?|messages?|claims?)\b/,
  ligne: /\b(?:lignes?|lines?)\b/,
  lignes: /\b(?:lignes?|lines?|points?|items?|elements?|coches?|cases?|checks?|ticks?|checkmarks?|garanties?|atouts?|benefices?|bullets?|rows?|etapes?|steps?)\b/,
  chiffre: /\b(?:chiffres?|nombres?|numbers?|figures?|valeurs?|values?|stats?|statistiques?|pourcentages?|percentages?|gains?)\b/,
  libelle: /\b(?:libelles?|labels?|legendes?|captions?|sous-titres?|subtitles?|explications?|textes?|texts?|phrases?|sentences?)\b/,
  visuel: /\b(?:captures?|ecrans?|images?|visuels?|photos?|produits?|boitiers?|objets?|schemas?|illustrations?|screens?|screenshots?|visuals?|pictures?|products?|devices?|appareils?|maquettes?|mockups?|icones?|icons?|logos?|diagrammes?|diagrams?|interfaces?|cartes?|maps?)\b/,
  barres: /\b(?:barres?|bars?|colonnes?|columns?)\b/,
  tuiles: /\b(?:tuiles?|tiles?|blocs?|blocks?|cartes?|cards?|cases?)\b/,
  centre: /\b(?:tuile centrale|central tile|centre tile|center tile|centre|center|centrale|central|middle)\b/,
  prix: /\b(?:prix|prices?|tarifs?|montants?|amounts?|pricing)\b/,
  nom: /\b(?:noms?|names?|offres?|offers?|titres?|titles?|formules?|plans?)\b/,
  date: /\b(?:dates?|jours?|days?|mois|months?|titres?|titles?|mots?|words?)\b/,
  citation: /\b(?:citations?|quotes?|quotations?|temoignages?|testimonials?|phrases?|sentences?)\b/,
  auteur: /\b(?:auteurs?|authors?|signatures?|attributions?)\b/,
  logos: /\b(?:logos?|marques?|brands?|partenaires?|partners?|clients?)\b/,
  note: /\b(?:notes?|cartouches?|mentions?|legendes?|captions?)\b/,
  fonction: /\b(?:fonctions?|roles?|postes?|jobs?)\b/
};
const BRX = {
  none: /\b(?:aucune apparition|pas d'apparition|sans apparition|tout (?:est )?a l'ecran d'un bloc|no build|no animation|all at once on screen)\b/,
  seq: /\b(?:puis|ensuite|then|followed by|apres quoi)\b/,
  stat: /\bdeja\b|\balready\b|des l'arrivee|des le debut|avant (?:la prise de parole|de parler|qu'(?:il|elle) parle)|before (?:speaking|the speaker|anyone speaks)|from the start/,
  keep: /\b(?:reste|restent|stays?|remains?)\b/,
  together: /\b(?:ensemble|en meme temps|simultanement|d'un coup|together|at once|at the same time|simultaneously)\b/,
  after: /\b(?:suit|suivent|juste apres|une seconde apres|aussitot apres|follows?|right after|a second later|shortly after)\b/,
  appear: /(?:apparai|apparu|s'affiche|affichent|arrive|s'allume|allument|se pose|se posent|surgit|appears?|shows? up|comes? in|lights? up|fades? in|pops? in|builds? in)/,
  plural: /\b(?:toutes|tous|chaque|une a une|un a un|l'une apres l'autre|l'un apres l'autre|all|each|one by one|one after another|in turn)\b/
};
const ORD = [
  [/\b(?:premiere|premier|1re|1ere|1er|first)\b/g, 0],
  [/(?<!\b(?:une|un|a|one) )\b(?:seconde|second|deuxieme|2e|2nd)\b/g, 1],
  [/\b(?:troisieme|3e|third|3rd)\b/g, 2],
  [/\b(?:quatrieme|4e|fourth|4th)\b/g, 3],
  [/\b(?:cinquieme|5e|fifth|5th)\b/g, 4],
  [/\b(?:sixieme|6e|sixth|6th)\b/g, 5],
  [/\b(?:derniere|dernier|last)\b/g, 'last']
];
const G = (key, kw, o) => Object.assign({ key, kw }, o || {});
const SUR = G('surtitre', KW.surtitre, { prio: 1 });
const GROUPS = {
  A1: [SUR, G('titre', KW.titre)],
  A2: [G('visuel', KW.visuel), SUR, G('titre', KW.titre)],
  A3: [SUR, G('lignes', KW.lignes, { multi: true })],
  A4: [SUR, G('titre', KW.titre, { subKw: KW.ligne })],
  A5: [SUR, G('chiffre', KW.chiffre), G('libelle', KW.libelle)],
  A6: [SUR, G('titre', KW.titre), G('barres', KW.barres, { multi: true })],
  A7: [SUR, G('titre', KW.titre), G('lignes', KW.lignes, { multi: true })],
  A8: [SUR, G('titre', KW.titre), G('lignes', KW.lignes, { multi: true })],
  A9: [G('visuel', KW.visuel), SUR, G('titre', KW.titre), G('lignes', KW.lignes, { multi: true })],
  A12: [SUR, G('titre', KW.titre), G('note', KW.note)],
  A14: [G('centre', KW.centre, { prio: 1 }), G('tuiles', KW.tuiles, { multi: true })],
  A16: [SUR, G('titre', KW.titre), G('logos', KW.logos, { multi: true })],
  A17: [SUR, G('citation', KW.citation), G('auteur', KW.auteur)],
  A19: [SUR, G('visuel', KW.visuel), G('nom', KW.nom, { multi: 'auto' }), G('prix', KW.prix, { multi: 'auto' })],
  A20: [SUR, G('libelle', KW.libelle), G('date', KW.date), G('visuel', KW.visuel)],
  A21: [G('nom', KW.titre), G('fonction', KW.fonction)],
  AF: [SUR, G('titre', KW.titre)]
};
GROUPS.A11 = GROUPS.A9;
['A18', 'A22', 'A23', 'A24', 'A25'].forEach((k) => { GROUPS[k] = GROUPS.A12; });
// Groupes des variantes (le rendu sans variante garde les groupes d'origine).
const VGROUPS = {};
VGROUPS.A10 = [G('visuel', KW.visuel)];
VGROUPS.A13 = [G('visuel', KW.visuel)];
VGROUPS.A15 = [SUR, G('titre', KW.titre), G('tuiles', KW.tuiles)];
GROUPS.FIN = [G('visuel', KW.visuel), SUR, G('titre', /\b(?:signes?|logos?|mots?|noms?|titres?|evenements?)\b/), G('libelle', /\b(?:lignes?|lieux?|signatures?|libelles?)\b/), G('note', /\b(?:mentions?|sources?)\b/)];
GROUPS.COLORIS = [G('visuel', /\b(?:coloris|couleurs?|produits?|rangees?|murs?|eventails?|colou?rs?|colorways?)\b/, { multi: 'auto' })];
GROUPS.FRISE = [SUR, G('titre', KW.titre), G('tuiles', /\b(?:jalons?|tuiles?|dates?|milestones?)\b/, { multi: true })];

// ===========================================================================
// VARIANTES DE COMPOSITION (fiches design, slide.variante). Sans variante, chaque archétype garde
// son rendu d'origine (R.Axx plus haut). Une variante pose le contenu visuel de la fiche : produit
// mis en lumière, capture dans un appareil générique, photo à fond perdu, tuiles, icônes, matières ;
// la profondeur (ombre de contact sur fond clair, halo doux, objet qui sort du cadre) ; et, quand
// l'image manque, le repli dessiné de la fiche, sans nombre ni marque.
// Positions des fiches en % du cadre (x, y, l, h), converties en pouces par P().
// Halos, ombres et dégradés de transparence : des PNG générés ici (zlib, sans dépendance), posés
// comme des images ; ils se lisent dans PowerPoint, Keynote et Canva.
// ===========================================================================

const VS = {
  ppi: 48,                                   // résolution des halos et ombres générés (ils sont flous)
  ombre: { opacite: 0.24, hauteur: 0.085, largeur: 0.78 },  // ombre de contact, fond clair seulement
  halo: { produit: 0.11, accent: 0.42, etendue: 0.42 },     // halo doux : neutre derrière un produit (fond sombre), d'accent pour un halo de fiche
  // Silhouette (repli d'un produit) : gris du volume (part du texte dans le fond), arête claire de 2 %
  // de sa largeur, et lumière de studio (haut éclairci, bas assombri, arête, reflet en haut à gauche).
  silhouette: {
    sombre: 0.3, clair: 0.15, arete: 0.022,
    lumiereSombre: { haut: 0.16, bas: 0.3, arete: 0.5, reflet: 0.2 },
    lumiereClair: { haut: 0.55, bas: 0.12, arete: 0.75, reflet: 0.5 },
    teinte: { haut: 0.22, bas: 0.22, arete: 0.55, reflet: 0.24 }
  },
  appareil: { coin: 0.13, bord: 0.03, tablette: 0.075, portable: 0.035 },
  voile: { photo: 30, chiffre: 45, contenu: 60 },           // voile noir (%) sous un texte posé sur une photo
  tuile: { rayon: 0.2, libelle: 11, pad: 0.06 }
};

// Zone d'une fiche (en % du cadre) → pouces.
function P(x, y, l, h) {
  return { x: x * W / 100, y: y * H / 100, w: l * W / 100, h: h * H / 100 };
}
function inter(a, b) {
  const x = Math.max(a.x, b.x);
  const y = Math.max(a.y, b.y);
  const x2 = Math.min(a.x + a.w, b.x + b.w);
  const y2 = Math.min(a.y + a.h, b.y + b.h);
  return x2 > x + 1e-4 && y2 > y + 1e-4 ? { x, y, w: x2 - x, h: y2 - y } : null;
}
function grow(b, dx, dy) {
  return { x: b.x - dx, y: b.y - dy, w: b.w + 2 * dx, h: b.h + 2 * (dy === undefined ? dx : dy) };
}
function darkBg(c) {
  return lum(c.P.bg) < 0.35;
}

// PNG (RGBA 8 bits), encodé à la main : signature, IHDR, IDAT (zlib), IEND.
const CRC_TABLE = (() => {
  const t = new Int32Array(256);
  for (let n = 0; n < 256; n++) {
    let v = n;
    for (let k = 0; k < 8; k++) v = v & 1 ? 0xedb88320 ^ (v >>> 1) : v >>> 1;
    t[n] = v;
  }
  return t;
})();
function crc32(buf) {
  let v = -1;
  for (let i = 0; i < buf.length; i++) v = CRC_TABLE[(v ^ buf[i]) & 0xff] ^ (v >>> 8);
  return (v ^ -1) >>> 0;
}
function pngChunk(type, data) {
  const len = Buffer.alloc(4);
  len.writeUInt32BE(data.length);
  const td = Buffer.concat([Buffer.from(type, 'ascii'), data]);
  const crc = Buffer.alloc(4);
  crc.writeUInt32BE(crc32(td));
  return Buffer.concat([len, td, crc]);
}
function encodePng(w, h, rgba) {
  const stride = w * 4 + 1;
  const raw = Buffer.alloc(stride * h);
  for (let y = 0; y < h; y++) rgba.copy(raw, y * stride + 1, y * w * 4, (y + 1) * w * 4);
  const ihdr = Buffer.alloc(13);
  ihdr.writeUInt32BE(w, 0);
  ihdr.writeUInt32BE(h, 4);
  ihdr[8] = 8;
  ihdr[9] = 6;
  return Buffer.concat([Buffer.from([137, 80, 78, 71, 13, 10, 26, 10]), pngChunk('IHDR', ihdr), pngChunk('IDAT', zlib.deflateSync(raw, { level: 9 })), pngChunk('IEND', Buffer.alloc(0))]);
}
const GEN_CACHE = new Map();
// Image générée : alpha(x, y) en pouces dans la boîte, de 0 à 1, d'une seule couleur (ou color(x, y)).
function genImage(c, box, color, alpha, name, o) {
  o = o || {};
  const ppi = o.ppi || VS.ppi;
  let pw = Math.max(6, Math.round(box.w * ppi));
  let ph = Math.max(6, Math.round(box.h * ppi));
  const cap = 700000;
  if (pw * ph > cap) {
    const k = Math.sqrt(cap / (pw * ph));
    pw = Math.max(6, Math.round(pw * k));
    ph = Math.max(6, Math.round(ph * k));
  }
  const key = (o.key || name) + '|' + color + '|' + pw + 'x' + ph + '|' + round2(box.w) + 'x' + round2(box.h);
  let buf = GEN_CACHE.get(key);
  if (!buf) {
    const px = Buffer.alloc(pw * ph * 4);
    const rgb = rgbOf(color);
    for (let j = 0; j < ph; j++) {
      const y = (j + 0.5) / ph * box.h;
      for (let i = 0; i < pw; i++) {
        const x = (i + 0.5) / pw * box.w;
        // Bord de la boîte : fondu à zéro, pour qu'aucun halo ne laisse voir son rectangle.
        const edge = o.edge === false ? 1 : smooth01(Math.min(x, box.w - x, y, box.h - y) / (Math.min(box.w, box.h) * 0.14));
        const a = clamp(alpha(x, y) * edge, 0, 1);
        const k = (j * pw + i) * 4;
        const col = o.colorAt ? o.colorAt(x, y) : rgb;
        px[k] = col[0];
        px[k + 1] = col[1];
        px[k + 2] = col[2];
        px[k + 3] = Math.round(a * 255);
      }
    }
    buf = encodePng(pw, ph, px);
    GEN_CACHE.set(key, buf);
  }
  return c.add({ k: 'image', gen: true, x: box.x, y: box.y, w: box.w, h: box.h, info: { type: 'png', mime: 'image/png', w: pw, h: ph, buf }, mode: 'fill', name: name || 'Halo', alt: '', g: o.g, sub: o.sub, rot: o.rot });
}
// Profils d'alpha.
function smooth01(t) {
  t = clamp(t, 0, 1);
  return t * t * (3 - 2 * t);
}
// Ellipse floue qui remplit la boîte : A au centre, 0 au bord.
function alphaEllipse(A, k, box) {
  const rx = box.w / 2;
  const ry = box.h / 2;
  return (x, y) => {
    const dx = (x - rx) / rx;
    const dy = (y - ry) / ry;
    const d2 = dx * dx + dy * dy;
    if (d2 >= 1) return 0;
    return A * Math.exp(-k * d2) * (1 - smooth01((d2 - 0.55) / 0.45));
  };
}
// Distance signée à un rectangle arrondi (r : rectangle relatif à la boîte, rad : rayon).
function sdRound(x, y, r, rad) {
  const cx = r.x + r.w / 2;
  const cy = r.y + r.h / 2;
  const qx = Math.abs(x - cx) - (r.w / 2 - rad);
  const qy = Math.abs(y - cy) - (r.h / 2 - rad);
  const ox = Math.max(qx, 0);
  const oy = Math.max(qy, 0);
  return Math.sqrt(ox * ox + oy * oy) + Math.min(Math.max(qx, qy), 0) - rad;
}
// Halo autour d'un rectangle arrondi : A sur son bord, décroissance gaussienne (sigma en pouces).
function alphaAround(A, r, rad, sigma, inside) {
  return (x, y) => {
    const d = sdRound(x, y, r, rad);
    if (d <= 0) return inside === undefined ? A : inside;
    return A * Math.exp(-(d * d) / (2 * sigma * sigma));
  };
}
// Anneau flou : rayon r (pouces) autour du centre de la boîte.
function alphaRing(A, r, sigma, box) {
  return (x, y) => {
    const d = Math.hypot(x - box.w / 2, y - box.h / 2) - r;
    return A * Math.exp(-(d * d) / (2 * sigma * sigma));
  };
}

// Ombre de contact (fond clair seulement) : une ellipse sombre très floue sous l'objet.
function contactShadow(c, r, o) {
  o = o || {};
  if (darkBg(c) || c.slide.profondeur === false) return null;
  r = r.content || r;
  const S = VS.ombre;
  const sh = clamp(r.h * S.hauteur, 0.09, 0.42);
  const sw = r.w * (o.largeur || S.largeur);
  const box = { x: r.x + (r.w - sw) / 2, y: r.y + r.h - sh * 0.5, w: sw, h: sh };
  return genImage(c, box, mix(c.P.bg, '000000', 0.85), alphaEllipse(o.opacite || S.opacite, 1.6, box), 'Ombre de contact', { g: o.g, sub: o.sub, key: 'ombre' });
}
// Halo doux derrière un objet : neutre (couleur du texte, très léger) sur fond sombre, ou de la
// couleur donnée (accent, coloris) quand la fiche le demande.
function softHalo(c, r, o) {
  o = o || {};
  if (c.slide.profondeur === false) return null;
  const color = o.color || c.P.fg;
  const A = o.opacite !== undefined ? o.opacite : VS.halo.produit;
  if (!o.color && !darkBg(c)) return null;
  r = r.content || r;
  const e = o.etendue !== undefined ? o.etendue : VS.halo.etendue;
  const box = grow(r, r.w * e, r.h * e);
  return genImage(c, box, color, alphaEllipse(A, 2.4, box), o.name || 'Halo', { g: o.g, sub: o.sub, key: 'halo' + A });
}

// ---------------------------------------------------------------------------
// Images d'une variante : posées avec le traitement de la fiche (ombre, halo, fond perdu, coins),
// recadrées par une zone (clip : une capture coupée par le bord d'une tuile), ou remplacées par le
// repli dessiné de la fiche. L'image manquante part dans les notes (« Image à fournir »).
// ---------------------------------------------------------------------------
const BRIEF = {
  fr: {
    objet: 'PNG détouré à fond transparent, recadré au plus près, 2000 px de haut au moins',
    interface: 'capture nue (sans cadre d\'appareil), à la définition de l\'écran',
    appareil: 'capture nue (sans cadre d\'appareil), à la définition de l\'écran',
    photo: 'photo JPEG de 1920 px de large au moins, sans texte incrusté',
    icone: 'PNG carré de 1024 px, fond transparent',
    logo: 'logo monochrome, PNG à fond transparent',
    tuile: 'image JPEG ou PNG de 1200 px de large au moins',
    fragment: 'composant isolé de son écran (carte, colonne, bouton, tableau), PNG exporté à 2x, sans l\'interface autour',
    carte: 'image de 1920 px de large au moins'
  },
  en: {
    objet: 'transparent cut-out PNG, tightly cropped, at least 2000 px tall',
    interface: 'bare screenshot (no device frame), at screen resolution',
    appareil: 'bare screenshot (no device frame), at screen resolution',
    photo: 'JPEG photo at least 1920 px wide, no text burnt in',
    icone: 'square 1024 px PNG, transparent background',
    logo: 'single-colour logo, transparent PNG',
    tuile: 'JPEG or PNG at least 1200 px wide',
    fragment: 'a single component cut out of its screen (card, column, button, table), PNG exported at 2x, without the surrounding UI',
    carte: 'image at least 1920 px wide'
  }
};
function loadImg(c, spec) {
  spec = c.imageSpec(spec);
  if (!spec || !spec.chemin) return null;
  const abs = path.resolve(c.env.deckDir, spec.chemin);
  const info = imageInfo(abs);
  return info && info.w > 0 && info.h > 0 ? { spec, abs, info, attendu: str(spec.attendu || spec.libelle || spec.alt) } : null;
}
// Rectangle de l'image entière : contenue dans la boîte, ou qui la couvre.
// Un PNG détouré se cale sur sa partie opaque (info.content) : le rectangle rendu est celui du fichier
// entier, et r.content celui de l'objet visible (ombre, halo, filets et alignements s'y accrochent).
function fitRect(box, info, mode, ax, ay) {
  const cb = mode !== 'cover' && info.content ? info.content : null;
  const iw = info.w * (cb ? cb.w : 1);
  const ih = info.h * (cb ? cb.h : 1);
  const s = mode === 'cover' ? Math.max(box.w / iw, box.h / ih) : Math.min(box.w / iw, box.h / ih);
  const w = iw * s;
  const h = ih * s;
  const x = ax === 'left' ? box.x : ax === 'right' ? box.x + box.w - w : box.x + (box.w - w) / 2;
  const y = ay === 'top' ? box.y : ay === 'bottom' ? box.y + box.h - h : box.y + (box.h - h) / 2;
  if (!cb) return { x, y, w, h };
  const fw = w / cb.w;
  const fh = h / cb.h;
  return { x: x - cb.x * fw, y: y - cb.y * fh, w: fw, h: fh, content: { x, y, w, h } };
}
// Image posée par son rectangle entier ; seule la partie dans « clip » est gardée (recadrage).
function putImage(c, im, rect, o) {
  o = o || {};
  const vis = o.clip ? inter(rect, o.clip) : rect;
  if (!vis) return null;
  const it = { k: 'image', abs: im.abs, info: im.info, mode: 'fill', radius: o.radius || 0, name: o.name || 'Image', alt: im.attendu || path.basename(im.abs), g: o.g, sub: o.sub, x: vis.x, y: vis.y, w: vis.w, h: vis.h, rot: o.rot, gray: o.gray };
  if (vis.w < rect.w - 1e-3 || vis.h < rect.h - 1e-3) it.full = rect;
  return c.add(it);
}
// Image manquante d'une variante : la consigne part dans les notes (avec le brief du visuel).
function registerMissing(c, spec, kind, defaultLabel, o) {
  o = o || {};
  spec = c.imageSpec(spec);
  const attendu = (spec && str(spec.attendu || spec.libelle || spec.alt)) || defaultLabel || '';
  if (spec && spec.chemin) {
    const abs = path.resolve(c.env.deckDir, spec.chemin);
    c.warn('Image « ' + spec.chemin + ' » ' + (fs.existsSync(abs) ? 'illisible (PNG, JPEG ou GIF attendu)' : c.L.missingFile) + ' : repli dessiné à la place, à remplacer.');
  } else {
    c.warn('Image attendue' + (attendu ? ' (« ' + attendu + ' »)' : '') + ' : repli dessiné à la place.');
  }
  c.missing.push({ kind, attendu, chemin: spec && spec.chemin ? spec.chemin : '', brief: (BRIEF[c.lang] || BRIEF.fr)[kind] });
  return attendu;
}
// Le repli dessiné, groupé dans le .pptx sous le nom de ce qu'il faut fournir.
function missingVisual(c, spec, kind, defaultLabel, o, draw) {
  const attendu = registerMissing(c, spec, kind, defaultLabel, o);
  const cap = c.L.cap[kind] || c.L.cap.interface;
  const short = shortLabel(str(stripValider(attendu)).replace(new RegExp(FOURNIR_SRC, 'gi'), (m) => markerInner(m)), 6);
  const ph = { id: c.phs.length, name: cap + (short ? ' · ' + short : ''), kind, g: o.g, sub: o.sub };
  c.phs.push(ph);
  const prev = c.curPh;
  c.curPh = ph.id;
  try {
    draw();
  } finally {
    c.curPh = prev;
  }
}
// Le visuel d'une zone. o : kind (objet, interface, photo, icone, logo, tuile), mode (contain, cover),
// alignX/alignY, clip, radius, ombre (contact, fond clair), halo (true : neutre ; couleur : teinté),
// repli(box) (dessin quand l'image manque), label (ce que l'image doit montrer, par défaut), g, sub.
// Retourne le rectangle de l'image posée, ou null pour un repli.
function visual(c, box, spec, o) {
  o = o || {};
  const im = loadImg(c, spec);
  if (im) {
    const mode = im.spec.ajustement === 'couvrir' ? 'cover' : im.spec.ajustement === 'contenir' ? 'contain' : (o.mode || 'contain');
    const r = fitRect(box, im.info, mode, o.alignX, o.alignY);
    const clip = mode === 'cover' ? (o.clip ? inter(box, o.clip) : box) : o.clip;
    if (o.halo) softHalo(c, r, { color: o.halo === true ? undefined : o.halo, opacite: o.haloA, g: o.g, sub: o.sub, etendue: o.haloE });
    if (o.ombre) contactShadow(c, r, { g: o.g, sub: o.sub });
    putImage(c, im, r, { clip, radius: o.radius, name: o.name, g: o.g, sub: o.sub, rot: o.rot, gray: o.gray });
    return r.content || r;
  }
  const kind = o.kind || 'objet';
  if (o.repli) missingVisual(c, spec, kind, o.label, o, () => o.repli(box));
  else drawPlaceholder(c, box, kind, registerMissing(c, spec, kind, o.label, o), Object.assign({}, o, { name: o.name }));
  return null;
}

// Rognage d'un dessin : les formes ajoutées depuis « start » sont coupées par le rectangle « clip »
// (une capture schématique qui sort d'une tuile). Les rectangles sont tronqués ; un rectangle arrondi
// coupé d'un seul côté garde ses coins arrondis de l'autre côté ; une forme coupée autrement disparaît.
function clipItems(c, start, clip) {
  const out = [];
  c.items.slice(start).forEach((it) => {
    if (!['rect', 'round', 'ellipse'].includes(it.k)) {
      out.push(it);
      return;
    }
    const v = inter(it, clip);
    if (!v) return;
    if (Math.abs(v.w - it.w) < 1e-3 && Math.abs(v.h - it.h) < 1e-3) {
      out.push(it);
      return;
    }
    if (it.k === 'ellipse') return;
    if (it.k === 'rect') {
      out.push(Object.assign({}, it, v));
      return;
    }
    const r = Math.min(it.radius || 0, it.w / 2, it.h / 2);
    const cutT = v.y > it.y + 1e-3;
    const cutB = v.y + v.h < it.y + it.h - 1e-3;
    const cutL = v.x > it.x + 1e-3;
    const cutR = v.x + v.w < it.x + it.w - 1e-3;
    const sides = [cutT, cutB, cutL, cutR].filter(Boolean).length;
    if (sides === 1 && r > 0.005 && (cutT || cutB ? v.h > 2 * r : v.w > 2 * r)) {
      // Partie arrondie (du côté non coupé) + rectangle plein jusqu'à la coupe.
      if (cutB) {
        out.push(Object.assign({}, it, { y: v.y, h: 2 * r }));
        out.push(Object.assign({}, it, { k: 'rect', y: v.y + r, h: v.h - r, name: it.name }));
      } else if (cutT) {
        out.push(Object.assign({}, it, { y: v.y + v.h - 2 * r, h: 2 * r }));
        out.push(Object.assign({}, it, { k: 'rect', y: v.y, h: v.h - r, name: it.name }));
      } else if (cutR) {
        out.push(Object.assign({}, it, { x: v.x, w: 2 * r }));
        out.push(Object.assign({}, it, { k: 'rect', x: v.x + r, w: v.w - r, name: it.name }));
      } else {
        out.push(Object.assign({}, it, { x: v.x + v.w - 2 * r, w: 2 * r }));
        out.push(Object.assign({}, it, { k: 'rect', x: v.x, w: v.w - r, name: it.name }));
      }
      return;
    }
    out.push(Object.assign({}, it, v, { k: 'rect' }));
  });
  // Les noms restent uniques sur la slide (volet de sélection, appariement des formes du .pptx).
  c.items.length = start;
  out.forEach((it) => {
    const base = String(it.name || it.k).replace(/ \d+$/, '');
    const n = (c.names[base] || 0) + 1;
    c.names[base] = n;
    it.name = n > 1 ? base + ' ' + n : base;
    c.items.push(it);
  });
}

// ---------------------------------------------------------------------------
// Appareils génériques (jamais reconnaissables) : coins à 13 % de la largeur, bord de 3 %, ni encoche,
// ni îlot, ni bouton, ni caméra, ni logo. La capture de l'utilisateur couvre l'écran ; sans capture,
// une interface schématique (barres grises, une ligne en accent, aucun texte ni chiffre).
// ---------------------------------------------------------------------------
// Corps d'appareil : verre noir et fin liseré métallique, sur tous les fonds (le corpus montre des
// cadres noirs, jamais gris clair). Sur fond sombre, le liseré seul détache l'appareil du fond.
function deviceColors(c) {
  const dark = darkBg(c);
  const ink = lum(c.T.texte) < 0.35 ? c.T.texte : '15181C';
  const body = dark ? mix(c.P.bg, '000000', 0.55) : mix(c.P.bg, ink, 0.9);
  return { body, base: dark ? mix(c.P.bg, c.P.fg, 0.34) : mix(c.P.bg, ink, 0.22), rim: dark ? mix(c.P.bg, c.P.fg, 0.42) : mix(body, 'FFFFFF', 0.32) };
}
// Contenu schématique d'un écran portrait (téléphone, boîtier) : un titre, des cartes, une seule en avant.
function drawScreenPortrait(c, s, C, rad, o) {
  o = o || {};
  const SC = STYLE.schema;
  c.round({ x: s.x, y: s.y, w: s.w, h: s.h, fill: C.card, radius: rad, name: 'Schéma écran' });
  const p = s.w * 0.09;
  const ix = s.x + p;
  const iw = s.w - 2 * p;
  const bh = Math.max(0.045, Math.min(SC.barre, s.w * 0.035));
  const pas = Math.max(bh * 1.9, Math.min(SC.pas, s.h * 0.035));
  pill(c, ix, s.y + s.h * 0.08, iw * 0.55, bh * 1.4, C.strong);
  pill(c, ix, s.y + s.h * 0.08 + pas * 1.25, iw * 0.35, bh, C.bar);
  const ct = s.y + s.h * 0.2;
  const n = s.h / s.w > 1.6 ? 4 : 3;
  const cardH = s.h * (n === 4 ? 0.12 : 0.16);
  const gap = s.h * 0.025;
  const hi = o.hi === undefined ? 1 : o.hi;
  for (let i = 0; i < n; i++) {
    const y = ct + i * (cardH + gap);
    const hot = i === hi && !C.mute;
    c.round({ x: ix, y, w: iw, h: cardH, fill: hot ? C.tint : C.sub, radius: Math.min(0.1, cardH * 0.25), name: 'Schéma carte' });
    const d = cardH * 0.42;
    c.ellipse({ x: ix + cardH * 0.25, y: y + (cardH - d) / 2, w: d, h: d, fill: C.bar, name: 'Schéma' });
    const tx = ix + cardH * 0.25 + d + cardH * 0.22;
    const tw = ix + iw - tx - cardH * 0.25;
    const ty = y + cardH / 2 - (pas * 0.8 + bh) / 2;
    if (hot) hiBar(c, C, tx, ty, tw * SC.longueurs[i % 3], bh);
    else pill(c, tx, ty, tw * SC.longueurs[i % 3], bh, C.strong);
    pill(c, tx, ty + pas * 0.8, tw * 0.5, bh, C.bar);
  }
  if (s.h / s.w > 1.6) pill(c, ix, s.y + s.h * 0.9, iw, Math.max(bh * 2.6, s.h * 0.055), C.strong, 'Schéma bouton');
}
// Écran paysage : la fenêtre schématique du moteur, aux coins de l'écran.
function drawScreenLandscape(c, s, C, rad, variant) {
  const rnd = rng(17 * (c.index + 1) + Math.round(s.x * 10));
  const start = c.items.length;
  drawWindow(c, s, Object.assign({}, C, { shadow: false }), rnd, variant || interfaceVariant('', c.index));
  const card = c.items[start];
  if (card && card.k === 'round') card.radius = rad;
  if (C.mute) c.items.slice(start).forEach((it) => { if (/en avant/.test(it.name || '')) it.fill = C.bar; });
}
function muteColors(C) {
  return Object.assign({}, C, { mute: true, tint: C.sub, accent: C.soft, accentFaint: false });
}
// type : telephone, tablette, portable, boitier. box : la zone « appareil » de la fiche.
// o.capture : spec de la capture ; o.mute : pas d'accent dans le schéma ; o.g, o.sub ; o.label.
function drawDevice(c, box, type, o) {
  o = o || {};
  const D = VS.appareil;
  const col = deviceColors(c);
  let C = schemaColors(c);
  if (o.mute) C = muteColors(C);
  const g = { g: o.g, sub: o.sub };
  let body;
  let screen;
  let rBody;
  let rScreen;
  if (type === 'tablette') {
    // Paysage : la plus grande boîte de rapport 1,43 dans la zone.
    let w = box.w;
    let h = w / 1.43;
    if (h > box.h) {
      h = box.h;
      w = h * 1.43;
    }
    body = { x: box.x + (box.w - w) / 2, y: box.y + (box.h - h) / 2, w, h };
    const e = Math.min(w, h) * D.bord;
    rBody = Math.min(w, h) * D.tablette;
    screen = { x: body.x + e, y: body.y + e, w: w - 2 * e, h: h - 2 * e };
    rScreen = Math.max(0.02, rBody - e);
  } else if (type === 'portable') {
    // Écran à fine base : l'écran sur 92 % de la zone, la base sur toute la largeur, sans clavier ni logo.
    const baseH = Math.max(0.07, box.h * 0.035);
    let lw = box.w * 0.84;
    let lh = lw / 1.56;
    if (lh > box.h - baseH) {
      lh = box.h - baseH;
      lw = lh * 1.56;
    }
    body = { x: box.x + (box.w - lw) / 2, y: box.y + (box.h - baseH - lh) / 2, w: lw, h: lh };
    const e = lw * D.portable * 0.55;
    rBody = lw * 0.022;
    screen = { x: body.x + e, y: body.y + e, w: lw - 2 * e, h: lh - 1.6 * e };
    rScreen = Math.max(0.01, rBody * 0.4);
    const bw = Math.min(box.w, lw * 1.16);
    const by = body.y + lh;
    if (!darkBg(c)) contactShadow(c, { x: box.x + (box.w - bw) / 2, y: by - 0.02, w: bw, h: baseH * 2.2 }, g);
    c.round(Object.assign({ x: box.x + (box.w - bw) / 2, y: by - 0.005, w: bw, h: baseH, fill: col.base, radius: baseH * 0.45, name: 'Appareil base' }, g));
  } else {
    // Portrait (téléphone) ou boîtier (zoom serré) : coins à 13 % de la largeur (22 % pour le boîtier).
    const ratio = type === 'boitier' ? 0.86 : 0.49;
    let w = Math.min(box.w, box.h * ratio);
    let h = w / ratio;
    if (type === 'boitier') {
      w = box.w;
      h = box.h;
    }
    body = { x: box.x + (box.w - w) / 2, y: box.y + (box.h - h) / 2, w, h };
    const e = w * (type === 'boitier' ? 0.075 : D.bord);
    rBody = w * (type === 'boitier' ? 0.22 : D.coin);
    screen = { x: body.x + e, y: body.y + e, w: w - 2 * e, h: h - 2 * e };
    rScreen = Math.max(0.02, rBody - e);
  }
  if (type !== 'portable' && !darkBg(c) && type !== 'boitier') contactShadow(c, body, g);
  c.round(Object.assign({ x: body.x, y: body.y, w: body.w, h: body.h, fill: col.body, line: col.rim, lineW: clamp(body.w * 0.006 * 72, 0.75, 1.75), radius: rBody, name: 'Appareil' }, g));
  // L'écran : la capture fournie, sinon le schéma (groupé, nommé « Capture à fournir »).
  const sBox = o.screen ? o.screen : screen;
  const im = loadImg(c, o.capture);
  if (im) {
    putImage(c, im, fitRect(sBox, im.info, 'cover'), { clip: sBox, radius: rScreen, name: 'Capture', g: o.g, sub: o.sub });
  } else {
    missingVisual(c, o.capture, 'interface', o.label || (c.lang === 'en' ? 'screenshot' : 'capture d\'écran'), g, () => {
      if (sBox.w > sBox.h * 1.05) drawScreenLandscape(c, sBox, C, rScreen, o.variant);
      else drawScreenPortrait(c, sBox, C, rScreen, { hi: o.hi });
    });
  }
  return { body, screen: sBox };
}

// ---------------------------------------------------------------------------
// Silhouette d'objet (repli d'un produit) : un volume arrondi modelé par la lumière, comme un objet
// photographié en studio : haut éclairé, bas dans l'ombre (dégradé vertical), arête claire en haut
// (2 % de sa largeur), reflet doux en haut à gauche (PNG contenu dans la forme) ; ombre de contact
// sur fond clair, halo neutre sur fond sombre. Aucun bouton, aucune caméra, aucun logo, aucun détail
// qui imite un produit réel. o.forme : bloc (défaut), bande (profil), disque, carre ; o.fill : un HEX
// de coloris ; o.ton : écart de gris (paliers de coloris) ; o.rot : rotation (degrés) ;
// o.ombre, o.halo, o.reflet : false pour les retirer.
// ---------------------------------------------------------------------------
function drawSilhouette(c, box, o) {
  o = o || {};
  const dark = darkBg(c);
  const S = VS.silhouette;
  const g = { g: o.g, sub: o.sub };
  let b = Object.assign({}, box);
  if (!o.exact) {
    // Proportions d'un objet : on garde la boîte, sauf un bloc trop allongé.
    if (o.forme === 'disque' || o.forme === 'carre') {
      const s = Math.min(b.w, b.h);
      b = { x: b.x + (b.w - s) / 2, y: b.y + (b.h - s) / 2, w: s, h: s };
    } else if (o.forme !== 'bande' && b.w > b.h * 1.5) {
      const w = b.h * 1.5;
      b = { x: b.x + (b.w - w) / 2, y: b.y, w, h: b.h };
    } else if (o.forme !== 'bande' && b.w < b.h * 0.72) {
      // Un bloc trop élancé se lirait comme un téléphone : on le ramène à un volume trapu.
      const h = b.w / 0.72;
      b = { x: b.x, y: b.y + (b.h - h) / 2, w: b.w, h };
    }
  }
  const tinted = !!o.fill;
  const base = o.fill || mix(c.P.bg, c.P.fg, (dark ? S.sombre : S.clair) + (o.ton || 0));
  const rad = o.forme === 'disque' ? Math.min(b.w, b.h) / 2 : o.forme === 'bande' ? b.h / 2 : Math.min(b.w, b.h) * (o.forme === 'carre' ? 0.2 : o.exact ? 0.16 : 0.3);
  if (o.ombre !== false && !dark && o.forme !== 'bande' && !o.rot) contactShadow(c, b, g);
  if (o.halo !== false && dark && !o.rot) softHalo(c, b, Object.assign({ etendue: 0.35 }, g));
  const L = tinted ? S.teinte : dark ? S.lumiereSombre : S.lumiereClair;
  const top = mix(base, 'FFFFFF', L.haut);
  const bottom = mix(base, '000000', L.bas);
  const edge = mix(base, 'FFFFFF', L.arete);
  const e = Math.max(0.018, b.w * S.arete);
  const kind = o.forme === 'disque' ? 'ellipse' : 'round';
  c.add(Object.assign({ k: kind, x: b.x, y: b.y, w: b.w, h: b.h, fill: edge, radius: rad, rot: o.rot, name: 'Silhouette arête' }, g));
  c.add(Object.assign({ k: kind, x: b.x, y: b.y + e, w: b.w, h: b.h - e, fill: base, radius: Math.max(0.01, rad - e * 0.3), grad2: { from: top, to: bottom, ang: 90 }, rot: o.rot, name: 'Silhouette' }, g));
  if (o.reflet !== false && L.reflet > 0) {
    // Le reflet ne déborde jamais de la forme : son alpha est nul hors du rectangle arrondi.
    const inside = kind === 'ellipse'
      ? (x, y) => {
        const dx = (x - b.w / 2) / (b.w / 2);
        const dy = (y - b.h / 2) / (b.h / 2);
        return 1 - smooth01((Math.sqrt(dx * dx + dy * dy) - 0.96) / 0.04);
      }
      : (x, y) => 1 - smooth01((sdRound(x, y, { x: 0, y: 0, w: b.w, h: b.h }, rad) + 0.025) / 0.025);
    const A = L.reflet;
    genImage(c, b, 'FFFFFF', (x, y) => {
      const dx = (x - b.w * 0.3) / (b.w * 0.6);
      const dy = (y - b.h * 0.2) / (b.h * 0.45);
      return A * Math.exp(-2.2 * (dx * dx + dy * dy)) * inside(x, y);
    }, 'Silhouette reflet', Object.assign({ edge: false, key: 'reflet' + kind + A + '|' + round2(rad), ppi: 40, rot: o.rot }, g));
  }
  return b;
}

// Tuile d'icône (repli d'une icône, fiche A2) : carré arrondi à 20 % du côté, dégradé vertical de
// l'accent (haut éclairci de 20 %), anneau blanc au centre (50 % du côté, trait de 8 %).
function drawIconTile(c, box, o) {
  o = o || {};
  const s = Math.min(box.w, box.h);
  const x = box.x + (box.w - s) / 2;
  const y = box.y + (box.h - s) / 2;
  const fill = o.fill || c.P.accent;
  const g = { g: o.g, sub: o.sub };
  c.round(Object.assign({ x, y, w: s, h: s, fill, radius: s * 0.2, grad2: { from: mix(fill, 'FFFFFF', 0.2), to: fill, ang: 90 }, name: 'Icône' }, g));
  const ring = onAccent(fill, c.T.fondSombre);
  const d = s * 0.5;
  const sw = s * 0.08 * 72;
  if (o.glyph === 'carre') c.round(Object.assign({ x: x + (s - d) / 2, y: y + (s - d) / 2, w: d, h: d, line: ring, lineW: sw, radius: d * 0.18, name: 'Icône forme' }, g));
  else if (o.glyph === 'barres') {
    [0.3, 0.46, 0.62].forEach((t, k) => c.round(Object.assign({ x: x + s * 0.27, y: y + s * t - s * 0.04, w: s * (k === 1 ? 0.32 : 0.46), h: s * 0.08, fill: ring, radius: s * 0.04, name: 'Icône forme' }, g)));
  } else if (o.glyph === 'point') c.ellipse(Object.assign({ x: x + s * 0.34, y: y + s * 0.34, w: s * 0.32, h: s * 0.32, fill: ring, name: 'Icône forme' }, g));
  else if (o.glyph === 'demi') {
    c.ellipse(Object.assign({ x: x + (s - d) / 2 + sw / 144, y: y + (s - d) / 2 + sw / 144, w: d - sw / 72, h: d - sw / 72, line: ring, lineW: sw, name: 'Icône forme' }, g));
    c.ellipse(Object.assign({ x: x + s * 0.41, y: y + s * 0.41, w: s * 0.18, h: s * 0.18, fill: ring, name: 'Icône forme' }, g));
  } else c.ellipse(Object.assign({ x: x + (s - d) / 2 + sw / 144, y: y + (s - d) / 2 + sw / 144, w: d - sw / 72, h: d - sw / 72, line: ring, lineW: sw, name: 'Icône forme' }, g));
  return { x, y, w: s, h: s };
}
// Teintes d'une rangée d'icônes de repli : l'accent, l'accent 2, leur mélange et un gris, chacune avec
// sa forme, pour qu'elles se lisent comme des icônes différentes (jamais trois fois la même).
const ICON_GLYPHS = ['anneau', 'carre', 'barres', 'point', 'demi'];
function iconTints(c) {
  const neutral = mix(c.P.bg, c.P.fg, darkBg(c) ? 0.5 : 0.42);
  const a2 = c.T.gradient ? c.P.accent2 : mix(c.P.accent, 'FFFFFF', 0.3);
  return [c.P.accent, a2, neutral, mix(c.P.accent, a2, 0.5), mix(c.P.accent, neutral, 0.55)];
}
// Pictogramme géométrique gris (repli d'une icône dans une tuile de bento) : cercle, carré,
// triangle ou anneau, au trait ou plein, selon le rang ; aucun signe qui se lise.
function drawGlyph(c, box, i, o) {
  o = o || {};
  const s = Math.min(box.w, box.h);
  const x = box.x + (box.w - s) / 2;
  const y = box.y + (box.h - s) / 2;
  const col = o.color || mix(c.P.surface, c.P.fg, 0.45);
  const g = { g: o.g, sub: o.sub, name: 'Pictogramme' };
  const lw = Math.max(1.5, s * 0.09 * 72);
  switch (i % 5) {
    case 0: c.ellipse(Object.assign({ x: x + s * 0.12, y: y + s * 0.12, w: s * 0.76, h: s * 0.76, line: col, lineW: lw }, g)); c.ellipse(Object.assign({ x: x + s * 0.38, y: y + s * 0.38, w: s * 0.24, h: s * 0.24, fill: col }, g)); break;
    case 1: c.round(Object.assign({ x: x + s * 0.14, y: y + s * 0.14, w: s * 0.72, h: s * 0.72, line: col, lineW: lw, radius: s * 0.16 }, g)); break;
    case 2: c.add(Object.assign({ k: 'path', pts: [[x + s * 0.5, y + s * 0.12], [x + s * 0.9, y + s * 0.84], [x + s * 0.1, y + s * 0.84]], closed: true, stroke: col, strokeW: lw, join: 'round' }, g)); break;
    case 3: for (let k = 0; k < 3; k++) c.round(Object.assign({ x: x + s * 0.12, y: y + s * (0.2 + k * 0.24), w: s * (k === 1 ? 0.56 : 0.76), h: s * 0.1, fill: col, radius: s * 0.05 }, g)); break;
    default: c.ellipse(Object.assign({ x: x + s * 0.18, y: y + s * 0.18, w: s * 0.64, h: s * 0.64, fill: col }, g));
  }
}
// Photo absente, rendue douce (variantes) : aplat un peu plus clair que le fond et deux halos
// neutres très flous, en PNG ; aucune personne dessinée.
function drawPhotoSoft(c, b, o) {
  o = o || {};
  const dark = darkBg(c);
  const ink = c.P.fg;
  const base = o.base || mix(c.P.bg, ink, dark ? 0.08 : 0.06);
  const g = { g: o.g, sub: o.sub };
  if (o.radius) c.round(Object.assign({ x: b.x, y: b.y, w: b.w, h: b.h, fill: base, radius: o.radius, name: 'Schéma photo' }, g));
  else c.rect(Object.assign({ x: b.x, y: b.y, w: b.w, h: b.h, fill: base, name: 'Schéma photo' }, g));
  const h1 = { x: b.x + b.w * 0.42, y: b.y - b.h * 0.25, w: b.w * 0.75, h: b.h * 1.1 };
  const h2 = { x: b.x - b.w * 0.2, y: b.y + b.h * 0.35, w: b.w * 0.75, h: b.h * 0.95 };
  const clipB = { x: b.x, y: b.y, w: b.w, h: b.h };
  [h1, h2].forEach((h, i) => {
    const v = inter(h, clipB);
    if (!v) return;
    // Le halo est calculé sur sa boîte entière, mais seule la partie dans la photo est posée.
    const A = i === 0 ? (dark ? 0.13 : 0.5) : (dark ? 0.08 : 0.35);
    const col = dark ? ink : 'FFFFFF';
    const fn = alphaEllipse(A, 1.8, h);
    genImage(c, v, col, (x, y) => fn(x + v.x - h.x, y + v.y - h.y), 'Schéma lumière', Object.assign({ key: 'photo' + i + round2(h.w) + round2(h.h) + round2(v.x - h.x) + round2(v.y - h.y) }, g));
  });
}
// Voile en dégradé (bas d'une photo, sous un texte) : du transparent au noir à « A ».
function gradientVeil(c, b, A, dir, o) {
  o = o || {};
  return genImage(c, b, '000000', (x, y) => {
    const t = dir === 'haut' ? 1 - y / b.h : dir === 'gauche' ? 1 - x / b.w : dir === 'droite' ? x / b.w : y / b.h;
    return A * smooth01(t);
  }, o.name || 'Voile', { key: 'voile' + dir + A, g: o.g, sub: o.sub, ppi: 24 });
}

// ---------------------------------------------------------------------------
// Aides de texte des variantes : un texte posé dans une zone de fiche (centré sur la zone, ou par
// le haut de ses capitales), au corps de la fiche, réduit jusqu'à un plancher.
// ---------------------------------------------------------------------------
function tv(c, field) {
  const v = c.t[field];
  return v === undefined || v === null ? '' : String(v).trim() === '' ? '' : v;
}
function zt(c, z, text, o) {
  o = o || {};
  const font = o.font || 'titre';
  const wt = o.wt || 'semi';
  const paras = o.paras || c.para(text, { wt, font, color: o.color, g: o.g, sub: o.sub, point: o.point, grad: o.grad, subLines: o.subLines });
  const size = o.size || 24;
  const min = o.min !== undefined ? o.min : Math.max(9, Math.round(size * 0.72));
  // Sur une ligne imposée, on garde 6 % de marge : l'estimation des chasses reste une estimation.
  const stages = o.stages || (o.noWrap ? [{ w: z.w * 0.94, size, min, maxLines: 1 }] : undefined);
  const base = {
    x: z.x, w: z.w, paras, size, min, maxTotal: o.maxTotal || 2, maxLines: o.maxLines, stages, wt, align: o.align || 'center', font,
    color: o.color || c.P.fg, lh: o.lh || K.titre, balance: o.balance !== false && !o.noWrap, noWrap: o.noWrap, name: o.name || 'Texte', g: o.g, sub: o.sub
  };
  if (o.anchor === 'top') return topBox(c, Object.assign(base, { capTop: z.y, room: o.room }));
  return centerBox(c, Object.assign(base, { cy: z.y + z.h / 2, room: o.room || Math.max(z.h * 1.8, 0.7) }));
}
// Une liste (un paragraphe par ligne) dans une zone, au pas de k caps.
function zlist(c, z, lines, o) {
  o = o || {};
  const font = o.font || 'texte';
  const paras = [];
  const actif = o.actif === undefined ? Number(c.t.actif) || 0 : o.actif;
  lines.forEach((l, i) => {
    let color = o.color || c.P.fg;
    if (actif) color = i + 1 === actif ? (o.activeColor || c.P.fg) : (o.idleColor || c.P.fg2);
    if (o.colors && o.colors[i]) color = o.colors[i];
    c.para(l, { wt: o.wt || 'semi', font, color, g: o.g || 'lignes', sub: i, gapK: (o.k || K.courte) - (o.lh || K.titre) }).forEach((p) => paras.push(p));
  });
  const size = o.size || 24;
  const stages = o.stages || [{ size, min: o.min || Math.max(12, Math.round(size * 0.75)), maxLines: o.maxLines || 2 }];
  const base = { x: z.x, w: z.w, paras, stages, wt: o.wt || 'semi', align: o.align || 'left', font, lh: o.lh || K.titre, name: o.name || 'Liste' };
  if (o.anchor === 'top') return topBox(c, Object.assign(base, { capTop: z.y }));
  return centerBox(c, Object.assign(base, { cy: z.y + z.h / 2, room: o.room || Math.max(z.h * 2, 1.2) }));
}
function gradOK(c) {
  return c.T.gradient && c.P.accent === c.T.accent && contrast(c.P.bg, c.T.accent) >= 2.6 && contrast(c.P.bg, c.T.accent2) >= 2.6 && !['keynote', 'canva'].includes(normKey((c.deck.meta || {}).format));
}
// Resserre une zone de texte sur sa ligne la plus longue (le dégradé la parcourt alors en entier).
function hugText(it) {
  const geo = textGeom(it);
  let wmax = 0;
  it.paras.forEach((p) => {
    const ps = paraSize(it, p, it.fitted);
    wmax = Math.max(wmax, wrapInfo(p.runs.map((r) => r.t).join(''), ps, heavy(paraWeight(it, p)), it.w, paraTrack(it, p, ps), roleOf(it, p)).widest);
  });
  const w = Math.min(it.w, wmax * 1.04 + 0.12);
  if (it.align === 'center') it.x += (it.w - w) / 2;
  else if (it.align === 'right') it.x += it.w - w;
  it.w = w;
  return geo;
}
function imagesOf(c) {
  return arr(c.slide.images);
}
function photoSpec(c) {
  return c.slide.image_fond || c.slide.image;
}
// Photo à fond perdu (cover) avec voile, ou repli doux. Retourne true si une vraie photo est posée.
function fullPhoto(c, spec, o) {
  o = o || {};
  const box = o.box || { x: 0, y: 0, w: W, h: H };
  const im = loadImg(c, spec);
  if (im) {
    putImage(c, im, fitRect(box, im.info, 'cover'), { clip: box, name: o.name || 'Photo', g: o.g, gray: o.gray, radius: o.radius });
    const v = o.voile !== undefined ? o.voile : (c.slide.voile !== undefined ? Number(c.slide.voile) || 0 : 0);
    if (v > 0) c.rect({ x: box.x, y: box.y, w: box.w, h: box.h, fill: '000000', transparency: 100 - clamp(v, 0, 100), name: 'Voile', g: o.g });
    return true;
  }
  missingVisual(c, spec, 'photo', o.label || (c.lang === 'en' ? 'calm photo' : 'photo calme'), { g: o.g }, () => drawPhotoSoft(c, box, { g: o.g, radius: o.radius }));
  return false;
}
// Repli d'objet ou visuel fourni, avec le traitement de profondeur de la fiche. Quand image.attendu
// décrit autre chose qu'un objet (une carte, un écran, une photo), le repli suit ce qu'on attend :
// une carte schématique, une interface ou une photo douce, contenues dans la zone, jamais une
// silhouette de produit à la place d'une carte.
function productVisual(c, box, spec, o) {
  o = o || {};
  const sp = c.imageSpec(spec);
  const att = sp ? str(sp.attendu || sp.libelle || sp.alt) : '';
  let k = sp && att && !loadImg(c, spec) ? placeholderKind(c, sp, att, {}) : 'objet';
  if (k === 'interface' && KIND_RX.objet.test(normText(att))) k = 'objet';
  const other = ['carte', 'interface', 'photo'].includes(k);
  return visual(c, box, spec, Object.assign({
    kind: other ? k : 'objet', ombre: true, halo: darkBg(c) && o.halo !== false, label: o.label || (c.lang === 'en' ? 'cut-out product' : 'produit détouré'),
    repli: other ? (b) => flatRepli(c, b, k, att, o) : (b) => drawSilhouette(c, o.silBox ? o.silBox(b) : b, { forme: o.forme, g: o.g, sub: o.sub, fill: o.fill, ton: o.ton, exact: o.exact, ombre: o.ombreSil, halo: o.haloSil })
  }, o));
}
function flatRepli(c, b, k, attendu, o) {
  const C = schemaColors(c);
  const rnd = rng(41 * (c.index + 1) + Math.round(b.x * 10));
  const r = 1.3;
  let w = Math.min(b.w, W - 2 * 0.3);
  let h = w / r;
  if (h > b.h) {
    h = b.h;
    w = h * r;
  }
  const x = clamp(b.x + (b.w - w) / 2, 0.3, W - 0.3 - w);
  const bx = { x, y: b.y + (b.h - h) / 2, w, h };
  if (k === 'carte') drawMap(c, bx, C, rnd);
  else if (k === 'photo') drawPhotoSoft(c, bx, { g: o.g, sub: o.sub, radius: STYLE.schema.rayon });
  else drawWindow(c, bx, Object.assign({}, C, { shadow: false }), rnd, interfaceVariant(attendu, c.index));
}
// Écran ou capture dans une zone : interface schématique claire et entière quand elle manque.
function screenVisual(c, box, spec, o) {
  o = o || {};
  return visual(c, box, spec, Object.assign({ kind: 'interface', mode: 'contain', radius: STYLE.schema.rayon, label: c.lang === 'en' ? 'screenshot' : 'capture d\'écran' }, o));
}
function srcLine(c, z, o) {
  if (!c.sourceOnSlide || c.sourceDone) return;
  o = o || {};
  c.text({ x: z.x, y: z.y, w: z.w, h: Math.max(z.h, 0.3), text: c.sourceDisplay, size: STYLE.source[0], min: STYLE.source[1], color: o.color || c.P.fg2, align: o.align || 'center', valign: 'top', font: 'texte', lh: K.titre, name: 'Source', g: o.g });
  c.sourceDone = true;
}

const V = {};

// ---------------------------------------------------------------------------
// Textes : A1, A2, A3, A4, A7, A8, A17, A21
// ---------------------------------------------------------------------------
V['A1/aplat'] = (c) => R.A1(c);
// Le nom en dégradé de section (accent → accent2), accent uni sans accent2 ou pour Keynote et Canva.
function gradientTitle(c, S, big) {
  const grad = gradOK(c);
  c.accentUsed = true;
  const paras = c.para(c.f('titre', 'titre'), { wt: 'semi', font: 'titre', g: 'titre', point: !big, color: c.P.accentTxt, grad, subLines: !big });
  const stages = big ? bigStages(STYLE.A1.corps[0], paras.length > 1) : [{ size: S.corps[0], min: S.corps[1], maxLines: paras.length > 1 ? 1 : 2, maxTotal: 2 }];
  const t = centerBox(c, { x: S.x, w: S.w, cy: S.cy, paras, stages, wt: 'semi', align: 'center', font: 'titre', color: c.P.accentTxt, lh: K.titre, balance: true, name: 'Titre' });
  if (grad) {
    hugText(t.it);
    t.it.grad = true;
  }
  c.kicker(t.g, { x: S.x, w: S.w, align: 'center' });
}
V['A1/degrade'] = (c) => gradientTitle(c, STYLE.A1, true);
V['A1/sur-image'] = (c) => {
  const real = fullPhoto(c, photoSpec(c), { voile: c.slide.voile !== undefined ? Number(c.slide.voile) : VS.voile.photo, g: 'visuel' });
  const color = real ? 'FFFFFF' : c.P.fg;
  const A = STYLE.A1;
  const paras = c.para(c.f('titre', 'titre'), { wt: 'semi', font: 'titre', g: 'titre', point: true, color });
  const t = centerBox(c, { x: A.x, w: A.w, cy: A.cy, paras, stages: bigStages(A.corps[0], paras.length > 1), wt: 'semi', align: 'center', font: 'titre', color, lh: K.titre, balance: true, name: 'Titre' });
  c.kicker(t.g, { x: A.x, w: A.w, align: 'center', color: real ? 'E8E8E8' : undefined });
};
// Couronne : des mots (textes.couronne) ou, à défaut, des pastilles et des barres grises, posés sur
// une ellipse qui laisse libre un ovale central de 60 % L × 36 % H.
V['A1/entoure'] = (c) => {
  // Le nom d'abord (au centre, plus petit), puis la couronne sur deux anneaux : l'intérieur net,
  // l'extérieur sur trois plans de profondeur (corps et gris variés) qui sortent du cadre.
  const z = P(20, 42, 60, 16);
  const t = zt(c, z, c.f('titre', 'titre'), { size: 72, min: 48, maxTotal: 1, point: true, g: 'titre', name: 'Titre' });
  c.kicker(t.g, { x: z.x, w: z.w, align: 'center' });
  const words = arr(c.t.couronne).map(str).filter((s) => s.trim());
  const rnd = rng(97 + c.index * 13);
  const cx = W / 2;
  const cy = H / 2;
  const tb = grow(hugBox(t.it), 0.35, 0.3);
  const placed = [tb];
  const N = words.length ? Math.max(words.length, 24) : 20;
  for (let i = 0; i < N; i++) {
    const outer = i % 2 === 1;
    const a = -Math.PI / 2 + i * 2 * Math.PI / N + (rnd() - 0.5) * 0.25;
    const rx = (outer ? 0.47 : 0.3) * W + (rnd() - 0.5) * 0.4;
    const ry = (outer ? 0.46 : 0.31) * H + (rnd() - 0.5) * 0.25;
    const x = cx + Math.cos(a) * rx;
    const y = cy + Math.sin(a) * ry;
    const depth = outer ? [0.72, 0.55, 0.38][Math.floor(rnd() * 3)] : 0.4;
    const color = mix(c.P.fg, c.P.bg, depth);
    if (words.length) {
      const wd = words[i % words.length];
      const pt = outer ? [13, 18, 24][Math.floor(rnd() * 3)] : 17;
      const S = scalePt(pt, 'texte');
      const tw = Math.min(2.8, textWidth(typo(stripValider(wd), c.lang), S, true, 0, 'texte') + 0.2);
      const box = { x: x - tw / 2, y: y - capIn('texte', S) * 1.3, w: tw, h: capIn('texte', S) * 2.6 };
      if (placed.some((b) => inter(grow(b, 0.06, 0.02), box))) continue;
      placed.push(box);
      c.text({ x: box.x, y: box.y, w: box.w, h: box.h, text: wd, size: pt, min: pt, maxLines: 1, noWrap: true, wt: 'regular', color, align: 'center', font: 'texte', lh: K.titre, name: 'Couronne', g: 'lignes', sub: i });
    } else {
      const box = { x: x - 0.5, y: y - 0.1, w: 1, h: 0.2 };
      if (placed.some((b) => inter(b, box))) continue;
      placed.push(box);
      if (i % 3 === 0) c.ellipse({ x: x - 0.09, y: y - 0.09, w: 0.18, h: 0.18, fill: color, name: 'Couronne', g: 'lignes', sub: i });
      else {
        const pw = 0.45 + rnd() * 0.7;
        pill(c, x - pw / 2, y - 0.055, pw, 0.11, color, 'Couronne');
        c.items[c.items.length - 1].g = 'lignes';
        c.items[c.items.length - 1].sub = i;
      }
    }
  }
  c.groups = [SUR, G('titre', KW.titre), G('lignes', /\b(?:couronnes?|elements?|mots?|pastilles?)\b/, { multi: false })];
};
// Rectangle réellement occupé par un texte centré (sa ligne la plus longue, ses lignes).
function hugBox(it) {
  const geo = textGeom(it);
  let wmax = 0;
  it.paras.forEach((p) => {
    const ps = paraSize(it, p, it.fitted);
    wmax = Math.max(wmax, wrapInfo(p.runs.map((r) => r.t).join(''), ps, heavy(paraWeight(it, p)), it.w, paraTrack(it, p, ps), roleOf(it, p)).widest);
  });
  const w = Math.min(it.w, wmax);
  const x = it.align === 'center' ? it.x + (it.w - w) / 2 : it.align === 'right' ? it.x + it.w - w : it.x;
  return { x, y: geo.capTop - geo.capH * 0.3, w, h: geo.base - geo.capTop + geo.capH * 0.6 };
}
V['A1/matiere'] = (c) => {
  if (!loadImg(c, c.slide.image)) {
    if (c.slide.image) registerMissing(c, c.slide.image, 'objet', c.lang === 'en' ? 'the word rendered in material' : 'le mot rendu en matière');
    // Sans rendu fourni : la matière la plus simple de la fiche, le trait lumineux en contour (lettres
    // au trait d'accent, lueur douce). Un nom qui reste à fournir garde l'aplat d'origine, estompé.
    R.A1(c);
    if (!hasFournir(c.t.titre)) {
      const it = c.items.filter((x) => x.k === 'text' && x.name === 'Titre').pop();
      if (it) {
        it.outline = { color: c.P.accent, pt: 2, glow: 6, glowA: 0.45 };
        c.accentUsed = true;
      }
    }
    return;
  }
  visual(c, P(10, 30, 80, 40), c.slide.image, { kind: 'objet', g: 'titre' });
};

// A2 : l'icône (image fournie, ou tuile de repli) et le nom.
function iconVisual(c, box, spec, o) {
  o = o || {};
  return visual(c, box, spec, Object.assign({ kind: 'icone', label: c.lang === 'en' ? 'icon' : 'icône', repli: (b) => drawIconTile(c, b, { g: o.g, sub: o.sub, fill: o.fill, glyph: o.glyph }) }, o));
}
V['A2/icone-nom'] = (c) => {
  iconVisual(c, P(39, 30.5, 22, 39), c.slide.image, { g: 'visuel' });
  const z = P(10, 76, 80, 8);
  const t = zt(c, z, c.f('titre', 'nom'), { size: 32, min: 24, maxTotal: 1, g: 'titre', name: 'Nom' });
  c.kicker(t.g, { x: z.x, w: z.w, align: 'center' });
};
V['A2/icone-cote'] = (c) => {
  // L'icône et le nom forment un groupe centré dans le cadre (fiche : sur la même ligne).
  const iz = P(0, 30.5, 22, 39);
  const s = Math.min(iz.w, iz.h);
  const ps = scalePt(32, 'titre');
  const nw = Math.min(4.8, textWidth(shownText(c, c.f('titre', 'nom')), ps, true, trackFor('titre', ps), 'titre') + 0.1);
  const gap = 0.6;
  const x0 = Math.max(M, (W - (s + gap + nw)) / 2);
  iconVisual(c, { x: x0, y: iz.y + (iz.h - s) / 2, w: s, h: s }, c.slide.image, { g: 'visuel' });
  const z = { x: x0 + s + gap, y: P(0, 45, 0, 10).y, w: Math.min(4.8, W - M - (x0 + s + gap)), h: P(0, 45, 0, 10).h };
  const t = zt(c, z, c.f('titre', 'nom'), { size: 32, min: 24, maxTotal: 2, align: 'left', g: 'titre', name: 'Nom' });
  c.kicker(t.g, { x: z.x, w: z.w, align: 'left' });
};
V['A2/logo-nom'] = (c) => {
  const spec = c.slide.image || (c.T.logo ? { chemin: c.T.logo } : null);
  const im = loadImg(c, spec);
  if (!im) {
    R.A1(c);
    return;
  }
  const size = scalePt(80, 'titre');
  const name = shownText(c, c.f('titre', 'nom'));
  const tw = Math.min(6.4, textWidth(name, size, true, trackFor('titre', size), 'titre'));
  const capH = capIn('titre', size);
  const lh = capH * 1.1;
  const lw = lh * im.info.w / im.info.h;
  const gap = capH * 0.35;
  const total = lw + gap + tw;
  const x0 = (W - total) / 2;
  putImage(c, im, { x: x0, y: H / 2 - lh / 2, w: lw, h: lh }, { name: 'Logo', g: 'titre' });
  c.line({ text: c.f('titre', 'nom'), x: x0 + lw + gap, w: tw + 0.6, base: H / 2 + capH / 2, size, wt: 'semi', align: 'left', font: 'titre', name: 'Nom', g: 'titre' });
};
V['A2/rangee'] = (c) => {
  const imgs = imagesOf(c);
  [14.8, 38.85, 62.9].forEach((x, i) => {
    iconVisual(c, P(x, 30, 22.3, 40), imgs[i] || (i === 0 ? c.slide.image : null), { g: 'visuel', sub: i, fill: iconTints(c)[i], glyph: ICON_GLYPHS[i] });
  });
  c.groups = [G('visuel', KW.visuel, { multi: true })];
};
V['A2/objet-interface'] = (c) => {
  // Fiche : le bouton seul, sur 31 à 33 % L ; il s'élargit pour un libellé plus long.
  const z = P(33, 43, 34, 13);
  const dark = darkBg(c);
  const fill = dark ? (contrast(c.T.fondClair, c.P.bg) >= 4.5 ? c.T.fondClair : 'FFFFFF') : mix(c.P.bg, c.P.fg, 0.88);
  const color = readableOn(fill, c.T.fondSombre, 'FFFFFF');
  const size = scalePt(28, 'texte');
  const label = shownText(c, c.f('titre', 'action'));
  const w = clamp(Math.max(z.w, textWidth(label, size, true, trackFor('texte', size), 'texte') + z.h * 1.4), z.h * 2.2, W - 1.2);
  c.round({ x: (W - w) / 2, y: z.y, w, h: z.h, fill, radius: z.h / 2, name: 'Bouton', g: 'visuel' });
  zt(c, { x: (W - w) / 2, y: z.y, w, h: z.h }, c.f('titre', 'action'), { size: 28, min: 20, maxTotal: 1, font: 'texte', color, g: 'visuel', name: 'Bouton libellé' });
};
V['A2/icone-seule'] = (c) => {
  iconVisual(c, P(39, 30, 22, 40), c.slide.image, { g: 'visuel' });
};

// A3 : sommaire. Corps selon le nombre de lignes (STYLE.A3), alignement de la variante.
function summary(c, o) {
  const S = STYLE.A3;
  let lines = arr(c.t.lignes);
  if (!lines.length) lines.push(c.f('lignes', 'lignes'));
  if (o.slice) lines = lines.slice(0, o.slice);
  const actif = Number(c.t.actif) || 0;
  c.accentUsed = !!actif || !!o.colors;
  const paras = [];
  lines.forEach((l, i) => {
    let color = c.P.fg;
    if (o.colors && o.colors[i]) color = o.colors[i];
    else if (actif) color = i + 1 === actif ? c.P.accentTxt : (o.idle || c.P.fg2);
    if (o.pale !== undefined && i === o.pale) color = mix(c.P.fg, c.P.bg, 0.75);
    c.para(l, { color, wt: 'semi', font: 'titre', g: 'lignes', sub: i }).forEach((p) => paras.push(p));
  });
  const n = o.count || lines.length;
  const size = o.size || S.corps[clamp(n, 1, 8)];
  const t = centerBox(c, { x: o.x, w: o.w, cy: o.cy || S.cy, paras, size, min: Math.min(size, S.plancher), maxLines: 1, wt: 'semi', align: o.align, font: 'titre', lh: K.sommaire, name: 'Sommaire' });
  c.kicker(t.g, { x: o.x, w: o.w, align: o.align });
  return t;
}
V['A3/centre'] = (c) => R.A3(c);
V['A3/droite'] = (c) => summary(c, { x: 2.0, w: 5.6, align: 'right' });
V['A3/ligne'] = (c) => {
  const lines = arr(c.t.lignes);
  if (!lines.length) lines.push(c.f('lignes', 'lignes'));
  const actif = Number(c.t.actif) || 0;
  c.accentUsed = !!actif;
  const runs = [];
  lines.forEach((l, i) => {
    if (i) runs.push({ t: '      ' });
    const ps = c.para(l, { wt: 'semi', font: 'titre' });
    const color = actif ? (i + 1 === actif ? c.P.accentTxt : c.P.fg2) : c.P.fg;
    ps.forEach((p) => p.runs.forEach((r) => runs.push(Object.assign({}, r, { color: r.marker ? undefined : color }))));
  });
  const para = { runs: runs.length ? runs : [{ t: '' }], rel: 1, g: 'lignes', wt: 'semi', font: 'titre' };
  const z = P(6, 43, 88, 14);
  const t = centerBox(c, { x: z.x, w: z.w, cy: z.y + z.h / 2, paras: [para], size: 40, min: 22, maxLines: 1, wt: 'semi', align: 'center', font: 'titre', lh: K.titre, name: 'Sommaire' });
  c.kicker(t.g, { x: z.x, w: z.w, align: 'center' });
};
V['A3/numerote'] = (c) => {
  const lines = arr(c.t.lignes);
  if (!lines.length) lines.push(c.f('lignes', 'lignes'));
  const z = P(32, 29, 48, 42);
  const size = Math.min(48, STYLE.A3.corps[clamp(lines.length, 1, 8)]);
  const t = zlist(c, z, lines, { size, min: 24, maxLines: 1, font: 'titre', k: K.sommaire + 0.25, lh: K.sommaire, color: c.P.fg, actif: Number(c.t.actif) || 0, activeColor: c.P.fg, idleColor: c.P.fg2 });
  const geo = t.g;
  const numeros = c.t.numeros !== false;
  // Numéros et lignes forment un bloc centré dans le cadre (fiche : pile numérotée au centre).
  hugText(t.it);
  const cap0 = geo.lines.length ? geo.lines[0].cap : 0.3;
  const lead = cap0 * 1.5 + cap0 * 0.7;
  t.it.x = Math.max(M + lead, (W - (lead + t.it.w)) / 2 + lead);
  geo.lines.forEach((ln, i) => {
    if (i >= lines.length) return;
    const d = ln.cap * 1.5;
    const x = t.it.x - d - ln.cap * 0.7;
    if (numeros) {
      c.ellipse({ x, y: ln.c - d / 2, w: d, h: d, line: c.P.accent, lineW: Math.max(1.5, d * 72 * 0.06), name: 'Numéro', g: 'lignes', sub: i });
      c.text({ x, y: ln.c - d / 2, w: d, h: d, text: String(i + 1), size: Math.round(ln.ps * 0.5), min: 10, maxLines: 1, wt: 'semi', color: c.P.accentTxt, align: 'center', font: 'texte', lh: K.titre, name: 'Numéro chiffre', g: 'lignes', sub: i, fixed: Math.round(ln.ps * 0.5) });
    } else c.ellipse({ x: x + d * 0.3, y: ln.c - d * 0.2, w: d * 0.4, h: d * 0.4, fill: c.P.accent, name: 'Numéro', g: 'lignes', sub: i });
  });
  c.accentUsed = true;
  c.kicker(geo, { x: t.it.x, w: z.w, align: 'left' });
};
V['A3/suffixe'] = (c) => {
  const t = summary(c, { x: 1.0, w: 5.6, align: 'right' });
  const suf = tv(c, 'suffixe');
  if (!suf) return;
  const it = t.it;
  t.g.lines.forEach((ln, i) => {
    c.line({ text: suf, x: 6.8, w: 2.6, base: ln.c + ln.cap / 2, size: ln.ps, wt: 'regular', color: c.P.fg, align: 'left', font: 'titre', name: 'Suffixe', g: 'note', sub: i });
  });
  it.x = 1.0;
  c.groups = [SUR, G('lignes', KW.lignes, { multi: true }), G('note', /\b(?:suffixes?|mots? ajoutes?|second etat)\b/)];
};
V['A3/ligne-active'] = (c) => {
  const lines = arr(c.t.lignes);
  const actif = clamp(Number(c.t.actif) || 1, 1, Math.max(1, lines.length));
  const shown = lines.slice(0, Math.min(lines.length, actif + 1));
  c.t = Object.assign({}, c.t, { lignes: shown, actif: 0 });
  summary(c, { x: 1.0, w: 8.0, align: 'center', count: lines.length, pale: actif < lines.length ? actif : undefined });
};
V['A3/couleurs'] = (c) => {
  const cols = arr(c.t.couleurs).map((h) => hex(h, null, 'couleurs', c.warnings)).filter(Boolean);
  summary(c, { x: 2.0, w: 5.6, align: 'right', colors: cols.length ? cols.map((h) => textAccent(c.P.bg, h, c.P.fg)) : null });
};

V['A4/aplat'] = (c) => R.A4(c);
V['A4/degrade'] = (c) => gradientTitle(c, STYLE.A4, false);
V['A4/mot-accent'] = (c) => R.A4(c);
V['A4/definition'] = (c) => {
  const mot = tv(c, 'mot') || tv(c, 'surtitre');
  const nature = tv(c, 'nature');
  c.accentUsed = true;
  const z1 = P(14, 30, 72, 7);
  const paras = [];
  if (mot) c.para(String(mot).toUpperCase(), { wt: 'semi', font: 'texte', color: c.P.accentTxt }).forEach((p) => paras.push(p));
  if (nature) {
    const np = c.para(nature, { wt: 'regular', font: 'texte', color: c.P.fg2 });
    if (paras.length) {
      paras[0].runs.push({ t: '   ' });
      np[0].runs.forEach((r) => paras[0].runs.push(Object.assign({}, r, { color: r.marker ? undefined : c.P.fg2 })));
    } else np.forEach((p) => paras.push(p));
  }
  const z2 = P(14, 39, 72, 24);
  const t = zt(c, z2, c.f('titre', 'définition'), { size: 40, min: 30, maxTotal: 3, align: 'left', anchor: 'top', g: 'titre', name: 'Définition', point: true });
  if (paras.length) c.line({ paras, x: z1.x, w: z1.w, base: t.g.capTop - 0.36, size: scalePt(24, 'texte'), wt: 'semi', color: c.P.accentTxt, align: 'left', font: 'texte', name: 'Mot', g: 'titre' });
};
V['A4/sur-image'] = (c) => {
  const real = fullPhoto(c, photoSpec(c), { voile: c.slide.voile !== undefined ? Number(c.slide.voile) : 40, g: 'visuel' });
  const S = STYLE.A4;
  const color = real ? 'FFFFFF' : c.P.fg;
  const paras = c.para(c.f('titre', 'phrase'), { wt: 'semi', font: 'titre', g: 'titre', subLines: true, point: true, color });
  const t = centerBox(c, { x: S.x, w: S.w, cy: S.cy, paras, stages: [{ size: S.corps[0], min: S.corps[1], maxLines: paras.length > 1 ? 1 : 2, maxTotal: 2 }], wt: 'semi', align: 'center', font: 'titre', color, lh: K.titre, balance: true, name: 'Phrase' });
  c.kicker(t.g, { x: S.x, w: S.w, align: 'center', color: real ? 'E8E8E8' : undefined });
  c.groups = [G('visuel', KW.visuel), SUR, G('titre', KW.titre)];
};
V['A4/sourdine'] = (c) => {
  const S = STYLE.A4;
  const paras = c.para(c.f('titre', 'phrase'), { wt: 'semi', font: 'titre', g: 'titre', subLines: true, color: c.P.fg2 });
  const t = centerBox(c, { x: S.x, w: S.w, cy: S.cy, paras, stages: [{ size: S.corps[0], min: S.corps[1], maxLines: paras.length > 1 ? 1 : 2, maxTotal: 2 }], wt: 'semi', align: 'center', font: 'titre', color: c.P.fg2, lh: K.titre, balance: true, name: 'Phrase' });
  c.kicker(t.g, { x: S.x, w: S.w, align: 'center' });
};
V['A4/enchainee'] = (c) => R.A4(c);

// A7 : listes.
V['A7/centree'] = (c) => R.A7(c);
V['A7/empilement'] = (c) => {
  const lines = arr(c.t.lignes);
  const k = Number(c.t.actif) || lines.length;
  c.t = Object.assign({}, c.t, { lignes: lines.slice(0, Math.max(1, k)), actif: 0 });
  // La pile garde le même pas d'un état à l'autre (1,95 cap), même à deux lignes : sinon elle saute.
  c._pitchK = K.liste;
  R.A7(c);
};
function sideList(c, zv, zl, size, drawVis) {
  drawVis();
  let lines = arr(c.t.lignes).slice(0, 6);
  if (!lines.length) lines = [c.f('lignes', 'lignes')];
  const t = zlist(c, zl, lines, { size, k: K.courte, color: c.P.fg });
  const geo = listHeading(c, t.g, { x: zl.x, w: zl.w, align: 'left', size: Math.max(16, size * 0.7) });
  c.kicker(geo, { x: zl.x, w: zl.w, align: 'left' });
  c.groups = [G('visuel', KW.visuel), SUR, G('titre', KW.titre), G('lignes', KW.lignes, { multi: true })];
}
V['A7/a-cote-icone'] = (c) => sideList(c, null, P(45, 36, 48, 28), 24, () => iconVisual(c, P(11.5, 31, 21, 38), c.slide.image, { g: 'visuel' }));
V['A7/a-cote-objet'] = (c) => sideList(c, null, P(58, 34, 36, 32), 24, () => {
  const z = P(4, 14, 48, 72);
  const im = loadImg(c, c.slide.image);
  const kind = placeholderKind(c, c.imageSpec(c.slide.image), str((c.imageSpec(c.slide.image) || {}).attendu), {});
  if (!im && kind !== 'objet') screenVisual(c, { x: 0.5, y: z.y + 0.2, w: z.w - 0.2, h: z.h - 0.4 }, c.slide.image, { g: 'visuel' });
  else productVisual(c, z, c.slide.image, { g: 'visuel' });
});
V['A7/deux-colonnes'] = (c) => {
  const lines = arr(c.t.lignes);
  if (!lines.length) lines.push(c.f('lignes', 'lignes'));
  const half = Math.ceil(lines.length / 2);
  const cols = [lines.slice(0, half), lines.slice(half)];
  // Deux colonnes au même corps et au même pas : le plus petit des deux ajustements. La seconde
  // colonne suit la première (6 % L après sa ligne la plus longue), et l'icône et les colonnes forment
  // un bloc centré : des libellés courts ne laissent plus un trou au milieu de la slide.
  const boxes = cols.map((ls, k) => {
    if (!ls.length) return null;
    const z = P(k ? 66 : 34, 20, 28, 60);
    const paras = [];
    ls.forEach((l, i) => c.para(l, { wt: 'semi', font: 'texte', g: 'lignes', sub: k * half + i, gapK: K.courte - K.titre }).forEach((p) => paras.push(p)));
    return c.text({ x: z.x, y: z.y, w: z.w, h: z.h, paras, size: 20, min: 12, maxLines: 1, wt: 'semi', align: 'left', valign: 'middle', font: 'texte', lh: K.titre, name: 'Liste ' + (k + 1) });
  }).filter(Boolean);
  const fitted = Math.min.apply(null, boxes.map((b) => b.fitted));
  boxes.forEach((b) => { b.fitted = fitted; b.valign = 'top'; b.y = P(0, 20, 0, 0).y + (P(0, 0, 0, 60).h - textGeom(Object.assign({}, boxes[0], { valign: 'top' })).h) / 2; });
  const widest = (b) => Math.max.apply(null, b.paras.map((p) => wrapInfo(p.runs.map((r) => r.t).join(''), paraSize(b, p, b.fitted), heavy(paraWeight(b, p)), 99, paraTrack(b, p, paraSize(b, p, b.fitted)), roleOf(b, p)).widest));
  const iz = P(0, 33, 18, 34);
  const is = Math.min(iz.w, iz.h);
  const gapI = W * 0.08;
  const gapC = W * 0.06;
  const w1 = widest(boxes[0]);
  const w2 = boxes[1] ? widest(boxes[1]) : 0;
  const total = is + gapI + w1 + (boxes[1] ? gapC + w2 : 0);
  const x0 = Math.max(M, (W - total) / 2);
  iconVisual(c, { x: x0, y: iz.y + (iz.h - is) / 2, w: is, h: is }, c.slide.image, { g: 'visuel' });
  boxes[0].x = x0 + is + gapI;
  boxes[0].w = w1 + 0.3;
  if (boxes[1]) {
    boxes[1].x = boxes[0].x + w1 + gapC;
    boxes[1].w = Math.max(w2 + 0.3, 0.5);
  }
  c.groups = [G('visuel', KW.visuel), G('lignes', KW.lignes, { multi: false })];
};
V['A7/sur-photo'] = (c) => {
  const real = fullPhoto(c, photoSpec(c), { voile: c.slide.voile !== undefined ? Number(c.slide.voile) : 45, g: 'visuel' });
  const S = STYLE.A7;
  const lines = arr(c.t.lignes).length ? arr(c.t.lignes) : [c.f('lignes', 'lignes')];
  const pitchK = lines.length === 2 ? K.liste2 : K.liste;
  const fg = real ? 'FFFFFF' : c.P.fg;
  const paras = listParas(c, lines, { color: fg, activeColor: fg, idleColor: real ? 'C8C8C8' : c.P.fg2, font: 'titre', gapK: pitchK - K.titre });
  const t = centerBox(c, { x: S.x, w: S.w, cy: S.cy, paras, stages: [{ size: S.lignes[0], min: S.lignes[1], maxLines: 1 }, { size: S.lignes[1], min: 24, maxLines: 2 }], wt: 'semi', align: 'center', font: 'titre', color: fg, lh: K.titre, name: 'Liste' });
  c.kicker(t.g, { x: S.x, w: S.w, align: 'center', color: real ? 'E8E8E8' : undefined });
  c.groups = [G('visuel', KW.visuel), SUR, G('lignes', KW.lignes, { multi: true })];
};
V['A7/filet'] = (c) => {
  const z = P(6, 42, 88, 62);
  screenVisual(c, z, c.slide.image, { g: 'visuel', mode: 'cover', clip: { x: 0, y: 0, w: W, h: H }, radius: STYLE.schema.rayon, alignY: 'top' });
  const zl = P(50, 15, 40, 21);
  const lines = arr(c.t.lignes).slice(0, 4);
  const t = zlist(c, zl, lines.length ? lines : [c.f('lignes', 'lignes')], { size: 18, min: 12, k: K.courte, actif: Number(c.t.actif) || 0, maxLines: 1 });
  const f = P(48, 15, 0.3, 21);
  c.rect({ x: zl.x - 0.2, y: t.g.capTop - 0.04, w: 0.015, h: t.g.base - t.g.capTop + 0.08, fill: c.P.fg2, name: 'Filet', g: 'lignes' });
  c.kicker(t.g, { x: zl.x, w: zl.w, align: 'left' });
  c.groups = [G('visuel', KW.visuel), SUR, G('lignes', KW.lignes, { multi: true })];
  void f;
};

// A8 : pictogrammes au trait (cercle et coche du même trait, en accent), triangle d'alerte,
// pictogrammes fournis. Une ligne qui n'est qu'un [À FOURNIR] garde sa case vide.
function checkList(c, o) {
  const S = STYLE.A8;
  let lines = arr(c.t.lignes).slice(0, 7);
  if (!lines.length) lines = [c.f('lignes', 'lignes')];
  const n = lines.length;
  const size0 = o.size || S.lignes[0];
  const fg = o.color || c.P.fg;
  const lineParas = lines.map((l, i) => c.para(l, { wt: 'semi', font: 'texte', g: 'lignes', sub: i, color: fg }));
  const cap0 = capIn('texte', scalePt(size0, 'texte'));
  const avail = S.largeurMax - cap0 * (S.picto + S.ecart);
  let size = null;
  lineParas.forEach((ps) => {
    const s = c.fit({ paras: ps, w: avail, size: size0, min: S.lignes[1], maxLines: 1, wt: 'semi', font: 'texte' });
    if (s === null) c.warn('Ligne trop longue pour la liste à coches : raccourcissez-la (5 mots au plus).');
    const v = s === null ? scalePt(S.lignes[1], 'texte') : s;
    size = size === null ? v : Math.min(size, v);
  });
  const cap = capIn('texte', size);
  const pitch = K.liste * cap;
  const d = S.picto * cap * 1.08;
  const gap = S.ecart * cap;
  const tw = Math.max.apply(null, lineParas.map((ps) => wrapInfo(ps.map((p) => p.runs.map((r) => r.t).join('')).join(' '), size, true, 99, trackFor('texte', size), 'texte').widest));
  const x0 = Math.max(M, (W - (d + gap + tw)) / 2);
  const cy0 = S.cy - (n - 1) * pitch / 2;
  const stroke = Math.max(1.5, d * 0.09 * 72);
  const pictos = arr(c.t.pictos).length ? arr(c.t.pictos) : imagesOf(c);
  c.accentUsed = true;
  lineParas.forEach((ps, i) => {
    const base = cy0 + i * pitch + cap / 2;
    const iy = base - d + cap * 0.06;
    const aFournir = ps.some((p) => p.runs.some((r) => r.marker)) && ps.every((p) => p.runs.every((r) => r.marker || !r.t.trim()));
    const gi = { g: 'lignes', sub: i };
    const gc = { g: o.checksApart ? 'coches' : 'lignes', sub: i };
    const mode = o.mode;
    if (mode === 'picto' && pictos[i] && loadImg(c, pictos[i])) {
      visual(c, { x: x0, y: iy, w: d, h: d }, pictos[i], Object.assign({ kind: 'icone' }, gi));
    } else if (mode === 'alerte') {
      c.add(Object.assign({ k: 'path', pts: [[x0 + d / 2, iy + d * 0.04], [x0 + d * 0.98, iy + d * 0.92], [x0 + d * 0.02, iy + d * 0.92]], closed: true, stroke: c.P.accent, strokeW: stroke, join: 'round', name: 'Alerte ' + (i + 1) }, gi));
      c.rect(Object.assign({ x: x0 + d / 2 - d * 0.035, y: iy + d * 0.36, w: d * 0.07, h: d * 0.28, fill: c.P.accent, name: 'Alerte trait ' + (i + 1) }, gi));
      c.ellipse(Object.assign({ x: x0 + d / 2 - d * 0.045, y: iy + d * 0.7, w: d * 0.09, h: d * 0.09, fill: c.P.accent, name: 'Alerte point ' + (i + 1) }, gi));
    } else {
      c.ellipse(Object.assign({ x: x0 + stroke / 144, y: iy + stroke / 144, w: d - stroke / 72, h: d - stroke / 72, line: o.coche === false || aFournir ? c.P.line : c.P.accent, lineW: stroke, name: 'Cercle ' + (i + 1) }, gi));
      if (o.coche !== false && !aFournir) c.check(Object.assign({ cx: x0 + d / 2, cy: iy + d / 2, d: d * 0.92, color: c.P.accent, strokeW: stroke, name: 'Coche ' + (i + 1) }, gc));
    }
    c.line({ paras: ps, x: x0 + d + gap, w: Math.min(tw + 0.5, W - (x0 + d + gap) - 0.2), base, size, wt: 'semi', align: 'left', font: 'texte', color: fg, name: 'Ligne ' + (i + 1), g: 'lignes', sub: i });
  });
  const geo = listHeading(c, { capTop: cy0 - cap / 2, capH: cap, firstSize: size }, { x: x0, w: W - x0 - M, align: 'left', size: S.titre });
  c.kicker(geo, { x: x0, w: W - x0 - M, align: 'left' });
}
V['A8/coche-par-ligne'] = (c) => checkList(c, {});
V['A8/cercles-puis-coches'] = (c) => {
  checkList(c, { checksApart: true, coche: c.t.coche === false ? false : undefined });
  c.groups = [SUR, G('titre', KW.titre), G('lignes', /\b(?:lignes?|lines?|cercles?|circles?|points?|items?|cases?)\b/, { multi: true }), G('coches', /\b(?:coches?|checks?|ticks?|checkmarks?)\b/)];
};
V['A8/risque-puis-reponse'] = (c) => checkList(c, { mode: normKey(c.t.etat) === 'reponse' ? 'coche' : 'alerte' });
V['A8/picto-par-ligne'] = (c) => checkList(c, { mode: 'picto', size: 30 });
V['A8/sur-contenu'] = (c) => {
  const real = fullPhoto(c, photoSpec(c), { voile: c.slide.voile !== undefined ? Number(c.slide.voile) : VS.voile.contenu, g: 'visuel' });
  checkList(c, { color: real ? 'FFFFFF' : c.P.fg });
  c.groups = [G('visuel', KW.visuel), SUR, G('titre', KW.titre), G('lignes', KW.lignes, { multi: true })];
};

// A17 : citations (aucun portrait, aucun guillemet décoratif).
function quote(c, o) {
  let q = c.f('citation', 'citation').trim();
  if (o.guillemets && !/^[«"“]/.test(q) && !hasFournir(q)) q = c.lang === 'fr' ? '« ' + q + ' »' : '“' + q + '”';
  const z = o.z;
  const qt = topBox(c, { x: z.x, w: z.w, capTop: 0, paras: c.para(q, { wt: 'semi', font: 'titre', g: 'citation' }), size: o.size, min: o.min, maxTotal: o.maxTotal || 4, wt: 'semi', align: o.align, font: 'titre', lh: K.citation, balance: true, name: 'Citation' });
  let auteur = c.f('auteur', 'auteur');
  if (o.caps) auteur = String(auteur).toUpperCase();
  const za = o.za || z;
  const at = topBox(c, { x: za.x, w: za.w, capTop: 0, paras: c.para(auteur, { wt: o.caps ? 'semi' : 'regular', font: 'texte', color: o.accent ? c.P.accentTxt : c.P.fg2, g: 'auteur' }), size: o.asize, min: Math.min(o.asize, 14), maxTotal: 2, color: o.accent ? c.P.accentTxt : c.P.fg2, align: o.align, font: 'texte', lh: K.titre, balance: true, name: 'Auteur', g: 'auteur' });
  if (o.caps) at.it.paras.forEach((p) => { p.track = 0.08; });
  const ecart = o.ecart !== undefined ? o.ecart : STYLE.A17.ecart * o.asize / STYLE.A17.auteur[0];
  const total = (qt.g.base - qt.g.capTop) + ecart + (at.g.base - at.g.capTop);
  const q2 = placeTop(qt.it, (o.cy || STYLE.A17.cy) - total / 2);
  placeTop(at.it, q2.g.base + ecart);
  if (o.accent) c.accentUsed = true;
  c.kicker(q2.g, { x: z.x, w: z.w, align: o.align });
}
V['A17/courte'] = (c) => R.A17(c);
V['A17/longue'] = (c) => quote(c, { z: P(9.2, 22, 80, 44), size: 28, min: 22, maxTotal: 5, asize: 20, align: 'left', guillemets: false });
V['A17/source-accent'] = (c) => quote(c, { z: P(9.2, 30, 76, 30), size: 30, min: 24, asize: 18, align: 'left', caps: true, accent: true, ecart: 0.3, guillemets: false });
V['A17/centree-signature'] = (c) => {
  quote(c, { z: P(15, 40, 70, 12), za: P(30, 56, 40, 5), size: 24, min: 18, maxTotal: 2, asize: 20, align: 'center', ecart: 0.42, guillemets: true });
};

// A21 : synthés et cartes d'invité.
function people2(c) {
  const list = arr(c.t.personnes).length ? arr(c.t.personnes) : arr(c.t.intervenants).map((id) => c.env.people[id] || { nom: id });
  return list.map((p) => (typeof p === 'string' ? (c.env.people[p] || { nom: p }) : p));
}
function synthe(c, o) {
  const S = STYLE.A21;
  const real = o.photo === false ? false : fullPhoto(c, photoSpec(c), { voile: c.slide.voile !== undefined ? Number(c.slide.voile) : 0, g: 'visuel', label: c.lang === 'en' ? 'photo or video frame of the speaker' : 'photo ou plan de la personne' });
  const who = c.env.people[c.t.intervenant || c.slide.intervenant] || {};
  const list = o.list || [{ nom: c.t.nom || who.nom, fonction: c.t.fonction || who.role }];
  const size = scalePt(S.corps, 'texte');
  const light = o.clair;
  list.forEach((p, i) => {
    const right = o.right || (o.list && i === 1);
    const x = right ? (o.list ? W * 0.547 : W * 0.497) : S.x;
    const w = right ? W * 0.947 - x : (o.list ? 4.0 : 6);
    const fg = real && !light ? 'FFFFFF' : c.P.fg;
    const fg2 = real && !light ? 'FFFFFF' : (light ? c.P.fg : c.P.fg2);
    c.line({ text: str(p.nom) || c.f('nom', 'nom'), x, w, base: S.bases[0], size, wt: 'semi', color: fg, align: right ? 'right' : 'left', font: 'texte', name: 'Nom', g: 'nom', sub: o.list ? i : undefined });
    c.line({ text: str(p.fonction || p.role) || c.f('fonction', 'fonction'), x, w, base: S.bases[1], size, wt: 'regular', color: fg2, align: right ? 'right' : 'left', font: 'texte', name: 'Fonction', g: 'fonction', sub: o.list ? i : undefined });
  });
}
V['A21/gauche'] = (c) => synthe(c, {});
V['A21/droite'] = (c) => synthe(c, { right: true });
V['A21/double'] = (c) => {
  const list = people2(c).slice(0, 2);
  while (list.length < 2) list.push({});
  synthe(c, { list });
};
V['A21/sur-clair'] = (c) => synthe(c, { clair: true });
function guestCard(c, o) {
  o = o || {};
  const who = c.env.people[c.t.intervenant || c.slide.intervenant] || {};
  const zl = o.zl || P(29, 34, 42, 20);
  const im = loadImg(c, c.slide.logo_invite || c.t.logo || (o.portrait ? null : c.slide.image));
  if (im) putImage(c, im, fitRect(zl, im.info, 'contain'), { name: 'Logo invité', g: 'visuel' });
  else zt(c, zl, c.lang === 'en' ? '[TO PROVIDE: logo]' : '[À FOURNIR : logo]', { size: 22, min: 16, maxTotal: 1, g: 'visuel', name: 'Logo invité' });
  if (o.noName) return;
  zt(c, P(15, 70, 70, 5.5), str(c.t.nom || who.nom) || c.f('nom', 'nom'), { size: 22, min: 16, maxTotal: 1, font: 'texte', g: 'nom', name: 'Nom' });
  zt(c, P(15, 77, 70, 5), str(c.t.fonction || who.role) || c.f('fonction', 'fonction'), { size: 18, min: 14, maxTotal: 1, font: 'texte', wt: 'regular', color: c.P.fg2, g: 'fonction', name: 'Fonction' });
}
V['A21/carte-invite'] = (c) => guestCard(c);
// Carte-portrait : le logo à gauche, le portrait en noir et blanc à droite, fondu dans le fond du
// côté du logo. Sans portrait : la carte d'invité (le nom écrit remplace le visage).
V['A21/carte-portrait'] = (c) => {
  const im = loadImg(c, c.slide.image);
  if (!im) {
    if (c.slide.image) registerMissing(c, c.slide.image, 'photo', c.lang === 'en' ? 'black-and-white portrait' : 'portrait noir et blanc');
    guestCard(c);
    return;
  }
  const z = P(52, 0, 48, 100);
  putImage(c, im, fitRect(z, im.info, 'cover'), { clip: z, name: 'Portrait', g: 'visuel', gray: true });
  const fade = { x: z.x - 0.02, y: 0, w: z.w * 0.45, h: H };
  genImage(c, fade, c.P.bg, (x) => 1 - smooth01(x / fade.w), 'Fondu portrait', { key: 'fondu', ppi: 24, g: 'visuel' });
  guestCard(c, { zl: P(8, 34, 40, 28), portrait: true, noName: true });
};

// ---------------------------------------------------------------------------
// Produit et image : A9, A10, A12, A13, A18 (A22 à A25 sont des plans vidéo)
// ---------------------------------------------------------------------------
// Le type d'appareil d'une capture : slide.appareil, sinon ce que dit image.attendu.
function deviceType(c, spec, fallback) {
  const forced = normKey(c.slide.appareil || (c.imageSpec(spec) || {}).appareil);
  if (['telephone', 'tablette', 'portable', 'boitier'].includes(forced)) return forced;
  const t = normText(str((c.imageSpec(spec) || {}).attendu));
  if (/\b(tablettes?|tablets?)\b/.test(t)) return 'tablette';
  if (/\b(ordinateurs?|portables? (?:pc|mac)|laptops?|ecrans? d'ordinateur|desktop)\b/.test(t)) return 'portable';
  if (/\b(montres?|watch|boitiers?)\b/.test(t)) return 'boitier';
  return fallback;
}
const GV_A9 = [G('visuel', KW.visuel), SUR, G('titre', KW.titre), G('chiffre', KW.chiffre), G('libelle', KW.libelle), G('lignes', KW.lignes, { multi: true })];

V['A9/appareil-centre-mot'] = (c) => {
  drawDevice(c, P(37.5, 4.4, 25, 91), deviceType(c, c.slide.image, 'telephone'), { capture: c.slide.image, g: 'visuel' });
  const right = c.t.cote !== 'gauche';
  const z = right ? P(66, 40, 30, 20) : P(4, 40, 30, 20);
  const t = zt(c, z, c.f('titre', 'titre'), { size: 34, min: 26, maxTotal: 3, g: 'titre', lh: K.objet, name: 'Mot' });
  c.kicker(t.g, { x: z.x, w: z.w, align: 'center' });
  c.groups = GV_A9;
};
// L'objet coupé par le cadre : il sort de 10 % à gauche et en bas ; l'affirmation à droite.
V['A9/objet-coupe'] = (c) => {
  const right = c.t.cote === 'droite';
  // L'objet est agrandi pour sortir du cadre (10 % à gauche et en bas), même détouré au plus près.
  // Fiche : 58 à 62 % L, fond perdu sur 2 ou 3 bords ; le produit est calé sur sa partie opaque.
  const box = right ? P(42, 5, 80, 135) : P(-22, 5, 80, 135);
  productVisual(c, box, c.slide.image, {
    g: 'visuel', ombre: false, alignX: right ? 'left' : 'right', alignY: 'top',
    silBox: () => (right ? P(42, 7, 72, 118) : P(-14, 7, 72, 118)), ombreSil: false, exact: true
  });
  const z = right ? P(6, 38, 28, 24) : P(66, 38, 28, 24);
  const t = zt(c, z, c.f('titre', 'affirmation'), { size: 34, min: 26, maxTotal: 3, g: 'titre', lh: K.objet, name: 'Affirmation' });
  c.kicker(t.g, { x: z.x, w: z.w, align: 'center' });
  c.groups = GV_A9;
};
V['A9/objet-liste'] = (c) => {
  iconVisual(c, P(12, 31, 21, 37.5), c.slide.image, { g: 'visuel', glyph: 'carre' });
  const zl = P(45, 36, 50, 28);
  let lines = arr(c.t.lignes).slice(0, 5);
  if (!lines.length) lines = [c.f('lignes', 'lignes')];
  const t = zlist(c, zl, lines, { size: 24, k: K.courte, color: c.P.fg });
  let geo = t.g;
  if (tv(c, 'titre')) {
    const hd = c.line({ text: c.t.titre, x: zl.x, w: zl.w, base: geo.capTop - geo.capH * 1.1, size: scalePt(32, 'titre'), wt: 'semi', align: 'left', font: 'titre', name: 'Titre', g: 'titre' });
    geo = textGeom(hd);
  }
  c.kicker(geo, { x: zl.x, w: zl.w, align: 'left' });
  c.groups = GV_A9;
};
V['A9/objet-chiffre'] = (c) => {
  productVisual(c, P(-22, 4, 78, 135), c.slide.image, { g: 'visuel', ombre: false, halo: false, alignX: 'right', alignY: 'top', silBox: () => P(-14, 7, 70, 118), exact: true, ombreSil: false });
  c.accentUsed = true;
  const grad = gradOK(c);
  const z = P(58, 30, 34, 30);
  const h = zt(c, z, c.f('chiffre', 'chiffre'), { size: 110, min: 72, maxTotal: 1, noWrap: true, color: c.P.accentTxt, grad, g: 'chiffre', name: 'Chiffre' });
  if (grad) {
    hugText(h.it);
    h.it.grad = true;
  }
  const lib = zt(c, { x: z.x - 0.2, y: h.g.base + 0.18 + descGap(c, h), w: z.w + 0.4, h: 0.5 }, c.f('libelle', 'libellé'), { size: 20, min: 14, maxTotal: 2, font: 'texte', anchor: 'top', g: 'libelle', name: 'Libellé' });
  c.kicker(h.g, { x: z.x, w: z.w, align: 'center', size: 20 });
  srcLine(c, { x: z.x - 0.2, y: lib.g.base + 0.16, w: z.w + 0.4, h: 0.3 }, { g: 'libelle' });
  c.groups = GV_A9;
};
// Objet annoté : libellés de part et d'autre, reliés par un filet de 1 pt à l'objet.
V['A9/annotee'] = (c) => {
  const zo = P(30, 8, 40, 84);
  const r = productVisual(c, zo, c.slide.image, { g: 'visuel', silBox: (b) => ({ x: b.x + b.w * 0.18, y: b.y + b.h * 0.06, w: b.w * 0.64, h: b.h * 0.86 }) });
  const obj = r || { x: zo.x + zo.w * 0.18, y: zo.y, w: zo.w * 0.64, h: zo.h };
  const slots = [[6, 26, 'g'], [74, 44, 'd'], [6, 64, 'g'], [74, 20, 'd'], [74, 68, 'd']];
  arr(c.t.annotations).slice(0, 5).forEach((a, i) => {
    const txt = typeof a === 'string' ? a : str(a.texte || a.titre);
    const s = slots[i];
    const left = s[2] === 'g';
    const z = P(s[0], s[1], 20, 8);
    const t = zt(c, z, txt, { size: 20, min: 14, maxTotal: 2, font: 'texte', align: left ? 'right' : 'left', g: 'lignes', sub: i, name: 'Libellé ' + (i + 1) });
    const y = t.g.lines[0].c;
    const x1 = left ? z.x + z.w + 0.12 : obj.x + obj.w - obj.w * 0.12;
    const x2 = left ? obj.x + obj.w * 0.12 : z.x - 0.12;
    c.rect({ x: Math.min(x1, x2), y: y - 0.007, w: Math.abs(x2 - x1), h: 0.014, fill: c.P.fg2, name: 'Filet ' + (i + 1), g: 'lignes', sub: i });
    c.ellipse({ x: (left ? x2 : x1) - 0.035, y: y - 0.035, w: 0.07, h: 0.07, fill: c.P.fg2, name: 'Point ' + (i + 1), g: 'lignes', sub: i });
  });
  c.groups = GV_A9;
};
V['A9/empilee'] = (c) => {
  productVisual(c, P(34, 8, 32, 31), c.slide.image, { g: 'visuel' });
  const zt1 = P(15, 43, 70, 10);
  const t = zt(c, zt1, c.f('titre', 'nom'), { size: 32, min: 24, maxTotal: 1, g: 'titre', name: 'Nom' });
  const lines = arr(c.t.lignes).slice(0, 3);
  if (lines.length) zlist(c, { x: P(20, 0, 60, 0).x, y: t.g.base + 0.42, w: P(0, 0, 60, 0).w, h: 1.2 }, lines, { size: 24, k: K.courte, color: c.P.fg, wt: 'regular', align: 'center', anchor: 'top' });
  c.kicker(t.g, { x: zt1.x, w: zt1.w, align: 'center' });
  c.groups = GV_A9;
};

// A10 : la capture dans un appareil générique, ou nue.
V['A10/telephone-centre'] = (c) => { drawDevice(c, P(37.5, 4.4, 25, 91), 'telephone', { capture: c.slide.image, g: 'visuel' }); };
V['A10/tablette-centre'] = (c) => { drawDevice(c, P(14, 4.4, 72, 91), 'tablette', { capture: c.slide.image, g: 'visuel' }); };
V['A10/portable-centre'] = (c) => { drawDevice(c, P(7, 4.5, 86, 91), 'portable', { capture: c.slide.image, g: 'visuel' }); };
V['A10/zoom-serre'] = (c) => { drawDevice(c, P(28, -5, 46, 110), 'boitier', { capture: c.slide.image, g: 'visuel', screen: P(31, 12, 38, 76) }); };
V['A10/capture-nue'] = (c) => {
  const im = loadImg(c, c.slide.image);
  if (im) {
    // Une capture au format de l'écran (16:9 à 4 % près) passe à fond perdu ; sinon elle reste entière
    // (une interface coupée se lit comme une erreur de cadrage) : contenue sur 92 % H, coins arrondis.
    const box = { x: 0, y: 0, w: W, h: H };
    const ratio = im.info.w / im.info.h;
    if (Math.abs(ratio / (W / H) - 1) <= 0.04 || im.spec.ajustement === 'couvrir') {
      putImage(c, im, fitRect(box, im.info, 'cover'), { clip: box, name: 'Capture', g: 'visuel' });
      return;
    }
    const r = fitRect(grow(box, -W * 0.04, -H * 0.04), im.info, 'contain');
    putImage(c, im, r, { radius: STYLE.schema.rayon, name: 'Capture', g: 'visuel' });
    return;
  }
  const h = H * 0.85;
  screenVisual(c, { x: (W - h * 1.6) / 2, y: (H - h) / 2, w: h * 1.6, h }, c.slide.image, { g: 'visuel' });
};
V['A10/rangee'] = (c) => {
  const imgs = imagesOf(c);
  const type = deviceType(c, imgs[0] || c.slide.image, 'telephone');
  [10.5, 38, 65.5].forEach((x, i) => {
    drawDevice(c, P(x, 3, 24, 94), type, { capture: imgs[i] || (i === 0 ? c.slide.image : null), g: 'visuel', sub: i, mute: i !== 1, hi: [0, 1, 2][i], variant: ['liste', 'tableau', 'document'][i] });
  });
  c.groups = [G('visuel', KW.visuel, { multi: 'auto' })];
};

// A12 : vue intérieure, éclaté, flux.
// Pièce mise en avant d'un repli de vue intérieure : même gris que les autres, liseré d'accent et
// lueur d'accent floue (jamais un aplat d'accent atténué, qui vire au brun sur fond sombre).
function glowPart(c, b, rad, name, g) {
  const pad = Math.min(0.32, Math.max(0.16, Math.min(b.w, b.h) * 0.35));
  genImage(c, grow(b, pad, pad), c.P.accent, alphaAround(darkBg(c) ? 0.5 : 0.38, { x: pad, y: pad, w: b.w, h: b.h }, rad, pad * 0.32, 0.08), 'Lueur ' + name, Object.assign({ key: 'lueurpiece' + round2(pad) + round2(rad), ppi: 44 }, g));
  c.round(Object.assign({ x: b.x, y: b.y, w: b.w, h: b.h, fill: mix(c.P.bg, c.P.fg, darkBg(c) ? 0.16 : 0.1), line: c.P.accent, lineW: 1.5, radius: rad, name }, g));
}
V['A12/macro-matiere'] = (c) => {
  const box = { x: 0, y: 0, w: W, h: H };
  const im = loadImg(c, c.slide.image);
  if (im) {
    putImage(c, im, fitRect(box, im.info, 'cover'), { clip: box, name: 'Macro', g: 'visuel' });
    return;
  }
  missingVisual(c, c.slide.image, 'photo', c.lang === 'en' ? 'macro shot of the material' : 'macro de la matière', { g: 'visuel' }, () => {
    const dark = darkBg(c);
    c.rect({ x: 0, y: 0, w: W, h: H, fill: mix(c.P.bg, c.P.fg, dark ? 0.06 : 0.05), name: 'Schéma matière', g: 'visuel' });
    // Une bande de lumière rasante, en diagonale, en dégradé de transparence.
    const ang = -0.42;
    const ca = Math.cos(ang);
    const sa = Math.sin(ang);
    genImage(c, box, dark ? c.P.fg : 'FFFFFF', (x, y) => {
      const d = (x - W * 0.52) * sa - (y - H * 0.5) * ca;
      // Matière brossée : de fines stries parallèles, plus visibles dans la lumière.
      const band = Math.exp(-(d * d) / (2 * 0.55 * 0.55));
      const u = x * ca + y * sa;
      const v = -x * sa + y * ca;
      const strie = 0.5 + 0.5 * Math.sin(v * 140 + Math.sin(v * 23 + u * 0.7) * 2.2);
      return (dark ? 0.16 : 0.6) * band * (0.75 + 0.25 * strie) + (dark ? 0.05 : 0.2) * Math.exp(-((d - 1.4) * (d - 1.4)) / (2 * 0.25 * 0.25)) + (dark ? 0.025 : 0.06) * strie;
    }, 'Schéma lumière rasante', { g: 'visuel', key: 'rasante2', ppi: 48 });
  });
};
V['A12/capot-ouvert'] = (c) => {
  const z = P(14, 6, 72, 88);
  productVisual(c, z, c.slide.image, {
    g: 'visuel', label: c.lang === 'en' ? 'object with its cover open' : 'objet capot ouvert',
    repli: (b) => {
      const dark = darkBg(c);
      const shell = { x: b.x + b.w * 0.06, y: b.y + b.h * 0.08, w: b.w * 0.88, h: b.h * 0.84 };
      if (!dark) contactShadow(c, shell, { g: 'visuel' });
      // La coque : un fond plus sombre que l'objet, un liseré métallique ; les pièces au trait fin.
      c.round({ x: shell.x, y: shell.y, w: shell.w, h: shell.h, fill: mix(c.P.bg, dark ? '000000' : c.P.fg, dark ? 0.35 : 0.06), line: mix(c.P.bg, c.P.fg, dark ? 0.42 : 0.3), lineW: 1.5, radius: Math.min(shell.w, shell.h) * 0.1, name: 'Schéma coque', g: 'visuel' });
      const cells = [[0.05, 0.07, 0.5, 0.4], [0.59, 0.07, 0.36, 0.24], [0.59, 0.35, 0.36, 0.58], [0.05, 0.52, 0.24, 0.41], [0.33, 0.52, 0.22, 0.41]];
      cells.forEach((q, i) => {
        const b2 = { x: shell.x + shell.w * q[0], y: shell.y + shell.h * q[1], w: shell.w * q[2], h: shell.h * q[3] };
        if (i === 0) {
          glowPart(c, b2, 0.06, 'Schéma bloc en avant', { g: 'visuel' });
          return;
        }
        c.round({ x: b2.x, y: b2.y, w: b2.w, h: b2.h, fill: mix(c.P.bg, c.P.fg, (dark ? 0.08 : 0.05) + i * 0.012), line: mix(c.P.bg, c.P.fg, dark ? 0.28 : 0.22), lineW: 0.75, radius: 0.06, name: 'Schéma bloc', g: 'visuel' });
        // Détail au trait : deux ou trois filets parallèles, sans inscription.
        for (let k = 0; k < 3; k++) c.rect({ x: b2.x + b2.w * 0.14, y: b2.y + b2.h * (0.3 + k * 0.2), w: b2.w * (k === 1 ? 0.5 : 0.72), h: 0.012, fill: mix(c.P.bg, c.P.fg, dark ? 0.22 : 0.2), name: 'Schéma trait', g: 'visuel' });
      });
    }
  });
};
V['A12/eclate-axial'] = (c) => {
  const z = P(15, 0, 70, 100);
  let hot = null;
  productVisual(c, z, c.slide.image, {
    g: 'visuel', label: c.lang === 'en' ? 'exploded view along one axis' : 'éclaté le long d\'un axe',
    repli: () => {
      const dark = darkBg(c);
      const n = 5;
      // Des plaques fines et bien séparées le long d'un axe : on lit un éclaté, pas une pile.
      for (let i = n - 1; i >= 0; i--) {
        const pw = W * 0.34;
        const ph = H * 0.085;
        const x = W * 0.3 + i * W * 0.012;
        const y = H * 0.13 + i * H * 0.155;
        const isHot = i === 2;
        if (isHot) {
          glowPart(c, { x, y, w: pw, h: ph }, ph * 0.3, 'Schéma plaque en avant', { g: 'visuel' });
          hot = { x, y, w: pw, h: ph };
          continue;
        }
        const fill = mix(c.P.bg, c.P.fg, (dark ? 0.16 : 0.09) + i * 0.015);
        c.round({ x, y, w: pw, h: ph, fill, line: mix(fill, 'FFFFFF', dark ? 0.25 : 0.6), lineW: 0.75, radius: ph * 0.3, grad2: { from: mix(fill, 'FFFFFF', dark ? 0.14 : 0.4), to: mix(fill, '000000', dark ? 0.2 : 0.06), ang: 90 }, name: 'Schéma plaque', g: 'visuel' });
      }
    }
  });
  const label = tv(c, 'libelle') || tv(c, 'titre');
  if (label) {
    // L'étiquette à droite de la pièce mise en avant, reliée par un filet horizontal qui ne traverse
    // aucune autre pièce.
    const target = hot || { x: W * 0.36, y: H * 0.45, w: W * 0.34, h: 0.1 };
    const lx = target.x + target.w + 0.75;
    const zl = { x: lx, y: target.y + target.h / 2 - 0.2, w: W - M - lx, h: 0.4 };
    zt(c, zl, label, { size: 18, min: 12, maxTotal: 1, font: 'texte', align: 'left', g: 'note', name: 'Étiquette' });
    c.rect({ x: target.x + target.w + 0.12, y: target.y + target.h / 2 - 0.007, w: lx - 0.12 - (target.x + target.w + 0.12), h: 0.014, fill: c.P.fg2, name: 'Filet', g: 'note' });
  }
  c.groups = [G('visuel', KW.visuel), G('note', /\b(?:etiquettes?|labels?|filets?|libelles?|notes?)\b/)];
};
// Flux ou halo autour de la pièce : l'objet, puis le halo d'accent (seul accent de la slide).
V['A12/flux-lumiere'] = (c) => {
  const zo = P(35, 22, 30, 56);
  const flow = P(4, 26, 92, 48);
  // Le flux : des traînées d'accent en dégradé de transparence, de part et d'autre de la pièce.
  genImage(c, flow, c.P.accent, (x, y) => {
    const u = (x - flow.w / 2) / (flow.w / 2);
    const v = (y - flow.h / 2) / (flow.h / 2);
    const fade = Math.exp(-u * u * 1.6) * (1 - smooth01((Math.abs(u) - 0.75) / 0.25));
    let a = 0;
    [-0.55, -0.2, 0.15, 0.5].forEach((o, k) => {
      const yy = v - o - 0.12 * Math.sin(u * 2.2 + k);
      a += Math.exp(-(yy * yy) / (2 * 0.035 * 0.035)) * (0.55 - k * 0.07);
    });
    return a * fade + 0.22 * Math.exp(-(u * u + v * v) * 2.2);
  }, 'Flux', { g: 'note', key: 'flux', ppi: 40 });
  productVisual(c, zo, c.slide.image, { g: 'visuel', halo: false, ombre: false, ombreSil: false, haloSil: false });
  c.accentUsed = true;
  c.groups = [G('visuel', KW.visuel), G('note', /\b(?:flux|halos?|lumieres?|trainees?|faisceaux?)\b/)];
};

// A13 : produit seul. Ombre de contact sur fond clair, halo doux neutre sur fond sombre.
V['A13/centre-entier'] = (c) => {
  // Seule la hauteur est fixée (72 % H) ; la largeur suit la forme du produit.
  productVisual(c, P(10, 14, 80, 72), c.slide.image, { g: 'visuel', silBox: () => P(37, 14, 26, 72) });
};
V['A13/hero-coupe'] = (c) => {
  // Agrandi jusqu'à sortir du cadre : par le bas (produit en hauteur) ou par la droite (en largeur).
  productVisual(c, P(26, 8, 90, 145), c.slide.image, { g: 'visuel', alignX: 'left', alignY: 'top', ombre: false, halo: false, silBox: () => P(24, 10, 96, 112), exact: true, ombreSil: false });
};
V['A13/profil-levitation'] = (c) => {
  productVisual(c, P(14, 39, 72, 21), c.slide.image, { g: 'visuel', ombre: false, forme: 'bande', silBox: () => P(14, 46, 72, 7), exact: true, ombreSil: false });
};
V['A13/coloris'] = (c) => {
  const imgs = imagesOf(c);
  const sils = [P(19, 15, 28.4, 70), P(52.6, 21, 25, 62)];
  [[20, 10, 28, 80], [52, 10, 26, 80]].forEach((z, i) => {
    productVisual(c, P(z[0], z[1], z[2], z[3]), imgs[i] || (i === 0 ? c.slide.image : null), { g: 'visuel', sub: i, ton: i * 0.06, silBox: () => sils[i], exact: true });
  });
  c.groups = [G('visuel', KW.visuel, { multi: 'auto' })];
};

// A18 : photo plein cadre.
function photoNote(c, z, text, i) {
  if (!str(text).trim()) return;
  c.round({ x: z.x, y: z.y, w: z.w, h: z.h, fill: '000000', transparency: 45, radius: 0.08, name: 'Cartouche', g: 'note', sub: i });
  c.text({ x: z.x + 0.12, y: z.y + 0.06, w: z.w - 0.24, h: z.h - 0.12, text, size: 11, min: 9, color: 'FFFFFF', align: 'left', valign: 'middle', font: 'texte', lh: K.titre, name: 'Note', g: 'note', sub: i });
}
V['A18/usage'] = (c) => {
  fullPhoto(c, photoSpec(c), { g: 'visuel', label: c.lang === 'en' ? 'photo of the product in use' : 'photo d\'usage' });
  if (tv(c, 'note')) photoNote(c, P(70, 82, 25, 12), c.t.note);
};
V['A18/exemple-cartouche'] = (c) => {
  const real = fullPhoto(c, photoSpec(c), { g: 'visuel' });
  if (real) photoNote(c, P(70, 80, 25, 13), c.f('note', 'légende'));
};
V['A18/diptyque'] = (c) => {
  const imgs = imagesOf(c);
  const notes = arr(c.t.notes);
  [P(0, 0, 50, 100), P(50, 0, 50, 100)].forEach((z, i) => {
    const real = fullPhoto(c, imgs[i] || (i === 0 ? c.slide.image : null), { box: { x: z.x + (i ? 0.02 : 0), y: 0, w: z.w - 0.02, h: H }, g: 'visuel' });
    if (real && notes[i]) photoNote(c, i ? P(76, 82, 20, 12) : P(4, 82, 20, 12), notes[i], i);
  });
  c.groups = [G('visuel', KW.visuel), G('note', KW.note)];
};
V['A18/photo-titre'] = (c) => {
  const real = fullPhoto(c, photoSpec(c), { voile: c.slide.voile !== undefined ? Number(c.slide.voile) : VS.voile.photo, g: 'visuel' });
  const z = P(8, 36, 84, 23);
  const color = real ? 'FFFFFF' : c.P.fg;
  const t = zt(c, z, c.f('titre', 'titre'), { size: 72, min: 44, maxTotal: 2, color, point: true, g: 'titre', name: 'Titre' });
  c.kicker(t.g, { x: z.x, w: z.w, align: 'center', color: real ? 'E8E8E8' : undefined });
};
// A22 à A25 : plans de scène (vidéo, salle). En slide : la photo de la scène en plein cadre.
['A22/hall-ecran', 'A22/scene-mur', 'A22/panneau-verre', 'A23/mot-coupe', 'A23/contenu-lisible', 'A23/interface-geante', 'A23/slide-floue',
  'A24/large-centre', 'A24/taille-centre', 'A24/decor-sujet', 'A25/table-flux', 'A25/mains-fond-uni', 'A25/epaule', 'A25/table-haute', 'A25/tend-appareil'].forEach((k) => {
  V[k] = (c) => {
    c.warn(k.split('/')[0] + ' « ' + k.split('/')[1] + ' » est un plan de scène (vidéo ou salle) : en slide, il est rendu comme une photo plein cadre.');
    // La photo de la scène à fond perdu (repli doux sans personne dessinée), un titre éventuel en bas.
    const real = fullPhoto(c, photoSpec(c), { g: 'visuel', label: c.lang === 'en' ? 'photo of the scene' : 'photo de la scène' });
    if (tv(c, 'titre')) {
      if (real) gradientVeil(c, { x: 0, y: H * 0.55, w: W, h: H * 0.45 }, 0.6, 'bas', { g: 'titre' });
      const t = c.text({ x: M, y: H - 1.55, w: FULL_W, h: 1.15, text: c.t.titre, size: STYLE.A18.titre[0], min: STYLE.A18.titre[1], wt: 'semi', align: 'left', valign: 'bottom', color: real ? 'FFFFFF' : c.P.fg, font: 'titre', lh: K.titre, name: 'Titre', g: 'titre' });
      c.kicker(textGeom(t), { x: M, w: FULL_W, align: 'left', color: real ? 'E8E8E8' : undefined });
    }
  };
});

// ---------------------------------------------------------------------------
// Chiffres et preuves : A5, A6, A11, A15, A16
// ---------------------------------------------------------------------------
// Écart à ajouter sous un chiffre qui a un jambage (g, j, p, q, y), pour que le libellé ne le touche pas.
function descGap(c, h) {
  return /[gjpqyç,;]/.test(shownText(c, c.f('chiffre', 'chiffre'))) ? h.g.capH * 0.28 : 0;
}
// Le chiffre héros : en dégradé d'accent si permis, sinon accent uni ; resserré sur son texte.
function heroNumber(c, z, o) {
  o = o || {};
  const grad = o.grad !== false && gradOK(c);
  const color = o.color || c.P.accentTxt;
  const h = zt(c, z, c.f('chiffre', 'chiffre'), { size: o.size || 144, min: o.min || 110, maxTotal: 1, noWrap: true, color, grad: grad && !o.color, g: 'chiffre', name: 'Chiffre', font: 'titre' });
  if (grad && !o.color) {
    hugText(h.it);
    h.it.grad = true;
  }
  c.accentUsed = true;
  return h;
}
V['A5/centre'] = (c) => R.A5(c);
V['A5/bloc'] = (c) => {
  const S = STYLE.A5;
  const h = heroNumber(c, { x: M, y: P(0, 32.6, 0, 25.9).y, w: FULL_W, h: P(0, 0, 0, 25.9).h });
  // Libellé collé (haut des capitales à 63 % H) ; plus bas si le chiffre a un jambage (g, j, p, q, y).
  const desc = /[gjpqyç,;]/.test(shownText(c, c.f('chiffre', 'chiffre'))) ? h.g.base + h.g.capH * 0.32 : 0;
  const lib = zt(c, { x: S.libelleX, y: Math.max(H * 0.63, desc), w: S.libelleW, h: 0.6 }, c.f('libelle', 'libellé'), { size: 24, min: 18, maxTotal: 2, font: 'texte', anchor: 'top', g: 'libelle', name: 'Libellé' });
  c.kicker(h.g, { x: M, w: FULL_W, align: 'center', size: S.surtitre, ecart: S.surtitreEcart });
  c.sourceLine({ y: lib.g.base + 0.2, x: S.libelleX, w: S.libelleW, g: 'libelle' });
};
// Le chiffre à droite, le visuel coupé par le bord gauche (un écran reste entier).
V['A5/a-cote'] = (c) => {
  const spec = c.slide.image;
  const kind = placeholderKind(c, c.imageSpec(spec), str((c.imageSpec(spec) || {}).attendu), {});
  const im = loadImg(c, spec);
  if (kind === 'interface' || kind === 'carte') screenVisual(c, P(5, 14, 48, 72), spec, { g: 'visuel', mode: im ? 'cover' : 'contain', clip: im ? undefined : undefined });
  else if (kind === 'appareil') drawDevice(c, P(14, 4.4, 25, 91), 'telephone', { capture: spec, g: 'visuel' });
  else productVisual(c, P(-24, 5, 78, 132), spec, { g: 'visuel', alignX: 'right', alignY: 'top', ombre: false, silBox: () => P(-14, 8, 66, 112), exact: true, ombreSil: false });
  const z = P(58, 34, 36, 20.9);
  const h = heroNumber(c, z, { size: 116, min: hasFournir(c.f('chiffre', 'chiffre')) ? 60 : 88 });
  const lib = zt(c, { x: P(58, 0, 0, 0).x, y: h.g.base + 0.3 + descGap(c, h), w: P(0, 0, 36, 0).w, h: 0.6 }, c.f('libelle', 'libellé'), { size: 22, min: 16, maxTotal: 2, font: 'texte', anchor: 'top', g: 'libelle', name: 'Libellé' });
  c.kicker(h.g, { x: z.x, w: z.w, align: 'center', size: 22, ecart: STYLE.A5.surtitreEcart });
  srcLine(c, { x: z.x, y: lib.g.base + 0.18, w: z.w, h: 0.3 }, { g: 'libelle' });
  c.groups = [G('visuel', KW.visuel), SUR, G('chiffre', KW.chiffre), G('libelle', KW.libelle)];
};
// Le chiffre blanc sur une photo floutée et assombrie (la photo se fournit déjà floutée) ; sans
// photo, la variante « centre » sur le fond du bloc.
V['A5/sur-photo'] = (c) => {
  const spec = photoSpec(c);
  if (!loadImg(c, spec)) {
    if (spec) registerMissing(c, spec, 'photo', c.lang === 'en' ? 'blurred photo of the place or the use' : 'photo floutée du lieu ou de l\'usage');
    R.A5(c);
    return;
  }
  fullPhoto(c, spec, { voile: c.slide.voile !== undefined ? Number(c.slide.voile) : VS.voile.chiffre, g: 'visuel' });
  const h = heroNumber(c, P(6, 31.5, 88, 25.9), { color: 'FFFFFF', grad: false });
  const lib = zt(c, P(8, 72.2, 84, 4.3), c.f('libelle', 'libellé'), { size: 24, min: 18, maxTotal: 1, font: 'texte', color: 'FFFFFF', g: 'libelle', name: 'Libellé' });
  c.kicker(h.g, { x: M, w: FULL_W, align: 'center', size: 24, color: 'E8E8E8', ecart: STYLE.A5.surtitreEcart });
  srcLine(c, { x: P(8, 0, 0, 0).x, y: lib.g.base + 0.2, w: P(0, 0, 84, 0).w, h: 0.3 }, { color: 'C8C8C8', g: 'libelle' });
  c.groups = [G('visuel', KW.visuel), SUR, G('chiffre', KW.chiffre), G('libelle', KW.libelle)];
};
// Chiffre dans un anneau lumineux : anneau d'accent (trait 2,2 % H) et halos flous concentriques.
V['A5/objet-anneau'] = (c) => {
  const z = P(33.3, 20.3, 33.3, 59.4);
  const d = Math.min(z.w, z.h);
  const cx = z.x + z.w / 2;
  const cy = z.y + z.h / 2;
  const tw = H * 0.022;
  const glow = { x: cx - d * 0.85, y: cy - d * 0.85, w: d * 1.7, h: d * 1.7 };
  const r0 = d / 2 - tw / 2;
  genImage(c, glow, c.P.accent, (x, y) => alphaRing(0.3, r0, d * 0.05, glow)(x, y) + alphaRing(0.16, r0, d * 0.16, glow)(x, y) + alphaRing(0.08, r0 * 1.2, d * 0.28, glow)(x, y), 'Halo anneau', { g: 'visuel', key: 'anneau', ppi: 44 });
  c.ellipse({ x: cx - d / 2 + tw / 2, y: cy - d / 2 + tw / 2, w: d - tw, h: d - tw, line: c.P.accent, lineW: tw * 72, name: 'Anneau', g: 'visuel' });
  c.accentUsed = true;
  const fg = darkBg(c) ? 'FFFFFF' : c.P.fg;
  const h = zt(c, P(36, 40.3, 28, 12.9), c.f('chiffre', 'durée'), { size: 72, min: 40, maxTotal: 1, noWrap: true, color: fg, g: 'chiffre', name: 'Chiffre' });
  if (tv(c, 'libelle')) zt(c, { x: z.x + d * 0.15, y: h.g.base + 0.12, w: d * 0.7, h: 0.5 }, c.t.libelle, { size: 34, min: 20, maxTotal: 1, font: 'texte', color: fg, anchor: 'top', g: 'libelle', name: 'Unité' });
  c.kicker({ capTop: z.y - 0.1, capH: 0.5, firstSize: 48 }, { x: M, w: FULL_W, align: 'center', size: 20, accent: false });
  srcLine(c, { x: M, y: z.y + z.h + 0.2, w: FULL_W, h: 0.3 }, { g: 'libelle' });
  c.groups = [G('visuel', /\b(?:anneaux?|rings?|cercles?|circles?)\b/), SUR, G('chiffre', KW.chiffre), G('libelle', KW.libelle)];
};
// Chiffre dans une jauge pleine : pilule d'accent (rayon 28 % de sa hauteur) et plot à droite.
V['A5/objet-jauge'] = (c) => {
  const z = P(36, 37, 31, 26);
  const plot = { x: z.x + z.w + 0.05, y: z.y + z.h / 2 - H * 0.04, w: W * 0.016, h: H * 0.08 };
  const ring = grow(z, 0.07, 0.07);
  c.round({ x: ring.x, y: ring.y, w: ring.w, h: ring.h, line: mix(c.P.fg, c.P.bg, 0.45), lineW: 3, radius: ring.h * 0.3, name: 'Jauge contour', g: 'visuel' });
  // Chiffre à fournir : la jauge reste vide (un liseré d'accent), pour que le marqueur estompé se
  // lise sur le fond et non sur l'accent ; elle se remplit quand le chiffre arrive.
  const empty = hasFournir(c.f('chiffre', 'autonomie'));
  if (empty) c.round({ x: z.x, y: z.y, w: z.w, h: z.h, line: c.P.accent, lineW: 2, radius: z.h * 0.28, name: 'Jauge', g: 'visuel' });
  else c.round({ x: z.x, y: z.y, w: z.w, h: z.h, fill: c.P.accent, radius: z.h * 0.28, name: 'Jauge', g: 'visuel' });
  c.round({ x: plot.x + 0.07, y: plot.y, w: plot.w, h: plot.h, fill: mix(c.P.fg, c.P.bg, 0.45), radius: plot.w / 2, name: 'Jauge plot', g: 'visuel' });
  c.accentUsed = true;
  const on = empty ? c.P.fg : readableOn(c.P.accent, c.T.fondSombre, 'FFFFFF');
  zt(c, P(38.5, 37, 26, 26), c.f('chiffre', 'autonomie'), { size: 54, min: 32, maxTotal: 1, noWrap: true, color: on, g: 'chiffre', name: 'Chiffre' });
  if (tv(c, 'libelle')) zt(c, { x: 0.4, y: z.y, w: z.x - 0.4 - 0.25, h: z.h }, c.t.libelle, { size: 54, min: 28, maxTotal: 1, align: 'right', g: 'libelle', name: 'Libellé' });
  srcLine(c, { x: M, y: ring.y + ring.h + 0.3, w: FULL_W, h: 0.3 }, { g: 'libelle' });
  c.groups = [G('visuel', /\b(?:jauges?|gauges?|batteries?|piles?)\b/), G('chiffre', KW.chiffre), G('libelle', KW.libelle)];
};
// Chiffre au trait : contour d'accent de 2,5 pt, sans remplissage, lueur de 4 pt à 40 %.
V['A5/contour'] = (c) => {
  const S = STYLE.A5;
  const h = zt(c, P(10, 32.6, 80, 25.9), c.f('chiffre', 'chiffre'), { size: 144, min: 110, maxTotal: 1, noWrap: true, color: c.P.accentTxt, g: 'chiffre', name: 'Chiffre' });
  if (!hasFournir(c.t.chiffre)) h.it.outline = { color: c.P.accent, pt: 2.5, glow: 4, glowA: 0.4 };
  c.accentUsed = true;
  // Comme « bloc » : le libellé descend sous un chiffre qui a un jambage (g, j, p, q, y).
  const desc = /[gjpqyç,;]/.test(shownText(c, c.f('chiffre', 'chiffre'))) ? h.g.base + h.g.capH * 0.32 : 0;
  const lib = zt(c, { x: S.libelleX, y: Math.max(H * 0.63, desc), w: S.libelleW, h: 0.6 }, c.f('libelle', 'libellé'), { size: 24, min: 18, maxTotal: 2, font: 'texte', color: darkBg(c) ? 'FFFFFF' : c.P.fg, anchor: 'top', g: 'libelle', name: 'Libellé' });
  c.kicker(h.g, { x: M, w: FULL_W, align: 'center', size: S.surtitre, ecart: S.surtitreEcart });
  c.sourceLine({ y: lib.g.base + 0.2, x: S.libelleX, w: S.libelleW, g: 'libelle' });
};

// A6 : barres fines, libellé au-dessus, seule l'étiquette d'écart écrite au bout de la barre de soi.
V['A6/barres'] = (c) => {
  const zt0 = P(6, 8.9, 88, 5);
  const t = zt(c, zt0, c.f('titre', 'grandeur mesurée'), { size: 28, min: 20, maxTotal: 1, anchor: 'top', g: 'titre', name: 'Titre' });
  c.kicker(t.g, { x: zt0.x, w: zt0.w, align: 'center' });
  c.accentUsed = true;
  let bars = arr(c.t.barres).slice(0, 4);
  if (!bars.length) bars = [{ libelle: c.f('barres', 'barres') }];
  const vals = bars.map((b) => Number(b.valeur));
  const known = vals.every((v) => isFinite(v) && v > 0);
  const maxV = known ? Math.max.apply(null, vals) : 1;
  const n = bars.length;
  const pitch = H * 0.145;
  const mid = n <= 2 ? H * 0.583 : H * 0.52;
  const X0 = W * 0.15;
  const LEN = W * 0.7;
  const th = H * 0.011;
  const showValues = c.t.afficher_valeurs === undefined ? ['valeurs', 'graduee', 'exigee'].includes(c.env.pub.graduation) : !!c.t.afficher_valeurs;
  let lastY = 0;
  bars.forEach((b, i) => {
    const hl = !!b.mise_en_avant;
    const by = mid + (i - (n - 1) / 2) * pitch;
    const len = known ? Math.max(th * 2, vals[i] / maxV * LEN) : LEN;
    const lab = str(b.libelle) || c.f('_', 'libellé');
    c.line({ text: lab, x: X0, w: LEN * 0.62, base: by - H * 0.03, size: scalePt(23, 'texte'), wt: 'semi', color: hl ? c.P.fg : c.P.fg2, align: 'left', font: 'texte', name: 'Libellé barre ' + (i + 1), g: 'barres', sub: i });
    if (known) c.round({ x: X0, y: by - th / 2, w: len, h: th, fill: hl ? c.P.accent : c.P.other, radius: th / 2, name: 'Barre ' + (i + 1), g: 'barres', sub: i });
    else c.add({ k: 'path', pts: [[X0, by], [X0 + len, by]], stroke: c.P.other, strokeW: 2, dash: 'sysDot', cap: 'rnd', name: 'Barre ' + (i + 1), g: 'barres', sub: i });
    let et = b.etiquette !== undefined ? String(b.etiquette) : (showValues && known ? String(b.valeur) + (c.t.unite ? ' ' + c.t.unite : '') : '');
    if (!known && hl && !et) et = c.lang === 'en' ? '[TO PROVIDE: gap]' : '[À FOURNIR : écart]';
    if (et) {
      // L'étiquette finit au bout de la barre ; si la barre est trop courte pour la porter sans toucher
      // le libellé, elle finit au bout de la piste (même ligne de base), comme une colonne de valeurs.
      const ps = scalePt(23, 'texte');
      const nameW = textWidth(shownText(c, lab), ps, true, trackFor('texte', ps), 'texte');
      const etW = textWidth(shownText(c, et), ps, true, trackFor('texte', ps), 'texte');
      const end = X0 + len - etW < X0 + nameW + 0.3 ? X0 + LEN : X0 + len;
      c.line({ text: et, x: end - 3.2, w: 3.2, base: by - H * 0.03, size: ps, wt: 'semi', color: hl ? c.P.fg : c.P.fg2, align: 'right', font: 'texte', name: 'Valeur barre ' + (i + 1), g: 'barres', sub: i });
    }
    lastY = by;
  });
  if (tv(c, 'axe')) c.line({ text: c.t.axe, x: X0, w: LEN, base: lastY + H * 0.08, size: scalePt(16, 'texte'), wt: 'regular', color: c.P.fg2, align: 'left', font: 'texte', name: 'Sens de lecture' });
  srcLine(c, P(6, 91, 88, 4));
};
// Lissage d'une série (Catmull-Rom), pour une courbe sans graduation.
function smoothPts(pts, k) {
  if (pts.length < 3) return pts;
  const out = [];
  for (let i = 0; i < pts.length - 1; i++) {
    const p0 = pts[Math.max(0, i - 1)];
    const p1 = pts[i];
    const p2 = pts[i + 1];
    const p3 = pts[Math.min(pts.length - 1, i + 2)];
    for (let s = 0; s < k; s++) {
      const t = s / k;
      const t2 = t * t;
      const t3 = t2 * t;
      out.push([0, 1].map((j) => 0.5 * ((2 * p1[j]) + (-p0[j] + p2[j]) * t + (2 * p0[j] - 5 * p1[j] + 4 * p2[j] - p3[j]) * t2 + (-p0[j] + 3 * p1[j] - 3 * p2[j] + p3[j]) * t3)));
    }
  }
  out.push(pts[pts.length - 1]);
  return out;
}
// Courbes sur deux axes, sans graduation : axes en filets gris, noms des axes, séries de
// l'utilisateur (soi en accent, l'autre en gris). Sans données : axes et noms posés, un [À FOURNIR].
V['A6/deux-axes'] = (c) => {
  const zt0 = P(20, 7.5, 70, 5);
  const t = zt(c, zt0, c.f('titre', 'grandeur mesurée'), { size: 28, min: 20, maxTotal: 1, anchor: 'top', g: 'titre', name: 'Titre' });
  c.kicker(t.g, { x: zt0.x, w: zt0.w, align: 'center' });
  c.accentUsed = true;
  const A = { x0: W * 0.2, y0: H * 0.18, x1: W * 0.9, y1: H * 0.86 };
  const axis = mix(c.P.fg, c.P.bg, 0.7);
  c.rect({ x: A.x0, y: A.y0, w: 0.02, h: A.y1 - A.y0, fill: axis, name: 'Axe vertical', g: 'titre' });
  c.rect({ x: A.x0, y: A.y1 - 0.01, w: A.x1 - A.x0, h: 0.02, fill: axis, name: 'Axe horizontal', g: 'titre' });
  const axeY = tv(c, 'axe_y');
  const axeX = tv(c, 'axe_x') || tv(c, 'axe');
  if (axeY) {
    const ty = c.text({ x: W * 0.02, y: H * 0.46, w: W * 0.165, h: 0.5, text: axeY, size: 16, min: 12, maxTotal: 2, wt: 'semi', color: c.P.fg2, align: 'right', valign: 'top', font: 'texte', lh: K.titre, name: 'Axe vertical nom', g: 'titre' });
    if (tv(c, 'sens_y')) c.text({ x: W * 0.02, y: ty.y + 0.38, w: W * 0.165, h: 0.3, text: c.t.sens_y, size: 10, min: 9, maxTotal: 2, color: c.P.fg2, align: 'right', valign: 'top', font: 'texte', lh: K.titre, name: 'Axe vertical sens', g: 'titre' });
  }
  if (axeX) {
    c.text({ x: A.x0, y: A.y1 + 0.1, w: A.x1 - A.x0, h: 0.3, text: axeX, size: 16, min: 12, maxLines: 1, wt: 'semi', color: c.P.fg2, align: 'center', valign: 'top', font: 'texte', lh: K.titre, name: 'Axe horizontal nom', g: 'titre' });
    if (tv(c, 'sens_x')) c.text({ x: A.x0, y: A.y1 + 0.36, w: A.x1 - A.x0, h: 0.22, text: c.t.sens_x, size: 10, min: 9, maxLines: 1, color: c.P.fg2, align: 'center', valign: 'top', font: 'texte', lh: K.titre, name: 'Axe horizontal sens', g: 'titre' });
  }
  const series = arr(c.t.series).filter((s) => s && arr(s.points).length >= 2);
  if (!series.length) {
    zt(c, { x: A.x0, y: A.y0, w: A.x1 - A.x0, h: A.y1 - A.y0 }, c.lang === 'en' ? '[TO PROVIDE: curves]' : '[À FOURNIR : courbes]', { size: 28, min: 20, maxTotal: 1, g: 'barres', name: 'Courbes' });
    srcLine(c, P(6, 94, 88, 4));
    return;
  }
  const norm = series.map((s) => arr(s.points).map((p, i, all) => (Array.isArray(p) ? [Number(p[0]), Number(p[1])] : [i / Math.max(1, all.length - 1), Number(p)])));
  const xs = [].concat.apply([], norm.map((s) => s.map((p) => p[0])));
  const ys = [].concat.apply([], norm.map((s) => s.map((p) => p[1])));
  const xmin = Math.min.apply(null, xs);
  const xmax = Math.max.apply(null, xs);
  const ymin = Math.min(0, Math.min.apply(null, ys));
  const ymax = Math.max.apply(null, ys);
  const PX = { x0: A.x0 + 0.35, x1: A.x1 - 0.2, y0: A.y0 + 0.5, y1: A.y1 - 0.25 };
  const map = (p) => [PX.x0 + (p[0] - xmin) / Math.max(1e-9, xmax - xmin) * (PX.x1 - PX.x0), PX.y1 - (p[1] - ymin) / Math.max(1e-9, ymax - ymin) * (PX.y1 - PX.y0)];
  // L'autre d'abord (dessous), soi ensuite.
  const order = series.map((s, i) => i).sort((a, b) => (series[a].mise_en_avant ? 1 : 0) - (series[b].mise_en_avant ? 1 : 0));
  order.forEach((i, k) => {
    const s = series[i];
    const hl = !!s.mise_en_avant;
    const pts = smoothPts(norm[i].map(map), 8);
    c.add({ k: 'path', pts, stroke: hl ? c.P.accent : c.P.other, strokeW: H * 0.009 * 72, cap: 'rnd', join: 'round', name: 'Courbe ' + (k + 1), g: 'barres', sub: k });
    const end = pts[pts.length - 1];
    const lab = str(s.libelle);
    if (lab) c.text({ x: end[0] - 2.4, y: end[1] - 0.42, w: 2.4, h: 0.32, text: lab, size: 16, min: 12, maxTotal: 2, wt: 'semi', color: hl ? c.P.fg : c.P.fg2, align: 'right', valign: 'bottom', font: 'texte', lh: K.titre, name: 'Série ' + (k + 1), g: 'barres', sub: k });
  });
  srcLine(c, P(6, 94, 88, 4));
  c.groups = [SUR, G('titre', /\b(?:titres?|axes?|titles?)\b/), G('barres', /\b(?:courbes?|curves?|series?|lignes?|lines?)\b/, { multi: true })];
};
// Deux anneaux de part : piste à 15 %, arc sur la part fournie (gris pour l'autre, accent pour soi).
function arcPts(cx, cy, r, a0, a1, n) {
  const pts = [];
  for (let i = 0; i <= n; i++) {
    const a = a0 + (a1 - a0) * i / n;
    pts.push([cx + r * Math.cos(a), cy + r * Math.sin(a)]);
  }
  return pts;
}
V['A6/anneaux'] = (c) => {
  let parts = arr(c.t.barres).slice(0, 2);
  while (parts.length < 2) parts.push({});
  // L'autre à gauche, soi à droite.
  parts = parts.slice().sort((a, b) => (a.mise_en_avant ? 1 : 0) - (b.mise_en_avant ? 1 : 0));
  c.accentUsed = true;
  [[14, 31], [39, 31]].forEach((pos, i) => {
    const p = parts[i];
    const hl = !!p.mise_en_avant;
    const z = P(pos[0], pos[1], 21.5, 38);
    const d = Math.min(z.w, z.h);
    const cx = z.x + z.w / 2;
    const cy = z.y + z.h / 2;
    const tw = H * 0.008 * 1.6;
    const r = d / 2 - tw;
    c.ellipse({ x: cx - r, y: cy - r, w: 2 * r, h: 2 * r, line: mix(c.P.fg, c.P.bg, 0.85), lineW: tw * 72, name: 'Piste ' + (i + 1), g: 'barres', sub: i });
    const v = Number(p.valeur);
    const frac = isFinite(v) && v > 0 ? clamp(v > 1 ? v / 100 : v, 0, 1) : 0;
    if (frac > 0) c.add({ k: 'path', pts: arcPts(cx, cy, r, -Math.PI / 2, -Math.PI / 2 + frac * 2 * Math.PI, Math.max(8, Math.round(frac * 90))), stroke: hl ? c.P.accent : c.P.other, strokeW: tw * 72, cap: 'rnd', name: 'Part ' + (i + 1), g: 'barres', sub: i });
    const val = p.etiquette !== undefined ? String(p.etiquette) : (frac > 0 ? '' : (c.lang === 'en' ? '[TO PROVIDE: share]' : '[À FOURNIR : part]'));
    const vt = zt(c, { x: cx - r * 0.8, y: cy - 0.4, w: r * 1.6, h: 0.6 }, val || ' ', { size: 40, min: 24, maxTotal: 1, noWrap: true, color: hl ? c.P.accentTxt : c.P.fg2, g: 'barres', sub: i, name: 'Valeur ' + (i + 1) });
    if (str(p.libelle)) zt(c, { x: cx - r * 0.8, y: vt.g.base + 0.12, w: r * 1.6, h: 0.3 }, p.libelle, { size: 14, min: 10, maxTotal: 2, font: 'texte', color: c.P.fg2, anchor: 'top', g: 'barres', sub: i, name: 'Nom ' + (i + 1) });
  });
  const zt0 = P(64, 40, 32, 20);
  const t = zt(c, zt0, c.f('titre', 'grandeur'), { size: 40, min: 26, maxTotal: 3, align: 'left', g: 'titre', name: 'Titre' });
  c.kicker(t.g, { x: zt0.x, w: zt0.w, align: 'left' });
  srcLine(c, P(6, 92, 88, 4));
  c.groups = [SUR, G('titre', KW.titre), G('barres', /\b(?:anneaux?|rings?|parts?|barres?)\b/, { multi: true })];
};
// Frise des générations et saut de soi.
V['A6/frise'] = (c) => {
  const zt0 = P(6, 8.3, 88, 5);
  const t = zt(c, zt0, c.f('titre', 'grandeur mesurée'), { size: 28, min: 20, maxTotal: 1, anchor: 'top', g: 'titre', name: 'Titre' });
  c.kicker(t.g, { x: zt0.x, w: zt0.w, align: 'center' });
  c.accentUsed = true;
  const axis = mix(c.P.fg, c.P.bg, 0.7);
  const X0 = W * 0.127;
  c.rect({ x: X0, y: H * 0.16, w: 0.02, h: H * 0.68, fill: axis, name: 'Axe vertical', g: 'titre' });
  c.rect({ x: X0, y: H * 0.84 - 0.01, w: W * 0.743, h: 0.02, fill: axis, name: 'Axe horizontal', g: 'titre' });
  const n = clamp(Number(c.t.generations) || arr(c.t.jalons).length || 5, 3, 6);
  const pts = [];
  for (let i = 0; i < n; i++) pts.push([W * (0.17 + i * (0.66 / (n - 1 || 1))), H * (0.69 - i * 0.012)]);
  c.add({ k: 'path', pts, stroke: c.P.other, strokeW: 1.5, name: 'Ligne des générations', g: 'barres' });
  const gs = W * 0.035;
  pts.forEach((p, i) => {
    c.round({ x: p[0] - gs / 2, y: p[1] - gs / 2, w: gs, h: gs, fill: c.P.bg, line: c.P.other, lineW: 1.5, radius: gs * 0.2, name: 'Génération ' + (i + 1), g: 'barres' });
    c.round({ x: p[0] - gs * 0.22, y: p[1] - gs * 0.22, w: gs * 0.44, h: gs * 0.44, line: c.P.other, lineW: 1, radius: gs * 0.06, name: 'Génération cœur ' + (i + 1), g: 'barres' });
  });
  const per = arr(c.t.periodes);
  if (per.length) {
    c.line({ text: str(per[0]), x: pts[0][0] - 0.6, w: 1.2, base: H * 0.895, size: scalePt(16, 'texte'), wt: 'regular', color: c.P.fg2, align: 'center', font: 'texte', name: 'Période début', g: 'barres' });
    if (per[1]) c.line({ text: str(per[per.length - 1]), x: pts[n - 1][0] - 0.6, w: 1.2, base: H * 0.895, size: scalePt(16, 'texte'), wt: 'regular', color: c.P.fg2, align: 'center', font: 'texte', name: 'Période fin', g: 'barres' });
  }
  // La tuile de soi : carré sombre au liseré d'accent lumineux, son nom dedans.
  const last = pts[n - 1];
  const tile = { x: last[0] - W * 0.0365, y: H * 0.23, w: W * 0.073, h: W * 0.073 };
  const glowB = grow(tile, 0.35, 0.35);
  genImage(c, glowB, c.P.accent, alphaAround(0.55, { x: 0.35, y: 0.35, w: tile.w, h: tile.h }, tile.w * 0.18, 0.09, 0), 'Halo tuile', { g: 'chiffre', key: 'halotuile', ppi: 60 });
  c.round({ x: tile.x, y: tile.y, w: tile.w, h: tile.h, fill: mix(c.T.fondSombre, '000000', 0.4), line: c.P.accent, lineW: 1.5, radius: tile.w * 0.18, name: 'Tuile de soi', g: 'chiffre' });
  zt(c, grow(tile, -0.06, -0.06), str(c.t.nom) || ' ', { size: 16, min: 9, maxTotal: 2, font: 'texte', color: 'FFFFFF', g: 'chiffre', name: 'Nom de soi' });
  c.rect({ x: last[0] - 0.012, y: tile.y + tile.h + 0.08, w: 0.024, h: last[1] - gs / 2 - (tile.y + tile.h + 0.16), fill: c.P.accent, name: 'Flèche', g: 'chiffre' });
  c.add({ k: 'path', pts: [[last[0] - 0.07, tile.y + tile.h + 0.18], [last[0], tile.y + tile.h + 0.08], [last[0] + 0.07, tile.y + tile.h + 0.18]], stroke: c.P.accent, strokeW: 1.7, cap: 'rnd', join: 'round', name: 'Flèche pointe', g: 'chiffre' });
  const ch = tv(c, 'chiffre') ? c.t.chiffre : (c.lang === 'en' ? '[TO PROVIDE: gap]' : '[À FOURNIR : écart]');
  zt(c, { x: last[0] - 0.15 - 2.6, y: H * 0.45, w: 2.6, h: H * 0.094 }, ch, { size: 52, min: 28, maxTotal: 1, noWrap: true, align: 'right', color: c.P.accentTxt, g: 'chiffre', name: 'Écart' });
  srcLine(c, P(6, 94, 88, 4));
  c.groups = [SUR, G('titre', KW.titre), G('barres', /\b(?:generations?|jalons?|lignes?|frises?)\b/), G('chiffre', /\b(?:tuiles?|soi|fleches?|ecarts?|chiffres?|sauts?)\b/)];
};
// Tableau de rangs à logos, source toujours visible. Rien n'est dessiné à la place d'un rang.
V['A6/classement'] = (c) => {
  const zt0 = P(6, 11.9, 88, 5.8);
  const t = zt(c, zt0, c.f('titre', 'classement'), { size: 32, min: 22, maxTotal: 1, anchor: 'top', g: 'titre', name: 'Titre' });
  c.kicker(t.g, { x: zt0.x, w: zt0.w, align: 'center' });
  const cols = arr(c.t.colonnes).slice(0, 3);
  const rows = Math.min(8, Math.max(1, Math.max.apply(null, cols.map((k) => arr(k.logos).length).concat([arr(c.t.rangs).length, 1]))));
  const pitch = H * 0.067;
  const y0 = H * 0.29;
  const centers = cols.length === 1 ? [0.51] : cols.length === 2 ? [0.42, 0.6] : [0.33, 0.51, 0.69];
  for (let r = 0; r < rows; r++) {
    const cy = y0 + (r + 0.5) * pitch;
    const rang = arr(c.t.rangs)[r];
    c.line({ text: rang !== undefined ? str(rang) : (c.lang === 'en' ? '[TO PROVIDE: rank]' : '[À FOURNIR : rang]'), x: W * 0.12, w: W * 0.09, base: cy + 0.06, size: scalePt(16, 'texte'), wt: 'semi', color: c.P.fg2, align: 'right', font: 'texte', name: 'Rang', g: 'logos' });
    if (r < rows - 1) c.rect({ x: W * 0.17, y: cy + pitch / 2 - 0.004, w: W * 0.63, h: 0.008, fill: mix(c.P.fg, c.P.bg, 0.82), name: 'Filet', g: 'logos' });
    cols.forEach((k, j) => {
      const lg = arr(k.logos)[r];
      if (!lg) return;
      const logo = typeof lg === 'string' ? { nom: lg } : lg;
      const box = { x: W * centers[j] - W * 0.08, y: cy - H * 0.017, w: W * 0.16, h: H * 0.034 };
      const im = loadImg(c, logo.image);
      if (im) putImage(c, im, fitRect(box, im.info, 'contain'), { name: 'Logo', g: 'logos' });
      else c.line({ text: str(logo.nom) || c.f('_', 'logo'), x: box.x - 0.3, w: box.w + 0.6, base: cy + 0.06, size: scalePt(12, 'texte'), wt: 'semi', color: c.P.fg2, align: 'center', font: 'texte', name: 'Logo nom', g: 'logos' });
    });
  }
  cols.forEach((k, j) => c.line({ text: str(k.periode) || (c.lang === 'en' ? '[TO PROVIDE: year]' : '[À FOURNIR : année]'), x: W * centers[j] - 0.8, w: 1.6, base: y0 + rows * pitch + 0.3, size: scalePt(14, 'texte'), wt: 'regular', color: c.P.fg2, align: 'center', font: 'texte', name: 'Période', g: 'logos' }));
  if (c.sourceText) {
    c.text({ x: W * 0.5, y: H * 0.94, w: W * 0.47, h: 0.25, text: c.sourceDisplay || c.sourceText, size: 9, min: 8, maxLines: 1, color: c.P.fg2, align: 'right', valign: 'top', font: 'texte', lh: K.titre, name: 'Source' });
    c.sourceDone = true;
  }
};

// A11 : schéma à bloc surligné. Le schéma fourni, ou un plan de blocs au trait (cases inégales,
// sans inscription), avec le ou les blocs allumés : contour, intérieur éclairci, lueur douce.
const PLAN_CELLS = {
  lines: [
    [0.5, 0, 0.5, 1], [0, 0.14, 0.5, 0.14], [0, 0.4, 0.5, 0.4], [0, 0.575, 0.5, 0.575], [0, 0.87, 0.5, 0.87],
    [0.38, 0.14, 0.38, 0.4], [0.38, 0.575, 0.38, 0.87], [0.5, 0.24, 1, 0.24], [0.5, 0.59, 1, 0.59], [0.5, 0.8, 1, 0.8],
    [0.75, 0.24, 0.75, 0.59], [0.66, 0.8, 0.66, 1]
  ]
};
function schemaPlan(c, sq, spec, o) {
  o = o || {};
  const im = loadImg(c, spec);
  if (im) {
    putImage(c, im, fitRect(sq, im.info, 'contain'), { name: 'Schéma', g: 'visuel' });
    return;
  }
  missingVisual(c, spec, 'interface', c.lang === 'en' ? 'diagram of the system' : 'schéma du système', { g: 'visuel' }, () => {
    const lc = mix(c.P.fg, c.P.bg, 0.65);
    c.round({ x: sq.x, y: sq.y, w: sq.w, h: sq.h, fill: mix(c.P.bg, c.P.fg, 0.04), line: lc, lineW: 0.75, radius: 0.04, name: 'Schéma plan', g: 'visuel' });
    PLAN_CELLS.lines.forEach((l, i) => {
      const x1 = sq.x + l[0] * sq.w;
      const y1 = sq.y + l[1] * sq.h;
      const x2 = sq.x + l[2] * sq.w;
      const y2 = sq.y + l[3] * sq.h;
      if (Math.abs(x1 - x2) < 1e-6) c.rect({ x: x1 - 0.004, y: y1, w: 0.008, h: y2 - y1, fill: lc, name: 'Schéma trait', g: 'visuel' });
      else c.rect({ x: x1, y: y1 - 0.004, w: x2 - x1, h: 0.008, fill: lc, name: 'Schéma trait', g: 'visuel' });
      void i;
    });
  });
}
function litBlock(c, b, i) {
  const glowB = grow(b, 0.3, 0.3);
  genImage(c, glowB, darkBg(c) ? c.P.fg : c.P.accent, alphaAround(darkBg(c) ? 0.22 : 0.3, { x: 0.3, y: 0.3, w: b.w, h: b.h }, 0.04, 0.09, 0), 'Lueur bloc ' + (i + 1), { g: 'lignes', sub: i, key: 'lueur', ppi: 40 });
  c.round({ x: b.x, y: b.y, w: b.w, h: b.h, fill: mix(c.P.bg, c.P.fg, darkBg(c) ? 0.12 : 0.06), line: c.P.fg, lineW: 1.5, radius: 0.04, name: 'Bloc allumé ' + (i + 1), g: 'lignes', sub: i });
}
function systemName(c, z) {
  const logo = loadImg(c, c.slide.logo_systeme || (c.T.logo ? { chemin: c.T.logo } : null));
  const name = tv(c, 'titre');
  if (name) zt(c, z, name, { size: 26, min: 14, maxTotal: 1, align: 'left', font: 'titre', g: 'visuel', name: 'Nom du système' });
  else if (logo) putImage(c, logo, fitRect(z, logo.info, 'contain', 'left'), { name: 'Logo', g: 'visuel' });
  else zt(c, z, c.lang === 'en' ? '[TO PROVIDE: name]' : '[À FOURNIR : nom]', { size: 26, min: 14, maxTotal: 1, align: 'left', g: 'visuel', name: 'Nom du système' });
}
function legend(c, bl, b, zt0, side, i) {
  const right = side === 'droite';
  const t = zt(c, zt0, str(bl.titre) || c.f('_', 'bloc'), { size: 18, min: 13, maxTotal: 1, font: 'texte', align: right ? 'right' : 'left', anchor: 'top', g: 'lignes', sub: i, name: 'Légende ' + (i + 1) });
  const fy = t.g.base + 0.1;
  const fx0 = right ? b.x + b.w : zt0.x;
  const fx1 = right ? zt0.x + zt0.w : b.x;
  c.rect({ x: Math.min(fx0, fx1), y: fy, w: Math.abs(fx1 - fx0), h: 0.0105, fill: mix(c.P.fg, c.P.bg, 0.55), name: 'Filet légende ' + (i + 1), g: 'lignes', sub: i });
  const lines = arr(bl.lignes).slice(0, 5);
  if (lines.length) zlist(c, { x: zt0.x, y: fy + 0.14, w: zt0.w, h: 0.6 }, lines, { size: 14, min: 10, wt: 'regular', color: c.P.fg2, align: right ? 'right' : 'left', anchor: 'top', k: 1.65, g: 'lignes', maxLines: 2, actif: 0 });
  c.items.slice(-1).forEach((it) => { if (it.k === 'text') it.paras.forEach((p) => { p.sub = i; }); });
}
function blockZone(bl, def) {
  const z = arr(bl && bl.zone);
  return z.length === 4 ? P(z[0], z[1], z[2], z[3]) : def;
}
V['A11/legende-laterale'] = (c) => {
  const sq = P(31, 16.5, 38, 67);
  schemaPlan(c, sq, c.slide.image);
  systemName(c, P(32.6, 18, 15, 4.7));
  const right = c.t.cote === 'droite';
  const bl = arr(c.t.blocs)[0] || {};
  const b = blockZone(bl, right ? P(50.5, 50, 18, 26) : P(31.5, 55, 18.5, 28));
  litBlock(c, b, 0);
  legend(c, bl, b, right ? { x: W * 0.715, y: b.y, w: W * 0.24, h: 0.3 } : { x: W * 0.045, y: b.y, w: W * 0.24, h: 0.3 }, right ? 'droite' : 'gauche', 0);
  c.groups = [G('visuel', KW.visuel), G('lignes', /\b(?:blocs?|blocks?|legendes?|captions?)\b/, { multi: true })];
};
V['A11/plusieurs-blocs'] = (c) => {
  const sq = P(31, 16.5, 38, 67);
  schemaPlan(c, sq, c.slide.image);
  systemName(c, P(32.6, 18, 15, 4.7));
  const defs = [[P(32, 26, 13.5, 17), { x: W * 0.05, w: W * 0.22 }, 'gauche'], [P(32, 55, 13.5, 20), { x: W * 0.05, w: W * 0.22 }, 'gauche'], [P(50, 17.5, 18.5, 15), { x: W * 0.73, w: W * 0.225 }, 'droite']];
  arr(c.t.blocs).slice(0, 3).forEach((bl, i) => {
    const b = blockZone(bl, defs[i][0]);
    litBlock(c, b, i);
    legend(c, bl, b, { x: defs[i][1].x, y: b.y - 0.05, w: defs[i][1].w, h: 0.3 }, defs[i][2], i);
  });
  c.groups = [G('visuel', KW.visuel), G('lignes', /\b(?:blocs?|blocks?|legendes?|captions?)\b/, { multi: true })];
};
V['A11/schema-chiffre'] = (c) => {
  const sq = P(11, 16.5, 38, 67);
  schemaPlan(c, sq, c.slide.image);
  systemName(c, P(12.6, 18, 15, 4.7));
  const bl = arr(c.t.blocs)[0] || {};
  litBlock(c, blockZone(bl, P(11.5, 26, 37, 30)), 0);
  const z = P(55, 37, 39, 16.2);
  const h = heroNumber(c, z, { size: 90, min: 60 });
  const lib = zt(c, { x: P(54, 0, 0, 0).x, y: h.g.base + 0.25 + descGap(c, h), w: P(0, 0, 41, 0).w, h: 0.4 }, c.f('libelle', 'libellé'), { size: 20, min: 14, maxTotal: 2, font: 'texte', anchor: 'top', g: 'libelle', name: 'Libellé' });
  srcLine(c, { x: z.x, y: lib.g.base + 0.18, w: z.w, h: 0.3 }, { g: 'libelle' });
  c.groups = [G('visuel', KW.visuel), G('lignes', /\b(?:blocs?|blocks?)\b/), G('chiffre', KW.chiffre), G('libelle', KW.libelle)];
};
V['A11/carte-annotee'] = (c) => {
  const z = P(15, 26, 71, 46);
  const im = loadImg(c, c.slide.image);
  if (im) putImage(c, im, fitRect(z, im.info, 'contain'), { name: 'Vue de dessus', g: 'visuel' });
  else {
    missingVisual(c, c.slide.image, 'objet', c.lang === 'en' ? 'top view of the object' : 'vue de dessus détourée', { g: 'visuel' }, () => {
      c.round({ x: z.x, y: z.y, w: z.w, h: z.h, fill: mix(c.P.bg, c.P.fg, 0.08), radius: 0.14, name: 'Schéma vue', g: 'visuel' });
      [[0.06, 0.12, 0.2, 0.32], [0.3, 0.12, 0.14, 0.2], [0.5, 0.18, 0.12, 0.26], [0.68, 0.1, 0.24, 0.3], [0.06, 0.56, 0.3, 0.3], [0.4, 0.56, 0.1, 0.18], [0.56, 0.58, 0.18, 0.28], [0.8, 0.52, 0.12, 0.34]].forEach((q) => {
        c.round({ x: z.x + z.w * q[0], y: z.y + z.h * q[1], w: z.w * q[2], h: z.h * q[3], fill: mix(c.P.bg, c.P.fg, 0.14), radius: 0.04, name: 'Schéma composant', g: 'visuel' });
      });
    });
  }
  const defs = [{ zone: [51, 40, 9, 13], haut: true }, { zone: [43, 59, 4.7, 5.3], haut: false }, { zone: [24, 36, 8, 10], haut: true }, { zone: [70, 56, 8, 10], haut: false }];
  arr(c.t.annotations).slice(0, 6).forEach((a, i) => {
    const an = typeof a === 'string' ? { texte: a } : a;
    const d = defs[i % defs.length];
    const zz = arr(an.zone).length === 4 ? arr(an.zone) : d.zone;
    const b = P(zz[0], zz[1], zz[2], zz[3]);
    const up = an.position ? normKey(an.position) !== 'bas' : d.haut;
    c.round({ x: b.x, y: b.y, w: b.w, h: b.h, line: c.P.fg, lineW: 1, radius: 0.02, name: 'Cadre ' + (i + 1), g: 'lignes', sub: i });
    const fx = b.x + b.w / 2;
    const ly = up ? H * 0.19 : H * 0.88;
    c.rect({ x: fx - 0.007, y: up ? ly + 0.05 : b.y + b.h, w: 0.014, h: up ? b.y - ly - 0.05 : ly - 0.25 - (b.y + b.h), fill: c.P.fg, name: 'Filet ' + (i + 1), g: 'lignes', sub: i });
    c.line({ text: str(an.texte || an.titre), x: fx + 0.08, w: 2.4, base: up ? ly + 0.12 : ly, size: scalePt(18, 'texte'), wt: 'semi', align: 'left', font: 'texte', name: 'Étiquette ' + (i + 1), g: 'lignes', sub: i });
  });
  c.groups = [G('visuel', KW.visuel), G('lignes', /\b(?:etiquettes?|labels?|cadres?|annotations?|composants?)\b/, { multi: true })];
};
// Le système en carré lumineux : carré presque noir, liseré d'accent qui déborde en halo flou.
V['A11/carre-halo'] = (c) => {
  const s = Math.min(P(0, 0, 33.3, 0).w, P(0, 0, 0, 59).h);
  const sq = { x: (W - s) / 2, y: (H - s) / 2, w: s, h: s };
  const pad = W * 0.09;
  const gb = grow(sq, pad, pad);
  // Coins presque vifs (5 % du côté) : un composant, pas une icône d'app.
  const rad = s * 0.05;
  genImage(c, gb, c.P.accent, alphaAround(0.6, { x: pad, y: pad, w: s, h: s }, rad, 0.22, 0), 'Halo du carré', { g: 'visuel', key: 'carrehalo', ppi: 40 });
  c.round({ x: sq.x, y: sq.y, w: s, h: s, fill: mix(c.T.fondSombre, '000000', 0.55), line: c.P.accent, lineW: 2.5, radius: rad, name: 'Carré', g: 'visuel' });
  c.accentUsed = true;
  const logo = loadImg(c, c.slide.image || (c.T.logo && !tv(c, 'titre') ? { chemin: c.T.logo } : null));
  const zin = grow(sq, -s * 0.14, -s * 0.3);
  if (logo) putImage(c, logo, fitRect(zin, logo.info, 'contain'), { name: 'Logo', g: 'visuel' });
  else zt(c, zin, c.f('titre', 'nom'), { size: 52, min: 26, maxTotal: 2, color: 'FFFFFF', g: 'visuel', name: 'Nom' });
};

// A15 : murs d'abondance, qui débordent du cadre.
function elems(c) {
  return arr(c.t.elements).map((e) => (typeof e === 'string' ? { titre: e } : e || {}));
}
V['A15/vignettes'] = (c) => {
  const els = elems(c);
  const vw = W * 0.21;
  const vh = H * 0.215;
  const gx = W * 0.0125;
  const gy = H * 0.022;
  const rad = W * 0.012;
  let k = 0;
  for (let r = 0; r < 5; r++) {
    const off = -((r % 3) * (vw + gx) / 3) - W * 0.03;
    for (let col = 0; col < 6; col++) {
      const x = off + col * (vw + gx);
      const y = -H * 0.03 + r * (vh + gy) - H * 0.02;
      if (x > W || y > H) continue;
      const e = els.length ? els[k % els.length] : {};
      const box = { x, y, w: vw, h: vh };
      const im = loadImg(c, e.image);
      if (im) putImage(c, im, fitRect(box, im.info, 'cover'), { clip: box, radius: rad, name: 'Vignette', g: 'tuiles' });
      else {
        const tone = 0.1 + ((k * 7) % 5) * 0.01;
        c.round({ x, y, w: vw, h: vh, fill: mix(c.P.bg, c.P.fg, tone), radius: rad, name: 'Vignette', g: 'tuiles' });
        pill(c, x + vw * 0.1, y + vh * 0.78, vw * (0.35 + ((k * 3) % 4) * 0.1), 0.06, mix(c.P.bg, c.P.fg, tone + 0.12), 'Vignette barre');
        c.items[c.items.length - 1].g = 'tuiles';
      }
      k += 1;
    }
  }
  if (!els.some((e) => loadImg(c, e.image))) registerMissing(c, null, 'tuile', c.lang === 'en' ? 'thumbnails of the catalogue' : 'vignettes du catalogue');
  c.groups = [G('tuiles', /\b(?:grilles?|murs?|vignettes?|tuiles?|walls?|grids?)\b/)];
};
V['A15/icones'] = (c) => {
  const els = elems(c);
  const s = W * 0.075;
  const gx = W * 0.013;
  let k = 0;
  const any = els.some((e) => loadImg(c, e.image));
  for (let r = 0; r < 7; r++) {
    const off = (r % 2 ? -(s + gx) / 2 : 0) - W * 0.02;
    for (let col = 0; col < 13; col++) {
      const x = off + col * (s + gx);
      const y = -H * 0.04 + r * (s + gx);
      if (x > W || y > H) continue;
      const e = els.length ? els[k % els.length] : {};
      const box = { x, y, w: s, h: s };
      const im = loadImg(c, e.image);
      if (im) putImage(c, im, fitRect(box, im.info, 'contain'), { name: 'Pastille', g: 'tuiles' });
      else {
        // Repli : des pastilles en nuances voisines de gris, chacune avec un pictogramme, pour qu'on
        // lise un mur d'icônes (et non un carrelage) ; quelques-unes dans l'accent, très atténué.
        const tone = mix(c.P.bg, c.P.fg, (darkBg(c) ? 0.2 : 0.14) + ((k * 5) % 5) * 0.035);
        const fill = (k * 7) % 9 === 0 ? mix(tone, c.P.accent, 0.55) : tone;
        c.round({ x, y, w: s, h: s, fill, radius: s * 0.22, grad2: { from: mix(fill, 'FFFFFF', 0.1), to: fill, ang: 90 }, name: 'Pastille', g: 'tuiles' });
        drawGlyph(c, grow(box, -s * 0.3, -s * 0.3), k, { g: 'tuiles', color: mix(fill, readableOn(fill, '111111', 'FFFFFF'), 0.6) });
      }
      k += 1;
    }
  }
  if (!any) registerMissing(c, null, 'icone', c.lang === 'en' ? 'icons of the services' : 'icônes des services');
  c.groups = [G('tuiles', /\b(?:murs?|pastilles?|icones?|icons?|walls?)\b/)];
};
V['A15/mots'] = (c) => {
  const els = elems(c).map((e) => str(e.titre)).filter(Boolean);
  const two = !!c.t.deux_tons;
  const rows = 9;
  const pitch = H * 0.103;
  const y0 = H * 0.07 + pitch * 0.5;
  if (!els.length) {
    // Repli : des barres arrondies de longueurs variées, en lignes justifiées.
    const rnd = rng(11 + c.index);
    for (let r = 0; r < rows; r++) {
      const n = 3 + (r % 2);
      const lens = [];
      for (let i = 0; i < n; i++) lens.push(0.6 + rnd() * 1.4);
      const tot = lens.reduce((a, b) => a + b, 0);
      const gap = (W * 0.928 - tot) / (n - 1);
      let x = W * 0.036;
      lens.forEach((l) => {
        pill(c, x, y0 + r * pitch - H * 0.008, l, H * 0.016, mix(c.P.bg, c.P.fg, 0.22 + rnd() * 0.08), 'Mot');
        c.items[c.items.length - 1].g = 'tuiles';
        x += l + gap;
      });
    }
    registerMissing(c, null, 'tuile', c.lang === 'en' ? 'list of the labels' : 'liste des libellés');
    c.groups = [G('tuiles', /\b(?:murs?|mots?|libelles?|walls?|words?)\b/)];
    return;
  }
  let k = 0;
  const size = scalePt(16, 'texte');
  const gapW = textWidth('      ', size, true, 0, 'texte');
  for (let r = 0; r < rows; r++) {
    // Chaque ligne se remplit jusqu'à 88 % de la largeur (fiche : lignes justifiées d'un bord à l'autre).
    const line = [];
    let lw = 0;
    for (let guard = 0; guard < 40; guard++) {
      const wd = els[k % els.length];
      const ww = textWidth(shownText(c, wd), size, true, trackFor('texte', size), 'texte');
      if (line.length && lw + gapW + ww > W * 0.88) break;
      line.push(wd);
      lw += (line.length > 1 ? gapW : 0) + ww;
      k += 1;
    }
    const runs = [];
    line.forEach((wd, i) => {
      if (i) runs.push({ t: '      ' });
      c.para(wd, { font: 'texte' })[0].runs.forEach((rr) => runs.push(Object.assign({}, rr, { color: rr.marker ? undefined : (two && (r + i) % 2 ? c.P.accentTxt : c.P.fg2) })));
    });
    c.text({ x: W * 0.036, y: y0 + r * pitch - 0.2, w: W * 0.928, h: 0.4, paras: [{ runs, rel: 1, wt: 'semi', font: 'texte' }], size: 16, min: 11, maxLines: 1, wt: 'semi', align: 'center', valign: 'middle', font: 'texte', color: c.P.fg2, lh: K.titre, name: 'Mots ' + (r + 1), g: 'tuiles' });
  }
  if (two) c.accentUsed = true;
  c.groups = [G('tuiles', /\b(?:murs?|mots?|libelles?|walls?|words?)\b/)];
};
V['A15/nuage'] = (c) => {
  const els = elems(c).map((e) => str(e.titre)).filter(Boolean);
  if (!els.length) {
    V['A15/mots'](c);
    return;
  }
  const rnd = rng(23 + c.index * 7);
  const planes = [[13, 0.3], [22, 0.7], [36, 1]];
  const placed = [];
  els.slice(0, 16).forEach((wd, i) => {
    const pl = planes[i % 3];
    const size = scalePt(pl[0], 'texte');
    const tw = textWidth(shownText(c, wd), size, true, trackFor('texte', size), 'texte') + 0.1;
    const th = capIn('texte', size) * 2.2;
    let best = null;
    for (let tries = 0; tries < 40; tries++) {
      const x = -0.4 + rnd() * (W + 0.8 - tw * 0.6);
      const y = 0.2 + rnd() * (H - 0.4 - th);
      const box = { x, y, w: tw, h: th };
      const center = !tv(c, 'titre') || !inter(box, P(15, 38, 70, 16));
      const free = placed.every((b) => !inter(grow(b, 0.1, 0.05), box));
      if (center && free) {
        best = box;
        break;
      }
    }
    if (!best) return;
    placed.push(best);
    const color = mix(c.P.fg, c.P.bg, 1 - pl[1]);
    c.text({ x: best.x, y: best.y, w: best.w + 0.2, h: best.h, text: wd, size: pl[0], min: pl[0], maxLines: 1, wt: 'semi', color, align: 'left', valign: 'middle', font: 'texte', lh: K.titre, name: 'Mot', g: 'tuiles', noWrap: true });
  });
  if (tv(c, 'titre')) {
    const z = P(10, 40, 80, 9.4);
    zt(c, z, c.t.titre, { size: 52, min: 36, maxTotal: 1, g: 'titre', name: 'Nom' });
  }
  c.groups = [G('tuiles', /\b(?:nuages?|mots?|clouds?|words?)\b/), G('titre', KW.titre)];
};
V['A15/cartes-libelles'] = (c) => {
  const els = elems(c);
  const cw = W * 0.152;
  const ch = H * 0.142;
  const gx = W * 0.0125;
  const gy = H * 0.021;
  const card = darkBg(c) ? mix(c.P.bg, c.P.fg, 0.12) : 'FFFFFF';
  let k = 0;
  for (let r = 0; r < 7; r++) {
    for (let col = 0; col < 6; col++) {
      const x = W * 0.012 + col * (cw + gx);
      const y = H * 0.022 + r * (ch + gy);
      if (y > H) continue;
      const e = els.length ? els[k % els.length] : {};
      c.round({ x, y, w: cw, h: ch, fill: card, radius: W * 0.015, name: 'Carte', g: 'tuiles' });
      const ib = { x: x + W * 0.014, y: y + H * 0.023, w: W * 0.033, h: W * 0.033 };
      const im = loadImg(c, e.image);
      if (im) putImage(c, im, fitRect(ib, im.info, 'contain'), { name: 'Carte icône', g: 'tuiles' });
      else c.round({ x: ib.x, y: ib.y, w: ib.w, h: ib.h, fill: mix(card, c.P.accent, 0.22), radius: ib.w * 0.25, name: 'Carte icône', g: 'tuiles' });
      if (str(e.titre)) c.text({ x: x + W * 0.014, y: y + ch * 0.55, w: cw - W * 0.028, h: ch * 0.4, text: e.titre, size: 9, min: 7, maxTotal: 2, wt: 'regular', color: c.P.fg, align: 'left', valign: 'top', font: 'texte', lh: K.titre, name: 'Carte libellé', g: 'tuiles' });
      else {
        pill(c, x + W * 0.014, y + ch * 0.62, (cw - W * 0.028) * 0.6, 0.05, mix(card, c.P.fg, 0.22), 'Carte barre');
        c.items[c.items.length - 1].g = 'tuiles';
        pill(c, x + W * 0.014, y + ch * 0.62 + 0.1, (cw - W * 0.028) * 0.4, 0.05, mix(card, c.P.fg, 0.16), 'Carte barre');
        c.items[c.items.length - 1].g = 'tuiles';
      }
      k += 1;
    }
  }
  c.groups = [G('tuiles', /\b(?:murs?|cartes?|cards?|walls?)\b/)];
};
// Mosaïque découpée par une forme simple (cœur ou cercle) : on garde les cases dont le centre
// est dans la forme.
V['A15/forme'] = (c) => {
  const els = elems(c);
  const z = P(30, 12, 40, 70);
  const forme = normKey(c.t.forme) || 'coeur';
  const cell = 0.22;
  const gap = W * 0.008;
  const inside = (u, v) => {
    if (forme === 'cercle') return u * u + v * v <= 1;
    const x = u * 1.16;
    const y = -v * 1.12 + 0.12;
    const q = x * x + y * y - 1;
    return q * q * q - x * x * y * y * y <= 0;
  };
  const s = Math.min(z.w, z.h);
  const cx = z.x + z.w / 2;
  const cy = z.y + z.h / 2;
  let k = 0;
  for (let y = cy - s / 2; y < cy + s / 2; y += cell + gap) {
    for (let x = cx - s / 2; x < cx + s / 2; x += cell + gap) {
      const u = (x + cell / 2 - cx) / (s / 2);
      const v = (y + cell / 2 - cy) / (s / 2);
      if (!inside(u, v)) continue;
      const e = els.length ? els[k % els.length] : {};
      const box = { x, y, w: cell, h: cell };
      const im = loadImg(c, e.image);
      if (im) putImage(c, im, fitRect(box, im.info, 'cover'), { clip: box, radius: 0.03, name: 'Mosaïque', g: 'tuiles' });
      else c.round({ x, y, w: cell, h: cell, fill: mix(c.P.bg, c.P.fg, 0.1 + ((k * 7) % 6) * 0.015), radius: 0.03, name: 'Mosaïque', g: 'tuiles' });
      k += 1;
    }
  }
  if (!els.some((e) => loadImg(c, e.image))) registerMissing(c, null, 'tuile', c.lang === 'en' ? 'thumbnails for the mosaic' : 'vignettes de la mosaïque');
  c.groups = [G('tuiles', /\b(?:formes?|mosaiques?|coeurs?|shapes?)\b/)];
};

// A16 : logos monochromes à aire égale ; un logo manquant devient le nom en texte, jamais un dessin.
function logoAt(c, lg, box, o) {
  o = o || {};
  const logo = typeof lg === 'string' ? { nom: lg } : (lg || {});
  const im = loadImg(c, logo.image);
  if (im) {
    const a = im.info.w / im.info.h;
    const area = o.area || 0.15;
    let h = Math.sqrt(area / a);
    let w = a * h;
    if (w > box.w) {
      w = box.w;
      h = w / a;
    }
    if (h > box.h) {
      h = box.h;
      w = h * a;
    }
    putImage(c, im, { x: box.x + (box.w - w) / 2, y: box.y + (box.h - h) / 2, w, h }, { name: 'Logo', g: 'logos', sub: o.sub });
    return;
  }
  const nm = str(logo.nom) || c.f('_', 'logo');
  c.text({ x: box.x - 0.15, y: box.y, w: box.w + 0.3, h: box.h, text: nm, size: o.nameSize || 20, min: Math.min(o.nameSize || 20, 9), maxTotal: 2, wt: 'semi', color: o.color || c.P.fg2, align: 'center', valign: 'middle', font: 'texte', lh: K.titre, name: 'Logo nom', g: 'logos', sub: o.sub });
}
// Aucun logo donné : un seul marqueur, au centre (jamais de logo dessiné).
function noLogos(c) {
  if (arr(c.t.logos).length) return false;
  zt(c, P(10, 42, 80, 16), c.f('logos', 'logos'), { size: 32, min: 20, maxTotal: 1, font: 'texte', g: 'logos', name: 'Logos' });
  return true;
}
function logosHead(c, topY) {
  if (!tv(c, 'titre')) return;
  c.line({ text: c.t.titre, x: M, w: FULL_W, base: topY - 0.3, size: scalePt(24, 'texte'), wt: 'regular', color: c.P.fg2, align: 'center', font: 'texte', name: 'Titre', g: 'titre' });
}
V['A16/grille'] = (c) => {
  if (noLogos(c)) return;
  const logos = arr(c.t.logos).slice(0, 20);
  const n = Math.max(1, logos.length);
  const rows = n > 15 ? 4 : n > 10 ? 3 : n > 5 ? 2 : 1;
  const rowsY = { 1: [50], 2: [38, 62], 3: [28, 50, 72], 4: [17, 39, 61, 82.7] }[rows];
  const colsX = [14.5, 32.3, 50, 67.7, 85.3];
  const shift = tv(c, 'titre') ? 4 : 0;
  logos.forEach((lg, i) => {
    const r = Math.floor(i / 5);
    const inRow = Math.min(5, n - r * 5);
    const xs = inRow === 5 ? colsX : colsX.slice(0, inRow).map((x, j) => 50 + (j - (inRow - 1) / 2) * 17.7);
    const b = P(xs[i % 5] - 5.5, rowsY[r] + shift - 4, 11, 8);
    logoAt(c, lg, b, { sub: i });
  });
  logosHead(c, P(0, rowsY[0] + shift - 4, 0, 0).y);
};
V['A16/ligne'] = (c) => {
  if (noLogos(c)) return;
  const logos = arr(c.t.logos).slice(0, 4);
  const n = Math.max(1, logos.length);
  const cs = { 1: [50], 2: [32, 68], 3: [18, 50, 82], 4: [17, 39, 61, 83] }[n];
  const lw = n === 4 ? 17 : 20;
  logos.forEach((lg, i) => logoAt(c, lg, P(cs[i] - lw / 2, 45, lw, 10), { sub: i, area: 0.4, nameSize: 28 }));
  logosHead(c, P(0, 45, 0, 0).y);
};
V['A16/logo-seul'] = (c) => {
  const lg = arr(c.t.logos)[0] || { nom: tv(c, 'titre') || c.f('_', 'logo') };
  logoAt(c, lg, P(27, 37, 46, 26), { area: 3, nameSize: 56, color: c.P.fg });
};
V['A16/mur-dense'] = (c) => {
  if (noLogos(c)) return;
  const logos = arr(c.t.logos).slice(0, 84);
  const cols = logos.length > 60 ? 12 : logos.length > 40 ? 10 : 8;
  const rows = Math.ceil(logos.length / cols);
  const pitchY = H * 0.124;
  const pitchX = W * 0.92 / cols;
  const y0 = H / 2 - (rows - 1) * pitchY / 2;
  logos.forEach((lg, i) => {
    const r = Math.floor(i / cols);
    const col = i % cols;
    const b = { x: W * 0.04 + col * pitchX + (pitchX - W * 0.07) / 2, y: y0 + r * pitchY - H * 0.0225, w: W * 0.07, h: H * 0.045 };
    logoAt(c, lg, b, { sub: i, area: 0.06, nameSize: 11 });
  });
};
V['A16/pastilles'] = (c) => {
  if (noLogos(c)) return;
  const logos = arr(c.t.logos).slice(0, 30);
  const d = W * 0.073;
  const pitch = W * 0.084;
  const per = logos.length > 27 ? 10 : 9;
  const rows = Math.ceil(logos.length / per) || 1;
  const y0 = H / 2 - (rows - 1) * pitch / 2;
  logos.forEach((lg, i) => {
    const logo = typeof lg === 'string' ? { nom: lg } : lg;
    const r = Math.floor(i / per);
    const col = i % per;
    const inRow = Math.min(per, logos.length - r * per);
    const x = W / 2 + (col - (inRow - 1) / 2) * pitch + (r % 2 ? pitch / 4 : -pitch / 4) - d / 2;
    const y = y0 + r * pitch - d / 2;
    const fill = hex(logo.couleur, null, 'couleur', null) || c.P.fg2;
    c.ellipse({ x, y, w: d, h: d, fill, name: 'Pastille', g: 'logos', sub: i });
    const im = loadImg(c, logo.image);
    const inner = grow({ x, y, w: d, h: d }, -d * 0.22, -d * 0.22);
    if (im) putImage(c, im, fitRect(inner, im.info, 'contain'), { name: 'Logo', g: 'logos', sub: i });
    else c.text({ x: x + 0.04, y, w: d - 0.08, h: d, text: str(logo.nom) || c.f('_', 'logo'), size: 9, min: 7, maxTotal: 2, wt: 'semi', color: readableOn(fill, '111111', 'FFFFFF'), align: 'center', valign: 'middle', font: 'texte', lh: K.titre, name: 'Logo nom', g: 'logos', sub: i });
  });
};
V['A16/soi-au-centre'] = (c) => {
  const logos = arr(c.t.logos).slice(0, 16);
  const rowsN = [3, 4, 3, 4, 3];
  const ys = [12, 30.5, 51, 71, 89];
  let k = 0;
  rowsN.forEach((n, r) => {
    for (let j = 0; j < n; j++) {
      const mid = r === 2 && j === 1;
      const x = 50 + (j - (n - 1) / 2) * 18;
      const b = P(x - 6, ys[r] - 4.5, 12, 9);
      if (mid) {
        const own = c.T.logo ? { nom: c.deck.theme && c.deck.theme.nom, image: c.T.logo } : { nom: (c.deck.theme && c.deck.theme.nom) || c.f('_', 'logo') };
        logoAt(c, own, b, { sub: 99, color: c.P.fg });
        continue;
      }
      if (k < logos.length) logoAt(c, logos[k], b, { sub: k });
      k += 1;
    }
  });
  c.groups = [G('logos', KW.logos, { multi: false })];
};

// ---------------------------------------------------------------------------
// Récap et conversion : A14 (bento), A19 (prix), A20 (disponibilité), FIN, COLORIS, FRISE
// ---------------------------------------------------------------------------
// Grilles des bentos (fiche), en % du cadre : colonnes, rangées et types de cases autour du centre.
const BENTO = {
  nom: {
    cols: [[1, 28.6], [30.5, 39], [70.4, 28.6]], rows: [[1.7, 31], [34.3, 31.4], [67.3, 31]],
    cells: [[0, 0, 'capture'], [1, 0, 'icone'], [2, 0, 'photo'], [0, 1, 'capture'], [2, 1, 'mot'], [0, 2, 'icone'], [1, 2, 'capture'], [2, 2, 'icone']]
  },
  produit: {
    // Rangées du haut et du bas en quatre cases ; colonne gauche et droite de la rangée du milieu.
    cols4: [[1, 24], [25.9, 23.7], [50.5, 23.7], [75, 24]], mid: [[1, 24], [25.9, 48.2], [75, 24]], rows: [[1.7, 23], [26.3, 47.4], [75.3, 23]]
  }
};
const BENTO_TYPES = {
  'produit-au-centre': ['icone', 'chiffre', 'capture', 'photo', 'capture', 'mot', 'mot', 'chiffre', 'icone', 'icone'],
  'mot-geant-et-produit': ['photo', 'matiere', 'chiffre', 'photo', 'coloris', 'photo', 'mot', 'capture', 'icone', 'icone'],
  'tuiles-chiffres': ['chiffre', 'chiffre', 'chiffre', 'icone', 'photo', 'chiffre', 'mot', 'icone', 'icone', 'halo'],
  'theme-et-matieres': ['coloris', 'mot', 'mot', 'matiere', 'matiere', 'matiere', 'matiere', 'liste', 'icone', 'mot']
};
// Le contenu d'une tuile : son type (donné, ou celui de la case), son visuel et ses mots.
// Visuel d'une tuile qui manque : une seule consigne par bento quand aucun chemin n'est donné.
function tileMissing(c, spec, kind, label, g, draw) {
  if (c.imageSpec(spec) && c.imageSpec(spec).chemin) {
    missingVisual(c, spec, kind, label, g, draw);
    return;
  }
  (c._tuilesSans = c._tuilesSans || []).push(label);
  const ph = { id: c.phs.length, name: (c.L.cap[kind] || c.L.cap.tuile) + (label ? ' · ' + shortLabel(label, 6) : ''), kind, g: g.g, sub: g.sub };
  c.phs.push(ph);
  const prev = c.curPh;
  c.curPh = ph.id;
  try {
    draw();
  } finally {
    c.curPh = prev;
  }
}
function tilesMissingNote(c) {
  const l = uniq(c._tuilesSans || []);
  if (!l.length) return;
  c.missing.push({ kind: 'tuile', attendu: (c.lang === 'en' ? 'visuals of the tiles: ' : 'visuels des tuiles : ') + l.join(', '), chemin: '', brief: (BRIEF[c.lang] || BRIEF.fr).tuile });
  c.warn('Tuiles sans visuel (' + l.join(', ') + ') : repli dessiné.');
}
function bentoTile(c, b, tile, slotType, i, o) {
  o = o || {};
  const g = { g: 'tuiles', sub: i };
  const rad = Math.min(VS.tuile.rayon, 0.25 * Math.min(b.w, b.h));
  const type = normKey(tile.type) || (tile.chiffre ? 'chiffre' : tile.lignes ? 'liste' : slotType);
  const surface = c.P.surface;
  const label = str(tile.titre);
  const smallLabel = (txt, zy, zh) => {
    if (!txt) return;
    c.text(Object.assign({ x: b.x + b.w * 0.06, y: zy, w: b.w * 0.88, h: zh, text: txt, size: VS.tuile.libelle, min: 8, maxTotal: 2, wt: 'regular', color: c.P.fg2, align: 'center', valign: 'middle', font: 'texte', lh: K.titre, name: 'Libellé tuile ' + (i + 1) }, g));
  };
  if (type === 'photo' || type === 'matiere') {
    const im = loadImg(c, tile.image);
    const white = type === 'photo';
    if (im) {
      putImage(c, im, fitRect(b, im.info, 'cover'), Object.assign({ clip: b, radius: rad, name: type === 'photo' ? 'Photo tuile' : 'Matière tuile' }, g));
      if (white && label) gradientVeil(c, { x: b.x, y: b.y + b.h * 0.45, w: b.w, h: b.h * 0.55 }, 0.5, 'bas', g);
    } else {
      tileMissing(c, tile.image, 'tuile', label || (type === 'photo' ? 'photo' : (c.lang === 'en' ? 'material' : 'matière')), g, () => {
        if (type === 'photo') drawPhotoSoft(c, b, Object.assign({ radius: rad, base: mix(surface, c.P.fg, 0.04) }, g));
        else c.round(Object.assign({ x: b.x, y: b.y, w: b.w, h: b.h, fill: mix(surface, darkBg(c) ? '000000' : c.P.fg, 0.07), radius: rad, name: 'Schéma matière' }, g));
      });
    }
    if (label) {
      if (white) c.text(Object.assign({ x: b.x + b.w * 0.07, y: b.y + b.h * 0.62, w: b.w * 0.86, h: b.h * 0.32, text: label, size: 20, min: 11, maxTotal: 2, wt: 'semi', color: im ? 'FFFFFF' : c.P.fg, align: 'left', valign: 'bottom', font: 'texte', lh: K.titre, name: 'Titre tuile ' + (i + 1) }, g));
      else zt(c, grow(b, -b.w * 0.08, -b.h * 0.2), label, Object.assign({ size: 24, min: 12, maxTotal: 2, font: 'texte', color: im ? 'FFFFFF' : c.P.fg, name: 'Titre tuile ' + (i + 1) }, g));
    }
    return;
  }
  if (type === 'capture') {
    // La capture sort du haut de la tuile (coupée par son bord), le libellé dessous.
    const cap = { x: b.x + b.w * 0.14, y: b.y - b.h * 0.1, w: b.w * 0.72, h: b.h * 0.84 };
    const im = loadImg(c, tile.image);
    if (im) putImage(c, im, fitRect(cap, im.info, 'cover', undefined, 'top'), Object.assign({ clip: inter(cap, b), radius: 0.06, name: 'Capture tuile' }, g));
    else {
      tileMissing(c, tile.image, 'interface', label || (c.lang === 'en' ? 'screenshot' : 'capture'), g, () => {
        const start = c.items.length;
        const C = schemaColors(c);
        if (cap.h > cap.w * 1.15) drawScreenPortrait(c, cap, C, 0.08, { hi: 1 });
        else drawWindow(c, cap, Object.assign({}, C, { shadow: false }), rng(5 + i), ['liste', 'document', 'tableau'][i % 3]);
        clipItems(c, start, { x: b.x, y: b.y, w: b.w, h: b.h * 0.78 });
      });
    }
    smallLabel(label, b.y + b.h * 0.8, b.h * 0.17);
    return;
  }
  if (type === 'icone' || type === 'halo') {
    const s = Math.min(b.w, b.h) * (type === 'halo' ? 0.5 : 0.36);
    const ib = { x: b.x + (b.w - s) / 2, y: b.y + b.h * 0.42 - s / 2, w: s, h: s };
    if (type === 'halo') {
      const gb = grow(ib, s * 0.6, s * 0.6);
      genImage(c, gb, c.P.accent, alphaAround(0.5, { x: s * 0.6, y: s * 0.6, w: s, h: s }, s * 0.22, s * 0.18, 0), 'Halo tuile', Object.assign({ key: 'halotuile2', ppi: 50 }, g));
    }
    const im = loadImg(c, tile.image);
    if (im) putImage(c, im, fitRect(ib, im.info, 'contain'), Object.assign({ name: 'Icône tuile' }, g));
    else if (type === 'halo') c.round(Object.assign({ x: ib.x, y: ib.y, w: s, h: s, fill: mix(c.T.fondSombre, '000000', 0.3), line: c.P.accent, lineW: 1.5, radius: s * 0.22, name: 'Symbole' }, g));
    else tileMissing(c, tile.image, 'icone', label || (c.lang === 'en' ? 'icon' : 'icône'), g, () => drawGlyph(c, ib, i, g));
    smallLabel(label, b.y + b.h * 0.78, b.h * 0.18);
    return;
  }
  if (type === 'coloris') {
    const cols = arr(tile.coloris).length ? arr(tile.coloris) : [{}, {}, {}];
    const n = Math.min(4, cols.length);
    const sw = b.w * 0.8 / n;
    cols.slice(0, n).forEach((col, k) => {
      const hx = hex(col.hex, null, 'coloris', null);
      drawSilhouette(c, { x: b.x + b.w * 0.1 + k * sw + sw * 0.15, y: b.y + b.h * 0.12, w: sw * 0.7, h: b.h * 0.58 }, Object.assign({ exact: true, fill: hx || undefined, ton: hx ? 0 : k * 0.05, ombre: false, halo: false }, g));
    });
    smallLabel(label, b.y + b.h * 0.76, b.h * 0.2);
    return;
  }
  if (type === 'liste') {
    const lines = arr(tile.lignes).length ? arr(tile.lignes) : [label];
    const paras = [];
    lines.slice(0, 4).forEach((l) => c.para(l, { wt: 'semi', font: 'texte', gapK: 0.6 }).forEach((p) => paras.push(p)));
    c.text(Object.assign({ x: b.x + b.w * 0.1, y: b.y + b.h * 0.12, w: b.w * 0.8, h: b.h * 0.76, paras, size: 16, min: 9, maxTotal: 6, wt: 'semi', align: 'left', valign: 'middle', font: 'texte', lh: K.titre, name: 'Liste tuile ' + (i + 1) }, g));
    return;
  }
  if (type === 'chiffre') {
    const paras = [];
    if (tile.mention) c.para(tile.mention, { pt: VS.tuile.libelle, wt: 'regular', font: 'texte', color: c.P.fg2, gap: 0.02 }).forEach((p) => paras.push(p));
    c.para(tile.chiffre || (c.lang === 'en' ? '[TO PROVIDE: figure]' : '[À FOURNIR : chiffre]'), { wt: 'semi', font: 'titre', color: c.P.accentTxt, gap: 0.04 }).forEach((p) => paras.push(p));
    if (label) c.para(label, { pt: VS.tuile.libelle, wt: 'regular', font: 'texte', color: c.P.fg2 }).forEach((p) => paras.push(p));
    c.text(Object.assign({ x: b.x + b.w * 0.06, y: b.y + b.h * 0.08, w: b.w * 0.88, h: b.h * 0.84, paras, size: 48, min: 20, maxTotal: 4, wt: 'semi', align: 'center', valign: 'middle', font: 'titre', lh: K.titre, name: 'Chiffre tuile ' + (i + 1) }, g));
    return;
  }
  // Mot : petit surtitre facultatif, le mot en accent.
  const paras = [];
  if (tile.surtitre) c.para(tile.surtitre, { pt: VS.tuile.libelle, wt: 'regular', font: 'texte', color: c.P.fg2, gap: 0.05 }).forEach((p) => paras.push(p));
  c.para(label || tile.texte || (c.lang === 'en' ? '[TO PROVIDE: tile]' : '[À FOURNIR : tuile]'), { wt: 'semi', font: 'titre', color: c.P.accentTxt }).forEach((p) => paras.push(p));
  c.text(Object.assign({ x: b.x + b.w * 0.08, y: b.y + b.h * 0.1, w: b.w * 0.84, h: b.h * 0.8, paras, size: 24, min: 12, maxTotal: 4, wt: 'semi', align: 'center', valign: 'middle', font: 'titre', lh: K.titre, balance: true, name: 'Mot tuile ' + (i + 1) }, g));
}
// Le bento occupe tout le cadre : quand la source s'affiche sur la slide, la rangée du bas s'arrête
// à 94 % H et la source passe dessous, au lieu de recouvrir les libellés des tuiles.
function bentoRows(c, rows) {
  if (!c.sourceOnSlide || c.sourceDone) return rows;
  const out = rows.map((r) => r.slice());
  const last = out[out.length - 1];
  last[1] = Math.max(10, 94.2 - last[0]);
  return out;
}
// Bento au nom central : grille 3 × 3 de la fiche, tuile centrale en aplat d'accent. Moins de
// 8 tuiles : des cases fusionnent (mêmes fusions que le bento d'origine), jamais de trou.
V['A14/nom-au-centre'] = (c) => {
  const B = Object.assign({}, BENTO.nom, { rows: bentoRows(c, BENTO.nom.rows) });
  let tiles = arr(c.t.tuiles).slice(0, 8).map((t) => (typeof t === 'string' ? { titre: t } : t || {}));
  while (tiles.length < 4) tiles.push({ titre: c.lang === 'en' ? '[TO PROVIDE: tile]' : '[À FOURNIR : tuile]' });
  const n = tiles.length;
  const cell = (col, row, cs, rs) => {
    const x = B.cols[col][0];
    const y = B.rows[row][0];
    const xe = B.cols[col + (cs || 1) - 1][0] + B.cols[col + (cs || 1) - 1][1];
    const ye = B.rows[row + (rs || 1) - 1][0] + B.rows[row + (rs || 1) - 1][1];
    return P(x, y, xe - x, ye - y);
  };
  const LAY = {
    8: B.cells,
    7: [[0, 0, 'capture', 1, 2], [1, 0, 'icone'], [2, 0, 'photo'], [2, 1, 'mot'], [0, 2, 'icone'], [1, 2, 'capture'], [2, 2, 'icone']],
    6: [[0, 0, 'capture', 1, 2], [1, 0, 'icone'], [2, 0, 'photo', 1, 2], [0, 2, 'icone'], [1, 2, 'capture'], [2, 2, 'mot']],
    5: [[0, 0, 'capture', 1, 2], [1, 0, 'icone'], [2, 0, 'photo', 1, 2], [0, 2, 'mot', 2, 1], [2, 2, 'icone']],
    4: [[0, 0, 'capture', 1, 3], [1, 0, 'icone'], [2, 0, 'photo', 1, 3], [1, 2, 'mot']]
  };
  const center = cell(1, 1);
  const rad = (b) => Math.min(VS.tuile.rayon, 0.25 * Math.min(b.w, b.h));
  const onAcc = onAccent(c.P.accent, c.T.fondSombre);
  c.round({ x: center.x, y: center.y, w: center.w, h: center.h, fill: c.P.accent, radius: rad(center), name: 'Tuile centrale', g: 'centre' });
  const ct = zt(c, grow(center, -0.2, -0.15), c.f('titre', 'nom'), { size: 54, min: 30, maxTotal: 2, color: onAcc, g: 'centre', name: 'Titre central' });
  c.kicker(ct.g, { x: center.x + 0.2, w: center.w - 0.4, align: 'center', color: onAcc, wt: 'semi', g: 'centre' });
  LAY[n].forEach((L, i) => {
    const b = cell(L[0], L[1], L[3], L[4]);
    c.round({ x: b.x, y: b.y, w: b.w, h: b.h, fill: c.P.surface, radius: rad(b), name: 'Tuile ' + (i + 1), g: 'tuiles', sub: i });
    bentoTile(c, b, tiles[i], L[2], i);
  });
  tilesMissingNote(c);
  srcLine(c, { x: M, y: H - 0.3, w: FULL_W, h: 0.28 });
};
// Bentos à dix cases autour d'un centre (produit, mot géant, chiffres, thème). Moins de 10 tuiles :
// les cases des rangées du haut et du bas fusionnent deux à deux.
function bento10(c, variant, drawCenter) {
  const B = Object.assign({}, BENTO.produit, { rows: bentoRows(c, BENTO.produit.rows) });
  const types = BENTO_TYPES[variant];
  let tiles = arr(c.t.tuiles).slice(0, 10).map((t) => (typeof t === 'string' ? { titre: t } : t || {}));
  while (tiles.length < 4) tiles.push({ titre: c.lang === 'en' ? '[TO PROVIDE: tile]' : '[À FOURNIR : tuile]' });
  const n = tiles.length;
  // Cases : haut (4), milieu gauche, milieu droit, bas (4) ; fusions selon n.
  let top = [[0], [1], [2], [3]];
  let bottom = [[0], [1], [2], [3]];
  const merges = [['b', 1], ['t', 1], ['b', 0], ['t', 0], ['b', 0], ['t', 0]];
  let count = 10;
  for (const [row, k] of merges) {
    if (count <= n) break;
    const arrR = row === 't' ? top : bottom;
    if (arrR.length > k + 1) {
      arrR.splice(k, 2, arrR[k].concat(arrR[k + 1]));
      count -= 1;
    }
  }
  top = top.slice();
  bottom = bottom.slice();
  const rc = (cols, row) => {
    const x = B.cols4[cols[0]][0];
    const last = B.cols4[cols[cols.length - 1]];
    return P(x, B.rows[row][0], last[0] + last[1] - x, B.rows[row][1]);
  };
  const slots = [];
  top.forEach((cs) => slots.push({ b: rc(cs, 0), type: types[cs[0]] }));
  slots.push({ b: P(B.mid[0][0], B.rows[1][0], B.mid[0][1], B.rows[1][1]), type: types[4] });
  slots.push({ b: P(B.mid[2][0], B.rows[1][0], B.mid[2][1], B.rows[1][1]), type: types[5] });
  bottom.forEach((cs) => slots.push({ b: rc(cs, 2), type: types[6 + cs[0]] }));
  const center = P(B.mid[1][0], B.rows[1][0], B.mid[1][1], B.rows[1][1]);
  const rad = (b) => Math.min(VS.tuile.rayon, 0.25 * Math.min(b.w, b.h));
  drawCenter(center, rad(center));
  slots.forEach((s, i) => {
    c.round({ x: s.b.x, y: s.b.y, w: s.b.w, h: s.b.h, fill: c.P.surface, radius: rad(s.b), name: 'Tuile ' + (i + 1), g: 'tuiles', sub: i });
    bentoTile(c, s.b, tiles[i] || {}, s.type, i);
  });
  tilesMissingNote(c);
  srcLine(c, { x: M, y: H - 0.3, w: FULL_W, h: 0.28 });
}
function centerProduct(c, center, rad, o) {
  o = o || {};
  c.round({ x: center.x, y: center.y, w: center.w, h: center.h, fill: o.fill || c.P.surface, radius: rad, name: 'Tuile centrale', g: 'centre' });
  const pz = P(31.7, 29.6, 36.6, 40.8);
  const spec = c.slide.image;
  const im = loadImg(c, spec);
  if (im) {
    const r = fitRect(pz, im.info, 'contain');
    contactShadow(c, r, { g: 'centre' });
    putImage(c, im, r, { name: 'Produit', g: 'centre' });
  } else {
    missingVisual(c, spec, 'objet', c.lang === 'en' ? 'cut-out product' : 'produit détouré', { g: 'centre' }, () => {
      drawSilhouette(c, { x: pz.x + pz.w * 0.3, y: pz.y + pz.h * 0.04, w: pz.w * 0.4, h: pz.h * 0.92 }, { g: 'centre', halo: false });
    });
  }
}
V['A14/produit-au-centre'] = (c) => bento10(c, 'produit-au-centre', (center, rad) => centerProduct(c, center, rad));
V['A14/tuiles-chiffres'] = (c) => bento10(c, 'tuiles-chiffres', (center, rad) => centerProduct(c, center, rad));
V['A14/mot-geant-et-produit'] = (c) => bento10(c, 'mot-geant-et-produit', (center, rad) => {
  c.round({ x: center.x, y: center.y, w: center.w, h: center.h, fill: mix(c.P.surface, '000000', 0.25), radius: rad, name: 'Tuile centrale', g: 'centre' });
  c.accentUsed = true;
  const word = c.f('titre', 'mot');
  zt(c, P(28.3, 31, 43.4, 23.7), word, { size: 84, min: 54, maxTotal: 1, noWrap: true, color: c.P.accentTxt, g: 'centre', name: 'Mot géant' });
  const pz = P(32.6, 45.3, 34.7, 40);
  const im = loadImg(c, c.slide.image);
  if (im) putImage(c, im, fitRect(pz, im.info, 'contain', undefined, 'top'), { clip: center, name: 'Produit', g: 'centre' });
  else if (c.slide.image) registerMissing(c, c.slide.image, 'objet', c.lang === 'en' ? 'cut-out product' : 'produit détouré');
});
V['A14/theme-et-matieres'] = (c) => bento10(c, 'theme-et-matieres', (center, rad) => {
  c.round({ x: center.x, y: center.y, w: center.w, h: center.h, fill: c.P.surface, radius: rad, name: 'Tuile centrale', g: 'centre' });
  const iz = P(27.3, 29.1, 25.1, 41.7);
  const im = loadImg(c, c.slide.image);
  if (im) putImage(c, im, fitRect(iz, im.info, 'cover'), { clip: iz, radius: 0.12, name: 'Image du thème', g: 'centre' });
  else missingVisual(c, c.slide.image, 'photo', c.lang === 'en' ? 'photo of the theme' : 'photo du thème', { g: 'centre' }, () => drawPhotoSoft(c, iz, { g: 'centre', radius: 0.12 }));
  zt(c, P(53.9, 36.7, 18.3, 26.5), c.f('titre', 'thème'), { size: 28, min: 16, maxTotal: 3, g: 'centre', name: 'Thème' });
});
V['A14/grille-icones'] = (c) => {
  let tiles = arr(c.t.tuiles).slice(0, 12).map((t) => (typeof t === 'string' ? { titre: t } : t || {}));
  if (!tiles.length) tiles = [{}, {}, {}, {}, {}, {}];
  if (!tiles.some((t) => loadImg(c, t.image))) registerMissing(c, null, 'icone', c.lang === 'en' ? 'one icon per new feature' : 'une icône par nouveauté');
  const n = Math.max(1, tiles.length);
  const perRow = n > 6 ? Math.ceil(n / 2) : n;
  const rows = n > 6 ? 2 : 1;
  const s = Math.min(W * 0.096, H * 0.17);
  const step = s + W * 0.018;
  const y0 = rows === 2 ? H * 0.293 : H * 0.5 - s / 2;
  tiles.forEach((t, i) => {
    const r = Math.floor(i / perRow);
    const k = i % perRow;
    const inRow = Math.min(perRow, n - r * perRow);
    const x = W / 2 + (k - (inRow - 1) / 2) * step - s / 2;
    const y = y0 + r * (H * 0.227);
    // Repli : la tuile d'icône d'A2, dans les teintes de la rangée et une forme par nouveauté.
    iconVisual(c, { x, y, w: s, h: s }, t.image, { g: 'tuiles', sub: i, fill: iconTints(c)[i % 5], glyph: ICON_GLYPHS[(i + Math.floor(i / 5)) % 5] });
  });
  c.groups = [G('tuiles', /\b(?:grilles?|icones?|icons?|tuiles?)\b/)];
};

// Bento d'un logiciel (outil métier, SaaS) : grille de 12 colonnes lue en trois zones, qui suivent
// le parcours montré de gauche à droite ; tuile centrale sombre (logo, puis le nom ou la boucle en
// trois mots). Chaque tuile porte son titre en haut à gauche et un composant de l'interface, isolé
// de son écran, qui sort de la tuile par la droite ou par le bas. Une seule tuile d'accent : la liste.
// Mesures : récaps des sessions développeurs (marge 2,4 à 3,1 % L, gouttière 0,6 à 1 % L) et
// convention pour les rangées (300 / 352 / 312 sur 1080).
const BENTO_LOGICIEL = {
  marge: 0.21, gouttiere: 0.094, rangees: [300, 352, 312], centre: [4, 4, 1],
  // Cases par nombre de tuiles : [colonne de début, colonnes, rangée, type par défaut].
  cases: {
    11: [[0, 4, 0, 'fragment'], [4, 4, 0, 'fragment'], [8, 4, 0, 'fragment'], [0, 2, 1, 'chiffre'], [2, 2, 1, 'fragment'], [8, 2, 1, 'fragment'], [10, 2, 1, 'photo'], [0, 4, 2, 'fragment'], [4, 2, 2, 'fragment'], [6, 2, 2, 'liste'], [8, 4, 2, 'fragment']],
    10: [[0, 4, 0, 'fragment'], [4, 4, 0, 'fragment'], [8, 4, 0, 'fragment'], [0, 4, 1, 'fragment'], [8, 2, 1, 'fragment'], [10, 2, 1, 'photo'], [0, 4, 2, 'fragment'], [4, 2, 2, 'fragment'], [6, 2, 2, 'liste'], [8, 4, 2, 'fragment']],
    9: [[0, 4, 0, 'fragment'], [4, 4, 0, 'fragment'], [8, 4, 0, 'fragment'], [0, 4, 1, 'fragment'], [8, 4, 1, 'photo'], [0, 4, 2, 'fragment'], [4, 2, 2, 'fragment'], [6, 2, 2, 'liste'], [8, 4, 2, 'fragment']],
    8: [[0, 4, 0, 'fragment'], [4, 4, 0, 'fragment'], [8, 4, 0, 'fragment'], [0, 4, 1, 'fragment'], [8, 4, 1, 'photo'], [0, 4, 2, 'fragment'], [4, 4, 2, 'liste'], [8, 4, 2, 'fragment']],
    7: [[0, 6, 0, 'fragment'], [6, 6, 0, 'fragment'], [0, 4, 1, 'fragment'], [8, 4, 1, 'photo'], [0, 4, 2, 'fragment'], [4, 4, 2, 'liste'], [8, 4, 2, 'fragment']],
    6: [[0, 6, 0, 'fragment'], [6, 6, 0, 'fragment'], [0, 4, 1, 'fragment'], [8, 4, 1, 'photo'], [0, 6, 2, 'fragment'], [6, 6, 2, 'fragment']]
  },
  titre: [16, 11], texte: 9, liste: [13, 8], chiffre: [96, 48], centreTitre: [30, 18], centreTexte: 9
};
function logicielBox(c) {
  const S = BENTO_LOGICIEL;
  const m = S.marge;
  const g = S.gouttiere;
  const room = c.sourceOnSlide && !c.sourceDone ? 0.2 : 0;
  const cw = (W - 2 * m - 11 * g) / 12;
  const usable = H - 2 * m - 2 * g - room;
  const tot = S.rangees.reduce((a, b) => a + b, 0);
  const rh = S.rangees.map((r) => usable * r / tot);
  const ry = [m, m + rh[0] + g, m + rh[0] + rh[1] + 2 * g];
  return (col, span, row) => ({ x: m + col * (cw + g), y: ry[row], w: span * cw + (span - 1) * g, h: rh[row] });
}
// Titre (et sa ligne de texte) en haut à gauche d'une tuile ; rend la géométrie pour poser le composant.
function logicielHead(c, b, tile, i, o) {
  const S = BENTO_LOGICIEL;
  const pad = o.pad;
  const paras = [];
  c.para(str(tile.titre) || (c.lang === 'en' ? '[TO PROVIDE: name]' : '[À FOURNIR : nom]'), { wt: 'semi', font: 'titre', color: o.color, gap: 0.05 }).forEach((p) => paras.push(p));
  if (str(tile.texte)) c.para(tile.texte, { pt: S.texte, wt: 'regular', font: 'texte', color: o.color2 }).forEach((p) => paras.push(p));
  const it = c.text({ x: b.x + pad, y: b.y + pad, w: o.w, h: o.h, paras, size: S.titre[0], min: S.titre[1], maxTotal: 4, wt: 'semi', align: 'left', valign: o.valign || 'top', font: 'titre', color: o.color, lh: K.titre, balance: true, name: 'Titre tuile ' + (i + 1), g: 'tuiles', sub: i });
  return textGeom(it);
}
// Tuile « fragment » : un composant isolé (carte, colonne de statuts, bouton, tableau) posé à sa
// taille d'interface : 1 px de la capture = 1 px d'un écran de 1 920 px de large (× tile.echelle,
// 0,5 pour un export 2x). Large : sous le titre ; haut (colonne, panneau) : à droite du titre.
// Un composant qui tient, ou qui dépasse de moins de moitié, est montré entier (réduit au besoin),
// calé en bas ; au-delà, il garde sa taille et sort de la tuile par la droite et le bas.
function logicielFragment(c, b, tile, i, rad, pad) {
  const g = { g: 'tuiles', sub: i };
  const im = loadImg(c, tile.image);
  const tall = im ? im.info.w / im.info.h < 0.8 : false;
  const head = logicielHead(c, b, tile, i, { pad, w: tall ? b.w * 0.5 - pad : b.w - 2 * pad, h: tall ? b.h - 2 * pad : b.h * 0.42, color: c.P.fg, color2: c.P.fg2 });
  const yTop = tall ? b.y + pad : head.top + head.h + 0.12;
  if (!im) {
    const cap = tall ? { x: b.x + b.w * 0.56, y: b.y + pad, w: b.w * 0.44 - pad, h: b.h } : { x: b.x + pad, y: yTop, w: b.w - pad, h: b.y + b.h - yTop + 0.1 };
    (c._fragmentsSans = c._fragmentsSans || []).push(str(tile.titre) || String(i + 1));
    const ph = { id: c.phs.length, name: c.L.cap.fragment + (str(tile.titre) ? ' · ' + shortLabel(tile.titre, 6) : ''), kind: 'fragment', g: g.g, sub: g.sub };
    c.phs.push(ph);
    const prev = c.curPh;
    c.curPh = ph.id;
    try {
      const start = c.items.length;
      drawWindow(c, cap, Object.assign({}, schemaColors(c), { shadow: false }), rng(11 + i), ['tableau', 'liste', 'document'][i % 3]);
      clipItems(c, start, b);
    } finally {
      c.curPh = prev;
    }
    return;
  }
  const k = (Number(tile.echelle) > 0 ? Number(tile.echelle) : 1) * W / 1920;
  let w = im.info.w * k;
  let h = im.info.h * k;
  const room = tall ? { x: b.x + b.w * 0.56, y: b.y + pad, w: b.w * 0.44 - pad, h: b.h - 2 * pad } : { x: b.x + pad, y: yTop, w: b.w - 2 * pad, h: b.y + b.h - pad - yTop };
  let r;
  if (w <= room.w * 1.5 && h <= room.h * 1.5) {
    const s = Math.min(1, room.w / w, room.h / h);
    w *= s;
    h *= s;
    r = { x: room.x, y: tall ? room.y : room.y + room.h - h, w, h };
  } else {
    if (tall && w > room.w) {
      h *= room.w / w;
      w = room.w;
    }
    r = { x: room.x, y: room.y, w, h };
  }
  putImage(c, im, r, Object.assign({ clip: b, radius: Math.min(0.08, rad / 2), name: 'Fragment ' + (i + 1) }, g));
  const vis = inter(r, b);
  if (vis) c.round(Object.assign({ x: vis.x, y: vis.y, w: vis.w, h: vis.h, line: c.P.line, lineW: 0.5, radius: Math.min(0.08, rad / 2), name: 'Contour fragment ' + (i + 1) }, g));
}
// Composants manquants : une consigne par bento, avec le brief d'un composant isolé.
function fragmentsMissingNote(c) {
  const l = uniq(c._fragmentsSans || []);
  if (!l.length) return;
  c.missing.push({ kind: 'fragment', attendu: (c.lang === 'en' ? 'components of the tiles: ' : 'composants des tuiles : ') + l.join(', '), chemin: '', brief: (BRIEF[c.lang] || BRIEF.fr).fragment });
  c.warn('Tuiles sans composant (' + l.join(', ') + ') : interface schématique à la place.');
}
function logicielTile(c, b, tile, type, i, o) {
  const S = BENTO_LOGICIEL;
  const g = { g: 'tuiles', sub: i };
  const rad = Math.min(VS.tuile.rayon, 0.25 * Math.min(b.w, b.h));
  const pad = Math.min(0.2, Math.max(0.14, b.w * 0.07));
  if (type === 'liste') {
    const acc = o.accent;
    const fill = acc ? c.P.accent : c.P.surface;
    const ink = acc ? onAccent(c.P.accent, c.T.fondSombre) : c.P.fg;
    c.round(Object.assign({ x: b.x, y: b.y, w: b.w, h: b.h, fill, radius: rad, name: 'Tuile ' + (i + 1) }, g));
    if (str(tile.titre)) c.text(Object.assign({ x: b.x + pad, y: b.y + pad, w: b.w - 2 * pad, h: 0.24, text: str(tile.titre).toLocaleUpperCase(c.lang === 'en' ? 'en' : 'fr'), size: 8, min: 7, maxTotal: 1, wt: 'semi', align: 'left', valign: 'top', font: 'texte', color: ink, name: 'Surtitre tuile ' + (i + 1) }, g));
    const lines = arr(tile.lignes).length ? arr(tile.lignes) : [str(tile.texte) || (c.lang === 'en' ? '[TO PROVIDE: line]' : '[À FOURNIR : ligne]')];
    const paras = [];
    lines.slice(0, 5).forEach((l) => c.para(l, { wt: 'semi', font: 'titre', color: ink, gapK: 0.35 }).forEach((p) => paras.push(p)));
    c.text(Object.assign({ x: b.x + pad, y: b.y + pad + 0.3, w: b.w - 2 * pad, h: b.h - 2 * pad - 0.3, paras, size: S.liste[0], min: S.liste[1], maxTotal: 7, wt: 'semi', align: 'left', valign: 'bottom', font: 'titre', color: ink, lh: K.titre, name: 'Liste tuile ' + (i + 1) }, g));
    return;
  }
  c.round(Object.assign({ x: b.x, y: b.y, w: b.w, h: b.h, fill: c.P.surface, radius: rad, name: 'Tuile ' + (i + 1) }, g));
  if (type === 'fragment' || type === 'capture') return logicielFragment(c, b, tile, i, rad, pad);
  if (type === 'chiffre') {
    // Le chiffre en grand en haut à gauche, son titre en bas ; jamais en accent (la liste le porte).
    c.text(Object.assign({ x: b.x + pad * 0.7, y: b.y + pad * 0.6, w: b.w - 1.4 * pad, h: b.h * 0.58, text: tile.chiffre || (c.lang === 'en' ? '[TO PROVIDE: figure]' : '[À FOURNIR : chiffre]'), size: S.chiffre[0], min: S.chiffre[1], maxTotal: 1, wt: 'semi', align: 'left', valign: 'top', font: 'titre', color: c.P.fg, lh: 0.9, name: 'Chiffre tuile ' + (i + 1) }, g));
    logicielHead(c, b, tile, i, { pad, w: b.w - 2 * pad, h: b.h - 2 * pad, valign: 'bottom', color: c.P.fg, color2: c.P.fg2 });
    return;
  }
  // Photo, icône, mot, matière, coloris : le dessin commun des tuiles de bento.
  bentoTile(c, b, tile, type, i);
}
V['A14/fragments-logiciel'] = (c) => {
  const S = BENTO_LOGICIEL;
  const box = logicielBox(c);
  let tiles = arr(c.t.tuiles).slice(0, 11).map((t) => (typeof t === 'string' ? { titre: t } : t || {}));
  if (arr(c.t.tuiles).length > 11) c.warn('Bento logiciel : 11 tuiles au plus ; les suivantes sont ignorées.');
  while (tiles.length < 6) tiles.push({ titre: c.lang === 'en' ? '[TO PROVIDE: tile]' : '[À FOURNIR : tuile]' });
  const cases = S.cases[tiles.length];
  // Tuile centrale : aplat sombre sur un deck clair, aplat d'accent sur un deck sombre.
  const center = box(S.centre[0], S.centre[1], S.centre[2]);
  const rad = (b) => Math.min(VS.tuile.rayon, 0.25 * Math.min(b.w, b.h));
  const dark = darkBg(c);
  const cFill = dark ? c.P.accent : c.T.fondSombre;
  const cInk = dark ? onAccent(c.P.accent, c.T.fondSombre) : c.T.texteSombre;
  const cInk2 = dark ? cInk : c.T.texteSecSombre;
  c.round({ x: center.x, y: center.y, w: center.w, h: center.h, fill: cFill, radius: rad(center), name: 'Tuile centrale', g: 'centre' });
  const pad = 0.26;
  const logo = loadImg(c, c.slide.image);
  if (logo) putImage(c, logo, fitRect({ x: center.x + pad, y: center.y + pad, w: center.w * 0.4, h: 0.3 }, logo.info, 'contain', 'left', 'top'), { name: 'Logo', g: 'centre' });
  else if (c.slide.image) registerMissing(c, c.slide.image, 'logo', c.lang === 'en' ? 'logo for a dark background' : 'logo pour fond sombre');
  const hasTxt = !!str(c.t.texte);
  c.text({ x: center.x + pad, y: center.y + pad + 0.36, w: center.w * (hasTxt ? 0.6 : 1) - pad, h: center.h - 2 * pad - 0.36, text: c.f('titre', 'nom'), size: S.centreTitre[0], min: S.centreTitre[1], maxTotal: 3, wt: 'semi', align: 'left', valign: 'bottom', font: 'titre', color: cInk, lh: K.titre, name: 'Titre central', g: 'centre' });
  if (hasTxt) c.text({ x: center.x + center.w * 0.6, y: center.y + pad, w: center.w * 0.4 - pad, h: center.h - 2 * pad, text: c.t.texte, size: S.centreTexte, min: 7, maxTotal: 6, wt: 'regular', align: 'left', valign: 'bottom', font: 'texte', color: cInk2, name: 'Texte central', g: 'centre' });
  // Une seule tuile d'accent : la première liste, et seulement sur un deck clair (sur sombre, le centre l'a).
  let accentFree = !dark;
  tiles.forEach((t, i) => {
    const L = cases[i];
    const type = normKey(t.type) || (t.chiffre ? 'chiffre' : arr(t.lignes).length ? 'liste' : L[3]);
    const acc = type === 'liste' && accentFree;
    if (acc) accentFree = false;
    logicielTile(c, box(L[0], L[1], L[2]), t, type, i, { accent: acc });
  });
  if (!accentFree || dark) c.accentUsed = true;
  tilesMissingNote(c);
  fragmentsMissingNote(c);
  srcLine(c, { x: M, y: H - 0.3, w: FULL_W, h: 0.28 });
  c.groups = [G('centre', KW.centre, { prio: 1 }), G('tuiles', KW.tuiles, { multi: true })];
};

// A19 : prix. Le produit d'un côté (ombre de contact sur fond clair), le prix de l'autre ; un prix
// manquant reste un marqueur estompé au corps du prix.
function offers(c) {
  let o = arr(c.t.offres).slice(0, 4);
  if (!o.length) o = [{ nom: c.t.titre, mention: c.t.mention, prix: c.t.prix, note: c.t.note }];
  return o.map((x) => x || {});
}
function priceColumn(c, list, zcol) {
  const S = STYLE.A19;
  const stacks = [];
  let cap = 0;
  list.forEach((o, i) => {
    const st = offerStack(c, o, zcol.x, zcol.w, 'center', cap, list.length > 1 ? i : undefined, S.ecartNomColonne);
    stacks.push(st);
    cap = st.base + S.ecartOffres;
  });
  const total = stacks[stacks.length - 1].base;
  stacks.forEach((st) => shiftItems(st.items, S.cy - total / 2));
  c.kicker(textGeom(stacks[0].nameItem), { x: zcol.x, w: zcol.w, align: 'center' });
}
V['A19/colonne'] = (c) => {
  productVisual(c, P(8, 5, 35, 90), c.slide.image, { g: 'visuel', silBox: () => P(15, 14, 21, 72) });
  priceColumn(c, offers(c).slice(0, 1), P(47, 0, 46, 0));
};
V['A19/deux-offres'] = (c) => {
  productVisual(c, P(8, 5, 35, 90), c.slide.image, {
    g: 'visuel', repli: (b) => {
      drawSilhouette(c, P(11, 10, 20, 78), { g: 'visuel', ton: 0.05 });
      drawSilhouette(c, P(25, 26, 15, 60), { g: 'visuel' });
      void b;
    }
  });
  priceColumn(c, offers(c).slice(0, 2), P(47, 0, 46, 0));
};
V['A19/nom-en-haut'] = (c) => {
  const S = STYLE.A19;
  const o = offers(c)[0];
  const st = offerStack(c, o, M, FULL_W, 'center', S.nomHaut, undefined, S.ecartNomHaut);
  const top = Math.max(H * 0.47, st.base + 0.3);
  productVisual(c, { x: P(18, 0, 64, 0).x, y: top, w: P(0, 0, 64, 0).w, h: H * 0.9 - top }, c.slide.image, { g: 'visuel', alignY: 'bottom', silBox: (b) => ({ x: W * 0.32, y: b.y + b.h * 0.25, w: W * 0.36, h: b.h * 0.7 }), forme: 'bande', exact: true });
  c.kicker(textGeom(st.nameItem), { x: M, w: FULL_W, align: 'center' });
};
V['A19/gamme-alignee'] = (c) => {
  const list = offers(c).slice(0, 4);
  const n = list.length;
  const step = W * 0.213;
  list.forEach((o, i) => {
    const cx = W / 2 + (i - (n - 1) / 2) * step;
    // Même échelle pour tous (fiche : de 14 à 65 % H), posés sur la même ligne.
    productVisual(c, { x: cx - W * 0.085, y: H * 0.1, w: W * 0.17, h: H * 0.55 }, o.image, { g: 'visuel', sub: i, alignY: 'bottom', exact: true, silBox: (b) => {
      const w = b.w * 0.78;
      const h = Math.min(b.h * 0.9, w / 0.6);
      return { x: b.x + (b.w - w) / 2, y: b.y + b.h - h, w, h };
    }, ton: i * 0.03 });
    const zn = { x: cx - W * 0.095, y: H * 0.71, w: W * 0.19, h: H * 0.06 };
    const t = zt(c, zn, str(o.nom) || c.f('_', 'nom'), { size: 20, min: 13, maxTotal: 1, anchor: 'top', g: 'nom', sub: i, name: 'Nom' });
    let base = t.g.base;
    if (o.mention) base = zt(c, { x: zn.x, y: base + 0.12, w: zn.w, h: 0.2 }, o.mention, { size: 11, min: 9, maxTotal: 1, font: 'texte', wt: 'regular', color: c.P.fg2, anchor: 'top', g: 'prix', sub: i, name: 'Mention' }).g.base;
    zt(c, { x: zn.x, y: base + 0.1, w: zn.w, h: 0.3 }, str(o.prix) || c.f('_', 'prix'), { size: 24, min: 15, maxTotal: 1, noWrap: true, anchor: 'top', g: 'prix', sub: i, name: 'Prix' });
  });
  c.groups = [SUR, G('visuel', KW.visuel), G('nom', KW.nom), G('prix', KW.prix)];
};
V['A19/prix-heros'] = (c) => {
  c.kicker(priceHero(c, offers(c)[0]), { x: M, w: FULL_W, align: 'center' });
  c.sourceLine();
};
// Ancrage : le prix de référence en gris (état « reference »), puis le vrai prix en accent au même
// endroit, sur la slide suivante (Morphose ou fondu).
V['A19/ancrage'] = (c) => {
  const ref = normKey(c.t.etat) === 'reference';
  const o = offers(c)[0];
  c.accentUsed = !ref;
  const z = P(5, 37, 90, 26);
  const color = ref ? c.P.fg2 : c.P.accentTxt;
  const h = zt(c, z, str(o.prix) || c.f('_', 'prix'), { size: 144, min: 96, maxTotal: 1, noWrap: true, color, g: 'prix', name: 'Prix' });
  const lib = tv(c, 'libelle') || o.note;
  if (lib) zt(c, P(10, 76, 80, 7), lib, { size: 18, min: 14, maxTotal: 1, font: 'texte', wt: 'regular', color: c.P.fg2, g: 'prix', name: 'Précision' });
  if (o.nom) c.line({ text: o.nom, x: M, w: FULL_W, base: h.g.capTop - 0.45, size: scalePt(24, 'texte'), wt: 'regular', color: c.P.fg2, align: 'center', font: 'texte', name: 'Nom', g: 'nom' });
  c.sourceLine();
};

// A20 : disponibilité.
function rangeFallback(c, zone, o) {
  // Une gamme générique, calée en bas : grand écran, tablette, téléphone, boîtier.
  o = o || {};
  const bottom = zone.y + zone.h;
  const hgt = zone.h;
  // Le grand écran porte la gamme (fiche : 35 à 90 % H) ; les autres appareils se serrent à côté.
  const specs = [['portable', 0.7, 0.98], ['tablette', 0.36, 0.68], ['telephone', 0.13, 0.62], ['boitier', 0.09, 0.26]];
  const total = specs.reduce((a, s) => a + s[1], 0) + 0.06;
  let x = zone.x + (zone.w - total * Math.min(zone.w / total, hgt * 2.2)) / 2;
  const unit = Math.min(zone.w / total, hgt * 2.2);
  specs.forEach((s, i) => {
    const w = s[1] * unit;
    const h = s[2] * hgt;
    const box = { x, y: bottom - h, w, h };
    if (s[0] === 'boitier') drawSilhouette(c, box, { g: o.g, forme: 'carre', halo: false });
    else drawDevice(c, box, s[0], { g: o.g, mute: i !== 0, variant: ['tableau', 'liste', 'liste'][i] });
    x += w + unit * 0.012;
  });
}
function dateBlock(c, zl, zd, o) {
  o = o || {};
  let geo = null;
  let base = null;
  if (tv(c, 'libelle')) {
    const l = zt(c, zl, c.t.libelle, { size: o.lsize || 16, min: 12, maxTotal: 1, font: 'texte', wt: 'regular', color: c.P.fg2, anchor: 'top', g: 'libelle', name: 'Libellé' });
    base = l.g.base;
    geo = l.g;
  }
  const d = zt(c, { x: zd.x, y: base === null ? zd.y : base + (o.ecart || STYLE.A20.ecart), w: zd.w, h: zd.h }, c.f('titre', 'date'), { size: o.size || 40, min: o.min || 30, maxTotal: 2, anchor: 'top', g: 'date', name: 'Date' });
  c.kicker(geo || d.g, { x: zd.x, w: zd.w, align: 'center', ecart: 0.9 });
  return d;
}
V['A20/haut-et-gamme'] = (c) => {
  const d = dateBlock(c, P(30, 7, 40, 4.5), P(10, 12.5, 80, 11));
  const top = Math.max(H * 0.3, d.g.base + 0.35);
  const zone = { x: W * 0.04, y: top, w: W * 0.92, h: H * 0.89 - top };
  const im = loadImg(c, c.slide.image);
  if (im) {
    const r = fitRect(zone, im.info, 'contain', undefined, 'bottom');
    contactShadow(c, r, { g: 'visuel', largeur: 0.92 });
    putImage(c, im, r, { name: 'Gamme', g: 'visuel' });
  } else missingVisual(c, c.slide.image, 'objet', c.lang === 'en' ? 'the product range, aligned' : 'la gamme alignée', { g: 'visuel' }, () => rangeFallback(c, zone, { g: 'visuel' }));
  c.sourceLine();
};
V['A20/suite-de-dates'] = V['A20/haut-et-gamme'];
V['A20/colonne'] = (c) => {
  productVisual(c, P(11, 8, 42, 84), c.slide.image, { g: 'visuel', silBox: () => P(21, 16, 22, 70) });
  const zd = P(57, 44, 34, 10.5);
  const zl = P(57, 38.5, 34, 4.5);
  dateBlock(c, zl, tv(c, 'libelle') ? zd : P(57, 42, 34, 10.5));
  c.sourceLine();
};
V['A20/date-et-lieux'] = (c) => {
  productVisual(c, P(5, 22, 52, 62), c.slide.image, { g: 'visuel', silBox: () => P(18, 26, 26, 56) });
  const d = dateBlock(c, P(62, 22, 32, 4.5), P(62, 27, 32, 9));
  const lieux = arr(c.t.lieux).slice(0, 6);
  if (lieux.length) zlist(c, { x: P(62, 0, 0, 0).x, y: d.g.base + 0.42, w: P(0, 0, 32, 0).w, h: 1.6 }, lieux, { size: 18, min: 12, k: 1.8, wt: 'regular', color: c.P.fg, align: 'center', anchor: 'top', g: 'lignes', maxLines: 1, actif: 0 });
  c.groups = [SUR, G('visuel', KW.visuel), G('libelle', KW.libelle), G('date', KW.date), G('lignes', /\b(?:lieux|pays|villes?|places?|countries|cities|listes?)\b/)];
  c.sourceLine();
};
V['A20/mot-seul'] = (c) => {
  const S = STYLE.A20;
  const A = STYLE.A1;
  const motParas = c.para(c.f('titre', 'date'), { wt: 'semi', font: 'titre', g: 'date' });
  const m = topBox(c, { x: P(5, 0, 0, 0).x, w: P(0, 0, 90, 0).w, capTop: 0, paras: motParas, stages: bigStages(A.corps[0], motParas.length > 1), wt: 'semi', align: 'center', font: 'titre', lh: K.titre, balance: true, name: 'Date', g: 'date' });
  const label = tv(c, 'libelle');
  const l = label ? topBox(c, { x: M, w: FULL_W, capTop: 0, text: label, size: 24, min: 16, maxLines: 1, color: c.P.fg2, align: 'center', font: 'texte', lh: K.titre, name: 'Libellé', g: 'libelle' }) : null;
  const gap = l ? S.seul.ecart * m.g.capH : 0;
  const lh = l ? l.g.base - l.g.capTop : 0;
  const top = A.cy - (lh + gap + (m.g.base - m.g.capTop)) / 2;
  let geo;
  if (l) {
    geo = placeTop(l.it, top).g;
    placeTop(m.it, geo.base + gap);
  } else geo = placeTop(m.it, top).g;
  c.kicker(geo, { x: M, w: FULL_W, align: 'center', ecart: 0.9 });
  c.sourceLine();
};

// FIN : la slide finale. Le signe (logo de l'utilisateur) ou un mot ; les mentions en petit dessous.
function mentions(c, z) {
  const m = arr(c.t.mentions).map(str).filter((s) => s.trim());
  if (!m.length) return;
  const paras = [];
  m.slice(0, 8).forEach((s) => c.para(s, { wt: 'regular', font: 'texte', color: c.P.fg2 }).forEach((p) => paras.push(p)));
  c.text({ x: z.x, y: z.y, w: z.w, h: z.h, paras, size: 9, min: 7, maxTotal: 8, wt: 'regular', color: c.P.fg2, align: 'center', valign: 'top', font: 'texte', lh: K.titre, name: 'Mentions', g: 'note' });
}
function signLogo(c, z, o) {
  o = o || {};
  const spec = c.slide.image && !o.photo ? c.slide.image : (c.slide.logo_final || (c.T.logo ? { chemin: c.T.logo } : null));
  const im = loadImg(c, spec);
  if (!im) return false;
  putImage(c, im, fitRect(z, im.info, 'contain'), { name: 'Signe', g: 'titre' });
  return true;
}
function finalWord(c, o) {
  o = o || {};
  const S = STYLE.finale;
  const paras = c.para(c.f('titre', 'mot'), { wt: 'semi', font: 'titre', g: 'titre', point: true });
  const t = centerBox(c, { x: P(5, 0, 0, 0).x, w: P(0, 0, 90, 0).w, cy: S.cy, paras, stages: bigStages(S.corps[0], paras.length > 1), wt: 'semi', align: 'center', font: 'titre', lh: K.titre, balance: true, name: 'Titre' });
  c.kicker(t.g, { x: M, w: FULL_W, align: 'center' });
  return t;
}
function finalLine(c, z, o) {
  const txt = tv(c, 'libelle') || tv(c, 'ligne');
  if (!txt) return;
  zt(c, z, txt, { size: 22, min: 16, maxTotal: 1, font: 'texte', wt: 'regular', color: (o && o.color) || c.P.fg, g: 'libelle', name: 'Ligne' });
}
V['FIN/signe-seul'] = (c) => {
  if (!signLogo(c, P(35, 34, 30, 27.5))) {
    V['FIN/mot-final'](c);
    return;
  }
  mentions(c, P(10, 86, 80, 10));
};
V['FIN/signe-et-ligne'] = (c) => {
  if (!signLogo(c, P(35, 34, 30, 27.5))) finalWord(c);
  finalLine(c, P(15, 85, 70, 5.5));
  mentions(c, P(20, 92, 60, 6));
};
V['FIN/signe-et-evenement'] = (c) => {
  if (!signLogo(c, P(35, 31, 30, 27.5))) {
    zt(c, P(10, 36, 80, 18), c.f('titre', 'événement'), { size: 60, min: 40, maxTotal: 1, g: 'titre', name: 'Événement' });
    if (tv(c, 'lieu')) zt(c, P(20, 58, 60, 5), c.t.lieu, { size: 16, min: 12, maxTotal: 1, font: 'texte', wt: 'regular', color: c.P.fg2, g: 'libelle', name: 'Lieu' });
  } else {
    zt(c, P(20, 68.5, 60, 6), c.f('titre', 'événement'), { size: 24, min: 18, maxTotal: 1, g: 'titre', name: 'Événement' });
    zt(c, P(20, 75.5, 60, 4), tv(c, 'lieu') || c.f('lieu', 'lieu'), { size: 16, min: 12, maxTotal: 1, font: 'texte', wt: 'regular', color: c.P.fg2, g: 'libelle', name: 'Lieu' });
  }
  mentions(c, P(10, 86, 80, 10));
};
V['FIN/signe-sur-photo'] = (c) => {
  const spec = c.slide.image_fond || c.slide.image;
  if (!loadImg(c, spec)) {
    if (spec) registerMissing(c, spec, 'photo', c.lang === 'en' ? 'calm photo (sky, material)' : 'photo calme (ciel, matière)');
    V['FIN/signe-seul'](c);
    return;
  }
  fullPhoto(c, spec, { voile: c.slide.voile !== undefined ? Number(c.slide.voile) : 20, g: 'visuel' });
  if (!signLogo(c, P(35, 33, 30, 29), { photo: true })) {
    const t = finalWord(c);
    t.it.color = 'FFFFFF';
    t.it.paras.forEach((p) => { p.color = 'FFFFFF'; });
  }
  finalLine(c, P(15, 85, 70, 5), { color: 'FFFFFF' });
};
V['FIN/mot-final'] = (c) => {
  finalWord(c);
  finalLine(c, P(15, 85, 70, 5));
  mentions(c, P(10, 92, 80, 6));
};

// COLORIS : la gamme de coloris. Même angle, même échelle ; aucun nom écrit (sauf afficher_noms) ;
// une silhouette remplie du HEX fourni, sinon des paliers de gris et une image à fournir.
function colorways(c) {
  const list = arr(c.t.coloris).map((x) => (typeof x === 'string' ? { nom: x } : x || {}));
  const imgs = imagesOf(c);
  if (!list.length && imgs.length) return imgs.map((im) => ({ image: im }));
  if (!list.length) return [{}, {}, {}, {}];
  return list.map((x, i) => Object.assign({ image: x.image || imgs[i] }, x));
}
function colorwayVisual(c, box, cw, i, o) {
  o = o || {};
  const hx = hex(cw.hex, null, 'coloris', null);
  const im = loadImg(c, cw.image);
  const g = { g: 'visuel', sub: i };
  if (im) {
    const r = fitRect(box, im.info, 'contain', undefined, o.alignY || 'bottom');
    if (o.halo) softHalo(c, r, Object.assign({ color: hx || c.P.fg, opacite: hx ? 0.35 : 0.12 }, g));
    if (o.ombre !== false) contactShadow(c, r, g);
    putImage(c, im, r, Object.assign({ name: 'Coloris ' + (i + 1), rot: o.rot }, g));
    return r;
  }
  if (!c._colorisNoted) {
    c._colorisNoted = true;
    registerMissing(c, cw.image, 'objet', c.lang === 'en' ? 'one cut-out PNG per colourway, same angle and scale' : 'un PNG détouré par coloris, même angle et même échelle');
  }
  const sil = o.silBox ? o.silBox(box) : box;
  if (o.rot) {
    // Silhouette pivotée : le même volume modelé, tourné, sans ombre ni halo.
    drawSilhouette(c, sil, Object.assign({ exact: true, fill: hx || undefined, ton: hx ? 0 : i * 0.06, ombre: false, halo: false, rot: o.rot }, g));
    return null;
  }
  if (o.halo && hx) softHalo(c, sil, Object.assign({ color: hx, opacite: 0.35 }, g));
  drawSilhouette(c, sil, Object.assign({ exact: true, fill: hx || undefined, ton: hx ? 0 : i * 0.06, ombre: o.ombre, halo: false }, g));
  return null;
}
function colorNames(c, list, xs, w) {
  if (!c.t.afficher_noms) return;
  list.forEach((cw, i) => { if (str(cw.nom)) zt(c, { x: xs[i] - w / 2, y: H * 0.84, w, h: H * 0.05 }, cw.nom, { size: 16, min: 11, maxTotal: 1, font: 'texte', wt: 'regular', color: c.P.fg2, g: 'visuel', sub: i, name: 'Nom coloris' }); });
}
V['COLORIS/rangee-alignee'] = (c) => {
  const list = colorways(c).slice(0, 5);
  const n = list.length;
  const bw = W * (n === 5 ? 0.17 : 0.206);
  const step = W * (n === 5 ? 0.185 : 0.231);
  const xs = list.map((x, i) => W / 2 + (i - (n - 1) / 2) * step);
  list.forEach((cw, i) => colorwayVisual(c, { x: xs[i] - bw / 2, y: H * 0.18, w: bw, h: H * 0.62 }, cw, i, { silBox: (b) => ({ x: b.x + b.w * 0.2, y: b.y, w: b.w * 0.6, h: b.h }) }));
  colorNames(c, list, xs, bw);
};
V['COLORIS/rangee-chevauchee'] = (c) => {
  const list = colorways(c).slice(0, 5);
  list.forEach((cw, i) => colorwayVisual(c, P(19 + i * 13, 23 + i * 2, 22, 85), cw, i, { alignY: 'top', ombre: false, silBox: (b) => ({ x: b.x, y: b.y, w: b.w, h: b.h }) }));
};
V['COLORIS/eventail'] = (c) => {
  const list = colorways(c).slice(0, 5);
  const n = list.length;
  const ow = W * 0.19;
  const oh = H * 0.6;
  const pivot = { x: W * 0.38, y: H * 0.8 };
  // Du fond (le plus pivoté) vers l'avant (à plat).
  for (let i = n - 1; i >= 0; i--) {
    const ang = n > 1 ? i * 60 / (n - 1) : 0;
    const a = ang * Math.PI / 180;
    const vx = ow / 2;
    const vy = -oh / 2;
    const cx = pivot.x + vx * Math.cos(a) - vy * Math.sin(a);
    const cy = pivot.y + vx * Math.sin(a) + vy * Math.cos(a);
    colorwayVisual(c, { x: cx - ow / 2, y: cy - oh / 2, w: ow, h: oh }, list[i], i, { rot: ang, ombre: false, alignY: 'middle' });
  }
};
V['COLORIS/un-par-un'] = (c) => {
  const cw = colorways(c)[0];
  colorwayVisual(c, P(35, 12, 30, 76), cw, 0, { halo: true, ombre: false, alignY: 'middle', silBox: (b) => ({ x: b.x + b.w * 0.15, y: b.y, w: b.w * 0.7, h: b.h }) });
};
V['COLORIS/mur'] = (c) => {
  const list = colorways(c);
  let k = 0;
  [[6, [-6, 12, 30, 48, 66, 84]], [52, [3, 21, 39, 57, 75, 93]]].forEach(([y, xs]) => {
    xs.forEach((x) => {
      colorwayVisual(c, P(x, y, 15, 38), list[k % list.length], k, { ombre: false, alignY: 'middle', silBox: (b) => ({ x: b.x + b.w * 0.12, y: b.y, w: b.w * 0.76, h: b.h }) });
      k += 1;
    });
  });
};

// Les noms d'une rangée de tuiles au même corps : le plus petit des ajustements (un nom long ne
// rapetisse plus seul dans sa tuile).
function sameSize(items) {
  const fs = items.filter((it) => it && it.fitted).map((it) => it.fitted);
  if (fs.length < 2) return;
  const m = Math.min.apply(null, fs);
  items.forEach((it) => { if (it && it.fitted) it.fitted = m; });
}
// FRISE : les jalons sur une seule ligne, le présent seul en accent ; aucune date inventée.
function milestones(c) {
  return arr(c.t.jalons).map((x) => (typeof x === 'string' ? { titre: x } : x || {}));
}
V['FRISE/rangee-datee'] = (c) => {
  let list = milestones(c).slice(0, 7);
  if (!list.length) list = [{}, {}, {}, {}, {}, {}];
  const n = list.length;
  const tw = W * 0.129;
  const step = W * 0.158;
  c.accentUsed = true;
  const names = [];
  list.forEach((j, i) => {
    const cx = W / 2 + (i - (n - 1) / 2) * step;
    const b = { x: cx - tw / 2, y: H * 0.3, w: tw, h: H * 0.23 };
    const now = i === n - 1;
    c.round({ x: b.x, y: b.y, w: b.w, h: b.h, fill: c.P.surface, line: now ? c.P.accent : undefined, lineW: now ? 1.5 : undefined, radius: Math.min(VS.tuile.rayon, b.w * 0.16), name: 'Jalon ' + (i + 1), g: 'tuiles', sub: i });
    const ib = grow(b, -b.w * 0.2, -b.h * 0.2);
    const im = loadImg(c, j.image);
    if (im) putImage(c, im, fitRect(ib, im.info, 'contain'), { name: 'Jalon image', g: 'tuiles', sub: i });
    else if (str(j.titre)) names.push(zt(c, ib, j.titre, { size: 18, min: 10, maxTotal: 2, font: 'texte', color: now ? c.P.accentTxt : c.P.fg, g: 'tuiles', sub: i, name: 'Jalon nom' }).it);
    else drawGlyph(c, grow(b, -b.w * 0.3, -b.h * 0.3), i, { g: 'tuiles', sub: i, color: now ? c.P.accent : undefined });
    const date = str(j.date) || (c.lang === 'en' ? '[TO PROVIDE: date]' : '[À FOURNIR : date]');
    zt(c, { x: b.x - 0.1, y: H * 0.57, w: b.w + 0.2, h: H * 0.05 }, date, { size: 16, min: 11, maxTotal: 1, font: 'texte', wt: now ? 'semi' : 'regular', color: now ? c.P.accentTxt : c.P.fg2, g: 'tuiles', sub: i, name: 'Date' });
  });
  sameSize(names);
  const tz = P(10, 12, 80, 8);
  if (tv(c, 'titre')) zt(c, tz, c.t.titre, { size: 28, min: 20, maxTotal: 1, g: 'titre', name: 'Titre' });
  c.groups = [G('titre', KW.titre), G('tuiles', /\b(?:jalons?|tuiles?|dates?|etapes?|milestones?)\b/, { multi: true })];
};
V['FRISE/generations'] = (c) => {
  let list = milestones(c).slice(0, 6);
  if (!list.length) list = [{}, {}, {}, {}, {}];
  const n = list.length;
  const tw = W * 0.17;
  const step = W * 0.1875;
  c.accentUsed = true;
  const names = [];
  list.forEach((j, i) => {
    const cx = W / 2 + (i - (n - 1) / 2) * step;
    const b = { x: cx - tw / 2, y: H * 0.348, w: tw, h: H * 0.302 };
    const now = i === n - 1;
    c.round({ x: b.x, y: b.y, w: b.w, h: b.h, fill: c.P.surface, radius: Math.min(VS.tuile.rayon, b.w * 0.14), name: 'Génération ' + (i + 1), g: 'tuiles', sub: i });
    names.push(zt(c, grow(b, -b.w * 0.1, -b.h * 0.2), str(j.titre) || c.f('_', 'nom'), { size: 28, min: 14, maxTotal: 2, color: now ? c.P.accentTxt : c.P.fg, g: 'tuiles', sub: i, name: 'Nom' }).it);
  });
  sameSize(names);
  c.groups = [G('tuiles', /\b(?:generations?|tuiles?|jalons?)\b/, { multi: false })];
};
V['FRISE/trois-jalons'] = (c) => {
  let list = milestones(c).slice(0, 3);
  while (list.length < 3) list.push({});
  const forms = ['carre', 'disque', 'carre'];
  list.forEach((j, i) => {
    const z = P(8 + i * 30, 28, 24, 44);
    productVisual(c, z, j.image, { g: 'tuiles', sub: i, halo: false, ombre: true, forme: forms[i], label: str(j.titre) || (c.lang === 'en' ? 'object of the milestone' : 'objet du jalon'), silBox: (b) => grow(b, -b.w * 0.12, -b.h * 0.12), haloSil: false });
    if (str(j.date)) zt(c, P(8 + i * 30, 77, 24, 5), j.date, { size: 16, min: 11, maxTotal: 1, font: 'texte', wt: 'regular', color: c.P.fg2, g: 'tuiles', sub: i, name: 'Date' });
  });
  c.groups = [G('tuiles', /\b(?:jalons?|objets?|images?)\b/, { multi: true })];
};
V['FRISE/courbe-et-saut'] = (c) => {
  const tz = P(20, 6.5, 60, 7);
  if (tv(c, 'titre')) zt(c, tz, c.t.titre, { size: 28, min: 20, maxTotal: 1, anchor: 'top', g: 'titre', name: 'Titre' });
  const n = clamp(milestones(c).length || 4, 3, 6);
  const pts = [];
  for (let i = 0; i < n; i++) pts.push([W * (0.17 + i * (0.6 / (n - 1))), H * (0.695 - i * 0.012)]);
  c.add({ k: 'path', pts: [[W * 0.1, H * 0.7]].concat(pts), stroke: c.P.other, strokeW: 1.5, name: 'Ligne', g: 'barres' });
  c.rect({ x: W * 0.1, y: H * 0.84, w: W * 0.8, h: 0.015, fill: mix(c.P.fg, c.P.bg, 0.7), name: 'Axe', g: 'titre' });
  pts.forEach((p, i) => c.ellipse({ x: p[0] - 0.09, y: p[1] - 0.09, w: 0.18, h: 0.18, fill: c.P.bg, line: c.P.other, lineW: 1.5, name: 'Jalon ' + (i + 1), g: 'barres' }));
  const last = pts[n - 1];
  const tile = { x: last[0] - W * 0.04, y: H * 0.22, w: W * 0.08, h: W * 0.08 };
  genImage(c, grow(tile, 0.35, 0.35), c.P.accent, alphaAround(0.55, { x: 0.35, y: 0.35, w: tile.w, h: tile.h }, tile.w * 0.2, 0.1, 0), 'Halo nouveauté', { g: 'chiffre', key: 'halosaut', ppi: 60 });
  c.round({ x: tile.x, y: tile.y, w: tile.w, h: tile.h, fill: mix(c.T.fondSombre, '000000', 0.4), line: c.P.accent, lineW: 1.5, radius: tile.w * 0.2, name: 'Nouveauté', g: 'chiffre' });
  if (tv(c, 'nom')) zt(c, grow(tile, -0.06, -0.06), c.t.nom, { size: 16, min: 9, maxTotal: 2, font: 'texte', color: 'FFFFFF', g: 'chiffre', name: 'Nom' });
  c.rect({ x: last[0] - 0.01, y: tile.y + tile.h + 0.08, w: 0.02, h: last[1] - 0.12 - (tile.y + tile.h + 0.08), fill: c.P.accent, name: 'Flèche', g: 'chiffre' });
  c.accentUsed = true;
  zt(c, { x: last[0] - 0.2 - 2.4, y: H * 0.38, w: 2.4, h: H * 0.12 }, tv(c, 'chiffre') || (c.lang === 'en' ? '[TO PROVIDE: gap]' : '[À FOURNIR : écart]'), { size: 48, min: 28, maxTotal: 1, noWrap: true, align: 'right', color: c.P.accentTxt, g: 'chiffre', name: 'Écart' });
  const per = arr(c.t.periodes);
  if (per[0]) c.line({ text: str(per[0]), x: W * 0.11, w: 1.4, base: H * 0.9, size: scalePt(16, 'texte'), wt: 'regular', color: c.P.fg2, align: 'left', font: 'texte', name: 'Période début', g: 'titre' });
  if (per[1]) c.line({ text: str(per[per.length - 1]), x: W * 0.84 - 1.4, w: 1.4, base: H * 0.9, size: scalePt(16, 'texte'), wt: 'regular', color: c.P.fg2, align: 'right', font: 'texte', name: 'Période fin', g: 'titre' });
  srcLine(c, P(6, 94, 88, 4));
  c.groups = [G('titre', /\b(?:titres?|axes?)\b/), G('barres', /\b(?:lignes?|jalons?|lines?)\b/), G('chiffre', /\b(?:nouveautes?|sauts?|fleches?|ecarts?|chiffres?)\b/)];
};
V['FRISE/objet-du-passe'] = (c) => {
  productVisual(c, P(35, 15, 30, 70), c.slide.image, { g: 'visuel', halo: false, silBox: (b) => grow(b, -b.w * 0.2, -b.h * 0.18), haloSil: false, label: c.lang === 'en' ? 'object or screen of the past' : 'objet ou écran d\'autrefois' });
  c.groups = [G('visuel', KW.visuel)];
};

// ---------------------------------------------------------------------------
// Aiguillage : slide.variante (nom exact des fiches). FIN, COLORIS et FRISE se posent sur n'importe
// quel archétype (archetype « FIN », « COLORIS » ou « FRISE » accepté aussi) ; les autres
// variantes appartiennent à leur archétype.
// ---------------------------------------------------------------------------
const FAMILLES_LIBRES = ['FIN', 'COLORIS', 'FRISE'];
// Variantes qui posent elles-mêmes leur photo à fond perdu : pas d'image de fond en plus.
const OWN_PHOTO = new Set(['A1/sur-image', 'A4/sur-image', 'A5/sur-photo', 'A7/sur-photo', 'A8/sur-contenu', 'A10/capture-nue', 'A12/macro-matiere',
  'A18/usage', 'A18/exemple-cartouche', 'A18/diptyque', 'A18/photo-titre', 'A21/gauche', 'A21/droite', 'A21/double', 'A21/sur-clair', 'A21/carte-portrait', 'FIN/signe-sur-photo']);
const VARIANTE_DEFAUT = { FIN: 'signe-seul', COLORIS: 'rangee-alignee', FRISE: 'rangee-datee' };
function resolveVariant(arch, variante) {
  const v = normKey(variante);
  if (!v && VARIANTE_DEFAUT[arch]) return { key: arch + '/' + VARIANTE_DEFAUT[arch], arch, fn: V[arch + '/' + VARIANTE_DEFAUT[arch]] };
  if (!v) return null;
  if (V[arch + '/' + v]) return { key: arch + '/' + v, arch, fn: V[arch + '/' + v] };
  for (const f of FAMILLES_LIBRES) if (V[f + '/' + v]) return { key: f + '/' + v, arch: f, fn: V[f + '/' + v] };
  return null;
}
function variantNames(arch) {
  return Object.keys(V).filter((k) => k.startsWith(arch + '/')).map((k) => k.split('/')[1]);
}


// Cibles d'un groupe : éléments entiers (it.g) ou plages de paragraphes d'une zone de texte.
function groupTargets(c, key) {
  const bySub = {};
  const all = [];
  const push = (sub, t) => {
    all.push(t);
    if (sub !== undefined) (bySub[sub] = bySub[sub] || []).push(t);
  };
  c.items.forEach((it, idx) => {
    if (it.g === key) {
      push(it.sub, { idx, pr: null });
    } else if (it.k === 'text' && it.g === undefined) {
      let start = -1;
      let cur;
      const flush = (end) => {
        if (start >= 0) push(cur, { idx, pr: [start, end] });
        start = -1;
      };
      it.paras.forEach((p, pi) => {
        if (p.g === key) {
          if (start >= 0 && p.sub !== cur) flush(pi - 1);
          if (start < 0) {
            start = pi;
            cur = p.sub;
          }
        } else {
          flush(pi - 1);
        }
      });
      flush(it.paras.length - 1);
    }
  });
  const subs = Object.keys(bySub).map(Number).sort((a, b) => a - b);
  return { all, bySub, subs };
}
function ordinalsIn(seg) {
  const found = [];
  ORD.forEach(([rx, v]) => {
    rx.lastIndex = 0;
    let m;
    while ((m = rx.exec(seg))) found.push({ pos: m.index, v });
  });
  return found.sort((a, b) => a.pos - b.pos).map((x) => x.v);
}
function isPluralWord(word, seg, pos) {
  const w = String(word || '');
  if (/s$/.test(w) && !['prix', 'mois', 'fois', 'cas'].includes(w)) return true;
  // « les prix », « les deux offres », « the three lines » : un déterminant pluriel juste avant.
  const before = seg.slice(Math.max(0, (pos || 0) - 24), pos || 0);
  return /\b(?:les|des|ces|nos|vos|the|these|those|all|both)\b(?:\s+[a-z]+)?\s+$/.test(before) || BRX.plural.test(seg);
}
function planAnimations(c) {
  const raw = arr(c.slide.build).map((b) => {
    if (typeof b === 'string') return b;
    if (b && typeof b === 'object') return [b.element, b.quoi, b.texte, b.text].filter(Boolean).join(' ');
    return '';
  }).filter((s) => s.trim());
  if (!raw.length) return [];
  const defs = [];
  (c.groups || (c.variante && VGROUPS[c.renderArch]) || GROUPS[c.renderArch] || []).forEach((d, i) => {
    const t = groupTargets(c, d.key);
    if (!t.all.length) return;
    const multi = d.multi === true || (d.multi === 'auto' && t.subs.length > 1);
    defs.push(Object.assign({}, d, { order: i, t, multi, done: new Set(), whole: false, isStatic: false, lastStep: -1 }));
  });
  if (!defs.length) return [];
  const byPrio = defs.slice().sort((a, b) => (a.prio || 5) - (b.prio || 5) || a.order - b.order);
  const isDone = (d) => d.whole || (d.t.subs.length > 0 && d.t.subs.every((k) => d.done.has(k)));
  const restOf = (d) => {
    if (d.whole) return [];
    if (!d.t.subs.length) return d.t.all;
    const out = [];
    d.t.subs.filter((k) => !d.done.has(k)).forEach((k) => d.t.bySub[k].forEach((t) => out.push(t)));
    // Éléments sans rang (rares) : avec le reste.
    d.t.all.filter((t) => !d.t.subs.some((k) => d.t.bySub[k].includes(t))).forEach((t) => out.push(t));
    return out;
  };
  const steps = [];
  for (const entry of raw) {
    const n = normText(entry).replace(/«[^»]*»|“[^”]*”|"[^"]*"/g, ' ');
    if (BRX.none.test(n)) return [];
    const entryTogether = BRX.together.test(n);
    let lastDef = null;
    n.split(BRX.seq).forEach((seg) => {
      const isStatic = BRX.stat.test(seg);
      const keep = BRX.keep.test(seg) && !BRX.appear.test(seg);
      const after = BRX.after.test(seg);
      const together = entryTogether || BRX.together.test(seg);
      let s = seg;
      const mentions = [];
      byPrio.forEach((d) => {
        const tryRx = (rx, sub) => {
          const m = rx.exec(s);
          if (!m) return false;
          mentions.push({ d, pos: m.index, word: m[0], sub });
          s = s.slice(0, m.index) + ' '.repeat(m[0].length) + s.slice(m.index + m[0].length);
          return true;
        };
        if (d.subKw && tryRx(d.subKw, true)) return;
        tryRx(d.kw, false);
      });
      mentions.sort((a, b) => a.pos - b.pos);
      const ords = ordinalsIn(seg);
      if (!mentions.length && ords.length && lastDef) mentions.push({ d: lastDef, pos: 0, word: '', sub: true });
      if (!mentions.length && (isStatic || BRX.appear.test(seg))) {
        const d = defs.find((x) => !isDone(x));
        if (d) mentions.push({ d, pos: 0, word: '', implicit: true });
      }
      if (!mentions.length) return;
      if (keep && !isStatic) {
        lastDef = mentions[mentions.length - 1].d;
        return;
      }
      const units = [];
      mentions.forEach((mn) => {
        const d = mn.d;
        lastDef = d;
        if (isDone(d)) return;
        const subLevel = d.t.subs.length > 0 && (d.multi || mn.sub || (ords.length > 0 && d.t.subs.length > 1));
        if (subLevel) {
          const free = d.t.subs.filter((k) => !d.done.has(k));
          let chosen;
          if (ords.length) chosen = uniq(ords.map((o) => (o === 'last' ? d.t.subs[d.t.subs.length - 1] : d.t.subs[o])).filter((k) => k !== undefined && !d.done.has(k)).map(String)).map(Number);
          else if (mn.implicit || isPluralWord(mn.word, seg, mn.pos)) chosen = free;
          else chosen = free.slice(0, 1);
          if (!chosen.length) return;
          chosen.forEach((k) => d.done.add(k));
          if (together || isStatic) units.push({ d, targets: [].concat.apply([], chosen.map((k) => d.t.bySub[k])), label: [d.key, chosen], multi: false });
          else chosen.forEach((k) => units.push({ d, targets: d.t.bySub[k], label: [d.key, [k]], multi: true }));
        } else {
          const targets = restOf(d);
          d.whole = true;
          if (targets.length) units.push({ d, targets, label: [d.key, null], multi: false });
        }
      });
      if (!units.length) return;
      if (isStatic) {
        units.forEach((u) => { u.d.isStatic = true; });
        return;
      }
      units.forEach((u, j) => {
        let trigger;
        if (j === 0) trigger = after && steps.length ? 'after' : 'click';
        else trigger = u.multi && !together ? 'click' : 'with';
        steps.push({ trigger, targets: u.targets.slice(), labels: [u.label] });
        u.d.lastStep = steps.length - 1;
      });
    });
  }
  if (!steps.length) return [];
  // Groupes jamais nommés : avec le groupe animé qui les précède dans l'ordre de lecture.
  defs.forEach((d) => {
    if (d.isStatic) return;
    const rest = restOf(d);
    if (!rest.length) return;
    const prev = defs.filter((x) => x.order <= d.order && x.lastStep >= 0).pop();
    if (!prev) return;
    steps[prev.lastStep].targets.push.apply(steps[prev.lastStep].targets, rest);
    steps[prev.lastStep].labels.push([d.key, null]);
    d.whole = true;
  });
  steps[0].trigger = 'click';
  return steps;
}
function describeSteps(steps, L) {
  const parts = [];
  let k = 0;
  steps.forEach((s) => {
    const names = s.labels.map(([key, subs]) => {
      const nm = L.parts[key] || key;
      return subs ? subs.map((x) => nm + ' ' + (x + 1)).join(' + ') : nm;
    }).join(' + ');
    if (s.trigger === 'click') {
      k += 1;
      parts.push(k + ') ' + names);
    } else {
      parts[parts.length - 1] += (s.trigger === 'after' ? ' → ' : ' + ') + names;
    }
  });
  return parts.join(' · ');
}

// ---------------------------------------------------------------------------
// Notes du présentateur : le texte à dire, puis apparitions, minutage, source, ce qui
// reste à valider et à fournir. Aucun terme de travail (étape, archétype).
// ---------------------------------------------------------------------------
function noteSegments(slide, env) {
  const def = slide.intervenant || (env.intervenants[0] && env.intervenants[0].id) || '';
  const n = slide.notes;
  if (n === undefined || n === null || n === '') return [];
  if (typeof n === 'string') return [{ intervenant: def, texte: n }];
  return arr(n).map((s) => (typeof s === 'string' ? { intervenant: def, texte: s } : { intervenant: s.intervenant || def, texte: str(s.texte || s.text), type: s.type }))
    .filter((s) => s.texte.trim() !== '');
}
// En-tête d'une prise de parole : NOM · fonction. Une fonction inconnue (vide ou écrite en
// marqueur) est signalée une seule fois, à la première prise de parole de la personne.
function speakerHead(id, env, L) {
  const who = env.people[id];
  if (!who) return String(id || '').toUpperCase();
  const name = String(stripValider(who.nom || id)).toUpperCase();
  const role = str(who.role).trim();
  const first = !env.introduced.has(id);
  env.introduced.add(id);
  if (role && !hasFournir(role)) return name + ' · ' + stripValider(role);
  if (first) return name + ' · ' + (hasFournir(role) ? role : (env.lang === 'en' ? '[TO PROVIDE: ' + L.role + ']' : '[À FOURNIR : ' + L.role + ']'));
  return name;
}
function provideItems(slide, c, env, withBrief) {
  const L = c.L;
  const out = [];
  if (c.fournirs.length) out.push(c.fournirs.join(', ') + '.');
  arr(slide.a_fournir).forEach((x) => { if (str(x).trim()) out.push(str(x).trim()); });
  if (c.arch === 'AF' && c.t.attendu) out.push(str(c.t.attendu).trim());
  c.missing.forEach((m) => {
    if (m.kind === 'logo' && !m.chemin) return;
    out.push((L.kind[m.kind] || L.kind.interface) + (m.attendu ? ' ' + L.q(m.attendu) : '') + (m.chemin ? ' (' + m.chemin + ')' : '') + (withBrief && m.brief ? (c.lang === 'en' ? ' — ' : ' : ') + m.brief : '') + '.');
  });
  return uniq(out);
}
function buildNotes(slide, c, env, start) {
  const L = c.L;
  const out = [];
  const segs = noteSegments(slide, env);
  if (!segs.length) {
    out.push(L.noNotes);
    c.warn('Notes vides : marqueur ajouté dans les notes.');
  }
  segs.forEach((s) => {
    const changed = env.lastSpeaker && s.intervenant && s.intervenant !== env.lastSpeaker;
    const head = (changed ? '→ ' : '') + speakerHead(s.intervenant, env, L) + (s.type === 'relais' ? ' (' + L.relay + ')' : '');
    if (s.intervenant) out.push(head);
    out.push(s.texte.trim());
    out.push('');
    if (s.intervenant) env.lastSpeaker = s.intervenant;
  });
  const build = arr(slide.build).map((b) => (typeof b === 'string' ? b : str(b && (b.texte || b.text)))).filter((b) => b.trim());
  if (build.length) {
    out.push(L.build);
    build.forEach((b, i) => out.push((i + 1) + '. ' + b));
    out.push('');
  }
  const d = Number(slide.duree_s) || 0;
  out.push(L.timing + ' ' + fmtTime(start) + ' → ' + fmtTime(start + d) + ' (' + d + ' s)');
  if (c.sourceText) {
    const where = env.sourceMode === 'renvoi' ? L.sourceRenvoi + c.sourceRef + ', ' + L.sourceFinal
      : c.sourceOnSlide ? L.sourceShown : env.sourceMode === 'carton_final' ? L.sourceFinal : L.sourceHidden;
    out.push(L.source + ' (' + where + ')' + L.sep + c.sourceText);
  }
  if (c.proposals.length) out.push(L.toValidate + L.sep + c.proposals.map((p) => L.q(p)).join(c.lang === 'en' ? '; ' : ' ; '));
  const prov = provideItems(slide, c, env);
  if (prov.length) out.push(L.toProvide + L.sep + prov.join(' '));
  return out.join('\n').replace(/\n{3,}/g, '\n\n').trim();
}

// ---------------------------------------------------------------------------
// Rendu .pptx. Retourne, pour chaque élément, les identifiants des formes créées
// (pptxgenjs numérote les objets d'une slide à partir de 2, dans l'ordre d'ajout).
// Interligne exact (a:spcPts), suivi en points (spc), demi-gras par la face SemiBold.
// ---------------------------------------------------------------------------
function shadowPt() {
  const O = STYLE.schema.ombre;
  return { type: 'outer', blur: Math.round(O.flou * 72 * 10) / 10, offset: Math.round(O.decalage * 72 * 10) / 10, angle: 90, color: '000000', opacity: O.opacite };
}
function pathBox(it) {
  const xs = it.pts.map((q) => q[0]);
  const ys = it.pts.map((q) => q[1]);
  const x = Math.min.apply(null, xs);
  const y = Math.min.apply(null, ys);
  return { x, y, w: Math.max(0.01, Math.max.apply(null, xs) - x), h: Math.max(0.01, Math.max.apply(null, ys) - y) };
}
function pptxRender(pres, slideObj, c, env) {
  const T = env.T;
  const langTag = env.lang === 'en' ? 'en-US' : 'fr-FR';
  const map = [];
  let n = 0;
  const reg = (idx, type, names) => {
    map[idx] = { ids: names.map((nm, k) => n + 2 + k), names, type };
    n += names.length;
  };
  c.items.forEach((it, idx) => {
    if (it.k === 'rect' || it.k === 'round' || it.k === 'ellipse') {
      const shape = it.k === 'ellipse' ? pres.ShapeType.ellipse : it.k === 'round' ? pres.ShapeType.roundRect : pres.ShapeType.rect;
      const o = { x: round2(it.x), y: round2(it.y), w: round2(Math.max(0.01, it.w)), h: round2(Math.max(0.01, it.h)), objectName: it.name };
      if (it.fill) o.fill = it.transparency ? { color: it.fill, transparency: it.transparency } : { color: it.fill };
      if (it.line) o.line = { color: it.line, width: it.lineW || 1, dashType: it.dash || 'solid' };
      if (it.k === 'round') o.rectRadius = round2(Math.max(0, Math.min(it.radius || 0.1, it.w / 2, it.h / 2)));
      if (it.shadow) o.shadow = shadowPt();
      if (it.rot) o.rotate = Math.round(it.rot * 100) / 100;
      slideObj.addShape(shape, o);
      reg(idx, 'sp', [it.name]);
    } else if (it.k === 'path') {
      // Tracé libre (courbe, arc, triangle) : géométrie personnalisée, points relatifs à sa boîte.
      const bb = pathBox(it);
      const pts = it.pts.map((q) => ({ x: round2(q[0] - bb.x), y: round2(q[1] - bb.y) }));
      if (it.closed) pts.push({ close: true });
      const o = { x: round2(bb.x), y: round2(bb.y), w: round2(bb.w), h: round2(bb.h), points: pts, objectName: it.name };
      if (it.fill) o.fill = it.transparency ? { color: it.fill, transparency: it.transparency } : { color: it.fill };
      if (it.stroke) o.line = { color: it.stroke, width: it.strokeW || 1, dashType: it.dash || 'solid' };
      slideObj.addShape(pres.ShapeType.custGeom, o);
      reg(idx, 'sp', [it.name]);
    } else if (it.k === 'check') {
      const s = it.d;
      const a = { x: it.cx - 0.24 * s, y: it.cy + 0.0 * s };
      const b = { x: it.cx - 0.06 * s, y: it.cy + 0.18 * s };
      const e = { x: it.cx + 0.26 * s, y: it.cy - 0.2 * s };
      const w = it.strokeW || Math.max(1.5, s * 7);
      slideObj.addShape(pres.ShapeType.line, { x: round2(a.x), y: round2(a.y), w: round2(b.x - a.x), h: round2(b.y - a.y), line: { color: it.color, width: w }, objectName: it.name + ' a' });
      slideObj.addShape(pres.ShapeType.line, { x: round2(b.x), y: round2(e.y), w: round2(e.x - b.x), h: round2(b.y - e.y), flipV: true, line: { color: it.color, width: w }, objectName: it.name + ' b' });
      reg(idx, 'sp', [it.name + ' a', it.name + ' b']);
    } else if (it.k === 'rule') {
      // Filet pointillé d'un [À FOURNIR] en grand corps : épaisseur fixe, opacité du marqueur.
      slideObj.addShape(pres.ShapeType.line, { x: round2(it.x), y: round2(it.y + it.h / 2), w: round2(it.w), h: 0, line: { color: it.color, width: it.pt, dashType: 'sysDot', transparency: Math.round((1 - STYLE.marqueur.opacite) * 100) }, objectName: it.name });
      reg(idx, 'sp', [it.name]);
    } else if (it.k === 'image') {
      const src = it.gen ? { data: it.info.mime + ';base64,' + it.info.buf.toString('base64') } : { path: it.abs };
      if (it.full) {
        // Image recadrée : posée à sa taille entière, seule la partie visible est gardée (srcRect).
        slideObj.addImage(Object.assign({}, src, { x: round2(it.x), y: round2(it.y), w: round2(it.full.w), h: round2(it.full.h), sizing: { type: 'crop', x: round2(it.x - it.full.x), y: round2(it.y - it.full.y), w: round2(it.w), h: round2(it.h) }, altText: it.alt, objectName: it.name }));
      } else if (it.gen || it.rot) {
        slideObj.addImage(Object.assign({}, src, { x: round2(it.x), y: round2(it.y), w: round2(it.w), h: round2(it.h), rotate: it.rot || undefined, altText: it.alt || 'décor', objectName: it.name }));
      } else if (it.mode === 'cover') {
        const iw = it.info.w;
        const ih = it.info.h;
        slideObj.addImage({ path: it.abs, x: round2(it.x), y: round2(it.y), w: round2(it.w), h: round2(it.w * ih / iw), sizing: { type: 'cover', w: round2(it.w), h: round2(it.h) }, altText: it.alt, objectName: it.name });
      } else {
        // Rectangle déjà calculé à la composition (image entière, sans déformation).
        slideObj.addImage({ path: it.abs, x: round2(it.x), y: round2(it.y), w: round2(it.w), h: round2(it.h), altText: it.alt, objectName: it.name });
      }
      reg(idx, 'pic', [it.name]);
      if (it.radius) map[idx].radius = it.radius;
    } else if (it.k === 'text') {
      const runsOut = [];
      it.paras.forEach((p, pi) => {
        const ps = Math.round(paraSize(it, p, it.fitted) * 2) / 2;
        const F = faceOf(T, roleOf(it, p), paraWeight(it, p));
        const track = paraTrack(it, p, ps);
        const lnPt = Math.round(paraLineH(it, p, ps) * 72 * 100) / 100;
        const after = pi < it.paras.length - 1 ? Math.round(paraGap(it, p, ps) * 72 * 100) / 100 : 0;
        const runs = p.runs.length ? p.runs : [{ t: '' }];
        runs.forEach((r, ri) => {
          const o = {
            fontFace: xmlFace(F.face), fontSize: ps, bold: F.bold,
            color: r.marker ? markerInk(c, r.color || (r.accent ? c.P.accentTxt : (p.color || it.color))) : (r.color || (r.accent ? c.P.accentTxt : (p.color || it.color))),
            align: p.align || it.align, lineSpacing: lnPt, paraSpaceAfter: after, lang: langTag
          };
          if (track) o.charSpacing = Math.round(track * ps * 100) / 100;
          // [À FOURNIR] estompé : <a:alpha> dans le srgbClr du run (transparence 60 → alpha 40 000).
          // Ce remplissage porte un alpha : le dégradé du chiffre héros (post-traitement) le laisse.
          if (r.marker) o.transparency = Math.round((1 - STYLE.marqueur.texte) * 100);
          if (r.marker && r.ul !== false) o.underline = { style: STYLE.marqueur.trait, color: c.P.accentTxt };
          if (ri === runs.length - 1 && pi < it.paras.length - 1) o.breakLine = true;
          runsOut.push({ text: r.t, options: o });
        });
      });
      const F0 = faceOf(T, it.font, it.wt);
      slideObj.addText(runsOut, {
        x: round2(it.x), y: round2(it.y), w: round2(it.w), h: round2(it.h), margin: 0, valign: it.valign, align: it.align,
        isTextBox: true, objectName: it.name, wrap: !it.noWrap, fontFace: xmlFace(F0.face), fontSize: it.fitted, color: it.color, lang: langTag
      });
      reg(idx, 'sp', [it.name]);
      map[idx].text = true;
      map[idx].nparas = it.paras.length;
    }
  });
  return map;
}

// ---------------------------------------------------------------------------
// Rendu HTML (aperçu) : 1 pouce = 10 cqw, 1 pt = 1/7,2 cqw. Mêmes positions, corps, interlignes
// (line-height = interligne / corps), suivis et graisses que le .pptx.
// ---------------------------------------------------------------------------
function cq(inches) {
  return round2(inches * 10) + 'cqw';
}
function cqPt(pt) {
  return round2(pt / 7.2) + 'cqw';
}
function htmlItems(c, env) {
  const T = env.T;
  const out = [];
  c.items.forEach((it) => {
    const pos = 'left:' + cq(it.x !== undefined ? it.x : 0) + ';top:' + cq(it.y !== undefined ? it.y : 0) + ';width:' + cq(it.w || 0) + ';height:' + cq(it.h || 0) + ';';
    if (it.k === 'rect' || it.k === 'round' || it.k === 'ellipse') {
      let st = pos;
      if (it.fill) {
        const [r, g, b] = rgbOf(it.fill);
        st += 'background:rgba(' + r + ',' + g + ',' + b + ',' + (it.transparency ? round2(1 - it.transparency / 100) : 1) + ');';
      }
      if (it.line) st += 'border:' + cqPt(it.lineW || 1) + ' ' + (it.dash === 'dash' ? 'dashed' : 'solid') + ' #' + it.line + ';box-sizing:border-box;';
      if (it.k === 'ellipse') st += 'border-radius:50%;';
      if (it.k === 'round') st += 'border-radius:' + cq(Math.max(0, Math.min(it.radius || 0.1, it.w / 2, it.h / 2))) + ';';
      if (it.grad2 && it.fill) st += 'background:linear-gradient(' + (90 + (it.grad2.ang === undefined ? 90 : it.grad2.ang)) + 'deg,#' + it.grad2.from + ',#' + it.grad2.to + ');';
      if (it.rot) st += 'transform:rotate(' + it.rot + 'deg);';
      if (it.shadow) {
        const O = STYLE.schema.ombre;
        st += 'box-shadow:0 ' + cq(O.decalage) + ' ' + cq(O.flou) + ' rgba(0,0,0,' + O.opacite + ');';
      }
      out.push('<div class="sh" title="' + escHtml(it.name || '') + '" style="' + st + '"></div>');
    } else if (it.k === 'path') {
      const bb = pathBox(it);
      const u = (v) => round2(v * 1000);
      const d = it.pts.map((q, k) => (k ? 'L' : 'M') + u(q[0] - bb.x) + ' ' + u(q[1] - bb.y)).join(' ') + (it.closed ? ' Z' : '');
      const stroke = it.stroke ? ' stroke="#' + it.stroke + '" stroke-width="' + round2((it.strokeW || 1) / 72 * 1000) + '" stroke-linecap="' + (it.cap === 'rnd' ? 'round' : 'butt') + '" stroke-linejoin="' + (it.join === 'round' ? 'round' : 'miter') + '"' + (it.dash === 'sysDot' ? ' stroke-dasharray="' + round2((it.strokeW || 1) / 72 * 1000) + ' ' + round2((it.strokeW || 1) / 72 * 2000) + '"' : '') : '';
      const fill = it.fill ? '#' + it.fill + '" fill-opacity="' + (it.transparency ? round2(1 - it.transparency / 100) : 1) : 'none';
      out.push('<svg class="sh" style="left:' + cq(bb.x) + ';top:' + cq(bb.y) + ';width:' + cq(bb.w) + ';height:' + cq(bb.h) + ';overflow:visible" viewBox="0 0 ' + u(bb.w) + ' ' + u(bb.h) + '" preserveAspectRatio="none"><path d="' + d + '" fill="' + fill + '"' + stroke + '/></svg>');
    } else if (it.k === 'check') {
      const s = it.d;
      const box = 'left:' + cq(it.cx - s / 2) + ';top:' + cq(it.cy - s / 2) + ';width:' + cq(s) + ';height:' + cq(s) + ';';
      const pts = [[0.26, 0.5], [0.44, 0.68], [0.76, 0.3]].map((p) => (p[0] * 100) + ',' + (p[1] * 100)).join(' ');
      const sw = round2((it.strokeW || Math.max(1.5, s * 7)) / 72 / s * 100);
      out.push('<svg class="sh" style="' + box + '" viewBox="0 0 100 100"><polyline points="' + pts + '" fill="none" stroke="#' + it.color + '" stroke-width="' + sw + '" stroke-linecap="square"/></svg>');
    } else if (it.k === 'rule') {
      const [ur, ug, ub] = rgbOf(it.color);
      // Position calculée pour la police que l'aperçu affiche (xh, wh), pas pour celle du .pptx.
      const rx = it.xh !== undefined ? it.xh : it.x;
      const rw = it.wh !== undefined ? it.wh : it.w;
      out.push('<div class="sh" title="' + escHtml(it.name || '') + '" style="left:' + cq(rx) + ';top:' + cq(it.y) + ';width:' + cq(rw) + ';height:0;border-top:max(1px,' + cqPt(it.pt) + ') dotted rgba(' + ur + ',' + ug + ',' + ub + ',' + STYLE.marqueur.opacite + ');"></div>');
    } else if (it.k === 'image') {
      const data = 'data:' + it.info.mime + ';base64,' + it.info.buf.toString('base64');
      const fx = (it.gray ? 'filter:grayscale(1);' : '') + (it.rot ? 'transform:rotate(' + it.rot + 'deg);' : '');
      if (it.full) {
        // Recadrage : une fenêtre (la partie visible) et l'image entière dedans, à sa place.
        out.push('<div class="sh" style="' + pos + 'overflow:hidden;' + (it.radius ? 'border-radius:' + cq(it.radius) + ';' : '') + '"><img alt="' + escHtml(it.alt || '') + '" src="' + data + '" style="position:absolute;left:' + cq(it.full.x - it.x) + ';top:' + cq(it.full.y - it.y) + ';width:' + cq(it.full.w) + ';height:' + cq(it.full.h) + ';max-width:none;' + fx + '"></div>');
      } else out.push('<img class="sh" alt="' + escHtml(it.alt || '') + '" src="' + data + '" style="' + pos + 'object-fit:' + (it.mode === 'cover' ? 'cover' : 'fill') + ';' + (it.radius ? 'border-radius:' + cq(it.radius) + ';' : '') + fx + '">');
    } else if (it.k === 'text') {
      const jc = it.valign === 'top' ? 'flex-start' : it.valign === 'bottom' ? 'flex-end' : 'center';
      let inner = '';
      it.paras.forEach((p, pi) => {
        const ps = Math.round(paraSize(it, p, it.fitted) * 2) / 2;
        const role = roleOf(it, p);
        const F = faceOf(T, role, paraWeight(it, p));
        const fam = role === 'titre' ? T.cssTitre : T.cssTexte;
        const track = paraTrack(it, p, ps);
        const lineH = round2(paraLineH(it, p, ps) * 72 / ps);
        const after = pi < it.paras.length - 1 ? cq(paraGap(it, p, ps)) : '0';
        const st = 'font-size:' + cqPt(ps) + ';line-height:' + lineH + ';font-weight:' + F.css + ';font-family:' + escHtml(fam) +
          ';letter-spacing:' + (track ? track + 'em' : 'normal') +
          ';color:#' + (p.color || it.color) + ';text-align:' + (p.align || it.align) + ';margin:0 0 ' + after + ' 0;';
        const runs = p.runs.map((r) => {
          const t = escHtml(r.t) || '&#8203;';
          let s = '';
          if (r.marker) {
            // Estompé comme dans le .pptx : la couleur du texte remplacé (sauf l'accent), à l'opacité du marqueur. En
            // rgba plutôt qu'en opacity, pour que le pointillé garde la sienne, comme dans le .pptx.
            const [mr, mg, mb] = rgbOf(markerInk(c, r.color || (r.accent ? c.P.accentTxt : (p.color || it.color))));
            s += 'color:rgba(' + mr + ',' + mg + ',' + mb + ',' + STYLE.marqueur.texte + ');';
          } else if (r.color) s += 'color:#' + r.color + ';';
          else if (r.accent) s += 'color:#' + c.P.accentTxt + ';';
          // Lueur autour du trait seul (comme <a:glow> dans le .pptx) : un text-shadow remplirait les lettres.
          if (it.outline && !r.marker) s += '-webkit-text-stroke:' + cqPt(it.outline.pt) + ' #' + it.outline.color + ';color:transparent;-webkit-text-fill-color:transparent;filter:drop-shadow(0 0 ' + cqPt(it.outline.glow) + ' rgba(' + rgbOf(it.outline.color).join(',') + ',' + Math.min(1, it.outline.glowA * 1.6) + '));';
          if (r.grad && it.grad && !r.marker) s +='background:linear-gradient(90deg,#' + c.P.accent + ',#' + c.P.accent2 + ');-webkit-background-clip:text;background-clip:text;-webkit-text-fill-color:transparent;color:transparent;';
          if (r.marker && r.ul !== false) {
            const [ur, ug, ub] = rgbOf(c.P.accentTxt);
            s += 'text-decoration:underline dotted rgba(' + ur + ',' + ug + ',' + ub + ',' + STYLE.marqueur.opacite + ');text-decoration-thickness:max(2px,.05em);text-underline-offset:.12em;';
          }
          return s ? '<span' + (r.marker ? ' class="mk"' : '') + ' style="' + s + '">' + t + '</span>' : t;
        }).join('');
        inner += '<p style="' + st + (it.noWrap ? 'white-space:nowrap;' : '') + '">' + runs + '</p>';
      });
      out.push('<div class="tx" data-name="' + escHtml(it.name) + '" style="' + pos + 'justify-content:' + jc + ';"><div class="in">' + inner + '</div></div>');
    }
  });
  return out.join('\n');
}

function previewHtml(deck, composed, env, totals) {
  const meta = deck.meta || {};
  const L = LABELS[env.lang] || LABELS.fr;
  const cards = composed.map((x, i) => {
    const s = x.slide;
    const d = Number(s.duree_s) || 0;
    const head = (i + 1) + (s.bloc ? ' · ' + escHtml(s.bloc) : '') + ' · ' + fmtTime(x.start) + ' → ' + fmtTime(x.start + d) + ' <span class="id">' + escHtml(s.id || '') + '</span>';
    const warn = x.c.warnings.length ? '<ul class="warn">' + x.c.warnings.map((w) => '<li>' + escHtml(w) + '</li>').join('') + '</ul>' : '';
    const anim = x.steps && x.steps.length ? '<p class="anim">' + escHtml((env.lang === 'en' ? 'Builds in the .pptx: ' : 'Apparitions du .pptx : ') + describeSteps(x.steps, L)) + '</p>' : '';
    return '<section class="card" id="slide-' + (i + 1) + '">' +
      '<h2>' + head + '</h2>' +
      '<div class="slide" data-index="' + (i + 1) + '" style="background:#' + x.c.P.bg + '">' + htmlItems(x.c, env) + '</div>' +
      warn + anim + '<pre class="notes">' + escHtml(x.notes) + '</pre></section>';
  }).join('\n');
  const pubDesc = meta.public && typeof meta.public === 'object' ? (meta.public.description || meta.public.type) : meta.public;
  const target = Number(meta.duree_min) || 0;
  const info = [
    meta.format ? 'Format : ' + escHtml(meta.format) : '',
    pubDesc ? 'Public : ' + escHtml(pubDesc) + ' (' + escHtml(env.pub.cle) + ')' : '',
    meta.registre ? 'Registre : ' + escHtml(meta.registre) : '',
    'Durée : ' + fmtTime(totals.duree) + (target ? ' pour ' + target + ' min visées' : ''),
    composed.length + ' slides 16:9'
  ].filter(Boolean).join(' · ');
  return '<!doctype html>\n<html lang="' + (env.lang === 'en' ? 'en' : 'fr') + '">\n<head>\n<meta charset="utf-8">\n<meta name="viewport" content="width=device-width, initial-scale=1">\n' +
    '<title>' + escHtml(meta.titre || 'Aperçu') + '</title>\n<style>\n' +
    ':root{--page:#ECEDEF;--ink:#1D1F22;--muted:#5F6670;--card:#FFFFFF;--warn:#8A4B00;--warnbg:#FFF4E0}\n' +
    '@media (prefers-color-scheme: dark){:root{--page:#16181B;--ink:#E9EBEE;--muted:#A3A9B1;--card:#212429;--warn:#FFC266;--warnbg:#3A2A10}}\n' +
    '*{box-sizing:border-box}html,body{margin:0}body{background:var(--page);color:var(--ink);font:15px/1.5 Arial,"Segoe UI",Roboto,sans-serif;padding:24px 16px 64px}\n' +
    'header{max-width:1100px;margin:0 auto 20px}header h1{font-size:22px;margin:0 0 4px}header p{margin:0;color:var(--muted)}\n' +
    '.card{max-width:1100px;margin:0 auto 28px;background:var(--card);border-radius:10px;padding:14px;box-shadow:0 1px 3px rgba(0,0,0,.08)}\n' +
    '.card h2{font-size:13px;font-weight:600;color:var(--muted);margin:0 0 10px;letter-spacing:.02em}.card h2 .id{font-weight:400;opacity:.7;margin-left:6px}\n' +
    '.slide{position:relative;width:100%;aspect-ratio:16/9;overflow:hidden;container-type:inline-size;border-radius:4px}\n' +
    '.slide .sh,.slide .tx{position:absolute;margin:0}\n.slide .tx{display:flex;flex-direction:column;overflow:visible}\n.slide .tx .in{width:100%}\n' +
    '.slide p{overflow-wrap:normal;word-break:normal;hyphens:none;font-kerning:normal}\n' +
    '.notes{white-space:pre-wrap;font:13px/1.55 ui-monospace,Menlo,Consolas,monospace;margin:12px 0 0;padding:12px;background:var(--page);border-radius:6px;color:var(--ink)}\n' +
    '.warn{margin:10px 0 0;padding:8px 12px 8px 28px;background:var(--warnbg);color:var(--warn);border-radius:6px;font-size:13px}\n' +
    '.anim{margin:10px 0 0;font-size:13px;color:var(--muted)}\n' +
    'body.qa .tx.over{outline:2px solid #FF2D2D;outline-offset:1px}\n#qa-banner{display:none;position:sticky;top:0;z-index:5;max-width:1100px;margin:0 auto 16px;padding:8px 12px;border-radius:6px;background:#FF2D2D;color:#fff;font-weight:600}\nbody.qa #qa-banner{display:block}\n' +
    '@media print{body{padding:0;background:#fff}.card{box-shadow:none;page-break-inside:avoid}}\n' +
    '</style>\n</head>\n<body>\n<div id="qa-banner"></div>\n<header><h1>' + escHtml(meta.titre || 'Aperçu') + '</h1><p>' + info + '</p></header>\n' +
    cards + '\n<script>\n' +
    '(function(){\n' +
    '  function overflows(){var out=[];document.querySelectorAll(".slide").forEach(function(sl){sl.querySelectorAll(".tx").forEach(function(b){var i=b.firstElementChild;var bh=b.clientHeight,bw=b.clientWidth;var over=i.offsetHeight>bh+1||i.scrollWidth>bw+1;b.classList.toggle("over",over);if(over)out.push({slide:+sl.dataset.index,element:b.dataset.name,hauteur:i.offsetHeight,place:bh,largeur:i.scrollWidth,placeLargeur:bw});});});return out;}\n' +
    '  window.__deckQA=overflows;\n' +
    '  function run(){var o=overflows();if(location.hash.indexOf("qa")>=0){document.body.classList.add("qa");var bn=document.getElementById("qa-banner");bn.style.background=o.length?"#D92D20":"#1F7A4D";bn.textContent=o.length?o.length+" texte(s) débordent : slides "+o.map(function(x){return x.slide}).join(", "):"Aucun débordement détecté.";}}\n' +
    '  if(document.fonts&&document.fonts.ready){document.fonts.ready.then(run);}else{window.addEventListener("load",run);}\n' +
    '  window.addEventListener("hashchange",run);window.addEventListener("resize",run);\n' +
    '})();\n</script>\n</body>\n</html>\n';
}

// ---------------------------------------------------------------------------
// Post-traitement du paquet : couleurs du thème, notes en paragraphes, placeholders groupés,
// dégradé du chiffre héros, transition en fondu et animations d'entrée de chaque slide.
// Seuls les fichiers des slides, du thème et des notes sont réécrits ; presentation.xml
// n'est pas touché.
// ---------------------------------------------------------------------------
const EMU = 914400;
function slideTokens(xml) {
  const toks = [];
  const re = /<p:(sp|pic|cxnSp|graphicFrame|grpSp)\b[^>]*>[\s\S]*?<\/p:\1>/g;
  let m;
  while ((m = re.exec(xml))) {
    const idm = /<p:cNvPr id="(\d+)" name="([^"]*)"/.exec(m[0]);
    toks.push({ start: m.index, end: m.index + m[0].length, tag: m[1], id: idm ? Number(idm[1]) : -1, name: idm ? unescXml(idm[2]) : '', xml: m[0] });
  }
  return toks;
}
function effectXml(t, nodeType, delay, nid, dur) {
  const effId = nid();
  const setId = nid();
  const animId = nid();
  const tgt = t.pr
    ? '<p:spTgt spid="' + t.spid + '"><p:txEl><p:pRg st="' + t.pr[0] + '" end="' + t.pr[1] + '"/></p:txEl></p:spTgt>'
    : '<p:spTgt spid="' + t.spid + '"/>';
  const grp = t.type === 'sp' ? ' grpId="0"' : '';
  return '<p:par><p:cTn id="' + effId + '" presetID="10" presetClass="entr" presetSubtype="0" fill="hold"' + grp + ' nodeType="' + nodeType + '">' +
    '<p:stCondLst><p:cond delay="' + delay + '"/></p:stCondLst><p:childTnLst>' +
    '<p:set><p:cBhvr><p:cTn id="' + setId + '" dur="1" fill="hold"><p:stCondLst><p:cond delay="0"/></p:stCondLst></p:cTn>' +
    '<p:tgtEl>' + tgt + '</p:tgtEl><p:attrNameLst><p:attrName>style.visibility</p:attrName></p:attrNameLst></p:cBhvr>' +
    '<p:to><p:strVal val="visible"/></p:to></p:set>' +
    '<p:animEffect transition="in" filter="fade"><p:cBhvr><p:cTn id="' + animId + '" dur="' + dur + '"/><p:tgtEl>' + tgt + '</p:tgtEl></p:cBhvr></p:animEffect>' +
    '</p:childTnLst></p:cTn></p:par>';
}
function timingXml(steps) {
  const DUR = STYLE.apparition.duree_ms;
  const SUITE = STYLE.apparition.suite_ms;
  const clicks = [];
  steps.forEach((s) => {
    if (!s.targets.length) return;
    if (s.trigger === 'click' || !clicks.length) clicks.push([{ trig: 'click', steps: [s] }]);
    else {
      const subs = clicks[clicks.length - 1];
      if (s.trigger === 'after') subs.push({ trig: 'after', steps: [s] });
      else subs[subs.length - 1].steps.push(s);
    }
  });
  if (!clicks.length) return { xml: '', builds: [] };
  let id = 2;
  const nid = () => ++id;
  const builds = [];
  let body = '';
  clicks.forEach((subs) => {
    const outerId = nid();
    let inner = '';
    let offset = 0;
    subs.forEach((sg, k) => {
      const effDelay = sg.trig === 'after' ? SUITE : 0;
      const subOffset = k === 0 ? 0 : offset;
      const subId = nid();
      let effects = '';
      let first = true;
      sg.steps.forEach((st) => st.targets.forEach((t) => {
        const nodeType = first ? (sg.trig === 'after' ? 'afterEffect' : 'clickEffect') : 'withEffect';
        first = false;
        effects += effectXml(t, nodeType, effDelay, nid, DUR);
        builds.push(t);
      }));
      inner += '<p:par><p:cTn id="' + subId + '" fill="hold"><p:stCondLst><p:cond delay="' + subOffset + '"/></p:stCondLst><p:childTnLst>' + effects + '</p:childTnLst></p:cTn></p:par>';
      offset = subOffset + effDelay + DUR;
    });
    body += '<p:par><p:cTn id="' + outerId + '" fill="hold"><p:stCondLst><p:cond delay="indefinite"/></p:stCondLst><p:childTnLst>' + inner + '</p:childTnLst></p:cTn></p:par>';
  });
  const xml = '<p:timing><p:tnLst><p:par><p:cTn id="1" dur="indefinite" restart="never" nodeType="tmRoot"><p:childTnLst>' +
    '<p:seq concurrent="1" nextAc="seek"><p:cTn id="2" dur="indefinite" nodeType="mainSeq"><p:childTnLst>' + body + '</p:childTnLst></p:cTn>' +
    '<p:prevCondLst><p:cond evt="onPrev" delay="0"><p:tgtEl><p:sldTgt/></p:tgtEl></p:cond></p:prevCondLst>' +
    '<p:nextCondLst><p:cond evt="onNext" delay="0"><p:tgtEl><p:sldTgt/></p:tgtEl></p:cond></p:nextCondLst>' +
    '</p:seq></p:childTnLst></p:cTn></p:par></p:tnLst>';
  return { xml, builds };
}
// pptxgenjs répète <a:pPr> devant chaque run d'un paragraphe (texte en accent, point final) :
// le schéma n'en admet qu'un, en tête. On garde le premier, on retire les suivants.
function fixParagraphs(xml) {
  const PPR = /<a:pPr\b[^>]*\/>|<a:pPr\b[^>]*>[\s\S]*?<\/a:pPr>/g;
  return xml.replace(/<a:p>([\s\S]*?)<\/a:p>/g, (all, inner) => {
    let seen = false;
    const out = inner.replace(PPR, (m, off) => {
      if (!seen && !/<a:(?:r|br|fld)\b/.test(inner.slice(0, off))) {
        seen = true;
        return m;
      }
      return '';
    });
    return '<a:p>' + out + '</a:p>';
  });
}
function processSlideXml(xml, x, env, slideNo) {
  xml = fixParagraphs(xml);
  // pptxgenjs coupe le crénage (kern="0") dès qu'un suivi est posé : un titre serré sans crénage
  // laisse des trous entre certaines paires (To, Av, Te). On le rétablit dès 12 pt.
  xml = xml.replace(/ kern="0"/g, ' kern="1200"');
  const c = x.c;
  const map = x.map || [];
  const warn = (m) => env.globalWarnings.push('slide ' + slideNo + ' : ' + m);
  let toks = slideTokens(xml);
  const byId = {};
  toks.forEach((t) => { byId[t.id] = t; });
  // 1. Les identifiants calculés au rendu correspondent-ils aux formes écrites ?
  let consistent = true;
  map.forEach((m) => {
    if (!m) return;
    m.ids.forEach((id, k) => {
      const t = byId[id];
      if (!t || t.name !== m.names[k]) consistent = false;
    });
  });
  if (!consistent) warn('identifiants des formes inattendus : placeholders non groupés et apparitions non posées.');
  // 2. Placeholders dessinés : leurs formes deviennent un seul groupe, simple à remplacer.
  const phGroup = {};
  if (consistent && c.phs.length) {
    let nextId = Math.max.apply(null, toks.map((t) => t.id).concat([1])) + 1;
    const groups = [];
    c.phs.forEach((ph) => {
      const idxs = c.items.map((it, i) => (it.ph === ph.id ? i : -1)).filter((i) => i >= 0);
      const ids = [].concat.apply([], idxs.map((i) => map[i].ids));
      if (ids.length < 2) return;
      const tks = ids.map((id) => byId[id]).sort((a, b) => a.start - b.start);
      const contiguous = tks.every((t, k) => k === 0 || toks.indexOf(t) === toks.indexOf(tks[k - 1]) + 1);
      if (!contiguous) return;
      const its = idxs.map((i) => c.items[i]);
      const bx = (it) => (it.k === 'check' ? [it.cx - it.d / 2, it.cy - it.d / 2, it.d, it.d] : [it.x, it.y, it.w, it.h]);
      const x0 = Math.min.apply(null, its.map((it) => bx(it)[0]));
      const y0 = Math.min.apply(null, its.map((it) => bx(it)[1]));
      const x1 = Math.max.apply(null, its.map((it) => bx(it)[0] + bx(it)[2]));
      const y1 = Math.max.apply(null, its.map((it) => bx(it)[1] + bx(it)[3]));
      const gid = nextId++;
      groups.push({ gid, name: ph.name, first: tks[0], last: tks[tks.length - 1], box: [x0, y0, Math.max(0.01, x1 - x0), Math.max(0.01, y1 - y0)] });
      phGroup[ph.id] = gid;
    });
    groups.sort((a, b) => b.first.start - a.first.start).forEach((g) => {
      const [gx, gy, gw, gh] = g.box.map((v) => Math.round(v * EMU));
      const xf = '<a:xfrm><a:off x="' + gx + '" y="' + gy + '"/><a:ext cx="' + Math.max(1, gw) + '" cy="' + Math.max(1, gh) + '"/><a:chOff x="' + gx + '" y="' + gy + '"/><a:chExt cx="' + Math.max(1, gw) + '" cy="' + Math.max(1, gh) + '"/></a:xfrm>';
      const open = '<p:grpSp><p:nvGrpSpPr><p:cNvPr id="' + g.gid + '" name="' + escXml(g.name) + '"/><p:cNvGrpSpPr/><p:nvPr/></p:nvGrpSpPr><p:grpSpPr>' + xf + '</p:grpSpPr>';
      xml = xml.slice(0, g.first.start) + open + xml.slice(g.first.start, g.last.end) + '</p:grpSp>' + xml.slice(g.last.end);
    });
    toks = slideTokens(xml);
    toks.forEach((t) => { byId[t.id] = t; });
  }
  // 3. Dégradé du chiffre héros (accent → accent2), dans les propriétés du texte.
  if (consistent) {
    c.items.forEach((it, i) => {
      if (!it.grad || !map[i]) return;
      const id = map[i].ids[0];
      const re = new RegExp('<p:sp>(?:(?!<\\/p:sp>)[\\s\\S])*?<p:cNvPr id="' + id + '" [\\s\\S]*?<\\/p:sp>');
      xml = xml.replace(re, (sp) => sp.replace(new RegExp('(<a:rPr\\b[^>]*>)<a:solidFill><a:srgbClr val="' + c.P.accentTxt + '"(?:\\/>|><\\/a:srgbClr>)<\\/a:solidFill>', 'g'),
        '$1<a:gradFill flip="none" rotWithShape="1"><a:gsLst><a:gs pos="0"><a:srgbClr val="' + c.P.accent + '"/></a:gs><a:gs pos="100000"><a:srgbClr val="' + c.P.accent2 + '"/></a:gs></a:gsLst><a:lin ang="0" scaled="1"/></a:gradFill>'));
    });
  }
  // 3 bis. Coins arrondis d'une capture nue (pptxgenjs n'écrit qu'un rectangle).
  if (consistent) {
    c.items.forEach((it, i) => {
      if (it.k !== 'image' || !it.radius || !map[i]) return;
      const id = map[i].ids[0];
      const adj = Math.round(Math.min(50000, it.radius / Math.max(0.01, Math.min(it.w, it.h)) * 100000));
      const re = new RegExp('<p:pic>(?:(?!<\\/p:pic>)[\\s\\S])*?<p:cNvPr id="' + id + '" [\\s\\S]*?<\\/p:pic>');
      xml = xml.replace(re, (pic) => pic.replace(/<a:prstGeom prst="rect">\s*<a:avLst\s*\/>\s*<\/a:prstGeom>/, '<a:prstGeom prst="roundRect"><a:avLst><a:gd name="adj" fmla="val ' + adj + '"/></a:avLst></a:prstGeom>'));
    });
  }
  // 3 quater. Variantes : bouts et angles ronds des tracés, dégradé d'une forme, chiffre au trait
  // (contour et lueur), photo en niveaux de gris.
  if (consistent) {
    const spOf = (id, tag) => new RegExp('<p:' + tag + '>(?:(?!<\\/p:' + tag + '>)[\\s\\S])*?<p:cNvPr id="' + id + '" [\\s\\S]*?<\\/p:' + tag + '>');
    c.items.forEach((it, i) => {
      if (!map[i]) return;
      const id = map[i].ids[0];
      if ((it.k === 'path' || it.k === 'round' || it.k === 'ellipse') && (it.cap || it.join)) {
        xml = xml.replace(spOf(id, 'sp'), (sp) => sp.replace(/<a:ln w="/, '<a:ln' + (it.cap === 'rnd' ? ' cap="rnd"' : '') + ' w="').replace(/<\/a:ln>/, it.join === 'round' ? '<a:round/></a:ln>' : '</a:ln>'));
      }
      if (it.grad2 && it.fill && (it.k === 'round' || it.k === 'rect' || it.k === 'ellipse')) {
        const a = Math.round(((it.grad2.ang === undefined ? 90 : it.grad2.ang) % 360) * 60000);
        xml = xml.replace(spOf(id, 'sp'), (sp) => sp.replace(new RegExp('(<\\/a:prstGeom>)<a:solidFill><a:srgbClr val="' + it.fill + '"(?:\\/>|>(?:<a:alpha val="\\d+"\\/>)?<\\/a:srgbClr>)<\\/a:solidFill>'),
          '$1<a:gradFill rotWithShape="1"><a:gsLst><a:gs pos="0"><a:srgbClr val="' + it.grad2.from + '"/></a:gs><a:gs pos="100000"><a:srgbClr val="' + it.grad2.to + '"/></a:gs></a:gsLst><a:lin ang="' + a + '" scaled="0"/></a:gradFill>'));
      }
      if (it.k === 'text' && it.outline) {
        const O = it.outline;
        xml = xml.replace(spOf(id, 'sp'), (sp) => sp.replace(/(<a:rPr\b[^>]*>)<a:solidFill><a:srgbClr val="[0-9A-F]{6}"(?:\/>|><\/a:srgbClr>)<\/a:solidFill>/g,
          '$1<a:ln w="' + Math.round(O.pt * 12700) + '"><a:solidFill><a:srgbClr val="' + O.color + '"/></a:solidFill></a:ln><a:noFill/><a:effectLst><a:glow rad="' + Math.round(O.glow * 12700) + '"><a:srgbClr val="' + O.color + '"><a:alpha val="' + Math.round(O.glowA * 100000) + '"/></a:srgbClr></a:glow></a:effectLst>'));
      }
      if (it.k === 'image' && it.gray) {
        xml = xml.replace(spOf(id, 'pic'), (pic) => pic.replace(/(<a:blip r:embed="[^"]+">)/, '$1<a:grayscl/>'));
      }
    });
  }
  // 3 ter. Soulignement des [À FOURNIR] adouci (opacité de STYLE.marqueur).
  const alpha = Math.round(STYLE.marqueur.opacite * 100000);
  if (alpha < 100000) xml = xml.replace(/<a:uFill><a:solidFill><a:srgbClr val="([0-9A-F]{6})"(?:\/>|><\/a:srgbClr>)<\/a:solidFill><\/a:uFill>/g, '<a:uFill><a:solidFill><a:srgbClr val="$1"><a:alpha val="' + alpha + '"/></a:srgbClr></a:solidFill></a:uFill>');
  // 4. Apparitions : cibles → identifiants (le groupe pour un placeholder), plages de paragraphes vérifiées.
  let timing = '';
  if (consistent && x.steps && x.steps.length) {
    const npara = (id) => {
      const t = byId[id];
      if (!t) return -1;
      const body = /<p:txBody>[\s\S]*<\/p:txBody>/.exec(t.xml);
      return body ? (body[0].match(/<a:p[ >]/g) || []).length : 0;
    };
    const resolved = x.steps.map((s) => {
      const seen = new Set();
      const targets = [];
      s.targets.forEach((tg) => {
        const it = c.items[tg.idx];
        const m = map[tg.idx];
        if (!it || !m) return;
        let list;
        if (it.ph !== undefined && phGroup[it.ph]) list = [{ spid: phGroup[it.ph], type: 'grp', pr: null }];
        else list = m.ids.map((id) => ({ spid: id, type: m.type, pr: tg.pr }));
        list.forEach((t) => {
          if (t.pr && npara(t.spid) !== (m.nparas || 0)) t.pr = null;
          const key = t.spid + ':' + (t.pr ? t.pr.join('-') : '*');
          if (seen.has(key)) return;
          seen.add(key);
          targets.push(t);
        });
      });
      return { trigger: s.trigger, targets };
    });
    // Une forme animée en entier et par paragraphes à la fois : on garde l'animation entière.
    const wholeIds = new Set();
    resolved.forEach((s) => s.targets.forEach((t) => { if (!t.pr) wholeIds.add(t.spid); }));
    const seenWhole = new Set();
    resolved.forEach((s) => {
      s.targets = s.targets.filter((t) => {
        if (t.pr && wholeIds.has(t.spid)) return false;
        if (!t.pr) {
          if (seenWhole.has(t.spid)) return false;
          seenWhole.add(t.spid);
        }
        return true;
      });
    });
    const tm = timingXml(resolved);
    if (tm.xml) {
      const bld = {};
      tm.builds.forEach((t) => {
        if (t.type !== 'sp') return;
        const isText = map.some((m) => m && m.text && m.ids.includes(t.spid));
        const cur = bld[t.spid] || (isText ? '' : ' animBg="1"');
        bld[t.spid] = t.pr ? ' build="p"' : cur;
      });
      const entries = Object.keys(bld).map((id) => '<p:bldP spid="' + id + '" grpId="0"' + bld[id] + '/>').join('');
      timing = tm.xml + (entries ? '<p:bldLst>' + entries + '</p:bldLst>' : '') + '</p:timing>';
      x.clicks = resolved.filter((s) => s.trigger === 'click' && s.targets.length).length;
    }
  }
  // 5. Transition en fondu, puis animations : après <p:clrMapOvr>, avant </p:sld>.
  const transition = '<p:transition spd="' + STYLE.transition.vitesse + '"><p:fade/></p:transition>';
  const tail = '<p:clrMapOvr><a:masterClrMapping/></p:clrMapOvr>';
  if (xml.includes(tail + '</p:sld>')) xml = xml.replace(tail + '</p:sld>', tail + transition + timing + '</p:sld>');
  else {
    xml = xml.replace(/<\/p:sld>\s*$/, transition + timing + '</p:sld>');
    if (!xml.includes('<p:transition')) warn('transition non posée (structure de slide inattendue).');
  }
  return xml;
}
async function postProcess(buf, env, composed) {
  const JSZip = loadJSZip();
  if (!JSZip) {
    env.globalWarnings.push('jszip introuvable : couleurs du thème, notes, transitions et apparitions non posées (le fichier reste valide).');
    return buf;
  }
  const zip = await JSZip.loadAsync(buf);
  const T = env.T;
  const themePath = 'ppt/theme/theme1.xml';
  const tf = zip.file(themePath);
  if (tf) {
    let xml = await tf.async('string');
    const slots = {
      dk1: T.texte, lt1: T.fondClair, dk2: T.fondSombre, lt2: mix(T.fondClair, T.texte, 0.08),
      accent1: T.accent, accent2: T.accent2, accent3: T.texteSec, accent4: T.texteSecSombre,
      accent5: mix(T.accent, T.fondSombre, 0.4), accent6: mix(T.accent2, T.fondSombre, 0.4), hlink: T.accent, folHlink: T.accent2
    };
    const inner = Object.keys(slots).map((k) => '<a:' + k + '><a:srgbClr val="' + slots[k] + '"/></a:' + k + '>').join('');
    const safeName = escXml(String(T.nom).replace(/[\x00-\x08\x0B\x0C\x0E-\x1F]/g, ''));
    xml = xml.replace(/<a:clrScheme name="[^"]*">[\s\S]*?<\/a:clrScheme>/, '<a:clrScheme name="' + safeName + '">' + inner + '</a:clrScheme>');
    xml = xml.replace(/(<a:theme\b[^>]*\bname=")[^"]*(")/, '$1' + safeName + '$2');
    zip.file(themePath, xml);
  }
  const langTag = env.lang === 'en' ? 'en-US' : 'fr-FR';
  const notesFiles = Object.keys(zip.files).filter((n) => /^ppt\/notesSlides\/notesSlide\d+\.xml$/.test(n));
  for (const n of notesFiles) {
    let xml = await zip.file(n).async('string');
    xml = xml.replace(/<a:p><a:r><a:rPr lang="en-US" dirty="0"\/><a:t>([\s\S]*?)<\/a:t><\/a:r><a:endParaRPr lang="en-US" dirty="0"\/><\/a:p>/, (all, text) => {
      return text.split(/\r?\n/).map((line) => {
        if (!line) return '<a:p><a:endParaRPr lang="' + langTag + '" dirty="0"/></a:p>';
        const sp = /^\s|\s$/.test(line) ? ' xml:space="preserve"' : '';
        return '<a:p><a:r><a:rPr lang="' + langTag + '" dirty="0"/><a:t' + sp + '>' + line + '</a:t></a:r></a:p>';
      }).join('');
    });
    zip.file(n, xml);
  }
  for (let i = 0; i < composed.length; i++) {
    const file = 'ppt/slides/slide' + (i + 1) + '.xml';
    const f = zip.file(file);
    if (!f) continue;
    const xml = await f.async('string');
    zip.file(file, processSlideXml(xml, composed[i], env, i + 1));
  }
  return zip.generateAsync({ type: 'nodebuffer', compression: 'DEFLATE' });
}

// ---------------------------------------------------------------------------
// Programme principal
// ---------------------------------------------------------------------------
function usage(code) {
  console.log('Usage : node build_deck.js deck.json sortie.pptx [--preview sortie.html] [--polices auto|repli]');
  console.log('  --polices auto (par défaut) : le .pptx écrit les polices du thème, installées ici ou non ; repli : il écrit les polices de repli.');
  process.exit(code);
}

async function main() {
  const args = process.argv.slice(2);
  if (!args.length || args.includes('-h') || args.includes('--help')) usage(args.length ? 0 : 2);
  const pos = [];
  let preview = null;
  let fontMode = 'auto';
  for (let i = 0; i < args.length; i++) {
    if (args[i] === '--preview') preview = args[++i];
    else if (args[i] === '--polices') fontMode = args[++i];
    else pos.push(args[i]);
  }
  if (pos.length < 2) usage(2);
  // « principale » (ancien mode qui forçait la police du thème) vaut désormais « auto ».
  if (fontMode === 'principale') fontMode = 'auto';
  if (!['auto', 'repli'].includes(fontMode)) {
    console.error('--polices attend auto ou repli.');
    process.exit(2);
  }
  const deckPath = path.resolve(pos[0]);
  const outPath = path.resolve(pos[1]);
  let deck;
  try {
    deck = JSON.parse(fs.readFileSync(deckPath, 'utf8'));
  } catch (e) {
    console.error('Impossible de lire ' + deckPath + ' : ' + e.message);
    process.exit(2);
  }
  if (!Array.isArray(deck.slides) || !deck.slides.length) {
    console.error('deck.json ne contient aucune slide (champ « slides »).');
    process.exit(2);
  }
  const meta = deck.meta || {};
  const globalWarnings = [];
  const fontNotes = [];
  const lang = String(meta.langue || 'fr').toLowerCase().startsWith('en') ? 'en' : 'fr';
  if (meta.ratio && String(meta.ratio).replace(/\s/g, '') !== '16:9') globalWarnings.push('meta.ratio vaut « ' + meta.ratio + ' » : le rendu est toujours en 16:9.');
  const T = resolveTheme(deck.theme, fontMode, globalWarnings, fontNotes);
  FONT.titre = { cle: T.cleTitre, mesure: T.mesureTitre, ici: T.iciTitre };
  FONT.texte = { cle: T.cleTexte, mesure: T.mesureTexte, ici: T.iciTexte };
  const pub = resolvePublic(meta, loadPublics());
  let sourceMode = meta.affichage_source || pub.affichage_source || 'sous_le_chiffre';
  if (!['sous_le_chiffre', 'renvoi', 'carton_final', 'aucun'].includes(sourceMode)) sourceMode = 'sous_le_chiffre';
  const intervenants = arr(deck.intervenants);
  const people = {};
  intervenants.forEach((p) => { if (p && p.id) people[p.id] = p; });

  const env = {
    T, lang, deckDir: path.dirname(deckPath), pub, sourceMode, intervenants, people,
    collectedSources: [], sourceCounter: 0, sourceIndex: {}, lastSpeaker: null, introduced: new Set(), globalWarnings,
    finalIndex: deck.slides.length - 1,
    // Canva perd l'opacité des runs à l'import : les [À FOURNIR] y gardent des crochets visibles.
    crochets: normKey(meta.format) === 'canva'
  };

  // Composition
  const composed = [];
  let clock = 0;
  deck.slides.forEach((slide, i) => {
    const c = composeSlide(deck, slide, i, env);
    if (c.sourceRef && c.sourceNew) env.collectedSources.push({ n: c.sourceRef, text: c.sourceText, slides: [i + 1] });
    else if (c.sourceRef) env.collectedSources.find((x) => x.n === c.sourceRef).slides.push(i + 1);
    const steps = planAnimations(c);
    const notes = buildNotes(slide, c, env, clock);
    composed.push({ slide, c, notes, steps, start: clock });
    clock += Number(slide.duree_s) || 0;
  });
  if ((sourceMode === 'carton_final' || sourceMode === 'renvoi') && env.collectedSources.length && meta.carton_sources !== false) {
    const slide = { id: 'sources', bloc: composed[composed.length - 1].slide.bloc, archetype: 'SOURCES', fond: 'sombre', duree_s: 0 };
    const c = new SlideCtx(deck, slide, composed.length, env);
    c.sourceOnSlide = false;
    R.SOURCES(c);
    composed.push({ slide, c, notes: LABELS[lang].finalNotes, steps: [], start: clock });
  }

  // .pptx
  const pres = new PptxGenJS();
  pres.layout = 'LAYOUT_16x9';
  pres.title = stripValider(str(meta.titre || 'Présentation'));
  if (intervenants[0] && intervenants[0].nom) pres.author = String(intervenants[0].nom);
  pres.theme = { headFontFace: xmlFace(T.fontTitre), bodyFontFace: xmlFace(T.fontTexte) };
  pres.defineSlideMaster({ title: 'Fond sombre', background: { color: T.fondSombre } });
  pres.defineSlideMaster({ title: 'Fond clair', background: { color: T.fondClair } });
  let lastSection = null;
  composed.forEach((x) => {
    const bloc = str(x.slide.bloc).trim();
    if (bloc && bloc !== lastSection) {
      pres.addSection({ title: bloc });
      lastSection = bloc;
    }
    const opts = { masterName: x.c.P.fond === 'clair' ? 'Fond clair' : 'Fond sombre' };
    if (lastSection) opts.sectionTitle = lastSection;
    const so = pres.addSlide(opts);
    so.background = { color: x.c.P.bg };
    x.map = pptxRender(pres, so, x.c, env);
    so.addNotes(x.notes);
  });
  let buf = await pres.write({ outputType: 'nodebuffer' });
  buf = await postProcess(buf, env, composed);
  fs.mkdirSync(path.dirname(outPath), { recursive: true });
  fs.writeFileSync(outPath, buf);

  // Aperçu
  if (preview) {
    const prevPath = path.resolve(preview);
    fs.mkdirSync(path.dirname(prevPath), { recursive: true });
    fs.writeFileSync(prevPath, previewHtml(deck, composed, env, { duree: clock }));
  }

  // Compte rendu
  const L = LABELS[lang];
  const target = Number(meta.duree_min) || 0;
  const animated = composed.filter((x) => x.clicks);
  console.log('Deck rendu : ' + composed.length + ' slides 16:9 → ' + outPath + ' (un seul fichier)');
  console.log('Transitions : fondu sur chaque slide · apparitions : ' + animated.reduce((n, x) => n + x.clicks, 0) + ' clic(s) sur ' + animated.length + ' slide(s)');
  if (preview) console.log('Aperçu HTML → ' + path.resolve(preview) + ' (ajoutez #qa à l\'adresse pour voir les débordements)');
  const semiNote = (fam, semi) => '« ' + fam + ' »' + (semi ? ' (demi-gras : « ' + semi + ' »)' : ' (demi-gras rendu en gras : pas de face SemiBold installée)');
  console.log('Polices : titre ' + semiNote(T.fontTitre, T.semiTitre) + ', texte ' + semiNote(T.fontTexte, T.semiTexte) + ' · public : ' + pub.cle + ' · sources : ' + sourceMode);
  fontNotes.forEach((m) => console.log('  ' + m));
  console.log('Minutage : ' + fmtTime(clock) + (target ? ' pour ' + target + ' min visées' : ''));
  // Ce qu'il faut valider et fournir, slide par slide.
  const val = [];
  const prov = [];
  composed.forEach((x, i) => {
    const notesProps = [];
    noteSegments(x.slide, env).forEach((s) => stripValider(s.texte, notesProps));
    const screen = x.c.proposals.map((p) => L.q(p));
    const said = notesProps.filter((p) => !x.c.proposals.includes(p)).map((p) => L.q(p));
    if (screen.length || said.length) val.push('  - slide ' + (i + 1) + ' (' + (x.slide.id || '') + ') : ' + (screen.length ? (lang === 'en' ? 'on screen ' : 'à l\'écran ') + screen.join(' ; ') : '') + (screen.length && said.length ? ' · ' : '') + (said.length ? (lang === 'en' ? 'in the script ' : 'dans le script ') + said.join(' ; ') : ''));
    const items = provideItems(x.slide, x.c, env, true);
    const inNotes = noteSegments(x.slide, env).reduce((n, s) => n + fournirLabels(s.texte).length, 0);
    if (items.length || inNotes) prov.push('  - slide ' + (i + 1) + ' (' + (x.slide.id || '') + ') : ' + items.join(' ') + (inNotes ? (items.length ? ' · ' : '') + inNotes + (lang === 'en' ? ' marker(s) in the script' : ' marqueur(s) dans le script') : ''));
  });
  console.log(L.toValidate + ' (' + val.length + ' slide' + (val.length > 1 ? 's' : '') + ')' + (val.length ? ' :' : ' : aucun'));
  val.forEach((l) => console.log(l));
  console.log(L.toProvide + ' (' + prov.length + ' slide' + (prov.length > 1 ? 's' : '') + ')' + (prov.length ? ' :' : ' : aucun'));
  prov.forEach((l) => console.log(l));
  const all = [];
  globalWarnings.forEach((w) => all.push('  - ' + w));
  composed.forEach((x, i) => x.c.warnings.forEach((w) => all.push('  - slide ' + (i + 1) + ' (' + (x.slide.id || '') + ') : ' + w)));
  composed.forEach((x, i) => x.c.fournirs.forEach((l) => {
    const n = l.split(/\s+/).filter(Boolean).length;
    if (n > 3) all.push('  - slide ' + (i + 1) + ' (' + (x.slide.id || '') + ') : libellé [À FOURNIR] de ' + n + ' mots à l\'écran (« ' + l + ' ») : 3 au plus, la consigne va dans a_fournir.');
  }));
  if (all.length) {
    console.log('À vérifier (' + all.length + ') :');
    all.forEach((l) => console.log(l));
  }
}

main().catch((e) => {
  console.error('Échec du rendu : ' + (e && e.stack ? e.stack : e));
  process.exit(1);
});
