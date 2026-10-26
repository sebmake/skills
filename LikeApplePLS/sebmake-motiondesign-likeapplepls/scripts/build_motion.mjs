#!/usr/bin/env node
// build_motion.mjs : motion.json → script .jsx (ExtendScript ES3, After Effects et EffectCraft).
//
// Usage :
//   node build_motion.mjs <motion.json> [-o sortie.jsx] [--prefixe TEST-] [--relatif]
//       écrit le script (par défaut à côté du motion.json, même nom en .jsx), puis le contrôle ES3.
//       Chaque fichier est cherché relatif au script (After Effects), puis à son chemin absolu (EffectCraft) ;
//       --relatif n'écrit aucun chemin absolu (script à partager : After Effects seulement le retrouve)
//   node build_motion.mjs <motion.json> --plan
//       imprime le plan temporel en JSON (utilisé par check_motion.py)
//   node build_motion.mjs --recettes [sortie.json]
//       exporte la table des recettes, des transitions et des courbes (lue par check_motion.py)
//   node build_motion.mjs --liste
//       liste les recettes et les transitions, avec leurs comptes
//
// Les chemins de fichiers du motion.json sont relatifs à son dossier ; le script reçoit des chemins absolus.
// Codes de sortie : 0 succès ; 1 erreur de lecture ou de génération ; 2 écart ES3 dans le script produit.
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { generer, plan, verifierES3, exporterRecettes, RECETTES, TRANSITIONS } from './motion_lib.mjs';

const ici = path.dirname(fileURLToPath(import.meta.url));
const args = process.argv.slice(2);
const opt = (nom) => { const i = args.indexOf(nom); return i >= 0 ? args[i + 1] : undefined; };
const drapeau = (nom) => args.includes(nom);

function sortir(code, msg) { if (msg) (code ? console.error : console.log)(msg); process.exit(code); }

if (drapeau('--recettes')) {
  const i = args.indexOf('--recettes');
  const dest = args[i + 1] && !args[i + 1].startsWith('--') ? args[i + 1] : path.join(ici, 'recettes.json');
  fs.writeFileSync(dest, JSON.stringify(exporterRecettes(), null, 1) + '\n');
  sortir(0, 'écrit : ' + dest);
}
if (drapeau('--liste')) {
  for (const [k, v] of Object.entries(RECETTES)) console.log(`${k.padEnd(22)} ${v.famille.padEnd(9)} ${v.majeur ? 'majeur ' : '       '} ${v.epoque.padEnd(9)} ${v.mesure.slice(0, 110)}`);
  console.log('');
  for (const [k, v] of Object.entries(TRANSITIONS)) console.log(`transition ${k.padEnd(18)} ${v.mesure.slice(0, 120)}`);
  sortir(0);
}

const entree = args.find((a) => a.endsWith('.json'));
if (!entree) sortir(1, 'usage : node build_motion.mjs <motion.json> [-o sortie.jsx] [--prefixe TEST-] [--plan]');
let motion;
try { motion = JSON.parse(fs.readFileSync(entree, 'utf8')); } catch (e) { sortir(1, `lecture impossible de ${entree} : ${e.message}`); }
const base = path.dirname(path.resolve(entree));
const destination = opt('-o') || entree.replace(/\.json$/, '.jsx');
// [chemin relatif au script produit, chemin absolu] : After Effects retrouve les fichiers à côté du script, EffectCraft par l'absolu.
const resoudre = (f) => { const abs = path.isAbsolute(f) ? f : path.resolve(base, f); return [path.relative(path.dirname(path.resolve(destination)), abs).split(path.sep).join('/'), drapeau('--relatif') ? '' : abs]; };

if (drapeau('--plan')) {
  try { process.stdout.write(JSON.stringify(plan(motion), null, 1) + '\n'); process.exit(0); } catch (e) { sortir(1, 'plan impossible : ' + e.message); }
}

let res;
try { res = generer(motion, { base, prefixe: opt('--prefixe') || '', source: path.basename(entree), resoudre }); }
catch (e) { sortir(1, 'génération impossible : ' + e.message); }
const dest = destination;
fs.writeFileSync(dest, res.jsx, 'utf8');
const ecarts = verifierES3(res.jsx);
console.log(`écrit : ${dest} (${res.jsx.split('\n').length} lignes)`);
console.log(`recettes : ${res.recettes.join(', ')}`);
console.log(`courbes : ${res.courbes.join(', ')}`);
for (const n of res.notes) console.log('note : ' + n);
if (ecarts.length) { for (const e of ecarts) console.error('ES3 : ' + e); process.exit(2); }
console.log('ES3 : aucun écart (let, const, =>, ``, JSON, méthodes ES5, virgules finales, mots réservés ; syntaxe analysée)');
