"""Routes API pour la gestion des rapports."""
from flask import Blueprint, request, jsonify
from datetime import datetime
from models.rapport import Rapport
from models.campain import Campain
from models.test import Test
from models.variable import Variable
from utils.auth import token_required
from utils.pagination import get_pagination_params, paginate_results
from utils.validation import validate_required_fields
from utils.campain_executor import CampainExecutor

rapports_bp = Blueprint('rapports_api', __name__, url_prefix='/api/rapports')

# Instance de l'exécuteur de campagne
executor = None

def get_socketio():
    """Récupère l'instance SocketIO depuis l'application Flask."""
    from flask import current_app
    return current_app.extensions.get('socketio')

def init_executor():
    """Initialise l'exécuteur de campagne."""
    global executor
    socketio = get_socketio()
    if executor is None and socketio:
        executor = CampainExecutor(socketio)

@rapports_bp.route('/execute', methods=['POST'])
@token_required
def execute_campain():
    """Lance l'exécution d'une campagne."""
    try:
        init_executor()
        
        data = request.get_json()
        
        # Validation
        is_valid, message = validate_required_fields(data, ['campain_id', 'name', 'filiere'])
        if not is_valid:
            return jsonify({'message': message}), 400
        
        campain_id = data['campain_id']
        rapport_name = data['name']
        filiere = data['filiere']
        stop_on_failure = data.get('stop_on_failure', False)
        
        # Vérifier l'unicité du nom
        existing = Rapport.get_by_name(rapport_name)
        if existing:
            return jsonify({'message': 'Un rapport avec ce nom existe déjà'}), 400
        
        # Récupérer les tests de la campagne
        tests = Test.get_by_campain(campain_id)
        if not tests:
            return jsonify({'message': 'Aucun test dans cette campagne'}), 400
        
        test_ids = [test['_id'] for test in tests]
        
        # Créer le rapport initial
        rapport_id = Rapport.create(
            campain_id=campain_id,
            result='pending',
            details=rapport_name,
            filiere=filiere,
            tests=[],
            status='pending',
            progress=0,
            stop_on_failure=stop_on_failure
        )
        
        # Lancer l'exécution en arrière-plan
        executor.execute_campain(rapport_id, campain_id, filiere, test_ids, stop_on_failure)
        
        return jsonify({
            'message': 'Exécution de la campagne lancée',
            'rapport_id': rapport_id
        }), 201
    
    except Exception as e:
        return jsonify({'message': f'Erreur serveur: {str(e)}'}), 500

@rapports_bp.route('/generate-name', methods=['GET'])
@token_required
def generate_rapport_name():
    """Génère un nom unique pour un rapport."""
    try:
        # Générer le nom de base (Mois Année)
        now = datetime.now()
        months_fr = ['Janvier', 'Février', 'Mars', 'Avril', 'Mai', 'Juin',
                     'Juillet', 'Août', 'Septembre', 'Octobre', 'Novembre', 'Décembre']
        base_name = f"{months_fr[now.month - 1]} {now.year}"
        
        # Vérifier l'unicité et ajouter un suffixe si nécessaire
        name = base_name
        counter = 1
        while Rapport.get_by_name(name):
            name = f"{base_name} ({counter})"
            counter += 1
        
        return jsonify({'name': name}), 200
    
    except Exception as e:
        return jsonify({'message': f'Erreur serveur: {str(e)}'}), 500

@rapports_bp.route('/filieres', methods=['GET'])
@token_required
def get_filieres():
    """Récupère la liste des filières disponibles."""
    try:
        filieres = Variable.get_all_filieres()
        return jsonify({'filieres': filieres}), 200
    
    except Exception as e:
        return jsonify({'message': f'Erreur serveur: {str(e)}'}), 500

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
