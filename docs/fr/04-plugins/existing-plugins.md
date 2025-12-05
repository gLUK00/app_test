# Plugins Existants

TestGyver est livré avec un ensemble de plugins intégrés.

## Réseau & Protocoles

### Requête HTTP (`http`)
Effectue des appels API REST.
*   **Méthodes** : GET, POST, PUT, DELETE.
*   **Fonctionnalités** : En-têtes personnalisés, corps JSON, upload de fichiers.
*   **Sorties** : Code de statut, Corps de réponse, Temps de réponse.

### Commande SSH (`ssh`)
Exécute des commandes shell sur un serveur distant.
*   **Auth** : Nom d'utilisateur/Mot de passe.
*   **Sorties** : Stdout, Stderr, Code de sortie.

### FTP / SFTP (`ftp`, `sftp`)
Opérations de transfert de fichiers.
*   **Actions** : Upload, Download, List, Delete.

### WebDAV (`webdav`)
Interagit avec des serveurs WebDAV.

## Utilitaires

### Opérations E/S (`io`)
Manipulation du système de fichiers sur le serveur TestGyver (dans le workdir de la campagne).
*   **Opérations** : Créer rép, Supprimer fichier/rép, Écrire/Lire variables dans fichiers.

### Conversion de Variable (`var`)
Convertit les types de variables.
*   **Source** : N'importe quelle variable.
*   **Cibles** : int, float, bool, list, dict, json.
*   **Cas d'usage** : Parser une chaîne JSON d'une réponse HTTP en un dictionnaire utilisable.

### Attente (`wait`)
Met en pause l'exécution pour un nombre spécifié de secondes.
