# Prérequis

Avant d'installer TestGyver, assurez-vous que votre système respecte les exigences suivantes.

## Configuration Système

*   **Système d'exploitation** : Linux, macOS ou Windows (WSL2 recommandé).
*   **Mémoire** : Minimum 2GB de RAM recommandé.
*   **Espace Disque** : 500MB pour le code de l'application et les dépendances.

## Logiciels Requis

### Python
TestGyver est construit avec Python. Vous avez besoin de **Python 3.11** ou supérieur.
*   Vérifier la version : `python --version`

### MongoDB
L'application utilise MongoDB comme base de données principale. Vous avez besoin de **MongoDB 6.0** ou supérieur.
*   Vous pouvez l'installer localement ou utiliser un conteneur Docker.
*   [Télécharger MongoDB Community Server](https://www.mongodb.com/try/download/community)

### Git
Requis pour cloner le dépôt.
*   [Télécharger Git](https://git-scm.com/downloads)

### Optionnel
*   **Docker & Docker Compose** : Recommandé pour un déploiement conteneurisé et pour exécuter les environnements de test (serveurs FTP, SFTP pour les tests).
