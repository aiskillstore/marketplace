# Catalogue des glissements sémantiques

Guide pour détecter et corriger les dérives de sens lors de la synthèse.

## Types de glissements

### 1. Amalgame

**Définition** : Fusionner deux concepts distincts.

**Exemple** :
- Source : "simplification des procédures"
- Glissement : "dérégulation"

**Correction** : Vérifier que les termes utilisés correspondent exactement au concept source.

### 2. Réduction

**Définition** : Réduire un ensemble à l'un de ses éléments.

**Exemple** :
- Source : "paquet législatif multi-volets (IA, données, cybersécurité)"
- Glissement : "loi sur l'IA"

**Correction** : Préserver la complexité ou signaler explicitement la simplification.

### 3. Surinterprétation

**Définition** : Attribuer au texte ce qu'il ne dit pas.

**Exemple** :
- Source : "Le ministre a évoqué cette possibilité"
- Glissement : "Le ministre a annoncé cette mesure"

**Correction** : Distinguer ce qui est dit, suggéré, et conclu.

### 4. Omission

**Définition** : Effacer des nuances ou des réserves.

**Exemple** :
- Source : "efficace sous certaines conditions"
- Glissement : "efficace"

**Correction** : Préserver les modalités et les conditions.

### 5. Inversion de polarité

**Définition** : Inverser le sens positif/négatif.

**Exemple** :
- Source : "malgré les progrès, des défis persistent"
- Glissement : "grâce aux progrès, les défis diminuent"

**Correction** : Respecter l'orientation argumentative.

### 6. Généralisation abusive

**Définition** : Étendre une affirmation au-delà de son champ.

**Exemple** :
- Source : "certaines PME bénéficient"
- Glissement : "les entreprises bénéficient"

**Correction** : Conserver les quantificateurs et les restrictions.

### 7. Aplatissement temporel

**Définition** : Effacer la dimension temporelle.

**Exemple** :
- Source : "sera mis en œuvre progressivement d'ici 2027"
- Glissement : "est mis en œuvre"

**Correction** : Préserver les marqueurs temporels.

### 8. Substitution d'agent

**Définition** : Changer qui fait l'action.

**Exemple** :
- Source : "La Commission propose"
- Glissement : "L'UE décide"

**Correction** : Identifier précisément l'acteur responsable.

## Protocole de vérification

### Étape 1 : Repérage

Pour chaque phrase de la synthèse, identifier :
- Le concept source correspondant
- Les modifications apportées

### Étape 2 : Classification

Classer chaque modification :
- **Légitime** : reformulation fidèle
- **À risque** : simplification acceptable mais à signaler
- **Glissement** : dérive à corriger

### Étape 3 : Correction

Pour chaque glissement :
- Revenir au texte source
- Reformuler fidèlement
- Si impossible, signaler l'interprétation

## Indicateurs de vigilance

### Mots-drapeaux (souvent sources de glissements)

| Mot source | Glissement fréquent |
|------------|---------------------|
| simplifier | déréglementer |
| optimiser | supprimer |
| adapter | transformer |
| certains | tous |
| pourrait | va |
| propose | impose |
| étudie | décide |

### Structures à risque

- Négations transformées en affirmations
- Conditionnels devenus indicatifs
- Pluriels réduits à singuliers
- Nuances modales effacées

## Checklist finale

Avant de valider une synthèse :

- [ ] Chaque affirmation a une source identifiable
- [ ] Les quantificateurs sont préservés
- [ ] Les modalités (possible, probable, certain) sont respectées
- [ ] Les acteurs sont correctement attribués
- [ ] La temporalité est fidèle
- [ ] Les réserves et conditions sont mentionnées
