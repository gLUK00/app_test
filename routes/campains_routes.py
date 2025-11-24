"""Routes API pour la gestion des campagnes."""
from flask import Blueprint, request, jsonify, send_file, current_app
from werkzeug.utils import secure_filename
from models.campain import Campain
from utils.auth import token_required
from utils.pagination import get_pagination_params, paginate_results
from utils.validation import validate_required_fields
from utils.workdir import create_campain_workdir, delete_campain_workdir, get_campain_workdir
from pathlib import Path
import os
from datetime import datetime
import json
import base64
from io import BytesIO
from models.test import Test

campains_bp = Blueprint('campains_api', __name__, url_prefix='/api/campains')


def emit_files_updated(campain_id):
    """Émet un événement WebSocket pour indiquer que les fichiers ont été mis à jour."""
    try:
        socketio = current_app.extensions.get('socketio')
        if socketio:
            socketio.emit('files_updated', {'campain_id': campain_id}, room=f'campain_{campain_id}')
    except Exception as e:
        print(f"Erreur lors de l'émission de l'événement files_updated: {e}")


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
        
        # Créer le répertoire de travail pour la campagne
        try:
            create_campain_workdir(campain_id)
        except Exception as e:
            print(f"Avertissement: Impossible de créer le répertoire de travail: {e}")
        
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

@campains_bp.route('/<campain_id>/rename', methods=['PUT'])
@token_required
def rename_campain(campain_id):
    """Renomme une campagne existante."""
    try:
        data = request.get_json()
        new_name = data.get('name')
        
        if not new_name or not new_name.strip():
            return jsonify({'message': 'Le nom de la campagne ne peut pas être vide'}), 400
            
        new_name = new_name.strip()
        
        # Vérifier si la campagne existe
        campain = Campain.find_by_id(campain_id)
        if not campain:
            return jsonify({'message': 'Campagne non trouvée'}), 404
            
        # Vérifier si le nom est déjà utilisé par une autre campagne
        existing_campain = Campain.find_by_name(new_name)
        if existing_campain and str(existing_campain['_id']) != campain_id:
            return jsonify({'message': 'Une campagne avec ce nom existe déjà'}), 409
            
        Campain.update(campain_id, {'name': new_name})
        
        return jsonify({'message': 'Campagne renommée avec succès', 'name': new_name}), 200
    
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
        
        # Supprimer le répertoire de travail de la campagne
        try:
            delete_campain_workdir(campain_id)
        except Exception as e:
            print(f"Avertissement: Impossible de supprimer le répertoire de travail: {e}")
        
        return jsonify({'message': 'Campagne supprimée avec succès'}), 200
    
    except Exception as e:
        return jsonify({'message': f'Erreur serveur: {str(e)}'}), 500


@campains_bp.route('/<campain_id>/files', methods=['GET'])
@token_required
def list_files(campain_id):
    """Liste les fichiers du répertoire de travail de la campagne."""
    try:
        # Vérifier que la campagne existe
        campain = Campain.find_by_id(campain_id)
        if not campain:
            return jsonify({'message': 'Campagne non trouvée'}), 404
        
        # Récupérer le répertoire files de la campagne
        campain_dir = Path(get_campain_workdir(campain_id)) / "files"
        
        if not campain_dir.exists():
            return jsonify({'files': []}), 200
        
        files = []
        for file_path in campain_dir.iterdir():
            if file_path.is_file():
                stat = file_path.stat()
                files.append({
                    'name': file_path.name,
                    'size': round(stat.st_size / 1024, 2),  # Taille en Ko
                    'modified': datetime.fromtimestamp(stat.st_mtime).isoformat()
                })
        
        # Trier par nom
        files.sort(key=lambda x: x['name'])
        
        return jsonify({'files': files}), 200
    
    except Exception as e:
        return jsonify({'message': f'Erreur serveur: {str(e)}'}), 500


@campains_bp.route('/<campain_id>/files', methods=['POST'])
@token_required
def upload_file(campain_id):
    """Upload un fichier dans le répertoire de travail de la campagne."""
    try:
        # Vérifier que la campagne existe
        campain = Campain.find_by_id(campain_id)
        if not campain:
            return jsonify({'message': 'Campagne non trouvée'}), 404
        
        # Vérifier qu'un fichier est présent dans la requête
        if 'file' not in request.files:
            return jsonify({'message': 'Aucun fichier fourni'}), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({'message': 'Nom de fichier vide'}), 400
        
        # Récupérer le nom personnalisé si fourni
        custom_name = request.form.get('customName', '').strip()
        
        # Utiliser le nom personnalisé ou le nom original
        if custom_name:
            filename = secure_filename(custom_name)
        else:
            filename = secure_filename(file.filename)
        
        # Récupérer le répertoire files de la campagne
        campain_dir = Path(get_campain_workdir(campain_id)) / "files"
        campain_dir.mkdir(parents=True, exist_ok=True)
        
        # Sauvegarder le fichier
        file_path = campain_dir / filename
        file.save(str(file_path))
        
        # Retourner les informations du fichier uploadé
        stat = file_path.stat()
        file_info = {
            'name': filename,
            'size': round(stat.st_size / 1024, 2),
            'modified': datetime.fromtimestamp(stat.st_mtime).isoformat()
        }
        
        # Émettre un événement WebSocket
        emit_files_updated(campain_id)
        
        return jsonify({
            'message': 'Fichier uploadé avec succès',
            'file': file_info
        }), 201
    
    except Exception as e:
        return jsonify({'message': f'Erreur serveur: {str(e)}'}), 500


@campains_bp.route('/<campain_id>/files/<filename>', methods=['GET'])
@token_required
def download_file(campain_id, filename):
    """Télécharge un fichier du répertoire de travail de la campagne."""
    try:
        # Vérifier que la campagne existe
        campain = Campain.find_by_id(campain_id)
        if not campain:
            return jsonify({'message': 'Campagne non trouvée'}), 404
        
        # Récupérer le chemin du fichier
        campain_dir = Path(get_campain_workdir(campain_id)) / "files"
        file_path = campain_dir / secure_filename(filename)
        
        if not file_path.exists() or not file_path.is_file():
            return jsonify({'message': 'Fichier non trouvé'}), 404
        
        return send_file(
            str(file_path),
            as_attachment=True,
            download_name=filename
        )
    
    except Exception as e:
        return jsonify({'message': f'Erreur serveur: {str(e)}'}), 500


@campains_bp.route('/<campain_id>/files/<filename>', methods=['DELETE'])
@token_required
def delete_file(campain_id, filename):
    """Supprime un fichier du répertoire de travail de la campagne."""
    try:
        # Vérifier que la campagne existe
        campain = Campain.find_by_id(campain_id)
        if not campain:
            return jsonify({'message': 'Campagne non trouvée'}), 404
        
        # Récupérer le chemin du fichier
        campain_dir = Path(get_campain_workdir(campain_id)) / "files"
        file_path = campain_dir / secure_filename(filename)
        
        if not file_path.exists() or not file_path.is_file():
            return jsonify({'message': 'Fichier non trouvé'}), 404
        
        # Supprimer le fichier
        os.remove(str(file_path))
        
        # Émettre un événement WebSocket
        emit_files_updated(campain_id)
        
        return jsonify({'message': 'Fichier supprimé avec succès'}), 200
    
    except Exception as e:
        return jsonify({'message': f'Erreur serveur: {str(e)}'}), 500

@campains_bp.route('/<campain_id>/export', methods=['GET'])
@token_required
def export_campain(campain_id):
    """Exporte une campagne au format JSON."""
    try:
        # Récupérer la campagne
        campain = Campain.find_by_id(campain_id)
        if not campain:
            return jsonify({'message': 'Campagne non trouvée'}), 404
            
        # Récupérer les tests
        tests = Test.get_by_campain(campain_id)
        
        # Préparer les données d'export
        export_data = {
            'campain': campain,
            'tests': tests,
            'exportDate': datetime.utcnow().isoformat(),
            'version': '1.0'
        }
        
        # Gérer l'inclusion des fichiers
        include_files = request.args.get('include_files', 'false').lower() == 'true'
        
        if include_files:
            files_list = []
            workdir = Path(get_campain_workdir(campain_id))
            files_dir = workdir / 'files'
            
            if files_dir.exists():
                for file_path in files_dir.iterdir():
                    if file_path.is_file():
                        with open(file_path, 'rb') as f:
                            content = f.read()
                            encoded_content = base64.b64encode(content).decode('utf-8')
                            files_list.append({
                                'name': file_path.name,
                                'content': encoded_content
                            })
            
            export_data['files'] = files_list
            
        # Générer le JSON
        json_output = json.dumps(export_data, indent=4, default=str)
        
        # Créer le fichier en mémoire
        mem_file = BytesIO()
        mem_file.write(json_output.encode('utf-8'))
        mem_file.seek(0)
        
        # Nom du fichier
        safe_name = secure_filename(campain['name'])
        filename = f"campain_{safe_name}_{campain_id}.json"
        
        return send_file(
            mem_file,
            as_attachment=True,
            download_name=filename,
            mimetype='application/json'
        )
        
    except Exception as e:
        return jsonify({'message': f'Erreur lors de l\'export: {str(e)}'}), 500

@campains_bp.route('/import', methods=['POST'])
@token_required
def import_campain():
    """Importe une campagne depuis un fichier JSON."""
    try:
        if 'file' not in request.files:
            return jsonify({'message': 'Aucun fichier fourni'}), 400
            
        file = request.files['file']
        if file.filename == '':
            return jsonify({'message': 'Aucun fichier sélectionné'}), 400
            
        if not file.filename.endswith('.json'):
            return jsonify({'message': 'Le fichier doit être au format JSON'}), 400

        # Lire et parser le JSON
        try:
            content = file.read()
            data = json.loads(content)
        except json.JSONDecodeError:
            return jsonify({'message': 'Fichier JSON invalide'}), 400
            
        # Vérifier la structure
        if 'campain' not in data or 'tests' not in data:
            return jsonify({'message': 'Format de fichier invalide (sections campain ou tests manquantes)'}), 400
            
        # Récupérer le nom de la campagne (soit du formulaire, soit du JSON, soit par défaut)
        import_name = request.form.get('name')
        if not import_name:
            import_name = f"Import de {data['campain'].get('name', 'Campagne sans nom')}"
            
        # 1. Créer la campagne
        user_id = request.user_id  # Injecté par token_required
        campain_id = Campain.create(
            user_created=user_id,
            name=import_name,
            description=data['campain'].get('description', '')
        )
        
        # Créer le répertoire de travail
        create_campain_workdir(campain_id)
        
        # 2. Créer les tests
        for test_data in data['tests']:
            Test.create(
                campain_id=campain_id,
                user_id=user_id,
                actions=test_data.get('actions', []),
                name=test_data.get('name', ''),
                description=test_data.get('description', ''),
                variables=test_data.get('variables', [])
            )
            
        # 3. Gérer les fichiers
        if 'files' in data and isinstance(data['files'], list):
            workdir = Path(get_campain_workdir(campain_id))
            files_dir = workdir / 'files'
            
            if not files_dir.exists():
                files_dir.mkdir(parents=True, exist_ok=True)
                
            for file_item in data['files']:
                if 'name' in file_item and 'content' in file_item:
                    # Remplacer les variables dans le nom du fichier
                    filename = file_item['name'].replace('{{test.campain_id}}', str(campain_id))
                    filename = secure_filename(filename)
                    
                    try:
                        file_content = base64.b64decode(file_item['content'])
                        file_path = files_dir / filename
                        with open(file_path, 'wb') as f:
                            f.write(file_content)
                    except Exception as e:
                        print(f"Erreur lors de la création du fichier {filename}: {e}")
                        # On continue même si un fichier échoue
        
        return jsonify({
            'message': 'Campagne importée avec succès',
            'campain_id': campain_id
        }), 201
        
    except Exception as e:
        return jsonify({'message': f'Erreur lors de l\'import: {str(e)}'}), 500
