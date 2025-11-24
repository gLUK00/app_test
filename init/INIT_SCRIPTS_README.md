# Scripts d'initialisation TestGyver

Ce document décrit les scripts situés dans `init/` qui préparent l'environnement de démonstration ou de tests automatisés. Il explique en particulier l'utilisation de `create_full_action_campain.py`, chargé de créer une campagne couvrant toutes les actions disponibles dans TestGyver.

## Prérequis communs

- Python 3.11+
- Dépendances listées dans `requirements.txt` (installer avec `pip install -r requirements.txt`).
- Serveur TestGyver lancé en local (script `start.sh` ou conteneur Docker).
- Accès administrateur à l'API (email/mot de passe disponibles dans `configuration.json`).
- Stack de services de tests lancé via `init/test-docker-compose.yml` pour fournir les cibles FTP/SFTP/WebDAV/HTTP/SSH.

## `init/create_full_action_campain.py`

### Objectif

Automatiser la création d'une campagne contenant un test exhaustif pour chaque type d'action supporté. Le script :

1. lit `init/test-docker-compose.yml` pour récupérer hôtes, ports et identifiants des services de tests ;
2. garantit la présence des variables nécessaires dans l'environnement cible (filière) ;
3. crée une campagne et y associe un logo de test ;
4. prépare les ressources distantes (FTP/SFTP/WebDAV) ainsi que les fichiers locaux dans le workdir de la campagne ;
5. génère les tests HTTP, FTP, SFTP, SSH, IO, WebDAV et VarAction avec des scénarios prêts à l'emploi ;
6. propose de lancer immédiatement la campagne en suivant l'exécution via WebSocket (fallback HTTP) ;
7. propose de nettoyer la campagne une fois le rapport terminé.

### Utilisation rapide

1. Démarrer les services de tests :
   ```bash
   cd init
   docker compose -f test-docker-compose.yml up -d
   ```
2. Lancer le serveur TestGyver (si ce n'est pas déjà fait) ;
3. Exécuter le script :
   ```bash
   python init/create_full_action_campain.py --api-url http://127.0.0.1:5000
   ```
4. Suivre les invites pour saisir l'email/mot de passe admin, le nom de campagne et l'environnement cible.

Options utiles :

| Option | Description |
| ------ | ----------- |
| `--email` / `--password` | Pré-remplissent l'authentification, sinon une invite apparaît. |
| `--campain-name` | Nom proposé par défaut pour la campagne. |
| `--environment` | Filière à utiliser pour les variables (ex. `recette`). |
| `--run` / `--no-run` | Force ou empêche l'exécution automatique sans poser la question. |
| `--cleanup` / `--keep` | Force ou empêche la suppression de la campagne à la fin. |
| `--skip-websocket` | Ignore le suivi Socket.IO et bascule directement sur le polling HTTP. |
| `--run-timeout` | Timeout max (s) pour le suivi de rapport (défaut 600s). |

### Ajouter un nouveau type d'action

Lorsqu'un nouveau plugin d'action est ajouté :

1. **Préparer les services de tests** : si le plugin dépend d'un service externe (SMTP, Kafka, etc.), étendre `init/test-docker-compose.yml` avec le conteneur correspondant, en conservant les ports publiés sur `127.0.0.1`.
2. **Créer les variables nécessaires** : compléter la méthode `_variable_blueprints()` dans `create_full_action_campain.py` pour inclure les clés/filières requises par l'action.
3. **Mettre à jour la génération de tests** :
   - ajouter un builder dans l'attribut `builders` de `_build_blueprints()` ;
   - implémenter une méthode `_build_<action>_tests()` qui retourne une liste de `TestBlueprint` prêts à être envoyés à l'API ;
   - préparer, si besoin, des ressources distantes dans `_prepare_external_services()`.
4. **Documenter le scénario** : décrire brièvement l'action et ses paramètres dans les tests générés (champ `description`) pour faciliter la lecture des rapports.
5. **Mettre à jour ce README** : expliquer le service nécessaire, les variables ajoutées et toute consigne particulière pour exécuter la nouvelle action.

### Dépannage rapide

- **WebSocket indisponible** : le script bascule automatiquement en polling HTTP, mais vérifiez que Socket.IO est activé côté serveur (`flask run` via `start.sh`).
- **Échecs FTP/SFTP/WebDAV** : assurez-vous que `init/test-docker-compose.yml` est démarré et que vos ports ne sont pas occupés par un autre service local.
- **Authentification** : les identifiants par défaut sont définis dans `configuration.json` (`admin@testgyver.local` / `admin`).
- **Manque d'espace disque** : les conteneurs FTP/SFTP/WebDAV utilisent des volumes Docker nommés (`ftp-data`, `sftp-data`, etc.) qui peuvent être purgés via `docker volume rm` si nécessaire.

## Autres scripts

- `init/check_autocomplete_install.sh`, `init/check_plugins.py`, etc. : outils spécialisés décrits dans leurs READMEs respectifs (`docs/*`). Ce document se concentre sur la campagne complète, mais vous pouvez ajouter d'autres sections ici si vous créez de nouveaux scripts d'initialisation.
