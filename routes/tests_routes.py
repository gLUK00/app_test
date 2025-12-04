"""Routes API pour la gestion des tests."""
from flask import Blueprint, request, jsonify, current_app
from flask_babel import _
from models.test import Test
from models.variable import Variable
from utils.auth import token_required
from utils.pagination import get_pagination_params, paginate_results
from utils.validation import validate_required_fields

tests_bp = Blueprint('tests_api', __name__, url_prefix='/api/tests')

@tests_bp.route('', methods=['GET'])
@token_required
def get_tests():
    """Récupère la liste des tests."""
    try:
        campain_id = request.args.get('campain_id')
        
        if campain_id:
            tests = Test.get_by_campain(campain_id)
            result = {
                'data': tests,
                'pagination': {
                    'page': 1,
                    'page_size': len(tests),
                    'total': len(tests),
                    'total_pages': 1
                }
            }
        else:
            tests = Test.get_all()
            page, page_size = get_pagination_params(request)
            result = paginate_results(tests, page, page_size)
        
        return jsonify(result), 200
    
    except Exception as e:
        return jsonify({'message': _('Erreur serveur: %(error)s', error=str(e))}), 500

@tests_bp.route('', methods=['POST'])
@token_required
def create_test():
    """Crée un nouveau test."""
    try:
        data = request.get_json()
        
        # Validation
        is_valid, message = validate_required_fields(data, ['campain_id', 'actions'])
        if not is_valid:
            return jsonify({'message': message}), 400
        
        test_id = Test.create(
            campain_id=data['campain_id'],
            user_id=request.user_id,
            actions=data['actions'],
            name=data.get('name'),
            description=data.get('description'),
            variables=data.get('variables', [])
        )
        
        return jsonify({
            'message': _('Test créé avec succès'),
            'test_id': test_id
        }), 201
    
    except Exception as e:
        return jsonify({'message': _('Erreur serveur: %(error)s', error=str(e))}), 500

@tests_bp.route('/<test_id>', methods=['GET'])
@token_required
def get_test(test_id):
    """Récupère les détails d'un test spécifique."""
    try:
        test = Test.find_by_id(test_id)
        
        if not test:
            return jsonify({'message': _('Test non trouvé')}), 404
        
        return jsonify(test), 200
    
    except Exception as e:
        return jsonify({'message': _('Erreur serveur: %(error)s', error=str(e))}), 500

@tests_bp.route('/<test_id>', methods=['PUT'])
@token_required
def update_test(test_id):
    """Met à jour un test existant."""
    try:
        data = request.get_json()
        
        print(f"[DEBUG] Mise à jour du test {test_id}")
        print(f"[DEBUG] Données reçues: {data}")
        if 'actions' in data:
            print(f"[DEBUG] Nombre d'actions: {len(data['actions'])}")
            for i, action in enumerate(data['actions']):
                print(f"[DEBUG] Action {i}: {action}")
        
        Test.update(test_id, data)
        
        return jsonify({'message': _('Test mis à jour avec succès')}), 200
    
    except Exception as e:
        print(f"[ERROR] Erreur lors de la mise à jour: {str(e)}")
        return jsonify({'message': _('Erreur serveur: %(error)s', error=str(e))}), 500

@tests_bp.route('/<test_id>', methods=['DELETE'])
@token_required
def delete_test(test_id):
    """Supprime un test."""
    try:
        success = Test.delete(test_id)
        
        if not success:
            return jsonify({'message': _('Test non trouvé')}), 404
        
        return jsonify({'message': _('Test supprimé avec succès')}), 200
    
    except Exception as e:
        return jsonify({'message': _('Erreur serveur: %(error)s', error=str(e))}), 500

@tests_bp.route('/<test_id>/actions', methods=['POST'])
@token_required
def add_action(test_id):
    """Ajoute une action à un test."""
    try:
        data = request.get_json()
        
        # Validation
        is_valid, message = validate_required_fields(data, ['type', 'value'])
        if not is_valid:
            return jsonify({'message': message}), 400
        
        Test.add_action(test_id, data)
        
        return jsonify({'message': _('Action ajoutée avec succès')}), 200
    
    except Exception as e:
        return jsonify({'message': _('Erreur serveur: %(error)s', error=str(e))}), 500

@tests_bp.route('/filieres', methods=['GET'])
@token_required
def get_filieres():
    """Récupère la liste des filières disponibles."""
    try:
        filieres = Variable.get_all_filieres()
        return jsonify(filieres), 200
    
    except Exception as e:
        return jsonify({'message': _('Erreur serveur: %(error)s', error=str(e))}), 500

@tests_bp.route('/<test_id>/execute', methods=['POST'])
@token_required
def execute_test(test_id):
    """Lance l'exécution d'un test individuel."""
    try:
        data = request.get_json()
        
        # Validation
        is_valid, message = validate_required_fields(data, ['filiere'])
        if not is_valid:
            return jsonify({'message': message}), 400
        
        filiere = data['filiere']
        
        # Vérifier que le test existe
        test = Test.find_by_id(test_id)
        if not test:
            return jsonify({'message': _('Test non trouvé')}), 404
        
        # Récupérer le test_executor depuis l'app
        test_executor = current_app.config.get('TEST_EXECUTOR')
        if not test_executor:
            return jsonify({'message': _('Exécuteur de test non disponible')}), 500
        
        # Lancer l'exécution
        test_executor.execute_test(test_id, filiere)
        
        return jsonify({
            'message': _('Exécution du test lancée'),
            'test_id': test_id
        }), 200
    
    except Exception as e:
        return jsonify({'message': _('Erreur serveur: %(error)s', error=str(e))}), 500

@tests_bp.route('/<test_id>/move-up', methods=['POST'])
@token_required
def move_test_up(test_id):
    """Déplace un test vers le haut dans l'ordre d'exécution."""
    try:
        success = Test.move_up(test_id)
        
        if not success:
            return jsonify({'message': _('Impossible de déplacer le test (déjà en première position ou test introuvable)')}), 400
        
        return jsonify({'message': _('Test déplacé vers le haut avec succès')}), 200
    
    except Exception as e:
        return jsonify({'message': _('Erreur serveur: %(error)s', error=str(e))}), 500

@tests_bp.route('/<test_id>/move-down', methods=['POST'])
@token_required
def move_test_down(test_id):
    """Déplace un test vers le bas dans l'ordre d'exécution."""
    try:
        success = Test.move_down(test_id)
        
        if not success:
            return jsonify({'message': _('Impossible de déplacer le test (déjà en dernière position ou test introuvable)')}), 400
        
        return jsonify({'message': _('Test déplacé vers le bas avec succès')}), 200
    
    except Exception as e:
        return jsonify({'message': _('Erreur serveur: %(error)s', error=str(e))}), 500
