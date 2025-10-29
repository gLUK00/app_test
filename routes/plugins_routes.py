"""Routes pour la gestion des plugins."""
from flask import Blueprint, jsonify, request
from plugins import plugin_registry
from utils.auth import token_required, admin_required

plugins_routes = Blueprint('plugins_routes', __name__)


@plugins_routes.route('/api/plugins', methods=['GET'])
@token_required
def get_all_plugins_api(current_user):
    """
    Récupère tous les plugins disponibles.
    ---
    tags:
      - Plugins
    security:
      - Bearer: []
    responses:
      200:
        description: Liste de tous les plugins
        schema:
          type: object
          properties:
            actions:
              type: object
            reports:
              type: object
            auth:
              type: object
    """
    try:
        plugins = plugin_registry.get_all_plugins()
        return jsonify(plugins), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@plugins_routes.route('/api/plugins/<plugin_type>', methods=['GET'])
@token_required
def get_plugins_by_type(current_user, plugin_type):
    """
    Récupère les plugins d'un type spécifique.
    ---
    tags:
      - Plugins
    security:
      - Bearer: []
    parameters:
      - name: plugin_type
        in: path
        type: string
        required: true
        description: Type de plugin (actions, reports, auth)
    responses:
      200:
        description: Liste des plugins du type spécifié
      404:
        description: Type de plugin non trouvé
    """
    try:
        manager = plugin_registry.get_manager(plugin_type)
        if not manager:
            return jsonify({"error": f"Type de plugin '{plugin_type}' non trouvé"}), 404
        
        plugins = manager.list_plugins()
        return jsonify({
            "type": plugin_type,
            "count": len(plugins),
            "plugins": plugins
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@plugins_routes.route('/api/plugins/<plugin_type>/<plugin_name>', methods=['GET'])
@token_required
def get_plugin_info(current_user, plugin_type, plugin_name):
    """
    Récupère les informations détaillées d'un plugin spécifique.
    ---
    tags:
      - Plugins
    security:
      - Bearer: []
    parameters:
      - name: plugin_type
        in: path
        type: string
        required: true
        description: Type de plugin
      - name: plugin_name
        in: path
        type: string
        required: true
        description: Nom du plugin
    responses:
      200:
        description: Informations du plugin
      404:
        description: Plugin non trouvé
    """
    try:
        manager = plugin_registry.get_manager(plugin_type)
        if not manager:
            return jsonify({"error": f"Type de plugin '{plugin_type}' non trouvé"}), 404
        
        info = manager.get_plugin_info(plugin_name)
        if not info:
            return jsonify({"error": f"Plugin '{plugin_name}' non trouvé"}), 404
        
        return jsonify(info), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@plugins_routes.route('/api/plugins/reload', methods=['POST'])
@admin_required
def reload_all_plugins(current_user):
    """
    Recharge tous les plugins (admin uniquement).
    ---
    tags:
      - Plugins
    security:
      - Bearer: []
    responses:
      200:
        description: Plugins rechargés avec succès
      403:
        description: Accès refusé
    """
    try:
        plugin_registry.reload_all()
        counts = plugin_registry.get_plugin_count()
        return jsonify({
            "message": "Tous les plugins ont été rechargés",
            "counts": counts
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@plugins_routes.route('/api/plugins/<plugin_type>/reload', methods=['POST'])
@admin_required
def reload_plugins_by_type(current_user, plugin_type):
    """
    Recharge les plugins d'un type spécifique (admin uniquement).
    ---
    tags:
      - Plugins
    security:
      - Bearer: []
    parameters:
      - name: plugin_type
        in: path
        type: string
        required: true
        description: Type de plugin à recharger
    responses:
      200:
        description: Plugins rechargés avec succès
      403:
        description: Accès refusé
      404:
        description: Type de plugin non trouvé
    """
    try:
        manager = plugin_registry.get_manager(plugin_type)
        if not manager:
            return jsonify({"error": f"Type de plugin '{plugin_type}' non trouvé"}), 404
        
        manager.reload_plugins()
        count = len(manager.get_all_plugins())
        
        return jsonify({
            "message": f"Plugins de type '{plugin_type}' rechargés",
            "count": count
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@plugins_routes.route('/api/plugins/stats', methods=['GET'])
@token_required
def get_plugin_stats(current_user):
    """
    Récupère les statistiques des plugins.
    ---
    tags:
      - Plugins
    security:
      - Bearer: []
    responses:
      200:
        description: Statistiques des plugins
    """
    try:
        counts = plugin_registry.get_plugin_count()
        total = sum(counts.values())
        
        return jsonify({
            "total": total,
            "by_type": counts
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
