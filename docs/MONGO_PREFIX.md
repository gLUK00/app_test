# Système de Préfixe pour les Collections MongoDB

## Vue d'ensemble

Cette fonctionnalité permet d'ajouter automatiquement un préfixe à tous les noms de collections MongoDB utilisés par l'application TestGyver. Cela facilite la gestion de multiples instances de l'application sur la même base de données ou la migration de données.

## Configuration

### Activation du préfixe

Le préfixe est configuré dans le fichier `configuration.json` :

```json
{
    "mongo": {
        "user": "root",
        "pass": "mypass",
        "host": "localhost",
        "port": "27017",
        "bdd": "testGyver",
        "prefix": "mgv_"
    }
}
```

### Désactivation du préfixe

Pour désactiver le préfixe, définissez-le comme une chaîne vide :

```json
{
    "mongo": {
        "prefix": ""
    }
}
```

Ou supprimez complètement le champ `prefix` (comportement par défaut) :

```json
{
    "mongo": {
        "user": "root",
        "pass": "mypass",
        "host": "localhost",
        "port": "27017",
        "bdd": "testGyver"
    }
}
```

## Collections affectées

Avec le préfixe `"mgv_"`, les collections suivantes sont créées :

| Collection d'origine | Collection avec préfixe |
|---------------------|------------------------|
| `users`             | `mgv_users`            |
| `variables`         | `mgv_variables`        |
| `campains`          | `mgv_campains`         |
| `tests`             | `mgv_tests`            |
| `rapports`          | `mgv_rapports`         |

## Implémentation technique

### Fonction `get_collection()`

La fonction `get_collection()` dans `utils/db.py` a été modifiée pour appliquer automatiquement le préfixe :

```python
def get_collection(collection_name):
    """Retourne une collection MongoDB spécifique avec le préfixe configuré."""
    db = get_db_connection()
    config = load_config()
    mongo_config = config['mongo']
    
    # Récupérer le préfixe depuis la configuration (vide "" par défaut)
    prefix = mongo_config.get('prefix', '')
    
    # Appliquer le préfixe au nom de la collection
    prefixed_collection_name = f"{prefix}{collection_name}"
    
    return db[prefixed_collection_name]
```

### Compatibilité avec l'existant

#### ✅ Aucune modification nécessaire dans les modèles

Tous les modèles (`User`, `Variable`, `Campain`, `Test`, `Rapport`) utilisent déjà `get_collection()`, donc le préfixe est appliqué automatiquement.

**Exemple dans `models/user.py` :**
```python
class User:
    collection_name = 'users'
    
    @staticmethod
    def create(name, email, password, role='user'):
        collection = get_collection(User.collection_name)
        # → Retourne la collection 'mgv_users' si prefix='mgv_'
```

#### ✅ Références croisées

Les références entre collections fonctionnent automatiquement car elles utilisent également `get_collection()`.

**Exemple dans `models/campain.py` :**
```python
# Ligne 36
user_collection = get_collection('users')
# → Retourne la collection 'mgv_users' si prefix='mgv_'
```

## Cas d'usage

### 1. Multiples instances sur la même base

Vous pouvez exécuter plusieurs instances de TestGyver sur la même base de données MongoDB en utilisant des préfixes différents :

- Instance de production : `"prefix": "prod_"`
- Instance de développement : `"prefix": "dev_"`
- Instance de test : `"prefix": "test_"`

### 2. Migration de données

Le préfixe facilite la migration progressive des données :

1. Créer de nouvelles collections avec le préfixe : `mgv_*`
2. Migrer les données des anciennes collections vers les nouvelles
3. Basculer l'application vers les nouvelles collections
4. Supprimer les anciennes collections

### 3. Isolation par environnement

Dans une base partagée, isoler les données par environnement :

```json
// Production
{"mongo": {"prefix": "prod_"}}

// Staging
{"mongo": {"prefix": "staging_"}}

// Development
{"mongo": {"prefix": "dev_"}}
```

## Tests

Un script de test complet valide le fonctionnement du système de préfixe :

```bash
python3 _build/test_mongo_prefix.py
```

### Tests effectués

1. **test_prefix_configuration** : Vérifie que le préfixe est bien lu depuis la configuration
2. **test_collection_names** : Vérifie que les noms de collections dans les modèles sont corrects
3. **test_get_collection_with_prefix** : Vérifie que `get_collection()` applique le préfixe
4. **test_prefix_default_value** : Teste le comportement avec un préfixe vide ou manquant
5. **test_models_compatibility** : Vérifie la compatibilité avec tous les modèles
6. **test_cross_collection_references** : Vérifie les références croisées entre collections

### Résultat des tests

```
✅ Tests réussis : 6/6

Collections créées :
  - users → mgv_users
  - variables → mgv_variables
  - campains → mgv_campains
  - tests → mgv_tests
  - rapports → mgv_rapports
```

## Impacts sur l'existant

### ✅ Avantages

- **Transparence** : Aucun changement dans le code des modèles
- **Flexibilité** : Le préfixe peut être activé/désactivé facilement
- **Compatibilité** : Fonctionne avec toutes les fonctionnalités existantes
- **Sécurité** : Valeur par défaut vide si le champ n'existe pas

### ⚠️ Points d'attention

1. **Migration de données existantes** : Si vous activez le préfixe sur une installation existante, vous devrez migrer vos données vers les nouvelles collections préfixées.

2. **Cohérence** : Toutes les instances de l'application pointant vers la même base doivent utiliser le même préfixe.

3. **Sauvegarde/Restauration** : Pensez à adapter vos scripts de backup pour inclure les collections préfixées.

## Migration depuis une installation existante

Si vous avez déjà des données dans MongoDB sans préfixe :

### Option 1 : Garder les collections actuelles

Laissez le préfixe vide :
```json
{"mongo": {"prefix": ""}}
```

### Option 2 : Migrer vers des collections préfixées

1. Configurer le préfixe dans `configuration.json`
2. Copier les collections existantes avec le préfixe :

```javascript
// Dans MongoDB
db.users.aggregate([{$out: "mgv_users"}])
db.variables.aggregate([{$out: "mgv_variables"}])
db.campains.aggregate([{$out: "mgv_campains"}])
db.tests.aggregate([{$out: "mgv_tests"}])
db.rapports.aggregate([{$out: "mgv_rapports"}])
```

3. Vérifier que tout fonctionne
4. Supprimer les anciennes collections (optionnel)

```javascript
db.users.drop()
db.variables.drop()
db.campains.drop()
db.tests.drop()
db.rapports.drop()
```

## Dépannage

### Les données ne sont pas trouvées après activation du préfixe

**Cause** : L'application cherche dans les nouvelles collections préfixées, mais les données sont dans les anciennes.

**Solution** : Migrez les données ou désactivez le préfixe.

### Erreur "collection not found"

**Cause** : La collection n'existe pas encore.

**Solution** : MongoDB crée automatiquement les collections lors de la première insertion. Assurez-vous que votre application a les permissions nécessaires.

### Comportement différent entre environnements

**Cause** : Préfixes différents dans les fichiers de configuration.

**Solution** : Vérifiez que tous les environnements utilisent le même préfixe.

## Conclusion

Le système de préfixe pour les collections MongoDB est une fonctionnalité puissante et flexible qui :

- S'intègre de manière transparente avec l'architecture existante
- Ne nécessite aucune modification du code des modèles
- Peut être activé/désactivé facilement
- Facilite la gestion de multiples instances et la migration de données

**Valeur par défaut recommandée** : `"mgv_"` (pour "MacGyver")
