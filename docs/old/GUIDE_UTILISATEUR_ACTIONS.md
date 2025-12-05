# Guide Utilisateur - Gestion des Actions dans les Tests

## Vue d'ensemble

Chaque test dans TestGyver est maintenant composé d'une **série d'actions** qui seront exécutées séquentiellement. Cette approche vous permet de créer des scénarios de test complexes combinant différents types d'actions.

## Qu'est-ce qu'une action ?

Une action représente une opération spécifique à effectuer lors de l'exécution du test. Il existe plusieurs types d'actions :

- **HTTP Request** : Envoyer des requêtes HTTP/HTTPS
- **FTP** : Se connecter et transférer des fichiers via FTP
- **SFTP** : Se connecter et transférer des fichiers via SFTP (FTP sécurisé)
- **SSH** : Exécuter des commandes sur un serveur distant via SSH
- **WebDAV** : Interagir avec des serveurs WebDAV

## Créer un nouveau test

### 1. Accéder à la page de création

Depuis la page de détails d'une campagne, cliquez sur le bouton **"+ Ajouter un test"**.

### 2. Renseigner les informations du test

- **Nom du test** (obligatoire) : Un nom descriptif pour identifier votre test
- **Description** (optionnel) : Des détails supplémentaires sur l'objectif du test

### 3. Ajouter des actions

#### Ajouter une première action

1. Cliquez sur le bouton **"+ Ajouter une action"**
2. Une fenêtre modale s'ouvre avec les champs suivants :
   - **Nom de l'action** : Identifiez clairement cette étape (ex: "Connexion au serveur", "Upload du fichier")
   - **Description** : Détails optionnels sur cette action
   - **Type d'action** : Sélectionnez le type approprié
   
3. Selon le type d'action choisi, des **champs spécifiques** apparaîtront :

   **Exemple pour HTTP Request :**
   - URL
   - Méthode (GET, POST, PUT, DELETE)
   - Headers (format JSON)
   - Body (format JSON)
   
   **Exemple pour FTP :**
   - Host
   - Port
   - Username
   - Password
   - Opération (upload, download, list)
   
4. Remplissez tous les champs obligatoires (marqués d'un astérisque *)
5. Cliquez sur **"Enregistrer"**

#### Ajouter d'autres actions

Répétez le processus pour chaque action à inclure dans votre test. Les actions seront exécutées dans l'ordre dans lequel vous les ajoutez.

### 4. Gérer vos actions

Une fois les actions ajoutées, vous pouvez :

#### Réorganiser l'ordre d'exécution
- Utilisez les boutons **flèche haut** ⬆️ et **flèche bas** ⬇️ pour changer l'ordre
- L'action en haut de la liste (#1) sera exécutée en premier

#### Modifier une action
- Cliquez sur le bouton **crayon** ✏️ pour ouvrir le modal d'édition
- Modifiez les champs nécessaires
- Cliquez sur "Enregistrer"

#### Supprimer une action
- Cliquez sur le bouton **poubelle** 🗑️
- Confirmez la suppression dans la boîte de dialogue

### 5. Finaliser la création

Une fois toutes vos actions configurées :
1. Vérifiez que l'ordre est correct
2. Cliquez sur le bouton **"Créer le test"**
3. Vous serez redirigé vers la page de détails de la campagne

## Modifier un test existant

### 1. Accéder à l'édition

Depuis la page de détails de la campagne :
1. Trouvez le test que vous souhaitez modifier dans la liste
2. Cliquez sur le bouton **crayon** ✏️ dans la colonne "Actions"

### 2. Apporter vos modifications

Vous pouvez :
- Modifier le nom et la description du test
- Ajouter de nouvelles actions
- Modifier les actions existantes
- Supprimer des actions
- Réorganiser l'ordre des actions

### 3. Enregistrer ou supprimer

- **"Enregistrer les modifications"** : Sauvegarde toutes vos modifications
- **"Supprimer le test"** : Supprime définitivement le test et toutes ses actions (avec confirmation)

## Bonnes pratiques

### Nommage des actions
Utilisez des noms descriptifs qui indiquent clairement ce que fait chaque action :
- ✅ "Connexion au serveur de production"
- ✅ "Upload du fichier de configuration"
- ✅ "Vérification de la réponse HTTP"
- ❌ "Action 1"
- ❌ "Test"

### Organisation des actions
1. **Ordre logique** : Organisez vos actions dans l'ordre d'exécution souhaité
2. **Actions préparatoires** : Placez les actions de setup en premier (connexions, initialisations)
3. **Actions principales** : Les opérations de test au milieu
4. **Actions de nettoyage** : Les opérations de cleanup en dernier (si applicable)

### Utilisation des descriptions
Utilisez les descriptions pour :
- Expliquer le contexte de l'action
- Documenter les valeurs attendues
- Ajouter des notes pour les autres utilisateurs

### Tests modulaires
Créez des tests avec un nombre raisonnable d'actions (5-10 maximum recommandé) pour :
- Faciliter la maintenance
- Améliorer la lisibilité
- Simplifier le débogage en cas d'échec

## Exemples de scénarios

### Scénario 1 : Test d'API REST
1. **Action #1 - HTTP Request** : POST /api/login (récupérer un token)
2. **Action #2 - HTTP Request** : GET /api/users (avec le token)
3. **Action #3 - HTTP Request** : POST /api/users (créer un utilisateur)
4. **Action #4 - HTTP Request** : DELETE /api/users/123 (supprimer l'utilisateur)

### Scénario 2 : Déploiement de fichier
1. **Action #1 - SSH** : Arrêter le service sur le serveur
2. **Action #2 - SFTP** : Upload du nouveau fichier
3. **Action #3 - SSH** : Modifier les permissions
4. **Action #4 - SSH** : Redémarrer le service

### Scénario 3 : Test de backup
1. **Action #1 - SSH** : Créer un backup de la base de données
2. **Action #2 - SFTP** : Télécharger le backup
3. **Action #3 - HTTP Request** : Notifier le système de monitoring

## Dépannage

### L'action ne s'enregistre pas
- Vérifiez que tous les champs obligatoires sont remplis
- Vérifiez que les valeurs JSON (headers, body) sont valides

### Impossible de créer le test
- Assurez-vous d'avoir ajouté au moins une action
- Vérifiez que le nom du test est renseigné

### Les actions ne s'exécutent pas dans le bon ordre
- Utilisez les boutons de réorganisation avant de sauvegarder le test
- L'ordre affiché dans la liste est l'ordre d'exécution

## Support

Pour toute question ou problème, consultez la documentation complète ou contactez votre administrateur système.
