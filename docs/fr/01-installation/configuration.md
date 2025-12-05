# Configuration

L'application est configurée via un fichier `configuration.json` situé à la racine.

## Structure

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
    },
    "jwt_secret": "votre-cle-secrete",
    "app": {
        "debug": true,
        "port": 5000,
        "host": "0.0.0.0"
    },
    "pagination": {
        "page_size": 20,
        "max_page_size": 100
    },
    "security": {
        "token_expiration_minutes": 60,
        "password_min_length": 8
    },
    "workdir": "./workdir",
    "version": "1.0.0"
}
```

## Détail des Paramètres

### Mongo
*   **user** : Nom d'utilisateur MongoDB.
*   **pass** : Mot de passe MongoDB.
*   **host** : Adresse de l'hôte de la base de données (ex: `localhost` ou `mongo` dans Docker).
*   **port** : Port de la base de données (défaut : `27017`).
*   **bdd** : Nom de la base de données à utiliser.
*   **prefix** : Préfixe pour les noms de collections (ex: `mgv_` donne `mgv_users`).
*   **soft_delete** : Si true, les éléments sont marqués comme supprimés au lieu d'être effacés.

### Security
*   **jwt_secret** : Une longue chaîne aléatoire utilisée pour signer les tokens JWT. **Changez-la en production !**
*   **token_expiration_minutes** : Durée de la session en minutes.
*   **password_min_length** : Nombre minimum de caractères pour les mots de passe utilisateurs.

### App
*   **debug** : Active le mode debug Flask (rechargement auto). Mettre à `false` en production.
*   **port** : Port sur lequel l'application écoute.
*   **host** : Interface à écouter (`0.0.0.0` pour toutes les interfaces).

### Workdir
*   **workdir** : Chemin vers le répertoire où les fichiers de campagne et les données temporaires sont stockés.
