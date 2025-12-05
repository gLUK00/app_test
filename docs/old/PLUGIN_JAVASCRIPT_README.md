# Fonctions JavaScript dans les Plugins d'Actions

## Vue d'ensemble

Cette fonctionnalité permet aux plugins d'actions de définir du code JavaScript personnalisé qui s'exécute côté client lors de la configuration des actions dans les tests. Cela améliore l'expérience utilisateur en permettant une validation en temps réel et des interactions dynamiques.

## Fonctionnalités implémentées

### 1. Extension de la classe `ActionBase`

Deux nouvelles méthodes ont été ajoutées à la classe de base `ActionBase` :

```python
def get_js_show_form(self):
    """
    Retourne le code JavaScript à exécuter lors de l'affichage du formulaire.
    Cette fonction est appelée après la génération des champs dynamiques.
    
    Returns:
        str: Code JavaScript de la fonction jsShowForm ou None
    """
    return None

def get_js_validate_form(self):
    """
    Retourne le code JavaScript à exécuter lors de la validation du formulaire.
    Cette fonction est appelée avant la soumission du formulaire.
    
    Returns:
        str: Code JavaScript de la fonction jsValidateForm ou None
    """
    return None
```

Par défaut, ces méthodes retournent `None`, ce qui signifie qu'aucun code JavaScript personnalisé ne sera exécuté. Les plugins existants continuent de fonctionner sans modification.

### 2. Nouvelles routes API

Deux nouvelles routes ont été ajoutées dans `routes/actions_routes.py` :

- **GET `/api/actions/javascript`** : Récupère tous les codes JavaScript pour tous les types d'actions
- **GET `/api/actions/javascript/<action_type>`** : Récupère le code JavaScript pour un type d'action spécifique

Exemple de réponse :
```json
{
  "var": {
    "jsShowForm": "function jsShowForm(actionConfig) { ... }",
    "jsValidateForm": "function jsValidateForm(actionConfig, variables) { ... }"
  }
}
```

### 3. Mise à jour de l'interface utilisateur

Le fichier `static/test_actions.js` a été mis à jour pour :

- Charger les fonctions JavaScript des plugins au démarrage
- Exécuter `jsShowForm` lors de l'affichage des champs dynamiques d'une action
- Exécuter `jsValidateForm` lors de la validation du formulaire avant soumission

**Nouvelles méthodes dans `TestActionsManager` :**

```javascript
async loadActionJavaScriptFunctions() {
    // Charge les fonctions JavaScript depuis l'API
}

executeJsShowForm(actionType, actionConfig) {
    // Exécute la fonction jsShowForm du plugin si elle existe
}

executeJsValidateForm(actionType, actionConfig) {
    // Exécute la fonction jsValidateForm du plugin si elle existe
    // Retourne {isValid: boolean, errorMessage: string}
}
```

### 4. Implémentation dans VarAction

Le plugin `VarAction` a été mis à jour pour utiliser les fonctions JavaScript :

**jsShowForm** : Met en évidence visuellement si la variable sélectionnée existe ou non
- Ajoute des classes Bootstrap `is-valid` / `is-invalid` au champ de sélection
- Met à jour le style en temps réel lors du changement de sélection

**jsValidateForm** : Valide que la variable sélectionnée existe dans les variables du test
- Vérifie que le champ `variable_name` n'est pas vide
- Vérifie que la variable existe dans la liste des variables du test
- Retourne un message d'erreur explicite si la validation échoue

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      Plugin Python                          │
│  ┌───────────────────────────────────────────────────────┐  │
│  │  ActionBase                                           │  │
│  │  - get_js_show_form() → str | None                    │  │
│  │  - get_js_validate_form() → str | None                │  │
│  └───────────────────────────────────────────────────────┘  │
│                           ↓                                  │
│  ┌───────────────────────────────────────────────────────┐  │
│  │  VarAction (exemple)                                  │  │
│  │  - Définit jsShowForm                                 │  │
│  │  - Définit jsValidateForm                             │  │
│  └───────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│                      API REST                               │
│  GET /api/actions/javascript                                │
│  → Retourne tous les codes JavaScript                       │
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│                   Interface Utilisateur                     │
│  test_actions.js                                            │
│  1. Charge les fonctions JS au démarrage                    │
│  2. Exécute jsShowForm lors de l'affichage                  │
│  3. Exécute jsValidateForm lors de la validation            │
└─────────────────────────────────────────────────────────────┘
```

## Flux d'exécution

### Affichage du formulaire

1. L'utilisateur sélectionne un type d'action
2. `TestActionsManager.displayDynamicFields()` est appelée
3. Les champs dynamiques sont générés à partir du masque de saisie
4. Si le plugin définit `jsShowForm`, la fonction est exécutée avec `actionConfig` en paramètre
5. Le code JavaScript personnalisé peut modifier l'interface (ajout d'écouteurs, validation en temps réel, etc.)

### Validation du formulaire

1. L'utilisateur clique sur "Sauvegarder"
2. `TestActionsManager.saveAction()` est appelée
3. La validation standard des champs requis est effectuée
4. Si le plugin définit `jsValidateForm`, la fonction est exécutée avec `actionConfig` et `variables` en paramètres
5. Si la validation échoue (`isValid: false`), un message d'erreur est affiché et la soumission est annulée
6. Si la validation réussit, l'action est sauvegardée

## Exemple d'utilisation

```python
class CustomAction(ActionBase):
    plugin_name = "custom"
    
    def get_js_show_form(self):
        """
        IMPORTANT: Retourner uniquement le CORPS de la fonction, 
        pas la déclaration 'function jsShowForm(...)'.
        Le framework ajoute automatiquement new Function('actionConfig', code).
        """
        return """
// Ajouter un écouteur sur un champ
const urlField = document.getElementById('url');
if (urlField) {
    urlField.addEventListener('input', function() {
        // Valider l'URL en temps réel
        if (!this.value.startsWith('http')) {
            this.classList.add('is-invalid');
        } else {
            this.classList.remove('is-invalid');
            this.classList.add('is-valid');
        }
    });
}
"""
    
    def get_js_validate_form(self):
        """
        IMPORTANT: Retourner uniquement le CORPS de la fonction,
        pas la déclaration 'function jsValidateForm(...)'.
        Le framework ajoute automatiquement new Function('actionConfig', 'variables', code).
        """
        return """
// Vérifier que l'URL commence par http
if (!actionConfig.url || !actionConfig.url.startsWith('http')) {
    return {
        isValid: false,
        errorMessage: "L'URL doit commencer par http:// ou https://"
    };
}

return {isValid: true, errorMessage: ''};
"""
```

## Avantages

1. **Validation en temps réel** : Les utilisateurs reçoivent un retour immédiat sur leurs saisies
2. **Expérience utilisateur améliorée** : Interactions dynamiques et feedback visuel
3. **Validation métier** : Vérification de règles complexes côté client avant soumission
4. **Extensibilité** : Possibilité d'ajouter facilement de nouvelles fonctions JavaScript à l'avenir
5. **Rétrocompatibilité** : Les plugins existants continuent de fonctionner sans modification

## Compatibilité

- ✅ Tous les plugins existants sont compatibles (retournent `None` par défaut)
- ✅ Les tests existants continuent de fonctionner
- ✅ Aucun changement nécessaire pour les plugins qui n'utilisent pas cette fonctionnalité
- ✅ Le plugin VarAction a été mis à jour pour démontrer l'utilisation

## Tests

### Script de test : `_build/test_plugin_javascript.py`

Ce script valide :
- La présence des méthodes `get_js_show_form()` et `get_js_validate_form()` dans `ActionBase`
- L'implémentation correcte dans `VarAction`
- Le comportement par défaut (retour `None`) pour les plugins sans fonctions JavaScript
- La compatibilité de tous les plugins d'actions
- Le contenu des fonctions JavaScript de `VarAction`

Résultats :
```
✅ TOUS LES TESTS SONT PASSÉS AVEC SUCCÈS
   - 7 plugins d'actions chargés
   - 1 plugin avec fonctions JavaScript (VarAction)
   - 6 plugins standard (compatibilité totale)
```

### Tests existants

Tous les tests existants continuent de fonctionner :
- `_build/test_plugins.py` : 17 tests passés ✅
- `_build/test_var_action.py` : Tous les tests passés ✅
- `_build/test_var_action_integration.py` : Tous les tests passés ✅

## Évolutions futures

Le mécanisme est conçu pour être extensible. D'autres fonctions JavaScript pourront être ajoutées :

- `jsOnFieldChange(fieldName, value)` : Appelée lors du changement d'un champ spécifique
- `jsBeforeSubmit(actionConfig)` : Appelée juste avant la soumission du formulaire
- `jsAfterSave(actionConfig)` : Appelée après la sauvegarde réussie de l'action
- `jsOnError(error)` : Appelée en cas d'erreur lors de la sauvegarde

## Documentation

La documentation complète est disponible dans :
- `docs/PLUGIN_DEVELOPMENT_GUIDE.md` : Guide de développement de plugins (section "Fonctions JavaScript dans les plugins d'actions")
- `docs/VAR_ACTION_README.md` : Documentation du plugin VarAction (exemple d'utilisation)

## Résumé

Cette fonctionnalité enrichit considérablement le système de plugins en permettant aux développeurs de plugins d'ajouter du code JavaScript personnalisé pour améliorer l'expérience utilisateur. L'implémentation est rétrocompatible et extensible, avec un exemple concret dans le plugin VarAction qui valide l'existence des variables du test.
