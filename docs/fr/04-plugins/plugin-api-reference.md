# Référence API Plugin

## Méthodes `ActionBase`

### `get_metadata(self) -> dict`
Doit retourner un dictionnaire avec :
*   `name` : Nom unique interne.
*   `version` : Version du plugin.
*   `author` : Nom de l'auteur.
*   `description` : Courte description.

### `validate_config(self, config: dict) -> tuple[bool, str]`
Appelé avant l'exécution pour vérifier les paramètres.
*   **Retourne** : `(True, "")` si valide, ou `(False, "Message d'erreur")` si invalide.

### `get_input_mask(self) -> list[dict]`
Définit les champs de l'interface utilisateur. Chaque dict représente un champ :
*   `name` : Clé dans le dictionnaire de configuration.
*   `type` : `string`, `number`, `boolean`, `textarea`, `select`, `select-var-test`.
*   `label` : Nom affiché.
*   `required` : Booléen.
*   `options` : Liste de valeurs (pour `select`).

### `execute(self, context: ActionContext) -> tuple[int, list[str]]`
La logique principale.
*   **Retourne** : `(status_code, traces)`
    *   `status_code` : `0` pour succès, `1` pour échec.
    *   `traces` : Liste de chaînes (logs) à afficher dans le rapport.

## `ActionContext`

Un objet de type dictionnaire passé à `execute()`. Il contient :
*   Les variables résolues.
*   Les informations d'environnement.

## Variables de Sortie

Pour définir une variable de sortie pendant l'exécution :
```python
self.output_variables['ma_var'] = "valeur"
```
Cette valeur sera disponible pour les actions suivantes en tant que `{{ma_var}}`.
