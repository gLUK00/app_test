# Migration des Actions : parameters → value

## Problème
Les actions des tests utilisaient deux structures différentes :
- Anciennes données : `action.parameters`
- Nouveau code : `action.value`

Cela causait un problème lors de l'édition des tests où les valeurs des actions n'étaient pas remontées dans l'interface.

## Solution
Uniformisation de la structure pour utiliser uniquement `action.value`.

## Fichiers modifiés
- `templates/test_edit.html` : Utilise maintenant uniquement `action.value`
- `templates/test_add.html` : Utilise déjà `action.value` (aucun changement)

## Migration des données

### Exécution du script de migration
Pour migrer les données existantes dans MongoDB :

```bash
python migrate_actions_to_value.py
```

Ce script :
1. Parcourt tous les tests dans la collection `tests`
2. Pour chaque action :
   - Si elle a `parameters` mais pas `value` : renomme `parameters` en `value`
   - Si elle a les deux : supprime `parameters` et garde `value`
3. Affiche un résumé de la migration

### Vérification après migration
Pour vérifier que la migration s'est bien passée :

```bash
mongo
use testGyver
db.tests.find({ "actions.parameters": { $exists: true } }).count()
```

Ce compteur doit retourner 0.

## Structure finale des actions
```json
{
  "type": "http",
  "value": {
    "method": "GET",
    "url": "https://example.com",
    "headers": {},
    "body": null
  },
  "name": "Ma requête HTTP",
  "description": "Description optionnelle"
}
```

## Date de migration
28 octobre 2025
