# Plugins Existants

TestGyver est livré avec un ensemble de plugins intégrés.

## Réseau & Protocoles

### Requête HTTP (`http`)
Effectue des appels API REST.
*   **Couleur** : <span style="color: #0d6efd">Bleu (#0d6efd)</span>
*   **Méthodes** : GET, POST, PUT, DELETE.
*   **Fonctionnalités** : En-têtes personnalisés, corps JSON, upload de fichiers.
*   **Sorties** : Code de statut, Corps de réponse, Temps de réponse.

### Commande SSH (`ssh`)
Exécute des commandes shell sur un serveur distant.
*   **Couleur** : <span style="color: #212529">Sombre (#212529)</span>
*   **Auth** : Nom d'utilisateur/Mot de passe.
*   **Sorties** : Stdout, Stderr, Code de sortie.

### FTP / SFTP (`ftp`, `sftp`)
Opérations de transfert de fichiers.
*   **Couleur FTP** : <span style="color: #fd7e14">Orange (#fd7e14)</span>
*   **Couleur SFTP** : <span style="color: #20c997">Sarcelle (#20c997)</span>
*   **Actions** : Upload, Download, List, Delete.

### WebDAV (`webdav`)
Interagit avec des serveurs WebDAV.
*   **Couleur** : <span style="color: #6610f2">Violet (#6610f2)</span>

### Stockage S3 (`s3`)
Interagit avec des services de stockage compatibles S3 (AWS, MinIO, etc.).
*   **Couleur** : <span style="color: #dc3545">Rouge (#dc3545)</span>
*   **Actions** : Upload, Download, List, Delete.

## Utilitaires

### Opérations E/S (`io`)
Manipulation du système de fichiers sur le serveur TestGyver (dans le workdir de la campagne).
*   **Couleur** : <span style="color: #198754">Vert (#198754)</span>
*   **Opérations** : Créer rép, Supprimer fichier/rép, Écrire/Lire variables dans fichiers.

### Conversion de Variable (`var`)
Convertit les types de variables.
*   **Couleur** : <span style="color: #ffc107">Jaune (#ffc107)</span>
*   **Source** : N'importe quelle variable.
*   **Cibles** : int, float, bool, list, dict, json.
*   **Cas d'usage** : Parser une chaîne JSON d'une réponse HTTP en un dictionnaire utilisable.

### Pause (`pause`)
Met en pause l'exécution pour un nombre spécifié de secondes.
*   **Couleur** : <span style="color: #0dcaf0">Cyan (#0dcaf0)</span>

