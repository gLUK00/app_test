# Gestion des Campagnes

Une **Campagne** est un regroupement logique de tests conçus pour valider une fonctionnalité ou un flux de travail spécifique.

## Créer une Campagne

1.  Depuis le Tableau de Bord, cliquez sur **Ajouter une Campagne**.
2.  Remplissez les détails :
    *   **Nom** : Un nom unique pour votre campagne.
    *   **Description** : Détails optionnels sur l'objectif de la campagne.
3.  Cliquez sur **Enregistrer**. Vous serez redirigé vers la page de Détails de la Campagne.

![Formulaire Ajouter une Campagne](../../assets/campaign_add.png)
> Le formulaire "Ajouter une Campagne".

## Vue Détails de la Campagne

C'est le centre de contrôle de votre campagne.

![Détails de campagne](../../assets/campaign_detail.png)
> Page de détails d'une campagne montrant les sections Informations, Fichiers et Tests.

### 1. Informations
Affiche les métadonnées de la campagne. Vous pouvez modifier ou supprimer la campagne d'ici.

### 2. Gestion des Fichiers
Cette section vous permet de gérer les fichiers associés à la campagne (ex: fichiers de données pour les tests, ressources uploadées).
*   **Uploader** : Ajouter des fichiers au répertoire de travail de la campagne.
*   **Renommer/Supprimer** : Gérer les fichiers existants.
*   **Télécharger** : Récupérer les fichiers.

Ces fichiers sont accessibles dans vos tests via la variable `{{test.files_dir}}`.

### 3. Rapports Générés
Cette section liste tous les rapports (HTML, PDF, etc.) qui ont été générés à partir des exécutions de cette campagne.
*   **Visualiser** : Voir le type, la date et la taille de chaque rapport.
*   **Télécharger** : Récupérer le fichier du rapport.
*   **Supprimer** : Effacer les anciens rapports.
*   **Rafraîchir** : Mettre à jour la liste des rapports disponibles.

### 4. Liste des Tests
Affiche tous les tests de la campagne.
*   **Réorganiser** : Utilisez les flèches Haut/Bas pour changer l'ordre d'exécution.
*   **Ajouter un Test** : Créer un nouveau cas de test.
*   **Exécuter** : Lancer un test spécifique individuellement.

## Exécuter une Campagne

1.  Cliquez sur le bouton **Lancer la Campagne**.
2.  **Configurer l'Exécution** :
    *   **Nom** : Auto-généré (ex: "Mars 2023"), mais personnalisable.
    *   **Environnement** : Sélectionnez l'environnement cible (défini dans les Variables).
    *   **Arrêt sur Erreur** : Si coché, la campagne s'arrête immédiatement si un test échoue.
3.  **Lancer** : L'exécution démarre en arrière-plan.

![Modale d'exécution](../../assets/campaign_rapport.png)
> La modale "Lancer la Campagne" avec la sélection de l'environnement.

### Suivi en Temps Réel
Vous verrez une barre de progression et des mises à jour de statut.
*   **Bleu** : En cours
*   **Vert** : Terminé avec succès
*   **Rouge** : Échoué

Cliquez sur un rapport en cours ou terminé pour voir les logs détaillés.

## Structures de Données des Plugins

Les structures de données des plugins permettent de sauvegarder des configurations réutilisables pour les plugins d'action. C'est particulièrement utile pour stocker des identifiants de connexion (WebDAV, FTP, S3, SSH, etc.) que vous utilisez fréquemment dans plusieurs tests.

### Concept

Certains plugins d'action (WebDAV, FTP, SFTP, S3, SSH) fournissent une fonction `get_structure()` qui définit les champs configurables pour ce plugin. Par exemple, un plugin WebDAV peut définir :

| Champ | Type | Description |
|-------|------|-------------|
| url | string | URL du serveur WebDAV |
| username | string | Nom d'utilisateur |
| password | password | Mot de passe (masqué) |

### Créer une Structure de Données

1. Sur la page Détails de la Campagne, trouvez la section **Structures de données des plugins**.
2. Cliquez sur **Ajouter une structure**.
3. Sélectionnez un **Type de plugin** dans la liste déroulante (seuls les plugins supportant les structures de données sont listés).
4. Entrez un **Nom de structure** (ex: "Serveur WebDAV Production").
5. Remplissez les **valeurs** pour chaque champ.
6. Cliquez sur **Enregistrer**.

### Gérer les Structures de Données

La section Structures de données des plugins affiche toutes les configurations sauvegardées avec :

| Colonne | Description |
|---------|-------------|
| Nom | Le nom unique que vous avez donné à la structure |
| Type de plugin | Le type de plugin d'action (affiché comme badge coloré) |
| Créé | Date de création |
| Actions | Boutons Voir, Modifier ou Supprimer |

#### Actions Disponibles :
*   **Voir** (👁) : Ouvre une modale affichant les valeurs stockées de la structure (les mots de passe sont masqués).
*   **Modifier** (✏️) : Modifier le nom ou les valeurs de la structure.
*   **Supprimer** (🗑) : Supprimer la structure (avec confirmation).

### Cas d'Utilisation

1. **Identifiants Centralisés** : Stockez les identifiants WebDAV, FTP ou S3 une seule fois et référencez-les dans plusieurs tests.
2. **Changement d'Environnement** : Créez des structures séparées pour les environnements "Développement", "Staging" et "Production".
3. **Collaboration en Équipe** : Partagez des configurations cohérentes entre les membres de l'équipe via l'export/import de campagnes.

### Export et Import

Les structures de données des plugins sont automatiquement incluses lors de l'export d'une campagne. Lors de l'import d'une campagne, toutes les structures sont restaurées avec leurs valeurs originales.

!!! note "Note de Sécurité"
    Les mots de passe et données sensibles marqués avec `obfuscate: true` sont stockés dans la base de données mais affichés comme `••••••••` dans l'interface. Soyez prudent lors de l'export des campagnes car les valeurs réelles sont incluses dans le fichier JSON.
