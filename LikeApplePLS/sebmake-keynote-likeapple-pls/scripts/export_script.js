#!/usr/bin/env node
/*
 * export_script.js : sort de deck.json le script à dire, la liste des apparitions et les sous-titres.
 *
 *   node export_script.js deck.json --md script.md      script complet, slide par slide (Markdown)
 *   node export_script.js deck.json --etapes            apparitions, avec l'effet conseillé par logiciel
 *   node export_script.js deck.json --srt sortie.srt    sous-titres, une phrase (ou un morceau) par sous-titre
 *   node export_script.js deck.json --visuels visuels.md  visuels à préparer, slide par slide (type, brief,
 *                                                       format, fond transparent, angle, résolution)
 *
 * Les options se combinent. Aucune dépendance (Node 18 et plus).
 * Champs lus : notes (texte, liste de textes ou de segments), build, duree_s, intervenant, bloc,
 * textes, image, visuel, source, a_fournir. Format complet : ../references/deck-spec.md.
 *
 * Marqueurs : [À VALIDER : texte] (proposition de la skill) reste signalé dans le script et
 * listé à la fin ; [À FOURNIR : libellé] (ce qui manque) aussi, avec la consigne de a_fournir.
 * Aucun terme de travail (numéro d'étape, archétype) n'apparaît dans les sorties.
 */
'use strict';

const fs = require('fs');
const path = require('path');

const FOURNIR_RE = /\[(?:À|A) FOURNIR[^\]]*\]|\[TO PROVIDE[^\]]*\]/gi;
const VALIDER_RE = /\[(?:(?:À|A) VALIDER|TO VALIDATE|TO CONFIRM)[^\]]*\]/gi;
const FOURNIR_ONE = /\[(?:À|A) FOURNIR[^\]]*\]|\[TO PROVIDE[^\]]*\]/i;

// Effet conseillé par type de slide (Keynote / PowerPoint, voir references/formats/keynote.md §4).
// Le .pptx porte déjà un fondu au clic ; ces effets servent à retoucher, ou pour Keynote.
const EFFETS = {
  A1: ['Dissolution', 'Fondu'], A4: ['Dissolution, par paragraphe', 'Fondu, par paragraphe'],
  A5: ['Dissolution, puis Apparition', 'Fondu, puis Apparaître'],
  A6: ['Dissolution, élément par élément', 'Fondu, élément par élément'],
  A7: ['Dissolution, par paragraphe', 'Fondu, par paragraphe'],
  A8: ['Apparition, par paragraphe', 'Apparaître, par paragraphe'],
  A9: ['Dissolution', 'Fondu'], A11: ['Apparition', 'Apparaître'], A14: ['Dissolution', 'Fondu'],
  A19: ['Apparition', 'Apparaître'],
  A20: ['deux slides + Déplacement magique', 'deux slides + Morphose']
};

function arr(v) {
  if (v === undefined || v === null) return [];
  return Array.isArray(v) ? v : [v];
}
function str(v) {
  return v === undefined || v === null ? '' : String(v);
}
function uniq(list) {
  const out = [];
  list.forEach((x) => { if (x && !out.includes(x)) out.push(x); });
  return out;
}
function mmss(sec) {
  sec = Math.max(0, Math.round(sec));
  return Math.floor(sec / 60) + ':' + String(sec % 60).padStart(2, '0');
}
function srtTime(sec) {
  const ms = Math.max(0, Math.round(sec * 1000));
  const h = Math.floor(ms / 3600000);
  const m = Math.floor(ms / 60000) % 60;
  const s = Math.floor(ms / 1000) % 60;
  const r = ms % 1000;
  return String(h).padStart(2, '0') + ':' + String(m).padStart(2, '0') + ':' + String(s).padStart(2, '0') + ',' + String(r).padStart(3, '0');
}
function inner(m) {
  const s = String(m).slice(1, -1);
  const i = s.indexOf(':');
  return i < 0 ? '' : s.slice(i + 1).trim();
}
function propsOf(s) {
  // Une proposition sur deux lignes (\n) est listée sur une seule.
  return (str(s).match(VALIDER_RE) || []).map((m) => inner(m).replace(/\s*\n\s*/g, ' ')).filter(Boolean);
}
function provideOf(s) {
  return (str(s).match(FOURNIR_RE) || []).map(inner).filter(Boolean);
}
function unmark(s) {
  return str(s).replace(VALIDER_RE, (m) => inner(m));
}

// Segments de parole d'une slide : [{ intervenant, texte, type }]
function segments(slide, def) {
  const n = slide.notes;
  if (n === undefined || n === null || n === '') return [];
  const who = slide.intervenant || def;
  return arr(n)
    .map((s) => (typeof s === 'string' ? { intervenant: who, texte: s } : { intervenant: s.intervenant || who, texte: String(s.texte || s.text || ''), type: s.type }))
    .filter((s) => s.texte.trim() !== '');
}
function buildList(slide) {
  return arr(slide.build).map((b) => (typeof b === 'string' ? b : str(b && (b.texte || b.text)))).filter((b) => b.trim());
}

// Textes affichés, dans l'ordre de lecture, en une ligne.
function screenText(slide) {
  const t = slide.textes || {};
  const out = [];
  const add = (v) => { if (str(v).trim()) out.push(str(v).replace(/\n/g, ' / ').replace(/\*([^*]+)\*/g, '$1').trim()); };
  add(t.surtitre);
  add(t.libelle && !t.chiffre ? t.libelle : '');
  add(t.titre);
  add(t.chiffre);
  if (t.chiffre) add(t.libelle);
  arr(t.lignes).forEach(add);
  add(t.citation);
  add(t.auteur);
  arr(t.offres).forEach((o) => add([o.nom, o.mention, o.prix, o.note].filter(Boolean).join(' ')));
  arr(t.tuiles).forEach((x) => add(typeof x === 'string' ? x : [x.chiffre, x.titre, x.texte].filter(Boolean).join(' ')));
  arr(t.barres).forEach((b) => add([b.libelle, b.etiquette].filter(Boolean).join(' ')));
  arr(t.logos).forEach((l) => add(typeof l === 'string' ? l : l.nom));
  arr(t.elements).forEach((e) => add(typeof e === 'string' ? e : e.titre));
  add(t.nom);
  add(t.fonction);
  add(t.note);
  add(t.axe);
  return out.join(' · ');
}
function screenStrings(slide) {
  const all = [];
  const walk = (v) => {
    if (typeof v === 'string') all.push(v);
    else if (Array.isArray(v)) v.forEach(walk);
    else if (v && typeof v === 'object') Object.keys(v).forEach((k) => { if (k !== 'image') walk(v[k]); });
  };
  walk(slide.textes || {});
  if (slide.source) all.push(String(slide.source));
  return all;
}
// Images qui manquent encore (chemin introuvable), relatives à deck.json.
function missingImages(slide, deckDir) {
  const out = [];
  const check = (spec) => {
    if (!spec) return;
    const s = typeof spec === 'string' ? { chemin: spec } : spec;
    const abs = s.chemin ? path.resolve(deckDir, s.chemin) : '';
    if (!abs || !fs.existsSync(abs)) out.push(s);
  };
  check(slide.image);
  arr(slide.images).forEach(check);
  check(slide.image_fond);
  ['logo_invite', 'logo_systeme', 'logo_final'].forEach((k) => { if (typeof slide[k] === 'string') check(slide[k]); });
  const t = slide.textes || {};
  arr(t.tuiles).forEach((x) => { if (x && typeof x === 'object' && x.image) check(x.image); });
  ['elements', 'offres', 'coloris', 'jalons'].forEach((k) => arr(t[k]).forEach((x) => {
    if (x && typeof x === 'object' && x.image) check({ chemin: x.image, attendu: x.titre || x.nom });
  }));
  arr(t.pictos).forEach((x) => { if (typeof x === 'string') check(x); });
  arr(t.logos).forEach((x) => { if (x && typeof x === 'object' && x.image) check({ chemin: x.image, attendu: x.nom }); });
  arr(t.colonnes).forEach((c) => arr(c && c.logos).forEach((x) => {
    if (x && typeof x === 'object' && x.image) check({ chemin: x.image, attendu: x.nom });
  }));
  return out;
}

// ---------------------------------------------------------------------------
// Visuels à préparer (slide.visuel, sinon slide.image.attendu)
// ---------------------------------------------------------------------------
// Ce que chaque type de visuel demande par défaut (references/designs.md, section 7 de chaque fiche).
// Un champ écrit dans slide.visuel remplace toujours la valeur par défaut.
const TYPES_VISUEL = {
  capture: { fr: 'Capture d\'écran nue', en: 'Bare screenshot', format: 'PNG', transparent: false,
    resolution: { fr: 'résolution native de l\'écran (téléphone : 1170 × 2532 px ; écran large : 1920 × 1080 px au moins)', en: 'native screen resolution (phone: 1170 × 2532 px; wide screen: at least 1920 × 1080 px)' } },
  photo: { fr: 'Photo', en: 'Photo', format: 'JPEG', transparent: false,
    resolution: { fr: '1920 × 1080 px au moins, 3840 × 2160 px conseillé', en: 'at least 1920 × 1080 px, 3840 × 2160 px recommended' } },
  produit: { fr: 'Produit détouré', en: 'Cut-out product', format: 'PNG', transparent: true,
    resolution: { fr: '2000 px de haut au moins', en: 'at least 2000 px high' } },
  objet: { fr: 'Objet détouré', en: 'Cut-out object', format: 'PNG', transparent: true,
    resolution: { fr: '2000 px sur le grand côté au moins', en: 'at least 2000 px on the long side' } },
  icone: { fr: 'Icône', en: 'Icon', format: 'SVG ou PNG', formatEn: 'SVG or PNG', transparent: true,
    resolution: { fr: '1024 × 1024 px au moins', en: 'at least 1024 × 1024 px' } },
  logo: { fr: 'Logo monochrome', en: 'One-colour logo', format: 'SVG ou PNG', formatEn: 'SVG or PNG', transparent: true,
    resolution: { fr: '600 px de large au moins (1000 px de haut pour la slide finale)', en: 'at least 600 px wide (1000 px high for the closing slide)' } },
  schema: { fr: 'Schéma au trait', en: 'Line diagram', format: 'SVG ou PNG', formatEn: 'SVG or PNG', transparent: true,
    resolution: { fr: '2000 × 2000 px au moins', en: 'at least 2000 × 2000 px' } },
  matiere: { fr: 'Matière en gros plan', en: 'Close-up texture', format: 'JPEG', transparent: false,
    resolution: { fr: '1920 × 1080 px au moins', en: 'at least 1920 × 1080 px' } },
  pictogrammes: { fr: 'Pictogrammes au trait', en: 'Line pictograms', format: 'SVG', transparent: true,
    resolution: { fr: 'vectoriel, un fichier par pictogramme', en: 'vector, one file per pictogram' } },
  vignettes: { fr: 'Série de vignettes', en: 'Set of thumbnails', format: 'JPEG ou PNG', formatEn: 'JPEG or PNG', transparent: false,
    resolution: { fr: '640 px de large au moins chacune, toutes au même format', en: 'at least 640 px wide each, all the same format' } },
  video: { fr: 'Vidéo', en: 'Video', format: 'MP4', transparent: false,
    resolution: { fr: '1920 × 1080 px au moins, 3840 × 2160 px conseillé', en: 'at least 1920 × 1080 px, 3840 × 2160 px recommended' } },
  image: { fr: 'Image', en: 'Image', format: 'PNG ou JPEG', formatEn: 'PNG or JPEG', transparent: false,
    resolution: { fr: '1920 × 1080 px au moins', en: 'at least 1920 × 1080 px' } }
};
const TYPE_ALIASES = { screenshot: 'capture', ecran: 'capture', interface: 'capture', product: 'produit', rendu: 'produit',
  object: 'objet', icon: 'icone', 'icône': 'icone', diagram: 'schema', 'schéma': 'schema', texture: 'matiere', 'matière': 'matiere',
  pictogramme: 'pictogrammes', pictograms: 'pictogrammes', vignette: 'vignettes', thumbnails: 'vignettes', 'vidéo': 'video', rush: 'video' };

function normType(t) {
  const k = str(t).trim().toLowerCase();
  if (!k) return '';
  if (TYPES_VISUEL[k]) return k;
  if (TYPE_ALIASES[k]) return TYPE_ALIASES[k];
  const flat = k.normalize('NFD').replace(/[̀-ͯ]/g, '');
  return TYPES_VISUEL[flat] ? flat : (TYPE_ALIASES[flat] || k);
}

// Type probable d'une image décrite par image.attendu seulement : d'après la variante, puis l'archétype,
// puis les mots de l'attendu.
function typeFromSlide(arch, variante, attendu) {
  const v = str(variante).toLowerCase();
  const a = str(attendu).toLowerCase();
  if (/sur-image|sur-photo|photo|sur-contenu|usage|diptyque|cartouche|portrait/.test(v)) return 'photo';
  if (/macro|matiere/.test(v)) return 'matiere';
  if (/capture|telephone|tablette|portable|appareil|zoom-serre|filet/.test(v)) return 'capture';
  if (/^(objet-coupe|objet-chiffre|empilee|hero-coupe|centre-entier|profil-levitation|coloris)$/.test(v)) return 'produit';
  if (arch === 'A2' || /icone|picto/.test(v)) return arch === 'A15' ? 'vignettes' : 'icone';
  const parArch = { A10: 'capture', A11: 'schema', A12: 'produit', A13: 'produit', A15: 'vignettes', A16: 'logo',
    A18: 'photo', A19: 'produit', A20: 'produit', A21: 'photo', A22: 'video', A23: 'video', A24: 'video', A25: 'video', FIN: 'logo' };
  if (parArch[arch]) return parArch[arch];
  if (/\b(?:écran|ecran|capture|interface|tableau de bord|appli|app)\b/.test(a)) return 'capture';
  if (/\b(?:photo|portrait|paysage|scène|scene)\b/.test(a)) return 'photo';
  if (/\blogo\b/.test(a)) return 'logo';
  if (/\b(?:icône|icone)\b/.test(a)) return 'icone';
  if (/\b(?:carte|schéma|schema|plan)\b/.test(a)) return 'schema';
  if (arch === 'A9' || arch === 'A7' || arch === 'A5') return 'objet';
  return 'image';
}

// Dimensions d'une image PNG, JPEG ou GIF, lues dans l'en-tête du fichier ; null si illisible.
function imageSize(file) {
  try {
    const b = fs.readFileSync(file);
    if (b.length > 24 && b.readUInt32BE(0) === 0x89504e47) return { w: b.readUInt32BE(16), h: b.readUInt32BE(20) };
    if (b.length > 10 && b.toString('ascii', 0, 3) === 'GIF') return { w: b.readUInt16LE(6), h: b.readUInt16LE(8) };
    if (b.length > 4 && b[0] === 0xff && b[1] === 0xd8) {
      let i = 2;
      while (i + 9 < b.length) {
        if (b[i] !== 0xff) { i += 1; continue; }
        const m = b[i + 1];
        const len = b.readUInt16BE(i + 2);
        if (m >= 0xc0 && m <= 0xcf && m !== 0xc4 && m !== 0xc8 && m !== 0xcc) return { w: b.readUInt16BE(i + 7), h: b.readUInt16BE(i + 5) };
        i += 2 + len;
      }
    }
  } catch (e) { /* fichier illisible : pas de mesure */ }
  return null;
}
// Ce que resolution_min exige : { w, h } (au moins), ou { long } (grand côté) ; null si rien de mesurable.
function resolutionNeed(r) {
  if (Array.isArray(r) && r.length === 2) return { w: Number(r[0]), h: Number(r[1]) };
  if (typeof r === 'number') return { long: r };
  if (r && typeof r === 'object') return { w: Number(r.largeur || r.width || r.l) || 0, h: Number(r.hauteur || r.height || r.h) || 0 };
  const t = str(r).replace(/[\s\u00a0\u202f]+/g, ' ');
  let m = t.match(/(\d{2,5}) ?[×xX*] ?(\d{2,5})/);
  if (m) return { w: Number(m[1]), h: Number(m[2]) };
  m = t.match(/(\d{2,5}) ?px de (haut|large)|(\d{2,5}) ?px (high|wide)/);
  if (m) return /haut|high/.test(m[2] || m[4]) ? { h: Number(m[1] || m[3]) } : { w: Number(m[1] || m[3]) };
  m = t.match(/(\d{2,5})/);
  return m ? { long: Number(m[1]) } : null;
}
function belowNeed(size, need) {
  if (!size || !need) return false;
  if (need.long) return Math.max(size.w, size.h) < need.long;
  return (need.w && size.w < need.w) || (need.h && size.h < need.h);
}

function resolutionText(r, en) {
  if (r === undefined || r === null || r === '') return '';
  if (typeof r === 'string' && /^\s*\d{2,5}\s*[×xX*]\s*\d{2,5}\s*$/.test(r)) {
    const m = r.match(/(\d+)\D+(\d+)/);
    return m[1] + ' × ' + m[2] + ' px' + (en ? ' minimum' : ' au moins');
  }
  if (Array.isArray(r) && r.length === 2) return r[0] + ' × ' + r[1] + ' px' + (en ? ' minimum' : ' au moins');
  if (typeof r === 'number') return r + ' px' + (en ? ' on the long side, minimum' : ' sur le grand côté au moins');
  if (typeof r === 'object') {
    const w = r.largeur || r.width || r.l;
    const h = r.hauteur || r.height || r.h;
    if (w && h) return w + ' × ' + h + ' px' + (en ? ' minimum' : ' au moins');
    if (w) return w + ' px' + (en ? ' wide, minimum' : ' de large au moins');
    if (h) return h + ' px' + (en ? ' high, minimum' : ' de haut au moins');
  }
  return str(r);
}

// Liste des visuels d'une slide : [{ type, nom, brief, format, transparent, angle, resolution, chemin, fourni, deduit }]
// Ordre : les visuels décrits (slide.visuel), appariés dans l'ordre à image puis images[] ; puis les
// fichiers principaux sans brief ; puis les images d'éléments et les logos qui manquent encore.
function visualsOf(slide, deckDir, en) {
  const out = [];
  const arch = str(slide.archetype).toUpperCase();
  const variante = str(slide.variante).toLowerCase();
  const exists = (p) => !!p && fs.existsSync(path.resolve(deckDir, p));
  const lang = en ? 'en' : 'fr';
  const spec = (x) => (typeof x === 'string' ? { chemin: x, attendu: '' }
    : (x && typeof x === 'object' ? { chemin: str(x.chemin), attendu: str(x.attendu).trim() } : { chemin: '', attendu: '' }));
  const mains = [];
  if (slide.image) mains.push(spec(slide.image));
  arr(slide.images).forEach((x) => mains.push(spec(x)));
  const make = (v, k, deduit) => {
    const m = (k >= 0 && mains[k]) || {};
    const type = normType(v.type) || typeFromSlide(arch, variante, str(v.brief) || m.attendu);
    const d = TYPES_VISUEL[type] || TYPES_VISUEL.image;
    const chemin = str(v.chemin) || m.chemin || '';
    return {
      type, nom: TYPES_VISUEL[type] ? d[lang] : str(v.type),
      brief: str(v.brief).trim() || m.attendu || '',
      format: str(v.format).trim() || (en && d.formatEn ? d.formatEn : d.format),
      transparent: typeof v.fond_transparent === 'boolean' ? v.fond_transparent : d.transparent,
      angle: str(v.angle).trim(),
      resolution: resolutionText(v.resolution_min, en) || d.resolution[lang],
      chemin, fourni: exists(chemin), deduit,
      taille: exists(chemin) ? imageSize(path.resolve(deckDir, chemin)) : null,
      besoin: resolutionNeed(v.resolution_min)
    };
  };
  const decrits = arr(slide.visuel).filter((v) => v && typeof v === 'object');
  decrits.forEach((v, k) => out.push(make(v, k, false)));
  mains.forEach((m, k) => {
    if (k >= decrits.length && (m.attendu || (m.chemin && !exists(m.chemin)))) out.push(make({}, k, 'attendu'));
  });
  const fond = spec(slide.image_fond);
  if (fond.chemin && !exists(fond.chemin)) out.push(make({ type: 'photo', chemin: fond.chemin, brief: fond.attendu }, -1, 'element'));
  // Images portées par les éléments, et logos, qui manquent encore
  const t = slide.textes || {};
  const el = (list, type, label) => arr(list).forEach((x) => {
    if (x && typeof x === 'object' && x.image && !exists(x.image)) out.push(make({ type, chemin: str(x.image), brief: unmark(label(x)) }, -1, 'element'));
  });
  el(t.tuiles, 'image', (x) => [x.titre, x.texte].filter(Boolean).join(' · '));
  // Tuile de bento qui annonce un visuel (type capture, fragment, icone, photo, matiere) sans image : à préparer.
  arr(t.tuiles).forEach((x) => {
    const ty = x && typeof x === 'object' ? str(x.type).toLowerCase() : '';
    if (!x || x.image || !['capture', 'fragment', 'icone', 'photo', 'matiere'].includes(ty)) return;
    out.push(make({ type: ty, brief: unmark([x.titre, x.texte].filter(Boolean).join(' · ')) }, -1, 'element'));
  });
  el(t.elements, arch === 'A15' && /icones/.test(variante) ? 'icone' : 'image', (x) => str(x.titre));
  el(t.offres, 'produit', (x) => str(x.nom));
  el(t.coloris, 'produit', (x) => [x.nom, x.hex].filter(Boolean).join(' · '));
  el(t.jalons, 'objet', (x) => [x.titre, x.date].filter(Boolean).join(' · '));
  arr(t.pictos).forEach((x) => {
    const p = typeof x === 'string' ? x : str(x && (x.image || x.chemin));
    if (p && !exists(p)) out.push(make({ type: 'pictogrammes', chemin: p }, -1, 'element'));
  });
  // Logos : une seule entrée par slide, qui les nomme tous.
  const logos = [];
  const logo = (x) => {
    if (typeof x === 'string' && x.trim()) logos.push(unmark(x));
    else if (x && typeof x === 'object' && !exists(x.image)) logos.push(unmark(x.nom || x.image || '?'));
  };
  arr(t.logos).forEach(logo);
  arr(t.colonnes).forEach((c) => arr(c && c.logos).forEach(logo));
  ['logo_invite', 'logo_systeme', 'logo_final'].forEach((k) => {
    if (typeof slide[k] === 'string' && slide[k] && !exists(slide[k])) logos.push(slide[k]);
  });
  const noms = uniq(logos);
  if (noms.length) {
    logos.length = 0;
    noms.forEach((x) => logos.push(x));
    const v = make({ type: 'logo', brief: (en ? 'One-colour logo of: ' : 'Logo monochrome de : ') + logos.slice(0, 12).join(', ') + (logos.length > 12 ? ' …' : '') +
      (en ? '. Cropped tight, with the owner\'s consent.' : '. Recadré au ras du dessin, avec l\'accord de son titulaire.') }, -1, 'element');
    if (logos.length > 1) v.nom += ' × ' + logos.length;
    out.push(v);
  }
  return out;
}

// Coupe un texte en sous-titres de 2 lignes de 42 signes au plus.
function subtitleChunks(text) {
  const sentences = text.replace(/\s+/g, ' ').trim().match(/[^.!?…]+[.!?…]*["»”)]?\s*/g) || [];
  const chunks = [];
  const wrap = (sent, width) => {
    const lines = [];
    let cur = '';
    sent.split(' ').forEach((w) => {
      if (cur && (cur + ' ' + w).length > width) {
        lines.push(cur);
        cur = w;
      } else {
        cur = cur ? cur + ' ' + w : w;
      }
    });
    if (cur) lines.push(cur);
    return lines;
  };
  sentences.forEach((sent) => {
    sent = sent.trim();
    // Lignes de 42 signes au plus, deux lignes par sous-titre ; si la dernière resterait seule,
    // on répartit la phrase sur un nombre pair de lignes plus courtes.
    let lines = wrap(sent, 42);
    if (lines.length > 1 && lines.length % 2 === 1) {
      const even = wrap(sent, Math.max(20, Math.ceil(sent.length / (lines.length + 1)) + 6));
      if (even.length % 2 === 0 && even.every((l) => l.length <= 42)) lines = even;
    }
    for (let i = 0; i < lines.length; i += 2) chunks.push(lines.slice(i, i + 2).join('\n'));
  });
  return chunks;
}

function main() {
  const args = process.argv.slice(2);
  if (!args.length || args.includes('-h') || args.includes('--help')) {
    console.log('Usage : node export_script.js deck.json [--md script.md] [--etapes] [--srt sortie.srt] [--visuels visuels.md]');
    process.exit(args.length ? 0 : 2);
  }
  let deckPath = null;
  let md = null;
  let srt = null;
  let etapes = false;
  let visuels = null;
  for (let i = 0; i < args.length; i++) {
    if (args[i] === '--md') md = args[++i];
    else if (args[i] === '--srt') srt = args[++i];
    else if (args[i] === '--visuels') visuels = args[++i];
    else if (args[i] === '--etapes') etapes = true;
    else deckPath = args[i];
  }
  if ((args.includes('--visuels') && !visuels) || (args.includes('--md') && !md) || (args.includes('--srt') && !srt)) {
    console.error('Indiquez un nom de fichier après --md, --srt ou --visuels.');
    process.exit(2);
  }
  if (!deckPath || (!md && !srt && !etapes && !visuels)) {
    console.error('Indiquez deck.json et au moins une sortie : --md, --etapes, --srt ou --visuels.');
    process.exit(2);
  }
  let deck;
  try {
    deck = JSON.parse(fs.readFileSync(deckPath, 'utf8'));
  } catch (e) {
    console.error('Impossible de lire ' + deckPath + ' : ' + e.message);
    process.exit(2);
  }
  const deckDir = path.dirname(path.resolve(deckPath));
  const meta = deck.meta || {};
  const en = String(meta.langue || 'fr').toLowerCase().startsWith('en');
  const slides = arr(deck.slides);
  const people = {};
  arr(deck.intervenants).forEach((p) => { if (p && p.id) people[p.id] = p; });
  const def = (arr(deck.intervenants)[0] || {}).id || '';
  const T = en
    ? {
      sep: ': ', relay: 'handover', build: 'Build', source: 'Source', screen: 'On screen', validate: 'To validate', provide: 'To provide',
      total: 'Total duration', speakers: 'Speakers', none: 'none', roleMissing: 'role to provide', register: 'register',
      withAudience: ' with the audience, ', between: ' between speakers', forTarget: ' for ', onScreen: 'on screen', inScript: 'in the script',
      image: 'screenshot or image', q: (s) => '“' + s + '”', markersInScript: (n) => n + ' marker(s) in the script',
      etapesHead: 'The .pptx already fades each slide in, and fades these builds in on click. This list is for retouching, Keynote, Canva, Figma Slides or video.',
      noBuild: 'No build steps in deck.json.'
    }
    : {
      sep: ' : ', relay: 'relais', build: 'Apparitions', source: 'Source', screen: 'À l\'écran', validate: 'À valider', provide: 'Reste à fournir',
      total: 'Durée totale', speakers: 'Intervenants', none: 'aucun', roleMissing: 'fonction à fournir', register: 'registre',
      withAudience: ' au public, ', between: ' entre intervenants', forTarget: ' pour ', onScreen: 'à l\'écran', inScript: 'dans le script',
      image: 'capture ou image', q: (s) => '« ' + s + ' »', markersInScript: (n) => n + ' marqueur(s) dans le script',
      etapesHead: 'Le .pptx porte déjà un fondu entre les slides et ces apparitions en fondu, au clic. Cette liste sert à les retoucher, ou pour Keynote, Canva, Figma Slides et la vidéo.',
      noBuild: 'Aucune apparition prévue dans deck.json.'
    };
  const roleOf = (p) => {
    const r = str(p.role).trim();
    return r && !FOURNIR_ONE.test(r) ? unmark(r) : '';
  };

  // Script complet (Markdown)
  if (md) {
    let t = 0;
    const toValidate = [];
    const toProvide = [];
    let o = '# ' + unmark(meta.titre || 'Script') + '\n\n';
    o += T.speakers + T.sep + arr(deck.intervenants).map((p) => {
      const r = roleOf(p);
      return unmark(p.nom || p.id) + ' (' + (r || T.roleMissing) + ')';
    }).join(', ');
    if (meta.registre) o += ' · ' + T.register + T.sep + meta.registre + (meta.registre_intervenants ? T.withAudience + meta.registre_intervenants + T.between : '');
    o += '\n';
    arr(deck.intervenants).forEach((p) => {
      if (!roleOf(p)) toProvide.push('- ' + T.speakers + T.sep + unmark(p.nom || p.id) + ', ' + T.roleMissing + '.');
    });
    slides.forEach((s, i) => {
      const d = Number(s.duree_s) || 0;
      o += '\n## ' + (i + 1) + '. ' + (s.bloc ? s.bloc + ' · ' : '') + mmss(t) + ' → ' + mmss(t + d) + ' (' + d + ' s)\n';
      const scr = screenText(s);
      if (scr) o += '\n_' + T.screen + '_' + T.sep + scr + '\n';
      let last = null;
      const segs = segments(s, def);
      segs.forEach((g) => {
        const p = people[g.intervenant] || {};
        const name = unmark(p.nom || g.intervenant || '?');
        o += '\n' + (last && last !== g.intervenant ? '→ ' : '') + '**' + name + '**' + (g.type === 'relais' ? ' (' + T.relay + ')' : '') + T.sep + g.texte.trim() + '\n';
        last = g.intervenant;
      });
      const b = buildList(s);
      if (b.length) o += '\n_' + T.build + '_' + T.sep + b.join(' → ') + '\n';
      if (s.source) o += '\n_' + T.source + '_' + T.sep + s.source + '\n';
      // À valider : propositions affichées et dites.
      const onScreen = uniq([].concat.apply([], screenStrings(s).map(propsOf)));
      const said = uniq([].concat.apply([], segs.map((g) => propsOf(g.texte)))).filter((x) => !onScreen.includes(x));
      if (onScreen.length || said.length) {
        const parts = [];
        const semi = en ? '; ' : ' ; ';
        if (onScreen.length) parts.push(T.onScreen + ' ' + onScreen.map(T.q).join(semi));
        if (said.length) parts.push(T.inScript + ' ' + said.map(T.q).join(semi));
        toValidate.push('- ' + (i + 1) + '. ' + (s.id || '') + T.sep + parts.join(' · '));
      }
      // Reste à fournir : libellés à l'écran, consignes, images, slide AF, marqueurs du script.
      const prov = [];
      const labels = uniq([].concat.apply([], screenStrings(s).map(provideOf)));
      if (labels.length) prov.push(labels.join(', ') + '.');
      arr(s.a_fournir).forEach((x) => { if (str(x).trim()) prov.push(str(x).trim()); });
      if (String(s.archetype || '').toUpperCase() === 'AF' && (s.textes || {}).attendu) prov.push(str(s.textes.attendu).trim());
      missingImages(s, deckDir).forEach((im) => prov.push(T.image + (im.attendu ? ' ' + T.q(im.attendu) : '') + (im.chemin ? ' (' + im.chemin + ')' : '') + '.'));
      const inScript = segs.reduce((n, g) => n + provideOf(g.texte).length, 0);
      if (inScript) prov.push(T.markersInScript(inScript) + '.');
      if (prov.length) {
        o += '\n_' + T.provide + '_' + T.sep + uniq(prov).join(' ') + '\n';
        toProvide.push('- ' + (i + 1) + '. ' + (s.id || '') + T.sep + uniq(prov).join(' '));
      }
      t += d;
    });
    o += '\n---\n\n' + T.total + T.sep + mmss(t) + (meta.duree_min ? T.forTarget + meta.duree_min + ' min' : '') + '\n';
    o += '\n' + T.validate + T.sep + (toValidate.length ? '\n\n' + toValidate.join('\n') : T.none) + '\n';
    o += '\n' + T.provide + T.sep + (toProvide.length ? '\n\n' + toProvide.join('\n') : T.none) + '\n';
    fs.writeFileSync(md, o);
    console.log('Script → ' + path.resolve(md) + ' (' + slides.length + ' slides, ' + mmss(t) + ' ; ' + toValidate.length + ' slide(s) à valider, ' + toProvide.length + ' ligne(s) à fournir)');
  }

  // Apparitions : la liste de build, avec l'effet conseillé par logiciel.
  if (etapes) {
    let n = 0;
    console.log(T.etapesHead);
    slides.forEach((s, i) => {
      const b = buildList(s);
      if (!b.length) return;
      n += 1;
      const arch = String(s.archetype || '').toUpperCase();
      const e = EFFETS[arch];
      const effet = e ? ' [Keynote : ' + e[0] + ' · PowerPoint : ' + e[1] + ']' : '';
      console.log((i + 1) + '. ' + (s.id || '') + effet + '\n   ' + b.map((x, k) => (k + 1) + ') ' + x).join('\n   '));
    });
    if (!n) console.log(T.noBuild);
  }

  // Visuels à préparer : un bloc par slide qui en demande, dans l'ordre du deck.
  if (visuels) {
    const V = en
      ? { head: 'Visuals to prepare', intro: (a, b) => a + ' to prepare, ' + b + ' already provided (listed for reference). The engine draws a stand-in while a visual is missing; a stand-in never carries a number, a logo or a person.',
        todo: 'to prepare', done: 'provided', brief: 'Brief', format: 'Format', transparent: 'Transparent background', angle: 'Angle',
        res: 'Minimum resolution', file: 'File', yes: 'yes', no: 'no', free: 'free', noBrief: 'to write (what it must show)',
        deduced: ' (from image.attendu)', small: ', below the minimum: to replace before presenting',
        smallCount: (n) => n + ' provided file(s) below the minimum resolution.', none: 'No visual to prepare: no slide declares visuel or image.' }
      : { head: 'Visuels à préparer', intro: (a, b) => a + ' à préparer, ' + b + ' déjà fourni(s), listé(s) pour mémoire. Tant qu\'un visuel manque, le moteur dessine un repli ; un repli ne porte jamais de chiffre, de logo ni de personne.',
        todo: 'à préparer', done: 'fourni', brief: 'Brief', format: 'Format', transparent: 'Fond transparent', angle: 'Angle',
        res: 'Résolution minimale', file: 'Fichier', yes: 'oui', no: 'non', free: 'libre', noBrief: 'à écrire (ce qu\'il doit montrer)',
        deduced: ' (d\'après image.attendu)', small: ', sous la résolution minimale : à remplacer avant de présenter',
        smallCount: (n) => n + ' fichier(s) fourni(s) sous la résolution minimale.', none: 'Aucun visuel à préparer : aucune slide ne déclare de visuel ni d\'image.' };
    let aFaire = 0;
    let fournis = 0;
    let trop = 0;
    let body = '';
    slides.forEach((s, i) => {
      const list = visualsOf(s, deckDir, en);
      if (!list.length) return;
      let titre = unmark(screenText(s));
      if (titre.length > 70) titre = titre.slice(0, 70).replace(/\s+\S*$/, '').replace(/[\s·,;:]+$/, '') + '…';
      body += '\n## ' + (i + 1) + '. ' + (s.id || '') + (s.bloc ? ' · ' + s.bloc : '') + '\n' + (titre ? '\n_' + titre + '_\n' : '');
      list.forEach((v, k) => {
        if (v.fourni) fournis += 1; else aFaire += 1;
        const petit = v.fourni && belowNeed(v.taille, v.besoin);
        body += '\n' + (list.length > 1 ? (k + 1) + '. ' : '- ') + '**' + v.nom + '** · ' + (v.fourni ? V.done : V.todo) +
          (v.fourni && v.taille ? ' (' + v.taille.w + ' × ' + v.taille.h + ' px' + (petit ? V.small : '') + ')' : '') +
          (v.deduit === 'attendu' ? V.deduced : '') + '\n';
        if (petit) trop += 1;
        const pad = list.length > 1 ? '   ' : '  ';
        body += pad + '- ' + V.brief + T.sep + unmark(v.brief || V.noBrief) + '\n';
        body += pad + '- ' + V.format + T.sep + v.format + ' · ' + V.transparent + T.sep + (v.transparent ? V.yes : V.no) +
          ' · ' + V.angle + T.sep + (v.angle || V.free) + '\n';
        body += pad + '- ' + V.res + T.sep + v.resolution + '\n';
        if (v.chemin) body += pad + '- ' + V.file + T.sep + '`' + v.chemin + '`\n';
      });
    });
    let o = '# ' + V.head + T.sep + unmark(meta.titre || '') + '\n\n';
    o += (aFaire + fournis) ? V.intro(aFaire, fournis) + (trop ? ' ' + V.smallCount(trop) : '') + '\n' + body : V.none + '\n';
    fs.writeFileSync(visuels, o);
    console.log((en ? 'Visuals → ' : 'Visuels → ') + path.resolve(visuels) + ' (' + aFaire + (en ? ' to prepare, ' : ' à préparer, ') + fournis + (en ? ' provided)' : ' fourni(s))'));
  }

  // Sous-titres : le texte dit, propositions comprises (sans leur marqueur).
  if (srt) {
    let t = 0;
    let k = 0;
    let o = '';
    let markers = 0;
    slides.forEach((s) => {
      const d = Number(s.duree_s) || 0;
      const text = unmark(segments(s, def).map((g) => g.texte.trim()).join(' '));
      markers += (text.match(FOURNIR_RE) || []).length;
      const chunks = subtitleChunks(text);
      const total = chunks.reduce((a, c) => a + c.length, 0) || 1;
      let u = t;
      chunks.forEach((c) => {
        const dt = d * c.length / total;
        k += 1;
        o += k + '\n' + srtTime(u) + ' --> ' + srtTime(u + dt) + '\n' + c + '\n\n';
        u += dt;
      });
      t += d;
    });
    fs.writeFileSync(srt, o);
    console.log('Sous-titres → ' + path.resolve(srt) + ' (' + k + ' sous-titres, ' + mmss(t) + ')');
    if (markers) console.log('Attention : ' + markers + ' marqueur(s) [À FOURNIR] dans le texte à dire.');
  }
}

main();
