# Changelog - Gestion des Actions dans les Tests

## Date : 28 octobre 2025

## Modifications apportées

### 1. Page d'ajout de test (`templates/test_add.html`)

#### Changements principaux :
- **Suppression du champ "Type de test"** : Le concept de type unique a été remplacé par une liste d'actions
- **Ajout de la gestion des actions multiples** : Chaque test peut maintenant contenir plusieurs actions
- **Interface utilisateur améliorée** :
  - Section séparée pour les informations du test (nom, description)
  - Carte dédiée pour la liste des actions
  - Modal Bootstrap pour ajouter/modifier les actions

#### Fonctionnalités implémentées :
1. **Ajout d'actions** : Bouton "+ Ajouter une action" qui ouvre un modal
2. **Modification d'actions** : Bouton d'édition pour chaque action dans la liste
3. **Suppression d'actions** : Bouton de suppression avec confirmation
4. **Réorganisation d'actions** : Boutons flèche haut/bas pour changer l'ordre d'exécution
5. **Affichage visuel** : Badges numérotés (#1, #2, etc.) et types d'actions colorés

### 2. Page d'édition de test (`templates/test_edit.html`) - NOUVEAU

#### Création d'une nouvelle page :
- Permet de modifier un test existant
- Charge automatiquement les actions du test
- Interface identique à la page d'ajout pour une expérience cohérente
- Bouton de suppression du test complet

### 3. Routes web (`routes/web_routes.py`)

#### Ajout de la route :
```python
@web_bp.route('/campains/<campain_id>/edit/test/<test_id>')
@token_required
def edit_test(campain_id, test_id):
    """Page d'édition d'un test."""
```

### 4. Page de détails de campagne (`templates/campain_details.html`)

#### Modifications :
- Mise à jour de l'affichage des tests pour montrer :
  - Le nombre d'actions par test
  - Les types d'actions utilisés (badges multiples)
  - Nom et description de la première action comme titre du test
- Ajout d'un bouton "Modifier" pour chaque test
- Amélioration de l'interface avec des groupes de boutons

### 5. Styles CSS (`static/css/custom.css`)

#### Ajout de styles :
- `.action-item` : Style pour les cartes d'actions avec bordure gauche colorée
- `.action-item:hover` : Effet au survol avec ombre et translation
- Styles pour le modal et les champs dynamiques
- Amélioration des badges

## Structure des données

### Format d'un test :
```json
{
  "campain_id": "...",
  "actions": [
    {
      "name": "Nom de l'action",
      "description": "Description optionnelle",
      "type": "http|ftp|sftp|ssh|webdav",
      "parameters": {
        // Paramètres spécifiques au type d'action
      }
    }
  ]
}
```

## Flux utilisateur

### Création d'un test :
1. Remplir le nom et la description du test (optionnel)
2. Cliquer sur "+ Ajouter une action"
3. Dans le modal :
   - Saisir le nom de l'action
   - Saisir la description (optionnel)
   - Sélectionner le type d'action
   - Remplir les champs spécifiques qui apparaissent dynamiquement
4. Cliquer sur "Enregistrer"
5. Répéter les étapes 2-4 pour ajouter d'autres actions
6. Réorganiser les actions si nécessaire avec les flèches
7. Cliquer sur "Créer le test"

### Modification d'un test :
1. Depuis la page de détails de la campagne, cliquer sur le bouton "Modifier" du test
2. Modifier les informations du test et/ou ses actions
3. Cliquer sur "Enregistrer les modifications"

## Avantages de cette approche

1. **Flexibilité** : Un test peut combiner différents types d'actions (HTTP, FTP, SSH, etc.)
2. **Séquencement** : Les actions sont exécutées dans l'ordre défini
3. **Réutilisabilité** : Chaque action est indépendante et peut être facilement modifiée
4. **Clarté** : Interface visuelle claire avec numérotation et badges de type
5. **Contrôle** : Possibilité de réorganiser, modifier ou supprimer des actions individuellement

## Notes techniques

- Le système utilise toujours les masques de saisie dynamiques (`/api/actions/masks`)
- La validation des champs requis est maintenue
- Le support JSON pour les headers et body est préservé
- Les notifications utilisent le système `Notification` global
- Bootstrap 5 est utilisé pour le modal et les composants UI

## Compatibilité

- Rétrocompatible avec l'API existante
- Le modèle de données `Test` supporte déjà le format `actions` en array
- Les routes API n'ont pas été modifiées
