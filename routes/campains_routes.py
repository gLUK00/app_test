"""Routes API pour la gestion des campagnes."""
from flask import Blueprint, request, jsonify
from models.campain import Campain
from utils.auth import token_required
from utils.pagination import get_pagination_params, paginate_results
from utils.validation import validate_required_fields

campains_bp = Blueprint('campains_api', __name__, url_prefix='/api/campains')

@campains_bp.route('', methods=['GET'])
@token_required
def get_campains():
    """Récupère la liste des campagnes."""
    try:
        campains = Campain.get_all()
        page, page_size = get_pagination_params(request)
        result = paginate_results(campains, page, page_size)
        
        return jsonify(result), 200
    
    except Exception as e:
        return jsonify({'message': f'Erreur serveur: {str(e)}'}), 500

@campains_bp.route('', methods=['POST'])
@token_required
def create_campain():
    """Crée une nouvelle campagne."""
    try:
        data = request.get_json()
        
        # Validation
        is_valid, message = validate_required_fields(data, ['name'])
        if not is_valid:
            return jsonify({'message': message}), 400
        
        campain_id = Campain.create(
            user_created=request.user_id,
            name=data['name'],
            description=data.get('description', '')
        )
        
        return jsonify({
            'message': 'Campagne créée avec succès',
            'campain_id': campain_id
        }), 201
    
    except Exception as e:
        return jsonify({'message': f'Erreur serveur: {str(e)}'}), 500

@campains_bp.route('/<campain_id>', methods=['GET'])
@token_required
def get_campain(campain_id):
    """Récupère les détails d'une campagne spécifique."""
    try:
        campain = Campain.find_by_id(campain_id)
        
        if not campain:
            return jsonify({'message': 'Campagne non trouvée'}), 404
        
        return jsonify(campain), 200
    
    except Exception as e:
        return jsonify({'message': f'Erreur serveur: {str(e)}'}), 500

@campains_bp.route('/<campain_id>', methods=['PUT'])
@token_required
def update_campain(campain_id):
    """Met à jour une campagne existante."""
    try:
        data = request.get_json()
        
        Campain.update(campain_id, data)
        
        return jsonify({'message': 'Campagne mise à jour avec succès'}), 200
    
    except Exception as e:
        return jsonify({'message': f'Erreur serveur: {str(e)}'}), 500

@campains_bp.route('/<campain_id>', methods=['DELETE'])
@token_required
def delete_campain(campain_id):
    """Supprime une campagne."""
    try:
        success = Campain.delete(campain_id)
        
        if not success:
            return jsonify({'message': 'Campagne non trouvée'}), 404
        
        return jsonify({'message': 'Campagne supprimée avec succès'}), 200
    
    except Exception as e:
        return jsonify({'message': f'Erreur serveur: {str(e)}'}), 500
