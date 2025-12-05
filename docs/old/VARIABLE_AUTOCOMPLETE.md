# Plugin d'Autocomplétion des Variables

## Vue d'ensemble

Le plugin `VariableAutocomplete` permet d'ajouter l'autocomplétion des variables racines dans tous les champs de saisie `input[type="text"]` et `textarea` de l'application.

## Fonctionnalités

### 1. Détection Automatique
- Surveille en permanence la saisie dans les champs text et textarea
- Détecte automatiquement les mots en cours de frappe (caractères alphanumériques)
- S'active dès qu'un mot de plus d'un caractère est saisi

### 2. Suggestions Intelligentes
- Affiche une liste de variables racines filtrées selon le texte saisi
- Mise en évidence des correspondances dans les noms de variables
- Affichage des descriptions des variables (si disponibles)
- Navigation au clavier (flèches haut/bas, Entrée, Échap)
- Sélection à la souris avec survol

### 3. Insertion Automatique
- Remplace le mot en cours par `{{nom_variable}}` lors de la sélection
- Positionne automatiquement le curseur après l'insertion
- Permet de continuer la saisie immédiatement

## Utilisation

### Activation Automatique
Le plugin s'active automatiquement sur toutes les pages qui l'incluent :
- Page d'ajout de test (`test_add.html`)
- Page d'édition de test (`test_edit.html`)

### Utilisation dans les Formulaires

1. **Commencer à taper** dans un champ text ou textarea
2. **Une liste de suggestions** apparaît sous le champ dès que vous tapez un caractère
3. **Naviguer** dans les suggestions :
   - Utilisez les flèches ↑ ↓ du clavier
   - Ou survolez les suggestions avec la souris
4. **Sélectionner** une variable :
   - Appuyez sur `Entrée` pour la suggestion sélectionnée
   - Ou cliquez sur la suggestion souhaitée
5. La variable est insérée au format `{{nom_variable}}`
6. Le curseur est positionné après pour continuer la saisie

### Raccourcis Clavier
- `↑` / `↓` : Naviguer dans les suggestions
- `Entrée` : Insérer la variable sélectionnée
- `Échap` : Fermer les suggestions

## Architecture Technique

### Fichiers Créés/Modifiés

#### 1. Plugin JavaScript
**Fichier** : `/static/js/variable-autocomplete.js`
- Classe `VariableAutocomplete`
- Gestion complète de l'autocomplétion
- Observer DOM pour les champs dynamiques
- Gestion des événements clavier et souris

#### 2. Styles CSS
**Fichier** : `/static/css/custom.css`
- Styles `.variable-autocomplete-suggestions`
- Design moderne avec dégradé violet
- Animations et transitions
- Responsive design

#### 3. Route API
**Fichier** : `/routes/variables_routes.py`
- Support du paramètre `isRoot=true`
- Filtrage des variables racines
- Endpoint : `GET /api/variables?isRoot=true`

#### 4. Templates
**Fichiers modifiés** :
- `/templates/base.html` : Inclusion du script
- `/templates/test_add.html` : Initialisation du plugin
- `/templates/test_edit.html` : Initialisation du plugin

## API du Plugin

### Constructeur

```javascript
const autocomplete = new VariableAutocomplete({
    apiEndpoint: '/api/variables?isRoot=true&page_size=100',
    debounceDelay: 200,
    minChars: 1,
    maxSuggestions: 10
});
```

#### Options

| Option | Type | Défaut | Description |
|--------|------|--------|-------------|
| `apiEndpoint` | string | `/api/variables?isRoot=true` | Endpoint API pour récupérer les variables |
| `debounceDelay` | number | 200 | Délai en ms avant de filtrer les suggestions |
| `minChars` | number | 1 | Nombre minimum de caractères pour activer l'autocomplétion |
| `maxSuggestions` | number | 10 | Nombre maximum de suggestions affichées |

### Méthodes Publiques

#### `refresh()`
Recharge les variables depuis l'API.
```javascript
await variableAutocomplete.refresh();
```

#### `destroy()`
Détruit le plugin et nettoie les événements.
```javascript
variableAutocomplete.destroy();
```

## Personnalisation

### Modifier les Styles
Les styles se trouvent dans `/static/css/custom.css` sous la section "Autocomplétion des variables".

#### Couleurs principales
```css
/* Gradient des suggestions */
background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);

/* Couleur de surbrillance */
color: #ffd700;
```

### Changer l'Endpoint API
Lors de l'initialisation, vous pouvez spécifier un endpoint différent :
```javascript
new VariableAutocomplete({
    apiEndpoint: '/api/custom-endpoint'
});
```

### Ajuster le Comportement
Modifiez les options lors de l'initialisation :
```javascript
new VariableAutocomplete({
    debounceDelay: 300,  // Attendre plus longtemps
    minChars: 2,         // Minimum 2 caractères
    maxSuggestions: 20   // Afficher plus de suggestions
});
```

## Fonctionnement Interne

### 1. Chargement des Variables
Au démarrage, le plugin charge toutes les variables racines via l'API.

### 2. Observation du DOM
Un `MutationObserver` surveille l'ajout de nouveaux champs dans la page pour les traiter automatiquement.

### 3. Analyse de la Saisie
- Capture l'événement `input` sur chaque champ
- Extrait le mot en cours de saisie à la position du curseur
- Filtre les variables correspondantes

### 4. Affichage des Suggestions
- Crée dynamiquement une div de suggestions
- Positionne la div sous le champ actif
- Met en évidence les correspondances

### 5. Insertion
- Remplace le mot par la variable au format `{{variable}}`
- Préserve le reste du texte
- Positionne le curseur pour continuer

## Compatibilité

- ✅ Chrome/Edge (dernières versions)
- ✅ Firefox (dernières versions)
- ✅ Safari (dernières versions)
- ✅ Responsive (mobile et tablette)

## Dépendances

- Bootstrap 5.3+ (pour le style général)
- FontAwesome 6.4+ (pour les icônes)
- API Auth (pour les requêtes authentifiées)

## Exemples d'Utilisation

### Exemple 1 : Champ URL HTTP
```
Tapez : "https://api.example.com/users/use"
→ Suggestions : username, user_id, user_token
→ Sélectionnez "username"
→ Résultat : "https://api.example.com/users/{{username}}"
```

### Exemple 2 : Commande SSH
```
Tapez : "ssh ho"
→ Suggestions : hostname, host_ip
→ Sélectionnez "hostname"
→ Résultat : "ssh {{hostname}}"
```

### Exemple 3 : Chemin de fichier
```
Tapez : "/data/ba"
→ Suggestions : backup_path, base_dir
→ Sélectionnez "backup_path"
→ Résultat : "/data/{{backup_path}}"
```

## Débogage

### Activer les Logs
Les logs sont automatiquement affichés dans la console :
```javascript
console.log('[VariableAutocomplete] X variables racines chargées');
```

### Vérifier le Chargement
```javascript
console.log(window.variableAutocomplete.variables);
```

### Tester le Refresh
```javascript
await window.variableAutocomplete.refresh();
```

## Améliorations Futures

- [ ] Cache des variables avec expiration
- [ ] Support des variables imbriquées (non-racines)
- [ ] Prévisualisation de la valeur de la variable
- [ ] Historique des variables récemment utilisées
- [ ] Suggestions contextuelles selon le type de champ
- [ ] Support du glisser-déposer de variables

## Support

Pour tout problème ou question, vérifiez :
1. Que les variables racines existent dans la base de données
2. Que l'endpoint `/api/variables?isRoot=true` est accessible
3. Que le token d'authentification est valide
4. Les logs de la console navigateur

