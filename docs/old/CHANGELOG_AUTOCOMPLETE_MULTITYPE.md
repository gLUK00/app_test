# Changelog - Autocomplétion Multi-Types

## Version 2.0 - Support Multi-Types pour l'Autocomplétion

### 🎯 Objectif

Améliorer le système d'autocomplétion des variables pour supporter plusieurs types de suggestions avec des couleurs et des formats d'insertion distincts.

### ✨ Nouvelles Fonctionnalités

#### 1. Support de Plusieurs Types de Suggestions

Le plugin `variable-autocomplete.js` supporte maintenant trois types de variables :

- **Variables TestGyver** (globales)
  - Couleur : Bleu (#0d6efd)
  - Format d'insertion : `{{variable_name}}`
  - Icône : `fa-database`
  - Source : API des variables racines

- **Variables du Test** (locales)
  - Couleur : Vert (#198754)
  - Format d'insertion : `{{app.variable_name}}`
  - Icône : `fa-vial`
  - Source : Variables définies dans le test en cours

- **Variables de Collection** (contexte)
  - Couleur : Rouge (#dc3545)
  - Format d'insertion : `{{test.variable_name}}`
  - Icône : `fa-layer-group`
  - Source : Variables prédéfinies (test_id, campain_id)
  - Variables disponibles automatiquement

#### 2. Interface Améliorée

- **Groupement visuel** : Les suggestions sont organisées par type avec des séparateurs colorés
- **En-têtes distincts** : Chaque groupe a son propre en-tête avec icône et label
- **Bordures colorées** : Les suggestions ont une bordure gauche de la couleur de leur type
- **Mise en surbrillance** : La correspondance du texte recherché est mise en évidence

#### 3. Mise à Jour Dynamique

Les variables du test sont automatiquement mises à jour lors :
- De l'ajout d'une nouvelle variable au test
- De la suppression d'une variable du test
- Du chargement d'un test existant (mode édition)

### 📝 Fichiers Modifiés

#### JavaScript

**`static/js/variable-autocomplete.js`**
- Ajout de `variablesByType` pour stocker les variables par type
- Ajout de `suggestionTypes` pour la configuration des types
- Nouvelle méthode `setVariables(type, variables)` pour définir dynamiquement les variables
- Refactorisation de `showSuggestions()` pour gérer les groupes
- Mise à jour de `insertVariable()` pour utiliser le bon format selon le type

#### CSS

**`static/css/custom.css`**
- Nouveaux styles pour `.variable-suggestions-container`
- Nouveaux styles pour `.variable-suggestions-group`
- Styles des en-têtes avec support des couleurs dynamiques
- Styles des suggestions avec bordures colorées
- Amélioration de la hauteur maximale (400px au lieu de 300px)

#### HTML

**`templates/test_add.html`**
- Ajout de la fonction `updateTestVariablesSuggestions()`
- Redéfinition de `renderVariablesList()` pour mettre à jour les suggestions
- Redéfinition de `window.removeVariable()` pour mettre à jour les suggestions

**`templates/test_edit.html`**
- Ajout de la fonction `updateTestVariablesSuggestions()`
- Redéfinition de `renderVariablesList()` pour mettre à jour les suggestions
- Redéfinition de `window.removeVariable()` pour mettre à jour les suggestions
- Appel de `updateTestVariablesSuggestions()` après le chargement du test

### 📚 Documentation

**Nouveaux fichiers** :
- `docs/VARIABLE_AUTOCOMPLETE_MULTITYPE.md` : Documentation complète du système
- `static/test-multitype-autocomplete.html` : Page de test interactive

### 🔧 API Publique

#### Méthode `setVariables(type, variables)`

```javascript
/**
 * Définit les variables pour un type spécifique
 * @param {string} type - Type de variables ('testGyver' ou 'test')
 * @param {Array} variables - Tableau de variables (strings ou objets avec propriété 'key')
 */
window.variableAutocomplete.setVariables('test', ['token', 'user_id', 'response_code']);
```

### 🎨 Exemples d'Utilisation

#### Initialisation

```javascript
// Créer l'instance
const autocomplete = new VariableAutocomplete({
    apiEndpoint: '/api/variables?isRoot=true&page_size=100'
});

// Définir les variables du test
autocomplete.setVariables('test', ['token', 'user_id']);
```

#### Ajout de Variables

```javascript
// Ajouter une variable au test
testVariables.push('new_variable');

// Mettre à jour les suggestions
autocomplete.setVariables('test', testVariables);
```

### 🎯 Comportement

#### Navigation au Clavier

- **Flèche Bas** : Descendre dans les suggestions (traverse tous les types)
- **Flèche Haut** : Monter dans les suggestions (traverse tous les types)
- **Entrée** : Insérer la variable sélectionnée avec le bon format
- **Échap** : Fermer les suggestions
- **Clic** : Sélectionner et insérer la variable

#### Insertion de Variables

Selon le type de variable sélectionné, le format d'insertion est différent :

```javascript
// Variable TestGyver "url_api"
{{url_api}}

// Variable du Test "token"
{{app.token}}

// Variable de Collection "test_id"
{{test.test_id}}
```

### 🔄 Rétrocompatibilité

✅ **100% compatible** avec l'existant :
- Les pages utilisant l'ancien système continuent de fonctionner
- Les variables TestGyver sont toujours chargées automatiquement
- L'API et le comportement de base restent inchangés

### 🚀 Extensibilité

Le système est conçu pour être facilement extensible :

```javascript
// Ajouter un nouveau type de suggestions
this.suggestionTypes.custom = {
    color: '#ff6b6b',
    bgColor: '#ffe0e0',
    borderColor: '#ff6b6b',
    icon: 'fa-star',
    label: 'Variables personnalisées',
    insertFormat: (key) => `{{custom.${key}}}`,
    displayUppercase: false
};

// Utiliser le nouveau type
autocomplete.setVariables('custom', ['var1', 'var2']);
```

### 📊 Impact

- **Visibilité** : Les utilisateurs peuvent maintenant distinguer visuellement les variables globales des variables locales
- **Productivité** : L'autocomplétion propose maintenant toutes les variables pertinentes
- **Clarté** : Les formats d'insertion différents évitent les confusions
- **Maintenabilité** : Code mieux organisé et documenté

### 🐛 Corrections

- Amélioration de la gestion des événements de navigation au clavier
- Meilleure gestion du positionnement de la boîte de suggestions
- Optimisation du filtrage des suggestions

### 📝 Notes de Migration

Aucune migration nécessaire. Le système est rétrocompatible.

Pour bénéficier pleinement des nouvelles fonctionnalités :

1. Initialiser le plugin comme avant
2. Appeler `setVariables('test', variables)` pour définir les variables du test
3. Les suggestions s'afficheront automatiquement avec les deux types

### 🔮 Améliorations Futures Possibles

- Support de types supplémentaires (variables d'environnement, variables de campagne, etc.)
- Tri configurable des suggestions
- Groupes repliables
- Recherche fuzzy
- Favoris / historique

---

**Date** : 29 octobre 2025  
**Auteur** : GitHub Copilot  
**Ticket** : Évolution du plugin d'autocomplétion multi-types
