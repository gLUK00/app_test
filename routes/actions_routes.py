# -*- coding: utf-8 -*-
"""Routes API pour la gestion des masques de saisie des actions."""
from flask import Blueprint, jsonify
from plugins.actions import get_action, get_all_actions, ACTION_REGISTRY

actions_bp = Blueprint('actions_api', __name__, url_prefix='/api/actions')

@actions_bp.route('/masks', methods=['GET'])
def get_all_masks():
    """Récupère tous les masques de saisie pour tous les types d'actions."""
    try:
        # Utiliser le nouveau système de plugins
        actions = get_all_actions()
        masks = {}
        
        for action_type, action_info in actions.items():
            masks[action_type] = action_info['mask']
        
        return jsonify(masks), 200
    except Exception as e:
        return jsonify({'message': f'Erreur serveur: {str(e)}'}), 500

@actions_bp.route('/masks/<action_type>', methods=['GET'])
def get_mask(action_type):
    """Récupère le masque de saisie pour un type d'action spécifique."""
    try:
        # Utiliser le nouveau système de plugins
        action = get_action(action_type)
        
        if not action:
            return jsonify({'message': f'Type d\'action non supporté: {action_type}'}), 400
        
        mask = action.get_input_mask()
        
        return jsonify({'type': action_type, 'mask': mask}), 200
    except Exception as e:
        return jsonify({'message': f'Erreur serveur: {str(e)}'}), 500

@actions_bp.route('/output-variables', methods=['GET'])
def get_all_output_variables():
    """Récupère toutes les variables de sortie pour tous les types d'actions."""
    try:
        actions = get_all_actions()
        output_variables = {}
        
        for action_type, action_info in actions.items():
            action_instance = get_action(action_type)
            if action_instance:
                output_variables[action_type] = action_instance.get_output_variables()
        
        return jsonify(output_variables), 200
    except Exception as e:
        return jsonify({'message': f'Erreur serveur: {str(e)}'}), 500

@actions_bp.route('/output-variables/<action_type>', methods=['GET'])
def get_output_variables(action_type):
    """Récupère les variables de sortie pour un type d'action spécifique."""
    try:
        action = get_action(action_type)
        
        if not action:
            return jsonify({'message': f'Type d\'action non supporté: {action_type}'}), 400
        
        output_vars = action.get_output_variables()
        
        return jsonify({'type': action_type, 'output_variables': output_vars}), 200
    except Exception as e:
        return jsonify({'message': f'Erreur serveur: {str(e)}'}), 500

@actions_bp.route('/labels', methods=['GET'])
def get_all_labels():
    """Récupère tous les labels d'affichage pour tous les types d'actions."""
    try:
        actions = get_all_actions()
        labels = {}
        
        for action_type, action_info in actions.items():
            action_instance = get_action(action_type)
            if action_instance:
                # Utiliser le label de la classe ou générer un label par défaut
                if hasattr(action_instance, 'label') and action_instance.label:
                    labels[action_type] = action_instance.label
                else:
                    # Fallback: capitaliser le type d'action
                    labels[action_type] = action_type.replace('_', ' ').replace('-', ' ').title()
        
        return jsonify(labels), 200
    except Exception as e:
        return jsonify({'message': f'Erreur serveur: {str(e)}'}), 500
