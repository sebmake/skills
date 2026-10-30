#!/usr/bin/env node
// build_motion.mjs: motion.json → .jsx script (ExtendScript ES3, After Effects and EffectCraft).
//
// Usage:
//   node build_motion.mjs <motion.json> [-o output.jsx] [--prefixe TEST-] [--relatif]
//       writes the script (by default next to motion.json, same name with .jsx), then runs the ES3 check.
//       Each file is looked up relative to the script (After Effects), then by its absolute path (EffectCraft);
//       --relatif writes no absolute path (a script to share: only After Effects finds the files)
//   node build_motion.mjs <motion.json> --plan
//       prints the timing plan as JSON (used by check_motion.py)
//   node build_motion.mjs --recettes [output.json]
//       exports the table of recipes, transitions and curves (read by check_motion.py)
//   node build_motion.mjs --liste
//       lists the recipes and transitions, with their counts
//
// File paths in motion.json are relative to its folder; the script receives absolute paths.
// Exit codes: 0 success; 1 read or generation error; 2 ES3 problem in the generated script.
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
  sortir(0, 'written: ' + dest);
}
if (drapeau('--liste')) {
  for (const [k, v] of Object.entries(RECETTES)) console.log(`${k.padEnd(22)} ${v.famille.padEnd(9)} ${v.majeur ? 'major  ' : '       '} ${v.epoque.padEnd(9)} ${v.mesure.slice(0, 110)}`);
  console.log('');
  for (const [k, v] of Object.entries(TRANSITIONS)) console.log(`transition ${k.padEnd(18)} ${v.mesure.slice(0, 120)}`);
  sortir(0);
}

const entree = args.find((a) => a.endsWith('.json'));
if (!entree) sortir(1, 'usage: node build_motion.mjs <motion.json> [-o output.jsx] [--prefixe TEST-] [--plan]');
let motion;
try { motion = JSON.parse(fs.readFileSync(entree, 'utf8')); } catch (e) { sortir(1, `cannot read ${entree}: ${e.message}`); }
const base = path.dirname(path.resolve(entree));
const destination = opt('-o') || entree.replace(/\.json$/, '.jsx');
// [path relative to the generated script, absolute path]: After Effects finds files next to the script, EffectCraft by the absolute path.
const resoudre = (f) => { const abs = path.isAbsolute(f) ? f : path.resolve(base, f); return [path.relative(path.dirname(path.resolve(destination)), abs).split(path.sep).join('/'), drapeau('--relatif') ? '' : abs]; };

if (drapeau('--plan')) {
  try { process.stdout.write(JSON.stringify(plan(motion), null, 1) + '\n'); process.exit(0); } catch (e) { sortir(1, 'cannot build the plan: ' + e.message); }
}

let res;
try { res = generer(motion, { base, prefixe: opt('--prefixe') || '', source: path.basename(entree), resoudre }); }
catch (e) { sortir(1, 'generation failed: ' + e.message); }
const dest = destination;
fs.writeFileSync(dest, res.jsx, 'utf8');
const ecarts = verifierES3(res.jsx);
console.log(`written: ${dest} (${res.jsx.split('\n').length} lines)`);
console.log(`recipes: ${res.recettes.join(', ')}`);
console.log(`curves: ${res.courbes.join(', ')}`);
for (const n of res.notes) console.log('note: ' + n);
if (ecarts.length) { for (const e of ecarts) console.error('ES3: ' + e); process.exit(2); }
console.log('ES3: no problem found (let, const, =>, ``, JSON, ES5 methods, trailing commas, reserved words; syntax parsed)');
