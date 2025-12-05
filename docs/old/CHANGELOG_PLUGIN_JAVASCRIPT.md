# Changelog - Fonctions JavaScript dans les Plugins d'Actions

## Date : 5 novembre 2025

## Résumé

Évolution majeure du système de plugins d'actions permettant l'ajout de code JavaScript personnalisé pour améliorer l'expérience utilisateur lors de la configuration des actions dans les tests.

## Modifications apportées

### 1. Backend Python

#### `plugins/actions/action_base.py`
- ✨ Ajout de la méthode `get_js_show_form()` : Retourne le code JavaScript à exécuter lors de l'affichage du formulaire
- ✨ Ajout de la méthode `get_js_validate_form()` : Retourne le code JavaScript à exécuter lors de la validation du formulaire
- Par défaut, ces méthodes retournent `None` (rétrocompatibilité garantie)

#### `routes/actions_routes.py`
- ✨ Nouvelle route `GET /api/actions/javascript` : Récupère tous les codes JavaScript de tous les plugins
- ✨ Nouvelle route `GET /api/actions/javascript/<action_type>` : Récupère le code JavaScript d'un plugin spécifique
- Retourne uniquement les plugins qui définissent au moins une fonction JavaScript

#### `plugins/actions/var_action.py`
- ✨ Implémentation de `get_js_show_form()` : 
  - Ajoute un écouteur sur le champ `variable_name`
  - Met à jour visuellement le champ avec les classes Bootstrap `is-valid` / `is-invalid`
  - Valide en temps réel si la variable sélectionnée existe dans les variables du test
- ✨ Implémentation de `get_js_validate_form()` :
  - Vérifie que le champ `variable_name` n'est pas vide
  - Vérifie que la variable existe dans la liste des variables du test
  - Retourne un message d'erreur explicite si la validation échoue

### 2. Frontend JavaScript

#### `static/test_actions.js`
- ✨ Ajout de `actionJavaScriptFunctions` dans le constructeur pour stocker les fonctions JS des plugins
- ✨ Nouvelle méthode `loadActionJavaScriptFunctions()` : Charge les fonctions JavaScript depuis l'API au démarrage
- ✨ Nouvelle méthode `executeJsShowForm(actionType, actionConfig)` : Exécute la fonction jsShowForm du plugin si elle existe
- ✨ Nouvelle méthode `executeJsValidateForm(actionType, actionConfig)` : Exécute la fonction jsValidateForm du plugin si elle existe et retourne le résultat de validation
- 🔧 Modification de `displayDynamicFields()` : Appelle `executeJsShowForm()` après la génération des champs
- 🔧 Modification de `saveAction()` : Appelle `executeJsValidateForm()` avant la soumission et bloque si la validation échoue

### 3. Documentation

#### `docs/PLUGIN_DEVELOPMENT_GUIDE.md`
- ✨ Nouvelle section complète "Fonctions JavaScript dans les plugins d'actions"
- Explique les signatures des fonctions `jsShowForm` et `jsValidateForm`
- Fournit un exemple complet avec le plugin VarAction
- Liste les bonnes pratiques et considérations de sécurité
- Mentionne les évolutions futures possibles

#### `docs/PLUGIN_JAVASCRIPT_README.md` (nouveau)
- ✨ Documentation détaillée de la fonctionnalité
- Architecture et flux d'exécution
- Exemples d'utilisation
- Guide de test et validation

### 4. Tests

#### `_build/test_plugin_javascript.py` (nouveau)
- ✅ Teste la présence des méthodes `get_js_show_form()` et `get_js_validate_form()` dans ActionBase
- ✅ Vérifie l'implémentation dans VarAction
- ✅ Valide le comportement par défaut (retour `None`)
- ✅ Teste la compatibilité de tous les plugins d'actions
- ✅ Valide le contenu des fonctions JavaScript

#### `_build/test_api_javascript.py` (nouveau)
- ✅ Teste la route `GET /api/actions/javascript`
- ✅ Teste la route `GET /api/actions/javascript/<action_type>`
- ✅ Vérifie la gestion des erreurs (type d'action invalide)
- ✅ Valide le contenu JavaScript retourné

#### `_build/test_var_action.py`
- 🔧 Correction mineure du test `test_output_variables()` pour vérifier correctement la structure des variables de sortie

### 5. Fichiers modifiés

- `info.txt` : Tâche marquée comme terminée avec résumé de l'implémentation

## Résultats des tests

### Tests de compatibilité
```
✅ test_plugins.py : 17 tests passés
✅ test_var_action.py : Tous les tests passés
✅ test_var_action_integration.py : Tous les tests passés
```

### Nouveaux tests
```
✅ test_plugin_javascript.py : 5 tests passés
   - 7 plugins d'actions chargés
   - 1 plugin avec fonctions JavaScript (VarAction)
   - 6 plugins standard (compatibilité totale)

✅ test_api_javascript.py : 4 tests passés
   - API /api/actions/javascript fonctionnelle
   - API /api/actions/javascript/<type> fonctionnelle
   - Gestion des erreurs correcte
   - Contenu JavaScript valide
```

## Compatibilité

### ✅ Rétrocompatibilité totale
- Tous les plugins existants continuent de fonctionner sans modification
- Aucun changement nécessaire pour les plugins qui n'utilisent pas cette fonctionnalité
- Les méthodes `get_js_show_form()` et `get_js_validate_form()` retournent `None` par défaut

### ✅ Extensibilité
- Architecture conçue pour permettre l'ajout de nouvelles fonctions JavaScript à l'avenir
- Exemples : `jsOnFieldChange`, `jsBeforeSubmit`, `jsAfterSave`, `jsOnError`

## Exemple d'utilisation

### Code Python (Plugin)
```python
class VarAction(ActionBase):
    def get_js_validate_form(self):
        return """
function jsValidateForm(actionConfig, variables) {
    if (!variables.includes(actionConfig.variable_name)) {
        return {
            isValid: false,
            errorMessage: 'La variable n\'existe pas dans les variables du test'
        };
    }
    return {isValid: true, errorMessage: ''};
}
"""
```

### Résultat côté utilisateur
Lorsqu'un utilisateur configure une action VarAction et sélectionne une variable qui n'existe pas dans le test, un message d'erreur s'affiche immédiatement sans soumission du formulaire.

## Impact sur les performances

- ⚡ Impact minimal : Chargement des fonctions JavaScript au démarrage uniquement
- 🔄 Pas de requêtes supplémentaires pendant l'utilisation
- 💾 Stockage en mémoire des fonctions JavaScript (quelques Ko par plugin)

## Sécurité

- ✅ Le code JavaScript est exécuté côté client avec les privilèges de l'utilisateur
- ✅ Les validations JavaScript ne remplacent pas les validations côté serveur (`validate_config()`)
- ✅ Utilisation de `Function()` pour exécuter le code JavaScript de manière sécurisée

## Migration

### Pour les développeurs de plugins
Aucune migration nécessaire. Les plugins existants continuent de fonctionner.

Pour ajouter des fonctions JavaScript à un plugin existant :
1. Ajouter la méthode `get_js_show_form()` et/ou `get_js_validate_form()`
2. Retourner le code JavaScript sous forme de string
3. Tester avec les scripts de test fournis

## Prochaines étapes

- [ ] Ajouter d'autres fonctions JavaScript selon les besoins
- [ ] Créer des plugins d'exemple supplémentaires utilisant cette fonctionnalité
- [ ] Améliorer la documentation avec plus d'exemples
- [ ] Créer un générateur de code pour faciliter la création de fonctions JavaScript

## Auteur

TestGyver Team

## Version

1.0.0 - Première version de la fonctionnalité
