# Tests et Actions

Un **Test** est une séquence d'**Actions**. TestGyver exécute ces actions séquentiellement.

## Créer un Test

1.  Dans une Campagne, cliquez sur **Ajouter un Test**.
2.  Fournissez un nom et une description.
3.  **Ajouter des Variables** (Optionnel) : Définissez des variables spécifiques au test (ex: `username`, `itemId`) qui peuvent être utilisées dans vos actions.

## Ajouter des Actions

Les actions sont les briques élémentaires de votre test.

1.  Cliquez sur **Ajouter une Action**.
2.  **Sélectionner le Type d'Action** : Choisissez parmi les plugins disponibles (ex: Requête HTTP, Commande SSH, Attente).
3.  **Configurer l'Action** : Remplissez les paramètres spécifiques pour l'action choisie.

### Autocomplétion des Variables
Lorsque vous tapez dans les champs texte, TestGyver suggère les variables disponibles :
*   <span style="color:blue">**Variables Globales**</span> : `{{variable_name}}`
*   <span style="color:green">**Variables de Test**</span> : `{{app.variable_name}}`
*   <span style="color:red">**Variables de Collection**</span> : `{{test.test_id}}`, `{{test.files_dir}}`

### Variables de Sortie
Certaines actions produisent une sortie (ex: le corps d'une réponse HTTP).
*   Elles sont affichées comme **Variables de Sortie** dans la configuration de l'action.
*   Vous pouvez les utiliser dans les actions suivantes du même test.

## Ordonnancement des Actions
Les actions sont exécutées dans l'ordre où elles apparaissent. Vous pouvez les réorganiser via l'interface (drag-and-drop ou boutons selon la version).

## Exécution
Vous pouvez lancer un test unique directement depuis la page de Détails du Test pour vérifier son comportement avant de lancer la campagne complète.
