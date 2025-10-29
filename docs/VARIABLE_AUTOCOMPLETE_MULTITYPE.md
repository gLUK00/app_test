# Autocomplétion Multi-Types pour les Variables

## Vue d'ensemble

Le plugin d'autocomplétion `variable-autocomplete.js` a été amélioré pour supporter plusieurs types de suggestions de variables avec des couleurs et des formats d'insertion distincts.

## Types de Suggestions

### 1. Variables TestGyver (`testGyver`)

**Description** : Variables racines définies au niveau de l'application (variables globales multi-environnements).

**Caractéristiques** :
- **Couleur** : Bleu (`#0d6efd`)
- **Icône** : `fa-database`
- **Format d'insertion** : `{{variable_name}}`
- **Source** : API `/api/variables?isRoot=true`
- **Label** : "Variables TestGyver"

**Exemple** :
```
Saisie : url_api
Suggestion affichée : url_api (en bleu)
Insertion : {{url_api}}
```

### 2. Variables du Test (`test`)

**Description** : Variables définies spécifiquement pour le test en cours (variables locales au test).

**Caractéristiques** :
- **Couleur** : Vert (`#198754`)
- **Icône** : `fa-vial`
- **Format d'insertion** : `{{app.variable_name}}`
- **Source** : Tableau local `variables` du test en cours
- **Label** : "Variables du test"

**Exemple** :
```
Saisie : token
Suggestion affichée : token (en vert)
Insertion : {{app.token}}
```

### 3. Variables de Collection (`collection`)

**Description** : Variables de contexte disponibles automatiquement (ID du test, ID de la campagne).

**Caractéristiques** :
- **Couleur** : Rouge (`#dc3545`)
- **Icône** : `fa-layer-group`
- **Format d'insertion** : `{{test.variable_name}}`
- **Source** : Variables prédéfinies dans le plugin
- **Label** : "Variables de collection"
- **Variables disponibles** :
  - `test_id` : ID du test en cours
  - `campain_id` : ID de la campagne

**Exemple** :
```
Saisie : test_id
Suggestion affichée : test_id (en rouge)
Insertion : {{test.test_id}}
```

## Architecture

### Structure des Suggestions

Le plugin organise les suggestions en **groupes visuellement séparés** :

```
┌─────────────────────────────────────┐
│ Variables TestGyver (bleu)          │
├─────────────────────────────────────┤
│  url_api                            │
│  username                           │
│  password                           │
├─────────────────────────────────────┤
│ Variables du test (vert)            │
├─────────────────────────────────────┤
│  token                              │
│  response_id                        │
├─────────────────────────────────────┤
│ Variables de collection (rouge)     │
├─────────────────────────────────────┤
│  test_id                            │
│  campain_id                         │
└─────────────────────────────────────┘
```

### Configuration des Types

Chaque type de suggestion est défini dans `this.suggestionTypes` :

```javascript
this.suggestionTypes = {
    testGyver: {
        color: '#0d6efd',           // Couleur du texte/bordure
        bgColor: '#e7f1ff',         // Couleur de fond de l'en-tête
        borderColor: '#0d6efd',     // Couleur de la bordure gauche
        icon: 'fa-database',        // Icône FontAwesome
        label: 'Variables TestGyver', // Label affiché
        insertFormat: (key) => `{{${key}}}`,  // Format d'insertion
        displayUppercase: false     // Affichage en majuscules
    },
    test: {
        color: '#198754',
        bgColor: '#d1e7dd',
        borderColor: '#198754',
        icon: 'fa-vial',
        label: 'Variables du test',
        insertFormat: (key) => `{{app.${key}}}`,
        displayUppercase: false
    },
    collection: {
        color: '#dc3545',
        bgColor: '#f8d7da',
        borderColor: '#dc3545',
        icon: 'fa-layer-group',
        label: 'Variables de collection',
        insertFormat: (key) => `{{test.${key}}}`,
        displayUppercase: false
    }
};
```

## Utilisation

### Initialisation

```javascript
// Initialiser le plugin
window.variableAutocomplete = new VariableAutocomplete({
    apiEndpoint: '/api/variables?isRoot=true&page_size=100'
});

// Définir les variables du test en cours
window.variableAutocomplete.setVariables('test', ['token', 'user_id', 'response_data']);
```

### Méthode `setVariables(type, variables)`

Permet de définir dynamiquement les variables pour un type spécifique.

**Paramètres** :
- `type` (string) : Type de variables (`'testGyver'` ou `'test'`)
- `variables` (Array) : Tableau de variables (strings ou objets avec propriété `key`)

**Exemples** :

```javascript
// Avec des strings simples
variableAutocomplete.setVariables('test', ['var1', 'var2', 'var3']);

// Avec des objets complets
variableAutocomplete.setVariables('test', [
    { key: 'var1', description: 'Ma variable 1' },
    { key: 'var2', description: 'Ma variable 2' }
]);
```

### Mise à Jour Automatique

Dans les pages `test_add.html` et `test_edit.html`, les suggestions sont automatiquement mises à jour lorsque :

1. Une variable est ajoutée au test
2. Une variable est supprimée du test
3. Le test est chargé (pour test_edit.html)

```javascript
function updateTestVariablesSuggestions() {
    if (window.variableAutocomplete) {
        window.variableAutocomplete.setVariables('test', variables);
    }
}
```

## Fonctionnement

### Filtrage et Affichage

1. L'utilisateur tape dans un champ texte ou textarea
2. Le plugin détecte le mot en cours de saisie
3. Les variables des **deux types** sont filtrées selon le mot saisi
4. Les suggestions sont regroupées par type et affichées dans des listes séparées
5. Chaque groupe a sa propre couleur et son propre en-tête

### Navigation

- **Flèches haut/bas** : Naviguer entre toutes les suggestions (tous types confondus)
- **Entrée** : Insérer la variable sélectionnée avec le bon format
- **Échap** : Fermer les suggestions
- **Clic** : Sélectionner et insérer la variable

### Insertion

Lors de la sélection d'une variable :

1. Le plugin récupère le type de la variable sélectionnée
2. Il applique le format d'insertion correspondant au type
3. La variable est insérée dans le champ avec le format approprié

```javascript
insertVariable(variableKey, variableType = 'testGyver') {
    const typeConfig = this.suggestionTypes[variableType];
    const variableText = typeConfig.insertFormat(variableKey);
    // ... insertion dans le champ
}
```

## Styles CSS

Les styles sont définis dans `static/css/custom.css` :

### Structure

```css
.variable-autocomplete-suggestions       /* Container principal */
  .variable-suggestions-container       /* Container des groupes */
    .variable-suggestions-group         /* Un groupe de suggestions */
      .variable-suggestions-header      /* En-tête du groupe (coloré) */
      .variable-suggestions-list        /* Liste des suggestions */
        .variable-suggestion-tag        /* Une suggestion (colorée) */
```

### Personnalisation

Les couleurs des groupes sont appliquées dynamiquement via les attributs `style` :

```html
<div class="variable-suggestions-header" 
     style="border-left: 3px solid #0d6efd; background-color: #e7f1ff;">
    <!-- Contenu -->
</div>
```

## Extensibilité

### Ajouter un Nouveau Type

Pour ajouter un nouveau type de suggestions :

1. **Définir le type dans le constructeur** :

```javascript
this.variablesByType = {
    testGyver: [],
    test: [],
    custom: []  // Nouveau type
};

this.suggestionTypes = {
    // ... types existants
    custom: {
        color: '#ff6b6b',
        bgColor: '#ffe0e0',
        borderColor: '#ff6b6b',
        icon: 'fa-star',
        label: 'Variables personnalisées',
        insertFormat: (key) => `{{custom.${key}}}`,
        displayUppercase: true  // Afficher en majuscules
    }
};
```

2. **Alimenter les variables** :

```javascript
variableAutocomplete.setVariables('custom', ['custom_var1', 'custom_var2']);
```

3. **Le plugin gérera automatiquement** :
   - L'affichage du nouveau groupe
   - Le filtrage des suggestions
   - L'insertion avec le format spécifique

## Avantages

✅ **Clarté visuelle** : Les différents types de variables sont facilement identifiables par leur couleur

✅ **Formats distincts** : Chaque type utilise son propre format d'insertion ({{var}} vs {{app.var}})

✅ **Extensible** : Facile d'ajouter de nouveaux types de suggestions

✅ **Performant** : Les suggestions sont filtrées et affichées en temps réel

✅ **Accessible** : Navigation au clavier complète

✅ **Responsive** : S'adapte aux différentes tailles d'écran

## Exemples d'Utilisation

### Exemple 1 : Page d'ajout de test

```javascript
// Initialisation
const autocomplete = new VariableAutocomplete();

// Variables du test ajoutées par l'utilisateur
let testVariables = ['token', 'user_id'];

// Mettre à jour les suggestions
autocomplete.setVariables('test', testVariables);

// Ajouter une nouvelle variable
testVariables.push('response_code');
autocomplete.setVariables('test', testVariables);
```

### Exemple 2 : Page d'édition de test

```javascript
// Charger le test depuis l'API
const testData = await API.get(`/api/tests/${testId}`);

// Initialiser avec les variables du test existant
autocomplete.setVariables('test', testData.variables || []);
```

## Notes Techniques

- Les variables TestGyver sont chargées **une seule fois** au démarrage via l'API
- Les variables du test sont **mises à jour dynamiquement** lors des ajouts/suppressions
- Le plugin utilise un **debounce** de 200ms pour optimiser les performances
- Les suggestions sont limitées à **10 par type** par défaut (configurable)
- La navigation au clavier **traverse tous les types** de manière fluide

## Compatibilité

- ✅ Navigateurs modernes (Chrome, Firefox, Safari, Edge)
- ✅ Responsive (mobile, tablette, desktop)
- ✅ Compatible avec l'existant (les anciennes fonctionnalités restent disponibles)
