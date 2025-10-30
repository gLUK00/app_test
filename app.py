#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Application Flask principale pour TestGyver."""
from flask import Flask, jsonify
from flask_swagger_ui import get_swaggerui_blueprint
from flask_socketio import SocketIO
from utils.db import load_config
from routes import (
    auth_bp,
    users_bp,
    campains_bp,
    variables_bp,
    tests_bp,
    rapports_bp,
    web_bp,
    actions_bp,
    plugins_routes
)

# Variable globale pour l'instance SocketIO
socketio = None

def create_app():
    """Crée et configure l'application Flask."""
    global socketio
    
    app = Flask(__name__)
    
    # Charger la configuration
    config = load_config()
    app.config['SECRET_KEY'] = config['jwt_secret']
    app.config['JSON_AS_ASCII'] = False
    
    # Initialiser SocketIO
    socketio = SocketIO(app, cors_allowed_origins="*", async_mode='eventlet')
    
    # Stocker socketio dans les extensions pour un accès facile
    app.extensions['socketio'] = socketio
    
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
    
    # Utiliser socketio.run() au lieu de app.run()
    socketio.run(
        app,
        host=config['app']['host'],
        port=config['app']['port'],
        debug=config['app']['debug']
    )
