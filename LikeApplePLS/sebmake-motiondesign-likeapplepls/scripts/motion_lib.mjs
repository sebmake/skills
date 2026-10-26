// motion_lib.mjs : bibliothèque du générateur motion.json → script .jsx (ExtendScript ES3).
// Le script produit tourne dans After Effects et dans EffectCraft (même API objet).
//
// Sources des valeurs : les quatre analyses image par image du corpus (8 keynotes, 2019-2026),
//   texte (145 instances), objets (122), interfaces (189), transitions (182).
// Chaque recette porte ses comptes (« N sur M ») ; ce qui n'est pas mesuré est marqué « convention ».
// Les distances sont en u : 1 u = 1 % du petit côté de l'image (= 1 % de la hauteur en 16:9,
//   l'unité « % H » des analyses). Les durées sont en secondes.
//
// ─────────────────────────────────────────────────────────────────────────────────────────────
// TABLE DES COURBES
// Chaque courbe est une cubic-bezier (x1, y1, x2, y2). Le script la convertit en KeyframeEase :
//   clé de départ (sortie) : influence = x1 × 100, vitesse = (y1 / x1) × (v1 − v0) / T ;
//   clé d'arrivée (entrée) : influence = (1 − x2) × 100, vitesse = ((1 − y2) / (1 − x2)) × (v1 − v0) / T.
//   Poignée nulle (x1 = y1 = 0, ou x2 = y2 = 1) : influence 0,1 et pente de l'autre poignée.
// Conversion vérifiée dans EffectCraft le 21/10 : écart ≤ 0,0002 sur la progression (opacité, position Y
//   séparée et décroissante, échelle, dépassement à vitesse négative).
// Deux familles de noms, parce que les analyses n'ont pas ajusté les mêmes tables :
//   camelCase (easeOutExpo…) = table de l'analyse « texte » (bezier de Penner) ;
//   kebab (out-expo…) = table des analyses « objets », « interfaces », « transitions ».
// La colonne `n` dit où la courbe a été retenue et sur combien d'instances.
// ─────────────────────────────────────────────────────────────────────────────────────────────
export const COURBES = {
  'lineaire':        { b: [0, 0, 1, 1],                  n: 'fondus au noir 21 sur 21 ; avancées 7 sur 11 ; pivots de slide 4 sur 5 ; parallaxes 8 sur 13 ; filets de lumière r² 0,91' },
  // CSS
  'ease':            { b: [0.25, 0.1, 0.25, 1],          n: 'nom qui remonte au-dessus d\u2019un prix 3 sur 5 ; zoom arrière d\u2019une phrase 2 sur 2 ; titre en fondu lent 2 sur 5' },
  'ease-in':         { b: [0.42, 0, 1, 1],               n: 'pivot qui accélère (variante) ; extinction' },
  'ease-out':        { b: [0, 0, 0.58, 1],               n: 'reculs 4 sur 6 (courbe groupée) ; ouverture d\u2019un éclaté 5 sur 7 ; opacité du chiffre de 2020 4 sur 6' },
  'ease-in-out':     { b: [0.42, 0, 0.58, 1],            n: 'opacité du chiffre posé (ajustement commun, 18 chiffres) ; voile d\u2019interface' },
  // table « texte » (Penner)
  'easeInOutCubic':  { b: [0.645, 0.045, 0.355, 1],      n: 'opacité des titres « fondu + montée » 4 sur 4 ; lignes de cascade 11 sur 13' },
  'easeOutExpo':     { b: [0.19, 1, 0.22, 1],            n: 'montée des titres 4 sur 4 ; échelle du chiffre posé 11 sur 18' },
  'easeInOutQuart':  { b: [0.77, 0, 0.175, 1],           n: 'montée des lignes de cascade (0,10 s) 4 lignes sur 11 ; nouvelle ligne au fil de la voix' },
  'easeInOutQuint':  { b: [0.86, 0, 0.07, 1],            n: 'montée des lignes de cascade (0,10 s) 7 lignes sur 11 ; cascade rapide (0,05 s)' },
  'easeInQuad':      { b: [0.55, 0.085, 0.68, 0.53],     n: 'chute depuis le haut 5 sur 6 (phrases et chiffres de 2020)' },
  'easeOutQuart':    { b: [0.165, 0.84, 0.44, 1],        n: 'lignes qui entrent par le bas (juin 2020), ajustement commun' },
  'easeOutBack':     { b: [0.175, 0.885, 0.32, 1.275],   n: 'chiffre qui grandit en 2020, 6 sur 6 (dépassement +5 %)' },
  'easeInOutSine':   { b: [0.445, 0.05, 0.55, 0.95],     n: 'nouveau mot dans un fondu enchaîné (1 cas)' },
  'easeInCubic':     { b: [0.55, 0.055, 0.675, 0.19],    n: 'mot qui glisse (1 cas) ; cascade rapide de 2024 7 sur 7' },
  'easeOutCubic':    { b: [0.215, 0.61, 0.355, 1],       n: 'recentrage d\u2019une ligne qui se construit (convention)' },
  // tables « objets », « interfaces », « transitions »
  'out-cubic':       { b: [0.33, 1, 0.68, 1],            n: 'entrée latérale floue 8 sur 8 (courbe groupée, erreur 0,075)' },
  'out-quad':        { b: [0.5, 1, 0.89, 1],             n: 'logo qui s\u2019allume (3 fondus « out » sur 10) ; recul qui se pose' },
  'out-quint':       { b: [0.22, 1, 0.36, 1],            n: 'défilement par geste (variante)' },
  'out-expo':        { b: [0.16, 1, 0.3, 1],             n: 'panneau latéral (1 sur 4 mesurés) ; fond qui se floute (fin en douceur 8 sur 14)' },
  'out-sine':        { b: [0.61, 1, 0.88, 1],            n: 'signe final qui apparaît (1 cas)' },
  'out-back':        { b: [0.34, 1.56, 0.64, 1],         n: 'carte qui monte avec dépassement de 6 % (1 panneau sur 4)' },
  'in-quad':         { b: [0.11, 0, 0.5, 0],             n: 'révélation et extinction qui accélèrent (variante)' },
  'in-sine':         { b: [0.12, 0, 0.39, 0],            n: 'image qui monte du noir après une coupe (v3, v4)' },
  'in-out-sine':     { b: [0.37, 0, 0.63, 1],            n: 'bascule de lumière lente 2 sur 4 ; effacement d\u2019un logo' },
  'in-out-cubic':    { b: [0.65, 0, 0.35, 1],            n: 'image qui monte du noir (v4, v7) 4 sur 14' },
  'in-out-quart':    { b: [0.76, 0, 0.24, 1],            n: 'bascule de lumière lente (1 cas)' },
  // courbes de famille, ajustées en commun sur toutes les instances d\u2019une famille
  'montage-2020':    { b: [0.36, 0, 0.25, 1],            n: 'zooms, glissades et rangées de 2019-2020 : 21 instances, erreur 0,018' },
  'montage-2024':    { b: [0.6, 0.4, 0.17, 0.95],        n: 'zooms, glissades et rangées de 2024-2026 : 56 instances, erreur 0,026' },
  'zoom-2024':       { b: [0.56, 0.32, 0.19, 0.98],      n: 'zoom dans un détail, 2024-2026 : 18 instances, erreur 0,028' },
  'zoom-sortie':     { b: [0.64, 0.47, 0.15, 0.94],      n: 'zoom qui ressort du détail : 10 instances, erreur 0,019' },
  'rangee-2024':     { b: [0.67, 0.49, 0.09, 0.88],      n: 'écrans qui s\u2019empilent, 2024-2026 : 14 instances, erreur 0,014' },
  'glissade':        { b: [0.65, 0.5, 0.15, 0.93],       n: 'plan entier qui glisse vers le suivant : 16 instances, erreur 0,030' },
  'poussee-ecran':   { b: [0.43, 0.08, 0.21, 1],         n: 'un contenu en pousse un autre, cadre fixe : 7 instances, erreur 0,019' },
  'voile':           { b: [0.44, 0.21, 0.29, 1],         n: 'fond qui s\u2019assombrit : 18 instances, erreur 0,021' },
  'voile-2024':      { b: [0.52, 0.42, 0.34, 1],         n: 'fond qui s\u2019assombrit, 2024-2026 : 9 instances, erreur 0,021' },
  'defilement':      { b: [0.36, 0, 0.25, 1],            n: 'défilement : 27 instances, erreur 0,033' },
  'defilement-2024': { b: [0.39, 0.06, 0.25, 1],         n: 'défilement de présentation, 2024-2026 : 12 instances, erreur 0,020' },
  'geste':           { b: [0.43, 0, 0.06, 0.82],         n: 'défilement lancé d\u2019un coup de doigt : 4 instances, erreur 0,019' },
};

// ─────────────────────────────────────────────────────────────────────────────────────────────
// Calcul sur les courbes (côté Node)
// ─────────────────────────────────────────────────────────────────────────────────────────────
function bz(a, b, s) { return 3 * (1 - s) * (1 - s) * s * a + 3 * (1 - s) * s * s * b + s * s * s; }
/** progression (0 → 1) de la cubic-bezier c au temps normalisé x */
export function progression(c, x) {
  const [x1, y1, x2, y2] = c;
  let lo = 0, hi = 1;
  for (let i = 0; i < 60; i++) { const m = (lo + hi) / 2; if (bz(x1, x2, m) < x) lo = m; else hi = m; }
  return bz(y1, y2, (lo + hi) / 2);
}
/** temps normalisé où la progression atteint p (premier passage) */
export function tempsA(c, p) {
  let prev = 0;
  for (let i = 1; i <= 4000; i++) { const x = i / 4000, v = progression(c, x); if (v >= p) { const v0 = progression(c, prev); return prev + (x - prev) * ((p - v0) / Math.max(v - v0, 1e-9)); } prev = x; }
  return 1;
}
/** part de T entre deux niveaux de progression (0,1–0,9 par défaut) */
export function part(c, a = 0.1, b = 0.9) { return tempsA(c, b) - tempsA(c, a); }
/** durée clé à clé T qui donne une durée mesurée entre 10 et 90 % (ou 2 et 98 % : « visible ») */
export function T_depuis(c, d, mode = '10-90') { return mode === 'visible' ? d / part(c, 0.02, 0.98) : d / part(c); }
/** traduction After Effects d'une courbe, pour la documentation (vitesses en multiple de la vitesse moyenne) */
export function easeAE(c) {
  const [x1, y1, x2, y2] = c;
  const sortie = (x1 <= 1e-6 && y1 <= 1e-6) ? { influence: 0.1, vitesse: x2 > 1e-6 ? y2 / x2 : 1 } : { influence: Math.max(0.1, x1 * 100), vitesse: y1 / Math.max(x1, 0.001) };
  const entree = (x2 >= 1 - 1e-6 && y2 >= 1 - 1e-6) ? { influence: 0.1, vitesse: x1 < 1 - 1e-6 ? (1 - y1) / (1 - x1) : 1 } : { influence: Math.max(0.1, (1 - x2) * 100), vitesse: (1 - y2) / Math.max(1 - x2, 0.001) };
  return { sortie, entree };
}

// ─────────────────────────────────────────────────────────────────────────────────────────────
// RECETTES
// Chaque recette : famille, types d'éléments admis, mouvement majeur ou non (règle « une chose à la fois »),
// époque (2019-2020, 2024-2026 ou toutes), mesure (comptes), paramètres {defaut, min, max, unite, statut}.
// statut : « mesuré » (fourchette du corpus : un réglage hors fourchette est une erreur au contrôle)
//          ou « convention » (choix de la skill : un réglage différent est permis, signalé).
// ─────────────────────────────────────────────────────────────────────────────────────────────
const M = 'mesuré', CV = 'convention';
const p = (defaut, min, max, unite, statut, note) => ({ defaut, min, max, unite, statut, note });
const TEXTES = ['titre', 'phrase', 'surtitre'];
const VISUELS = ['image', 'capture', 'icone', 'logo', 'forme'];
const TOUS = ['titre', 'phrase', 'surtitre', 'liste', 'chiffre', 'logo', 'image', 'capture', 'icone', 'forme', 'fond', 'nul-camera'];

export const RECETTES = {
  // ── commun ──
  'coupe': { famille: 'commun', types: TOUS, majeur: false, epoque: 'toutes',
    mesure: 'Déjà plein à la première image : 14 titres sur 29, 6 phrases sur 12, 4 cartons sur 16, 3 surtitres sur 13 ; produit posé ou en lévitation immobile 10 tenues sur 13.',
    params: {} },
  'avec': { famille: 'texte', types: ['surtitre', 'phrase', 'titre', 'icone'], majeur: false, epoque: 'toutes',
    mesure: 'Le surtitre arrive avec son mot : 8 sur 11 séparables, écart de 0,06 s au plus. Il reprend la recette et le début de l\u2019élément nommé dans `avec`.',
    params: { ecart: p(0, -0.06, 0.06, 's', M, 'écart au milieu du fondu, 8 sur 11') } },

  // ── texte ──
  'titre-fondu-montee': { famille: 'texte', types: ['titre', 'phrase', 'chiffre'], majeur: true, epoque: '2024-2026',
    mesure: '4 titres sur 29 (2024 ×2, 2025, 2026), identiques au centième dans 3 cas sur 4. Opacité easeInOutCubic 4 sur 4 ; montée easeOutExpo 4 sur 4.',
    params: { T_opacite: p(0.77, 0.64, 0.77, 's', M, 'clé à clé'), T_position: p(0.92, 0.92, 1.17, 's', M, 'clé à clé'),
      retard_position: p(0.30, 0.26, 0.31, 's', M, 'la montée devient visible quand l\u2019opacité atteint 20 %'),
      montee: p(15.3, 7.4, 15.5, 'u', M, 'départ sous la place finale (extrapolé)'),
      flou: p(0, 0, 0.4, 'u', CV, 'léger flou de départ (netteté 0,58 à 0,68, 3 sur 4) ; valeur non chiffrée') } },
  'titre-fondu': { famille: 'texte', types: ['titre', 'phrase', 'surtitre'], majeur: false, epoque: 'toutes',
    mesure: 'Fondu lent sur place : 5 titres sur 29 ; 10→90 % médiane 0,43 s (0,27 à 0,71) ; courbes mêlées (ease 2, easeInQuad 2, ease-in 1) : courbe « ease » retenue.',
    params: { d1090: p(0.43, 0.27, 0.71, 's', M, 'durée 10→90 % de l\u2019opacité') } },
  'titre-balayage': { famille: 'texte', types: ['titre', 'phrase'], majeur: false, epoque: '2024-2026',
    mesure: 'Le mot se dévoile de gauche à droite derrière un front à bord flou : 3 titres sur 29 (tous en 2025) ; front linéaire 2 sur 2 mesurés ; bord flou 2,8 % de la largeur d\u2019image.',
    params: { T: p(0.6, 0.33, 0.86, 's', M, 'traversée du front, linéaire (2 mesures : 0,33 et 0,86 s clé à clé)'), bord: p(2.8, 2.8, 6.3, '% L', M, 'largeur du bord flou') } },
  'phrase-zoom-arriere': { famille: 'texte', types: ['phrase', 'titre'], majeur: true, epoque: '2019-2020',
    mesure: '2 phrases sur 12 (novembre 2020) : échelle ×7,5 et ×8,1 à la première image, courbe ease 2 sur 2 ; opacité ease-in-out ; flou 4,4 et ≥ 6,7 % H au départ.',
    params: { depart: p(8, 7.5, 8.1, '×', M, 'échelle de départ'), T_echelle: p(0.42, 0.40, 0.45, 's', M, 'clé à clé'),
      d1090_opacite: p(0.35, 0.33, 0.37, 's', M, 'opacité 10→90 %'), flou: p(5, 4.4, 6.7, 'u', M, 'σ du flou de départ ; sa décroissance suit l\u2019échelle (convention)') } },
  'chute': { famille: 'texte', types: ['phrase', 'chiffre', 'titre'], majeur: true, epoque: '2019-2020',
    mesure: 'Tombe d\u2019en haut sans rebond : 6 chutes (3 phrases nov. 2020, 3 chiffres juin 2020) ; easeInQuad 5 sur 6 ; T 0,20 à 0,27 s ; aucun rebond (≤ 1,5 % H, 6 sur 6). La fumée qui suit n\u2019est pas reproduite.',
    params: { T: p(0.23, 0.20, 0.27, 's', M, 'clé à clé'), hauteur: p(68, 45, 75, 'u', M, 'départ au-dessus de la place (extrapolé)') } },
  'phrase-par-le-bas': { famille: 'texte', types: ['phrase'], majeur: true, epoque: '2019-2020',
    mesure: '1 phrase sur 12 (juin 2020) : entre d\u2019en dessous du cadre, déjà opaque, courbe ease, T 0,65 s.',
    params: { T: p(0.65, 0.6, 0.7, 's', M, '1 cas'), depart: p(58, 50, 60, 'u', M, 'départ sous la place finale') } },
  'liste-cascade': { famille: 'texte', types: ['liste'], majeur: true, epoque: '2024-2026',
    mesure: '3 listes (2024, 2025 ×2), 10 écarts de 0,093 à 0,113 s ; chaque ligne fond en easeInOutCubic (11 sur 13), qui part avec sa montée : T 1,14 s (1,00 à 1,17 ; 11 lignes ajustées depuis le départ de la montée ; 10→90 % mesuré 0,72 s, traîne comprise) ; monte de 21 à 23 % H (extrapolé), easeInOutQuint 7 lignes sur 11 (T 1,17 s) ou easeInOutQuart 4 (T 0,98 s) ; à 25 % d\u2019opacité, la ligne est encore 18 % H sous sa place (11 sur 11). Lignes de haut en bas 16 listes sur 16.',
    params: { decalage: p(0.10, 0.093, 0.113, 's', M, 'entre deux lignes'), T_opacite: p(1.14, 1.0, 1.17, 's', M, 'opacité de chaque ligne, clé à clé, partie avec la montée (11 lignes)'),
      T_position: p(1.17, 0.98, 1.17, 's', M, 'montée de chaque ligne, easeInOutQuint, clé à clé'), montee: p(21, 18, 23, 'u', M, 'départ sous la place') } },
  'liste-cascade-rapide': { famille: 'texte', types: ['liste'], majeur: true, epoque: '2024-2026',
    mesure: '2 listes (2024, 2026), 13 écarts de 0,029 à 0,066 s ; fondu 10→90 % 0,42 s (2026) et 0,56 s (2024), traîne comprise ; en easeInOutCubic, T 0,75 s (0,64 à 0,83 ; 7 lignes sur 8 de 2026) ; montée 4 % H (2026) ou aucune (2024).',
    params: { decalage: p(0.05, 0.029, 0.066, 's', M, 'entre deux lignes'), T_opacite: p(0.75, 0.64, 0.83, 's', M, 'opacité de chaque ligne, easeInOutCubic, clé à clé (7 lignes)'),
      montee: p(4, 0, 4.1, 'u', M, 'départ sous la place'), T_position: p(1.0, 1.0, 1.02, 's', M, 'easeInOutQuint, 1 cas') } },
  'liste-par-le-bas': { famille: 'texte', types: ['liste'], majeur: true, epoque: '2019-2020',
    mesure: '4 listes (juin 2020) : lignes déjà opaques qui montent depuis +31 % H (27 à 35) ; décalage 0,37 s (0,362 à 0,377, 4 écarts) ; easeOutQuart (ajustement commun, erreur 0,005), T 0,63 à 0,67 s.',
    params: { decalage: p(0.37, 0.362, 0.377, 's', M, 'entre deux lignes'), T: p(0.65, 0.63, 0.67, 's', M, 'clé à clé'), depart: p(31, 27, 35, 'u', M, 'à la première image visible') } },
  'liste-au-fil': { famille: 'texte', types: ['liste'], majeur: true, epoque: '2024-2026',
    mesure: '3 listes (2024 ×2, 2025) : une ligne quand elle est dite, écarts 1,4 à 3,6 s ; nouvelle ligne easeInOutCubic (opacité, T 1,17 s) et easeInOutQuart (montée de 14 à 17 % H, T 0,95 s) ; les lignes déjà là remontent d\u2019une demi-interligne à chaque ajout (2 listes sur 2).',
    params: { intervalle: p(2.0, 1.4, 3.6, 's', M, 'entre deux lignes (ou la liste `temps`)'), T_opacite: p(1.17, 1.1, 1.2, 's', M, '1 ligne mesurée proprement'),
      T_position: p(0.95, 0.9, 1.0, 's', M, 'montée'), montee: p(15, 14, 17, 'u', M, 'départ de la nouvelle ligne') } },
  'nom-remonte': { famille: 'texte', types: ['phrase', 'chiffre'], majeur: true, epoque: 'toutes',
    mesure: 'Sur une slide de prix, le nom remonte pour faire place au libellé et au prix qui entrent dessous : 5 sur 5 (nov. 2020 ×3, sept. 2025 ×2). Nom : ease 3 sur 5, T 0,50 s (0,45 à 0,53), +10 % H (7,4 à 10,7). Prix : fondu 10→90 % 0,30 s (0,22 à 0,41).',
    params: { T_nom: p(0.5, 0.45, 0.53, 's', M, 'clé à clé'), remontee: p(10, 7.4, 10.7, 'u', M, 'déplacement du nom'),
      d1090_opacite: p(0.30, 0.22, 0.41, 's', M, 'fondu du libellé et du prix'), montee: p(10, 6, 14, 'u', M, 'montée du libellé et du prix') } },
  'mot-remplace': { famille: 'texte', types: TEXTES, majeur: false, epoque: 'toutes',
    mesure: 'L\u2019ancien mot disparaît et le nouveau apparaît sur la même image : 3 changements sur 14 (2024, 2025 ×2). Le mot ne se transforme pas et ne roule pas (0 sur 14).',
    params: {} },
  'mot-fondu-enchaine': { famille: 'texte', types: TEXTES, majeur: false, epoque: '2024-2026',
    mesure: '1 cas (2024) : l\u2019ancien floute et s\u2019efface (10→90 % 0,50 s), le nouveau apparaît (0,47 s, easeInOutSine) ; milieux décalés de 0,61 s.',
    params: { d1090_ancien: p(0.50, 0.45, 0.55, 's', M, '1 cas'), d1090_nouveau: p(0.47, 0.42, 0.52, 's', M, '1 cas'), ecart: p(0.61, 0.55, 0.65, 's', M, 'entre les deux milieux'),
      flou: p(1.5, 0, 3, 'u', CV, 'flou de l\u2019ancien mot, non chiffré') } },
  'mot-glisse': { famille: 'texte', types: TEXTES, majeur: false, epoque: '2019-2020',
    mesure: '1 cas (nov. 2020) : l\u2019ancien monte en s\u2019effaçant (0,22 s, ease-in), le nouveau arrive dessous (0,20 s, easeInCubic) ; décalés de 0,16 s.',
    params: { d1090_ancien: p(0.22, 0.2, 0.25, 's', M, '1 cas'), d1090_nouveau: p(0.20, 0.18, 0.23, 's', M, '1 cas'), ecart: p(0.16, 0.14, 0.18, 's', M, '1 cas'),
      glisse: p(6, 3, 10, 'u', CV, 'amplitude du glissement, non chiffrée') } },
  'chiffre-pose': { famille: 'texte', types: ['chiffre', 'titre'], majeur: true, epoque: '2024-2026',
    mesure: '18 chiffres sur 27 (nov. 2020 2, sept. 2025 14, sept. 2026 2) : naît trop grand et flou puis se pose sans dépasser (18 sur 18). Échelle easeOutExpo 11 sur 18, T 0,67 s ; opacité 10→90 % 0,20 s (ease-in-out) ; libellé +0,23 s du milieu du fondu du chiffre au milieu du sien (15 sur 18), fondu 10→90 % 0,27 s, ease-in-out 15 sur 15 (mesure passe-haut, que le chiffre flou ne trouble pas). Le chiffre ne compte jamais (0 sur 27).',
    params: { depart: p(4.1, 1.9, 8.0, '×', M, 'échelle de départ (extrapolée ; ×3,4 à la première image)'), T_echelle: p(0.67, 0.25, 0.80, 's', M, 'clé à clé'),
      d1090_opacite: p(0.20, 0.18, 0.62, 's', M, 'opacité 10→90 %'), flou: p(6.7, 1.1, 6.7, 'u', M, 'σ du flou à la première image (borne de la mesure) ; décroît avec le zoom (courbe : convention)'),
      retard_libelle: p(0.23, 0.19, 0.30, 's', M, 'du milieu du fondu du chiffre au milieu de celui du libellé'), d1090_libelle: p(0.27, 0.26, 0.27, 's', M, 'fondu du libellé, ease-in-out 15 sur 15') } },
  'chiffre-croissance': { famille: 'texte', types: ['chiffre'], majeur: true, epoque: '2019-2020',
    mesure: '6 chiffres sur 27 (juin 2020) : grandit depuis ×0,22 (0,19 à 0,37), dépasse de 5 % puis revient (6 sur 6), easeOutBack, T 0,83 s (0,72 à 0,88) ; opacité 10→90 % 0,22 s (ease-out 4 sur 6) ; libellé +0,26 s, fondu 0,11 s.',
    params: { depart: p(0.22, 0.19, 0.37, '×', M, 'échelle de départ'), T_echelle: p(0.83, 0.72, 0.88, 's', M, 'clé à clé'), d1090_opacite: p(0.22, 0.20, 0.24, 's', M, 'opacité 10→90 %'),
      retard_libelle: p(0.26, 0.16, 0.29, 's', M, 'du milieu du fondu du chiffre au milieu de celui du libellé'), d1090_libelle: p(0.11, 0.1, 0.15, 's', M, 'fondu du libellé') } },
  'carton-fondu': { famille: 'texte', types: ['titre', 'phrase'], majeur: false, epoque: 'toutes',
    mesure: 'Carton de film : fond sans bouger, 7 fondus sur 7 ; 10→90 % 0,45 s (0,31 à 0,78) ; linéaire 3 sur 7.',
    params: { d1090: p(0.45, 0.31, 0.78, 's', M, 'opacité 10→90 %') } },
  'carton-groupes': { famille: 'texte', types: ['phrase'], majeur: false, epoque: 'toutes',
    mesure: 'La phrase se construit par groupes de sens (2 à 4 mots), jamais mot à mot : 3 cartons (2019, 2025, 2026) ; écarts 0,6 à 2,5 s ; chaque groupe fond comme un carton ; la ligne se recentre à chaque ajout (vu, non chiffré).',
    params: { ecart: p(0.75, 0.6, 2.5, 's', M, 'entre deux groupes (0,61 / 0,77 / 0,85 s en 2025-2026)'), d1090: p(0.45, 0.31, 0.78, 's', M, 'fondu de chaque groupe'),
      T_recentrage: p(0.3, 0.2, 0.5, 's', CV, 'recentrage de la ligne, easeOutCubic') } },

  // ── objets ──
  'produit-entree': { famille: 'objet', types: VISUELS, majeur: true, epoque: '2024-2026',
    mesure: 'Le produit arrive par la droite sur la coupe (7 sur 7 à ± 0,1 s), freine et se pose : 9 entrées ; freine 8 sur 8, courbe out-cubic (erreur 0,075) ; 0→100 % 0,88 s (0,82 à 0,93) ; flou de bougé d\u2019un obturateur de 118° (74 à 169°).',
    params: { T: p(0.9, 0.82, 0.93, 's', M, 'clé à clé ≈ durée 0→100 %'), depuis: p('droite', null, null, '', M, 'droite 7 sur 7 ; gauche : convention'),
      obturateur: p(120, 74, 169, '°', M, 'angle d\u2019obturateur du flou de bougé') } },
  'produit-poussee': { famille: 'objet', types: VISUELS.concat(['nul-camera']), majeur: false, epoque: 'toutes',
    mesure: 'Avancée lente vers l\u2019objet : 11 avancées, linéaires 7 sur 11 ; ×1,27 (×1,02 à ×2,58) en 4,1 s (2,2 à 8,6). Commence avec le plan, bouge encore à la coupe (9 sur 17). Sur une slide tenue : ×1,02 à ×1,06 en 5 à 8 s (3 sur 7).',
    params: { facteur: p(1.27, 1.02, 2.58, '×', M, 'échelle de fin / début'), duree: p(4.1, 2.2, 8.6, 's', M, 'par défaut : toute la présence de l\u2019élément') } },
  'produit-recul': { famille: 'objet', types: VISUELS.concat(['nul-camera']), majeur: false, epoque: 'toutes',
    mesure: 'Recul qui freine : 6 reculs, freinent 4 sur 6 (ease-out, courbe groupée) ; ×0,45 (×0,05 à ×0,84) en 5,8 s (2,7 à 8,5).',
    params: { facteur: p(0.45, 0.05, 0.84, '×', M, 'échelle de fin / début'), duree: p(5.8, 2.7, 8.5, 's', M, 'durée 0→100 %') } },
  'produit-pivot': { famille: 'objet', types: VISUELS, majeur: true, epoque: 'toutes',
    mesure: 'Pivot du profil à la face : 4 pivots de slide sur 5 linéaires, en 1,7 à 2,6 s ; un quart de tour au plus (0 sur 7 au-delà) ; part 0,2 à 0,3 s après la coupe (2 sur 2) ; l\u2019objet finit de face (4 sur 4).',
    params: { angle: p(90, 12, 90, '°', M, 'du profil (90°) à la face (0°)'), T: p(2.0, 1.7, 2.6, 's', M, 'linéaire'), delai: p(0.25, 0.2, 0.3, 's', M, 'après la coupe') } },
  'produit-rotation': { famille: 'objet', types: VISUELS, majeur: false, epoque: 'toutes',
    mesure: 'Rotation dans le plan (objet vu de dessus) : 6 instances, 83° médian (19 à 160°), linéaire 2 sur 6 ; durée 4,2 s (1,4 à 9,5). Aucun tour complet (0 sur 17).',
    params: { angle: p(83, 19, 160, '°', M, 'angle parcouru'), duree: p(4.2, 1.4, 9.5, 's', M, 'linéaire') } },
  'produit-flotte': { famille: 'objet', types: VISUELS, majeur: false, epoque: 'toutes',
    mesure: 'Le produit en lévitation ne bouge pas : moins de 0,3 % H sur 2 à 18 s dans 10 tenues sur 13 ; aucune oscillation de flottement (0 sur 14). La lévitation tient à l\u2019ombre, au reflet et à la caméra qui bouge autour.',
    params: { derive: p(0, 0, 10, 'u/s', CV, 'dérive linéaire d\u2019un objet suspendu (2 films : 1 à 10 % H/s)'), ombre: p(1, 0, 1, '', CV, 'ombre douce au sol (1 = oui)') } },
  'eclate': { famille: 'objet', types: ['image', 'forme'], majeur: true, epoque: 'toutes',
    mesure: 'Éclaté : 7 ouvertures (freinent 5 sur 7, ease-out, 0→100 % 1,9 s ; étendue ×1,5 de ×1,08 à ×4,6) ; 9 fermetures ou poses (1,2 s, de 1,1 à 2,8 ; poses de plaques linéaires 3 sur 3). Aucun rebond (1 sur 15 à 3,9 %, dans la marge).',
    params: { sens: p('ouvre', null, null, '', M, 'ouvre (ease-out) ou ferme (linéaire)'), T_ouvre: p(1.9, 0.2, 18.8, 's', M, 'ouverture'), T_ferme: p(1.2, 1.1, 2.8, 's', M, 'fermeture ou pose'),
      amplitude: p(1, 0.5, 3, '×', CV, 'multiplie les décalages des pièces'), decalage: p(0, 0, 3.15, 's', CV, 'entre deux pièces (1 cas à 3,15 s ; non mesurable ailleurs)') } },
  'balayage-lumiere': { famille: 'objet', types: VISUELS.concat(['titre']), majeur: false, epoque: '2024-2026',
    mesure: 'Un filet de lumière traverse une fois, à vitesse constante : 8 filets sur une puce ou une arête, 0,28 s médian (0,10 à 1,17), largeur 31 à 32 % de l\u2019objet ; un seul passage 11 sur 11 ; vers la gauche 4, le haut 4, la droite 3, le bas 0.',
    params: { T: p(0.28, 0.10, 1.17, 's', M, 'traversée, linéaire'), largeur: p(31, 5, 32, '% objet', M, 'largeur de la bande'), sens: p('droite', null, null, '', M, 'gauche, haut ou droite ; jamais vers le bas (0 sur 11)'),
      intensite: p(45, 20, 80, '%', CV, 'opacité de la bande (mode Ajouter)'), inclinaison: p(20, 0, 35, '°', CV, 'inclinaison de la bande') } },
  'revelation-lumiere': { famille: 'objet', types: VISUELS, majeur: false, epoque: 'toutes',
    mesure: 'Sortie du noir : 12 instances, 10→90 % 1,6 s (0,1 à 6,0), linéaire ou qui accélère 8 sur 12 ; une puce sur slide en 0,3 à 0,6 s, 0,2 à 0,4 s après la coupe (4 sur 4). Extinction : 7 instances, 10→90 % 1,0 s. Éclat qui retombe : 3 puces sur 12 (+11 à +28 %).',
    params: { d1090: p(1.6, 0.1, 6.0, 's', M, 'linéaire'), delai: p(0.3, 0.2, 0.4, 's', M, 'après la coupe (slide)'), sens: p('allume', null, null, '', M, 'allume (sortie du noir) ou eteint (extinction, 10→90 % 1,0 s)'),
      eclat: p(0, 0, 28, '%', M, 'éclat au-dessus de la valeur finale (3 sur 12, puces ; forme en 3 clés : convention)') } },

  // ── interfaces ──
  'panneau-pose': { famille: 'interface', types: ['capture', 'forme', 'image', 'icone'], majeur: true, epoque: 'toutes',
    mesure: 'Panneau qui arrive : 16 instances, visible 0,36 s (0,17 à 0,50) ; aucun au-delà de 0,5 s (16 sur 16) ; les 4 courbes mesurées finissent en douceur (out-expo d\u2019un bord, ease dans la page) ; dépassement de 6 % 1 fois sur 4 (une carte qui monte).',
    params: { visible: p(0.36, 0.17, 0.50, 's', M, 'durée 2→98 %'), distance: p(40, 15.9, 62, 'u', M, 'trajet (35 à 62 % H depuis un bord, 15,9 % H dans la page)'),
      depuis: p('bas', null, null, '', M, 'bas, haut, gauche, droite'), dans_la_page: p(0, 0, 1, '', M, '1 = glisse dans la page (courbe ease, 15,9 % H)'),
      carte: p(0, 0, 1, '', M, '1 = carte qui monte, dépassement ≤ 6 % (out-back)'), fondu: p(1, 0, 1, '', CV, 'fondu d\u2019opacité sur le premier tiers') } },
  'zoom-detail': { famille: 'interface', types: ['capture', 'image', 'nul-camera'], majeur: true, epoque: 'toutes',
    mesure: 'Zoom dans un détail : 27 instances, visible 0,67 s (0,60 à 1,00 : 27 sur 27 dans ces bornes) ; ×2,2 en entrée (×1,45 à ×3,0) ; aucun dépassement au-delà de 1,1 %, aucune rotation, aucun zoom linéaire (0 sur 27) ; maintien sur le détail 7,2 s médian.',
    params: { facteur: p(2.2, 1.45, 3.0, '×', M, 'en entrée (sortie : ×1,6 à ×8,3)'), T: p(0.95, 0.60, 1.53, 's', M, 'clé à clé'), sens: p('entre', null, null, '', M, 'entre (17) ou sort (10)'),
      point: p([50, 50], null, null, '%', CV, 'point du détail, en % de l\u2019élément') } },
  'defilement': { famille: 'interface', types: ['capture'], majeur: true, epoque: 'toutes',
    mesure: 'Défilement : 27 instances, visible 0,73 s, 59,5 % H (14 à 196), vitesse de pointe 168 % H/s (max 791) ; fin en douceur 14 sur 27 ; jamais plus de 2 hauteurs d\u2019image (27 sur 27). Geste lancé : 1,72 s (4 cas) ; continu linéaire 68 % H/s (1 cas).',
    params: { distance: p(59.5, 14, 196, 'u', M, 'trajet'), T: p(1.07, 0.94, 2.16, 's', M, 'clé à clé'), mode: p('presentation', null, null, '', M, 'presentation (S, 2024-2026), geste (lancé), continu (linéaire)'),
      fenetre: p([60, 60], null, null, 'u', CV, 'largeur et hauteur de la zone visible') } },
  'empilement': { famille: 'interface', types: ['capture'], majeur: true, epoque: 'toutes',
    mesure: 'Écrans qui s\u2019empilent en rangée : 29 instances ; chaque nouvel écran entre par le côté et pousse la rangée de 26,6 % H (23,5 à 63) en 0,66 s visibles ; les arrivées ne se chevauchent jamais (11 sur 11) ; écart 1,67 s (0,83 à 10,5) ; en S 17 sur 19 ; aucun dépassement (0 sur 19).',
    params: { intervalle: p(1.67, 0.83, 10.5, 's', M, 'entre deux arrivées (rafale : 0,85 s, 3 cas)'), T: p(0.79, 0.6, 1.0, 's', M, 'clé à clé (2024-2026 0,79 ; 2019-2020 0,96)'),
      ecart: p(4, 2, 8, 'u', CV, 'espace entre deux écrans') } },
  'assombrir-autour': { famille: 'interface', types: VISUELS.concat(TEXTES, ['chiffre', 'liste']), majeur: false, epoque: 'toutes',
    mesure: 'Un voile noir tombe sur tout sauf l\u2019élément : 20 instances, visible 0,45 s (0,12 à 0,71) ; en S 13 sur 18 ; voile 40 % médian (24 à 62 pour une interface, 33 à 73 pour un projecteur) ; jamais jusqu\u2019au noir (20 sur 20). Le fond se floute avec (σ 0,34 % H, 10 sur 14 avec un voile).',
    params: { niveau: p(40, 5, 73, '%', M, 'opacité du voile (projecteur : 65 à 70)'), T: p(0.53, 0.40, 0.60, 's', M, 'clé à clé'),
      flou: p(0, 0, 0.78, 'u', M, 'σ du flou du fond (0,34 médian ; projecteur 0,78)') } },

  // ── caméra ──
  'camera-poussee': { famille: 'camera', types: ['nul-camera'], majeur: false, epoque: 'toutes',
    mesure: 'Avancée de caméra : linéaire 7 sur 11, ×1,27 en 4,1 s ; commence moins de 0,25 s après la coupe (9 sur 17) et bouge encore à la coupe (9 sur 17).',
    params: { facteur: p(1.27, 1.02, 2.58, '×', M, 'échelle de fin / début') } },
  'camera-recul': { famille: 'camera', types: ['nul-camera'], majeur: false, epoque: 'toutes',
    mesure: 'Recul de caméra : freine 4 sur 6 (ease-out), ×0,45 en 5,8 s ; le recul qui révèle l\u2019objet entier depuis un détail dure 7,4 à 8,5 s (3 cas).',
    params: { facteur: p(0.45, 0.05, 0.84, '×', M, 'échelle de fin / début') } },
  'camera-travelling': { famille: 'camera', types: ['nul-camera'], majeur: false, epoque: 'toutes',
    mesure: 'Translation à vitesse constante : 216 plans sur 309 qui bougent ; 4,7 % H/s médian ; parallaxe : le premier plan va 1,9 fois plus vite que le fond (0,9 à 12,4), linéaire 8 sur 13.',
    params: { vitesse: p(4.7, 0.5, 48, 'u/s', M, 'vitesse du plan de référence (profondeur 1)'), direction: p([-1, 0], null, null, '', CV, 'sens du mouvement de l\u2019image') } },
  'camera-se-pose': { famille: 'camera', types: ['nul-camera'], majeur: false, epoque: 'toutes',
    mesure: 'Mouvement qui ralentit jusqu\u2019à l\u2019arrêt dans le plan : 7 sur 21 ; arrivée à vitesse nulle 7 sur 7 ; 10→90 % 2,1 à 5,2 s (médiane 4,4) ; courbe out-cubic.',
    params: { d1090: p(4.4, 2.1, 5.2, 's', M, 'durée 10→90 %'), facteur: p(0.68, 0.46, 1.0, '×', M, 'échelle de fin / début (recul qui se pose)'), deplacement: p([0, 0], null, null, 'u', CV, 'translation ajoutée') } },

  // ── fin ──
  'logo-fin': { famille: 'fin', types: ['logo', 'titre', 'image'], majeur: false, epoque: 'toutes',
    mesure: 'Nom ou logo de fin : 20 entrées, coupe 10, fondu 10 (10→90 % 0,65 s ; out 3, linéaire 2, ease 1, in 4) ; ne bouge pas (≤ 1,1 % H, 18 sur 20) ; centre vertical entre 47 et 51 % H (15 sur 20) ; tenu 2,6 s (1,25 à 4,7). Carton final de keynote : tenu 4 à 50 s.',
    params: { entree: p('fondu', null, null, '', M, 'coupe ou fondu, à parts égales'), d1090: p(0.65, 0.27, 2.0, 's', M, 'fondu, courbe out-quad') } },
};

// Transitions : un tableau à part, appliqué entre éléments (de → vers).
export const TRANSITIONS = {
  'coupe': { mesure: 'Plus de 95 % des changements d\u2019image : 1 967 coupes contre 61 fondus dans les films, 6 894 contre 82 en régie.', params: {} },
  'raccord': { mesure: 'Raccord graphique : 22 sur 22 sont des coupes ; centre déplacé de 3,2 % H (médiane), taille changée de moins de 12 % (21 sur 22).', params: {} },
  'fondu-enchaine': { mesure: 'Fondu enchaîné court et rare : 25 vérifiés, 10→90 % 0,29 s, durée totale 0,25 à 0,98 s ; aucun au-delà de 1 s ; pas de courbe dominante (linéaire retenue).',
    params: { T: p(0.54, 0.25, 0.98, 's', M, 'durée totale') } },
  'passage-noir': { mesure: 'Fondu au noir linéaire 21 sur 21 (T 0,50 s, 11 sur 21 à 15 images) ; noir tenu 0,57 s (0,40 à 1,50 ; jamais moins de 0,40 s, 25 sur 25) ; fondu depuis le noir linéaire 11 sur 16 (T 0,50 s).',
    params: { T_fondu: p(0.5, 0.33, 1.27, 's', M, 'chaque fondu'), noir: p(0.5, 0.40, 1.50, 's', M, 'noir tenu') } },
  'fondu-au-noir': { mesure: 'Fondu au noir : linéaire 21 sur 21, T 0,50 s (0,33 à 1,27).', params: { T: p(0.5, 0.33, 1.27, 's', M, 'linéaire') } },
  'fondu-depuis-noir': { mesure: 'Fondu depuis le noir : 16 instances ; courts et linéaires 11 (T 0,50 s) ; longs (0,68 à 2,71 s) freinés 5 sur 5.',
    params: { T: p(0.5, 0.34, 2.71, 's', M, 'au-delà de 0,68 s, la courbe freine (out-cubic)') } },
  'montee-du-noir': { mesure: 'Coupe au noir, noir court (0,27 s, 33 cas), puis l\u2019image monte du noir : départ doux 13 sur 14, linéaire 0 ; 10→90 % 0,39 s (0,17 à 0,74).',
    params: { noir: p(0.27, 0.1, 0.5, 's', CV, 'noir tenu : médiane 0,27 s mesurée (33 cas) ; bornes : convention'), d1090: p(0.39, 0.17, 0.74, 's', M, 'montée, courbe in-out-cubic') } },
  'glissade': { mesure: 'Le plan entier part sur le côté et le suivant entre : 16 glissades (2024-2026), 138 % H (une largeur d\u2019image ou presque), visible 0,70 s ; horizontal 32 sur 32 ; aucun dépassement ; flou de mouvement vu 10 sur 16 (intensité non mesurée).',
    params: { T: p(0.89, 0.64, 0.94, 's', M, 'clé à clé'), sens: p('gauche', null, null, '', M, 'gauche ou droite ; jamais vertical (0 sur 32)') } },
  'poussee': { mesure: 'Un contenu en pousse un autre dans un cadre fixe : 7 instances, visible 0,57 s, courbe commune (0,43 ; 0,08 ; 0,21 ; 1).',
    params: { T: p(0.75, 0.6, 1.02, 's', M, 'clé à clé'), sens: p('gauche', null, null, '', M, 'horizontal') } },
  'bascule-lumiere': { mesure: 'La lumière change dans le plan sans coupe : 12 instances ; les 4 bascules lentes (1,2 à 2,6 s) sont adoucies 4 sur 4 (in-out-sine 2) ; l\u2019objet reste allumé pendant que le fond s\u2019éteint.',
    params: { T: p(2.4, 1.2, 2.6, 's', M, 'durée totale'), niveau: p(85, 30, 100, '%', CV, 'assombrissement final du fond') } },
};

// ─────────────────────────────────────────────────────────────────────────────────────────────
// Le moteur ExtendScript (ES3) inséré en tête de chaque script généré
// Pièges respectés : comp ouverte dans la visionneuse avant toute courbe (sans quoi EffectCraft ignore
// interpolations et eases) ; clés calées sur l'image et distantes d'au moins une image ; position en
// dimensions séparées (X, Y à une dimension) ; nuls de caméra posés neutres (ancre = position) avant de
// parenter ; calques de forme dessinés autour de leur ancre ; aucune expansion de masque, aucun masque
// animé ; repli dessiné si un fichier ne s'importe pas (File.exists n'est pas fiable dans EffectCraft) ;
// aucun calque de plus de 8 000 px ; aucune commande de fichier (enregistrer, ouvrir, fermer).
// ─────────────────────────────────────────────────────────────────────────────────────────────
export const MOTEUR = String.raw`
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
`;

// ─────────────────────────────────────────────────────────────────────────────────────────────
// Génération
// ─────────────────────────────────────────────────────────────────────────────────────────────
const FORMATS = { '16:9': [1920, 1080], '9:16': [1080, 1920], '1:1': [1080, 1080] };
export const DEFAUTS = {
  couleurs: { fond: '#0E1013', texte: '#F4F4F2', secondaire: '#9A9CA3', accent: '#4C8DFF', voile: '#000000', repli: '#2A2C31', repli_trait: '#55585F', lumiere: '#FFFFFF' },
  polices: { titre: ['Inter-SemiBold', 'Inter-Bold', 'Arial-BoldMT'], texte: ['Inter-Regular', 'Inter-Medium', 'ArialMT'], chiffre: ['Inter-Bold', 'Inter-SemiBold', 'Arial-BoldMT'], surtitre: ['Inter-Medium', 'Inter-Regular', 'ArialMT'] },
  // tailles en u (1 % du petit côté) : convention, sauf le chiffre (30 à 50 % H, analyse texte P2)
  tailles: { titre: 10, phrase: 5.4, surtitre: 3.2, liste: 4.4, chiffre: 30, libelle: 3.7, logo: 12, image: 50, capture: 60, icone: 10, forme: 20 },
};
const JS = (v) => JSON.stringify(v).replace(/[\u007f-\uffff]/g, (c) => '\\u' + c.charCodeAt(0).toString(16).padStart(4, '0'));
const r3 = (x) => Math.round(x * 1000) / 1000;
const ident = (id) => 'e_' + String(id).replace(/[^A-Za-z0-9_]/g, '_');

function couleur(theme, c, defaut) {
  if (!c) return theme.couleurs[defaut];
  if (/^#[0-9A-Fa-f]{6}$/.test(c)) return c.toUpperCase();
  return theme.couleurs[c] || theme.couleurs[defaut];
}
function polices(theme, role, defaut) { const r = theme.polices[role || defaut] || theme.polices[defaut]; return Array.isArray(r) ? r : [r]; }

/** paramètres d'une recette : défauts mesurés, écrasés par options */
export function parametres(nom, options = {}, table = RECETTES) {
  const r = table[nom]; if (!r) return { ...options };
  const out = {};
  for (const [k, d] of Object.entries(r.params)) out[k] = options[k] !== undefined ? options[k] : d.defaut;
  for (const [k, v] of Object.entries(options)) if (out[k] === undefined) out[k] = v;
  return out;
}

/**
 * Plan temporel d'un élément (utilisé par le générateur et par le contrôle).
 * Renvoie { debut, finEntree, sortie, fin, mouvements: [{de, a, majeur, quoi}] }.
 */
export function planElement(el, comp, tous = {}) {
  const fps = comp.cadence || 30, FD = 1 / fps;
  const cale = (t) => Math.round(t * fps) / fps;
  let rec = el.recette || 'coupe';
  let debut = el.debut || 0;
  let opts = el.options || {}, ref = null;
  if (rec === 'avec' && el.avec && tous[el.avec]) { ref = planElement(tous[el.avec], comp, tous); debut = ref.debut + (opts.ecart || 0); rec = ref.recette; opts = { ...(tous[el.avec].options || {}), ...opts }; delete opts.ecart; }
  const o = parametres(rec, opts);
  const n = el.lignes ? el.lignes.length : (el.groupes ? el.groupes.length : (el.fichiers ? el.fichiers.length : 1));
  const epoque = comp.epoque || '2024-2026';
  let entree = 0, mouv = [];
  const M_ = (de, a, majeur, quoi) => mouv.push({ de: r3(de), a: r3(a), majeur, quoi });
  switch (rec) {
    case 'coupe': case 'mot-remplace': entree = 0; break;
    case 'titre-fondu-montee': entree = Math.max(o.T_opacite, o.retard_position + o.T_position); M_(debut + o.retard_position, debut + o.retard_position + o.T_position, true, 'montée'); break;
    case 'titre-fondu': entree = T_depuis(COURBES.ease.b, o.d1090); break;
    case 'titre-balayage': entree = o.T; break;
    case 'phrase-zoom-arriere': entree = Math.max(o.T_echelle, T_depuis(COURBES['ease-in-out'].b, o.d1090_opacite)); M_(debut, debut + o.T_echelle, true, 'zoom arrière'); break;
    case 'chute': entree = o.T; M_(debut, debut + o.T, true, 'chute'); break;
    case 'phrase-par-le-bas': entree = o.T; M_(debut, debut + o.T, true, 'entrée par le bas'); break;
    case 'liste-cascade': { const T = Math.max(o.T_opacite, o.T_position); entree = (n - 1) * o.decalage + T; M_(debut, debut + (n - 1) * o.decalage + o.T_position, true, 'cascade'); break; }
    case 'liste-cascade-rapide': { const T = Math.max(o.T_opacite, o.montee > 0 ? o.T_position : 0); entree = (n - 1) * o.decalage + T; if (o.montee > 0) M_(debut, debut + (n - 1) * o.decalage + o.T_position, true, 'cascade'); break; }
    case 'liste-par-le-bas': entree = (n - 1) * o.decalage + o.T; for (let i = 0; i < n; i++) M_(debut + i * o.decalage, debut + i * o.decalage + o.T, true, 'ligne ' + (i + 1)); break;
    case 'liste-au-fil': { const ts = tempsLignes(el, o, debut); entree = ts[ts.length - 1] - debut + Math.max(o.T_opacite, o.T_position); ts.forEach((t, i) => M_(t, t + o.T_position, true, 'ligne ' + (i + 1))); break; }
    case 'nom-remonte': entree = Math.max(o.T_nom, T_depuis(COURBES.easeInOutCubic.b, o.d1090_opacite)); M_(debut, debut + entree, true, 'le nom remonte'); break;
    case 'mot-fondu-enchaine': entree = T_depuis(COURBES.easeInOutSine.b, o.d1090_nouveau); break;
    case 'mot-glisse': entree = T_depuis(COURBES.easeInCubic.b, o.d1090_nouveau); break;
    case 'chiffre-pose': entree = Math.max(o.T_echelle, debutLibelle('ease-in-out', o.d1090_opacite, 'ease-in-out', o.retard_libelle, o.d1090_libelle) + T_depuis(COURBES['ease-in-out'].b, o.d1090_libelle)); M_(debut, debut + o.T_echelle, true, 'le chiffre se pose'); break;
    case 'chiffre-croissance': entree = Math.max(o.T_echelle, debutLibelle('ease-out', o.d1090_opacite, 'ease-out', o.retard_libelle, o.d1090_libelle) + T_depuis(COURBES['ease-out'].b, o.d1090_libelle)); M_(debut, debut + o.T_echelle, true, 'le chiffre grandit'); break;
    case 'carton-fondu': entree = T_depuis(COURBES.lineaire.b, o.d1090); break;
    case 'carton-groupes': entree = (n - 1) * o.ecart + T_depuis(COURBES.lineaire.b, o.d1090); break;
    case 'produit-entree': entree = o.T; M_(debut, debut + o.T, true, 'entrée latérale'); break;
    case 'produit-poussee': case 'produit-recul': case 'produit-rotation': case 'produit-flotte': entree = 0; break;
    case 'produit-pivot': entree = o.delai + o.T; M_(debut + o.delai, debut + o.delai + o.T, true, 'pivot'); break;
    case 'eclate': { const T = o.sens === 'ferme' ? o.T_ferme : o.T_ouvre; const k = (el.pieces || [1, 2, 3]).length; entree = T + (k - 1) * o.decalage; M_(debut, debut + entree, true, 'éclaté'); break; }
    case 'balayage-lumiere': entree = o.T; break;
    case 'revelation-lumiere': entree = o.delai + T_depuis(COURBES.lineaire.b, o.sens === 'eteint' ? Math.min(o.d1090, 1.0) : o.d1090); break;
    case 'panneau-pose': { const c = panneauCourbe(o); entree = T_depuis(COURBES[c].b, o.visible, 'visible'); M_(debut, debut + entree, true, 'panneau'); break; }
    case 'zoom-detail': entree = o.T; M_(debut, debut + o.T, true, 'zoom'); break;
    case 'defilement': { const T = o.mode === 'continu' ? (o.distance / 68) : o.T; entree = T; M_(debut, debut + T, true, 'défilement'); break; }
    case 'empilement': { const T = epoque === '2019-2020' ? Math.max(o.T, 0.96) : o.T; entree = (n - 1) * o.intervalle + (n > 1 ? T : 0); for (let i = 1; i < n; i++) M_(debut + i * o.intervalle, debut + i * o.intervalle + T, true, 'écran ' + (i + 1)); break; }
    case 'assombrir-autour': entree = o.T; break;
    case 'logo-fin': entree = o.entree === 'coupe' ? 0 : T_depuis(COURBES['out-quad'].b, o.d1090); break;
    case 'camera-poussee': case 'camera-recul': case 'camera-travelling': case 'camera-se-pose': entree = 0; break;
    default: entree = 0;
  }
  // compléments (« puis ») : leur durée compte dans la présence, pas dans l'entrée
  const finEntree = cale(debut + entree);
  let sortieDebut;
  if (el.fin !== undefined) sortieDebut = el.fin;
  else if (el.maintien !== undefined) sortieDebut = finEntree + el.maintien;
  else if (ref) sortieDebut = ref.sortieDebut;
  else sortieDebut = comp.duree;
  const sortie = el.sortie || (ref ? ref.sortie : 'coupe');
  const fin = sortie === 'fondu' ? Math.min(comp.duree, sortieDebut + 1.15) : Math.min(comp.duree, sortieDebut);
  return { recette: rec, debut: r3(cale(debut)), finEntree: r3(finEntree), sortieDebut: r3(cale(sortieDebut)), fin: r3(cale(fin)), sortie, mouvements: mouv, n, options: o, avec: ref ? el.avec : undefined, apparition: apparitionDe(rec, o) };
}
/** temps entre le début d'une recette et la première trace visible (2 % de l'opacité) : il compte dans le fond vide après une coupe */
export function apparitionDe(rec, o) {
  const a = (c, T) => r3(T * tempsA(COURBES[c].b, 0.02));
  switch (rec) {
    case 'titre-fondu-montee': return a('easeInOutCubic', o.T_opacite);
    case 'titre-fondu': return a('ease', T_depuis(COURBES.ease.b, o.d1090));
    case 'phrase-zoom-arriere': return a('ease-in-out', T_depuis(COURBES['ease-in-out'].b, o.d1090_opacite));
    case 'liste-cascade': case 'liste-cascade-rapide': return a('easeInOutCubic', o.T_opacite);
    case 'liste-au-fil': return a('easeInOutCubic', o.T_opacite);
    case 'nom-remonte': return a('easeInOutCubic', T_depuis(COURBES.easeInOutCubic.b, o.d1090_opacite));
    case 'chiffre-pose': return a('ease-in-out', T_depuis(COURBES['ease-in-out'].b, o.d1090_opacite));
    case 'chiffre-croissance': return a('ease-out', T_depuis(COURBES['ease-out'].b, o.d1090_opacite));
    case 'carton-fondu': case 'carton-groupes': return a('lineaire', T_depuis(COURBES.lineaire.b, o.d1090));
    case 'logo-fin': return o.entree === 'coupe' ? 0 : a('out-quad', T_depuis(COURBES['out-quad'].b, o.d1090));
    default: return 0;
  }
}
function tempsLignes(el, o, debut) {
  const n = el.lignes.length;
  if (Array.isArray(o.temps) && o.temps.length === n) return o.temps;
  return Array.from({ length: n }, (_, i) => debut + i * o.intervalle);
}
function panneauCourbe(o) { return o.carte ? 'out-back' : (o.dans_la_page ? 'ease' : 'out-expo'); }

/** Plan de tout le fichier (pour le contrôle) */
export function plan(motion) {
  const comp = normaliserComp(motion.comp || {});
  const tous = Object.fromEntries((motion.elements || []).map((e) => [e.id, e]));
  const elements = (motion.elements || []).map((e) => ({ id: e.id, type: e.type, ...planElement(e, comp, tous), puis: (e.puis || []).map((q) => planComplement(e, q, comp, tous)) }));
  const transitions = (motion.transitions || []).map((t) => planTransition(t));
  const camera = motion.camera ? { recette: motion.camera.recette, debut: motion.camera.debut || 0, fin: motion.camera.fin !== undefined ? motion.camera.fin : comp.duree } : null;
  return { comp, elements, transitions, camera };
}
function planComplement(el, q, comp, tous) {
  const base = planElement(el, comp, tous);
  const t0 = q.a !== undefined ? q.a : (q.decalage !== undefined ? base.debut + q.decalage : base.finEntree);
  const fake = { ...el, recette: q.recette, debut: t0, options: q.options || {}, puis: undefined, maintien: undefined, fin: base.sortieDebut };
  const pl = planElement(fake, comp, tous);
  return { recette: q.recette, debut: pl.debut, finEntree: pl.finEntree, mouvements: pl.mouvements, options: pl.options };
}
export function planTransition(t) {
  const o = parametres(t.type, t.options || {}, TRANSITIONS);
  let d = 0;
  switch (t.type) {
    case 'fondu-enchaine': d = o.T; break;
    case 'passage-noir': d = 2 * o.T_fondu + o.noir; break;
    case 'fondu-au-noir': case 'fondu-depuis-noir': d = o.T; break;
    case 'montee-du-noir': d = o.noir + T_depuis(COURBES['in-out-cubic'].b, o.d1090); break;
    case 'glissade': case 'poussee': d = o.T; break;
    case 'bascule-lumiere': d = o.T; break;
    default: d = 0;
  }
  return { type: t.type, temps: t.temps, de: t.de || [], vers: t.vers || [], duree: r3(d), fin: r3(t.temps + d), majeur: ['glissade', 'poussee'].includes(t.type), options: o };
}
export function normaliserComp(c) {
  const fmt = c.format || '16:9';
  const [L, Hh] = FORMATS[fmt] || [c.largeur || 1920, c.hauteur || 1080];
  return { nom: c.nom || 'Motion', format: fmt, largeur: c.largeur || L, hauteur: c.hauteur || Hh, cadence: c.cadence || 30, duree: c.duree || 10, fond: c.fond, epoque: c.epoque || '2024-2026' };
}
export function normaliserTheme(t = {}) {
  return { couleurs: { ...DEFAUTS.couleurs, ...(t.couleurs || {}) }, polices: { ...DEFAUTS.polices, ...(t.polices || {}) }, tailles: { ...DEFAUTS.tailles, ...(t.tailles || {}) }, approche: t.approche || {} };
}

/** motion.json → script .jsx. Renvoie { jsx, notes } */
export function generer(motion, { base = '.', prefixe = '', source = 'motion.json', resoudre = (f) => [f, f] } = {}) {
  const comp = normaliserComp(motion.comp || {});
  const theme = normaliserTheme(motion.theme);
  const W = comp.largeur, H = comp.hauteur, U = Math.min(W, H) / 100, fps = comp.cadence;
  const nomComp = prefixe + comp.nom;
  const els = motion.elements || [];
  const tous = Object.fromEntries(els.map((e) => [e.id, e]));
  const courbes = new Set();
  const C = (nom) => { if (!COURBES[nom]) throw new Error('courbe inconnue : ' + nom); courbes.add(nom); return 'C[' + JS(nom) + ']'; };
  const notes = [];
  const px = (u) => r3(u * U);
  const X = (pc) => r3(pc / 100 * W), Y = (pc) => r3(pc / 100 * H);
  const recettesVues = new Set();
  const flouBouge = new Set();

  const phase = { calques: [], parents: [], anim: [], transitions: [], complements: [], camera: [], presence: [], coupures: [] };
  const plans = {};
  for (const e of els) plans[e.id] = planElement(e, comp, tous);

  // ── nuls de caméra ──
  const cam = motion.camera ? { id: '__camera', type: 'nul-camera', recette: motion.camera.recette, debut: motion.camera.debut || 0, fin: motion.camera.fin, options: motion.camera.options || {}, position: motion.camera.point || [50, 50] } : null;
  const profondeurs = new Set();
  if (cam) { profondeurs.add(1); for (const e of els) if (e.type !== 'fond' && e.camera !== false && e.parent === undefined && croiseCamera(plans[e.id], cam, comp)) profondeurs.add(e.profondeur === undefined ? 1 : e.profondeur); }
  const camVar = (pr) => 'cam_' + String(pr).replace('.', '_');
  if (cam) {
    phase.calques.push('// Caméra : un nul par profondeur, posé neutre (ancre = position) pour que le parentage ne déplace rien.');
    for (const pr of [...profondeurs].sort()) phase.calques.push(`var ${camVar(pr)} = md_nul(${JS('Caméra' + (profondeurs.size > 1 ? ' (profondeur ' + pr + ')' : ''))}, ${X(cam.position[0])}, ${Y(cam.position[1])});`);
  }

  // ── calques, de l'arrière vers l'avant ──
  for (const e of els) {
    const v = ident(e.id), pl = plans[e.id], o = pl.options;
    const rec = pl.recette; recettesVues.add(rec);
    const pos = e.position || [50, 50];
    const cx = X(pos[0]), cy = Y(pos[1]);
    const taille = e.taille !== undefined ? e.taille : theme.tailles[e.type === 'surtitre' ? 'surtitre' : e.type] || 10;
    const coulT = couleur(theme, e.couleur, e.type === 'surtitre' ? 'secondaire' : 'texte');
    const R = RECETTES[rec] || {};
    phase.calques.push('', `// ── ${e.id} (${e.type}) : ${rec}${R.mesure ? ' — ' + R.mesure.split(':')[0].slice(0, 90) : ''}`);
    // voile et flou placés sous l'élément mis en avant
    for (const q of (e.puis || []).concat(rec === 'assombrir-autour' ? [{ recette: 'assombrir-autour', options: e.options }] : [])) {
      if (q.recette !== 'assombrir-autour') continue;
      const qo = parametres('assombrir-autour', q.options || {});
      if (qo.flou > 0) phase.calques.push(`var ${v}_flou = md_solide(${JS(e.id + ' — flou du fond')}, "#808080", W, H); ${v}_flou.l.adjustmentLayer = true; var ${v}_flouP = md_flou(${v}_flou, true);`);
      phase.calques.push(`var ${v}_voile = md_solide(${JS(e.id + ' — voile')}, ${JS(couleur(theme, 'voile', 'voile'))}, W, H);`);
    }
    const nom = (s) => JS(e.id + ' — ' + s);
    switch (e.type) {
      case 'fond': {
        if (e.fichier) phase.calques.push(`var ${v} = md_image(${nom('fond')}, ${JS(resoudre(e.fichier))}, 0, W, W / H, W / 2, H / 2); if (${v}.h < H) { var k_${v} = H / ${v}.h; ${v}.s.setValue([${v}.ech * k_${v}, ${v}.ech * k_${v}, 100]); ${v}.ech *= k_${v}; }`);
        else phase.calques.push(`var ${v} = md_solide(${nom('fond uni')}, ${JS(couleur(theme, e.couleur, 'fond'))}, W, H);`);
        break;
      }
      case 'titre': case 'phrase': case 'surtitre': case 'chiffre': {
        const role = e.police || (e.type === 'chiffre' ? 'chiffre' : e.type === 'phrase' ? 'texte' : e.type === 'surtitre' ? 'surtitre' : 'titre');
        const contenu = String(e.contenu || '').replace(/\n/g, '\r');
        const corps = px(taille);
        const inter = e.interligne ? px(e.interligne) : (contenu.includes('\r') ? r3(corps * 1.12) : 0);
        const appr = theme.approche[e.type] !== undefined ? theme.approche[e.type] : (e.type === 'chiffre' ? -20 : (e.type === 'titre' ? -10 : 0));
        if (rec === 'carton-groupes') {
          const groupes = e.groupes || [contenu];
          phase.calques.push(`var ${v} = { groupes: [], ligne: null };`);
          phase.calques.push(`(function () { var g = ${JS(groupes)}, pol = ${JS(polices(theme, role, 'texte'))}, corps = ${corps}, acc = "", D = [];`);
          phase.calques.push(`  for (var i = 0; i < g.length; i++) { acc = acc + (i ? " " : "") + g[i]; var b = md_largeurTexte(acc, pol, corps), bg = md_largeurTexte(g[i], pol, corps); D.push({ fin: b.droite, decal: b.droite - bg.droite, gauche: b.gauche }); }`);
          phase.calques.push(`  ${v}.mesures = D; ${v}.ligne = md_nul(${nom('ligne (recentrage)')}, ${cx}, ${cy});`);
          phase.calques.push(`  for (var j = 0; j < g.length; j++) { var l = md_texte(${JS(e.id + ' — groupe ')} + (j + 1), g[j], pol, corps, ${JS(coulT)}, "gauche", 0, ${appr}); var r = l.sourceRectAtTime(0, false); md_tr(l).property("ADBE Anchor Point").setValue([0, r.top + r.height / 2]); ${v}.groupes.push(md_el(l, ${cx} + D[j].decal, ${cy}, r.width, r.height)); }`);
          phase.calques.push(`})();`);
        } else {
          phase.calques.push(`var ${v} = md_placerTexte(md_texte(${nom(contenu.replace(/\r/g, ' / ').slice(0, 40))}, ${JS(contenu)}, ${JS(polices(theme, role, 'titre'))}, ${corps}, ${JS(coulT)}, ${JS(e.alignement || 'centre')}, ${inter}, ${appr}), ${cx}, ${cy});`);
          if (e.type === 'chiffre' && e.libelle) {
            const tl = px(e.taille_libelle || theme.tailles.libelle);
            const ly = e.position_libelle ? Y(e.position_libelle[1]) : null;
            phase.calques.push(`var ${v}_lib = md_placerTexte(md_texte(${nom('libellé')}, ${JS(String(e.libelle))}, ${JS(polices(theme, 'texte', 'texte'))}, ${tl}, ${JS(couleur(theme, e.couleur_libelle, 'secondaire'))}, "centre", 0, 0), ${cx}, ${ly !== null ? ly : `${cy} + ${v}.h / 2 + ${r3(tl * 1.4)}`});`);
          }
        }
        break;
      }
      case 'liste': {
        const corps = px(taille), pas = e.interligne ? px(e.interligne) : r3(corps * 1.7);
        const lignes = (e.lignes || []).map(String);
        const gauche = (e.alignement || 'gauche') === 'gauche';
        phase.calques.push(`var ${v} = { lignes: [], pas: ${pas} };`);
        phase.calques.push(`(function () { var L = ${JS(lignes)}, pol = ${JS(polices(theme, e.police || 'texte', 'texte'))}, maxw = 0, ls = [];`);
        phase.calques.push(`  for (var i = 0; i < L.length; i++) { var l = md_texte(${JS(e.id + ' — ligne ')} + (i + 1), L[i], pol, ${corps}, ${JS(coulT)}, ${JS(gauche ? 'gauche' : 'centre')}, 0, 0); ls.push(l); maxw = Math.max(maxw, l.sourceRectAtTime(0, false).width); }`);
        phase.calques.push(`  for (var j = 0; j < ls.length; j++) { var y = ${cy} + (j - (ls.length - 1) / 2) * ${pas}; ${v}.lignes.push(md_placerTexte(ls[j], ${gauche ? `${cx} - maxw / 2` : cx}, y, ${gauche})); }`);
        phase.calques.push(`  ${v}.largeur = maxw; })();`);
        break;
      }
      case 'image': case 'capture': case 'icone': case 'logo': case 'forme': {
        const hauteur = px(taille);
        const ratio = e.ratio || ({ image: 1, capture: 16 / 10, icone: 1, logo: 3, forme: 1 })[e.type];
        if (rec === 'empilement') {
          const fichiers = e.fichiers || [e.fichier];
          phase.calques.push(`var ${v} = { ecrans: [], rangee: md_nul(${nom('rangée')}, ${cx}, ${cy}) };`);
          fichiers.forEach((f, i) => phase.calques.push(`${v}.ecrans.push(md_image(${nom('écran ' + (i + 1))}, ${JS(f ? resoudre(f) : '')}, ${hauteur}, 0, ${r3(ratio)}, ${cx}, ${cy}));`));
          phase.parents.push(`for (var i_${v} = 0; i_${v} < ${v}.ecrans.length; i_${v}++) ${v}.ecrans[i_${v}].l.parent = ${v}.rangee.l;`);
        } else if (rec === 'eclate') {
          const pieces = e.pieces && e.pieces.length ? e.pieces : null;
          phase.calques.push(`var ${v} = { pieces: [] };`);
          if (pieces) pieces.forEach((q, i) => {
            const qx = cx + px((q.position || [0, 0])[0]), qy = cy + px((q.position || [0, 0])[1]);
            const qh = px(q.taille || taille / pieces.length);
            if (q.fichier) phase.calques.push(`${v}.pieces.push(md_image(${nom('pièce ' + (i + 1))}, ${JS(resoudre(q.fichier))}, ${qh}, 0, ${r3(q.ratio || 1)}, ${qx}, ${qy}));`);
            else phase.calques.push(`${v}.pieces.push(md_el(md_forme(${nom('pièce ' + (i + 1))}, ${px(q.largeur || taille)}, ${qh}, ${px(q.coins || 1)}, ${JS(couleur(theme, q.couleur, 'secondaire'))}), ${qx}, ${qy}, ${px(q.largeur || taille)}, ${qh}));`);
          });
          else {
            // repli : trois plaques neutres empilées qui s'écartent verticalement
            for (let i = 0; i < 3; i++) phase.calques.push(`${v}.pieces.push(md_el(md_forme(${nom('[REPLI] plaque ' + (i + 1))}, ${r3(hauteur * ratio)}, ${r3(hauteur / 5)}, ${r3(hauteur / 40)}, ${JS(['#3A3D44', '#4A4E57', '#5B606B'][i])}), ${cx}, ${r3(cy + (i - 1) * hauteur / 4.5)}, ${r3(hauteur * ratio)}, ${r3(hauteur / 5)}));`);
            notes.push(`${e.id} : éclaté sans pièces fournies → trois plaques de repli`);
          }
          e._pieces = pieces || [{ direction: [0, -12] }, { direction: [0, 0] }, { direction: [0, 12] }];
        } else if (e.type === 'forme') {
          const w = px(e.largeur || taille * ratio);
          if (e.forme === 'rond') phase.calques.push(`var ${v} = md_el(md_rond(${nom('rond')}, [${w}, ${hauteur}], ${JS(couleur(theme, e.couleur, 'accent'))}), ${cx}, ${cy}, ${w}, ${hauteur});`);
          else phase.calques.push(`var ${v} = md_el(md_forme(${nom('forme')}, ${w}, ${hauteur}, ${px(e.coins || 0)}, ${JS(couleur(theme, e.couleur, 'accent'))}, ${e.contour ? JS(couleur(theme, e.contour, 'secondaire')) : 'null'}), ${cx}, ${cy}, ${w}, ${hauteur});`);
        } else {
          phase.calques.push(`var ${v} = md_image(${nom(e.type)}, ${JS(e.fichier ? resoudre(e.fichier) : '')}, ${hauteur}, 0, ${r3(ratio)}, ${cx}, ${cy});`);
          if (e.type === 'logo' && e.nom) phase.calques.push(`if (${v}.repli) { ${v}.l.remove(); MD_REPLIS.pop(); MD_REPLIS.push(${JS(e.id + ' : logo absent, remplacé par le nom')}); ${v} = md_placerTexte(md_texte(${nom('nom (repli du logo)')}, ${JS(e.nom)}, ${JS(polices(theme, 'titre', 'titre'))}, ${r3(hauteur * 0.6)}, ${JS(couleur(theme, e.couleur, 'texte'))}, "centre", 0, -10), ${cx}, ${cy}); }`);
        }
        if (rec === 'defilement') {
          const f = o.fenetre || [60, 60];
          phase.calques.push(`var ${v}_fenetre = md_el(md_forme(${nom('fenêtre (cache)')}, ${px(f[0])}, ${px(f[1])}, ${px(1.5)}, "#FFFFFF"), ${cx}, ${cy}, ${px(f[0])}, ${px(f[1])});`);
        }
        if (rec === 'produit-flotte' && o.ombre) {
          phase.calques.push(`var ${v}_ombre = md_el(md_rond(${nom('ombre')}, [${v}.w * 0.7, Math.max(4, ${v}.w * 0.06)], "#000000"), ${cx}, ${cy} + ${v}.h / 2 + ${px(2)}, 0, 0); ${v}_ombre.o.setValue(35); ${v}_ombre.l.moveAfter(${v}.l); md_flou(${v}_ombre, false).setValue(md_sigma(${px(1.2)}));`);
        }
        break;
      }
      case 'nul-camera': {
        phase.calques.push(`var ${v} = md_nul(${nom('nul de caméra')}, ${cx}, ${cy});`);
        break;
      }
      default: throw new Error(`type inconnu : ${e.type} (${e.id})`);
    }
    // parentage
    const enfants = layerList(e, v);
    if (e.parent !== undefined) { for (const c of enfants) phase.parents.push(`${c}.parent = ${ident(e.parent)}.l;`); }
    else if (cam && e.type !== 'fond' && e.camera !== false && croiseCamera(plans[e.id], cam, comp)) { const pr = e.profondeur === undefined ? 1 : e.profondeur; for (const c of enfants) phase.parents.push(`${c}.parent = ${camVar(pr)}.l;`); }
    else if (cam && e.type === 'fond' && e.camera === true) { for (const c of enfants) phase.parents.push(`${c}.parent = ${camVar(1)}.l;`); }
  }

  // ── animations des éléments ──
  for (const e of els) {
    const v = ident(e.id), pl = plans[e.id], o = pl.options, rec = pl.recette;
    const t0 = pl.debut;
    const A = phase.anim;
    A.push('', `// ${e.id} : ${rec} (début ${t0} s, fin d\u2019entrée ${pl.finEntree} s, présence jusqu\u2019à ${pl.fin} s)`);
    const pres = (who) => phase.presence.push(`md_presence(${who}, ${t0}, ${pl.fin});`);
    const sortieFondu = (who) => { if (pl.sortie === 'fondu') A.push(`md_anime(${who}.o, ${pl.sortieDebut}, 100, ${r3(pl.sortieDebut + 1.15)}, 0, null); // sortie en fondu linéaire, 1,15 s (2 titres : 0,90 et 0,93 s de 10 à 90 %)`); };
    const repere = (who, txt) => A.push(`md_repere(${who}.l, ${t0}, ${JS(txt)});`);
    switch (rec) {
      case 'coupe': {
        if (e.type === 'liste') { A.push(`for (var i_${v} = 0; i_${v} < ${v}.lignes.length; i_${v}++) md_presence(${v}.lignes[i_${v}], ${t0}, ${pl.fin});`); }
        else if (e.type === 'chiffre' && e.libelle) { pres(v); phase.presence.push(`md_presence(${v}_lib, ${t0}, ${pl.fin});`); }
        else if (e.type !== 'nul-camera') pres(v);
        if (e.type !== 'liste' && e.type !== 'nul-camera') sortieFondu(v);
        break;
      }
      case 'titre-fondu-montee': {
        repere(v, 'titre-fondu-montee : opacité easeInOutCubic T ' + o.T_opacite + ' s ; montée ' + o.montee + ' u easeOutExpo T ' + o.T_position + ' s');
        A.push(`md_anime(${v}.o, ${t0}, 0, ${r3(t0 + o.T_opacite)}, 100, ${C('easeInOutCubic')});`);
        A.push(`md_anime(${v}.y, ${r3(t0 + o.retard_position)}, ${v}.cy + ${px(o.montee)}, ${r3(t0 + o.retard_position + o.T_position)}, ${v}.cy, ${C('easeOutExpo')});`);
        if (o.flou > 0) A.push(`var f_${v} = md_flou(${v}, false); md_anime(f_${v}, ${t0}, md_sigma(${px(o.flou)}), ${r3(t0 + o.T_opacite)}, 0, ${C('easeInOutCubic')}); // convention : léger flou de départ`);
        pres(v); sortieFondu(v); break;
      }
      case 'titre-fondu': {
        const T = r3(T_depuis(COURBES.ease.b, o.d1090));
        repere(v, 'titre-fondu : opacité ease, T ' + T + ' s');
        A.push(`md_anime(${v}.o, ${t0}, 0, ${r3(t0 + T)}, 100, ${C('ease')});`); pres(v); sortieFondu(v); break;
      }
      case 'carton-fondu': {
        const T = r3(T_depuis(COURBES.lineaire.b, o.d1090));
        repere(v, 'carton-fondu : opacité linéaire, T ' + T + ' s');
        A.push(`md_anime(${v}.o, ${t0}, 0, ${r3(t0 + T)}, 100, null);`); pres(v); sortieFondu(v); break;
      }
      case 'titre-balayage': {
        repere(v, 'titre-balayage : front linéaire, T ' + o.T + ' s, bord ' + o.bord + ' % L');
        const bord = r3(o.bord / 100 * W);
        A.push(`(function () { var b = md_bornes(${v}), bord = ${bord}, h = b.height * 1.6, w = b.width + 3 * bord;`);
        A.push(`  var m = md_el(md_forme(${JS(e.id + ' — front du balayage (cache)')}, w, h, 0, "#FFFFFF"), 0, 0, w, h); m.l.parent = ${v}.l; m.x.setValue(b.left + b.width / 2); m.y.setValue(b.top + b.height / 2);`);
        A.push(`  md_flou(m, false).setValue(md_sigma(bord / 2.56));`);
        A.push(`  md_anime(m.x, ${t0}, b.left - w / 2 - bord, ${r3(t0 + o.T)}, b.left + b.width + w / 2 - w + 1.5 * bord, null);`);
        A.push(`  md_presence(m, ${t0}, ${pl.fin}); md_cache(${v}.l, m.l); })();`);
        pres(v); sortieFondu(v); break;
      }
      case 'phrase-zoom-arriere': {
        const To = r3(T_depuis(COURBES['ease-in-out'].b, o.d1090_opacite));
        repere(v, 'phrase-zoom-arriere : échelle ×' + o.depart + ' → 1, ease, T ' + o.T_echelle + ' s');
        A.push(`md_anime(${v}.s, ${t0}, [${v}.ech * ${o.depart}, ${v}.ech * ${o.depart}, 100], ${r3(t0 + o.T_echelle)}, [${v}.ech, ${v}.ech, 100], ${C('ease')});`);
        A.push(`md_anime(${v}.o, ${t0}, 0, ${r3(t0 + To)}, 100, ${C('ease-in-out')});`);
        A.push(`var f_${v} = md_flou(${v}, false); md_anime(f_${v}, ${t0}, md_sigma(${px(o.flou)}), ${r3(t0 + o.T_echelle)}, 0, ${C('ease')});`);
        pres(v); sortieFondu(v); break;
      }
      case 'chute': {
        repere(v, 'chute : easeInQuad, T ' + o.T + ' s, depuis ' + o.hauteur + ' u au-dessus, sans rebond');
        A.push(`md_anime(${v}.y, ${t0}, ${v}.cy - ${px(o.hauteur)}, ${r3(t0 + o.T)}, ${v}.cy, ${C('easeInQuad')});`);
        A.push(`md_anime(${v}.o, ${t0}, 0, ${r3(t0 + 3 / fps)}, 100, null); // opacité pleine en 3 images (0,09 s mesuré)`);
        pres(v); if (e.type === 'chiffre' && e.libelle) libelle(A, e, v, t0, debutLibelle(null, 0, 'ease-out', 0.18, 0.11), 0.18, 0.11, 'ease-out', pl, C); sortieFondu(v); break;
      }
      case 'phrase-par-le-bas': {
        repere(v, 'phrase-par-le-bas : ease, T ' + o.T + ' s, déjà opaque');
        A.push(`md_anime(${v}.y, ${t0}, ${v}.cy + ${px(o.depart)}, ${r3(t0 + o.T)}, ${v}.cy, ${C('ease')});`);
        pres(v); sortieFondu(v); break;
      }
      case 'liste-cascade': case 'liste-cascade-rapide': {
        const Top = r3(o.T_opacite);
        const cpos = 'easeInOutQuint';
        A.push(`// une ligne toutes les ${o.decalage} s ; opacité easeInOutCubic T ${Top} s ; montée ${o.montee} u ${cpos} T ${o.T_position} s`);
        A.push(`for (var i_${v} = 0; i_${v} < ${v}.lignes.length; i_${v}++) { var q = ${v}.lignes[i_${v}], t = ${t0} + i_${v} * ${o.decalage};`);
        A.push(`  md_anime(q.o, t, 0, t + ${Top}, 100, ${C('easeInOutCubic')});`);
        if (o.montee > 0) A.push(`  md_anime(q.y, t, q.cy + ${px(o.montee)}, t + ${o.T_position}, q.cy, ${C(cpos)});`);
        A.push(`  md_repere(q.l, t, ${JS(rec + ' : ligne ')} + (i_${v} + 1)); md_presence(q, ${t0}, ${pl.fin});${pl.sortie === 'fondu' ? ` md_anime(q.o, ${pl.sortieDebut}, 100, ${r3(pl.sortieDebut + 1.15)}, 0, null);` : ''} }`);
        break;
      }
      case 'liste-par-le-bas': {
        A.push(`// lignes déjà opaques qui montent depuis +${o.depart} u, easeOutQuart T ${o.T} s, une toutes les ${o.decalage} s`);
        A.push(`for (var i_${v} = 0; i_${v} < ${v}.lignes.length; i_${v}++) { var q = ${v}.lignes[i_${v}], t = ${t0} + i_${v} * ${o.decalage};`);
        A.push(`  md_anime(q.y, t, q.cy + ${px(o.depart)}, t + ${o.T}, q.cy, ${C('easeOutQuart')}); md_presence(q, t, ${pl.fin}); md_repere(q.l, t, "liste-par-le-bas : ligne " + (i_${v} + 1));${pl.sortie === 'fondu' ? ` md_anime(q.o, ${pl.sortieDebut}, 100, ${r3(pl.sortieDebut + 1.15)}, 0, null);` : ''} }`);
        break;
      }
      case 'liste-au-fil': {
        const ts = tempsLignes(e, o, t0).map(r3);
        A.push(`// une ligne quand elle est dite (${JS(ts)} s) ; la nouvelle : easeInOutCubic T ${o.T_opacite} s, montée ${o.montee} u easeInOutQuart T ${o.T_position} s ; les autres remontent d\u2019une demi-interligne`);
        A.push(`(function () { var ts = ${JS(ts)}, n = ${v}.lignes.length, pas = ${v}.pas;`);
        A.push(`  for (var i = 0; i < n; i++) { var q = ${v}.lignes[i], t = ts[i];`);
        A.push(`    var yk = function (j, k) { return ${cyOf(e, Y)} + (j - (k - 1) / 2) * pas; };`);
        A.push(`    md_anime(q.o, t, 0, t + ${o.T_opacite}, 100, ${C('easeInOutCubic')});`);
        A.push(`    md_anime(q.y, t, yk(i, i + 1) + ${px(o.montee)}, t + ${o.T_position}, yk(i, i + 1), ${C('easeInOutQuart')});`);
        A.push(`    for (var j = 0; j < i; j++) md_anime(${v}.lignes[j].y, t, yk(j, i), t + ${o.T_position}, yk(j, i + 1), ${C('easeInOutQuart')});`);
        A.push(`    md_presence(q, t, ${pl.fin}); md_repere(q.l, t, "liste-au-fil : ligne " + (i + 1));${pl.sortie === 'fondu' ? ` md_anime(q.o, ${pl.sortieDebut}, 100, ${r3(pl.sortieDebut + 1.15)}, 0, null);` : ''} } })();`);
        break;
      }
      case 'nom-remonte': {
        const To = r3(T_depuis(COURBES.easeInOutCubic.b, o.d1090_opacite));
        const nomId = (e.options || {}).nom;
        repere(v, 'nom-remonte : le nom monte de ' + o.remontee + ' u (ease, T ' + o.T_nom + ' s) ; libellé et prix entrent dessous');
        if (nomId && tous[nomId]) A.push(`md_anime(${ident(nomId)}.y, ${t0}, md_valeur(${ident(nomId)}.y, ${t0}), ${r3(t0 + o.T_nom)}, md_valeur(${ident(nomId)}.y, ${t0}) - ${px(o.remontee)}, ${C('ease')});`);
        else notes.push(`${e.id} : nom-remonte sans options.nom valide`);
        A.push(`md_anime(${v}.o, ${t0}, 0, ${r3(t0 + To)}, 100, ${C('easeInOutCubic')});`);
        A.push(`md_anime(${v}.y, ${t0}, ${v}.cy + ${px(o.montee)}, ${r3(t0 + To)}, ${v}.cy, ${C('easeInOutCubic')});`);
        pres(v); sortieFondu(v); break;
      }
      case 'mot-remplace': {
        const anc = (e.options || {}).ancien;
        repere(v, 'mot-remplace : sur la même image que la sortie de l\u2019ancien');
        if (anc && tous[anc]) phase.coupures.push(`${ident(anc)}.l.outPoint = md_cale(${t0}); // mot-remplace`);
        pres(v); sortieFondu(v); break;
      }
      case 'mot-fondu-enchaine': {
        const anc = (e.options || {}).ancien;
        const Ta = r3(T_depuis(COURBES.easeInOutSine.b, o.d1090_ancien)), Tn = r3(T_depuis(COURBES.easeInOutSine.b, o.d1090_nouveau));
        const ta = r3(t0 - o.ecart + Tn / 2 - Ta / 2);
        repere(v, 'mot-fondu-enchaine : 1 cas mesuré');
        if (anc && tous[anc]) {
          A.push(`md_anime(${ident(anc)}.o, ${ta}, 100, ${r3(ta + Ta)}, 0, ${C('easeInOutSine')});`);
          if (o.flou > 0) A.push(`var f_${v}_anc = md_flou(${ident(anc)}, false); md_anime(f_${v}_anc, ${ta}, 0, ${r3(ta + Ta)}, md_sigma(${px(o.flou)}), ${C('easeInOutSine')});`);
          phase.coupures.push(`${ident(anc)}.l.outPoint = md_cale(${r3(ta + Ta)});`);
        } else notes.push(`${e.id} : mot-fondu-enchaine sans options.ancien valide`);
        A.push(`md_anime(${v}.o, ${t0}, 0, ${r3(t0 + Tn)}, 100, ${C('easeInOutSine')});`);
        pres(v); sortieFondu(v); break;
      }
      case 'mot-glisse': {
        const anc = (e.options || {}).ancien;
        const Ta = r3(T_depuis(COURBES['ease-in'].b, o.d1090_ancien)), Tn = r3(T_depuis(COURBES.easeInCubic.b, o.d1090_nouveau));
        repere(v, 'mot-glisse : 1 cas mesuré');
        if (anc && tous[anc]) {
          const ta = r3(t0 - o.ecart);
          A.push(`md_anime(${ident(anc)}.o, ${ta}, 100, ${r3(ta + Ta)}, 0, ${C('ease-in')}); md_anime(${ident(anc)}.y, ${ta}, ${ident(anc)}.cy, ${r3(ta + Ta)}, ${ident(anc)}.cy - ${px(o.glisse)}, ${C('ease-in')});`);
          phase.coupures.push(`${ident(anc)}.l.outPoint = md_cale(${r3(ta + Ta)});`);
        } else notes.push(`${e.id} : mot-glisse sans options.ancien valide`);
        A.push(`md_anime(${v}.o, ${t0}, 0, ${r3(t0 + Tn)}, 100, ${C('easeInCubic')}); md_anime(${v}.y, ${t0}, ${v}.cy + ${px(o.glisse)}, ${r3(t0 + Tn)}, ${v}.cy, ${C('easeInCubic')});`);
        pres(v); sortieFondu(v); break;
      }
      case 'chiffre-pose': {
        const To = r3(T_depuis(COURBES['ease-in-out'].b, o.d1090_opacite));
        repere(v, 'chiffre-pose : ×' + o.depart + ' → 1 easeOutExpo T ' + o.T_echelle + ' s ; opacité T ' + To + ' s ; flou σ ' + o.flou + ' u → 0');
        A.push(`md_anime(${v}.s, ${t0}, [${v}.ech * ${o.depart}, ${v}.ech * ${o.depart}, 100], ${r3(t0 + o.T_echelle)}, [${v}.ech, ${v}.ech, 100], ${C('easeOutExpo')});`);
        A.push(`md_anime(${v}.o, ${t0}, 0, ${r3(t0 + To)}, 100, ${C('ease-in-out')});`);
        A.push(`var f_${v} = md_flou(${v}, false); md_anime(f_${v}, ${t0}, md_sigma(${px(o.flou)}), ${r3(t0 + o.T_echelle)}, 0, ${C('easeOutExpo')});`);
        pres(v);
        if (e.libelle) libelle(A, e, v, t0, debutLibelle('ease-in-out', o.d1090_opacite, 'ease-in-out', o.retard_libelle, o.d1090_libelle), o.retard_libelle, o.d1090_libelle, 'ease-in-out', pl, C);
        sortieFondu(v); break;
      }
      case 'chiffre-croissance': {
        const To = r3(T_depuis(COURBES['ease-out'].b, o.d1090_opacite));
        repere(v, 'chiffre-croissance : ×' + o.depart + ' → 1 easeOutBack (dépassement +5 %) T ' + o.T_echelle + ' s');
        A.push(`md_anime(${v}.s, ${t0}, [${v}.ech * ${o.depart}, ${v}.ech * ${o.depart}, 100], ${r3(t0 + o.T_echelle)}, [${v}.ech, ${v}.ech, 100], ${C('easeOutBack')});`);
        A.push(`md_anime(${v}.o, ${t0}, 0, ${r3(t0 + To)}, 100, ${C('ease-out')});`);
        pres(v);
        if (e.libelle) libelle(A, e, v, t0, debutLibelle('ease-out', o.d1090_opacite, 'ease-out', o.retard_libelle, o.d1090_libelle), o.retard_libelle, o.d1090_libelle, 'ease-out', pl, C);
        sortieFondu(v); break;
      }
      case 'carton-groupes': {
        const T = r3(T_depuis(COURBES.lineaire.b, o.d1090));
        A.push(`// groupes de sens toutes les ${o.ecart} s, fondu linéaire T ${T} s ; la ligne se recentre (convention : easeOutCubic ${o.T_recentrage} s)`);
        A.push(`(function () { var D = ${v}.mesures, n = ${v}.groupes.length; for (var j = 0; j < n; j++) ${v}.groupes[j].l.parent = ${v}.ligne.l;`);
        A.push(`  var centre = function (k) { return -(D[0].gauche + D[k].fin) / 2; };`);
        A.push(`  for (var k = 0; k < n; k++) { var t = ${t0} + k * ${o.ecart}, g = ${v}.groupes[k]; md_anime(g.o, t, 0, t + ${T}, 100, null); md_presence(g, t, ${pl.fin}); md_repere(g.l, t, "carton-groupes : groupe " + (k + 1));${pl.sortie === 'fondu' ? ` md_anime(g.o, ${pl.sortieDebut}, 100, ${r3(pl.sortieDebut + 1.15)}, 0, null);` : ''}`);
        A.push(`    if (k === 0) ${v}.ligne.x.setValue(${v}.ligne.cx + centre(0)); else md_anime(${v}.ligne.x, t, ${v}.ligne.cx + centre(k - 1), t + ${o.T_recentrage}, ${v}.ligne.cx + centre(k), ${C('easeOutCubic')}); } })();`);
        break;
      }
      case 'produit-entree': {
        repere(v, 'produit-entree : par la ' + o.depuis + ', out-cubic T ' + o.T + ' s, flou de bougé ' + o.obturateur + '°');
        const s = o.depuis === 'gauche' ? -1 : 1;
        A.push(`md_anime(${v}.x, ${t0}, ${s > 0 ? `W + ${v}.w / 2 + ${px(2)}` : `-${v}.w / 2 - ${px(2)}`}, ${r3(t0 + o.T)}, ${v}.cx, ${C('out-cubic')}); ${v}.l.motionBlur = true;`);
        flouBouge.add(o.obturateur);
        pres(v); sortieFondu(v); break;
      }
      case 'produit-poussee': case 'produit-recul': {
        const fin = rec === 'produit-poussee' ? pl.sortieDebut : r3(Math.min(pl.sortieDebut, t0 + o.duree));
        const fin2 = (e.options || {}).duree !== undefined ? r3(t0 + o.duree) : fin;
        repere(v, rec + ' : ×' + o.facteur + (rec === 'produit-poussee' ? ' linéaire' : ' ease-out') + ' de ' + t0 + ' à ' + fin2 + ' s');
        A.push(`md_anime(${v}.s, ${t0}, [${v}.ech, ${v}.ech, 100], ${fin2}, [${v}.ech * ${o.facteur}, ${v}.ech * ${o.facteur}, 100], ${rec === 'produit-poussee' ? 'null' : C('ease-out')});`);
        pres(v); sortieFondu(v); break;
      }
      case 'produit-rotation': {
        repere(v, 'produit-rotation : ' + o.angle + '° linéaire en ' + o.duree + ' s');
        A.push(`md_anime(${v}.r, ${t0}, 0, ${r3(t0 + o.duree)}, ${o.angle}, null);`); pres(v); sortieFondu(v); break;
      }
      case 'produit-pivot': {
        repere(v, 'produit-pivot : ' + o.angle + '° → 0 linéaire en ' + o.T + ' s, ' + o.delai + ' s après la coupe');
        A.push(`${v}.l.threeDLayer = true; var ry_${v} = md_tr(${v}.l).property("ADBE Rotate Y"); md_anime(ry_${v}, ${r3(t0 + o.delai)}, ${o.angle}, ${r3(t0 + o.delai + o.T)}, 0, null);`);
        pres(v); sortieFondu(v); break;
      }
      case 'produit-flotte': {
        repere(v, 'produit-flotte : immobile' + (o.derive ? ', dérive linéaire ' + o.derive + ' u/s (convention)' : '') + (o.ombre ? ', ombre au sol (convention)' : ''));
        if (o.derive) A.push(`md_anime(${v}.y, ${t0}, ${v}.cy, ${pl.sortieDebut}, ${v}.cy - ${px(o.derive)} * ${r3(pl.sortieDebut - t0)}, null);`);
        pres(v); if (o.ombre) phase.presence.push(`md_presence(${v}_ombre, ${t0}, ${pl.fin});`); sortieFondu(v); break;
      }
      case 'eclate': {
        const T = o.sens === 'ferme' ? o.T_ferme : o.T_ouvre;
        const courbe = o.sens === 'ferme' ? null : C('ease-out');
        A.push(`// éclaté (${o.sens}) : ${o.sens === 'ferme' ? 'linéaire' : 'ease-out'}, T ${T} s, décalage entre pièces ${o.decalage} s (convention)`);
        e._pieces.forEach((q, i) => {
          const d = q.direction || [0, 0], dx = px(d[0] * o.amplitude), dy = px(d[1] * o.amplitude), t = r3(t0 + i * o.decalage);
          const pv = `${v}.pieces[${i}]`;
          if (o.sens === 'ferme') { if (dx) A.push(`md_anime(${pv}.x, ${t}, ${pv}.cx + ${dx}, ${r3(t + T)}, ${pv}.cx, null);`); if (dy) A.push(`md_anime(${pv}.y, ${t}, ${pv}.cy + ${dy}, ${r3(t + T)}, ${pv}.cy, null);`); }
          else { if (dx) A.push(`md_anime(${pv}.x, ${t}, ${pv}.cx, ${r3(t + T)}, ${pv}.cx + ${dx}, ${courbe});`); if (dy) A.push(`md_anime(${pv}.y, ${t}, ${pv}.cy, ${r3(t + T)}, ${pv}.cy + ${dy}, ${courbe});`); }
          A.push(`md_presence(${pv}, ${t0}, ${pl.fin});`);
        });
        break;
      }
      case 'panneau-pose': {
        const c = panneauCourbe(o), T = r3(T_depuis(COURBES[c].b, o.visible, 'visible'));
        const dist = px(o.dans_la_page ? Math.min(o.distance, 15.9) : o.distance);
        const axe = (o.depuis === 'gauche' || o.depuis === 'droite') ? 'x' : 'y', sg = (o.depuis === 'bas' || o.depuis === 'droite') ? '+' : '-';
        repere(v, 'panneau-pose : depuis ' + o.depuis + ', ' + c + ', T ' + T + ' s (' + o.visible + ' s visibles)');
        A.push(`md_anime(${v}.${axe}, ${t0}, ${v}.c${axe} ${sg} ${dist}, ${r3(t0 + T)}, ${v}.c${axe}, ${C(c)});`);
        if (o.fondu) A.push(`md_anime(${v}.o, ${t0}, 0, ${r3(t0 + Math.max(T / 3, 2 / fps))}, 100, null); // convention : fondu sur le premier tiers`);
        pres(v); sortieFondu(v); break;
      }
      case 'zoom-detail': {
        const c = o.sens === 'sort' ? 'zoom-sortie' : (comp.epoque === '2019-2020' ? 'montage-2020' : 'zoom-2024');
        const pt = o.point || [50, 50], cible = (e.options || {}).cible || [50, 50];
        repere(v, 'zoom-detail : ×' + o.facteur + ' vers le point ' + pt.join(',') + ' %, ' + c + ', T ' + o.T + ' s');
        A.push(`(function () { var b = ${e.type === 'nul-camera' ? '{ left: 0, top: 0, width: W, height: H }' : `md_bornes(${v})`}, ax = b.left + b.width * ${pt[0] / 100}, ay = b.top + b.height * ${pt[1] / 100}, a0 = ${v}.a.value, k = ${v}.ech / 100;`);
        A.push(`  ${v}.a.setValue([ax, ay]); var px0 = md_valeur(${v}.x, ${t0}) + (ax - a0[0]) * k, py0 = md_valeur(${v}.y, ${t0}) + (ay - a0[1]) * k;`);
        A.push(`  if (${v}.x.numKeys === 0) ${v}.x.setValue(px0); if (${v}.y.numKeys === 0) ${v}.y.setValue(py0);`);
        const [s0, s1] = o.sens === 'sort' ? [`${v}.ech * ${o.facteur}`, `${v}.ech`] : [`${v}.ech`, `${v}.ech * ${o.facteur}`];
        const [pA, pB] = o.sens === 'sort' ? [[X(cible[0]), Y(cible[1])], ['px0', 'py0']] : [['px0', 'py0'], [X(cible[0]), Y(cible[1])]];
        A.push(`  md_anime(${v}.s, ${t0}, [${s0}, ${s0}, 100], ${r3(t0 + o.T)}, [${s1}, ${s1}, 100], ${C(c)});`);
        A.push(`  md_anime(${v}.x, ${t0}, ${pA[0]}, ${r3(t0 + o.T)}, ${pB[0]}, ${C(c)}); md_anime(${v}.y, ${t0}, ${pA[1]}, ${r3(t0 + o.T)}, ${pB[1]}, ${C(c)}); })();`);
        if (e.type !== 'nul-camera') { pres(v); sortieFondu(v); }
        break;
      }
      case 'defilement': {
        const c = o.mode === 'geste' ? 'geste' : o.mode === 'continu' ? null : (comp.epoque === '2019-2020' ? 'defilement' : 'defilement-2024');
        const T = o.mode === 'continu' ? r3(o.distance / 68) : o.T;
        repere(v, 'defilement (' + o.mode + ') : ' + o.distance + ' u en ' + T + ' s');
        A.push(`(function () { var f = ${v}_fenetre; if (!${v}.repli) { var k = f.w / ${v}.w; ${v}.s.setValue([${v}.ech * k, ${v}.ech * k, 100]); ${v}.ech *= k; ${v}.w *= k; ${v}.h *= k; }`);
        A.push(`  var y0 = f.cy - f.h / 2 + ${v}.h / 2; ${v}.cy = y0; md_anime(${v}.y, ${t0}, y0, ${r3(t0 + T)}, y0 - ${px(o.distance)}, ${c ? C(c) : 'null'}); md_cache(${v}.l, f.l); md_presence(f, ${t0}, ${pl.fin}); })();`);
        pres(v); sortieFondu(v); break;
      }
      case 'empilement': {
        const c = comp.epoque === '2019-2020' ? 'montage-2020' : 'rangee-2024';
        const T = comp.epoque === '2019-2020' ? Math.max(o.T, 0.96) : o.T;
        A.push(`// empilement : un écran à la fois, toutes les ${o.intervalle} s ; la rangée se recentre ; ${c}, T ${T} s`);
        A.push(`(function () { var E = ${v}.ecrans, n = E.length, pas = E[0].w + ${px(o.ecart)}, R = ${v}.rangee;`);
        A.push(`  for (var i = 0; i < n; i++) { E[i].x.setValue(${v}.rangee.cx + i * pas); }`);
        A.push(`  md_presence(E[0], ${t0}, ${pl.fin});`);
        A.push(`  for (var i = 1; i < n; i++) { var t = ${t0} + i * ${o.intervalle}, rx0 = R.cx - (i - 1) * pas / 2, rx1 = R.cx - i * pas / 2;`);
        A.push(`    md_anime(R.x, t, rx0, t + ${T}, rx1, ${C(c)});`);
        A.push(`    md_anime(E[i].x, t, W + E[i].w / 2 + ${px(2)} - rx0 + R.cx, t + ${T}, R.cx + i * pas, ${C(c)});`);
        A.push(`    md_presence(E[i], t, ${pl.fin}); md_repere(E[i].l, t, "empilement : écran " + (i + 1)); } })();`);
        break;
      }
      case 'logo-fin': {
        if (o.entree === 'coupe') repere(v, 'logo-fin : à la coupe, immobile');
        else { const T = r3(T_depuis(COURBES['out-quad'].b, o.d1090)); repere(v, 'logo-fin : fondu out-quad T ' + T + ' s, immobile'); A.push(`md_anime(${v}.o, ${t0}, 0, ${r3(t0 + T)}, 100, ${C('out-quad')});`); }
        pres(v); sortieFondu(v); break;
      }
      case 'camera-poussee': case 'camera-recul': case 'camera-travelling': case 'camera-se-pose': {
        if (e.type === 'nul-camera') cameraKeys(A, v, rec, o, t0, e.fin !== undefined ? e.fin : comp.duree, 1, C, px);
        break;
      }
            default: if (rec !== 'assombrir-autour' && rec !== 'balayage-lumiere' && rec !== 'revelation-lumiere') notes.push(`${e.id} : recette ${rec} non gérée`);
        pres(v); sortieFondu(v);
    }
    if (e.type === 'chiffre' && e.libelle && !['chiffre-pose', 'chiffre-croissance', 'chute', 'coupe'].includes(rec)) libelle(A, e, v, t0, debutLibelle(null, 0, 'ease-in-out', 0.23, 0.27), 0.23, 0.27, 'ease-in-out', pl, C);
    // compléments posés tout de suite (assombrir-autour) ou à la fin (lumières, qui copient l'élément)
    const comps = (e.puis || []).map((q) => ({ q, pl: planComplement(e, q, comp, tous) }));
    if (['assombrir-autour', 'balayage-lumiere', 'revelation-lumiere'].includes(rec)) comps.unshift({ q: { recette: rec, options: e.options }, pl: { debut: t0, options: o } });
    for (const { q, pl: qp } of comps) {
      const qo = qp.options, tq = qp.debut;
      recettesVues.add(q.recette);
      if (q.recette === 'assombrir-autour') {
        const c = comp.epoque === '2019-2020' ? 'voile' : 'voile-2024';
        A.push(`md_repere(${v}_voile.l, ${tq}, ${JS('assombrir-autour : voile ' + qo.niveau + ' %, ' + c + ', T ' + qo.T + ' s' + (qo.flou ? ', flou σ ' + qo.flou + ' u' : ''))});`);
        A.push(`md_anime(${v}_voile.o, ${tq}, 0, ${r3(tq + qo.T)}, ${qo.niveau}, ${C(c)}); md_presence(${v}_voile, ${tq}, ${pl.fin});`);
        if (qo.flou > 0) A.push(`md_anime(${v}_flouP, ${tq}, 0, ${r3(tq + qo.T)}, md_sigma(${px(qo.flou)}), ${C('out-expo')}); md_presence(${v}_flou, ${tq}, ${pl.fin});`);
      } else if (q.recette === 'balayage-lumiere') {
        const sens = qo.sens === 'bas' ? 'haut' : qo.sens;
        if (qo.sens === 'bas') notes.push(`${e.id} : balayage vers le bas jamais vu (0 sur 11) → remplacé par « haut »`);
        phase.complements.push(`// ${e.id} : balayage-lumiere, linéaire T ${qo.T} s, vers la ${sens}, bande ${qo.largeur} % de l\u2019objet (une seule fois)`);
        phase.complements.push(`(function () { var cible = ${cibleDe(e, v)}, b = md_bornes(cible), bw = b.width * ${qo.largeur / 100}, bh = Math.sqrt(b.width * b.width + b.height * b.height) * 1.2;`);
        phase.complements.push(`  var vert = ${sens === 'haut'}, L = vert ? bh : bw, Hh = vert ? bw : bh;`);
        phase.complements.push(`  var band = md_el(md_forme(${JS(e.id + ' — filet de lumière')}, L, Hh, 0, ${JS(couleur(theme, 'lumiere', 'lumiere'))}), 0, 0, L, Hh); band.l.parent = cible.l; band.l.moveBefore(cible.l);`);
        phase.complements.push(`  band.x.setValue(b.left + b.width / 2); band.y.setValue(b.top + b.height / 2); band.r.setValue(${qo.inclinaison}); band.o.setValue(${qo.intensite}); band.l.blendingMode = BlendingMode.ADD; md_flou(band, false).setValue(md_sigma(bw * 0.1));`);
        const [p0, p1, ax] = sens === 'gauche' ? ['b.left + b.width + bw', 'b.left - bw', 'x'] : sens === 'haut' ? ['b.top + b.height + bw', 'b.top - bw', 'y'] : ['b.left - bw', 'b.left + b.width + bw', 'x'];
        phase.complements.push(`  md_anime(band.${ax}, ${tq}, ${p0}, ${r3(tq + qo.T)}, ${p1}, null); md_presence(band, ${tq}, ${r3(tq + qo.T + 2 / fps)});`);
        phase.complements.push(`  var copie = cible.l.duplicate(); copie.name = ${JS(e.id + ' — cache du filet')}; md_cache(band.l, copie); md_repere(band.l, ${tq}, "balayage-lumiere"); })();`);
      } else if (q.recette === 'revelation-lumiere') {
        const Td = r3(T_depuis(COURBES.lineaire.b, qo.sens === 'eteint' ? Math.min(qo.d1090, 1.0) : qo.d1090));
        const ta = r3(tq + qo.delai);
        phase.complements.push(`// ${e.id} : revelation-lumiere (${qo.sens}), noir linéaire T ${Td} s, ${qo.delai} s après la coupe${qo.eclat ? ', éclat +' + qo.eclat + ' % (convention : 3 clés)' : ''}`);
        phase.complements.push(`(function () { var cible = ${cibleDe(e, v)};`);
        phase.complements.push(`  var noir = md_solide(${JS(e.id + ' — ombre de la révélation')}, "#000000", W, H); noir.l.moveBefore(cible.l);`);
        if (qo.sens === 'eteint') phase.complements.push(`  md_anime(noir.o, ${ta}, 0, ${r3(ta + Td)}, 100, null); md_presence(noir, ${ta}, ${pl.fin});`);
        else phase.complements.push(`  md_saut(noir.o, ${tq}, 100); md_anime(noir.o, ${ta}, 100, ${r3(ta + Td)}, 0, null); md_presence(noir, ${tq}, ${r3(ta + Td + 2 / fps)});`);
        phase.complements.push(`  var c1 = cible.l.duplicate(); c1.name = ${JS(e.id + ' — cache de l\u2019ombre')}; md_cache(noir.l, c1);`);
        if (qo.eclat > 0 && qo.sens !== 'eteint') {
          phase.complements.push(`  var ec = md_solide(${JS(e.id + ' — éclat')}, "#FFFFFF", W, H); ec.l.moveBefore(c1); ec.l.blendingMode = BlendingMode.ADD;`);
          phase.complements.push(`  md_anime(ec.o, ${r3(ta + Td * 0.6)}, 0, ${r3(ta + Td * 0.6 + 0.5)}, ${qo.eclat}, ${C('out-quad')}); md_anime(ec.o, ${r3(ta + Td * 0.6 + 0.5)}, ${qo.eclat}, ${r3(ta + Td * 0.6 + 1.1)}, 0, ${C('in-out-sine')}); md_presence(ec, ${r3(ta + Td * 0.6)}, ${r3(ta + Td * 0.6 + 1.1 + 2 / fps)});`);
          phase.complements.push(`  var c2 = cible.l.duplicate(); c2.name = ${JS(e.id + ' — cache de l\u2019éclat')}; md_cache(ec.l, c2);`);
        }
        phase.complements.push(`})();`);
      } else {
        notes.push(`${e.id} : complément « ${q.recette} » non géré dans « puis » (seuls assombrir-autour, balayage-lumiere, revelation-lumiere)`);
      }
    }
  }

  // ── transitions ──
  for (const t of motion.transitions || []) {
    const tp = planTransition(t), o = tp.options, T0 = r3(t.temps);
    const de = (t.de || []).filter((id) => tous[id]), vers = (t.vers || []).filter((id) => tous[id]);
    const TR = phase.transitions;
    TR.push('', `// transition ${t.type} à ${T0} s${de.length ? ' : ' + de.join(', ') : ''}${vers.length ? ' → ' + vers.join(', ') : ''}`);
    const calquesDe = de.flatMap((id) => tousCalques(tous[id], ident(id)));
    const calquesVers = vers.flatMap((id) => tousCalques(tous[id], ident(id)));
    const visDe = de.flatMap((id) => visibles(tous[id], ident(id)));
    const visVers = vers.flatMap((id) => visibles(tous[id], ident(id)));
    switch (t.type) {
      case 'coupe': case 'raccord':
        for (const c of calquesDe) TR.push(`if (${c}.outPoint > md_cale(${T0})) ${c}.outPoint = md_cale(${T0});`);
        for (const c of calquesVers) TR.push(`if (${c}.inPoint < md_cale(${T0})) ${c}.inPoint = md_cale(${T0});`);
        break;
      case 'fondu-enchaine':
        TR.push(`// fondu enchaîné linéaire, T ${o.T} s (aucun au-delà de 1 s : 25 sur 25)`);
        for (const c of visDe) TR.push(`md_anime(md_tr(${c}).property("ADBE Opacity"), ${T0}, md_valeur(md_tr(${c}).property("ADBE Opacity"), ${T0}), ${r3(T0 + o.T)}, 0, null);`);
        for (const c of calquesDe) TR.push(`${c}.outPoint = md_cale(${r3(T0 + o.T)});`);
        for (const c of visVers) TR.push(`md_anime(md_tr(${c}).property("ADBE Opacity"), ${T0}, 0, ${r3(T0 + o.T)}, md_valeur(md_tr(${c}).property("ADBE Opacity"), ${r3(T0 + o.T + 0.5)}), null);`);
        for (const c of calquesVers) TR.push(`if (${c}.inPoint > md_cale(${T0})) ${c}.inPoint = md_cale(${T0});`);
        break;
      case 'passage-noir': case 'fondu-au-noir': case 'fondu-depuis-noir': case 'montee-du-noir': {
        TR.push(`(function () { var n = md_solide(${JS('Noir — ' + t.type + ' ' + T0 + ' s')}, "#000000", W, H);`);
        if (t.type === 'passage-noir') {
          const a = T0, b = r3(T0 + o.T_fondu), c = r3(b + o.noir), d = r3(c + o.T_fondu);
          TR.push(`  md_anime(n.o, ${a}, 0, ${b}, 100, null); md_anime(n.o, ${c}, 100, ${d}, 0, null); md_presence(n, ${a}, ${r3(d + 1 / fps)}); md_repere(n.l, ${a}, "passage-noir : linéaire ${o.T_fondu} s, noir ${o.noir} s, linéaire ${o.T_fondu} s");`);
          for (const cl of calquesDe) TR.push(`  if (${cl}.outPoint > md_cale(${b})) ${cl}.outPoint = md_cale(${b});`);
          for (const cl of calquesVers) TR.push(`  if (${cl}.inPoint < md_cale(${c})) ${cl}.inPoint = md_cale(${c});`);
        } else if (t.type === 'fondu-au-noir') {
          TR.push(`  md_anime(n.o, ${T0}, 0, ${r3(T0 + o.T)}, 100, null); md_presence(n, ${T0}, comp.duration); md_repere(n.l, ${T0}, "fondu-au-noir : linéaire ${o.T} s");`);
        } else if (t.type === 'fondu-depuis-noir') {
          const c = o.T >= 0.68 ? C('out-cubic') : 'null';
          TR.push(`  md_anime(n.o, ${T0}, 100, ${r3(T0 + o.T)}, 0, ${c}); md_presence(n, 0, ${r3(T0 + o.T + 1 / fps)}); md_repere(n.l, ${T0}, "fondu-depuis-noir : ${o.T >= 0.68 ? 'out-cubic' : 'linéaire'} ${o.T} s");`);
        } else {
          const Tm = r3(T_depuis(COURBES['in-out-cubic'].b, o.d1090));
          TR.push(`  md_saut(n.o, ${T0}, 100); md_anime(n.o, ${r3(T0 + o.noir)}, 100, ${r3(T0 + o.noir + Tm)}, 0, ${C('in-out-cubic')}); md_presence(n, ${T0}, ${r3(T0 + o.noir + Tm + 1 / fps)}); md_repere(n.l, ${T0}, "montee-du-noir : noir ${o.noir} s puis in-out-cubic ${Tm} s");`);
          for (const cl of calquesDe) TR.push(`  if (${cl}.outPoint > md_cale(${T0})) ${cl}.outPoint = md_cale(${T0});`);
        }
        TR.push(`})();`);
        break;
      }
      case 'glissade': case 'poussee': {
        const c = t.type === 'glissade' ? 'glissade' : 'poussee-ecran';
        const sgn = o.sens === 'droite' ? 1 : -1;
        TR.push(`// ${t.type} : ${c}, T ${o.T} s, d\u2019une largeur d\u2019image, horizontal${t.type === 'glissade' ? ', flou de bougé (intensité : convention)' : ''}`);
        for (const id of de) for (const pv of propsX(tous[id], ident(id))) TR.push(`md_anime(${pv}.x, ${T0}, md_valeur(${pv}.x, ${T0}), ${r3(T0 + o.T)}, md_valeur(${pv}.x, ${T0}) + ${sgn} * W, ${C(c)});`);
        for (const id of vers) for (const pv of propsX(tous[id], ident(id))) TR.push(`md_anime(${pv}.x, ${T0}, md_valeur(${pv}.x, ${r3(T0 + o.T)}) - ${sgn} * W, ${r3(T0 + o.T)}, md_valeur(${pv}.x, ${r3(T0 + o.T)}), ${C(c)});`);
        for (const c of calquesDe) TR.push(`${c}.outPoint = md_cale(${r3(T0 + o.T)});${t.type === 'glissade' ? ` ${c}.motionBlur = true;` : ''}`);
        for (const c of calquesVers) TR.push(`if (${c}.inPoint > md_cale(${T0})) ${c}.inPoint = md_cale(${T0});${t.type === 'glissade' ? ` ${c}.motionBlur = true;` : ''}`);
        if (t.type === 'glissade') flouBouge.add(120);
        break;
      }
      case 'bascule-lumiere': {
        const f = (t.options || {}).fond;
        TR.push(`(function () { var n = md_solide(${JS('Bascule de lumière ' + T0 + ' s')}, "#000000", W, H);${f && tous[f] ? ` n.l.moveBefore(${ident(f)}.l);` : ''}`);
        TR.push(`  md_anime(n.o, ${T0}, 0, ${r3(T0 + o.T)}, ${o.niveau}, ${C('in-out-sine')}); md_presence(n, ${T0}, comp.duration); md_repere(n.l, ${T0}, "bascule-lumiere : in-out-sine ${o.T} s"); })();`);
        if (!f) notes.push(`bascule-lumiere à ${T0} s : options.fond absent → le voile couvre tout`);
        break;
      }
      default: notes.push(`transition inconnue : ${t.type}`);
    }
  }

  // ── caméra ──
  if (cam) {
    const rec = cam.recette, o = parametres(rec, cam.options), t0 = cam.debut, t1 = cam.fin !== undefined ? cam.fin : comp.duree;
    recettesVues.add(rec);
    for (const pr of [...profondeurs].sort()) cameraKeys(phase.camera, camVar(pr), rec, o, t0, t1, pr, C, px);
  }

  // ── assemblage ──
  const utilisees = [...courbes].sort();
  const lignesCourbes = utilisees.map((n) => { const ae = easeAE(COURBES[n].b); return `//   ${n.padEnd(16)} (${COURBES[n].b.join(', ')})  sortie ${r3(ae.sortie.influence)} % × ${r3(ae.sortie.vitesse)} ; entrée ${r3(ae.entree.influence)} % × ${r3(ae.entree.vitesse)} — ${COURBES[n].n}`; });
  const obt = [...flouBouge];
  const tete = [
    `// ${nomComp} : script généré par build_motion.mjs (skill sebmake-motiondesign-likeapplepls) depuis ${source}.`,
    `// ExtendScript ES3 : After Effects (Fichier > Scripts > Exécuter le fichier de script) ou EffectCraft (script.run).`,
    `// Composition ${W} × ${H}, ${fps} i/s, ${comp.duree} s, époque ${comp.epoque}. 1 u = ${r3(U)} px (1 % du petit côté).`,
    `// Recettes : ${[...recettesVues].sort().join(', ')}.`,
    `// Courbes (cubic-bezier → KeyframeEase calculée par md_anime ; vitesses en multiple de la vitesse moyenne) :`,
    ...lignesCourbes,
    `// Relancer le script remplace la composition du même nom. Rien n'est enregistré : enregistrez le projet vous-même.`,
  ];
  const corps = [
    `(function () {`,
    `var NOM = ${JS(nomComp)}, W = ${W}, H = ${H}, U = ${r3(U)}, IPS = ${fps}, DUREE = ${comp.duree};`,
    `var THEME = ${JS({ repli: theme.couleurs.repli, repli_trait: theme.couleurs.repli_trait })};`,
    `var C = {`,
    utilisees.map((n) => `  ${JS(n)}: [${COURBES[n].b.join(', ')}]`).join(',\n'),
    `};`,
    MOTEUR.trim(),
    `try { app.beginUndoGroup(NOM); } catch (e0) {}`,
    `// relancer remplace la composition du même nom ; ses solides (sans fichier, utilisés par elle seule) partent avec elle, sinon ils resteraient orphelins dans le projet`,
    `for (var i0 = app.project.numItems; i0 >= 1; i0--) { var it0 = app.project.item(i0); if (it0 instanceof CompItem && it0.name === NOM) { var so0 = [];`,
    `  for (var j0 = 1; j0 <= it0.numLayers; j0++) { try { var s0 = it0.layer(j0).source; if (s0 && s0 instanceof FootageItem && !s0.file && s0.mainSource && s0.mainSource.color && s0.usedIn.length === 1) so0.push(s0); } catch (e3) {} }`,
    `  it0.remove(); for (var k0 = 0; k0 < so0.length; k0++) { try { so0[k0].remove(); } catch (e4) {} } } }`,
    `var comp = app.project.items.addComp(NOM, W, H, 1, DUREE, IPS);`,
    `var FD = comp.frameDuration;`,
    `comp.bgColor = md_rgb(${JS(couleur(theme, comp.fond, 'fond'))});`,
    `try { comp.openInViewer(); } catch (e1) {} // indispensable dans EffectCraft : sans comp active, interpolations et eases sont ignorées`,
    obt.length ? `comp.motionBlur = true; try { comp.shutterAngle = ${Math.max(...obt)}; comp.shutterPhase = ${-Math.max(...obt) / 2}; } catch (e2) {} // obturateur 118° mesuré (74 à 169°) ; phase centrée : convention` : `// pas de flou de bougé : aucune recette rapide qui le montre`,
    '',
    '// ═══ 1. Calques, de l\u2019arrière vers l\u2019avant ═══',
    ...phase.calques,
    '',
    '// ═══ 2. Parentage (nuls neutres : rien ne bouge) ═══',
    ...phase.parents,
    '',
    '// ═══ 3. Animations ═══',
    ...phase.anim,
    '',
    '// ═══ 4. Présence des calques (points d\u2019entrée et de sortie) ═══',
    ...phase.presence,
    ...phase.coupures,
    '',
    '// ═══ 5. Transitions ═══',
    ...phase.transitions,
    '',
    '// ═══ 6. Lumières (elles copient l\u2019élément animé, d\u2019où leur place à la fin) ═══',
    ...phase.complements,
    '',
    '// ═══ 7. Caméra ═══',
    ...phase.camera,
    '',
    `try { app.endUndoGroup(); } catch (e3) {}`,
    `return NOM + " : " + comp.numLayers + " calques, " + MD_CLES + " cl\\u00e9s" + (MD_REPLIS.length ? " ; replis : " + MD_REPLIS.join(" | ") : " ; aucun repli");`,
    `})();`,
  ];
  return { jsx: '\ufeff' + tete.join('\n') + '\n' + corps.join('\n') + '\n', notes, courbes: utilisees, recettes: [...recettesVues] };
}

// un élément ne suit la caméra globale que si sa présence croise la fenêtre de la caméra
function croiseCamera(pl, cam, comp) { const c0 = cam.debut || 0, c1 = cam.fin !== undefined ? cam.fin : comp.duree; return pl.debut < c1 && pl.fin > c0; }
function aVoile(e) { return e.recette === 'assombrir-autour' || (e.puis || []).some((q) => q.recette === 'assombrir-autour'); }
/** calques visibles d'un élément (fondus des transitions), en expressions JS */
function visibles(e, v) {
  let out;
  if (e.type === 'liste') out = Array.from({ length: (e.lignes || []).length }, (_, i) => `${v}.lignes[${i}].l`);
  else if (e.recette === 'carton-groupes') out = Array.from({ length: (e.groupes || [1]).length }, (_, i) => `${v}.groupes[${i}].l`);
  else if (e.recette === 'empilement') out = Array.from({ length: (e.fichiers || [1]).length }, (_, i) => `${v}.ecrans[${i}].l`);
  else if (e.recette === 'eclate') out = Array.from({ length: (e.pieces && e.pieces.length) || 3 }, (_, i) => `${v}.pieces[${i}].l`);
  else if (e.type === 'nul-camera') out = [];
  else { out = [`${v}.l`]; if (e.type === 'chiffre' && e.libelle) out.push(`${v}_lib.l`); if (e.recette === 'produit-flotte' && parametres('produit-flotte', e.options || {}).ombre) out.push(`${v}_ombre.l`); }
  if (aVoile(e)) out.push(`${v}_voile.l`);
  return out;
}
/** tous les calques d'un élément (points d'entrée et de sortie) */
function tousCalques(e, v) {
  const out = visibles(e, v);
  if (e.recette === 'defilement') out.push(`${v}_fenetre.l`);
  if (aVoile(e) && (e.puis || []).concat(e.recette === 'assombrir-autour' ? [{ recette: 'assombrir-autour', options: e.options }] : []).some((q) => q.recette === 'assombrir-autour' && parametres('assombrir-autour', q.options || {}).flou > 0)) out.push(`${v}_flou.l`);
  return out;
}
function cyOf(e, Y) { return Y((e.position || [50, 50])[1]); }
function cibleDe(e, v) { return v; }
/** début du libellé après le début du chiffre : le retard mesuré va du milieu du fondu du chiffre au milieu de celui du libellé */
export function debutLibelle(cChiffre, d1090Chiffre, cLib, retard, d1090Lib) {
  const mc = cChiffre ? T_depuis(COURBES[cChiffre].b, d1090Chiffre) * tempsA(COURBES[cChiffre].b, 0.5) : 0;
  const ml = T_depuis(COURBES[cLib].b, d1090Lib) * tempsA(COURBES[cLib].b, 0.5);
  return Math.max(0, r3(mc + retard - ml));
}
function libelle(A, e, v, t0, debutLib, retard, d1090, courbe, pl, C) {
  const T = r3(T_depuis(COURBES[courbe].b, d1090)), t1 = r3(t0 + debutLib);
  A.push(`md_anime(${v}_lib.o, ${t1}, 0, ${r3(t1 + T)}, 100, ${C(courbe)}); md_presence(${v}_lib, ${t1}, ${pl.fin}); md_repere(${v}_lib.l, ${t1}, ${JS('libellé : milieu du fondu +' + retard + ' s après celui du chiffre, fondu sur place ' + T + ' s')});`);
  if (pl.sortie === 'fondu') A.push(`md_anime(${v}_lib.o, ${pl.sortieDebut}, 100, ${r3(pl.sortieDebut + 1.15)}, 0, null);`);
}
/** calques d'un élément (pour le parentage et les transitions), en expressions JS */
function layerList(e, v) {
  if (e.type === 'liste') return Array.from({ length: (e.lignes || []).length }, (_, i) => `${v}.lignes[${i}].l`);
  if (e.recette === 'carton-groupes') return [`${v}.ligne.l`];
  if (e.recette === 'empilement') return [`${v}.rangee.l`];
  if (e.recette === 'eclate') return Array.from({ length: (e.pieces && e.pieces.length) || 3 }, (_, i) => `${v}.pieces[${i}].l`);
  const out = [`${v}.l`];
  if (e.type === 'chiffre' && e.libelle) out.push(`${v}_lib.l`);
  if (e.recette === 'defilement') out.push(`${v}_fenetre.l`);
  if (e.recette === 'produit-flotte' && parametres('produit-flotte', e.options || {}).ombre) out.push(`${v}_ombre.l`);
  return out;
}
/** éléments dont on anime la position X (transitions) */
function propsX(e, v) {
  if (e.type === 'liste') return Array.from({ length: (e.lignes || []).length }, (_, i) => `${v}.lignes[${i}]`);
  if (e.recette === 'carton-groupes') return [`${v}.ligne`];
  if (e.recette === 'empilement') return [`${v}.rangee`];
  if (e.recette === 'eclate') return Array.from({ length: (e.pieces && e.pieces.length) || 3 }, (_, i) => `${v}.pieces[${i}]`);
  const out = [v];
  if (e.type === 'chiffre' && e.libelle) out.push(`${v}_lib`);
  if (e.recette === 'defilement') out.push(`${v}_fenetre`);
  if (e.recette === 'produit-flotte' && parametres('produit-flotte', e.options || {}).ombre) out.push(`${v}_ombre`);
  return out;
}
function cameraKeys(A, v, rec, o, t0, t1, pr, C, px) {
  const s1 = r3(100 * Math.pow(rec === 'camera-poussee' || rec === 'camera-recul' || rec === 'camera-se-pose' ? o.facteur : 1, pr));
  A.push(`md_repere(${v}.l, ${r3(t0)}, ${JS(rec + (pr !== 1 ? ' (profondeur ' + pr + ')' : ''))});`);
  if (rec === 'camera-poussee') A.push(`md_anime(${v}.s, ${r3(t0)}, [100, 100, 100], ${r3(t1)}, [${s1}, ${s1}, 100], null); // linéaire, du début à la fin du plan`);
  else if (rec === 'camera-recul') A.push(`md_anime(${v}.s, ${r3(t0)}, [100, 100, 100], ${r3(t1)}, [${s1}, ${s1}, 100], ${C('ease-out')}); // recul qui freine`);
  else if (rec === 'camera-se-pose') {
    const T = r3(T_depuis(COURBES['out-cubic'].b, o.d1090)), d = o.deplacement || [0, 0];
    A.push(`md_anime(${v}.s, ${r3(t0)}, [100, 100, 100], ${r3(t0 + T)}, [${s1}, ${s1}, 100], ${C('out-cubic')});`);
    if (d[0]) A.push(`md_anime(${v}.x, ${r3(t0)}, ${v}.cx, ${r3(t0 + T)}, ${v}.cx + ${r3(px(d[0]) * pr)}, ${C('out-cubic')});`);
    if (d[1]) A.push(`md_anime(${v}.y, ${r3(t0)}, ${v}.cy, ${r3(t0 + T)}, ${v}.cy + ${r3(px(d[1]) * pr)}, ${C('out-cubic')});`);
  } else if (rec === 'camera-travelling') {
    const d = o.direction || [-1, 0], n = Math.hypot(d[0], d[1]) || 1, dist = px(o.vitesse) * (t1 - t0) * pr;
    if (d[0]) A.push(`md_anime(${v}.x, ${r3(t0)}, ${v}.cx, ${r3(t1)}, ${v}.cx + ${r3(dist * d[0] / n)}, null); // linéaire ; profondeur ${pr}`);
    if (d[1]) A.push(`md_anime(${v}.y, ${r3(t0)}, ${v}.cy, ${r3(t1)}, ${v}.cy + ${r3(dist * d[1] / n)}, null);`);
  }
}

/** Contrôle de syntaxe ES3 (heuristique) : renvoie la liste des écarts trouvés */
export function verifierES3(code) {
  const sansChaines = code.replace(/\/\/[^\n]*/g, '').replace(/"(?:\\.|[^"\\])*"/g, '""').replace(/'(?:\\.|[^'\\])*'/g, "''");
  const regles = [
    [/\blet\s/, 'let'], [/\bconst\s/, 'const'], [/=>/, 'fonction fléchée'], [/`/, 'gabarit ``'], [/\bJSON\./, 'JSON natif'],
    [/\.forEach\(|\.map\(|\.filter\(|\.reduce\(|\.some\(|\.every\(/, 'méthode de tableau ES5'], [/\.trim\(\)/, 'trim (ES5)'],
    [/Object\.keys|Array\.isArray|Date\.now/, 'fonction ES5'], [/,\s*[}\]]/, 'virgule finale'], [/\?\./, 'chaînage optionnel'], [/\.\.\./, 'décomposition'],
    [/\bclass\s/, 'class'], [/\.(default|class|import|export|final|int|char|float|long|short|byte|native|static|super|throws|transient|volatile|goto|enum|package|private|protected|public|interface|boolean|double|abstract|synchronized|implements|extends|debugger)\b/, 'mot réservé ES3 en propriété'],
  ];
  const ecarts = [];
  for (const [re, nom] of regles) { const m = sansChaines.match(re); if (m) { const ligne = sansChaines.slice(0, m.index).split('\n').length; ecarts.push(`${nom} (ligne ${ligne})`); } }
  try { new Function(code.replace(/^\ufeff/, '')); } catch (e) { ecarts.push('syntaxe : ' + e.message); }
  return ecarts;
}

/** table des recettes exportée pour check_motion.py */
export function exporterRecettes() {
  const r = {};
  for (const [k, v] of Object.entries(RECETTES)) r[k] = { famille: v.famille, types: v.types, majeur: v.majeur, epoque: v.epoque, mesure: v.mesure, params: v.params };
  const t = {};
  for (const [k, v] of Object.entries(TRANSITIONS)) t[k] = { mesure: v.mesure, params: v.params };
  return { recettes: r, transitions: t, courbes: Object.fromEntries(Object.entries(COURBES).map(([k, v]) => [k, { bezier: v.b, ae: easeAE(v.b), part_10_90: r3(part(v.b)), part_visible: r3(part(v.b, 0.02, 0.98)), n: v.n }])) };
}
