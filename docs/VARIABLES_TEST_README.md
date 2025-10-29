# Fonctionnalité : Variables de Test

## Description

Cette fonctionnalité permet d'associer des variables personnalisées aux tests, directement depuis les pages d'ajout et de modification de tests.

## Fonctionnalités

### 1. Ajout de variables

- **Bouton "Ajouter une variable"** : Situé juste avant le bouton "Ajouter une action" dans la section des actions du test
- **Modale d'ajout** : Formulaire simple avec un seul champ pour le nom de la variable
- **Validation** : 
  - Caractères alphanumériques et underscore uniquement (regex: `[a-zA-Z0-9_]+`)
  - Vérification d'unicité (pas de doublons)
  - Nom obligatoire

### 2. Affichage des variables

- **Format badge/tag** : Les variables sont affichées sous forme de badges avec icône
- **Position** : Juste au-dessus de la liste des actions dans la même card
- **Visibilité** : Affichées uniquement s'il y a au moins une variable

### 3. Suppression de variables

- **Bouton de suppression** : Croix sur chaque badge de variable
- **Confirmation** : Demande de confirmation avant suppression

### 4. Persistance

- **Collection MongoDB** : Le champ `variables` (tableau de strings) a été ajouté à la collection `tests`
- **API** : Les endpoints POST et PUT de `/api/tests` gèrent maintenant le champ `variables`
- **Modèle** : La classe `Test` dans `models/test.py` supporte les variables

## Structure de données

### Collection `tests` - Nouveau champ

```json
{
  "_id": ObjectId,
  "campainId": ObjectId,
  "userId": ObjectId,
  "dateCreated": Date,
  "name": String,
  "description": String,
  "actions": Array,
  "variables": ["variable1", "variable2", "variable3"]  // NOUVEAU
}
```

## Pages modifiées

### 1. `templates/test_add.html`
- Ajout du bouton "Ajouter une variable"
- Ajout de la modale d'ajout de variable
- Ajout de la zone d'affichage `variablesList`
- Ajout du code JavaScript pour gérer les variables
- Modification de la fonction de soumission pour inclure les variables

### 2. `templates/test_edit.html`
- Ajout du bouton "Ajouter une variable"
- Ajout de la modale d'ajout de variable
- Ajout de la zone d'affichage `variablesList`
- Ajout du code JavaScript pour gérer les variables
- Modification de la fonction de chargement pour récupérer les variables existantes
- Modification de la fonction de mise à jour pour inclure les variables

### 3. `models/test.py`
- Ajout du paramètre `variables=None` à la méthode `create()`
- Ajout du champ `variables` dans `test_data` avec valeur par défaut `[]`
- Ajout de la gestion du champ `variables` dans la méthode `update()`

### 4. `routes/tests_routes.py`
- Modification de `create_test()` pour accepter et transmettre le champ `variables`
- Utilisation de `data.get('variables', [])` pour assurer la compatibilité

## Compatibilité

### Tests existants
✅ Les tests existants sans le champ `variables` continueront de fonctionner normalement
- Le champ est optionnel avec une valeur par défaut de `[]`
- Pas de migration de base de données nécessaire

### API
✅ L'API reste rétrocompatible
- Le champ `variables` est optionnel dans les requêtes POST et PUT
- Les anciennes requêtes sans ce champ fonctionneront toujours

## Utilisation

### Ajouter une variable à un test (nouveau test)

1. Naviguer vers la page "Ajouter un test" depuis une campagne
2. Remplir les informations du test (nom, description)
3. Cliquer sur le bouton "Ajouter une variable"
4. Saisir le nom de la variable (ex: `ma_variable`)
5. Cliquer sur "Ajouter"
6. La variable apparaît sous forme de badge bleu avec une icône tag
7. Ajouter les actions du test
8. Créer le test

### Ajouter une variable à un test existant

1. Naviguer vers la page "Modifier un test" depuis une campagne
2. Les variables existantes sont chargées et affichées automatiquement
3. Cliquer sur le bouton "Ajouter une variable"
4. Saisir le nom de la variable
5. Cliquer sur "Ajouter"
6. La variable apparaît dans la liste
7. Enregistrer les modifications

### Supprimer une variable

1. Sur la page d'ajout ou de modification de test
2. Cliquer sur la croix du badge de la variable à supprimer
3. Confirmer la suppression
4. La variable disparaît de la liste

## Cas d'erreur gérés

- ❌ Nom de variable vide : "Veuillez saisir un nom de variable"
- ❌ Nom de variable non alphanumérique : "Le nom de la variable doit contenir uniquement des caractères alphanumériques et underscore"
- ❌ Variable déjà existante : "Cette variable existe déjà"

## Tests à effectuer

### Tests fonctionnels
- [ ] Créer un test avec des variables
- [ ] Créer un test sans variable
- [ ] Modifier un test et ajouter des variables
- [ ] Modifier un test et supprimer des variables
- [ ] Vérifier la validation des noms de variables (caractères spéciaux, espaces, etc.)
- [ ] Vérifier la détection de doublons
- [ ] Vérifier la persistance en base de données

### Tests de régression
- [ ] Charger un test créé avant cette fonctionnalité (sans le champ `variables`)
- [ ] Modifier un ancien test et enregistrer les modifications
- [ ] Vérifier que la liste des tests dans la campagne s'affiche correctement
- [ ] Vérifier que les actions des tests continuent de fonctionner

## Notes techniques

- Les variables sont stockées sous forme de tableau de strings simples
- Pas de lien avec la collection `variables` de l'application (variables multi-environnements)
- Les variables sont spécifiques à chaque test
- L'ordre des variables n'est pas garanti (tableau non ordonné)

## Améliorations futures possibles

- Validation avancée des noms de variables (longueur max, préfixes interdits, etc.)
- Export/import de variables entre tests
- Recherche de variables dans un test
- Utilisation des variables dans les actions (remplacement automatique)
- Statistiques sur l'utilisation des variables
