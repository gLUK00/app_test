# Affichage/Masquage Dynamique des Champs d'Actions

## Vue d'ensemble

Cette fonctionnalité permet aux plugins d'actions de masquer ou afficher dynamiquement certains champs du formulaire en fonction du contexte via `hideFields()` et `showFields()`.

## Méthodes ajoutées à TestActionsManager

### `hideFields(fieldNames)`

Cache des champs du formulaire.

**Paramètres :**
- `fieldNames` (Array<string>) : Tableau des noms de champs à masquer

**Exemple :**
```javascript
manager.hideFields(['content', 'file_content']);
```

### `showFields(fieldNames)`

Affiche des champs du formulaire.

**Paramètres :**
- `fieldNames` (Array<string>) : Tableau des noms de champs à afficher

**Exemple :**
```javascript
manager.showFields(['remote_path', 'content']);
```

## Utilisation dans les plugins

### Accès au manager

```javascript
const manager = window.testActionsManager;
```

### Exemple complet : FTPAction

```python
def get_js_show_form(self):
    return """
const manager = window.testActionsManager;
const methodSelect = document.getElementById('method');

if (methodSelect && manager) {
    const updateFieldsVisibility = () => {
        const method = methodSelect.value;
        
        if (method === 'GET') {
            manager.showFields(['remote_path', 'file_content']);
            manager.hideFields(['content']);
        } else if (method === 'PUT') {
            manager.showFields(['remote_path', 'content', 'file_content']);
        } else if (method === 'DELETE') {
            manager.showFields(['remote_path']);
            manager.hideFields(['content', 'file_content']);
        }
    };
    
    methodSelect.addEventListener('change', updateFieldsVisibility);
    
    // Appliquer immédiatement si édition
    if (actionConfig?.method) {
        updateFieldsVisibility();
    }
}
"""
```

## Fonctionnement technique

1. Chaque champ possède un attribut `data-field-name` :
```html
<div class="mb-3" data-field-name="remote_path">
```

2. Les méthodes utilisent `querySelector` pour cibler les champs :
```javascript
const fieldGroup = document.querySelector(`[data-field-name="${fieldName}"]`);
fieldGroup.style.display = 'none'; // ou 'block'
```

## Cas d'usage

### GET : Télécharger un fichier
- ✅ `remote_path` : visible
- ✅ `file_content` : visible
- ❌ `content` : masqué

### PUT : Uploader un fichier
- ✅ `remote_path` : visible
- ✅ `content` : visible
- ✅ `file_content` : visible

### DELETE : Supprimer un fichier
- ✅ `remote_path` : visible
- ❌ `content` : masqué
- ❌ `file_content` : masqué

## Bonnes pratiques

1. **Vérifier l'existence du manager**
```javascript
if (manager) {
    manager.hideFields(['field1']);
}
```

2. **Gérer l'état initial (édition)**
```javascript
if (actionConfig?.method) {
    updateFieldsVisibility();
}
```

3. **Noms de champs exacts**
Les noms doivent correspondre à ceux de `get_input_mask()`.

## Fichiers modifiés

- `static/test_actions.js` : Ajout de `hideFields()` et `showFields()`, ajout de l'attribut `data-field-name`
- `plugins/actions/ftp_action.py` : Exemple d'utilisation dans `get_js_show_form()`
