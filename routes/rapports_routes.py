"""Routes API pour la gestion des rapports."""
from flask import Blueprint, request, jsonify
from models.rapport import Rapport
from utils.auth import token_required
from utils.pagination import get_pagination_params, paginate_results
from utils.validation import validate_required_fields

rapports_bp = Blueprint('rapports_api', __name__, url_prefix='/api/rapports')

@rapports_bp.route('', methods=['GET'])
@token_required
def get_rapports():
    """Récupère la liste des rapports."""
    try:
        campain_id = request.args.get('campain_id')
        
        if campain_id:
            rapports = Rapport.get_by_campain(campain_id)
        else:
            rapports = Rapport.get_all()
        
        page, page_size = get_pagination_params(request)
        result = paginate_results(rapports, page, page_size)
        
        return jsonify(result), 200
    
    except Exception as e:
        return jsonify({'message': f'Erreur serveur: {str(e)}'}), 500

@rapports_bp.route('', methods=['POST'])
@token_required
def create_rapport():
    """Crée un nouveau rapport."""
    try:
        data = request.get_json()
        
        # Validation
        is_valid, message = validate_required_fields(data, ['campain_id', 'result', 'filiere', 'tests'])
        if not is_valid:
            return jsonify({'message': message}), 400
        
        rapport_id = Rapport.create(
            campain_id=data['campain_id'],
            result=data['result'],
            details=data.get('details', ''),
            filiere=data['filiere'],
            tests=data['tests']
        )
        
        return jsonify({
            'message': 'Rapport créé avec succès',
            'rapport_id': rapport_id
        }), 201
    
    except Exception as e:
        return jsonify({'message': f'Erreur serveur: {str(e)}'}), 500

@rapports_bp.route('/<rapport_id>', methods=['GET'])
@token_required
def get_rapport(rapport_id):
    """Récupère les détails d'un rapport spécifique."""
    try:
        rapport = Rapport.find_by_id(rapport_id)
        
        if not rapport:
            return jsonify({'message': 'Rapport non trouvé'}), 404
        
        return jsonify(rapport), 200
    
    except Exception as e:
        return jsonify({'message': f'Erreur serveur: {str(e)}'}), 500

@rapports_bp.route('/<rapport_id>', methods=['PUT'])
@token_required
def update_rapport(rapport_id):
    """Met à jour un rapport existant."""
    try:
        data = request.get_json()
        
        Rapport.update(rapport_id, data)
        
        return jsonify({'message': 'Rapport mis à jour avec succès'}), 200
    
    except Exception as e:
        return jsonify({'message': f'Erreur serveur: {str(e)}'}), 500

@rapports_bp.route('/<rapport_id>', methods=['DELETE'])
@token_required
def delete_rapport(rapport_id):
    """Supprime un rapport."""
    try:
        success = Rapport.delete(rapport_id)
        
        if not success:
            return jsonify({'message': 'Rapport non trouvé'}), 404
        
        return jsonify({'message': 'Rapport supprimé avec succès'}), 200
    
    except Exception as e:
        return jsonify({'message': f'Erreur serveur: {str(e)}'}), 500
