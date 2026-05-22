"""Routes API pour la génération de rapports de performance."""
import os
from flask import Blueprint, request, jsonify, current_app, send_file
from flask_babel import gettext as _
from datetime import datetime
from models.rapport import Rapport
from utils.auth import token_required
from plugins.perf_reports import get_all_perf_reports, get_perf_report
from utils.workdir import get_campain_workdir

perf_reports_bp = Blueprint('perf_reports_api', __name__, url_prefix='/api/perf-reports')


@perf_reports_bp.route('/plugins', methods=['GET'])
@token_required
def get_perf_report_plugins():
    """Récupère la liste des plugins de rapport de performance disponibles."""
    try:
        plugins = get_all_perf_reports()
        result = []
        for p_type, p_data in plugins.items():
            result.append({
                "type": p_type,
                "metadata": p_data["metadata"],
                "schema": p_data["configuration_schema"]
            })
        return jsonify(result), 200
    except Exception as exc:
        return jsonify({'message': str(exc)}), 500


@perf_reports_bp.route('/<rapport_id>/generate', methods=['POST'])
@token_required
def generate_perf_report(rapport_id):
    """Génère un rapport pour un rapport de performance donné."""
    try:
        data = request.get_json()
        report_type = data.get('report_type')
        config = data.get('config', {})

        if not report_type:
            return jsonify({'message': _('Type de rapport manquant')}), 400

        # Récupérer le rapport de performance
        rapport = Rapport.find_by_id(rapport_id)
        if not rapport:
            return jsonify({'message': _('Rapport introuvable')}), 404

        if rapport.get('type') != 'performance':
            return jsonify({'message': _('Ce rapport n\'est pas un rapport de performance')}), 400

        if rapport.get('status') not in ('completed', 'failed'):
            return jsonify({'message': _('Le test de performance n\'est pas encore terminé')}), 400

        # Récupérer le plugin
        plugin = get_perf_report(report_type)
        if not plugin:
            return jsonify({'message': _('Plugin de rapport {} introuvable').format(report_type)}), 404

        # Valider la configuration
        is_valid, error_msg = plugin.validate_config(config)
        if not is_valid:
            return jsonify({'message': _('Configuration invalide: {}').format(error_msg)}), 400

        # Préparer le répertoire de sortie
        campain_id = str(rapport.get('campainId', ''))
        workdir = get_campain_workdir(campain_id)
        reports_dir = os.path.join(workdir, 'reports')
        os.makedirs(reports_dir, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        ext = plugin.get_output_format()
        filename = f"perf_report_{report_type}_{timestamp}.{ext}"
        output_path = os.path.join(reports_dir, filename)

        config['output_path'] = output_path

        # Générer le rapport
        result = plugin.generate(rapport, config)

        if result.get('success'):
            return jsonify({
                'message': _('Rapport de performance généré avec succès'),
                'file_path': result.get('file_path'),
                'download_url': f"/api/perf-reports/download/{campain_id}/{filename}"
            }), 200
        else:
            return jsonify({
                'message': _('Erreur lors de la génération: {}').format(result.get('message'))
            }), 500

    except Exception as exc:
        current_app.logger.error(f"Erreur génération rapport de performance: {str(exc)}")
        return jsonify({'message': str(exc)}), 500


@perf_reports_bp.route('/download/<campain_id>/<filename>', methods=['GET'])
@token_required
def download_perf_report(campain_id, filename):
    """Télécharge un rapport de performance généré."""
    try:
        # Sécurité : interdire la traversée de chemin
        safe_filename = os.path.basename(filename)
        if safe_filename != filename or '..' in filename:
            return jsonify({'message': _('Nom de fichier invalide')}), 400

        workdir = get_campain_workdir(campain_id)
        file_path = os.path.join(workdir, 'reports', safe_filename)

        if not os.path.exists(file_path):
            return jsonify({'message': _('Fichier introuvable')}), 404

        # Déterminer le MIME type selon l'extension
        ext = safe_filename.rsplit('.', 1)[-1].lower() if '.' in safe_filename else ''
        mime_map = {
            'html': 'text/html',
            'csv':  'text/csv',
            'json': 'application/json',
            'pdf':  'application/pdf',
        }
        mime_type = mime_map.get(ext, 'application/octet-stream')

        return send_file(
            file_path,
            mimetype=mime_type,
            as_attachment=True,
            download_name=safe_filename
        )
    except Exception as exc:
        current_app.logger.error(f"Erreur téléchargement rapport de performance: {str(exc)}")
        return jsonify({'message': str(exc)}), 500
