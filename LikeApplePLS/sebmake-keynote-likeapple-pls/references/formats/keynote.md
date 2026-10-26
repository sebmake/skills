# Format Keynote (.key, 16:9)

Keynote ouvre les .pptx. On construit donc le .pptx avec `build_deck.js` (voir `powerpoint.md`, section 1), puis on le passe dans Keynote.

## 1. Ouvrir le .pptx dans Keynote

- Fichier > Ouvrir > `sortie.pptx` (ou glisser le fichier sur l'icône de Keynote).
- Keynote crée un nouveau document. Le .pptx d'origine n'est pas modifié.
- Keynote affiche alors la liste des problèmes d'import (polices remplacées, effets non pris en charge). La lire en entier. Elle reste accessible ensuite par le menu Présentation (EN : View > Show Document Warnings).
- Enregistrer : Fichier > Enregistrer. Le fichier devient un .key.
- Vérifier la taille : inspecteur Document > Taille de la diapositive. Le rapport doit être 16:9. Le nombre de pixels dépend de la conversion (le .pptx mesure 10 × 5,625 pouces) : ne pas le changer s'il est bien en 16:9, car Keynote redimensionnerait le contenu.

## 2. Ce qui se convertit bien, ce qui se convertit mal

| Élément | Résultat | Quoi faire |
|---|---|---|
| Format 16:9, fonds unis, formes, textes | Bien | Rien |
| Couleurs HEX du thème | Bien | Contrôler une ou deux couleurs |
| Notes du présentateur | Bien : elles deviennent les notes de l'intervenant | Relire la mise en forme |
| Polices installées sur le Mac | Bien | Rien |
| Polices absentes du Mac | Remplacées à l'ouverture | Installer la police, puis rouvrir le .pptx (pas le .key). Ou Format > Police > Remplacer les polices |
| Animations PowerPoint | Variable : les fondus du moteur passent en général en Dissolution, parfois perdus | Vérifier chaque slide qui a un `build` ; reposer à la main celles qui manquent (section 4) |
| Graphiques natifs | Variable | Vérifier qu'aucune graduation n'est apparue si la grammaire n'en veut pas |
| Images SVG | Parfois converties en image fixe | Vérifier la netteté |

Jamais de police Apple (SF, New York) en remplacement, même si le Mac les propose.

## 3. Conversion automatique en .key (si Keynote est installé)

À faire seulement si Keynote est présent chez l'utilisateur. Vérifier d'abord :

```bash
open -Ra Keynote && echo "Keynote présent" || echo "Keynote absent"
```

L'édition classique a l'identifiant `com.apple.iWork.Keynote`. L'édition Creator Studio s'appelle « Keynote Creator Studio » (identifiant `com.apple.Keynote`). `tell application "Keynote"` trouve les deux.

Script AppleScript à écrire dans le dossier de travail (`pptx-vers-key.applescript`) :

```applescript
-- Usage : osascript pptx-vers-key.applescript /chemin/absolu/entree.pptx /chemin/absolu/sortie.key
on run argv
	if (count of argv) < 2 then error "Usage : osascript pptx-vers-key.applescript entree.pptx sortie.key"
	set entree to POSIX file (item 1 of argv)
	set sortie to POSIX file (item 2 of argv)
	tell application "Keynote"
		activate
		set doc to open entree
		set larg to width of doc
		set haut to height of doc
		set nb to count of slides of doc
		set avecNotes to 0
		repeat with s in slides of doc
			if (presenter notes of s as text) is not "" then set avecNotes to avecNotes + 1
		end repeat
		-- Optionnel, une ligne par slide concernée :
		-- set transition properties of slide 3 of doc to {transition effect:dissolve, transition duration:0.4}
		-- set transition properties of slide 7 of doc to {transition effect:magic move, transition duration:1.0}
		save doc in sortie
		close doc saving no
	end tell
	return "Slides : " & nb & " | avec notes : " & avecNotes & " | taille : " & larg & " x " & haut
end run
```

- Le script n'a été ni compilé ni exécuté contre Keynote (Keynote absent de la machine où la skill a été écrite). Le lancer seulement avec l'accord de l'utilisateur, et relire l'erreur s'il échoue.
- Au premier lancement, macOS demande si le terminal (ou Claude) peut contrôler Keynote. C'est l'utilisateur qui répond. La skill ne touche jamais aux réglages de confidentialité.
- Si Keynote affiche une fenêtre (avertissements d'import, premier lancement), le script attend. Prévenir l'utilisateur qu'il doit la fermer.
- Résultat attendu : une taille en 16:9 (largeur ÷ hauteur = 1,78), et autant de slides avec notes que de slides avec script.
- Les transitions sont pilotables par AppleScript. Les étapes (builds) ne le sont pas : le dictionnaire de Keynote ne les expose pas.

## 4. Les étapes (builds) à vérifier dans Keynote

Le .pptx contient des fondus entre slides et des apparitions au clic (champ `build`). Keynote les convertit le plus souvent en Dissolution. Vérifier slide par slide, et reposer à la main ce qui manque :

1. Sélectionner l'objet > inspecteur Animer > Composition d'entrée (EN : Build In) > Ajouter un effet.
2. Choisir Apparition (sec, EN : Appear) ou Dissolution (doux, EN : Dissolve). Durée : 0,3 à 0,5 s.
3. Liste : régler la livraison par puce ou par paragraphe (EN : Delivery > By Bullet).
4. Ordre et déclenchement : bouton Ordre de composition (EN : Build Order), départ Au clic.

| Archétype | Étapes | Effet |
|---|---|---|
| A1 Carte-titre, A4 Phrase-thèse | Le texte seul, au moment où il est dit | Dissolution |
| A5 Gros chiffre | Le chiffre, puis le libellé (ou l'inverse, choisi une fois pour tout le deck) | Dissolution, puis Apparition |
| A6 Graphique comparatif | L'autre (en gris), puis soi, puis l'écart écrit (2 à 4 temps) | Dissolution par élément |
| A7 Liste sans puces | Une ligne par clic, au rythme de la voix | Dissolution par puce |
| A8 Liste à coches | Les coches une à une, ou toutes sur la phrase de promesse | Apparition |
| A9 Objet + texte | L'objet, puis le texte | Dissolution |
| A11 Schéma à bloc surligné | Un bloc allumé à la fois | Apparition |
| A14 Bento | La tuile centrale, puis les autres | Dissolution |
| A19 Prix | Le nom, puis le prix (un prix d'ancrage avant, si l'utilisateur l'a fourni) | Apparition |
| A20 Disponibilité | Le grand mot change sur la même image | Deux slides et la transition Déplacement magique (EN : Magic Move) |

Transitions entre slides : aucune, ou Dissolution courte. Pas d'effet spectaculaire.

Lister les apparitions prévues (champ `build` de `deck.json`), avec l'effet de la table :

```bash
node "$SKILL/scripts/export_script.js" deck.json --etapes
```

Donner cette liste à l'utilisateur.

## 5. Présenter

- Lancer : Lecture > Lire le diaporama.
- Écran de l'intervenant : Lecture > Personnaliser l'écran de l'intervenant (EN : Play > Customize Presenter Display). Il montre les notes, la slide suivante et l'heure.
- Répéter : Lecture > Répéter le diaporama. Comparer avec la somme des `duree_s`.
- En visio : Lecture > Lire le diaporama dans une fenêtre, puis partager cette fenêtre seulement.

## 6. Check-list avant de livrer

- [ ] Taille de la diapositive en 16:9.
- [ ] La liste des problèmes d'import a été lue ; aucune police remplacée sans accord.
- [ ] Aucun logo, image ou police Apple ; seulement l'habillage de l'utilisateur.
- [ ] Les notes de l'intervenant contiennent le script de chaque slide, le relais et la durée.
- [ ] Les étapes de la table sont posées, ou leur liste est remise à l'utilisateur.
- [ ] Aucun chiffre, prix, date ou témoignage inventé ; les `[À FOURNIR]` restants sont signalés.
- [ ] Tutoiement ou vouvoiement constant, comme choisi au départ.
- [ ] Une répétition chronométrée tient dans le temps prévu.
