# Suppression Logique (Soft Delete)

## Vue d'ensemble

La fonctionnalité de **suppression logique** (soft delete) permet de "supprimer" des éléments (tests, campagnes, rapports) sans les supprimer physiquement de la base de données. Les éléments supprimés logiquement sont marqués avec un champ `isDeleted: true` et peuvent être restaurés ou supprimés définitivement par un administrateur.

## Configuration

### Activation de la suppression logique

La suppression logique est contrôlée par un paramètre dans le fichier `configuration.json` :

```json
{
  "mongo": {
    "user": "root",
    "pass": "mypass",
    "host": "localhost",
    "port": "27017",
    "bdd": "testGyver",
    "prefix": "mgv_",
    "soft_delete": true
  }
}
```

- **`soft_delete: true`** : Active la suppression logique
- **`soft_delete: false`** : Désactive la suppression logique (comportement de suppression physique classique)

### Comportement selon la configuration

| Configuration | Comportement lors de la suppression |
|--------------|-------------------------------------|
| `soft_delete: true` | L'élément est marqué `isDeleted: true` et reste en base de données |
| `soft_delete: false` | L'élément est supprimé physiquement de la base de données |

## Structure des données

### Champ `isDeleted`

Tous les documents des collections `tests`, `campains` et `rapports` possèdent désormais un champ `isDeleted` :

```javascript
{
  "_id": ObjectId("..."),
  // ... autres champs ...
  "isDeleted": false,        // false par défaut lors de la création
  "dateDeleted": ISODate()   // Date de suppression (ajouté uniquement si isDeleted: true)
}
```

- **`isDeleted: false`** : Élément actif (valeur par défaut)
- **`isDeleted: true`** : Élément supprimé logiquement
- **`dateDeleted`** : Date/heure de suppression (présent uniquement si supprimé)

## Fonctionnalités

### Modèles mis à jour

Les modèles `Test`, `Campain` et `Rapport` ont été modifiés pour gérer la suppression logique :

#### Méthodes de base

- **`create()`** : Crée un nouvel élément avec `isDeleted: false`
- **`get_all()`** : Retourne uniquement les éléments avec `isDeleted != true`
- **`get_by_campain()`** : Retourne uniquement les éléments actifs d'une campagne
- **`delete(id)`** : Suppression logique (si activée) ou physique (si désactivée)

#### Nouvelles méthodes

- **`get_deleted()`** : Retourne tous les éléments avec `isDeleted: true`
- **`restore(id)`** : Restaure un élément supprimé (met `isDeleted: false`)
- **`permanent_delete(id)`** : Supprime définitivement un élément de la base de données

### Exemple d'utilisation des modèles

```python
from models.campain import Campain

# Créer une campagne
campain_id = Campain.create(user_id, "Ma campagne", "Description")

# Supprimer logiquement
Campain.delete(campain_id)

# Récupérer les campagnes supprimées
deleted_campains = Campain.get_deleted()

# Restaurer
Campain.restore(campain_id)

# Supprimer définitivement
Campain.permanent_delete(campain_id)
```

## API REST

### Routes disponibles

#### Récupérer les éléments supprimés

```
GET /api/deleted/tests
GET /api/deleted/campains
GET /api/deleted/rapports
GET /api/deleted/all
```

**Authentification requise** : Oui (Admin uniquement)

**Réponse** (`/api/deleted/all`) :
```json
{
  "tests": [...],
  "campains": [...],
  "rapports": [...]
}
```

#### Restaurer des éléments

```
POST /api/deleted/restore
```

**Corps de la requête** :
```json
{
  "items": [
    {"type": "test", "id": "64abc123..."},
    {"type": "campain", "id": "64abc456..."}
  ]
}
```

**Réponse** :
```json
{
  "restored": [
    {"type": "test", "id": "64abc123..."}
  ],
  "errors": [],
  "success": true
}
```

#### Supprimer définitivement

```
DELETE /api/deleted/permanent
```

**Corps de la requête** :
```json
{
  "items": [
    {"type": "rapport", "id": "64abc789..."}
  ]
}
```

**Réponse** :
```json
{
  "deleted": [
    {"type": "rapport", "id": "64abc789..."}
  ],
  "errors": [],
  "success": true
}
```

## Interface d'administration

### Page de gestion

Une page d'administration est disponible à l'adresse `/admin/deleted` (accessible uniquement aux administrateurs).

#### Fonctionnalités de la page

- **Onglets séparés** pour Tests, Campagnes et Rapports
- **Compteurs** indiquant le nombre d'éléments supprimés par type
- **Sélection multiple** avec cases à cocher
- **Actions groupées** :
  - Restaurer la sélection
  - Supprimer définitivement la sélection
- **Actions individuelles** :
  - Restaurer un élément (icône ↶)
  - Supprimer définitivement un élément (icône 🗑️)

#### Confirmations

- **Restauration** : Modale de confirmation simple
- **Suppression définitive** : Modale de confirmation avec avertissement ⚠️ (action irréversible)

### Accès à la page

La page est accessible depuis le menu **Administration** → **Éléments supprimés** (visible uniquement pour les administrateurs).

## Migration des données existantes

### Script de migration

Un script de migration est fourni pour ajouter le champ `isDeleted: false` à tous les documents existants :

```bash
python3 _build/migrate_soft_delete.py
```

#### Que fait le script ?

1. Parcourt les collections `tests`, `campains` et `rapports`
2. Ajoute `isDeleted: false` aux documents qui n'ont pas ce champ
3. Affiche un résumé de la migration
4. Effectue une vérification après migration

#### Sortie du script

```
================================================================================
MIGRATION - Ajout du champ isDeleted aux collections
================================================================================

📋 Migration de la collection 'tests'...
  📊 15 document(s) à migrer
  ✅ Migration terminée : 15 document(s) mis à jour

📋 Migration de la collection 'campains'...
  📊 8 document(s) à migrer
  ✅ Migration terminée : 8 document(s) mis à jour

📋 Migration de la collection 'rapports'...
  📊 12 document(s) à migrer
  ✅ Migration terminée : 12 document(s) mis à jour

================================================================================
✅ MIGRATION TERMINÉE AVEC SUCCÈS
================================================================================
```

### Exécution recommandée

Il est recommandé d'exécuter le script de migration **avant** d'activer la fonctionnalité en production :

1. Sauvegarder la base de données
2. Exécuter le script de migration
3. Vérifier les résultats
4. Activer `soft_delete: true` dans `configuration.json`
5. Redémarrer l'application

## Tests

### Script de tests unitaires

Un script de tests est fourni pour valider la fonctionnalité :

```bash
python3 _build/test_soft_delete.py
```

#### Tests effectués

1. **Configuration** : Vérifie que `soft_delete` est activé
2. **Campagnes** : Teste suppression logique, restauration et suppression définitive
3. **Tests** : Teste suppression logique, restauration et suppression définitive
4. **Rapports** : Teste suppression logique, restauration et suppression définitive

#### Sortie du script

```
================================================================================
TESTS UNITAIRES - SUPPRESSION LOGIQUE (SOFT DELETE)
================================================================================

📋 Test 1: Vérification de la configuration soft_delete
  ℹ️  Suppression logique activée: True
  ✅ La suppression logique est activée

📋 Test 2: Suppression logique d'une campagne
  ✅ Campagne créée: 64abc123...
  ✅ Campagne supprimée (soft delete): True
  ✅ La campagne supprimée n'apparaît plus dans get_all()
  ✅ La campagne apparaît dans get_deleted()
  ✅ Campagne restaurée: True
  ✅ La campagne restaurée apparaît dans get_all()
  ✅ Campagne supprimée définitivement: True
  ✅ La campagne ne figure plus dans get_deleted() après suppression définitive

================================================================================
RÉSUMÉ DES TESTS
================================================================================
✅ RÉUSSI: Configuration soft_delete
✅ RÉUSSI: Suppression logique campagnes
✅ RÉUSSI: Suppression logique tests
✅ RÉUSSI: Suppression logique rapports

Total: 4 tests | Réussis: 4 | Échecs: 0
================================================================================

✅ Tous les tests sont passés avec succès!
```

## Impacts sur l'existant

### Compatibilité

✅ **Rétrocompatible** : Les documents existants sans le champ `isDeleted` sont traités comme actifs grâce au filtre `{'isDeleted': {'$ne': True}}`.

### Comportement des requêtes

| Méthode | Avant | Après (soft_delete activé) |
|---------|-------|---------------------------|
| `get_all()` | Tous les documents | Seulement `isDeleted != true` |
| `get_by_campain()` | Tous les documents de la campagne | Seulement `isDeleted != true` |
| `delete()` | Suppression physique | Ajout `isDeleted: true` |
| `find_by_id()` | Document par ID | **Pas de filtre** (retourne même si supprimé) |

⚠️ **Note** : `find_by_id()` retourne le document même s'il est supprimé logiquement. C'est voulu pour permettre la visualisation dans la page d'administration.

### Ordre des tests

Les tests d'une campagne sont triés par ordre d'exécution, **en excluant** automatiquement les tests supprimés logiquement.

## Sécurité

### Contrôle d'accès

- ✅ Toutes les routes `/api/deleted/*` nécessitent une authentification
- ✅ Toutes les routes `/api/deleted/*` nécessitent le rôle **admin**
- ✅ La page `/admin/deleted` nécessite le rôle **admin**

### Validation

- ✅ Validation du format des données (type + id requis)
- ✅ Gestion des erreurs pour chaque élément individuellement
- ✅ Retour détaillé avec éléments réussis et erreurs

## Documentation Swagger

La documentation Swagger a été mise à jour avec :

- **Nouveau tag** : "Éléments supprimés"
- **6 nouvelles routes** :
  - `GET /api/deleted/tests`
  - `GET /api/deleted/campains`
  - `GET /api/deleted/rapports`
  - `GET /api/deleted/all`
  - `POST /api/deleted/restore`
  - `DELETE /api/deleted/permanent`

Accessible via : `http://localhost:5000/swagger`

## Désactivation de la fonctionnalité

Pour revenir au comportement de suppression physique :

1. Modifier `configuration.json` : `"soft_delete": false`
2. Redémarrer l'application

⚠️ **Attention** : Les éléments marqués `isDeleted: true` ne seront pas automatiquement supprimés. Ils resteront en base de données mais seront invisibles dans l'application.

## Recommandations

### En production

1. **Sauvegarde** : Effectuer une sauvegarde avant activation
2. **Migration** : Exécuter le script de migration sur les données existantes
3. **Tests** : Vérifier le bon fonctionnement avec le script de tests
4. **Monitoring** : Surveiller la taille de la base de données

### Maintenance

- **Nettoyage régulier** : Supprimer définitivement les anciens éléments supprimés
- **Archivage** : Exporter les éléments supprimés avant suppression définitive
- **Audit** : Logger les restaurations et suppressions définitives

## Troubleshooting

### Problème : Les éléments supprimés apparaissent encore

**Cause** : Le champ `isDeleted` n'existe pas sur certains documents

**Solution** : Exécuter le script de migration
```bash
python3 _build/migrate_soft_delete.py
```

### Problème : Impossible de restaurer un élément

**Cause** : L'élément n'existe plus (suppression définitive)

**Solution** : Restaurer depuis une sauvegarde de la base de données

### Problème : Erreur 403 sur les routes /api/deleted/*

**Cause** : Utilisateur non administrateur

**Solution** : Se connecter avec un compte administrateur

## Fichiers modifiés

### Configuration
- `configuration.json` : Ajout du paramètre `soft_delete`

### Utilitaires
- `utils/db.py` : Fonction `is_soft_delete_enabled()`

### Modèles
- `models/test.py` : Méthodes soft delete
- `models/campain.py` : Méthodes soft delete
- `models/rapport.py` : Méthodes soft delete

### Routes
- `routes/deleted_routes.py` : Nouvelles routes API (créé)
- `routes/__init__.py` : Export du blueprint
- `routes/web_routes.py` : Route `/admin/deleted`
- `app.py` : Enregistrement du blueprint

### Templates
- `templates/base.html` : Lien dans le menu admin
- `templates/admin/deleted.html` : Page d'administration (créé)

### Scripts
- `_build/migrate_soft_delete.py` : Migration des données (créé)
- `_build/test_soft_delete.py` : Tests unitaires (créé)

### Documentation
- `static/swagger.json` : Documentation API
- `docs/SOFT_DELETE.md` : Cette documentation (créé)

## Conclusion

La fonctionnalité de suppression logique offre :

✅ **Sécurité** : Protection contre les suppressions accidentelles  
✅ **Flexibilité** : Possibilité de restaurer des éléments supprimés  
✅ **Traçabilité** : Conservation de l'historique avec dates de suppression  
✅ **Conformité** : Respect des exigences d'archivage et d'audit  
✅ **Simplicité** : Activation/désactivation par simple configuration  

La mise en œuvre est complète avec API, interface utilisateur, migration, tests et documentation.
