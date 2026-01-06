"""Routes API pour la gestion des campagnes."""
from flask import Blueprint, request, jsonify, send_file, current_app
from flask_babel import gettext as _
from werkzeug.utils import secure_filename
from models.campain import Campain
from utils.auth import token_required
from utils.pagination import get_pagination_params, paginate_results
from utils.validation import validate_required_fields
from utils.workdir import create_campain_workdir, delete_campain_workdir, get_campain_workdir
from pathlib import Path
import os
import shutil
from datetime import datetime
import json
import base64
from io import BytesIO
from models.test import Test
import uuid

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
        return jsonify({'message': _('Erreur serveur: {}').format(str(e))}), 500

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
            'message': _('Campagne créée avec succès'),
            'campain_id': campain_id
        }), 201
    
    except Exception as e:
        return jsonify({'message': _('Erreur serveur: {}').format(str(e))}), 500

@campains_bp.route('/<campain_id>', methods=['GET'])
@token_required
def get_campain(campain_id):
    """Récupère les détails d'une campagne spécifique."""
    try:
        campain = Campain.find_by_id(campain_id)
        
        if not campain:
            return jsonify({'message': _('Campagne non trouvée')}), 404
        
        return jsonify(campain), 200
    
    except Exception as e:
        return jsonify({'message': _('Erreur serveur: {}').format(str(e))}), 500

@campains_bp.route('/<campain_id>', methods=['PUT'])
@token_required
def update_campain(campain_id):
    """Met à jour une campagne existante."""
    try:
        data = request.get_json()
        
        Campain.update(campain_id, data)
        
        return jsonify({'message': _('Campagne mise à jour avec succès')}), 200
    
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


@campains_bp.route('/<campain_id>/workdir', methods=['GET'])
@token_required
def list_workdir_files(campain_id):
    """Liste les fichiers du répertoire work de la campagne."""
    try:
        # Vérifier que la campagne existe
        campain = Campain.find_by_id(campain_id)
        if not campain:
            return jsonify({'message': 'Campagne non trouvée'}), 404
        
        # Récupérer le chemin relatif demandé
        rel_path = request.args.get('path', '').strip('/')
        
        # Récupérer le répertoire work de la campagne
        base_dir = Path(get_campain_workdir(campain_id)) / "work"
        base_dir.mkdir(parents=True, exist_ok=True)
        target_dir = base_dir / rel_path
        
        # Sécurité : vérifier que le chemin cible est bien dans le répertoire work
        try:
            target_dir = target_dir.resolve()
            if not str(target_dir).startswith(str(base_dir.resolve())):
                return jsonify({'message': 'Accès non autorisé'}), 403
        except Exception:
            return jsonify({'message': 'Chemin invalide'}), 400
        
        if not target_dir.exists():
            return jsonify({'files': [], 'directories': [], 'workdir_path': str(base_dir.resolve())}), 200
        
        files = []
        directories = []
        
        for item in target_dir.iterdir():
            stat = item.stat()
            item_info = {
                'name': item.name,
                'modified': datetime.fromtimestamp(stat.st_mtime).isoformat(),
                'path': str(item.relative_to(base_dir))
            }
            
            if item.is_file():
                item_info['size'] = round(stat.st_size / 1024, 2)  # Taille en Ko
                item_info['type'] = 'file'
                files.append(item_info)
            elif item.is_dir():
                item_info['type'] = 'directory'
                directories.append(item_info)
        
        # Trier par nom
        files.sort(key=lambda x: x['name'])
        directories.sort(key=lambda x: x['name'])
        
        return jsonify({
            'files': files, 
            'directories': directories,
            'current_path': rel_path,
            'workdir_path': str(base_dir.resolve())
        }), 200
    
    except Exception as e:
        return jsonify({'message': f'Erreur serveur: {str(e)}'}), 500


@campains_bp.route('/<campain_id>/workdir/<path:filename>', methods=['GET'])
@token_required
def download_workdir_file(campain_id, filename):
    """Télécharge un fichier du répertoire work de la campagne."""
    try:
        # Vérifier que la campagne existe
        campain = Campain.find_by_id(campain_id)
        if not campain:
            return jsonify({'message': 'Campagne non trouvée'}), 404
        
        # Récupérer le chemin du fichier dans le répertoire work
        base_dir = Path(get_campain_workdir(campain_id)) / "work"
        file_path = (base_dir / filename).resolve()
        
        # Sécurité
        if not str(file_path).startswith(str(base_dir.resolve())):
            return jsonify({'message': 'Accès non autorisé'}), 403
        
        if not file_path.exists() or not file_path.is_file():
            return jsonify({'message': 'Fichier non trouvé'}), 404
        
        return send_file(
            str(file_path),
            as_attachment=True,
            download_name=file_path.name
        )
    
    except Exception as e:
        return jsonify({'message': f'Erreur serveur: {str(e)}'}), 500


@campains_bp.route('/<campain_id>/workdir/<path:filename>', methods=['DELETE'])
@token_required
def delete_workdir_file(campain_id, filename):
    """Supprime un fichier du répertoire work de la campagne."""
    try:
        # Vérifier que la campagne existe
        campain = Campain.find_by_id(campain_id)
        if not campain:
            return jsonify({'message': 'Campagne non trouvée'}), 404
        
        # Récupérer le chemin du fichier dans le répertoire work
        base_dir = Path(get_campain_workdir(campain_id)) / "work"
        file_path = (base_dir / filename).resolve()
        
        # Sécurité
        if not str(file_path).startswith(str(base_dir.resolve())):
            return jsonify({'message': 'Accès non autorisé'}), 403
        
        if not file_path.exists() or not file_path.is_file():
            return jsonify({'message': 'Fichier non trouvé'}), 404
        
        # Supprimer le fichier
        os.remove(str(file_path))
        
        # Émettre un événement WebSocket
        emit_files_updated(campain_id)
        
        return jsonify({'message': 'Fichier supprimé avec succès'}), 200
    
    except Exception as e:
        return jsonify({'message': f'Erreur serveur: {str(e)}'}), 500


@campains_bp.route('/<campain_id>/workdir-directories', methods=['DELETE'])
@token_required
def delete_workdir_directory(campain_id):
    """Supprime un répertoire du répertoire work."""
    try:
        path = request.args.get('path')
        if not path:
            return jsonify({'message': 'Chemin manquant'}), 400
            
        # Vérifier que la campagne existe
        campain = Campain.find_by_id(campain_id)
        if not campain:
            return jsonify({'message': 'Campagne non trouvée'}), 404
            
        # Récupérer le répertoire work de la campagne
        base_dir = Path(get_campain_workdir(campain_id)) / "work"
        dir_path = (base_dir / path).resolve()
        
        # Sécurité
        if not str(dir_path).startswith(str(base_dir.resolve())):
            return jsonify({'message': 'Accès non autorisé'}), 403
            
        if not dir_path.exists() or not dir_path.is_dir():
            return jsonify({'message': 'Répertoire non trouvé'}), 404
            
        try:
            shutil.rmtree(str(dir_path))
        except Exception as e:
            return jsonify({'message': f'Erreur lors de la suppression: {str(e)}'}), 500
            
        # Émettre un événement WebSocket
        emit_files_updated(campain_id)
        
        return jsonify({'message': 'Répertoire supprimé avec succès'}), 200
        
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
        
        # Récupérer le chemin relatif demandé
        rel_path = request.args.get('path', '').strip('/')
        
        # Récupérer le répertoire files de la campagne
        base_dir = Path(get_campain_workdir(campain_id)) / "files"
        base_dir.mkdir(parents=True, exist_ok=True)
        target_dir = base_dir / rel_path
        
        # Sécurité : vérifier que le chemin cible est bien dans le répertoire files
        try:
            target_dir = target_dir.resolve()
            if not str(target_dir).startswith(str(base_dir.resolve())):
                return jsonify({'message': 'Accès non autorisé'}), 403
        except Exception:
            return jsonify({'message': 'Chemin invalide'}), 400
        
        if not target_dir.exists():
            return jsonify({'files': [], 'directories': []}), 200
        
        files = []
        directories = []
        
        for item in target_dir.iterdir():
            stat = item.stat()
            item_info = {
                'name': item.name,
                'modified': datetime.fromtimestamp(stat.st_mtime).isoformat(),
                'path': str(item.relative_to(base_dir))
            }
            
            if item.is_file():
                item_info['size'] = round(stat.st_size / 1024, 2)  # Taille en Ko
                item_info['type'] = 'file'
                files.append(item_info)
            elif item.is_dir():
                item_info['type'] = 'directory'
                directories.append(item_info)
        
        # Trier par nom
        files.sort(key=lambda x: x['name'])
        directories.sort(key=lambda x: x['name'])
        
        return jsonify({
            'files': files, 
            'directories': directories,
            'current_path': rel_path,
            'files_dir': str(base_dir.resolve())
        }), 200
    
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


@campains_bp.route('/<campain_id>/files/<filename>', methods=['PUT'])
@token_required
def rename_file(campain_id, filename):
    """Renomme un fichier du répertoire de travail de la campagne."""
    try:
        # Vérifier que la campagne existe
        campain = Campain.find_by_id(campain_id)
        if not campain:
            return jsonify({'message': 'Campagne non trouvée'}), 404
        
        data = request.get_json()
        new_name = data.get('new_name')
        
        if not new_name:
            return jsonify({'message': 'Nouveau nom manquant'}), 400
            
        new_filename = secure_filename(new_name)
        if not new_filename:
            return jsonify({'message': 'Nom de fichier invalide'}), 400
            
        # Récupérer le répertoire files de la campagne
        campain_dir = Path(get_campain_workdir(campain_id)) / "files"
        old_file_path = campain_dir / secure_filename(filename)
        new_file_path = campain_dir / new_filename
        
        if not old_file_path.exists() or not old_file_path.is_file():
            return jsonify({'message': 'Fichier source non trouvé'}), 404
            
        if new_file_path.exists() and new_filename != secure_filename(filename):
            return jsonify({'message': 'Un fichier avec ce nom existe déjà'}), 409
            
        # Renommer le fichier
        os.rename(str(old_file_path), str(new_file_path))
        
        # Émettre un événement WebSocket
        emit_files_updated(campain_id)
        
        return jsonify({'message': 'Fichier renommé avec succès', 'new_name': new_filename}), 200
    
    except Exception as e:
        return jsonify({'message': f'Erreur serveur: {str(e)}'}), 500


@campains_bp.route('/<campain_id>/files/<path:filename>', methods=['GET'])
@token_required
def download_file(campain_id, filename):
    """Télécharge un fichier du répertoire de travail de la campagne."""
    try:
        # Vérifier que la campagne existe
        campain = Campain.find_by_id(campain_id)
        if not campain:
            return jsonify({'message': 'Campagne non trouvée'}), 404
        
        # Récupérer le chemin du fichier dans le répertoire files
        base_dir = Path(get_campain_workdir(campain_id)) / "files"
        file_path = (base_dir / filename).resolve()
        
        # Sécurité
        if not str(file_path).startswith(str(base_dir.resolve())):
            return jsonify({'message': 'Accès non autorisé'}), 403
        
        if not file_path.exists() or not file_path.is_file():
            return jsonify({'message': 'Fichier non trouvé'}), 404
        
        return send_file(
            str(file_path),
            as_attachment=True,
            download_name=file_path.name
        )
    
    except Exception as e:
        return jsonify({'message': f'Erreur serveur: {str(e)}'}), 500


@campains_bp.route('/<campain_id>/files/<path:filename>', methods=['DELETE'])
@token_required
def delete_file(campain_id, filename):
    """Supprime un fichier du répertoire de travail de la campagne."""
    try:
        # Vérifier que la campagne existe
        campain = Campain.find_by_id(campain_id)
        if not campain:
            return jsonify({'message': 'Campagne non trouvée'}), 404
        
        # Récupérer le chemin du fichier dans le répertoire files
        base_dir = Path(get_campain_workdir(campain_id)) / "files"
        file_path = (base_dir / filename).resolve()
        
        # Sécurité
        if not str(file_path).startswith(str(base_dir.resolve())):
            return jsonify({'message': 'Accès non autorisé'}), 403
        
        if not file_path.exists() or not file_path.is_file():
            return jsonify({'message': 'Fichier non trouvé'}), 404
        
        # Supprimer le fichier
        os.remove(str(file_path))
        
        # Émettre un événement WebSocket
        emit_files_updated(campain_id)
        
        return jsonify({'message': 'Fichier supprimé avec succès'}), 200
    
    except Exception as e:
        return jsonify({'message': f'Erreur serveur: {str(e)}'}), 500

@campains_bp.route('/<campain_id>/directories', methods=['DELETE'])
@token_required
def delete_directory(campain_id):
    """Supprime un répertoire vide."""
    try:
        path = request.args.get('path')
        if not path:
            return jsonify({'message': 'Chemin manquant'}), 400
            
        # Vérifier que la campagne existe
        campain = Campain.find_by_id(campain_id)
        if not campain:
            return jsonify({'message': 'Campagne non trouvée'}), 404
            
        # Récupérer le répertoire files de la campagne
        base_dir = Path(get_campain_workdir(campain_id)) / "files"
        dir_path = (base_dir / path).resolve()
        
        # Sécurité
        if not str(dir_path).startswith(str(base_dir.resolve())):
            return jsonify({'message': 'Accès non autorisé'}), 403
            
        if not dir_path.exists() or not dir_path.is_dir():
            return jsonify({'message': 'Répertoire non trouvé'}), 404
            
        try:
            shutil.rmtree(str(dir_path))
        except Exception as e:
            return jsonify({'message': f'Erreur lors de la suppression: {str(e)}'}), 500
            
        # Émettre un événement WebSocket
        emit_files_updated(campain_id)
        
        return jsonify({'message': 'Répertoire supprimé avec succès'}), 200
        
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
        
        # Récupérer les structures de données des plugins
        plugin_data_structures = Campain.get_plugin_data_structures(campain_id)
        
        # Préparer les données d'export
        export_data = {
            'campain': campain,
            'tests': tests,
            'plugin_data_structures': plugin_data_structures,
            'exportDate': datetime.utcnow().isoformat(),
            'version': '1.1'  # Version mise à jour pour inclure les structures
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
        
        # 4. Restaurer les structures de données des plugins
        if 'plugin_data_structures' in data and isinstance(data['plugin_data_structures'], list):
            for structure in data['plugin_data_structures']:
                if all(key in structure for key in ['name', 'plugin_type', 'values']):
                    try:
                        Campain.add_plugin_data_structure(
                            campain_id=campain_id,
                            name=structure['name'],
                            plugin_type=structure['plugin_type'],
                            values=structure['values']
                        )
                    except Exception as e:
                        print(f"Erreur lors de la restauration de la structure {structure.get('name', 'unknown')}: {e}")
                        # On continue même si une structure échoue
        
        return jsonify({
            'message': 'Campagne importée avec succès',
            'campain_id': campain_id
        }), 201
        
    except Exception as e:
        return jsonify({'message': f'Erreur lors de l\'import: {str(e)}'}), 500

@campains_bp.route('/<campain_id>/reports', methods=['GET'])
@token_required
def list_reports(campain_id):
    """Liste les rapports générés pour une campagne."""
    try:
        workdir = get_campain_workdir(campain_id)
        reports_dir = os.path.join(workdir, 'reports')
        
        if not os.path.exists(reports_dir):
            return jsonify([]), 200
            
        reports = []
        for filename in os.listdir(reports_dir):
            file_path = os.path.join(reports_dir, filename)
            if os.path.isfile(file_path):
                stat = os.stat(file_path)
                # Essayer de déduire le type de rapport depuis le nom
                # Format attendu: report_<type>_<timestamp>.<ext>
                parts = filename.split('_')
                report_type = parts[1] if len(parts) > 2 else 'unknown'
                
                reports.append({
                    'name': filename,
                    'type': report_type,
                    'size': stat.st_size,
                    'date': datetime.fromtimestamp(stat.st_mtime).isoformat(),
                    'download_url': f"/api/rapports/download/{campain_id}/{filename}"
                })
        
        # Trier par date décroissante
        reports.sort(key=lambda x: x['date'], reverse=True)
        
        return jsonify(reports), 200
    except Exception as e:
        return jsonify({'message': str(e)}), 500

@campains_bp.route('/<campain_id>/reports/<filename>', methods=['DELETE'])
@token_required
def delete_report(campain_id, filename):
    """Supprime un rapport généré."""
    try:
        workdir = get_campain_workdir(campain_id)
        reports_dir = os.path.join(workdir, 'reports')
        file_path = os.path.join(reports_dir, secure_filename(filename))
        
        if not os.path.exists(file_path):
            return jsonify({'message': _('Fichier non trouvé')}), 404
            
        os.remove(file_path)
        return jsonify({'message': _('Rapport supprimé avec succès')}), 200
    except Exception as e:
        return jsonify({'message': str(e)}), 500


# ==================== Plugin Data Structures Routes ====================

@campains_bp.route('/<campain_id>/plugin-structures', methods=['GET'])
@token_required
def get_plugin_structures(campain_id):
    """Récupère les structures de données des plugins d'une campagne."""
    try:
        # Vérifier que la campagne existe
        campain = Campain.find_by_id(campain_id)
        if not campain:
            return jsonify({'message': _('Campagne non trouvée')}), 404
        
        structures = Campain.get_plugin_data_structures(campain_id)
        return jsonify({'structures': structures}), 200
        
    except Exception as e:
        return jsonify({'message': _('Erreur serveur: {}').format(str(e))}), 500


@campains_bp.route('/<campain_id>/plugin-structures', methods=['POST'])
@token_required
def add_plugin_structure(campain_id):
    """Ajoute une structure de données de plugin à une campagne."""
    try:
        # Vérifier que la campagne existe
        campain = Campain.find_by_id(campain_id)
        if not campain:
            return jsonify({'message': _('Campagne non trouvée')}), 404
        
        data = request.get_json()
        
        # Validation
        if not data.get('name'):
            return jsonify({'message': _('Le nom de la structure est obligatoire')}), 400
        if not data.get('plugin_type'):
            return jsonify({'message': _('Le type de plugin est obligatoire')}), 400
        if not data.get('values') or not isinstance(data['values'], dict):
            return jsonify({'message': _('Les valeurs de la structure sont obligatoires')}), 400
        
        structure_id = Campain.add_plugin_data_structure(
            campain_id=campain_id,
            name=data['name'],
            plugin_type=data['plugin_type'],
            values=data['values']
        )
        
        if not structure_id:
            return jsonify({'message': _('Une structure avec ce nom existe déjà pour ce type de plugin')}), 409
        
        return jsonify({
            'message': _('Structure de données ajoutée avec succès'),
            'structure_id': structure_id
        }), 201
        
    except Exception as e:
        return jsonify({'message': _('Erreur serveur: {}').format(str(e))}), 500


@campains_bp.route('/<campain_id>/plugin-structures/<structure_id>', methods=['GET'])
@token_required
def get_plugin_structure(campain_id, structure_id):
    """Récupère une structure de données de plugin spécifique."""
    try:
        # Vérifier que la campagne existe
        campain = Campain.find_by_id(campain_id)
        if not campain:
            return jsonify({'message': _('Campagne non trouvée')}), 404
        
        structure = Campain.get_plugin_data_structure_by_id(campain_id, structure_id)
        
        if not structure:
            return jsonify({'message': _('Structure de données non trouvée')}), 404
        
        return jsonify(structure), 200
        
    except Exception as e:
        return jsonify({'message': _('Erreur serveur: {}').format(str(e))}), 500


@campains_bp.route('/<campain_id>/plugin-structures/<structure_id>', methods=['PUT'])
@token_required
def update_plugin_structure(campain_id, structure_id):
    """Met à jour une structure de données de plugin."""
    try:
        # Vérifier que la campagne existe
        campain = Campain.find_by_id(campain_id)
        if not campain:
            return jsonify({'message': _('Campagne non trouvée')}), 404
        
        data = request.get_json()
        
        name = data.get('name')
        values = data.get('values')
        
        if name is None and values is None:
            return jsonify({'message': _('Aucune modification fournie')}), 400
        
        success = Campain.update_plugin_data_structure(
            campain_id=campain_id,
            structure_id=structure_id,
            name=name,
            values=values
        )
        
        if not success:
            return jsonify({'message': _('Impossible de mettre à jour la structure (non trouvée ou nom déjà utilisé)')}), 400
        
        return jsonify({'message': _('Structure de données mise à jour avec succès')}), 200
        
    except Exception as e:
        return jsonify({'message': _('Erreur serveur: {}').format(str(e))}), 500


@campains_bp.route('/<campain_id>/plugin-structures/<structure_id>', methods=['DELETE'])
@token_required
def delete_plugin_structure(campain_id, structure_id):
    """Supprime une structure de données de plugin et nettoie les actions qui l'utilisent."""
    try:
        # Vérifier que la campagne existe
        campain = Campain.find_by_id(campain_id)
        if not campain:
            return jsonify({'message': _('Campagne non trouvée')}), 404
        
        # Récupérer la structure avant suppression pour pouvoir copier ses valeurs
        structure = Campain.get_plugin_data_structure_by_id(campain_id, structure_id)
        if not structure:
            return jsonify({'message': _('Structure de données non trouvée')}), 404
        
        # Nettoyer les actions qui référencent cette structure
        actions_cleaned = _cleanup_actions_referencing_structure(campain_id, structure_id, structure)
        
        # Supprimer la structure
        success = Campain.delete_plugin_data_structure(campain_id, structure_id)
        
        if not success:
            return jsonify({'message': _('Structure de données non trouvée')}), 404
        
        return jsonify({
            'message': _('Structure de données supprimée avec succès'),
            'actions_cleaned': actions_cleaned
        }), 200
        
    except Exception as e:
        return jsonify({'message': _('Erreur serveur: {}').format(str(e))}), 500


def _cleanup_actions_referencing_structure(campain_id, structure_id, structure):
    """
    Nettoie les actions qui référencent une structure supprimée.
    Copie les valeurs de la structure dans les champs de l'action avant de supprimer la référence.
    
    Args:
        campain_id: ID de la campagne
        structure_id: ID de la structure supprimée
        structure: Données de la structure (avec values)
        
    Returns:
        int: Nombre d'actions nettoyées
    """
    from models.test import Test
    from utils.db import get_collection
    from bson import ObjectId
    
    actions_cleaned = 0
    structure_values = structure.get('values', {})
    
    # Récupérer tous les tests de la campagne
    tests = Test.get_by_campain(campain_id)
    
    tests_collection = get_collection(Test.collection_name)
    
    for test in tests:
        test_modified = False
        actions = test.get('actions', [])
        
        for action in actions:
            if action.get('structure_id') == structure_id:
                # Copier les valeurs de la structure dans action.value
                if 'value' not in action:
                    action['value'] = {}
                
                for key, value in structure_values.items():
                    # Ne pas écraser les valeurs existantes
                    if key not in action['value'] or action['value'][key] == '' or action['value'][key] is None:
                        action['value'][key] = value
                
                # Supprimer la référence à la structure
                del action['structure_id']
                
                test_modified = True
                actions_cleaned += 1
        
        # Mettre à jour le test si des actions ont été modifiées
        if test_modified:
            tests_collection.update_one(
                {'_id': ObjectId(test['_id'])},
                {'$set': {'actions': actions}}
            )
    
    return actions_cleaned
