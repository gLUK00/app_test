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
