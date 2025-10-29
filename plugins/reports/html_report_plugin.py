"""Exemple de plugin de rapport HTML."""
import json
from datetime import datetime
from plugins.reports.report_base import ReportBase


class HTMLReportPlugin(ReportBase):
    """Plugin de génération de rapports HTML."""
    
    # Métadonnées du plugin
    plugin_name = "html"
    version = "1.0.0"
    author = "TestGyver Team"
    
    def get_metadata(self):
        """Retourne les métadonnées du rapport."""
        return {
            "name": self.plugin_name,
            "version": self.version,
            "author": self.author,
            "description": "Génère des rapports au format HTML",
            "output_format": self.get_output_format()
        }
    
    def validate_config(self, config):
        """Valide la configuration du rapport."""
        return (True, "")
    
    def get_output_format(self):
        """Retourne le format de sortie."""
        return "html"
    
    def get_configuration_schema(self):
        """Retourne le schéma de configuration."""
        return [
            {
                "name": "title",
                "type": "string",
                "label": "Titre du rapport",
                "placeholder": "Rapport de tests",
                "required": False
            },
            {
                "name": "include_details",
                "type": "checkbox",
                "label": "Inclure les détails des tests",
                "required": False
            },
            {
                "name": "theme",
                "type": "select",
                "label": "Thème du rapport",
                "options": ["light", "dark", "blue"],
                "required": False
            }
        ]
    
    def generate(self, test_results, config=None):
        """
        Génère le rapport HTML.
        
        Args:
            test_results (dict): Résultats des tests
            config (dict): Configuration personnalisée
        
        Returns:
            dict: Résultat de la génération
        """
        try:
            config = config or {}
            title = config.get('title', 'Rapport de tests TestGyver')
            theme = config.get('theme', 'light')
            include_details = config.get('include_details', True)
            
            # Générer le HTML
            html_content = self._generate_html(test_results, title, theme, include_details)
            
            # Générer le nom de fichier
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"rapport_{timestamp}.html"
            
            return {
                "success": True,
                "message": "Rapport HTML généré avec succès",
                "file_path": filename,
                "data": html_content
            }
            
        except Exception as e:
            return {
                "success": False,
                "message": f"Erreur lors de la génération du rapport : {str(e)}",
                "file_path": None,
                "data": None
            }
    
    def _generate_html(self, test_results, title, theme, include_details):
        """Génère le contenu HTML du rapport."""
        
        # Calculer les statistiques
        total_tests = len(test_results.get('tests', []))
        passed_tests = sum(1 for t in test_results.get('tests', []) if t.get('status') == 'passed')
        failed_tests = total_tests - passed_tests
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        html = f"""<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            margin: 20px;
            background-color: {'#f5f5f5' if theme == 'light' else '#1e1e1e'};
            color: {'#333' if theme == 'light' else '#e0e0e0'};
        }}
        .header {{
            background-color: {'#007bff' if theme == 'blue' else '#28a745' if theme == 'light' else '#0d47a1'};
            color: white;
            padding: 20px;
            border-radius: 5px;
            margin-bottom: 20px;
        }}
        .stats {{
            display: flex;
            gap: 20px;
            margin-bottom: 20px;
        }}
        .stat-card {{
            background: white;
            padding: 15px;
            border-radius: 5px;
            flex: 1;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .stat-value {{
            font-size: 2em;
            font-weight: bold;
            color: #007bff;
        }}
        .test-item {{
            background: white;
            padding: 15px;
            margin-bottom: 10px;
            border-radius: 5px;
            border-left: 4px solid;
        }}
        .test-passed {{
            border-left-color: #28a745;
        }}
        .test-failed {{
            border-left-color: #dc3545;
        }}
        .footer {{
            margin-top: 20px;
            padding: 10px;
            text-align: center;
            color: #666;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>{title}</h1>
        <p>Généré le {datetime.now().strftime("%d/%m/%Y à %H:%M:%S")}</p>
    </div>
    
    <div class="stats">
        <div class="stat-card">
            <div>Total de tests</div>
            <div class="stat-value">{total_tests}</div>
        </div>
        <div class="stat-card">
            <div>Tests réussis</div>
            <div class="stat-value" style="color: #28a745;">{passed_tests}</div>
        </div>
        <div class="stat-card">
            <div>Tests échoués</div>
            <div class="stat-value" style="color: #dc3545;">{failed_tests}</div>
        </div>
        <div class="stat-card">
            <div>Taux de réussite</div>
            <div class="stat-value" style="color: #007bff;">{success_rate:.1f}%</div>
        </div>
    </div>
"""
        
        if include_details:
            html += "<h2>Détails des tests</h2>\n"
            for test in test_results.get('tests', []):
                status_class = "test-passed" if test.get('status') == 'passed' else "test-failed"
                html += f"""
    <div class="test-item {status_class}">
        <h3>{test.get('name', 'Test sans nom')}</h3>
        <p><strong>Statut:</strong> {test.get('status', 'inconnu')}</p>
        <p><strong>Logs:</strong></p>
        <pre>{test.get('logs', 'Aucun log disponible')}</pre>
    </div>
"""
        
        html += """
    <div class="footer">
        <p>Rapport généré par TestGyver - Plugin HTML Report v1.0.0</p>
    </div>
</body>
</html>
"""
        return html
