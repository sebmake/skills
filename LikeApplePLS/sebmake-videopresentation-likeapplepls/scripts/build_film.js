#!/usr/bin/env node
/*
 * build_film.js : film.json → projets HyperFrames (HTML + GSAP) → planche de validation et MP4.
 *
 *   node build_film.js film.json [--sortie DOSSIER] [--planche] [--rendu]
 *                                [--seulement film,vertical-30] [--qualite draft|standard|high]
 *                                [--fps 30] [--check] [--force]
 *
 *   (sans option)  fabrique les projets seulement (à ouvrir avec « npx hyperframes preview »)
 *   --planche      projets + une image par plan (snapshot HyperFrames) + planche PNG, sans rendu vidéo
 *   --rendu        projets + lint + rendu MP4 de chaque sortie
 *   --seulement    limite aux sorties nommées : « film » et/ou des id de déclinaison
 *   --check        lance aussi « npx hyperframes check » (contraste, mise en page) avant le rendu
 *   --force        rend même si check_film.py ou le lint signalent des erreurs
 *
 * Une sortie = un projet HyperFrames autonome : index.html (racine) + compositions/<plan>.html
 * (une scène par plan, chacune avec sa propre timeline GSAP) + assets/. Chaque format est sa
 * propre composition : les déclinaisons 9:16 et 1:1 sont RECOMPOSÉES (mise en page recalculée par
 * chaque recette), jamais recadrées depuis le 16:9.
 *
 * Aucune voix. Musique : le fichier fourni (droits confirmés par l'utilisateur) ou rien. Aucun chiffre
 * inventé : un carton chiffré sans chiffre fourni affiche [À FOURNIR] estompé. Visuel absent :
 * repli dessiné neutre (formes grises), signalé dans la console et sur la planche.
 *
 * Dépendances : Node 18+, ffmpeg/ffprobe, npx hyperframes (0.8.x). Aucune dépendance npm.
 * Format de film.json : ../references/film-spec.md.
 */
'use strict';

const fs = require('fs');
const path = require('path');
const crypto = require('crypto');
const { spawnSync } = require('child_process');

// ===========================================================================
// RÉGLAGES : tirés des analyses du corpus, résumées dans ../references/ (grammaire-film.md,
// declinaisons.md, recettes.md). Les codes entre parenthèses (R2, F10…) renvoient aux fiches
// d'analyse d'origine, non livrées avec la skill. « conv. » = convention, non observé.
// ===========================================================================
const FORMATS = {
  '16:9': {
    W: 1920, H: 1080, tag: '16x9',
    sure: { x0: 192, y0: 108, x1: 1728, y1: 972 }, // zone titre 80 % central (SKILL HF)
    cy: 540, ligneMax: 1267, carMax: 42,            // ligne ≤ 66 % L (observé 9/9) ; 42 car. (conv.)
    tailles: { carton: 58, mot: 150, nomHeros: 124, nomDiscret: 56, libelle: 68, legende: 34, chiffre: 300, chiffreLibelle: 50 },
  },
  '9:16': {
    W: 1080, H: 1920, tag: '9x16',
    sure: { x0: 65, y0: 230, x1: 1015, y1: 1498 }, // texte entre 12 et 78 % H (SKILL HF), colonne droite (conv.)
    cy: 864, ligneMax: 800, carMax: 22,             // ligne de 800 px : 20 car. à 72 px (conv.)
    tailles: { carton: 72, mot: 150, nomHeros: 132, nomDiscret: 76, libelle: 76, legende: 42, chiffre: 250, chiffreLibelle: 58 },
  },
  '1:1': {
    W: 1080, H: 1080, tag: '1x1',
    sure: { x0: 86, y0: 86, x1: 994, y1: 994 },     // marges de 8 % (conv.)
    cy: 540, ligneMax: 908, carMax: 26,
    tailles: { carton: 62, mot: 124, nomHeros: 116, nomDiscret: 68, libelle: 64, legende: 38, chiffre: 230, chiffreLibelle: 52 },
  },
};

// Largeur moyenne d'un caractère, en em (estimation prudente, phrase en casse normale).
const LARGEUR_CAR = { regular: 0.55, gras: 0.6 };
const INTERLIGNE = 1.18;

// Durées de lecture (grammaire-film.md § 6.4 : convention calée sur l'observé).
const LECTURE = {
  base: 1.2, parMot: 0.3, minPhrase: 1.5, minMot: 1.0, minNom: 2.5,
  tenueConstruite: (mots) => 1.0 + 0.1 * mots, // tenue après le dernier groupe (R2)
  ecartGroupes: 0.8,                           // 0,6 à 2,5 s observé (R3)
  ecartMots: 0.4,                              // 0,3 à 0,5 s par mot (R3)
};
const FONDU = 0.4;      // fondu enchaîné (conv. ; non vérifiable à 2 images/s)
const NOIR_SORTIE = 0.4; // passage par le noir : sortie 0,4–0,6 s (R17)
const NOIR_ENTREE = 0.5; // entrée depuis le noir 0,4–0,8 s (R17)

// Minimum d'un plan par recette (pour l'ajustement des déclinaisons).
const MIN_RECETTE = {
  noir: 0.5, lisere: 2.0, macro: 1.5, orbite: 2.5, eclate: 3.0, revelation: 3.0, panneau: 2.0,
  empilement: 2.5, carton: 1.5, 'mot-sur-image': 1.5, mur: 2.5, fin: 2.5,
};
// Moment montré sur la planche (fraction de la durée du plan).
const INSTANT_PLANCHE = {
  noir: 0.5, lisere: 0.6, macro: 0.6, orbite: 0.6, eclate: 0.4, revelation: 0.8, panneau: 0.8,
  empilement: 0.85, carton: 0.75, 'mot-sur-image': 0.7, mur: 0.75, fin: 0.85,
};

const POLICES_INTERDITES = ['sf pro', 'sf pro display', 'sf pro text', 'sf compact', 'sf mono', 'new york',
  'san francisco', '-apple-system', 'blinkmacsystemfont', 'system-ui', 'ui-sans-serif', 'myriad'];

const GSAP_CDN = 'https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js';
const ENV_HF = Object.assign({}, process.env, { HYPERFRAMES_NO_TELEMETRY: '1', DO_NOT_TRACK: '1' });

// ===========================================================================
// OUTILS
// ===========================================================================
const avert = [];
function signaler(msg) { avert.push(msg); console.warn('  ! ' + msg); }
const r2 = (n) => Math.round(n * 100) / 100;
const r1 = (n) => Math.round(n * 10) / 10;
const px = (n) => `${Math.round(n)}px`;
const esc = (s) => String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
const slug = (s) => String(s).normalize('NFD').replace(/[̀-ͯ]/g, '').toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '') || 'film';
const nbMots = (s) => String(s || '').trim().split(/\s+/).filter((w) => /[\p{L}\p{N}]/u.test(w)).length;

function hexRgb(h) {
  const m = String(h || '').trim().replace('#', '');
  const v = m.length === 3 ? m.split('').map((c) => c + c).join('') : m;
  if (!/^[0-9a-fA-F]{6}$/.test(v)) throw new Error(`Couleur invalide : ${h} (attendu #RRGGBB)`);
  return [0, 2, 4].map((i) => parseInt(v.slice(i, i + 2), 16));
}
const rgbHex = (c) => '#' + c.map((x) => Math.max(0, Math.min(255, Math.round(x))).toString(16).padStart(2, '0')).join('');
function melange(a, b, t) { const A = hexRgb(a), B = hexRgb(b); return rgbHex(A.map((x, i) => x + (B[i] - x) * t)); }
function rgba(h, a) { const c = hexRgb(h); return `rgba(${c[0]},${c[1]},${c[2]},${a})`; }
function luminance(h) {
  return hexRgb(h).map((x) => { const v = x / 255; return v <= 0.03928 ? v / 12.92 : ((v + 0.055) / 1.055) ** 2.4; })
    .reduce((s, v, i) => s + v * [0.2126, 0.7152, 0.0722][i], 0);
}
function contraste(a, b) { const [x, y] = [luminance(a), luminance(b)].sort((p, q) => q - p); return (x + 0.05) / (y + 0.05); }

function run(cmd, args, opts = {}) {
  const r = spawnSync(cmd, args, Object.assign({ encoding: 'utf8', env: ENV_HF, maxBuffer: 64 * 1024 * 1024 }, opts));
  return r;
}

// Taille naturelle d'une image (ffprobe ; SVG lu dans ses attributs).
const cacheTaille = new Map();
function tailleImage(f) {
  if (cacheTaille.has(f)) return cacheTaille.get(f);
  let res = null;
  if (/\.svg$/i.test(f)) {
    const s = fs.readFileSync(f, 'utf8');
    const w = /<svg[^>]*\swidth="([\d.]+)/.exec(s), h = /<svg[^>]*\sheight="([\d.]+)/.exec(s);
    const vb = /viewBox="[\d.\-]+\s+[\d.\-]+\s+([\d.]+)\s+([\d.]+)"/.exec(s);
    res = { w: w ? +w[1] : vb ? +vb[1] : 1000, h: h ? +h[1] : vb ? +vb[2] : 1000, alpha: true };
  } else {
    const r = run('ffprobe', ['-v', 'error', '-select_streams', 'v:0', '-show_entries', 'stream=width,height,pix_fmt', '-of', 'csv=p=0', f]);
    const p = (r.stdout || '').trim().split(',');
    if (p.length >= 2 && +p[0] > 0) res = { w: +p[0], h: +p[1], alpha: /a|pal/.test(p[2] || '') && !/\.jpe?g$/i.test(f) };
    if (res && res.alpha) {
      // boîte utile d'un PNG détouré (marges transparentes retirées du cadrage)
      const b = run('ffmpeg', ['-hide_banner', '-i', f, '-vf', 'alphaextract,format=gray,bbox=min_val=12', '-f', 'null', '-']);
      const m = /x1:(\d+) x2:(\d+) y1:(\d+) y2:(\d+)/.exec(b.stderr || '');
      if (m && +m[2] > +m[1] && +m[4] > +m[3]) res.bbox = { x: +m[1], y: +m[3], w: +m[2] - +m[1] + 1, h: +m[4] - +m[3] + 1 };
    }
  }
  if (!res) res = { w: 1600, h: 1000, alpha: false };
  cacheTaille.set(f, res);
  return res;
}

// Coupe une phrase en groupes de sens (R3) : ponctuation d'abord, sinon au milieu.
function groupesAuto(texte, max = 3) {
  const mots = texte.trim().split(/\s+/);
  if (mots.length <= 6) return [texte.trim()];
  const segs = []; let cur = [];
  mots.forEach((m) => { cur.push(m); if (/[,.;:!?—]$/.test(m)) { segs.push(cur.join(' ')); cur = []; } });
  if (cur.length) segs.push(cur.join(' '));
  if (segs.length >= 2 && segs.length <= max && segs.every((s) => nbMots(s) >= 2)) return segs;
  const n = mots.length > 9 ? 3 : 2;
  const out = []; const taille = Math.ceil(mots.length / n);
  for (let i = 0; i < mots.length; i += taille) out.push(mots.slice(i, i + taille).join(' '));
  return out;
}

// Mise en lignes : jetons {texte, etape} → lignes. En 9:16 construit, une ligne par groupe (R3).
// La coupure se fait aux frontières de groupes, sinon après une ponctuation, sinon au plus équilibré.
const longueur = (l) => l.map((j) => j.texte).join(' ').length;
function couperEquilibre(jetons, carMax) {
  const total = longueur(jetons);
  if (total <= carMax || jetons.length < 2) return [jetons];
  const n = Math.ceil(total / carMax);
  if (n === 2) {
    let best = null;
    for (let i = 1; i < jetons.length; i++) {
      const a = longueur(jetons.slice(0, i)), b = longueur(jetons.slice(i));
      if (a > carMax || b > carMax) continue;
      const cout = Math.max(a, b) - (/[,.;:—]$/.test(jetons[i - 1].texte) ? 8 : 0);
      if (!best || cout < best.cout) best = { i, cout };
    }
    if (best) return [jetons.slice(0, best.i), jetons.slice(best.i)];
  }
  const cible = Math.min(carMax, Math.ceil(total / n) + 4);
  const lignes = []; let cur = [];
  jetons.forEach((j) => { if (cur.length && longueur(cur.concat([j])) > cible) { lignes.push(cur); cur = []; } cur.push(j); });
  if (cur.length) lignes.push(cur);
  return lignes;
}
function mettreEnLignes(jetons, carMax, unGroupeParLigne) {
  if (longueur(jetons) <= carMax && !unGroupeParLigne) return [jetons];
  const groupes = [];
  jetons.forEach((j, i) => { if (i === 0 || j.etape !== jetons[i - 1].etape) groupes.push([]); groupes[groupes.length - 1].push(j); });
  if (groupes.length === 1) return couperEquilibre(jetons, carMax);
  const lignes = []; let cur = [];
  groupes.forEach((g) => {
    if (unGroupeParLigne || (cur.length && longueur(cur.concat(g)) > carMax)) { if (cur.length) lignes.push(...couperEquilibre(cur, carMax)); cur = []; }
    cur = cur.concat(g);
    if (unGroupeParLigne) { lignes.push(...couperEquilibre(cur, carMax)); cur = []; }
  });
  if (cur.length) lignes.push(...couperEquilibre(cur, carMax));
  return lignes;
}

// ===========================================================================
// LECTURE DU FILM
// ===========================================================================
function lireArgs(argv) {
  const a = { fichier: null, sortie: null, planche: false, rendu: false, seulement: null, qualite: 'standard', fps: null, check: false, force: false };
  for (let i = 0; i < argv.length; i++) {
    const v = argv[i];
    if (v === '--sortie') a.sortie = argv[++i];
    else if (v === '--planche') a.planche = true;
    else if (v === '--rendu') a.rendu = true;
    else if (v === '--seulement') a.seulement = argv[++i].split(',').map((s) => s.trim());
    else if (v === '--qualite') a.qualite = argv[++i];
    else if (v === '--fps') a.fps = +argv[++i];
    else if (v === '--check') a.check = true;
    else if (v === '--force') a.force = true;
    else if (!v.startsWith('--') && !a.fichier) a.fichier = v;
    else throw new Error('Option inconnue : ' + v);
  }
  if (!a.fichier) {
    console.error('Usage : node build_film.js film.json [--sortie DOSSIER] [--planche] [--rendu] [--seulement film,ID] [--qualite draft|standard|high]');
    process.exit(2);
  }
  return a;
}

function chargerFilm(fichier) {
  const film = JSON.parse(fs.readFileSync(fichier, 'utf8'));
  film._dir = path.dirname(path.resolve(fichier));
  if (!film.meta || !film.theme || !Array.isArray(film.plans) || !film.plans.length) throw new Error('film.json : meta, theme et plans sont obligatoires.');
  const c = film.theme.couleurs || {};
  const def = { fond_sombre: '#0E1013', fond_clair: '#F2F1EE', texte_sur_sombre: '#F4F4F2', texte_sur_clair: '#16171A' };
  film.theme.couleurs = Object.assign({}, def, c);
  if (!film.theme.couleurs.accent) throw new Error('theme.couleurs.accent est obligatoire (une seule couleur forte).');
  if (!film.theme.couleurs.accent_2) film.theme.couleurs.accent_2 = melange(film.theme.couleurs.accent, '#000000', 0.35);
  for (const k of Object.keys(film.theme.couleurs)) hexRgb(film.theme.couleurs[k]);
  const pol = film.theme.polices || {};
  const pdef = (p, g) => Object.assign({ famille: 'Inter', repli: ['Arial'], fichier: null, graisse: g }, p || {});
  film.theme.polices = { titres: pdef(pol.titres, 700), texte: pdef(pol.texte, 400) };
  for (const p of Object.values(film.theme.polices)) {
    for (const nom of [p.famille].concat(p.repli || [])) {
      if (POLICES_INTERDITES.includes(String(nom).toLowerCase())) throw new Error(`Police refusée (propre à une marque) : ${nom}`);
    }
  }
  const ids = new Set();
  film.plans.forEach((p, i) => {
    if (!p.id || !/^[a-z0-9-]+$/.test(p.id)) throw new Error(`plans[${i}] : id manquant ou invalide (minuscules, chiffres, tirets).`);
    if (ids.has(p.id)) throw new Error(`id en double : ${p.id}`);
    ids.add(p.id);
    if (!RECETTES[p.recette]) throw new Error(`${p.id} : recette inconnue « ${p.recette} ». Recettes : ${Object.keys(RECETTES).join(', ')}`);
    if (!(p.duree_s > 0)) throw new Error(`${p.id} : duree_s manquante.`);
  });
  if (film.musique) {
    const m = film.musique;
    if (/^https?:/i.test(m.fichier || '')) throw new Error('musique.fichier : une adresse web est refusée. Fichier local fourni par l\'utilisateur, ou null.');
    if (m.droits_confirmes !== true) throw new Error('musique.droits_confirmes doit valoir true (l\'utilisateur a les droits), sinon musique: null.');
    if (!fs.existsSync(path.resolve(film._dir, m.fichier))) throw new Error('Fichier de musique introuvable : ' + m.fichier);
  }
  return film;
}

// ===========================================================================
// SORTIES : film long + déclinaisons, durées résolues
// ===========================================================================
function minimumPlan(p, fmtNom, premierReseau) {
  let m = MIN_RECETTE[p.recette] || 1.5;
  const t = p.texte;
  if (t) {
    if (t.type === 'nom') m = Math.max(m, LECTURE.minNom + 0.3);
    else if (t.type === 'chiffre') m = Math.max(m, LECTURE.base + LECTURE.parMot * (nbMots(t.libelle) + 1) + 0.6);
    else if (t.contenu) {
      // même calcul que check_film.py : entrée + construction + lecture (R2) + sortie
      const n = nbMots(t.contenu);
      const lect = Math.max(t.type === 'mot' ? LECTURE.minMot : LECTURE.minPhrase, LECTURE.base + LECTURE.parMot * n);
      const aff = t.type === 'mot' || t.type === 'libelle' ? 'bloc' : (t.affichage || (n > 6 ? 'groupes' : 'bloc'));
      const etapes = aff === 'bloc' ? 1 : aff === 'mot-a-mot' ? n : ((t.groupes || []).length || (n <= 9 ? 2 : 3));
      const constr = (etapes - 1) * (aff === 'mot-a-mot' ? LECTURE.ecartMots : LECTURE.ecartGroupes);
      const lecture = etapes > 1 ? constr + Math.max(lect - constr, LECTURE.tenueConstruite(n)) : lect;
      const marge = premierReseau ? 0.4 : (p.recette === 'mot-sur-image' ? 0.8 : 0.6); // entrée + sortie
      m = Math.max(m, Math.ceil((lecture + marge) * 10 - 1e-6) / 10);
    }
  }
  if (p.recette === 'revelation' && p._avecNom) m = Math.max(m, 4.0);
  // empilement + nom : arrivée des fenêtres (0,2 s chacune en réseau), 0,4 s d'ensemble, nom ≥ 2,5 s
  if (p.recette === 'empilement' && p._avecNom) m = Math.max(m, Math.ceil((0.5 + Math.min(5, ((p.visuels || {}).captures || [1, 2, 3]).length) * 0.2 + 0.4 + 2.8) * 10) / 10);
  if (p.recette === 'mur' && (p.mouvement || {}).mode === 'defile') m = Math.max(m, 0.5 * ((p.visuels || {}).elements || []).length + 1.0);
  return m;
}

function selectionAuto(film, cible) {
  const plans = film.plans.filter((p) => p.recette !== 'noir');
  const groupeDe = (p) => p.groupe || p.id;
  const parGroupe = new Map();
  plans.forEach((p) => { const g = groupeDe(p); if (!parGroupe.has(g)) parGroupe.set(g, []); parGroupe.get(g).push(p); });
  const groupes = [...parGroupe.values()];
  const role = (g) => g[0].role || '';
  const prio = (g) => Math.min(...g.map((p) => p.priorite || 3));
  const pris = new Set();
  const out = [];
  const prendre = (g, extra) => { if (!g || g.some((p) => pris.has(p.id))) return; g.forEach((p) => { pris.add(p.id); out.push(Object.assign({ id: p.id }, extra || {})); }); };
  const gab = cible <= 20 ? { contexte: 0, preuves: 1 } : cible <= 37 ? { contexte: 1, preuves: 2 } : cible <= 52 ? { contexte: 2, preuves: 3 } : { contexte: 2, preuves: 4 };
  // accroche : texte court sur image, sinon la chute (« on ouvre par la chute »), sinon un visuel
  const texteCourt = (p) => p.texte && ['phrase', 'mot'].includes(p.texte.type) && nbMots(p.texte.contenu) <= 4;
  // la phrase-thèse d'abord (declinaisons.md § 2) ; en 20 s et moins, un carton de 4 mots au plus si possible
  const cartonTexte = (p) => p.recette === 'carton' && p.texte && ['phrase', 'mot'].includes(p.texte.type);
  const these = plans.filter((p) => cartonTexte(p) && p.role === 'accroche' && nbMots(p.texte.contenu) <= 6);
  const chutes = plans.filter((p) => cartonTexte(p) && p.role === 'chute');
  const court = cible <= 20 ? these.concat(chutes).filter(texteCourt).sort((x, y) => nbMots(x.texte.contenu) - nbMots(y.texte.contenu))[0] : null;
  const acc = plans.find((p) => p.recette === 'mot-sur-image' && texteCourt(p))
    || court || these[0] || chutes[0]
    || plans.find((p) => p.role === 'accroche' && p.recette !== 'noir');
  if (acc) { pris.add(acc.id); out.push({ id: acc.id }); }
  groupes.filter((g) => role(g) === 'contexte').slice(0, gab.contexte).forEach((g) => prendre(g));
  const rev = groupes.find((g) => role(g) === 'revelation');
  prendre(rev, cible <= 37 ? { avec_nom: true } : null);
  const preuves = groupes.filter((g) => role(g) === 'preuve' && !g.some((p) => pris.has(p.id)));
  const choisies = preuves.map((g, i) => ({ g, i })).sort((a, b) => prio(a.g) - prio(b.g) || a.i - b.i).slice(0, gab.preuves).sort((a, b) => a.i - b.i);
  // 15 s : une preuve = un carton + le plan qui le prouve, sans libellé (budget de 4 textes, declinaisons.md § 3.2)
  // Jusqu'à 37 s, une preuve qui a son carton perd ses noms de fonction : le budget de textes du
  // gabarit (4 en 15 s, 7 en 30 s) ne tient pas sinon. À 15 s, la preuve = son carton + un plan.
  choisies.forEach(({ g }) => {
    let gg = g;
    if (cible <= 20) {
      const c = g.find((p) => p.recette === 'carton');
      const img = g.find((p) => p.recette !== 'carton');
      gg = c && img ? g.filter((p) => p === c || p === img) : g.slice(0, 2);
    }
    const aCarton = gg.some((p) => p.recette === 'carton');
    prendre(gg);
    if (cible <= 37 && aCarton) out.forEach((it) => { const p = film.plans.find((q) => q.id === it.id); if (gg.includes(p) && p.recette !== 'carton') it.sans_texte = true; });
  });
  // la chute, sauf si le dernier plan pris est déjà un carton (jamais deux cartons de suite)
  const dernierPris = out.length ? film.plans.find((q) => q.id === out[out.length - 1].id) : null;
  if (cible > 20 && !(dernierPris && dernierPris.recette === 'carton')) prendre(groupes.find((g) => role(g) === 'chute'));
  prendre(groupes.find((g) => role(g) === 'fin'));
  return out;
}

// Ajuste les durées libres pour tomber sur la cible, sans passer sous les minimums.
function ajusterDurees(items, cible) {
  const fixe = items.filter((it) => it.fixe).reduce((s, it) => s + it.duree, 0);
  let libres = items.filter((it) => !it.fixe);
  libres.forEach((it) => { it.bloque = false; });
  for (let iter = 0; iter < 20; iter++) {
    const bloques = libres.filter((it) => it.bloque).reduce((s, it) => s + it.duree, 0);
    const actifs = libres.filter((it) => !it.bloque);
    if (!actifs.length) break;
    const nat = actifs.reduce((s, it) => s + it.naturel, 0);
    const f = (cible - fixe - bloques) / nat;
    let change = false;
    actifs.forEach((it) => {
      it.duree = it.naturel * f;
      if (it.duree < it.min) { it.duree = it.min; it.bloque = true; change = true; }
    });
    if (!change) break;
  }
  items.forEach((it) => { it.duree = Math.round(it.duree * 10) / 10; });
}

// Le visuel le plus représentatif d'un plan (pour le fond d'un carton d'ouverture en réseau).
function visuelPrincipal(p) {
  const v = p.visuels || {};
  return v.capture || v.image || v.objet || (v.captures || [])[0] || (v.vues || [])[0] || (v.pieces || []).slice(-1)[0] || null;
}

function resoudreSorties(film) {
  const sorties = [];
  const filmFmt = '16:9';
  const pId = new Map(film.plans.map((p) => [p.id, p]));
  if ((film.meta.formats || ['16:9']).includes('16:9')) {
    sorties.push({ id: 'film', nom: `${slug(film.meta.titre || film.meta.produit)}-film-${FORMATS[filmFmt].tag}`, format: filmFmt, reseau: false,
      cible: film.meta.duree_cible_s, musiqueDebut: (film.musique || {}).debut_s || 0,
      plans: film.plans.map((p) => Object.assign({}, p)) });
  }
  for (const d of film.declinaisons || []) {
    if (!FORMATS[d.format]) throw new Error(`Déclinaison ${d.id} : format inconnu ${d.format}`);
    let liste = d.plans;
    if (!liste || d.regle === 'auto') liste = selectionAuto(film, d.duree_cible_s);
    const items = liste.map((x) => (typeof x === 'string' ? { id: x } : x)).filter((x) => {
      const p = pId.get(x.id);
      if (!p) { signaler(`Déclinaison ${d.id} : plan inconnu ${x.id} (ignoré)`); return false; }
      if (p.recette === 'noir') { signaler(`Déclinaison ${d.id} : ${x.id} est un noir, retiré (image 0 pleine, pas de noir en réseau)`); return false; }
      return true;
    }).map((x, i) => {
      const p = Object.assign({}, pId.get(x.id), { _avecNom: !!x.avec_nom });
      if (x.sans_texte && p.texte && p.texte.type === 'libelle') p.texte = null; // moins de mots, jamais d'autres mots
      const min = minimumPlan(p, d.format, i === 0);
      return { p, fixe: x.duree_s > 0, duree: x.duree_s > 0 ? x.duree_s : p.duree_s, naturel: p.duree_s, min };
    });
    // d'abord avec la durée conseillée des cartons (lecture confortable, son coupé) ; si la cible ne
    // le permet pas, avec les seuls minimums de lecture
    const conseil = (p) => (['carton', 'mot-sur-image'].includes(p.recette) && p.texte && ['phrase', 'mot'].includes(p.texte.type)
      ? Math.ceil((Math.max(2.0, 1.5 + 0.3 * nbMots(p.texte.contenu)) + 0.55) * 10 - 1e-6) / 10 : 0);
    const mins = items.map((it) => it.min);
    items.forEach((it) => { it.min = Math.max(it.min, conseil(it.p)); });
    ajusterDurees(items, d.duree_cible_s);
    if (items.reduce((x, it) => x + it.duree, 0) > d.duree_cible_s * 1.02 + 0.05) { // 2 % : arrondis au dixième
      items.forEach((it, i) => { it.min = mins[i]; it.duree = it.fixe ? it.duree : it.naturel; });
      ajusterDurees(items, d.duree_cible_s);
    }
    const plans = items.map((it, i) => {
      const p = Object.assign({}, it.p, { duree_s: it.duree });
      if (i === 0) p.transition = 'coupe';
      if (p.transition === 'noir') p.transition = 'coupe'; // pas de noir en réseau (conv.)
      return p;
    });
    // Ouverture sur un carton : image 0 pleine (declinaisons.md § 2). Le carton garde son texte et son
    // fond, mais le visuel du produit passe derrière lui, flouté et voilé (convention) : le fil ne
    // s'ouvre jamais sur un aplat sombre, et le produit est là dès la première image.
    const p0 = plans[0];
    if (p0 && p0.recette === 'carton' && p0.texte && p0.texte.type !== 'chiffre' && p0.fond !== 'accent') {
      const src = plans.find((q) => q.role === 'revelation' && visuelPrincipal(q)) || plans.find((q) => visuelPrincipal(q))
        || film.plans.find((q) => visuelPrincipal(q));
      if (src) p0._fondImage = visuelPrincipal(src);
    }
    sorties.push({ id: d.id, nom: `${slug(film.meta.titre || film.meta.produit)}-${slug(d.id)}-${FORMATS[d.format].tag}`, format: d.format, reseau: true,
      cible: d.duree_cible_s, musiqueDebut: d.musique_debut_s != null ? d.musique_debut_s : ((film.musique || {}).debut_s || 0), plans });
  }
  return sorties;
}

// Calage des débuts de plan sur les temps de la musique (convention, ±0,25 s).
function grilleTemps(film, projetDir, audioRel) {
  const m = film.musique;
  if (m.temps_s && m.temps_s.length) return m.temps_s.slice().sort((a, b) => a - b);
  if (m.bpm > 0) { const g = []; const pas = 60 / m.bpm; for (let t = m.premier_temps_s || 0; t < 900; t += pas) g.push(r2(t)); return g; }
  const r = run('npx', ['hyperframes', 'beats', projetDir, '--json'], { cwd: projetDir });
  try {
    const dir = path.join(projetDir, 'beats');
    const f = fs.readdirSync(dir, { recursive: true }).find((x) => String(x).endsWith('.json'));
    const j = JSON.parse(fs.readFileSync(path.join(dir, f), 'utf8'));
    const arr = j.beats || j.beatTimes || j.times || (Array.isArray(j) ? j : []);
    return arr.map((b) => (typeof b === 'number' ? b : b.time != null ? b.time : b.t)).filter((x) => typeof x === 'number');
  } catch (e) {
    signaler('Grille de temps introuvable (npx hyperframes beats) : coupes non calées. ' + (r.stderr || '').slice(0, 200));
    return [];
  }
}
function calerSurTemps(sortie, grille, debutMusique) {
  if (!grille.length) return;
  const plans = sortie.plans;
  const total = plans.reduce((x, p) => x + p.duree_s, 0);
  let t = 0, cales = 0;
  for (let i = 0; i < plans.length - 1; i++) {
    const p = plans[i];
    const fin = t + p.duree_s;
    const min = minimumPlan(p, null, i === 0 && sortie.reseau);
    let best = null;
    for (const g of grille) {
      const c = g - debutMusique;
      if (Math.abs(c - fin) <= 0.25 && c - t >= min - 0.01 && (best == null || Math.abs(c - fin) < Math.abs(best - fin))) best = c;
    }
    if (best != null) { p.duree_s = r2(best - t); cales++; }
    t += p.duree_s;
  }
  const dernier = plans[plans.length - 1];
  if (total - t >= minimumPlan(dernier, null, false)) dernier.duree_s = r2(total - t);
  console.log(`  coupes calées sur la musique : ${cales} sur ${plans.length - 1} (convention, ±0,25 s)`);
}

// ===========================================================================
// ASSETS : copie des visuels, replis dessinés neutres, polices
// ===========================================================================
function preparerAssets(film, projetDir) {
  const dir = path.join(projetDir, 'assets');
  fs.mkdirSync(dir, { recursive: true });
  const copies = new Map();
  let nRepli = 0;
  const api = {
    // Retourne { url, w, h, alpha, repli } pour un chemin fourni (ou un repli si absent).
    visuel(chemin, typeRepli, planId, silencieux) {
      if (chemin) {
        const abs = path.resolve(film._dir, chemin);
        if (fs.existsSync(abs)) {
          if (!copies.has(abs)) {
            const h = crypto.createHash('md5').update(abs).digest('hex').slice(0, 6);
            const nom = `v-${h}-${slug(path.basename(abs, path.extname(abs)))}${path.extname(abs).toLowerCase()}`;
            fs.copyFileSync(abs, path.join(dir, nom));
            const t = tailleImage(abs);
            copies.set(abs, { url: `assets/${nom}`, w: t.w, h: t.h, alpha: t.alpha, bbox: t.bbox || null, repli: false });
          }
          return copies.get(abs);
        }
        signaler(`${planId} : visuel introuvable « ${chemin} » → repli dessiné neutre`);
      } else if (!silencieux) {
        signaler(`${planId} : aucun visuel fourni (${typeRepli}) → repli dessiné neutre`);
      }
      nRepli++;
      const r = REPLIS[typeRepli] ? REPLIS[typeRepli](film.theme.couleurs, nRepli) : REPLIS.image(film.theme.couleurs, nRepli);
      const nom = `repli-${typeRepli}-${nRepli}.svg`;
      fs.writeFileSync(path.join(dir, nom), r.svg);
      return { url: `assets/${nom}`, w: r.w, h: r.h, alpha: r.alpha, bbox: r.bbox || null, repli: true };
    },
    fichier(chemin) {
      const abs = path.resolve(film._dir, chemin);
      const nom = `${slug(path.basename(abs, path.extname(abs)))}${path.extname(abs).toLowerCase()}`;
      fs.copyFileSync(abs, path.join(dir, nom));
      return `assets/${nom}`;
    },
  };
  // polices fournies
  let faces = '';
  for (const p of Object.values(film.theme.polices)) {
    if (p.fichier) {
      const abs = path.resolve(film._dir, p.fichier);
      if (!fs.existsSync(abs)) { signaler(`Police introuvable : ${p.fichier} → repli ${p.repli.join(', ')}`); continue; }
      fs.mkdirSync(path.join(dir, 'fonts'), { recursive: true });
      const nom = path.basename(abs);
      fs.copyFileSync(abs, path.join(dir, 'fonts', nom));
      faces += `@font-face { font-family: "${p.famille}"; src: url("assets/fonts/${nom}"); font-weight: ${p.graisse}; font-display: block; }\n`;
    }
  }
  api.fontFaces = faces;
  return api;
}

// Replis : formes neutres, sans texte, sans chiffre, sans marque.
const REPLIS = {
  objet: (c) => ({ w: 1200, h: 1500, alpha: true, bbox: { x: 250, y: 150, w: 700, h: 1200 }, svg: `<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="1500" viewBox="0 0 1200 1500">
<defs><linearGradient id="g" x1="0" x2="1"><stop offset="0" stop-color="#5E6168"/><stop offset=".45" stop-color="#B9BCC2"/><stop offset=".6" stop-color="#9DA1A8"/><stop offset="1" stop-color="#4F5258"/></linearGradient></defs>
<rect x="250" y="150" width="700" height="1200" rx="220" fill="url(#g)"/><rect x="330" y="230" width="540" height="1040" rx="170" fill="none" stroke="#FFFFFF" stroke-opacity=".25" stroke-width="6"/></svg>` }),
  capture: (c) => {
    let s = `<svg xmlns="http://www.w3.org/2000/svg" width="2400" height="1500"><rect width="2400" height="1500" fill="#F3F2EF"/><rect width="440" height="1500" fill="#E9E7E3"/>`;
    for (let i = 0; i < 6; i++) s += `<rect x="70" y="${200 + i * 90}" width="${[280, 220, 260, 200, 240, 180][i]}" height="22" rx="11" fill="#C6C8CC"/>`;
    s += `<rect x="520" y="110" width="560" height="28" rx="14" fill="#3A3C41"/>`;
    for (let i = 0; i < 3; i++) s += `<rect x="${520 + i * 620}" y="240" width="580" height="420" rx="30" fill="#FFFFFF"/><rect x="${570 + i * 620}" y="300" width="90" height="90" rx="22" fill="${i === 1 ? c.accent : '#D5D7DB'}"/><rect x="${570 + i * 620}" y="450" width="${[360, 300, 330][i]}" height="24" rx="12" fill="#3A3C41"/><rect x="${570 + i * 620}" y="500" width="220" height="18" rx="9" fill="#C6C8CC"/>`;
    s += `<rect x="520" y="720" width="1820" height="680" rx="30" fill="#FFFFFF"/>`;
    for (let i = 0; i < 5; i++) s += `<rect x="580" y="${800 + i * 110}" width="1700" height="1" fill="#E2E1DD"/><rect x="580" y="${830 + i * 110}" width="${[700, 560, 820, 480, 640][i]}" height="22" rx="11" fill="#C6C8CC"/>`;
    return { w: 2400, h: 1500, alpha: false, svg: s + '</svg>' };
  },
  image: (c) => ({ w: 2400, h: 1350, alpha: false, svg: `<svg xmlns="http://www.w3.org/2000/svg" width="2400" height="1350">
<defs><radialGradient id="g" cx=".65" cy=".45" r=".8"><stop offset="0" stop-color="${melange(c.fond_sombre, '#FFFFFF', 0.28)}"/><stop offset="1" stop-color="${c.fond_sombre}"/></radialGradient></defs>
<rect width="2400" height="1350" fill="url(#g)"/><rect y="900" width="2400" height="450" fill="${melange(c.fond_sombre, '#000000', 0.3)}"/>
<circle cx="1980" cy="700" r="170" fill="${melange(c.fond_sombre, '#FFFFFF', 0.4)}" opacity=".45"/></svg>` }),
  macro: (c) => ({ w: 2400, h: 1600, alpha: false, svg: `<svg xmlns="http://www.w3.org/2000/svg" width="2400" height="1600">
<defs><linearGradient id="g" x1="0" x2="1" y1="0" y2="1"><stop offset="0" stop-color="#3B3E43"/><stop offset=".5" stop-color="#9A9EA5"/><stop offset="1" stop-color="#34373C"/></linearGradient>
<filter id="n"><feTurbulence type="fractalNoise" baseFrequency="0.002 0.3" numOctaves="2" seed="3"/><feColorMatrix values="0 0 0 0 .5 0 0 0 0 .5 0 0 0 0 .5 .6 0 0 0 0"/></filter></defs>
<rect width="2400" height="1600" fill="url(#g)"/><rect width="2400" height="1600" filter="url(#n)" opacity=".5"/></svg>` }),
  element: (c, n) => {
    const t = ['#33373D', '#3A3631', '#30383A', '#38343C'][n % 4];
    const g = [`<circle cx="256" cy="256" r="90" fill="#E6E4DF"/>`, `<rect x="166" y="166" width="180" height="180" rx="36" fill="none" stroke="#E6E4DF" stroke-width="24"/>`,
      `<polygon points="256,160 360,350 152,350" fill="#E6E4DF"/>`, `<circle cx="256" cy="256" r="100" fill="none" stroke="#E6E4DF" stroke-width="24"/>`][n % 4];
    return { w: 512, h: 512, alpha: true, svg: `<svg xmlns="http://www.w3.org/2000/svg" width="512" height="512"><rect x="16" y="16" width="480" height="480" rx="112" fill="${t}"/>${g}</svg>` };
  },
};

// ===========================================================================
// MISE EN PAGE DU TEXTE
// ===========================================================================
function familleCSS(p) {
  const liste = [p.famille].concat(p.repli || []).filter(Boolean).map((f) => (/^[a-z-]+$/i.test(f) && !/\s/.test(f) && ['serif', 'sans-serif', 'monospace'].includes(f) ? f : `"${f}"`));
  if (!liste.includes('sans-serif')) liste.push('sans-serif');
  return liste.join(', ');
}

// Construit un bloc de texte : lignes, taille ajustée, étapes de construction.
// opts : { texte, groupes, affichage, taille, gras, carMax, ligneMax, forcerLigneParGroupe }
function preparerTexte(o) {
  const mots = nbMots(o.texte);
  let affichage = o.affichage || (mots > 6 ? 'groupes' : 'bloc');
  let unites;
  if (affichage === 'mot-a-mot') unites = o.texte.trim().split(/\s+/);
  else if (affichage === 'groupes') unites = (o.groupes && o.groupes.length ? o.groupes : groupesAuto(o.texte)).map((g) => g.trim());
  else unites = [o.texte.trim()];
  const jetons = [];
  unites.forEach((u, k) => u.split(/\s+/).forEach((w) => jetons.push({ texte: w, etape: affichage === 'bloc' ? 0 : k })));
  const k0 = o.gras ? LARGEUR_CAR.gras : LARGEUR_CAR.regular;
  const carMax = Math.max(6, Math.min(o.carMax, Math.floor(o.ligneMax / (k0 * o.taille)))); // couper plus tôt plutôt que réduire
  const lignes = affichage === 'mot-a-mot' ? couperEquilibre(jetons, carMax) : mettreEnLignes(jetons, carMax, o.forcerLigneParGroupe && affichage === 'groupes');
  const k = o.gras ? LARGEUR_CAR.gras : LARGEUR_CAR.regular;
  let taille = o.taille;
  const plusLongue = Math.max(...lignes.map((l) => l.map((j) => j.texte).join(' ').length));
  if (plusLongue * k * taille > o.ligneMax) taille = Math.max(o.taille * 0.72, o.ligneMax / (plusLongue * k));
  const deborde = plusLongue * k * taille > o.ligneMax + 1;
  const etapes = affichage === 'bloc' ? 1 : unites.length;
  return { lignes, taille: Math.round(taille), etapes, affichage, mots, deborde, plusLongue };
}

// HTML d'un bloc de texte centré en (cx, cy). Une copie par étape de construction (la ligne se
// recentre à chaque ajout, R3) ; le dernier élément arrive à 40 % puis passe au plein.
function htmlTexte(id, t, o) {
  const lh = Math.round(t.taille * INTERLIGNE);
  const hBloc = lh * t.lignes.length;
  const top = Math.round(o.cy - hBloc / 2);
  const larg = Math.round(o.largeur);
  const left = Math.round(o.cx - larg / 2);
  let html = '';
  for (let e = 0; e < t.etapes; e++) {
    const lignesHtml = t.lignes.map((l) => {
      const vis = l.filter((j) => j.etape <= e);
      const contenu = vis.map((j) => (j.etape === e && t.etapes > 1 ? `<span class="${id}-neuf">${esc(j.texte)}</span>` : esc(j.texte))).join(' ');
      return `<div class="${id}-ligne">${contenu || '&#8203;'}</div>`;
    }).join('');
    html += `<div id="${id}-e${e}" class="${id}-bloc">${lignesHtml}</div>`;
  }
  const css = `.${id}-bloc { position: absolute; left: ${left}px; top: ${top}px; width: ${larg}px; height: ${hBloc}px; opacity: 0; text-align: ${o.align || 'center'};
    font-family: ${o.famille}; font-weight: ${o.graisse}; font-size: ${t.taille}px; line-height: ${lh}px; color: ${o.couleur};
    letter-spacing: ${t.taille >= 100 ? '-0.025em' : t.taille >= 50 ? '-0.012em' : '0em'}; }
  .${id}-ligne { white-space: nowrap; height: ${lh}px; }
  .${id}-neuf { display: inline-block; }`;
  return { html, css, hBloc, top, lh };
}

// Timeline d'un bloc : entrée, construction, sortie. Renvoie le code JS et l'instant de fin de lecture.
function jsTexte(id, t, debut, fin, opts = {}) {
  const ent = opts.entree != null ? opts.entree : 0.35;
  let js = '';
  const ecart = t.affichage === 'mot-a-mot' ? LECTURE.ecartMots : LECTURE.ecartGroupes;
  for (let e = 0; e < t.etapes; e++) {
    const te = debut + e * ecart;
    if (e === 0) js += `tl.fromTo("#${id}-e0", { opacity: 0 }, { opacity: 1, duration: ${ent}, ease: "power1.out" }, ${r2(te)});\n`;
    else { js += `tl.set("#${id}-e${e - 1}", { opacity: 0 }, ${r2(te)});\ntl.set("#${id}-e${e}", { opacity: 1 }, ${r2(te)});\n`; }
    if (t.etapes > 1) js += `tl.fromTo("#${id}-e${e} .${id}-neuf", { opacity: 0.4 }, { opacity: 1, duration: 0.3, ease: "power1.out" }, ${r2(te)});\n`;
  }
  const dernier = `#${id}-e${t.etapes - 1}`;
  if (opts.sortie !== false && fin - debut > 0.6) js += `tl.to("${dernier}", { opacity: 0, duration: 0.35, ease: "power1.in" }, ${r2(fin - 0.4)});\n`;
  return { js, finConstruction: debut + (t.etapes - 1) * ecart };
}

// ===========================================================================
// GÉOMÉTRIE COMMUNE
// ===========================================================================
// Place la boîte utile d'un visuel (bbox) dans une boîte {cx, cy, w, h} : renvoie la position de
// l'élément et la taille/position du fond (et du masque) qui ne montrent que la partie utile.
function unionBbox(vs) {
  const bs = vs.map((v) => v.bbox || { x: 0, y: 0, w: v.w, h: v.h });
  const x0 = Math.min(...bs.map((b) => b.x)), y0 = Math.min(...bs.map((b) => b.y));
  const x1 = Math.max(...bs.map((b) => b.x + b.w)), y1 = Math.max(...bs.map((b) => b.y + b.h));
  return { x: x0, y: y0, w: x1 - x0, h: y1 - y0 };
}
function cadreObjet(v, box, bboxForce) {
  const bb = bboxForce || v.bbox || { x: 0, y: 0, w: v.w, h: v.h };
  const o = contenir(box.w, box.h, bb.w, bb.h);
  const s = o.s;
  const taille = `${r1(v.w * s)}px ${r1(v.h * s)}px`, pos = `${r1(-bb.x * s)}px ${r1(-bb.y * s)}px`;
  return { L: r1(box.cx - o.w / 2), T: r1(box.cy - o.h / 2), w: o.w, h: o.h, s, taille, pos,
    fond: (url) => `url("${url}") ${pos} / ${taille} no-repeat`,
    masque: (url) => `-webkit-mask-image: url("${url}"); mask-image: url("${url}"); -webkit-mask-size: ${taille}; mask-size: ${taille}; -webkit-mask-position: ${pos}; mask-position: ${pos}; -webkit-mask-repeat: no-repeat; mask-repeat: no-repeat;` };
}
function contenir(bw, bh, iw, ih) { const s = Math.min(bw / iw, bh / ih); return { w: iw * s, h: ih * s, s }; }
function couvrir(bw, bh, iw, ih) { const s = Math.max(bw / iw, bh / ih); return { w: iw * s, h: ih * s, s }; }

function couleursFond(theme, fond) {
  const c = theme.couleurs;
  if (fond === 'clair') return { bg: c.fond_clair, texte: c.texte_sur_clair, sombre: false };
  if (fond === 'accent') {
    const t = contraste(c.accent, c.texte_sur_sombre) >= contraste(c.accent, c.texte_sur_clair) ? c.texte_sur_sombre : c.texte_sur_clair;
    return { bg: c.accent, texte: t, sombre: luminance(c.accent) < 0.18 };
  }
  if (fond === 'noir') return { bg: '#000000', texte: c.texte_sur_sombre, sombre: true };
  return { bg: c.fond_sombre, texte: c.texte_sur_sombre, sombre: true };
}
function fondDegrade(theme, fond) {
  const c = couleursFond(theme, fond);
  if (fond === 'clair') return `radial-gradient(ellipse 85% 75% at 50% 30%, ${melange(c.bg, '#FFFFFF', 0.55)} 0%, ${c.bg} 70%)`;
  if (fond === 'noir') return '#000000';
  if (fond === 'accent') return c.bg;
  return `radial-gradient(ellipse 80% 70% at 50% 12%, ${melange(c.bg, '#FFFFFF', 0.11)} 0%, ${c.bg} 72%)`; // charbon, point chaud en haut (F10)
}

// Zone image + zone libellé (recettes.md, panneau : nom de fonction à côté de l'écran).
function dispo(fmt, avecLibelle, mobile) {
  const { W, H } = fmt;
  if (fmt.tag === '16x9') {
    if (avecLibelle) return { img: { cx: W * (mobile ? 0.5 : 0.40), cy: H / 2, w: W * (mobile ? 0.45 : 0.6), h: H * 0.86 }, lib: { cx: W * 0.81, cy: H / 2, w: W * 0.22, align: 'center' } };
    return { img: { cx: W / 2, cy: H / 2, w: W * 0.72, h: H * 0.86 }, lib: null };
  }
  if (fmt.tag === '9x16') {
    if (avecLibelle) return { img: { cx: W / 2, cy: H * 0.53, w: W * 0.9, h: H * 0.5 }, lib: { cx: W / 2, cy: H * 0.2, w: W * 0.8, align: 'center' } };
    return { img: { cx: W / 2, cy: fmt.cy, w: W * 0.9, h: H * 0.62 }, lib: null };
  }
  if (avecLibelle) return { img: { cx: W / 2, cy: H * 0.44, w: W * 0.84, h: H * 0.66 }, lib: { cx: W / 2, cy: H * 0.885, w: W * 0.84, align: 'center' } };
  return { img: { cx: W / 2, cy: H / 2, w: W * 0.84, h: H * 0.84 }, lib: null };
}
// Boîte d'un objet seul (declinaisons.md § 5 : 9:16 objet à 55–75 % de la largeur ; 1:1 à 60 %).
function boiteObjet(fmt, avecLibelle) {
  const { W, H } = fmt;
  if (fmt.tag === '16x9') return avecLibelle ? { cx: W * 0.4, cy: H * 0.5, w: W * 0.4, h: H * 0.66 } : { cx: W / 2, cy: H * 0.5, w: W * 0.5, h: H * 0.64 };
  if (fmt.tag === '9x16') return avecLibelle ? { cx: W / 2, cy: H * 0.54, w: W * 0.72, h: H * 0.44 } : { cx: W / 2, cy: H * 0.46, w: W * 0.72, h: H * 0.42 };
  return avecLibelle ? { cx: W / 2, cy: H * 0.44, w: W * 0.6, h: H * 0.6 } : { cx: W / 2, cy: H * 0.5, w: W * 0.62, h: H * 0.66 };
}

// Libellé (1 à 4 mots) : demi-gras, couleur du texte (grammaire-film.md § 6.3).
function libelle(ctx, zone, couleur, debut, fin) {
  const t = ctx.plan.texte;
  if (!t || !t.contenu || !zone) return { html: '', css: '', js: '' };
  const id = `${ctx.P}-lib`;
  const carMax = Math.max(8, Math.floor(zone.w / (LARGEUR_CAR.gras * ctx.fmt.tailles.libelle)));
  const prep = preparerTexte({ texte: t.contenu, affichage: 'bloc', taille: ctx.fmt.tailles.libelle, gras: true, carMax, ligneMax: zone.w });
  if (prep.deborde) signaler(`${ctx.plan.id} (${ctx.fmt.tag}) : libellé trop long pour sa zone`);
  const h = htmlTexte(id, prep, { cx: zone.cx, cy: zone.cy, largeur: zone.w, famille: familleCSS(ctx.theme.polices.titres), graisse: ctx.theme.polices.titres.graisse, couleur, align: zone.align });
  let js = `tl.fromTo("#${id}-e0", { opacity: 0, y: ${r1(ctx.fmt.H * 0.02)} }, { opacity: 1, y: 0, duration: 0.6, ease: "power2.out" }, ${r2(debut)});\n`;
  if (fin - debut > 1.2) js += `tl.to("#${id}-e0", { opacity: 0, duration: 0.4, ease: "power1.in" }, ${r2(fin - 0.45)});\n`;
  ctx.textes.push({ type: 'libelle', contenu: t.contenu, lignes: prep.lignes.length, taille: prep.taille });
  return { html: h.html, css: h.css, js };
}

// Le nom seul, après l'objet ou l'ensemble des écrans (déclinaisons avec « avec_nom ») : le plan
// s'efface en 0,4 s à tNom, puis le nom entre 0,3 s plus tard et tient jusqu'à la fin du plan.
function nomApres(ctx, idMonde, tNom, couleur) {
  const { P, fmt, D, theme } = ctx; const a = (t) => r2(ctx.t0 + t);
  const id = `${P}-nom`;
  const contenu = (ctx.plan.texte && ctx.plan.texte.type === 'nom' && ctx.plan.texte.contenu) || ctx.film.meta.produit;
  const t = preparerTexte({ texte: contenu, affichage: 'bloc', taille: fmt.tailles.nomHeros, gras: true, carMax: fmt.carMax, ligneMax: fmt.ligneMax });
  const h = htmlTexte(id, t, { cx: fmt.W / 2, cy: fmt.cy, largeur: fmt.ligneMax, famille: familleCSS(theme.polices.titres), graisse: theme.polices.titres.graisse, couleur });
  let js = `tl.to("#${idMonde}", { opacity: 0, duration: 0.4, ease: "power1.in" }, ${a(tNom)});\n`;
  js += jsTexte(id, t, ctx.t0 + tNom + 0.3, ctx.t0 + D, { sortie: false, entree: 0.4 }).js;
  ctx.textes.push({ type: 'nom', contenu, lignes: t.lignes.length, taille: t.taille });
  return { css: h.css, html: h.html, js };
}

// ===========================================================================
// RECETTES : chaque fonction reçoit ctx et renvoie { fond, css, html, js }.
// ctx : { P (préfixe d'id), plan, fmt, theme, D (durée locale), t0 (décalage d'entrée), reseau,
//         premier (premier plan de la sortie), assets, textes[] }.  a(t) = ctx.t0 + t.
// ===========================================================================
const RECETTES = {
  // ---- passage par le noir, point lumineux (R17 ; noir 10/14, point 3/14) ----
  noir(ctx) {
    const { P, fmt, D } = ctx; const a = (t) => r2(ctx.t0 + t);
    const m = ctx.plan.mouvement || {};
    if (!m.point) return { fond: '#000000', css: '', html: '', js: '' };
    const acc = ctx.theme.couleurs.accent;
    const css = `#${P}-pt { position: absolute; left: ${px(fmt.W / 2 - 300)}; top: ${px(fmt.H / 2 - 300)}; width: 600px; height: 600px; opacity: 0; }
      #${P}-pt .c { position: absolute; left: 292px; top: 292px; width: 16px; height: 16px; border-radius: 50%; background: #FFFFFF; box-shadow: 0 0 24px 8px rgba(255,255,255,.9); }
      #${P}-pt .g { position: absolute; left: 180px; top: 180px; width: 240px; height: 240px; border-radius: 50%; background: radial-gradient(closest-side, ${rgba(acc, 0.55)}, ${rgba(acc, 0)}); }
      #${P}-pt .h { position: absolute; left: 80px; top: 299px; width: 440px; height: 2px; background: linear-gradient(90deg, rgba(255,255,255,0), rgba(255,255,255,.6), rgba(255,255,255,0)); }
      #${P}-pt .v { position: absolute; left: 299px; top: 80px; width: 2px; height: 440px; background: linear-gradient(180deg, rgba(255,255,255,0), rgba(255,255,255,.6), rgba(255,255,255,0)); }`;
    const html = `<div id="${P}-pt"><div class="g"></div><div class="h"></div><div class="v"></div><div class="c"></div></div>`;
    const dur = Math.min(1.4, D * 0.8);
    const js = `tl.fromTo("#${P}-pt", { opacity: 0, scale: 0.2 }, { opacity: 1, scale: 1, duration: ${r2(dur * 0.45)}, ease: "power2.out" }, ${a(D * 0.1)});
tl.to("#${P}-pt", { opacity: 0, scale: 0.6, duration: ${r2(dur * 0.45)}, ease: "power2.in" }, ${a(D * 0.1 + dur * 0.5)});\n`;
    return { fond: '#000000', css, html, js };
  },

  // ---- studio sombre et liseré (R09, 3/14) ----
  lisere(ctx) {
    const { P, fmt, D, theme } = ctx; const a = (t) => r2(ctx.t0 + t);
    const m = ctx.plan.mouvement || {};
    const v = ctx.assets.visuel((ctx.plan.visuels || {}).objet, 'objet', ctx.plan.id);
    const b = boiteObjet(fmt, false);
    const big = { cx: b.cx, cy: b.cy, w: b.w * 1.15, h: b.h * 1.25 };
    const o = cadreObjet(v, big);
    const L = o.L, T = o.T;
    const dec = Math.max(4, Math.round(Math.min(fmt.W, fmt.H) * 0.006)); // 2 à 4 px observés à 540 p (R09)
    const dx = Math.round((m.cote === 'droite' ? -dec : dec) * 0.6);
    const css = `#${P}-obj { position: absolute; left: ${L}px; top: ${T}px; width: ${r1(o.w)}px; height: ${r1(o.h)}px; transform-origin: 50% 50%; }
      #${P}-obj .cp { position: absolute; left: 0; top: 0; width: 100%; height: 100%; background: ${o.fond(v.url)}; }
      #${P}-blanc { filter: brightness(0) invert(1) drop-shadow(0 0 ${Math.round(dec * 1.2)}px rgba(255,255,255,.55)); --a: -20%;
        -webkit-mask-image: linear-gradient(115deg, rgba(0,0,0,.22) calc(var(--a) - 45%), #000 var(--a), rgba(0,0,0,.22) calc(var(--a) + 50%));
        mask-image: linear-gradient(115deg, rgba(0,0,0,.22) calc(var(--a) - 45%), #000 var(--a), rgba(0,0,0,.22) calc(var(--a) + 50%)); }
      #${P}-sombre { left: ${dx}px !important; top: ${dec}px !important; filter: brightness(0.13); }`;
    const html = `<div id="${P}-obj" data-layout-allow-overflow><div id="${P}-blanc" class="cp"></div><div id="${P}-sombre" class="cp"></div></div>`;
    const js = `tl.fromTo("#${P}-obj", { scale: 1.06, opacity: 0 }, { scale: 1, opacity: 1, duration: ${r2(D)}, ease: "power1.out" }, ${a(0)});
tl.fromTo("#${P}-blanc", { "--a": "-20%", opacity: 0 }, { "--a": "125%", opacity: 0.95, duration: ${r2(D * 0.95)}, ease: "sine.inOut" }, ${a(0.1)});\n`;
    return { fond: `radial-gradient(ellipse 70% 65% at 50% 8%, ${melange(theme.couleurs.fond_sombre, '#FFFFFF', 0.14)} 0%, ${theme.couleurs.fond_sombre} 70%)`, css, html, js };
  },

  // ---- macro qui glisse + mise au point qui glisse (R03 12/14 ; R04 convention) ----
  macro(ctx) {
    const { P, fmt, D, theme } = ctx; const a = (t) => r2(ctx.t0 + t);
    const m = ctx.plan.mouvement || {};
    const v = ctx.assets.visuel((ctx.plan.visuels || {}).image, 'macro', ctx.plan.id);
    const { W, H } = fmt;
    let g, ox, oy, pxx, pyy;
    const pt = m.point || [50, 50];
    if (v.alpha) { // objet détouré : le point se lit dans sa boîte utile
      const bb = v.bbox || { x: 0, y: 0, w: v.w, h: v.h };
      const c = contenir(W * 0.9, H * 0.9, bb.w, bb.h);
      g = { w: v.w * c.s, h: v.h * c.s, s: c.s };
      ox = (W - bb.w * c.s) / 2 - bb.x * c.s; oy = (H - bb.h * c.s) / 2 - bb.y * c.s;
      pxx = ox + (bb.x + bb.w * pt[0] / 100) * c.s; pyy = oy + (bb.y + bb.h * pt[1] / 100) * c.s;
    } else {
      g = couvrir(W, H, v.w, v.h); ox = (W - g.w) / 2; oy = (H - g.h) / 2;
      pxx = ox + g.w * pt[0] / 100; pyy = oy + g.h * pt[1] / 100;
    }
    let s = Math.max(1.2, Math.min(3.5, m.echelle || 2.6));
    if (!v.alpha) s = Math.min(s, Math.max(1.15, (v.w / g.w) * 1.5)); // pas plus de 1,5 × la définition native (R03)
    const sens = m.sens || 'gauche';
    const amp = (sens === 'haut' || sens === 'bas' ? H : W) * 0.04;
    const camX = W / 2 - pxx * s, camY = H / 2 - pyy * s;
    const d0 = { x: camX, y: camY }, d1 = { x: camX, y: camY };
    if (sens === 'gauche') { d0.x += amp; d1.x -= amp; } else if (sens === 'droite') { d0.x -= amp; d1.x += amp; } else if (sens === 'haut') { d0.y += amp; d1.y -= amp; } else { d0.y -= amp; d1.y += amp; }
    if (!v.alpha) {
      // photo ou capture : la caméra ne sort jamais de l'image (sinon bande noire au bord du cadre),
      // avec une marge pour le bord flou des couches de mise au point
      const marge = Math.round(Math.max(W, H) * 0.012);
      const borner = (d, sc) => {
        const xMin = W - sc * (ox + g.w) + marge, xMax = -sc * ox - marge;
        const yMin = H - sc * (oy + g.h) + marge, yMax = -sc * oy - marge;
        d.x = xMin <= xMax ? Math.min(xMax, Math.max(xMin, d.x)) : (xMin + xMax) / 2;
        d.y = yMin <= yMax ? Math.min(yMax, Math.max(yMin, d.y)) : (yMin + yMax) / 2;
      };
      borner(d0, s); borner(d1, s * 1.03);
    }
    const vertical = sens === 'haut' || sens === 'bas';
    const c0 = (vertical ? pt[1] : pt[0]) - 10, c1 = c0 + 20;
    const masque = `linear-gradient(${vertical ? 180 : 90}deg, #000 calc(var(--c) - 24%), transparent calc(var(--c) - 9%), transparent calc(var(--c) + 9%), #000 calc(var(--c) + 24%))`;
    const css = `#${P}-cam { position: absolute; left: 0; top: 0; width: ${W}px; height: ${H}px; transform-origin: 0 0; }
      #${P}-cam .cp { position: absolute; left: ${r1(ox)}px; top: ${r1(oy)}px; width: ${r1(g.w)}px; height: ${r1(g.h)}px; background: url("${v.url}") center / 100% 100% no-repeat; }
      #${P}-flou { filter: blur(${r1(5 / s * 2)}px); -webkit-mask-image: ${masque}; mask-image: ${masque}; --c: ${c0}%; }
      #${P}-tirage { filter: blur(${r1(9 / s * 2)}px); }`;
    const html = `<div id="${P}-cam" data-layout-allow-overflow><div id="${P}-net" class="cp"></div><div id="${P}-flou" class="cp"></div><div id="${P}-tirage" class="cp"></div></div>`;
    let js = `tl.fromTo("#${P}-cam", { x: ${r1(d0.x)}, y: ${r1(d0.y)}, scale: ${r2(s)} }, { x: ${r1(d1.x)}, y: ${r1(d1.y)}, scale: ${r2(s * 1.03)}, duration: ${r2(D)}, ease: "power1.inOut" }, ${a(0)});
tl.fromTo("#${P}-flou", { "--c": "${c0}%" }, { "--c": "${c1}%", duration: ${r2(D * 0.85)}, ease: "power2.inOut" }, ${a(D * 0.1)});
tl.fromTo("#${P}-tirage", { opacity: 1 }, { opacity: 0, duration: ${r2(Math.min(1.0, D * 0.4))}, ease: "power2.inOut" }, ${a(0.1)});\n`;
    const fond = v.alpha ? fondDegrade(theme, ctx.plan.fond || 'sombre') : '#000000';
    const coulLib = v.alpha ? couleursFond(theme, ctx.plan.fond || 'sombre').texte : theme.couleurs.texte_sur_sombre;
    const lib = libelle(ctx, dispo(fmt, true, false).lib, coulLib, ctx.t0 + 0.5, ctx.t0 + D);
    return { fond, css: css + lib.css, html: html + lib.html, js: js + lib.js };
  },

  // ---- orbite simulée : rotation lente ±12° + reflet qui glisse + lévitation (R02 8/14, R01 9/14) ----
  orbite(ctx) {
    const { P, fmt, D, theme } = ctx; const a = (t) => r2(ctx.t0 + t);
    const m = ctx.plan.mouvement || {};
    const vis = ctx.plan.visuels || {};
    const chemins = vis.vues && vis.vues.length ? vis.vues : [vis.objet];
    const vues = chemins.map((c) => ctx.assets.visuel(c, 'objet', ctx.plan.id));
    const fond = ctx.plan.fond || 'clair';
    const cf = couleursFond(theme, fond);
    const avecLib = !!(ctx.plan.texte && ctx.plan.texte.contenu);
    const b = boiteObjet(fmt, avecLib);
    const o = cadreObjet(vues[0], b, unionBbox(vues));
    const L = o.L, T = o.T;
    const ang = Math.min(12, Math.abs(m.angle || 12)) * (m.sens === -1 ? -1 : 1);
    const ombre = cf.sombre
      ? `#${P}-sol { position: absolute; left: ${r1(b.cx - o.w * 0.4)}px; top: ${r1(T + o.h * 0.985)}px; width: ${r1(o.w * 0.8)}px; height: ${r1(o.h * 0.05)}px; border-radius: 50%; background: radial-gradient(closest-side, ${rgba(theme.couleurs.accent, 0.22)}, rgba(0,0,0,0)); filter: blur(18px); }`
      : `#${P}-sol { position: absolute; left: ${r1(b.cx - o.w * 0.32)}px; top: ${r1(T + o.h * 0.975)}px; width: ${r1(o.w * 0.64)}px; height: ${r1(o.h * 0.06)}px; border-radius: 50%; background: radial-gradient(closest-side, rgba(0,0,0,.32), rgba(0,0,0,0)); filter: blur(22px); }`;
    let css = `#${P}-scene3d { position: absolute; left: 0; top: 0; width: ${fmt.W}px; height: ${fmt.H}px; perspective: 1600px; }
      #${P}-pivot { position: absolute; left: ${L}px; top: ${T}px; width: ${r1(o.w)}px; height: ${r1(o.h)}px; transform-origin: 50% 50%; }
      #${P}-pivot .vue { position: absolute; left: 0; top: 0; width: 100%; height: 100%; background-position: ${o.pos}; background-size: ${o.taille}; background-repeat: no-repeat; }
      #${P}-reflet { position: absolute; left: 0; top: 0; width: 100%; height: 100%; ${o.masque(vues[0].url)} overflow: hidden; mix-blend-mode: ${cf.sombre ? 'screen' : 'overlay'}; }
      #${P}-bande { position: absolute; left: -60%; top: -10%; width: 60%; height: 120%; background: linear-gradient(100deg, rgba(255,255,255,0) 20%, rgba(255,255,255,${cf.sombre ? 0.45 : 0.35}) 50%, rgba(255,255,255,0) 80%); }
      ${ombre}`;
    let html = `<div id="${P}-sol"></div><div id="${P}-scene3d"><div id="${P}-pivot">`;
    vues.forEach((v, i) => { html += `<div id="${P}-v${i}" class="vue" style="background-image: url('${v.url}')"></div>`; });
    html += `<div id="${P}-reflet"><div id="${P}-bande" data-layout-allow-overflow></div></div></div></div>`;
    let js = `tl.fromTo("#${P}-pivot", { rotationY: ${-ang}, x: ${r1(fmt.W * 0.012)} }, { rotationY: ${ang}, x: ${r1(-fmt.W * 0.012)}, duration: ${r2(D)}, ease: "sine.inOut" }, ${a(0)});
tl.fromTo("#${P}-pivot", { y: 0 }, { y: ${r1(-fmt.H * 0.008)}, duration: ${r2(D / 2)}, ease: "sine.inOut" }, ${a(0)});
tl.to("#${P}-pivot", { y: 0, duration: ${r2(D / 2)}, ease: "sine.inOut" }, ${a(D / 2)});
tl.fromTo("#${P}-sol", { opacity: 1, scale: 1 }, { opacity: 0.8, scale: 0.93, duration: ${r2(D / 2)}, ease: "sine.inOut" }, ${a(0)});
tl.to("#${P}-sol", { opacity: 1, scale: 1, duration: ${r2(D / 2)}, ease: "sine.inOut" }, ${a(D / 2)});
tl.fromTo("#${P}-bande", { x: ${r1(o.w * 2.2)} }, { x: 0, duration: ${r2(D * 0.9)}, ease: "none" }, ${a(D * 0.05)});\n`;
    if (vues.length > 1) {
      const pas = D / vues.length;
      vues.forEach((v, i) => { js += `tl.fromTo("#${P}-v${i}", { opacity: ${i === 0 ? 1 : 0} }, { opacity: ${i === 0 ? 1 : 0}, duration: 0.01 }, ${a(0)});\n`; });
      for (let i = 1; i < vues.length; i++) {
        js += `tl.to("#${P}-v${i}", { opacity: 1, duration: 0.5, ease: "power1.inOut" }, ${a(i * pas - 0.25)});\n`;
        js += `tl.to("#${P}-v${i - 1}", { opacity: 0, duration: 0.5, ease: "power1.inOut" }, ${a(i * pas - 0.25)});\n`;
      }
    }
    const lib = libelle(ctx, dispo(fmt, true, false).lib, cf.texte, ctx.t0 + 0.5, ctx.t0 + D);
    return { fond: fondDegrade(theme, fond), css: css + lib.css, html: html + lib.html, js: js + lib.js };
  },

  // ---- éclaté en couches qui se referme (R07 ; éclaté 6/14, assemblage 7/14) ----
  eclate(ctx) {
    const { P, fmt, D, theme } = ctx; const a = (t) => r2(ctx.t0 + t);
    const m = ctx.plan.mouvement || {};
    const vis = ctx.plan.visuels || {};
    const fond = ctx.plan.fond || 'clair';
    const cf = couleursFond(theme, fond);
    const avecLib = !!(ctx.plan.texte && ctx.plan.texte.contenu);
    const b = boiteObjet(fmt, avecLib);
    let couches;
    let v0;
    if (vis.pieces && vis.pieces.length) {
      couches = vis.pieces.map((c) => ({ v: ctx.assets.visuel(c, 'objet', ctx.plan.id), clip: null }));
      v0 = couches[0].v;
    } else {
      v0 = ctx.assets.visuel(vis.objet, 'objet', ctx.plan.id);
      const n = Math.max(3, Math.min(6, m.bandes || 4));
      couches = [];
      for (let i = 0; i < n; i++) { // du bas vers le haut
        const haut = (n - 1 - i) / n * 100, bas = i / n * 100;
        couches.push({ v: v0, clip: `inset(${r1(haut)}% 0% ${r1(bas)}% 0%)` });
      }
    }
    const n = couches.length;
    const o = cadreObjet(v0, { cx: b.cx, cy: b.cy, w: b.w, h: b.h * 0.86 }, unionBbox(couches.map((c) => c.v)));
    const L = o.L, T = o.T;
    const profondeur = m.axe === 'profondeur';
    let css = `#${P}-scene3d { position: absolute; left: 0; top: 0; width: ${fmt.W}px; height: ${fmt.H}px; perspective: 2200px; }
      #${P}-pile { position: absolute; left: ${L}px; top: ${T}px; width: ${r1(o.w)}px; height: ${r1(o.h)}px; transform-style: preserve-3d; transform-origin: 50% 50%; }
      #${P}-pile .couche { position: absolute; left: 0; top: 0; width: 100%; height: 100%; background-position: ${o.pos}; background-size: ${o.taille}; background-repeat: no-repeat; }
      #${P}-sol { position: absolute; left: ${r1(b.cx - o.w * 0.34)}px; top: ${r1(T + o.h * 0.97)}px; width: ${r1(o.w * 0.68)}px; height: ${r1(o.h * 0.06)}px; border-radius: 50%; background: radial-gradient(closest-side, ${cf.sombre ? rgba(theme.couleurs.accent, 0.2) : 'rgba(0,0,0,.28)'}, rgba(0,0,0,0)); filter: blur(22px); }`;
    let html = `<div id="${P}-sol"></div><div id="${P}-scene3d"><div id="${P}-pile">`;
    couches.forEach((c, i) => {
      html += `<div id="${P}-c${i}" class="couche" style="background-image: url('${c.v.url}');${c.clip ? ` clip-path: ${c.clip};` : ''}"></div>`;
    });
    html += `</div></div>`;
    const tAss = Math.max(0.9, D - 2.0 - 1.1); // assemblage puis tenue ≥ 1 s
    const dAss = Math.min(2.0, Math.max(1.4, D - tAss - 1.0));
    let js = '';
    const ecartH = o.h * 0.22; // 18 à 30 % de la hauteur (R07)
    couches.forEach((c, i) => {
      const d = i - (n - 1) / 2;
      const from = profondeur
        ? { z: r1(d * 160), y: 0, x: 0, rotation: 0 }
        : { y: r1(-d * ecartH), x: r1(((i % 2) ? 1 : -1) * o.w * 0.02), rotation: r1(((i % 2) ? 1 : -1) * 3.5), z: 0 };
      js += `tl.fromTo("#${P}-c${i}", { opacity: 0, x: ${from.x}, y: ${from.y}, z: ${from.z}, rotation: ${from.rotation} }, { opacity: 1, duration: 0.4, ease: "power1.out" }, ${a(0.1 + i * 0.06)});\n`;
      js += `tl.to("#${P}-c${i}", { x: 0, y: 0, z: 0, rotation: 0, duration: ${r2(dAss)}, ease: "power3.inOut" }, ${a(tAss + (n - 1 - i) * 0.1)});\n`;
    });
    if (profondeur) {
      js += `tl.fromTo("#${P}-pile", { rotationX: 52, rotationZ: -28, scale: 0.86 }, { rotationX: 52, rotationZ: -28, scale: 0.9, duration: ${r2(tAss)}, ease: "none" }, ${a(0)});
tl.to("#${P}-pile", { rotationX: 0, rotationZ: 0, scale: 1, duration: ${r2(dAss + 0.3)}, ease: "power3.inOut" }, ${a(tAss + 0.2)});\n`;
    } else {
      js += `tl.fromTo("#${P}-pile", { scale: 0.94 }, { scale: 1, duration: ${r2(D)}, ease: "power1.out" }, ${a(0)});\n`;
    }
    js += `tl.fromTo("#${P}-sol", { opacity: 0 }, { opacity: 1, duration: ${r2(dAss)}, ease: "power2.inOut" }, ${a(tAss)});\n`;
    const lib = libelle(ctx, dispo(fmt, true, false).lib, cf.texte, ctx.t0 + 0.5, ctx.t0 + D);
    return { fond: fondDegrade(theme, fond), css: css + lib.css, html: html + lib.html, js: js + lib.js };
  },

  // ---- révélation : sortie du noir, halo, lévitation, filet de lumière, recul (R01, R05, R10, R11, R12) ----
  revelation(ctx) {
    const { P, fmt, D, theme } = ctx; const a = (t) => r2(ctx.t0 + t);
    const m = Object.assign({ recul: true, halo: true }, ctx.plan.mouvement || {});
    const v = ctx.assets.visuel((ctx.plan.visuels || {}).objet, 'objet', ctx.plan.id);
    const fond = ctx.plan.fond || 'sombre';
    const cf = couleursFond(theme, fond);
    const b = boiteObjet(fmt, false);
    const o = cadreObjet(v, b);
    const L = o.L, T = o.T;
    const acc = theme.couleurs.accent, acc2 = theme.couleurs.accent_2;
    const avecNom = !!ctx.plan._avecNom;
    const tNom = avecNom ? Math.max(1.2, D - 3.0) : D; // objet d'abord, puis le nom seul ≥ 2,5 s
    const sol = cf.sombre
      ? `#${P}-reflet { position: absolute; left: ${L}px; top: ${r1(T + o.h)}px; width: ${r1(o.w)}px; height: ${r1(o.h)}px; background: ${o.fond(v.url)}; transform: scaleY(-1); transform-origin: 50% 50%; opacity: 0.14; filter: blur(6px); -webkit-mask-image: linear-gradient(0deg, #000 0%, transparent 35%); mask-image: linear-gradient(0deg, #000 0%, transparent 35%); }`
      : `#${P}-reflet { position: absolute; left: ${r1(b.cx - o.w * 0.32)}px; top: ${r1(T + o.h * 0.975)}px; width: ${r1(o.w * 0.64)}px; height: ${r1(o.h * 0.06)}px; border-radius: 50%; background: radial-gradient(closest-side, rgba(0,0,0,.35), rgba(0,0,0,0)); filter: blur(26px); }`;
    let css = `#${P}-monde { position: absolute; left: 0; top: 0; width: ${fmt.W}px; height: ${fmt.H}px; transform-origin: ${r1(b.cx)}px ${r1(b.cy)}px; }
      #${P}-halo { position: absolute; left: ${r1(b.cx - o.w * 0.75)}px; top: ${r1(b.cy - o.h * 0.62)}px; width: ${r1(o.w * 1.5)}px; height: ${r1(o.h * 1.24)}px; border-radius: 50%;
        background: radial-gradient(closest-side at 42% 55%, ${rgba(acc, 0.9)}, ${rgba(acc, 0)}), radial-gradient(closest-side at 62% 42%, ${rgba(acc2, 0.8)}, ${rgba(acc2, 0)}); filter: blur(${Math.round(fmt.H * 0.05)}px); opacity: 0; }
      #${P}-lev { position: absolute; left: ${L}px; top: ${T}px; width: ${r1(o.w)}px; height: ${r1(o.h)}px; }
      #${P}-obj { position: absolute; left: 0; top: 0; width: 100%; height: 100%; background: ${o.fond(v.url)}; }
      #${P}-filet { position: absolute; left: 0; top: 0; width: 100%; height: 100%; overflow: hidden; ${o.masque(v.url)} mix-blend-mode: ${cf.sombre ? 'screen' : 'overlay'}; }
      #${P}-bande { position: absolute; left: -40%; top: -20%; width: 40%; height: 140%; background: linear-gradient(105deg, rgba(255,255,255,0) 30%, rgba(255,255,255,${cf.sombre ? 0.55 : 0.3}) 50%, rgba(255,255,255,0) 70%); }
      ${sol}`;
    let html = `<div id="${P}-monde" data-layout-allow-overflow>${m.halo ? `<div id="${P}-halo"></div>` : ''}<div id="${P}-reflet"></div><div id="${P}-lev"><div id="${P}-obj"></div><div id="${P}-filet"><div id="${P}-bande" data-layout-allow-overflow></div></div></div></div>`;
    const entree = ctx.reseau ? 0.25 : Math.min(1.2, D * 0.18);
    let js = `tl.fromTo("#${P}-monde", { opacity: 0 }, { opacity: 1, duration: ${r2(entree)}, ease: "power2.in" }, ${a(0)});\n`;
    if (m.recul) js += `tl.fromTo("#${P}-monde", { scale: 1.3 }, { scale: 1, duration: ${r2(Math.min(tNom, Math.max(3, D * 0.8)))}, ease: "expo.out" }, ${a(0)});\n`;
    if (m.halo) js += `tl.fromTo("#${P}-halo", { opacity: 0, scale: 0.85 }, { opacity: 0.42, scale: 1, duration: 1.2, ease: "power2.out" }, ${a(entree * 0.6)});\n`;
    js += `tl.fromTo("#${P}-lev", { y: 0 }, { y: ${r1(-fmt.H * 0.008)}, duration: ${r2(D / 2)}, ease: "sine.inOut" }, ${a(0)});
tl.to("#${P}-lev", { y: 0, duration: ${r2(D / 2)}, ease: "sine.inOut" }, ${a(D / 2)});
tl.fromTo("#${P}-bande", { x: 0 }, { x: ${r1(o.w * 2.5)}, duration: ${r2(Math.min(3.5, Math.max(2.0, tNom * 0.55)))}, ease: "none" }, ${a(Math.min(entree + 0.3, tNom * 0.3))});\n`;
    if (avecNom) {
      const n = nomApres(ctx, `${P}-monde`, tNom, cf.texte);
      css += n.css; html += n.html; js += n.js;
    }
    return { fond: fondDegrade(theme, fond), css, html, js };
  },

  // ---- panneau d'interface flottant, zoom dans un détail ou projecteur (UI R1, R2, R3, R6) ----
  panneau(ctx) {
    const { P, fmt, D, theme } = ctx; const a = (t) => r2(ctx.t0 + t);
    const m = ctx.plan.mouvement || {};
    const v = ctx.assets.visuel((ctx.plan.visuels || {}).capture, 'capture', ctx.plan.id);
    const fond = ctx.plan.fond || 'clair';
    const cf = couleursFond(theme, fond);
    const mobile = v.h > v.w;
    const avecLib = !!(ctx.plan.texte && ctx.plan.texte.contenu);
    const dz = dispo(fmt, avecLib, mobile);
    let zw = dz.img.w, zh = dz.img.h;
    if (mobile) { zh = fmt.tag === '16x9' ? fmt.H * 0.86 : fmt.tag === '9x16' ? fmt.H * (avecLib ? 0.5 : 0.6) : fmt.H * 0.7; zw = fmt.W * 0.9; }
    const g = contenir(zw, zh, v.w, v.h);
    const Pn = { x: dz.img.cx - g.w / 2, y: dz.img.cy - g.h / 2, w: g.w, h: g.h };
    const k = Pn.w / v.w;
    const rayon = Math.round((mobile ? 40 : 16) * fmt.H / 1080 * (fmt.tag === '9x16' ? 0.6 : 1));
    const ombre = cf.sombre ? `box-shadow: 0 0 0 1px rgba(255,255,255,.08);` : `box-shadow: 0 ${Math.round(fmt.H * 0.025)}px ${Math.round(fmt.H * 0.06)}px rgba(0,0,0,.18);`;
    const det = m.detail && m.detail.zone ? m.detail : null;
    let css = `#${P}-pousse { position: absolute; left: 0; top: 0; width: ${fmt.W}px; height: ${fmt.H}px; transform-origin: ${r1(Pn.x + Pn.w / 2)}px ${r1(Pn.y + Pn.h / 2)}px; }
      #${P}-cam { position: absolute; left: 0; top: 0; width: ${fmt.W}px; height: ${fmt.H}px; transform-origin: 0 0; }
      #${P}-pan { position: absolute; left: ${r1(Pn.x)}px; top: ${r1(Pn.y)}px; width: ${r1(Pn.w)}px; height: ${r1(Pn.h)}px; }
      #${P}-pan .cp { position: absolute; left: 0; top: 0; width: 100%; height: 100%; border-radius: ${rayon}px; overflow: hidden; background: url("${v.url}") 0 0 / 100% 100% no-repeat; }
      #${P}-base { ${ombre} }`;
    let html = `<div id="${P}-pousse" data-layout-allow-overflow><div id="${P}-cam" data-layout-allow-overflow><div id="${P}-pan"><div id="${P}-base" class="cp"></div>${det ? `<div id="${P}-net" class="cp"></div>` : ''}</div></div></div>`;
    const tEntree = ctx.reseau && ctx.premier ? 0 : 0.15;
    const dEntree = ctx.reseau ? 0.5 : 0.9;
    let js = `tl.fromTo("#${P}-pan", { y: ${r1(fmt.H * 0.04)}, opacity: 0, scale: 0.96 }, { y: 0, opacity: 1, scale: 1, duration: ${dEntree}, ease: "power3.out" }, ${a(tEntree)});\n`;
    if (det) {
      const z = det.zone.map((n) => +n);
      const zr = { x: z[0] / 100 * v.w, y: z[1] / 100 * v.h, w: z[2] / 100 * v.w, h: z[3] / 100 * v.h };
      const r = { x: Pn.x + zr.x * k, y: Pn.y + zr.y * k, w: zr.w * k, h: zr.h * k };
      const inset = `inset(${r1(zr.y * k)}px ${r1(Pn.w - (zr.x + zr.w) * k)}px ${r1(Pn.h - (zr.y + zr.h) * k)}px ${r1(zr.x * k)}px round ${Math.round(10 * fmt.H / 1080)}px)`;
      const tz = fmt.tag === '9x16' && !mobile ? (ctx.reseau ? 0.7 : 1.0) : (ctx.reseau ? 0.8 : 1.4);
      const sDef = 1.25 / k; // jamais plus de 1,25 × la définition native de la capture
      if ((det.mode || 'zoom') === 'projecteur') {
        // Projecteur (mesuré sur 1 passage : le reste tombe à 18 % de sa luminance en 0,8 s, l'élément
        // est grossi). Tout le cadre s'assombrit, pas seulement le panneau : sinon le panneau devient une
        // dalle sombre sur un fond clair. L'élément isolé monte au centre de la zone image et grossit.
        const sv = Math.max(1, Math.min((dz.img.w * 0.9) / r.w, (dz.img.h * 0.62) / r.h, 2.6, sDef));
        const dx = dz.img.cx - (r.x + r.w / 2), dy = dz.img.cy - (r.y + r.h / 2);
        css += `#${P}-voile-p { position: absolute; left: ${r1(-Pn.x)}px; top: ${r1(-Pn.y)}px; width: ${fmt.W}px; height: ${fmt.H}px; background: ${melange(theme.couleurs.fond_sombre, '#000000', 0.35)}; opacity: 0; }`;
        html = html.replace(`<div id="${P}-net" class="cp"></div>`, `<div id="${P}-voile-p" data-layout-allow-overflow></div><div id="${P}-net" class="cp"></div>`);
        js += `tl.set("#${P}-net", { clipPath: "${inset}", transformOrigin: "${r1(zr.x * k + zr.w * k / 2)}px ${r1(zr.y * k + zr.h * k / 2)}px" }, ${a(0)});
tl.fromTo("#${P}-base", { filter: "blur(0px)" }, { filter: "blur(8px)", duration: 0.8, ease: "power2.inOut" }, ${a(tz)});
tl.fromTo("#${P}-voile-p", { opacity: 0 }, { opacity: 0.8, duration: 0.8, ease: "power2.inOut" }, ${a(tz)});
tl.fromTo("#${P}-net", { x: 0, y: 0, scale: 1, filter: "drop-shadow(0px 0px 0px rgba(0,0,0,0))" }, { x: ${r1(dx)}, y: ${r1(dy)}, scale: ${r2(sv)}, filter: "drop-shadow(0px ${Math.round(fmt.H * 0.015)}px ${Math.round(fmt.H * 0.04)}px rgba(0,0,0,0.45))", duration: 1.0, ease: "power3.inOut" }, ${a(tz)});\n`;
        if (avecLib && !cf.sombre) js += `tl.to("#${P}-lib-e0", { color: "${theme.couleurs.texte_sur_sombre}", duration: 0.8, ease: "power2.inOut" }, ${a(tz)});\n`;
        if (sv < 1.15) signaler(`${ctx.plan.id} (${fmt.tag}) : l'élément éclairé grossit à peine (×${r2(sv)}) — ${sDef < 1.3 ? 'capture trop petite : la fournir en ×2' : 'zone déjà grande : la resserrer (mouvement.detail.zone)'}`);
      } else {
        const part = fmt.tag === '16x9' ? (avecLib ? 0.45 : 0.55) : fmt.tag === '9x16' ? 0.8 : 0.7;
        const sZone = Math.min((fmt.W * part) / r.w, (fmt.H * 0.8) / r.h);
        const s = Math.max(1, Math.min(sZone, sDef));
        const cx = avecLib && fmt.tag === '16x9' ? dz.img.cx : fmt.W / 2;
        const cy = dz.img.cy;
        // Le reste de l'écran se floute et s'efface vers le fond (« le reste flou », 6/12) : le libellé
        // garde une zone calme, même quand le panneau grossi passe derrière lui.
        js += `tl.set("#${P}-net", { clipPath: "${inset}" }, ${a(0)});
tl.fromTo("#${P}-cam", { x: 0, y: 0, scale: 1 }, { x: ${r1(cx - (r.x + r.w / 2) * s)}, y: ${r1(cy - (r.y + r.h / 2) * s)}, scale: ${r2(s)}, duration: 1.2, ease: "power3.inOut" }, ${a(tz)});
tl.fromTo("#${P}-base", { filter: "blur(0px)", opacity: 1 }, { filter: "blur(10px)", opacity: 0.3, duration: 1.0, ease: "power2.inOut" }, ${a(tz + 0.2)});\n`;
        if (s < 1.15) signaler(`${ctx.plan.id} (${fmt.tag}) : zoom limité à ×${r2(s)} — ${sDef <= sZone ? 'capture trop petite : la fournir en ×2' : 'zone trop large pour entrer dedans : la resserrer (mouvement.detail.zone)'}`);
      }
      // après l'entrée dans le détail, la caméra continue de glisser : jamais d'image figée
      js += `tl.fromTo("#${P}-pousse", { scale: 1 }, { scale: 1.03, duration: ${r2(D)}, ease: "none" }, ${a(0)});\n`;
    } else {
      js += `tl.fromTo("#${P}-pousse", { scale: 1 }, { scale: 1.05, duration: ${r2(D)}, ease: "none" }, ${a(0)});\n`;
    }
    const lib = libelle(ctx, dz.lib, cf.texte, ctx.t0 + tEntree + 0.4, ctx.t0 + D);
    return { fond: fondDegrade(theme, fond), css: css + lib.css, html: html + lib.html, js: js + lib.js };
  },

  // ---- empilement de fenêtres qui arrivent de la profondeur (UI R9, 3/12) ----
  empilement(ctx) {
    const { P, fmt, D, theme } = ctx; const a = (t) => r2(ctx.t0 + t);
    const vis = ctx.plan.visuels || {};
    const chemins = (vis.captures && vis.captures.length ? vis.captures : [null, null, null]).slice(0, 5);
    const caps = chemins.map((c) => ctx.assets.visuel(c, 'capture', ctx.plan.id));
    const fond = ctx.plan.fond || 'clair';
    const cf = couleursFond(theme, fond);
    const avecLib = !!(ctx.plan.texte && ctx.plan.texte.contenu);
    const dz = dispo(fmt, avecLib, false);
    const n = caps.length;
    const pas = fmt.tag === '9x16' ? { x: fmt.W * 0.03, y: fmt.H * 0.075 } : fmt.tag === '1x1' ? { x: fmt.W * 0.04, y: fmt.H * 0.06 } : { x: fmt.W * 0.04, y: fmt.H * 0.05 };
    const largeur = fmt.tag === '9x16' ? fmt.W * 0.8 : fmt.tag === '1x1' ? fmt.W * 0.66 : (avecLib ? fmt.W * 0.44 : fmt.W * 0.5);
    const hMax = (dz.img.h - pas.y * (n - 1)) * 0.98;
    const tailles = caps.map((c) => contenir(largeur, hMax, c.w, c.h));
    const totW = tailles[0].w + pas.x * (n - 1), totH = Math.max(...tailles.map((t, i) => t.h + pas.y * i));
    const x0 = dz.img.cx - totW / 2, y0 = dz.img.cy - totH / 2;
    const rayon = Math.round(14 * fmt.H / 1080);
    let css = `#${P}-scene3d { position: absolute; left: 0; top: 0; width: ${fmt.W}px; height: ${fmt.H}px; perspective: 1800px; }
      #${P}-cam { position: absolute; left: 0; top: 0; width: ${fmt.W}px; height: ${fmt.H}px; transform-origin: ${r1(dz.img.cx)}px ${r1(dz.img.cy)}px; }
      #${P}-cam .fen { position: absolute; border-radius: ${rayon}px; overflow: hidden; background-position: 0 0; background-size: 100% 100%; background-repeat: no-repeat;
        box-shadow: ${cf.sombre ? '0 0 0 1px rgba(255,255,255,.08), 0 22px 54px rgba(0,0,0,.45)' : `0 ${Math.round(fmt.H * 0.02)}px ${Math.round(fmt.H * 0.05)}px rgba(0,0,0,.22)`}; }`;
    let html = `<div id="${P}-scene3d"><div id="${P}-cam" data-layout-allow-overflow>`;
    let js = '';
    const pasT = ctx.reseau ? 0.2 : 0.35; // une fenêtre toutes les 0,2 à 0,35 s (arrivée en 0,5 s : 3/12)
    caps.forEach((c, i) => {
      const t = tailles[i];
      html += `<div id="${P}-f${i}" class="fen" style="left:${r1(x0 + pas.x * i)}px; top:${r1(y0 + pas.y * i)}px; width:${r1(t.w)}px; height:${r1(t.h)}px; background-image:url('${c.url}')"></div>`;
      js += `tl.fromTo("#${P}-f${i}", { z: -600, y: ${r1(fmt.H * 0.08)}, opacity: 0, filter: "blur(12px)" }, { z: 0, y: 0, opacity: 1, filter: "blur(0px)", duration: 0.5, ease: "power3.out" }, ${a((ctx.reseau && ctx.premier ? 0 : 0.3) + i * pasT)});\n`;
    });
    html += `</div></div>`;
    const tFin = (ctx.reseau && ctx.premier ? 0 : 0.3) + n * pasT + 0.2;
    const avecNom = !!ctx.plan._avecNom;
    const tNom = avecNom ? Math.max(tFin + 0.4, D - 3.0) : D; // l'ensemble tient 0,4 s au moins, puis le nom
    if (ctx.plan.role === 'revelation') {
      // Plan d'ensemble qui tient lieu de révélation (convention) : recul lent qui freine pendant tout le
      // plan (recul 6/14 films d'objet) et halo doux aux couleurs d'accent derrière les écrans (3/14).
      const acc = theme.couleurs.accent, acc2 = theme.couleurs.accent_2;
      css += `#${P}-halo { position: absolute; left: ${r1(dz.img.cx - totW * 0.72)}px; top: ${r1(dz.img.cy - totH * 0.7)}px; width: ${r1(totW * 1.44)}px; height: ${r1(totH * 1.4)}px; border-radius: 50%;
        background: radial-gradient(closest-side at 40% 55%, ${rgba(acc, 0.9)}, ${rgba(acc, 0)}), radial-gradient(closest-side at 64% 42%, ${rgba(acc2, 0.75)}, ${rgba(acc2, 0)}); filter: blur(${Math.round(fmt.H * 0.06)}px); opacity: 0; }`;
      html = `<div id="${P}-monde" style="position:absolute;left:0;top:0;width:${fmt.W}px;height:${fmt.H}px" data-layout-allow-overflow><div id="${P}-halo" data-layout-allow-overflow></div>${html}</div>`;
      js += `tl.fromTo("#${P}-cam", { scale: 1.08 }, { scale: 1, duration: ${r2(Math.max(1.5, tNom))}, ease: "power2.out" }, ${a(0)});
tl.fromTo("#${P}-halo", { opacity: 0, scale: 0.85 }, { opacity: 0.42, scale: 1, duration: 1.4, ease: "power2.out" }, ${a(Math.min(tFin, Math.max(0, tNom - 1.4)))});\n`;
    } else {
      html = `<div id="${P}-monde" style="position:absolute;left:0;top:0;width:${fmt.W}px;height:${fmt.H}px" data-layout-allow-overflow>${html}</div>`;
      js += `tl.fromTo("#${P}-cam", { scale: 1 }, { scale: 1.04, duration: ${r2(Math.max(0.5, D - tFin))}, ease: "none" }, ${a(Math.min(tFin, D - 0.5))});\n`;
    }
    if (avecNom) {
      const nm = nomApres(ctx, `${P}-monde`, tNom, cf.texte);
      return { fond: fondDegrade(theme, fond), css: css + nm.css, html: html + nm.html, js: js + nm.js };
    }
    const lib = libelle(ctx, dz.lib, cf.texte, ctx.t0 + 0.6, ctx.t0 + D);
    return { fond: fondDegrade(theme, fond), css: css + lib.css, html: html + lib.html, js: js + lib.js };
  },

  // ---- carton typographique : phrase, mot, chiffre (grammaire-film.md § 6) ----
  carton(ctx) {
    const { P, fmt, D, theme } = ctx;
    const t = ctx.plan.texte || { type: 'phrase', contenu: '[À FOURNIR]' };
    const fond = ctx.plan.fond || 'sombre';
    const cf = couleursFond(theme, fond);
    const ent = ctx.reseau && ctx.premier ? 0.15 : 0.35; // lisible à 0,2 s en ouverture réseau
    const debut = ctx.t0 + (ctx.reseau && ctx.premier ? 0 : 0.15);
    const fin = ctx.t0 + D;
    if (t.type === 'chiffre') {
      const fourni = t.chiffre != null && String(t.chiffre).trim() !== '';
      const valeur = fourni ? String(t.chiffre) : '[À FOURNIR]';
      const k = LARGEUR_CAR.gras + 0.02;
      let taille = fmt.tailles.chiffre;
      const largeMax = fmt.tag === '9x16' ? fmt.W * 0.7 : fmt.ligneMax;
      if (valeur.length * k * taille > largeMax) taille = Math.floor(largeMax / (valeur.length * k));
      const couleurChiffre = fourni && contraste(theme.couleurs.accent, cf.bg) >= 3 ? theme.couleurs.accent : cf.texte;
      const tl2 = preparerTexte({ texte: t.libelle || '', affichage: 'bloc', taille: fmt.tailles.chiffreLibelle, gras: false, carMax: fmt.carMax, ligneMax: fmt.ligneMax });
      const lhC = Math.round(taille * 1.05);
      const lhL = Math.round(tl2.taille * INTERLIGNE);
      const ecart = Math.round(fmt.H * 0.035);
      const hTot = lhC + ecart + lhL * tl2.lignes.length;
      const yC = fmt.cy - hTot / 2;
      const css = `#${P}-chiffre { position: absolute; left: 0; top: ${r1(yC)}px; width: ${fmt.W}px; height: ${lhC}px; line-height: ${lhC}px; text-align: center; white-space: nowrap;
          font-family: ${familleCSS(theme.polices.titres)}; font-weight: ${theme.polices.titres.graisse}; font-size: ${taille}px; letter-spacing: -0.03em; color: ${couleurChiffre}; opacity: 0; }
        #${P}-chiffre.manque { color: ${cf.texte}; }
        #${P}-lib-chiffre { position: absolute; left: ${r1((fmt.W - fmt.ligneMax) / 2)}px; top: ${r1(yC + lhC + ecart)}px; width: ${fmt.ligneMax}px; text-align: center;
          font-family: ${familleCSS(theme.polices.texte)}; font-weight: ${theme.polices.texte.graisse}; font-size: ${tl2.taille}px; line-height: ${lhL}px; color: ${cf.texte}; opacity: 0; }
        #${P}-lib-chiffre div { white-space: nowrap; }`;
      const html = `<div id="${P}-chiffre"${fourni ? '' : ' class="manque"'}>${esc(valeur)}</div><div id="${P}-lib-chiffre">${tl2.lignes.map((l) => `<div>${esc(l.map((j) => j.texte).join(' '))}</div>`).join('')}</div>`;
      const opC = fourni ? 1 : 0.38; // [À FOURNIR] estompé
      let js = `tl.fromTo("#${P}-chiffre", { opacity: 0, scale: 0.98 }, { opacity: ${opC}, scale: 1, duration: 0.45, ease: "power2.out" }, ${r2(debut)});
tl.fromTo("#${P}-lib-chiffre", { opacity: 0 }, { opacity: 1, duration: 0.4, ease: "power1.out" }, ${r2(debut + 0.5)});
tl.to(["#${P}-chiffre", "#${P}-lib-chiffre"], { opacity: 0, duration: 0.35, ease: "power1.in" }, ${r2(fin - 0.4)});\n`;
      if (!fourni) signaler(`${ctx.plan.id} : chiffre non fourni → [À FOURNIR] estompé à l'écran`);
      ctx.textes.push({ type: 'chiffre', contenu: `${valeur} ${t.libelle || ''}`.trim(), lignes: 1 + tl2.lignes.length, taille });
      return { fond: couleursFond(theme, fond).bg, css, html, js };
    }
    const estMot = t.type === 'mot';
    const pol = estMot ? theme.polices.titres : theme.polices.texte;
    const prep = preparerTexte({ texte: t.contenu || '', groupes: t.groupes, affichage: estMot ? 'bloc' : t.affichage,
      taille: estMot ? fmt.tailles.mot : fmt.tailles.carton, gras: estMot, carMax: estMot ? Math.floor(fmt.ligneMax / (LARGEUR_CAR.gras * fmt.tailles.mot)) : fmt.carMax,
      ligneMax: fmt.ligneMax, forcerLigneParGroupe: fmt.tag === '9x16' });
    if (prep.deborde) signaler(`${ctx.plan.id} (${fmt.tag}) : un mot ne tient pas dans la ligne, même réduit`);
    const id = `${P}-txt`;
    const h = htmlTexte(id, prep, { cx: fmt.W / 2, cy: fmt.cy, largeur: fmt.ligneMax, famille: familleCSS(pol), graisse: pol.graisse, couleur: cf.texte });
    const j = jsTexte(id, prep, debut, fin, { entree: ent });
    let js = j.js;
    let css = h.css, html = h.html;
    if (ctx.plan._fondImage && ctx.reseau && ctx.premier) {
      // ouverture d'une déclinaison : le produit derrière le carton, flouté (≈ 22 px à 1080) et voilé
      // par le fond du carton (80 %) ; recul lent dès la première image (mouvement dans la 1re seconde)
      const v = ctx.assets.visuel(ctx.plan._fondImage, 'image', ctx.plan.id, true);
      const flou = Math.round(Math.min(fmt.W, fmt.H) * 0.02); // un champ de couleur du produit, pas des formes lisibles
      css = `#${P}-fimg { position: absolute; left: ${-flou * 3}px; top: ${-flou * 3}px; width: ${fmt.W + flou * 6}px; height: ${fmt.H + flou * 6}px; background: url("${v.url}") center / ${v.alpha ? 'contain' : 'cover'} no-repeat; filter: blur(${flou}px); transform-origin: 50% 50%; }
      #${P}-fveil { position: absolute; left: 0; top: 0; width: ${fmt.W}px; height: ${fmt.H}px; background: ${cf.bg}; opacity: 0.8; }
      ${css}`;
      html = `<div id="${P}-fimg" data-layout-allow-overflow></div><div id="${P}-fveil"></div>${html}`;
      js = `tl.fromTo("#${P}-fimg", { scale: 1.12 }, { scale: 1, duration: ${r2(D)}, ease: "power1.out" }, ${r2(ctx.t0)});\n` + js;
    }
    if (estMot) js += `tl.fromTo("#${id}-e0", { scale: 1 }, { scale: 1.03, duration: ${r2(D)}, ease: "none" }, ${r2(ctx.t0)});\n`;
    ctx.textes.push({ type: t.type, contenu: t.contenu, lignes: prep.lignes.length, taille: prep.taille, etapes: prep.etapes, finConstruction: r2(j.finConstruction - ctx.t0) });
    return { fond: cf.bg, css, html, js };
  },

  // ---- mot posé sur l'image, dans sa zone calme (X02 ; texte § 1.6 ; R7) ----
  'mot-sur-image'(ctx) {
    const { P, fmt, D, theme } = ctx; const a = (t) => r2(ctx.t0 + t);
    const m = ctx.plan.mouvement || {};
    const v = ctx.assets.visuel((ctx.plan.visuels || {}).image, 'image', ctx.plan.id);
    const t = ctx.plan.texte || { type: 'mot', contenu: '[À FOURNIR]' };
    const clair = ctx.plan.fond === 'clair';
    const coul = clair ? theme.couleurs.texte_sur_clair : theme.couleurs.texte_sur_sombre;
    const { W, H } = fmt;
    const s = fmt.sure;
    // image : plein cadre recadré sur le point donné ; sans point en 9:16, bande centrale + texte au-dessus (§ 3.3)
    let img; let bande = false;
    if (fmt.tag === '16x9' || m.point) { const g = couvrir(W, H, v.w, v.h); const pt = m.point || [50, 50]; img = { w: g.w, h: g.h, x: Math.min(0, Math.max(W - g.w, W / 2 - g.w * pt[0] / 100)), y: Math.min(0, Math.max(H - g.h, H / 2 - g.h * pt[1] / 100)) }; }
    else if (fmt.tag === '1x1') { const g = couvrir(W, H, v.w, v.h); img = { w: g.w, h: g.h, x: (W - g.w) / 2, y: (H - g.h) / 2 }; }
    else { const hB = W * v.h / v.w; img = { w: W, h: hB, x: 0, y: H * 0.56 - hB / 2 }; bande = true; }
    let zone = m.zone || 'centre';
    if (fmt.tag !== '16x9' && (zone === 'gauche' || zone === 'droite')) zone = 'haut';
    if (bande) zone = 'haut';
    const pos = {
      centre: { cx: W / 2, cy: fmt.cy },
      haut: { cx: W / 2, cy: bande ? Math.max(s.y0 + 120, (img.y + s.y0) / 2) : s.y0 + (s.y1 - s.y0) * 0.16 },
      bas: { cx: W / 2, cy: s.y1 - (s.y1 - s.y0) * 0.14 },
      gauche: { cx: s.x0 + (s.x1 - s.x0) * 0.27, cy: fmt.cy },
      droite: { cx: s.x1 - (s.x1 - s.x0) * 0.27, cy: fmt.cy },
    }[zone] || { cx: W / 2, cy: fmt.cy };
    const estMot = t.type === 'mot';
    const pol = estMot ? theme.polices.titres : theme.polices.texte;
    const largeur = zone === 'gauche' || zone === 'droite' ? (s.x1 - s.x0) * 0.5 : fmt.ligneMax;
    const taille = estMot ? fmt.tailles.mot : Math.round(fmt.tailles.carton * 1.15);
    const prep = preparerTexte({ texte: t.contenu || '', groupes: t.groupes, affichage: estMot ? 'bloc' : t.affichage, taille, gras: estMot,
      carMax: Math.floor(largeur / ((estMot ? LARGEUR_CAR.gras : LARGEUR_CAR.regular) * taille)), ligneMax: largeur, forcerLigneParGroupe: fmt.tag === '9x16' });
    const id = `${P}-txt`;
    const h = htmlTexte(id, prep, { cx: pos.cx, cy: pos.cy, largeur, famille: familleCSS(pol), graisse: pol.graisse, couleur: coul });
    // voile local doux (10–20 %), jamais de boîte (R7)
    const voileC = clair ? 'rgba(255,255,255,.22)' : 'rgba(0,0,0,.30)';
    const css = `#${P}-img { position: absolute; left: ${r1(img.x)}px; top: ${r1(img.y)}px; width: ${r1(img.w)}px; height: ${r1(img.h)}px; background: url("${v.url}") center / 100% 100% no-repeat; transform-origin: 50% 50%; }
      #${P}-calme { position: absolute; left: ${r1(pos.cx - largeur * 0.75)}px; top: ${r1(pos.cy - h.hBloc * 1.6 - 60)}px; width: ${r1(largeur * 1.5)}px; height: ${r1(h.hBloc * 3.2 + 120)}px; background: radial-gradient(closest-side, ${voileC}, rgba(0,0,0,0)); }
      ${h.css}`;
    const html = `<div id="${P}-img" data-layout-allow-overflow></div><div id="${P}-calme" data-layout-allow-overflow></div>${h.html}`;
    const premier = ctx.reseau && ctx.premier;
    let js = `tl.fromTo("#${P}-img", { scale: 1 }, { scale: 1.06, duration: ${r2(D)}, ease: "none" }, ${a(0)});\n`;
    js += jsTexte(id, prep, ctx.t0 + (premier ? 0 : 0.4), ctx.t0 + D, { entree: premier ? 0.15 : 0.4 }).js;
    ctx.textes.push({ type: t.type, contenu: t.contenu, lignes: prep.lignes.length, taille: prep.taille, etapes: prep.etapes });
    return { fond: theme.couleurs.fond_sombre, css, html, js };
  },

  // ---- mur d'icônes ou de visuels : grille + projecteur, ou défilé (UI R14, R3) ----
  mur(ctx) {
    const { P, fmt, D, theme } = ctx; const a = (t) => r2(ctx.t0 + t);
    const m = ctx.plan.mouvement || {};
    const vis = ctx.plan.visuels || {};
    const chemins = vis.elements && vis.elements.length ? vis.elements : Array.from({ length: 8 }, () => null);
    if (!(vis.elements && vis.elements.length)) signaler(`${ctx.plan.id} : aucun élément fourni → 8 tuiles neutres dessinées`);
    const els = chemins.map((c) => ctx.assets.visuel(c, 'element', ctx.plan.id, !c));
    const n = els.length;
    const fond = ctx.plan.fond || 'sombre';
    const cf = couleursFond(theme, fond);
    if (m.mode === 'defile') {
      const pas = 0.5;
      const cote = fmt.H * (fmt.tag === '16x9' ? 0.3 : fmt.tag === '9x16' ? 0.2 : 0.32);
      let css = `#${P}-scene .el { position: absolute; left: ${r1(fmt.W / 2 - cote / 2)}px; top: ${r1(fmt.cy - cote / 2)}px; width: ${r1(cote)}px; height: ${r1(cote)}px; background-position: center; background-size: contain; background-repeat: no-repeat; opacity: 0; }
        #${P}-alt { position: absolute; left: 0; top: 0; width: ${fmt.W}px; height: ${fmt.H}px; background: ${theme.couleurs.fond_clair}; opacity: 0; }`;
      let html = `<div id="${P}-alt"></div>`;
      let js = '';
      els.forEach((e, i) => {
        html += `<div id="${P}-e${i}" class="el" style="background-image:url('${e.url}')"></div>`;
        const t = Math.min(i * pas, D - 0.3);
        js += `tl.set("#${P}-e${i}", { opacity: 1 }, ${a(t)});\n`;
        if (i < n - 1) js += `tl.set("#${P}-e${i}", { opacity: 0 }, ${a(Math.min((i + 1) * pas, D - 0.3))});\n`;
        js += `tl.set("#${P}-alt", { opacity: ${i % 2} }, ${a(t)});\n`; // fond alterné (F7)
      });
      return { fond: cf.bg, css, html, js };
    }
    // grille (dans la zone image quand un libellé occupe le côté)
    const avecLib = !!(ctx.plan.texte && ctx.plan.texte.contenu);
    const dz = dispo(fmt, avecLib, false);
    const zone = avecLib ? { w: dz.img.w * 0.92, h: Math.min(dz.img.h, fmt.sure.y1 - fmt.sure.y0) * 0.8 }
      : { w: (fmt.sure.x1 - fmt.sure.x0), h: (fmt.sure.y1 - fmt.sure.y0) * (fmt.tag === '9x16' ? 0.8 : 0.9) };
    const gcx = avecLib ? dz.img.cx : fmt.W / 2, gcy = avecLib ? dz.img.cy : fmt.cy;
    let cols, rows;
    if (fmt.tag === '16x9') { rows = n <= 5 ? 1 : n <= 12 ? 2 : 3; cols = Math.ceil(n / rows); }
    else if (fmt.tag === '9x16') { cols = n <= 4 ? 2 : 3; rows = Math.ceil(n / cols); }
    else { cols = Math.ceil(Math.sqrt(n)); rows = Math.ceil(n / cols); }
    const cell = Math.min(zone.w / cols, zone.h / rows);
    const cote = cell * 0.78;
    const gx = gcx - (cols * cell) / 2, gy = gcy - (rows * cell) / 2;
    let css = `#${P}-cam { position: absolute; left: 0; top: 0; width: ${fmt.W}px; height: ${fmt.H}px; transform-origin: ${r1(gcx)}px ${r1(gcy)}px; }
      #${P}-cam .el { position: absolute; width: ${r1(cote)}px; height: ${r1(cote)}px; background-position: center; background-size: contain; background-repeat: no-repeat; transform-origin: 50% 50%; }`;
    let html = `<div id="${P}-cam" data-layout-allow-overflow>`;
    let js = '';
    const focus = m.focus ? Math.min(n, Math.max(1, m.focus)) - 1 : -1;
    const centres = [];
    els.forEach((e, i) => {
      const c = i % cols, r = Math.floor(i / cols);
      const dansRang = r === rows - 1 ? n - r * cols : cols; // dernière rangée centrée
      const dx = (cols - dansRang) * cell / 2;
      const x = gx + dx + c * cell + (cell - cote) / 2, y = gy + r * cell + (cell - cote) / 2;
      centres.push({ x: x + cote / 2, y: y + cote / 2 });
      html += `<div id="${P}-e${i}" class="el" style="left:${r1(x)}px; top:${r1(y)}px; background-image:url('${e.url}')"></div>`;
      js += `tl.fromTo("#${P}-e${i}", { opacity: 0, scale: 0.9 }, { opacity: 1, scale: 1, duration: 0.5, ease: "power2.out" }, ${a((ctx.reseau && ctx.premier ? 0 : 0.2) + i * 0.08)});\n`;
    });
    html += `</div>`;
    const tPlein = 0.2 + n * 0.08 + 0.5;
    if (focus >= 0 && D - tPlein >= 2.0) {
      const tf = tPlein + 0.2;
      const autres = els.map((_, i) => i).filter((i) => i !== focus).map((i) => `"#${P}-e${i}"`).join(', ');
      const cF = centres[focus];
      const ech = Math.min(2, (fmt.tag === '16x9' ? fmt.H * 0.42 : fmt.W * 0.42) / cote);
      js += `tl.fromTo([${autres}], { filter: "brightness(1) blur(0px)" }, { filter: "brightness(0.22) blur(4px)", duration: 0.8, ease: "power2.inOut" }, ${a(tf)});
tl.set("#${P}-e${focus}", { zIndex: 2 }, ${a(tf)});
tl.to("#${P}-e${focus}", { x: ${r1(gcx - cF.x)}, y: ${r1(gcy - cF.y)}, scale: ${r2(ech)}, duration: 0.8, ease: "power2.inOut" }, ${a(tf)});\n`;
    } else {
      js += `tl.fromTo("#${P}-cam", { scale: 1 }, { scale: 1.04, duration: ${r2(Math.max(0.5, D - 0.2))}, ease: "none" }, ${a(0.2)});\n`;
    }
    const lib = libelle(ctx, dz.lib, cf.texte, ctx.t0 + 0.6, ctx.t0 + D);
    return { fond: fondDegrade(theme, fond), css: css + lib.css, html: html + lib.html, js: js + lib.js };
  },

  // ---- fin : nom seul, puis logo et ligne d'action s'ils sont fournis (R11 ; 3.5) ----
  fin(ctx) {
    const { P, fmt, D, theme } = ctx;
    const t = ctx.plan.texte || {};
    const m = ctx.plan.mouvement || {};
    const fond = ctx.plan.fond || 'sombre';
    const cf = couleursFond(theme, fond);
    const nom = t.contenu || ctx.film.meta.produit;
    const taille = m.taille === 'discret' ? fmt.tailles.nomDiscret : fmt.tailles.nomHeros;
    const prep = preparerTexte({ texte: nom, affichage: 'bloc', taille, gras: true, carMax: Math.floor(fmt.ligneMax / (LARGEUR_CAR.gras * taille)), ligneMax: fmt.ligneMax });
    const logoChemin = theme.logo ? (cf.sombre ? theme.logo.sur_sombre || theme.logo.sur_clair : theme.logo.sur_clair || theme.logo.sur_sombre) : null;
    let logo = null;
    if (logoChemin) {
      if (fs.existsSync(path.resolve(ctx.film._dir, logoChemin))) logo = ctx.assets.visuel(logoChemin, 'element', ctx.plan.id);
      else signaler(`${ctx.plan.id} : logo introuvable « ${logoChemin} » → fin sans logo (jamais de faux logo)`);
    }
    const ligne = t.ligne ? String(t.ligne) : null;
    const hLogo = logo ? Math.round(fmt.H * (fmt.tag === '9x16' ? 0.045 : 0.075)) : 0;
    const tl2 = ligne ? preparerTexte({ texte: ligne, affichage: 'bloc', taille: fmt.tailles.legende, gras: false, carMax: fmt.carMax + 8, ligneMax: fmt.ligneMax }) : null;
    const lhN = Math.round(prep.taille * INTERLIGNE) * prep.lignes.length;
    const ecart = Math.round(fmt.H * 0.045);
    const lhL = tl2 ? Math.round(tl2.taille * 1.3) * tl2.lignes.length : 0;
    const hTot = lhN + (ligne ? ecart * 0.7 + lhL : 0) + (logo ? ecart + hLogo : 0);
    const yN = fmt.cy - hTot / 2 + lhN / 2;
    const id = `${P}-nom`;
    const h = htmlTexte(id, prep, { cx: fmt.W / 2, cy: yN, largeur: fmt.ligneMax, famille: familleCSS(theme.polices.titres), graisse: theme.polices.titres.graisse, couleur: cf.texte });
    let css = h.css, html = h.html;
    let y = yN + lhN / 2;
    const premier = ctx.reseau && ctx.premier;
    const tNom = ctx.t0 + (premier ? 0 : ctx.reseau ? 0.1 : 0.3);
    let js = jsTexte(id, prep, tNom, ctx.t0 + D, { sortie: false, entree: ctx.reseau ? 0.3 : 0.5 }).js;
    if (ligne) {
      const manque = /\[À FOURNIR/.test(ligne);
      y += ecart * 0.7;
      css += `#${P}-ligne { position: absolute; left: ${r1((fmt.W - fmt.ligneMax) / 2)}px; top: ${r1(y)}px; width: ${fmt.ligneMax}px; text-align: center; font-family: ${familleCSS(theme.polices.texte)}; font-weight: ${theme.polices.texte.graisse}; font-size: ${tl2.taille}px; line-height: ${Math.round(tl2.taille * 1.3)}px; color: ${cf.texte}; opacity: 0; }
        #${P}-ligne div { white-space: nowrap; }`;
      html += `<div id="${P}-ligne">${tl2.lignes.map((l) => `<div>${esc(l.map((j) => j.texte).join(' '))}</div>`).join('')}</div>`;
      js += `tl.fromTo("#${P}-ligne", { opacity: 0 }, { opacity: ${manque ? 0.38 : 0.85}, duration: 0.4, ease: "power1.out" }, ${r2(tNom + 0.6)});\n`;
      y += lhL;
    }
    if (logo) {
      y += ecart;
      const lw = hLogo * logo.w / logo.h;
      css += `#${P}-logo { position: absolute; left: ${r1(fmt.W / 2 - lw / 2)}px; top: ${r1(y)}px; width: ${r1(lw)}px; height: ${hLogo}px; background: url("${logo.url}") center / contain no-repeat; opacity: 0; }`;
      html += `<div id="${P}-logo"></div>`;
      js += `tl.fromTo("#${P}-logo", { opacity: 0 }, { opacity: 1, duration: 0.4, ease: "power1.out" }, ${r2(tNom + (ligne ? 1.0 : 0.6))});\n`;
    }
    ctx.textes.push({ type: 'nom', contenu: nom, lignes: prep.lignes.length, taille: prep.taille });
    if (ligne) ctx.textes.push({ type: 'ligne', contenu: ligne, lignes: tl2.lignes.length, taille: tl2.taille });
    return { fond: cf.bg, css, html, js };
  },
};

// ===========================================================================
// PROJET HYPERFRAMES
// ===========================================================================
function ecrireScene(projetDir, ctx, rec, sortieNoir, finale) {
  const { P, fmt } = ctx;
  const a = (t) => r2(t);
  let trans = '';
  if (ctx.entree === 'fondu') trans += `tl.fromTo("#${P}-scene", { opacity: 0 }, { opacity: 1, duration: ${FONDU}, ease: "power1.inOut" }, 0);\n`;
  if (ctx.entree === 'noir') trans += `tl.fromTo("#${P}-voile", { opacity: 1 }, { opacity: 0, duration: ${NOIR_ENTREE}, ease: "power1.out" }, ${a(ctx.t0)});\n`;
  if (sortieNoir) trans += `tl.fromTo("#${P}-voile", { opacity: 0 }, { opacity: 1, duration: ${NOIR_SORTIE}, ease: "power1.in", immediateRender: false }, ${a(ctx.t0 + ctx.D - NOIR_SORTIE)});\n`;
  if (finale) trans += `tl.fromTo("#${P}-voile", { opacity: 0 }, { opacity: 1, duration: ${finale}, ease: "power1.in", immediateRender: false }, ${a(ctx.t0 + ctx.D - finale)});\n`;
  const html = `<!doctype html>
<html lang="${esc(ctx.film.meta.langue || 'fr')}"><head><meta charset="UTF-8" /></head><body>
<template>
  <style>
    ${ctx.assets.fontFaces}
    #root { position: absolute; inset: 0; overflow: hidden; }
    #${P}-scene { position: absolute; left: 0; top: 0; width: ${fmt.W}px; height: ${fmt.H}px; overflow: hidden; background: ${rec.fond}; }
    #${P}-voile { position: absolute; left: 0; top: 0; width: ${fmt.W}px; height: ${fmt.H}px; background: #000000; opacity: 0; }
    ${rec.css}
  </style>
  <div id="root" data-composition-id="${P}" data-width="${fmt.W}" data-height="${fmt.H}">
    <div id="${P}-scene">${rec.html}</div>
    <div id="${P}-voile"></div>
  </div>
  <script>
    (function () {
      const tl = gsap.timeline({ paused: true });
      ${rec.js.split('\n').join('\n      ')}
      ${trans.split('\n').join('\n      ')}
      window.__timelines["${P}"] = tl;
    })();
  </script>
</template>
</body></html>
`;
  fs.writeFileSync(path.join(projetDir, 'compositions', `${ctx.plan.id}.html`), html);
}

function construireProjet(film, sortie, racine) {
  const fmt = FORMATS[sortie.format];
  const projetDir = path.join(racine, 'projets', sortie.nom);
  fs.rmSync(projetDir, { recursive: true, force: true });
  fs.mkdirSync(path.join(projetDir, 'compositions'), { recursive: true });
  const assets = preparerAssets(film, projetDir);
  // musique
  let audioRel = null;
  if (film.musique) audioRel = assets.fichier(film.musique.fichier);
  if (film.musique && film.musique.caler_coupes) {
    const tmpIndex = path.join(projetDir, 'index.html');
    fs.writeFileSync(tmpIndex, `<!doctype html><html><body><div id="root" data-composition-id="film" data-width="${fmt.W}" data-height="${fmt.H}" data-duration="10"><audio id="musique" data-timeline-role="music" src="${audioRel}" data-start="0"></audio></div></body></html>`);
    calerSurTemps(sortie, grilleTemps(film, projetDir, audioRel), sortie.musiqueDebut);
  }
  // durées et débuts
  let t = 0;
  const plans = sortie.plans;
  const lignes = [];
  plans.forEach((p, i) => {
    const entree = i === 0 ? (sortie.reseau ? 'coupe' : (p.transition === 'fondu' ? 'coupe' : p.transition || 'coupe')) : (p.transition || 'coupe');
    const t0 = entree === 'fondu' ? FONDU : 0;
    const debut = t - t0;
    const D = p.duree_s;
    const suivant = plans[i + 1];
    const sortieNoir = !!(suivant && (suivant.transition || 'coupe') === 'noir');
    const derniere = i === plans.length - 1;
    const finale = derniere && !sortie.reseau ? 0.6 : 0; // fondu au noir final (film) ; réseau : pas de noir final
    const ctx = { P: `s-${p.id}`, plan: p, fmt, theme: film.theme, film, D, t0, entree, reseau: sortie.reseau, premier: i === 0, assets, textes: [] };
    const rec = RECETTES[p.recette](ctx);
    ecrireScene(projetDir, ctx, rec, sortieNoir, finale);
    lignes.push({ id: p.id, recette: p.recette, role: p.role || '', debut: r2(t), duree: r2(D), hote: { debut: r2(debut), duree: r2(D + t0) }, entree,
      texte: p.texte || null, textes: ctx.textes, notes: p.notes || '', avecNom: !!p._avecNom, fondImage: !!p._fondImage, instant: r2(t + D * (INSTANT_PLANCHE[p.recette] || 0.7)) });
    t += D;
  });
  const total = r2(t);
  // index.html
  let hotes = '';
  lignes.forEach((l, i) => {
    hotes += `      <div id="h-${l.id}" class="clip" data-composition-id="s-${l.id}" data-composition-src="compositions/${l.id}.html" data-start="${l.hote.debut}" data-duration="${l.hote.duree}" data-track-index="${i % 2}" data-width="${fmt.W}" data-height="${fmt.H}" style="z-index: ${i + 1}"></div>\n`;
  });
  let audio = '';
  let jsMain = '';
  if (audioRel) {
    const vol = film.musique.volume != null ? film.musique.volume : 0.9;
    const fs_ = film.musique.fondu_sortie_s != null ? film.musique.fondu_sortie_s : 2;
    const dF = r2(Math.min(fs_, total / 3));
    audio = `      <audio id="musique" data-timeline-role="music" src="${audioRel}" data-start="0" data-duration="${total}" data-media-start="${r2(sortie.musiqueDebut)}" data-volume="${fs_ > 0 ? 1 : vol}" data-track-index="10"></audio>\n`;
    if (fs_ > 0) jsMain = `tl.fromTo("#musique", { volume: ${vol} }, { volume: ${vol}, duration: ${r2(total - dF)}, ease: "none" }, 0);\n      tl.to("#musique", { volume: 0, duration: ${dF}, ease: "power1.in" }, ${r2(total - dF)});`;
  }
  const index = `<!doctype html>
<html lang="${esc(film.meta.langue || 'fr')}">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=${fmt.W}, height=${fmt.H}" />
    <title>${esc(film.meta.titre || film.meta.produit)} — ${esc(sortie.id)}</title>
    <script src="${GSAP_CDN}"></script>
    <style>
      body { margin: 0; background: #000000; }
      #root { position: relative; width: ${fmt.W}px; height: ${fmt.H}px; overflow: hidden; background: #000000; }
      .clip { position: absolute; left: 0; top: 0; width: ${fmt.W}px; height: ${fmt.H}px; }
    </style>
  </head>
  <body>
    <div id="root" data-composition-id="film" data-start="0" data-width="${fmt.W}" data-height="${fmt.H}" data-duration="${total}"${film.meta.fps ? ` data-fps="${film.meta.fps}"` : ''}>
${hotes}${audio}    </div>
    <script>
      const tl = gsap.timeline({ paused: true });
      ${jsMain}
      window.__timelines["film"] = tl;
    </script>
  </body>
</html>
`;
  fs.writeFileSync(path.join(projetDir, 'index.html'), index);
  fs.writeFileSync(path.join(projetDir, 'hyperframes.json'), JSON.stringify({ name: sortie.nom }, null, 2) + '\n');
  return { projetDir, total, lignes, fmt };
}

// ===========================================================================
// PLANCHE : une image par plan (snapshot HyperFrames), avec durée et texte
// ===========================================================================
function fairePlanche(film, sortie, proj, racine, controle) {
  const snapDir = path.join(proj.projetDir, '.planche');
  fs.rmSync(snapDir, { recursive: true, force: true });
  const instants = proj.lignes.map((l) => l.instant);
  console.log(`  snapshot de ${instants.length} plans…`);
  const r = run('npx', ['hyperframes', 'snapshot', proj.projetDir, '--at', instants.join(','), '--no-end', '--keep', '--describe', 'false', '--timeout', '20000', '-o', snapDir]);
  if (r.status !== 0) { console.error(r.stdout, r.stderr); throw new Error('snapshot HyperFrames en échec'); }
  const nomFichier = (t) => `at-${String(+t.toFixed(3))}s.png`; // 10 → « at-10s » (pas « at-1s »)
  const planDir = path.join(racine, 'planches', sortie.nom);
  fs.rmSync(planDir, { recursive: true, force: true });
  fs.mkdirSync(path.join(planDir, 'assets'), { recursive: true });
  const fmt = proj.fmt;
  const cols = fmt.tag === '16x9' ? 4 : fmt.tag === '9x16' ? 6 : 5;
  const W = 1920, marge = 40, gout = 24;
  const cw = (W - 2 * marge - gout * (cols - 1)) / cols;
  const ch = cw * fmt.H / fmt.W;
  const hTexte = 230;
  const rows = Math.ceil(proj.lignes.length / cols);
  const H = Math.ceil(170 + rows * (ch + hTexte + gout) + marge);
  let cells = '';
  proj.lignes.forEach((l, i) => {
    const f = nomFichier(l.instant);
    const src = path.join(snapDir, f);
    const dst = path.join(planDir, 'assets', `${String(i + 1).padStart(2, '0')}-${l.id}.png`);
    if (fs.existsSync(src)) fs.copyFileSync(src, dst); else signaler(`planche : image absente pour ${l.id} (${f})`);
    const c = i % cols, rr = Math.floor(i / cols);
    const x = marge + c * (cw + gout), y = 150 + rr * (ch + hTexte + gout);
    const tx = l.texte ? (l.texte.type === 'chiffre' ? `${l.texte.chiffre != null ? l.texte.chiffre : '[À FOURNIR]'} · ${l.texte.libelle || ''}` : (l.texte.contenu || '') + (l.texte.ligne ? ` · ${l.texte.ligne}` : '')) : (l.avecNom ? film.meta.produit : '');
    const alertes = (controle[l.id] || []).slice(0, 3);
    cells += `<div class="cell" style="left:${r1(x)}px; top:${r1(y)}px; width:${r1(cw)}px;">
      <div class="img" style="width:${r1(cw)}px; height:${r1(ch)}px; background-image:url('assets/${path.basename(dst)}')"></div>
      <div class="meta"><b>${i + 1}. ${esc(l.id)}</b> · ${esc(l.recette)}${l.role ? ' · ' + esc(l.role) : ''}</div>
      <div class="meta">${String(l.duree).replace('.', ',')} s · de ${String(l.debut).replace('.', ',')} à ${String(r2(l.debut + l.duree)).replace('.', ',')} s${l.entree !== 'coupe' ? ' · entrée : ' + esc(l.entree) : ''}</div>
      ${tx ? `<div class="tx">« ${esc(tx)} »</div>` : ''}
      ${l.notes ? `<div class="nt">${esc(l.notes)}</div>` : ''}
      ${alertes.map((a) => `<div class="al">${esc(a)}</div>`).join('')}
    </div>`;
  });
  const nbCartons = proj.lignes.filter((l) => l.textes.length).length;
  const html = `<!doctype html><html lang="fr"><head><meta charset="UTF-8" />
<script src="${GSAP_CDN}"></script>
<style>
  body { margin: 0; background: #F3F2EF; }
  #root { position: relative; width: ${W}px; height: ${H}px; overflow: hidden; background: #F3F2EF; font-family: "Inter", "Arial", sans-serif; color: #1C1D20; }
  h1 { position: absolute; left: ${marge}px; top: 34px; margin: 0; font-size: 40px; font-weight: 700; letter-spacing: -0.01em; }
  .sous { position: absolute; left: ${marge}px; top: 92px; font-size: 22px; color: #55585E; white-space: nowrap; }
  .cell { position: absolute; }
  .img { background-size: cover; background-position: center; border-radius: 6px; box-shadow: 0 0 0 1px rgba(0,0,0,.12); }
  .meta { font-size: 17px; line-height: 24px; margin-top: 6px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
  .tx { font-size: 18px; line-height: 24px; margin-top: 6px; font-weight: 700; overflow: hidden; max-height: 48px; }
  .nt { font-size: 15px; line-height: 20px; margin-top: 4px; color: #55585E; overflow: hidden; max-height: 40px; }
  .al { font-size: 15px; line-height: 20px; margin-top: 3px; color: #B3261E; overflow: hidden; white-space: nowrap; text-overflow: ellipsis; }
</style></head><body>
<div id="root" data-composition-id="planche" data-start="0" data-width="${W}" data-height="${H}" data-duration="1">
  <h1>${esc(film.meta.titre || film.meta.produit)} — ${esc(sortie.id)} (${esc(sortie.format)})</h1>
  <div class="sous">${proj.lignes.length} plans · ${String(proj.total).replace('.', ',')} s (cible ${sortie.cible} s) · ${nbCartons} plans avec texte · musique : ${film.musique ? esc(path.basename(film.musique.fichier)) : 'aucune (film muet)'} · planche à valider avant le rendu</div>
  ${cells}
</div>
<script> const tl = gsap.timeline({ paused: true }); window.__timelines["planche"] = tl; </script>
</body></html>`;
  fs.writeFileSync(path.join(planDir, 'index.html'), html);
  const out = path.join(racine, 'planches', `${sortie.nom}.png`);
  const tmp = path.join(planDir, '.snap');
  const r2_ = run('npx', ['hyperframes', 'snapshot', planDir, '--at', '0.5', '--no-end', '--keep', '--describe', 'false', '-o', tmp]);
  const png = path.join(tmp, 'at-0.5s.png');
  if (r2_.status === 0 && fs.existsSync(png)) { fs.copyFileSync(png, out); console.log('  planche : ' + out); }
  else { console.warn('  planche PNG impossible ; ouvrir ' + path.join(planDir, 'index.html')); }
  return out;
}

// ===========================================================================
// CONTRÔLE (check_film.py) et LINT
// ===========================================================================
function controler(fichier, resolu) {
  const py = path.join(__dirname, 'check_film.py');
  const r = run('python3', [py, fichier, '--resolu', resolu, '--json']);
  let res = { erreurs: [], avertissements: [], parPlan: {} };
  try { res = JSON.parse(r.stdout); } catch (e) { console.warn('  check_film.py : sortie illisible\n' + (r.stderr || r.stdout || '').slice(0, 800)); }
  return res;
}
function lint(projetDir) {
  const r = run('npx', ['hyperframes', 'lint', projetDir, '--json']);
  let j = null;
  try { j = JSON.parse(r.stdout); } catch (e) { /* format inattendu */ }
  const err = j ? (j.errors || j.findings || []).filter((f) => !f.severity || f.severity === 'error') : [];
  const warn = j ? (j.warnings || (j.findings || []).filter((f) => f.severity === 'warning')) : [];
  return { ok: r.status === 0, j, brut: (r.stdout || '') + (r.stderr || ''), err, warn };
}

// ===========================================================================
// PRINCIPAL
// ===========================================================================
function main() {
  const args = lireArgs(process.argv.slice(2));
  const film = chargerFilm(args.fichier);
  if (args.fps) film.meta.fps = args.fps;
  const racine = path.resolve(args.sortie || path.join(film._dir, `sortie-${slug(film.meta.titre || film.meta.produit)}`));
  fs.mkdirSync(racine, { recursive: true });
  let sorties = resoudreSorties(film);
  if (args.seulement) sorties = sorties.filter((s) => args.seulement.includes(s.id));
  if (!sorties.length) throw new Error('Aucune sortie à produire (vérifier --seulement et meta.formats).');

  const resolu = { sorties: [] };
  const projets = [];
  for (const s of sorties) {
    console.log(`\n▸ ${s.nom} (${s.format}, cible ${s.cible} s)`);
    const proj = construireProjet(film, s, racine);
    console.log(`  ${proj.lignes.length} plans, ${proj.total} s → ${proj.projetDir}`);
    projets.push({ s, proj });
    resolu.sorties.push({ id: s.id, nom: s.nom, format: s.format, reseau: s.reseau, cible: s.cible, total: proj.total,
      plans: proj.lignes.map((l) => ({ id: l.id, recette: l.recette, role: l.role, debut: l.debut, duree: l.duree, entree: l.entree, texte: l.texte, textes: l.textes, avecNom: l.avecNom, fondImage: l.fondImage, nCaptures: ((film.plans.find((q) => q.id === l.id) || {}).visuels || {}).captures ? film.plans.find((q) => q.id === l.id).visuels.captures.length : 0 })) });
  }
  const fResolu = path.join(racine, 'resolu.json');
  fs.writeFileSync(fResolu, JSON.stringify(resolu, null, 2));
  const ctl = controler(path.resolve(args.fichier), fResolu);
  console.log(`\nContrôle : ${ctl.erreurs.length} erreur(s), ${ctl.avertissements.length} avertissement(s)`);
  ctl.erreurs.forEach((e) => console.log('  ✗ ' + e));
  ctl.avertissements.slice(0, 40).forEach((e) => console.log('  · ' + e));

  let bloque = false;
  for (const { s, proj } of projets) {
    const l = lint(proj.projetDir);
    const nErr = l.j ? (l.j.errorCount != null ? l.j.errorCount : l.err.length) : (l.ok ? 0 : 1);
    const nWarn = l.j ? (l.j.warningCount != null ? l.j.warningCount : l.warn.length) : 0;
    console.log(`  lint ${s.nom} : ${nErr} erreur(s), ${nWarn} avertissement(s)`);
    if (nErr || (!l.j && !l.ok)) { console.log(l.brut.slice(0, 3000)); bloque = true; }
    else if (nWarn && l.j) console.log(JSON.stringify(l.j.findings || l.j.warnings || l.j, null, 0).slice(0, 1500));
  }
  if (args.planche) {
    for (const { s, proj } of projets) {
      const parPlan = (ctl.parPlan || {})[s.id] || {};
      fairePlanche(film, s, proj, racine, parPlan);
    }
  }
  if (args.rendu) {
    if ((ctl.erreurs.length || bloque) && !args.force) {
      console.error('\nRendu arrêté : corriger les erreurs ci-dessus (ou --force).');
      process.exit(1);
    }
    fs.mkdirSync(path.join(racine, 'rendus'), { recursive: true });
    for (const { s, proj } of projets) {
      if (args.check) {
        const c = run('npx', ['hyperframes', 'check', proj.projetDir]);
        console.log((c.stdout || '').split('\n').slice(-25).join('\n'));
      }
      const out = path.join(racine, 'rendus', `${s.nom}.mp4`);
      const q = { draft: 'draft', standard: 'standard', high: 'high' }[args.qualite] || 'standard';
      console.log(`\n▸ rendu ${s.nom} (${proj.total} s, qualité ${q})…`);
      const t0 = Date.now();
      const r = run('npx', ['hyperframes', 'render', proj.projetDir, '--output', out, '--quality', q, '--fps', String(film.meta.fps || 30), '--quiet'], { stdio: ['ignore', 'pipe', 'pipe'] });
      const sec = Math.round((Date.now() - t0) / 1000);
      if (r.status !== 0 || !fs.existsSync(out)) { console.error((r.stdout || '').slice(-2000), (r.stderr || '').slice(-2000)); throw new Error('Rendu en échec : ' + s.nom); }
      console.log(`  ✓ ${out} (${sec} s de calcul)`);
    }
  }
  if (avert.length) console.log(`\n${avert.length} remarque(s) du moteur (voir « ! » ci-dessus).`);
}

if (require.main === module) {
  try { main(); } catch (e) { console.error('\nErreur : ' + e.message); process.exit(1); }
}
module.exports = { RECETTES, FORMATS, LECTURE, resoudreSorties, preparerTexte, minimumPlan };
