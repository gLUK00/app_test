# TestGyver

## Choisir votre langue
- Français (défaut)
- [English](README.en.md)
- [Español](README.es.md)
- [Deutsch](README.de.md)
- [Italiano](README.it.md)

## Aperçu
TestGyver est une application de test multi-environnements destinée à orchestrer et documenter des campagnes de tests fonctionnels ou techniques. Inspirée par l'esprit ingénieux de MacGyver, la plateforme combine flexibilité, extensibilité (plugins d'actions) et visibilité (rapports détaillés) au sein d'une interface web construite avec Flask et MongoDB.

## Fonctionnalités majeures
- Authentification JWT avec page de connexion dédiée (`/`).
- Tableau de bord des campagnes accessible après connexion (`/dashboard`).
- Gestion complète des campagnes et de leurs tests (création, édition, actions et rapports).
- Modules d'administration réservés aux comptes `admin` pour gérer utilisateurs et variables multi-environnements.
- Catalogue d'actions extensible (HTTPRequest, WebDAV, FTP, SFTP, SSH, etc.) avec masques de saisie dynamiques.
- Génération de rapports structurés, historisation des exécutions et exposition d'une documentation Swagger (`/swagger`).

## Architecture technique
- **Backend / Frontend** : Flask + Jinja2 + Bootstrap + FontAwesome.
- **Base de données** : MongoDB (collections `users`, `variables`, `campains`, `tests`, `rapports`).
- **Persistance** : PyMongo pour interagir avec MongoDB.
- **Sécurité** : JWT (durée d'expiration configurable) et gestion des rôles (`admin`, `user`).
- **Configuration** : `configuration.json` centralisant les paramètres applicatifs, MongoDB, pagination, sécurité et version.
- **Statique** : ressources dans `static/` (CSS, JS, images) avec CDN locaux.

## Prérequis
- Python 3.11+
- MongoDB 6.x (ou compatible) accessible selon les paramètres de `configuration.json`
- Node facultatif si vous souhaitez étendre les assets statiques
- `pip` et un environnement virtuel recommandé

## Installation
1. Clonez le dépôt :
	```bash
	git clone <url-du-depot> && cd app_test
	```
2. Créez et activez un environnement virtuel :
	```bash
	python -m venv .venv
	source .venv/bin/activate
	```
3. Installez les dépendances :
	```bash
	pip install -r requirements.txt
	```

## Configuration
1. Copiez le modèle de configuration si disponible ou créez `configuration.json` :
	```json
	{
		 "mongo": {
			  "user": "root",
			  "pass": "mypass",
			  "host": "localhost",
			  "port": "27017",
			  "bdd": "testGyver"
		 },
		 "jwt_secret": "change-me",
		 "app": {
			  "debug": true,
			  "port": 5000
		 },
		 "pagination": {
			  "page_size": 20
		 },
		 "security": {
			  "token_expiration_minutes": 60
		 },
		 "version": "1.0.0"
	}
	```
2. Facultatif : créez un fichier `.env` (ignoré par Git) pour stocker les variables sensibles (mot de passe MongoDB, clés API, etc.).

## Exécution locale
1. Démarrez MongoDB (localement ou via Docker) et assurez-vous que les identifiants correspondent à ceux de `configuration.json`.
2. Exportez la variable `FLASK_APP` si nécessaire :
	```bash
	export FLASK_APP=app
	export FLASK_ENV=development
	```
3. Lancez l'application :
	```bash
	flask run --host=0.0.0.0 --port=5000
	```
4. Accédez à l'application sur `http://localhost:5000`.

## Scripts utiles
- `start.sh` : script d'entrée standardisé (utilisé aussi par Docker). Assurez-vous qu'il est exécutable (`chmod +x start.sh`).
- `flask` CLI : gérer les actions de maintenance (création d'utilisateurs admin, migrations éventuelles, etc.).

## Conteneurisation
1. Construisez l'image :
	```bash
	docker build -t testgyver:latest .
	```
2. Lancez le conteneur en liant les variables d'environnement :
	```bash
	docker run -p 5000:5000 --env-file .env testgyver:latest
	```
3. Montez votre `configuration.json` si vous souhaitez l'externaliser :
	```bash
	docker run -p 5000:5000 \
		 -v $(pwd)/configuration.json:/app/configuration.json \
		 --env-file .env \
		 testgyver:latest
	```

## Débogage dans VS Code
1. Installez l'extension Python (ms-python.python) et activez votre environnement.
2. Ouvrez le dépôt dans VS Code.
3. Sélectionnez la configuration **TestGyver: Flask Debug** depuis l'onglet Run and Debug.
4. Placez des points d'arrêt dans vos routes ou actions.
5. Lancez le débogueur pour exécuter `flask run` en mode développement.

## Structure des données
- `users` : informations d'identité, rôle, mot de passe hashé.
- `variables` : paires clé/valeur contextuelles, regroupées par filière/environnement.
- `campains` : métadonnées d'une campagne (auteur, description, date).
- `tests` : actions ordonnées associées à une campagne.
- `rapports` : résultat d'exécution des tests, logs détaillés par test.

## API principales
- `POST /api/login` & `POST /api/logout` : cycle d'authentification JWT.
- `CRUD /api/users` (admin) : gestion des membres.
- `CRUD /api/campains` : orchestration des campagnes.
- `CRUD /api/tests` : gestion des actions par campagne.
- `CRUD /api/variables` (admin) : configuration multi-environnements.
- `CRUD /api/rapports` : génération et consultation des rapports.
- `GET /swagger` : documentation interactive.

## Personnalisation des actions
Chaque classe dans `plugins/actions` hérite de `ActionBase` et fournit :
- un schéma JSON décrivant le masque de saisie (type, label, placeholder, etc.) ;
- une méthode `execute(ActionContext)` qui orchestre la logique métier ;
- des traces d'exécution exploitables dans les rapports.

## Aller plus loin
- Ajoutez vos propres actions en étendant `ActionBase`.
- Intégrez un orchestrateur (GitHub Actions, Jenkins) pour planifier l'exécution de campagnes.
- Connectez une plateforme de notification (Slack, Teams, courriel) pour diffuser les rapports automatiquement.

## Support
Pour toute question ou suggestion merci d'ouvrir une issue GitHub ou de contacter l'équipe TestGyver.

