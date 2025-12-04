#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Application Flask principale pour TestGyver."""
from flask import Flask, jsonify, request, session, g
from flask_babel import Babel
from models.user import User
# ...existing code...
from flask_swagger_ui import get_swaggerui_blueprint
from flask_socketio import SocketIO, join_room, leave_room
from utils.db import load_config
from utils.workdir import ensure_workdir_exists
from utils.initialization import initialize_variables_from_json
from utils.campain_executor import CampainExecutor
from utils.test_executor import TestExecutor
from routes import (
    auth_bp,
    users_bp,
    campains_bp,
    variables_bp,
    tests_bp,
    rapports_bp,
    web_bp,
    actions_bp,
    plugins_routes,
    deleted_bp
)

# Variable globale pour l'instance SocketIO
socketio = None
babel = Babel()

def get_locale():
    """Sélecteur de locale pour Babel."""
    # 1. Langue stockée dans le profil utilisateur (si connecté)
    user_id = session.get('user_id')
    if user_id:
        user = User.find_by_id(user_id)
        if user and user.get('language'):
            return user['language']
            
    # 2. Langue stockée en session
    if session.get('language'):
        return session['language']
        
    # 3. Langue du navigateur
    # 4. Français par défaut (si request.accept_languages ne trouve rien ou match pas)
    return request.accept_languages.best_match(['en', 'fr', 'es', 'zh', 'de', 'ja']) or 'fr'

def create_app():
    """Crée et configure l'application Flask."""
    global socketio
    
    app = Flask(__name__)
    
    # Charger la configuration
    config = load_config()
    app.config['SECRET_KEY'] = config['jwt_secret']
    app.config['JSON_AS_ASCII'] = False
    
    # Configuration Babel
    app.config['BABEL_DEFAULT_LOCALE'] = 'en'
    app.config['BABEL_SUPPORTED_LOCALES'] = ['en', 'fr', 'es', 'zh', 'de', 'ja']
    babel.init_app(app, locale_selector=get_locale)
    
    # Initialiser SocketIO avec le mode threading pour éviter les conflits avec le debugger
    # et assurer que les tâches de fond ne bloquent pas les heartbeats
    socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')
    
    # Stocker socketio dans les extensions pour un accès facile
    app.extensions['socketio'] = socketio
    
    # Initialiser les exécuteurs
    campain_executor = CampainExecutor(socketio)
    test_executor = TestExecutor(socketio)
    app.config['CAMPAIN_EXECUTOR'] = campain_executor
    app.config['TEST_EXECUTOR'] = test_executor
    
    # Gestionnaires d'événements WebSocket
    @socketio.on('join')
    def handle_join(data):
        """Permet à un client de rejoindre une room."""
        room = data.get('room')
        if room:
            join_room(room)
            print(f"Client rejoint la room: {room}")
    
    @socketio.on('join_rapport')
    def handle_join_rapport(data):
        """Permet à un client de rejoindre la room d'un rapport."""
        rapport_id = data.get('rapport_id')
        if rapport_id:
            room = f'rapport_{rapport_id}'
            join_room(room)
            print(f"Client rejoint la room du rapport: {room}")
    
    @socketio.on('join_test')
    def handle_join_test(data):
        """Permet à un client de rejoindre la room d'un test."""
        test_id = data.get('test_id')
        if test_id:
            room = f'test_{test_id}'
            join_room(room)
            print(f"Client rejoint la room du test: {room}")
    
    @socketio.on('leave')
    def handle_leave(data):
        """Permet à un client de quitter une room."""
        room = data.get('room')
        if room:
            leave_room(room)
            print(f"Client quitte la room: {room}")
    
    # Enregistrer les blueprints pour les routes web
    app.register_blueprint(web_bp)
    
    # Enregistrer les blueprints pour les API
    app.register_blueprint(auth_bp)
    app.register_blueprint(users_bp)
    app.register_blueprint(campains_bp)
    app.register_blueprint(variables_bp)
    app.register_blueprint(tests_bp)
    app.register_blueprint(rapports_bp)
    app.register_blueprint(actions_bp)
    app.register_blueprint(plugins_routes)
    app.register_blueprint(deleted_bp)
    
    # Configuration Swagger UI
    SWAGGER_URL = '/swagger'
    API_URL = '/static/swagger.json'
    
    swaggerui_blueprint = get_swaggerui_blueprint(
        SWAGGER_URL,
        API_URL,
        config={
            'app_name': "TestGyver API"
        }
    )
    app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)
    
    # Route de test
    @app.route('/health')
    def health():
        """Endpoint de santé pour vérifier que l'application fonctionne."""
        return jsonify({
            'status': 'healthy',
            'version': config['version']
        }), 200
    
    # Route pour le favicon
    @app.route('/favicon.ico')
    def favicon():
        """Sert le favicon de l'application."""
        from flask import send_from_directory
        import os
        return send_from_directory(os.path.join(app.root_path, 'static', 'images', 'favicon'),
                                    'favicon.ico', mimetype='image/vnd.microsoft.icon')
    
    # Gestionnaire d'erreurs 404
    @app.errorhandler(404)
    def not_found(error):
        """Gestionnaire d'erreur 404."""
        return jsonify({'message': 'Ressource non trouvée'}), 404
    
    # Gestionnaire d'erreurs 500
    @app.errorhandler(500)
    def internal_error(error):
        """Gestionnaire d'erreur 500."""
        return jsonify({'message': 'Erreur interne du serveur'}), 500
    
    # Contexte de template global
    @app.context_processor
    def inject_config():
        """Injecte la configuration dans tous les templates."""
        return {
            'app_version': config['version'],
            'app_name': 'TestGyver'
        }
    
    return app

# Créer l'application au niveau du module pour Flask CLI
app = create_app()

# Point d'entrée de l'application
if __name__ == '__main__':
    config = load_config()
    
    # Initialiser le répertoire de travail au démarrage
    print("\n" + "="*60)
    print("Initialisation du répertoire de travail des campagnes")
    print("="*60)
    ensure_workdir_exists()
    print("="*60 + "\n")
    
    # Initialiser les variables depuis le fichier JSON si présent
    print("\n" + "="*60)
    print("Initialisation des variables")
    print("="*60)
    initialize_variables_from_json('init/variables.json')
    print("="*60 + "\n")
    
    # Utiliser socketio.run() au lieu de app.run()
    # Désactiver le rechargement automatique pour éviter les redémarrages lors de l'écriture dans workdir
    socketio.run(
        app,
        host=config['app']['host'],
        port=config['app']['port'],
        debug=config['app']['debug'],
        use_reloader=False  # IMPORTANT: Désactiver le reloader pour éviter les redémarrages intempestifs
    )
