"""Classe de base pour les plugins de rapports de performance."""
from abc import abstractmethod
from plugins.plugin_base import PluginBase


class PerfReportBase(PluginBase):
    """
    Classe de base abstraite pour les plugins de rapports de performance.
    Les plugins de rapports de performance permettent de générer différents types
    de rapports (HTML, CSV, JSON, etc.) à partir des résultats de tests de performance.
    """

    # Métadonnées du plugin (à surcharger dans les sous-classes)
    plugin_name = None

    def __init__(self):
        """Initialise le plugin de rapport de performance."""
        self.report_data = None

    @abstractmethod
    def get_metadata(self):
        """
        Retourne les métadonnées du plugin de rapport de performance.

        Returns:
            dict: Métadonnées du plugin
        """
        return {
            "name": self.plugin_name or self.__class__.__name__,
            "version": self.version,
            "author": self.author,
            "description": self.__doc__.strip() if self.__doc__ else "",
            "output_format": self.get_output_format()
        }

    @abstractmethod
    def validate_config(self, config):
        """
        Valide la configuration du plugin.

        Args:
            config (dict): Configuration à valider

        Returns:
            tuple: (bool, str) - (succès, message d'erreur éventuel)
        """
        return (True, "")

    @abstractmethod
    def get_output_format(self):
        """
        Retourne le format de sortie du rapport.

        Returns:
            str: Format de sortie (html, csv, json, etc.)
        """
        pass

    @abstractmethod
    def get_configuration_schema(self):
        """
        Retourne le schéma de configuration du rapport.
        Permet de définir les options personnalisables affichées dans l'interface.

        Returns:
            list: Liste de champs de configuration
            [
                {"name": "title", "type": "string", "label": "...", "required": False},
                {"name": "theme",  "type": "select", "label": "...", "options": [...], "required": False},
                {"name": "flag",   "type": "checkbox", "label": "...", "required": False}
            ]
        """
        pass

    @abstractmethod
    def generate(self, perf_rapport, config=None):
        """
        Génère le rapport de performance.

        Args:
            perf_rapport (dict): Document rapport de performance depuis MongoDB.
                Contient notamment :
                - perf_results (dict) : résultats globaux + liste tests
                    - total_instances, executed_instances, passed_instances, failed_instances
                    - exec_time_avg_ms, exec_time_min_ms, exec_time_max_ms, exec_time_total_ms
                    - tests (list) : par test : name, total_instances, passed_instances,
                                     failed_instances, exec_time_avg/min/max/total_ms
                - perf_config (dict) : configuration utilisée pour le test
                - details (str)      : libellé du rapport
                - dateCreated        : datetime de création
                - startTime          : timestamp début (float)
                - endTime            : timestamp fin (float)
                - executionTimeMs    : durée totale en ms
            config (dict): Configuration personnalisée pour la génération

        Returns:
            dict: {
                "success": bool,
                "message": str,
                "file_path": str,   # chemin absolu vers le fichier généré
                "data": any         # données brutes optionnelles (ex: contenu CSV)
            }
        """
        pass

    def get_supported_templates(self):
        """
        Retourne la liste des modèles de rapport supportés.

        Returns:
            list: Liste des noms de modèles disponibles
        """
        return ["default"]
