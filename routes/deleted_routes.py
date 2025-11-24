"""Routes pour la gestion des éléments supprimés logiquement."""
from flask import Blueprint, jsonify, request
from models.test import Test
from models.campain import Campain
from models.rapport import Rapport
from utils.auth import token_required, admin_required

deleted_bp = Blueprint('deleted', __name__)

@deleted_bp.route('/api/deleted/tests', methods=['GET'])
@token_required
@admin_required
def get_deleted_tests():
    """Récupère tous les tests supprimés logiquement."""
    try:
        tests = Test.get_deleted()
        return jsonify({'tests': tests}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@deleted_bp.route('/api/deleted/campains', methods=['GET'])
@token_required
@admin_required
def get_deleted_campains():
    """Récupère toutes les campagnes supprimées logiquement."""
    try:
        campains = Campain.get_deleted()
        return jsonify({'campains': campains}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@deleted_bp.route('/api/deleted/rapports', methods=['GET'])
@token_required
@admin_required
def get_deleted_rapports():
    """Récupère tous les rapports supprimés logiquement."""
    try:
        rapports = Rapport.get_deleted()
        return jsonify({'rapports': rapports}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@deleted_bp.route('/api/deleted/all', methods=['GET'])
@token_required
@admin_required
def get_all_deleted():
    """Récupère tous les éléments supprimés logiquement (tests, campagnes, rapports)."""
    try:
        tests = Test.get_deleted()
        campains = Campain.get_deleted()
        rapports = Rapport.get_deleted()
        
        return jsonify({
            'tests': tests,
            'campains': campains,
            'rapports': rapports
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@deleted_bp.route('/api/deleted/restore', methods=['POST'])
@token_required
@admin_required
def restore_items():
    """Restaure un ou plusieurs éléments supprimés logiquement."""
    try:
        data = request.get_json()
        
        if not data or 'items' not in data:
            return jsonify({'error': 'Items requis'}), 400
        
        items = data['items']  # Format: [{'type': 'test', 'id': '...'}, ...]
        restored = []
        errors = []
        
        for item in items:
            item_type = item.get('type')
            item_id = item.get('id')
            
            if not item_type or not item_id:
                errors.append({'item': item, 'error': 'Type et ID requis'})
                continue
            
            try:
                if item_type == 'test':
                    success = Test.restore(item_id)
                elif item_type == 'campain':
                    success = Campain.restore(item_id)
                elif item_type == 'rapport':
                    success = Rapport.restore(item_id)
                else:
                    errors.append({'item': item, 'error': 'Type invalide'})
                    continue
                
                if success:
                    restored.append(item)
                else:
                    errors.append({'item': item, 'error': 'Échec de la restauration'})
            except Exception as e:
                errors.append({'item': item, 'error': str(e)})
        
        return jsonify({
            'restored': restored,
            'errors': errors,
            'success': len(errors) == 0
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@deleted_bp.route('/api/deleted/permanent', methods=['DELETE'])
@token_required
@admin_required
def permanent_delete_items():
    """Supprime définitivement (physiquement) un ou plusieurs éléments."""
    try:
        data = request.get_json()
        
        if not data or 'items' not in data:
            return jsonify({'error': 'Items requis'}), 400
        
        items = data['items']  # Format: [{'type': 'test', 'id': '...'}, ...]
        deleted = []
        errors = []
        
        for item in items:
            item_type = item.get('type')
            item_id = item.get('id')
            
            if not item_type or not item_id:
                errors.append({'item': item, 'error': 'Type et ID requis'})
                continue
            
            try:
                if item_type == 'test':
                    success = Test.permanent_delete(item_id)
                elif item_type == 'campain':
                    success = Campain.permanent_delete(item_id)
                elif item_type == 'rapport':
                    success = Rapport.permanent_delete(item_id)
                else:
                    errors.append({'item': item, 'error': 'Type invalide'})
                    continue
                
                if success:
                    deleted.append(item)
                else:
                    errors.append({'item': item, 'error': 'Échec de la suppression'})
            except Exception as e:
                errors.append({'item': item, 'error': str(e)})
        
        return jsonify({
            'deleted': deleted,
            'errors': errors,
            'success': len(errors) == 0
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
