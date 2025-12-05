# Amélioration : Création Récursive de Répertoires WebDAV

## Problème résolu

Avant cette amélioration, l'action WebDAV `MKDIR` ne pouvait créer qu'un seul niveau de répertoire à la fois. Si un utilisateur tentait de créer un chemin à plusieurs niveaux comme `path1/path2/path3` alors qu'aucun des répertoires n'existait, l'opération échouait avec une erreur de conflit.

## Solution implémentée

Une nouvelle méthode `_mkdir_recursive()` a été ajoutée au plugin WebDAV pour gérer automatiquement la création récursive de répertoires.

### Fonctionnement

La méthode `_mkdir_recursive()` :

1. **Normalise le chemin** en supprimant les slashes multiples et trailing
2. **Vérifie l'existence** du répertoire final
3. **Divise le chemin** en composants individuels
4. **Crée chaque niveau** un par un, de la racine vers la feuille
5. **Vérifie l'existence** avant chaque création pour éviter les erreurs

### Exemples d'utilisation

#### Création d'un chemin à plusieurs niveaux
```python
# Action WebDAV
{
    "type": "webdav",
    "value": {
        "action": "MKDIR",
        "url": "https://webdav.example.com",
        "src_file": "uploads/2025/10/31/reports",
        "username": "user",
        "password": "pass"
    }
}
```

**Résultat** : Crée successivement :
- `uploads/`
- `uploads/2025/`
- `uploads/2025/10/`
- `uploads/2025/10/31/`
- `uploads/2025/10/31/reports/`

#### Avec des répertoires parents existants

Si `uploads/` et `uploads/2025/` existent déjà :

```python
{
    "action": "MKDIR",
    "src_file": "uploads/2025/10/31"
}
```

**Résultat** : Crée uniquement :
- `uploads/2025/10/`
- `uploads/2025/10/31/`

#### Utilisation avec variables

```python
{
    "action": "MKDIR",
    "src_file": "{{test.campain_id}}/{{test.test_id}}/screenshots"
}
```

Avec `campain_id = "camp_123"` et `test_id = "test_456"` :

**Résultat** : Crée :
- `camp_123/`
- `camp_123/test_456/`
- `camp_123/test_456/screenshots/`

### Cas gérés

✅ **Chemin simple** : `folder1` → crée `folder1/`

✅ **Chemin à plusieurs niveaux** : `a/b/c` → crée `a/`, `a/b/`, `a/b/c/`

✅ **Trailing slash** : `folder1/folder2/` → normalisé en `folder1/folder2`

✅ **Parents existants** : Ne recrée pas les répertoires déjà existants

✅ **Chemin complet existant** : Ne fait rien si le répertoire final existe déjà

✅ **Chemins profonds** : Gère n'importe quel nombre de niveaux

### Traces d'exécution

L'action génère des traces détaillées pour chaque niveau créé :

```
Sous-répertoire créé: path1
Sous-répertoire créé: path1/path2
Sous-répertoire créé: path1/path2/path3
Répertoire créé: path1/path2/path3
```

Si le répertoire existe déjà :
```
Le répertoire path1/path2/path3 existe déjà
```

### Gestion des erreurs

Si une erreur survient lors de la création d'un niveau :
```
Erreur lors de la création de path1/path2: Insufficient Storage
```

L'exception est propagée et l'exécution s'arrête.

## Tests

Un script de test complet valide tous les scénarios :

```bash
python3 _build/test_webdav_mkdir_recursive.py
```

**Tests couverts** :
- Chemin simple (1 niveau)
- Chemins multiples (2, 3, 5 niveaux)
- Parents déjà existants
- Répertoire complet existant
- Trailing slash
- Niveaux partiellement existants

## Impact

### Avant
```python
# Échouait si path1/ ou path1/path2/ n'existaient pas
action = {
    "action": "MKDIR",
    "src_file": "path1/path2/path3"
}
# ❌ Erreur : ResourceConflict
```

### Après
```python
# Fonctionne automatiquement
action = {
    "action": "MKDIR",
    "src_file": "path1/path2/path3"
}
# ✅ Crée tous les niveaux nécessaires
```

## Compatibilité

✅ **Rétrocompatible** : Les scripts existants continuent de fonctionner

✅ **Transparent** : Aucun changement dans l'API de l'action

✅ **Optimal** : Ne crée que les répertoires manquants

## Code source

La méthode `_mkdir_recursive()` se trouve dans :
- **Fichier** : `plugins/actions/webdav_action.py`
- **Lignes** : ~153-191

## Performance

La méthode effectue un appel `exists()` pour chaque niveau du chemin, puis un `mkdir()` pour chaque niveau manquant.

**Exemple** pour `a/b/c/d/e` avec rien d'existant :
- 5 appels `exists()` (tous retournent False)
- 5 appels `mkdir()` (création de chaque niveau)
- **Total** : 10 requêtes WebDAV

**Optimisation** : Chaque niveau vérifie l'existence avant création pour éviter les créations inutiles.
