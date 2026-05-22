"""Routes API pour la gestion des rapports."""
import os
from flask import Blueprint, request, jsonify, current_app, send_file
from flask_babel import gettext as _
from werkzeug.utils import secure_filename
from datetime import datetime
from models.rapport import Rapport
from models.campain import Campain
from models.test import Test
from models.variable import Variable
from utils.auth import token_required
from utils.pagination import get_pagination_params, paginate_results
from utils.validation import validate_required_fields
from plugins.reports import get_all_reports, get_report
from utils.workdir import get_campain_workdir

rapports_bp = Blueprint('rapports_api', __name__, url_prefix='/api/rapports')

@rapports_bp.route('/execute', methods=['POST'])
@token_required
def execute_campain():
    """Lance l'exécution d'une campagne."""
    try:
        # Récupérer l'exécuteur depuis l'app
        executor = current_app.config.get('CAMPAIN_EXECUTOR')
        if not executor:
            return jsonify({'message': 'Exécuteur de campagne non disponible'}), 500
        
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

@rapports_bp.route('/plugins', methods=['GET'])
@token_required
def get_report_plugins():
    """Récupère la liste des plugins de rapport disponibles."""
    try:
        plugins = get_all_reports()
        # On ne renvoie que les métadonnées et le schéma
        result = []
        for p_type, p_data in plugins.items():
            result.append({
                "type": p_type,
                "metadata": p_data["metadata"],
                "schema": p_data["configuration_schema"]
            })
        return jsonify(result), 200
    except Exception as e:
        return jsonify({'message': str(e)}), 500

@rapports_bp.route('/<rapport_id>/generate', methods=['POST'])
@token_required
def generate_report(rapport_id):
    """Génère un rapport pour une exécution donnée."""
    try:
        data = request.get_json()
        report_type = data.get('report_type')
        config = data.get('config', {})
        
        if not report_type:
            return jsonify({'message': _('Type de rapport manquant')}), 400
            
        # Récupérer le rapport d'exécution
        rapport = Rapport.find_by_id(rapport_id)
        if not rapport:
            return jsonify({'message': _('Rapport introuvable')}), 404
            
        # Récupérer le plugin
        plugin = get_report(report_type)
        if not plugin:
            return jsonify({'message': _('Plugin de rapport {} introuvable').format(report_type)}), 404
            
        # Valider la config
        is_valid, error_msg = plugin.validate_config(config)
        if not is_valid:
            return jsonify({'message': _('Configuration invalide: {}').format(error_msg)}), 400
            
        # Définir le chemin de sortie
        campain_id = rapport.get('campainId')
        workdir = get_campain_workdir(campain_id)
        reports_dir = os.path.join(workdir, 'reports')
        os.makedirs(reports_dir, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        ext = plugin.get_output_format()
        filename = f"report_{report_type}_{timestamp}.{ext}"
        output_path = os.path.join(reports_dir, filename)
        
        config['output_path'] = output_path
        
        # Générer
        result = plugin.generate(rapport, config)
        
        if result.get('success'):
            return jsonify({
                'message': _('Rapport généré avec succès'),
                'file_path': result.get('file_path'),
                'download_url': f"/api/rapports/download/{campain_id}/{filename}"
            }), 200
        else:
            return jsonify({'message': _('Erreur lors de la génération: {}').format(result.get('message'))}), 500
            
    except Exception as e:
        current_app.logger.error(f"Erreur génération rapport: {str(e)}")
        return jsonify({'message': str(e)}), 500

@rapports_bp.route('/download/<campain_id>/<filename>', methods=['GET'])
@token_required
def download_report(campain_id, filename):
    """Télécharge un rapport généré."""
    try:
        # Vérifier que la campagne existe (optionnel mais recommandé)
        # campain = Campain.find_by_id(campain_id)
        
        workdir = get_campain_workdir(campain_id)
        reports_dir = os.path.join(workdir, 'reports')
        file_path = os.path.join(reports_dir, secure_filename(filename))
        
        if not os.path.exists(file_path) or not os.path.isfile(file_path):
            return jsonify({'message': _('Fichier non trouvé')}), 404
            
        return send_file(
            file_path,
            as_attachment=True,
            download_name=filename
        )
    except Exception as e:
        return jsonify({'message': str(e)}), 500


# ==========================================================================
# Routes de tests de performance
# ==========================================================================

@rapports_bp.route('/performance/generate-name', methods=['GET'])
@token_required
def generate_perf_rapport_name():
    """Génère un nom unique pour un rapport de performance."""
    try:
        now = datetime.now()
        months_fr = ['Janvier', 'Février', 'Mars', 'Avril', 'Mai', 'Juin',
                     'Juillet', 'Août', 'Septembre', 'Octobre', 'Novembre', 'Décembre']
        base_name = f"Perf - {months_fr[now.month - 1]} {now.year}"

        name = base_name
        counter = 1
        while Rapport.get_by_name(name):
            name = f"{base_name} ({counter})"
            counter += 1

        return jsonify({'name': name}), 200

    except Exception as e:
        return jsonify({'message': f'Erreur serveur: {str(e)}'}), 500


@rapports_bp.route('/performance/execute', methods=['POST'])
@token_required
def execute_performance():
    """Lance un test de performance."""
    try:
        executor = current_app.config.get('PERFORMANCE_EXECUTOR')
        if not executor:
            return jsonify({'message': _('Exécuteur de performance non disponible')}), 500

        data = request.get_json()

        # Validation des champs obligatoires
        is_valid, message = validate_required_fields(data, ['campain_id', 'filiere', 'tests_config'])
        if not is_valid:
            return jsonify({'message': message}), 400

        campain_id = data['campain_id']
        filiere = data['filiere']
        tests_config = data['tests_config']

        if not isinstance(tests_config, list) or len(tests_config) == 0:
            return jsonify({'message': _('La configuration des tests est invalide ou vide')}), 400

        # Vérifier que la campagne existe
        campain = Campain.find_by_id(campain_id)
        if not campain:
            return jsonify({'message': _('Campagne non trouvée')}), 404

        # Valider et normaliser les configs de test
        normalized_tests = []
        for tc in tests_config:
            test_id = tc.get('test_id')
            if not test_id:
                continue
            test = Test.find_by_id(test_id)
            if not test:
                return jsonify({'message': _('Test introuvable: {}').format(test_id)}), 404

            instances = max(1, int(tc.get('instances', 1)))
            parallel = bool(tc.get('parallel', False)) and instances > 1
            parallel_count = max(1, int(tc.get('parallel_count', 2))) if parallel else 1
            stop_on_instance_failure = bool(tc.get('stop_on_instance_failure', False))

            normalized_tests.append({
                'test_id': test_id,
                'instances': instances,
                'parallel': parallel,
                'parallel_count': parallel_count,
                'stop_on_instance_failure': stop_on_instance_failure
            })

        if not normalized_tests:
            return jsonify({'message': _('Aucun test valide sélectionné')}), 400

        tests_parallel = bool(data.get('tests_parallel', False))
        tests_parallel_count = max(1, int(data.get('tests_parallel_count', 2)))

        perf_config = {
            'tests': normalized_tests,
            'tests_parallel': tests_parallel,
            'tests_parallel_count': tests_parallel_count
        }

        # Générer le nom du rapport
        now = datetime.now()
        months_fr = ['Janvier', 'Février', 'Mars', 'Avril', 'Mai', 'Juin',
                     'Juillet', 'Août', 'Septembre', 'Octobre', 'Novembre', 'Décembre']
        base_name = f"Perf - {months_fr[now.month - 1]} {now.year}"
        name = base_name
        counter = 1
        while Rapport.get_by_name(name):
            name = f"{base_name} ({counter})"
            counter += 1

        # Créer le rapport en base
        rapport_id = Rapport.create_performance(
            campain_id=campain_id,
            details=name,
            filiere=filiere,
            perf_config=perf_config,
            status='pending'
        )

        # Lancer l'exécution en arrière-plan
        executor.execute_performance(rapport_id, campain_id, filiere, perf_config)

        return jsonify({
            'message': _('Test de performance lancé'),
            'rapport_id': rapport_id
        }), 201

    except Exception as e:
        return jsonify({'message': f'Erreur serveur: {str(e)}'}), 500
