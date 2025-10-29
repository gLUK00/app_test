"""Routes API pour la gestion des variables."""
from flask import Blueprint, request, jsonify
from models.variable import Variable
from utils.auth import token_required, admin_required
from utils.pagination import get_pagination_params, paginate_results
from utils.validation import validate_required_fields

variables_bp = Blueprint('variables_api', __name__, url_prefix='/api/variables')

@variables_bp.route('', methods=['GET'])
@token_required
def get_variables():
    """Récupère la liste des variables."""
    try:
        # Vérifier si on veut grouper par filière
        grouped = request.args.get('grouped', 'false').lower() == 'true'
        filiere = request.args.get('filiere')
        is_root = request.args.get('isRoot', '').lower()
        
        if grouped:
            variables = Variable.get_grouped_by_filiere()
            return jsonify(variables), 200
        elif filiere:
            variables = Variable.get_by_filiere(filiere)
        else:
            variables = Variable.get_all()
        
        # Filtrer par isRoot si spécifié
        if is_root == 'true':
            variables = [v for v in variables if v.get('isRoot') is True]
        elif is_root == 'false':
            variables = [v for v in variables if v.get('isRoot') is not True]
        
        page, page_size = get_pagination_params(request)
        result = paginate_results(variables, page, page_size)
        
        return jsonify(result), 200
    
    except Exception as e:
        return jsonify({'message': f'Erreur serveur: {str(e)}'}), 500

@variables_bp.route('', methods=['POST'])
@token_required
@admin_required
def create_variable():
    """Crée une nouvelle variable (admin uniquement)."""
    try:
        data = request.get_json()
        
        # Validation
        is_valid, message = validate_required_fields(data, ['key'])        
        if is_valid and not data.get('isRoot', False):
            is_valid, message = validate_required_fields(data, ['value', 'filiere'])
        if not is_valid:
            return jsonify({'message': message}), 400
        
        # Vérifier que la variable racine existe si ce n'est pas une variable root
        if not data.get('isRoot', False):
            root_variable = Variable.find_by_key_and_root(data['key'], is_root=True)
            if not root_variable:
                return jsonify({'message': f'La variable racine {data["key"]} doit être préalablement créée'}), 400
        
        variable_id = Variable.create(
            key=data['key'],
            value=data.get('value', ''),
            filiere=data.get('filiere', ''),
            description=data.get('description', ''),
            is_root=data.get('isRoot', False)
        )
        
        return jsonify({
            'message': 'Variable créée avec succès',
            'variable_id': variable_id
        }), 201
    
    except ValueError as e:
        return jsonify({'message': str(e)}), 400
    
    except Exception as e:
        return jsonify({'message': f'Erreur serveur: {str(e)}'}), 500

@variables_bp.route('/<variable_id>', methods=['GET'])
@token_required
@admin_required
def get_variable(variable_id):
    """Récupère les détails d'une variable spécifique."""
    try:
        variable = Variable.find_by_id(variable_id)
        
        if not variable:
            return jsonify({'message': 'Variable non trouvée'}), 404
        
        return jsonify(variable), 200
    
    except Exception as e:
        return jsonify({'message': f'Erreur serveur: {str(e)}'}), 500

@variables_bp.route('/<variable_id>', methods=['PUT'])
@token_required
@admin_required
def update_variable(variable_id):
    """Met à jour une variable existante (admin uniquement)."""
    try:
        data = request.get_json()
        
        # Validation
        is_valid, message = validate_required_fields(data, ['key'])        
        if is_valid and not data.get('isRoot', False):
            is_valid, message = validate_required_fields(data, ['value', 'filiere'])
        if not is_valid:
            return jsonify({'message': message}), 400
        
        # Vérifier que la variable racine existe si ce n'est pas une variable root
        if not data.get('isRoot', False):
            root_variable = Variable.find_by_key_and_root(data['key'], is_root=True)
            if not root_variable:
                return jsonify({'message': f'La variable racine {data["key"]} doit être préalablement créée'}), 400
        
        Variable.update(variable_id, data)
        
        return jsonify({'message': 'Variable mise à jour avec succès'}), 200
    
    except Exception as e:
        return jsonify({'message': f'Erreur serveur: {str(e)}'}), 500

@variables_bp.route('/<variable_id>', methods=['DELETE'])
@token_required
@admin_required
def delete_variable(variable_id):
    """Supprime une variable (admin uniquement)."""
    try:
        success = Variable.delete(variable_id)
        
        if not success:
            return jsonify({'message': 'Variable non trouvée'}), 404
        
        return jsonify({'message': 'Variable supprimée avec succès'}), 200
    
    except Exception as e:
        return jsonify({'message': f'Erreur serveur: {str(e)}'}), 500
